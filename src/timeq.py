#!/usr/bin/env python3

import numpy as np
import radest
import os
import sys

if __name__ == "__main__":

    # Get parameters
    if len(sys.argv) != 6:
        print("timeq - Program generating an estimate of the Time Equation")
        print()
        print("Usage:")
        print()
        print("  ./timeq <Lat> <Lon> <Fuse> <Year> <Out_File>")
        print()
        print("where")
        print()
        print("  <Lat>, the latitude, is positive and increasing northwards (decimal degrees)")
        print("  <Lon>, longitude, is positive and increasing eastwards (decimal degrees)")
        print("  <Fuse> is an integer indicating the hours displacement from GMT")
        print("  <Year> is an integer designating the year for which processing should occur")
        print("  <Out_File> is the output file name")
        print()
        print("Copyright 2019 by Mauri Favaron")
        print("This is open-source code, covered by the MIT license")
        print()
        sys.exit(1)
    lat   = float(sys.argv[1])
    lon   = float(sys.argv[2])
    fuse  = int(sys.argv[3])
    year  = int(sys.argv[4])
    out   = sys.argv[5]

    # Main loop: Iterate over all days in dsired year, and process them
    initial_date = np.datetime64("%4.4d-01-01T00:00:00" % year, 's')
    final_date   = np.datetime64("%4.4d-01-01T00:00:00" % (year+1), 's')
    num_days     = ((final_date - initial_date) / np.timedelta64(1, 'D')).astype(int)
    days         = np.array([np.datetime64('2000-01-01', 'D') for i in range(num_days)])
    time_eq      = np.array([0.0 for i in range(num_days)])
    for day in range(num_days):

        start_of_day = initial_date + np.timedelta64(day, 'D')
        print(start_of_day)

        # Compute extraterrestrial radiation for all seconds in this day
        time_stamp = np.array([start_of_day + np.timedelta64(sec, 's') for sec in range(86400)])
        ra         = radest.ExtraterrestrialRadiation(time_stamp, 1, lat, lon, fuse)

        # Find the index corresponding to the maximum extraterrestrial radiation
        # and use it to calculate the time stamp at which it occurs
        idx_max_ra  = np.argmax(ra)
        time_max_ra = time_stamp[idx_max_ra]

        # Compute difference from noon, and save it
        noon = start_of_day + np.timedelta64(12, 'h')
        days[day]    = start_of_day
        time_eq[day] = (time_max_ra - noon) / np.timedelta64(1, 's')

    # Print results
    f = open(out, "w")
    f.write("date, tm.eqn\n")
    for i in range(len(days)):
        f.write("%s, %f\n" % (str(days[i]), time_eq[i]))
    f.close()
