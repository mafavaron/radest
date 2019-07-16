#!/usr/bin/env python3

import numpy as np
import radest
import os
import sys

if __name__ == "__main__":

    # Get parameters
    if len(sys.argv) != 9:
        print("radlist - Program generating a time series of global radiation estimates")
        print()
        print("Usage:")
        print()
        print("  ./radlist.py <Lat> <Lon> <Fuse> <Height> <Initial_ISO_DateTime> <Delta_Time> <Num_Steps> <Out_File>")
        print()
        print("where")
        print()
        print("  <Lat>, the latitude, is positive and increasing northwards (decimal degrees)")
        print("  <Lon>, longitude, is positive and increasing eastwards (decimal degrees)")
        print("  <Fuse> is an integer indicating the hours displacement from GMT")
        print("  <Height> is the height above ground (m)")
        print("  <Initial_ISO_DateTime> is a string like 2019-03-08T12:00:00, indicating a date and time")
        print("  <Delta_Time> is the (intgeer!) time step (s)")
        print("  <Num_Steps> is the number of time steps (greater than 0)")
        print("  <Out_File> is the output file name")
        print()
        print("Copyright 2019 by Mauri Favaron")
        print("This is open-source code, covered by the MIT license")
        print()
        sys.exit(1)
    lat   = float(sys.argv[1])
    lon   = float(sys.argv[2])
    fuse  = int(sys.argv[3])
    z     = float(sys.argv[4])
    first = np.datetime64(sys.argv[5], 's')
    delta = int(sys.argv[6])
    n     = int(sys.argv[7])
    out   = sys.argv[8]

    # Generate the time sequence corresponding to the desired time range
    tm = np.array([first + np.timedelta64(i*delta, 's') for i in range(n)])

    # Estimate global radiation
    ra = radest.ExtraterrestrialRadiation(tm,delta, lat, lon, fuse)
    rg = radest.GlobalRadiation(ra, z)

    # Print results
    f = open(out, "w")
    f.write("date, Rg\n")
    for i in range(len(tm)):
        f.write("%s, %f\n" % (str(tm[i]), rg[i]))
    f.close()
