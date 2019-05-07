#!/usr/bin/env python3

import numpy as np
import radest
import os
import sys

if __name__ == "__main__":

    # Get parameters
    if len(sys.argv) != 1:
        print("radtst2 - Program generating various interesting tables for global radiation estimates")
        print()
        print("Usage:")
        print()
        print("  ./radtst2.py")
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
    time03 = np.array([np.datetime64('2019-03-21T12:00:00', 's')])
    time06 = np.array([np.datetime64('2019-06-21T12:00:00', 's')])
    time09 = np.array([np.datetime64('2019-09-21T12:00:00', 's')])
    time12 = np.array([np.datetime64('2019-12-21T12:00:00', 's')])
    lon = 0
    fuse = 0
    lats   = [i-89 for i in range(179)]
    rg03   = np.array([0. for ang in range(179)])
    rg06   = np.array([0. for ang in range(179)])
    rg09   = np.array([0. for ang in range(179)])
    rg12   = np.array([0. for ang in range(179)])
    out    = 'Equator_Latitudes.csv'
    for lat in lats:
        flat = float(lat)
        ra  = radest.ExtraterrestrialRadiation(time03, 3600, flat, lon, fuse)
        rg03[lat+89] = radest.GlobalRadiation(ra, z)
        ra  = radest.ExtraterrestrialRadiation(time06, 3600, flat, lon, fuse)
        rg06[lat+89] = radest.GlobalRadiation(ra, z)
        ra  = radest.ExtraterrestrialRadiation(time09, 3600, flat, lon, fuse)
        rg09[lat+89] = radest.GlobalRadiation(ra, z)
        ra  = radest.ExtraterrestrialRadiation(time12, 3600, flat, lon, fuse)
        rg12[lat+89] = radest.GlobalRadiation(ra, z)

    # Print results
    f = open(out, "w")
    f.write("lat, rg.03, rg.06, rg.09, rg.12\n")
    for i in range(len(rg03)):
        f.write("%d, %f, %f, %f, %f\n" % (i-89, rg03[i], rg06[i], rg09[i], rg12[i]))
    f.close()
