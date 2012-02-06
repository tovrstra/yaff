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


from molmod import angstrom
from molmod.io import XYZReader


__all__ = ['xyz_to_hdf5']


def xyz_to_hdf5(f, fn_xyz, sub=slice(None), file_unit=angstrom, name='pos'):
    """Convert XYZ trajectory file to Yaff HDF5 format.

       **Arguments:**

       f
            An open and writable HDF5 file.

       fn_xyz
            The filename of the XYZ trajectory file.

       **Optional arguments:**

       sub
            The sub argument for the XYZReader. This must be a slice object that
            defines the subsampling of the XYZ file reader. By default all
            frames are read.

       file_unit
            The unit of the data in the XYZ file. [default=angstrom]

       name
            The name of the HDF5 dataset where the trajectory is stored. This
            array is stored in the 'trajectory' group.

       This routine will also test the consistency of the row attribute of the
       trajectory group. If some trajectory data is already present, it will be
       replaced by the new data.
    """
    xyz_reader = XYZReader(fn_xyz, sub=sub)

    # Take care of the data group
    if 'trajectory' not in f:
        tgrp = f.create_group('trajectory')
        existing_row = None
    else:
        tgrp = f['trajectory']
        existing_row = tgrp.attrs['row']

    # Take care of the dataset
    if name in tgrp:
        del tgrp[name]

    # Create a new dataset
    shape = (0, len(xyz_reader.numbers), 3)
    maxshape = (None, len(xyz_reader.numbers), 3)
    ds = tgrp.create_dataset(name, shape, maxshape=maxshape, dtype=float)

    # Fill the dataset with data.
    row = 0
    for title, coordinates in xyz_reader:
        if ds.shape[0] <= row:
            # do not over-allocate. hdf5 works with chunks internally.
            ds.resize(row+1, axis=0)
        ds[row] = coordinates
        row += 1

    # Check number of rows
    if existing_row is None:
        tgrp.attrs['row'] = row
    else:
        if existing_row != row:
            raise ValueError('The amount of data loaded into the HDF5 file is not consistent with number of rows already present in the trajectory.')
