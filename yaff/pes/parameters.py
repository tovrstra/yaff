# YAFF is yet another force-field code
# Copyright (C) 2008 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of YAFF.
#
# YAFF is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# YAFF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


__all__ = ['Complain', 'Parameters', 'ParameterSection']


class Complain(object):
    '''Class for complain method of ParameterFile and ParameterSection'''
    def __init__(self, filename='__nofile__'):
        self.filename = filename

    def __call__(self, counter, message):
        if counter is None:
            raise IOError('The parameter file %s %s.' % (self.fn, message))
        else:
            raise IOError('Line %i in the parameter file %s %s.' % (counter, self.fn, message))


class Parameters(object):
    '''Object that represents a force field parameter file

       The parameter file is first parsed by this object into a convenient
       data structure with dictionaries. The actual force field is then
       generated based on these dictionaries.

       The parameter file has a purely line-based syntax. The order of the lines
       has no meaning. Comments begin with a hash sign (#) and continue till the
       end of a line. If the line is empty after stripping the comments, it is
       ignored. Every non-empty line should have the following format:

       PREFIX:SUFFIX DATA WHICH MAY BE MULTIPLE WORDS AND/OR NUMBERS

       The prefix is used for sections, the suffix for definitions and the
       remainder of the line contains arguments for the definition. Definitions
       may be repeated with different or the same arguments.
    '''
    def __init__(self, sections=None, complain=None):
        if sections is None:
            self.sections = {}
        else:
            self.sections = sections
        if complain is None:
            self.complain = Complain()
        else:
            self.complain = complain

    @classmethod
    def from_file(cls, filename):
        '''Load a parameter file from an actual file.'''


        def parse_line(line):
            '''parse a single line'''
            pos = line.find(':')
            if pos == -1:
                complain(counter, 'does not contain a colon')
            prefix = line[:pos].upper()
            rest = line[pos+1:].strip()
            if len(rest) == 0:
                complain(counter, 'does not have text after the colon')
            if len(prefix.split()) > 1:
                complain(counter, 'has a prefix that contains whitespace')
            pos = rest.find(' ')
            if pos == 0:
                complain(counter, 'does not have a definition after the prefix')
            elif pos == -1:
                complain(counter, 'does not have data after the definition')
            definition = rest[:pos].upper()
            data = rest[pos+1:]
            return prefix, definition, data

        with file(filename) as f:
            complain = Complain(filename)
            result = cls({}, complain)
            counter = 1
            for line in f:
                line = line[:line.find('#')].strip()
                if len(line) > 0:
                    # parse single line
                    prefix, suffix, data = parse_line(line)
                    # get/make section
                    section = result.sections.get(prefix)
                    if section is None:
                        section = ParameterSection(prefix, {}, complain)
                        result.sections[prefix] = section
                    # get/make definition
                    lines = section.definitions.get(suffix)
                    if lines is None:
                        lines = []
                        section.definitions[suffix] = lines
                    lines.append((counter, data))
                counter += 1

        return result

    def write_to_file(self, filename):
        '''Write the parameters back to a file

           The outut file will not contain any comments.
        '''
        with file(filename, 'w') as f:
            for prefix, section in self.sections.iteritems():
                for suffix, lines in section.definitions.iteritems():
                    for counter, data in lines:
                        print >> f, '%s:%s %s' % (prefix, suffix, data)
                    print >> f
                print >> f
                print >> f

    def __getitem__(self, prefix):
        return self.sections[prefix]


class ParameterSection(object):
    '''Object that represents one section in a force field parameter file'''
    def __init__(self, prefix, definitions=None, complain=None):
        self.prefix = prefix
        if definitions is None:
            self.definitions = []
        else:
            self.definitions = definitions
        if complain is None:
            self.complain = Complain()
        else:
            self.complain = complain

    def __getitem__(self, suffix):
        return self.definitions[suffix]
