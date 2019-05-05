#!/usr/bin/env python3

import numpy as np
import radest
import os
import sys

if __name__ == "__main__":

    # Get parameters
    if len(sys.argv) != 1:
        print("radtst - Program generating various interesting tables for global radiation estimates")
        print()
        print("Usage:")
        print()
        print("  ./radtst")
        print()
        print("Copyright 2019 by Mauri Favaron")
        print("This is open-source code, covered by the MIT license")
        print()
        sys.exit(1)

    # Build data sets and print them, in sequence
    lat    = 0.
    lon    = 0.
    fuse   = 0
    z      = 0.
    time03 = np.array([np.datetime64('2019-03-21T00:00:00', 's')])
    time06 = np.array([np.datetime64('2019-06-21T00:00:00', 's')])
    time09 = np.array([np.datetime64('2019-09-21T00:00:00', 's')])
    time12 = np.array([np.datetime64('2019-12-21T00:00:00', 's')])
    rg03   = np.array([0. for ang in range(360)])
    rg06   = np.array([0. for ang in range(360)])
    rg09   = np.array([0. for ang in range(360)])
    rg12   = np.array([0. for ang in range(360)])
    out    = 'Equator_2019-03-21.csv'
    for ang in range(360):
        lon  = ang
        fuse = int(ang/24)
        if fuse == 360:
            fuse = 0
        local03 = time03 + np.timedelta64(fuse, 'h')
        local06 = time06 + np.timedelta64(fuse, 'h')
        local09 = time09 + np.timedelta64(fuse, 'h')
        local12 = time12 + np.timedelta64(fuse, 'h')
        ra  = radest.ExtraterrestrialRadiation(local03, 3600, lat, lon, fuse)
        rg03[ang] = radest.GlobalRadiation(ra, z)
        ra  = radest.ExtraterrestrialRadiation(local06, 3600, lat, lon, fuse)
        rg06[ang] = radest.GlobalRadiation(ra, z)
        ra  = radest.ExtraterrestrialRadiation(local09, 3600, lat, lon, fuse)
        rg09[ang] = radest.GlobalRadiation(ra, z)
        ra  = radest.ExtraterrestrialRadiation(local12, 3600, lat, lon, fuse)
        rg12[ang] = radest.GlobalRadiation(ra, z)

    # Print results
    f = open(out, "w")
    f.write("date, rg.03, rg.06, rg.09, rg.12\n")
    for i in range(len(rg03)):
        f.write("%d, %f, %f, %f, %f\n" % (i, rg03[i], rg06[i], rg09[i], rg12[i]))
    f.close()
