#!/usr/bin/env python3

import os
import sys
import numpy as np

def DoY(time_stamp):

    base_time = time_stamp.astype('datetime64[Y]')
    delta_times = (time_stamp - base_time)
    num_days  = (delta_times/np.timedelta64(1,'D')).astype(int) + 1

    return num_days


def calcJD(time_stamp):

    # Get date parts
    yy = time_stamp.astype('datetime64[Y]').astype(int) + 1970
    mm = time_stamp.astype('datetime64[M]').astype(int) % 12 + 1
    dd = ((time_stamp - time_stamp.astype('datetime64[M]')) / np.timedelta64(1,'D') + 1).astype(int)

    # Compute Julian days
    yy = np.where(mm <= 2, yy-1, yy)
    mm = np.where(mm <= 2, mm+12, mm)
    A  = yy // 100
    B  = 2 - A + A//4
    jd = (np.floor(365.25*(yy + 4716)) + np.floor(30.6001*(mm+1)) + dd + B - 1524.5).astype(int)

    return jd


# Estimate of extraterrestrial solar radiation
#
# Input:
#
#    timeStamp        np.datetime64, identifying the initial instant to get radiation at
#
#    averagingPeriod  Integer, length of averaging period (s)
#
#    lat              Real, local latitude(degrees, positive northwards)
#
#    lon              Real, local longitude(degrees, positive eastwards)
#
#    zone             Integer, time zone number(hours, positive Eastwards, in range - 12 to 12)
#
# Output:
#
#    ra               Extraterrestrial radiation (W/m2)
#
def ExtraterrestrialRadiation(time_stamp, averaging_period, lat, lon, zone):

    # Constants
    SOLAR_CONSTANT = 1.e5 * 49.2/3600   # W/m2

    # Calcunate the day-in-year and solar declination
    doy = DoY(time_stamp)
    solar_declination = 0.409 * np.sin(2*np.pi /365 * doy - 1.39)
    print("Solar declination: %f" % solar_declination[0])

    # Compute Julian day
    day_start = np.array([np.datetime64(time_stamp[i], 'D') for i in range(len(time_stamp))])
    one_hour  = np.timedelta64(3600,'s')
    timenow   = (time_stamp - day_start)/one_hour
    timenow   -= zone
    JD = calcJD(time_stamp)
    print("Current time in hours: %f" % timenow[0])
    print("Julian day: %d" % JD[0])

    # Inverse squared relative distance factor for Sun-Earth
    dr = 1.0 + 0.033 * np.cos(2.0 * np.pi * doy / 365.0)
    print("Sun-Earth coeff: %f" % dr[0])

    # Calculate geographical positioning parameters (with a "-" sign for longitudes, according to ASCE conventions)
    central_meridian_longitude = -zone * 15.0
    if central_meridian_longitude < 0.0:
        central_meridian_longitude += 360.0
    print("Central meridian lon: %f" % central_meridian_longitude)
    local_longitude = -lon
    if local_longitude < 0.0:
        local_longitude += 360.0
    print("Local lon: %f" % local_longitude)

    # Compute hour at mid of averaging time
    t1 = averaging_period / 3600.0
    t = timenow + zone + 0.5 * t1
    print("Current time in hours: %f" % t[0])

    # Calculate seasonal correction for solar time
    b = 2.0 * np.pi * (doy - 81) / 364.0
    Sc = 0.1645 * np.sin(2.0 * b) - 0.1255 * np.cos(b) - 0.025 * np.sin(b)
    print("Seasonal correction: %f" % Sc[0])

    # Solar time angle at midpoint of averaging time
    delta_lon = central_meridian_longitude - local_longitude
    if delta_lon > 180.0:
        delta_lon -= 360.0
    omega = (np.pi / 12.0) * ((t + 0.06667 * delta_lon + Sc) - 12.0)

    # Solar time angle at beginning and end of averaging period
    omega1 = omega - np.pi * t1 / 24.0
    omega2 = omega + np.pi * t1 / 24.0

    # Adjust angular end points to exclude nighttime hours
    omegaS = np.arccos(-np.tan(lat * np.pi / 180.0) * np.tan(solar_declination))    # Sunset angle
    print("Omega: %f - %f - (%f,%f)" % (omega[0],omegaS[0],omega1[0],omega2[0]))
    for i in range(len(omegaS)):
        if omega1[i] < -omegaS[i]:
            omega1[i] = -omegaS[i]
        if omega2[i] < -omegaS[i]:
            omega2[i] = -omegaS[i]
        if omega1[i] > omegaS[i]:
            omega1[i] = omegaS[i]
        if omega2[i] > omegaS[i]:
            omega2[i] = omegaS[i]
        if omega1[i] > omega2[i]:
            omega1[i] = omega2[i]

    # Compute extraterrestrial radiation
    ra = 12.0 / np.pi * SOLAR_CONSTANT * dr * (
        (omega2-omega1) * np.sin(lat * np.pi / 180.0) * np.sin(solar_declination) +
        np.cos(lat * np.pi / 180.0) * np.cos(solar_declination) * (np.sin(omega2) - np.sin(omega1))
    )

    # Zero-limit
    ra = np.where(ra < 0., 0., ra)

    return ra


if __name__ == "__main__":

    # Test 1: DoY
    day = np.datetime64('2019-03-08')
    print('=================================================')
    print()
    print("Test no.1 - DoY applied to regular date")
    print()
    print("Date: %s" % str(day))
    print("Expected DoY: 67")
    print("Actual DoY:   %d" % DoY(day))
    print()

    # Test 2: Multi-date DoY
    day = np.array([np.datetime64('2019-03-08') + np.timedelta64(i, 'D') for i in range(3)])
    print('=================================================')
    print()
    print("Test no.2 - DoY applied to more regular dates")
    print()
    print("Date: %s" % str(day))
    print("Expected DoY: 67, 68, 69")
    print("Actual DoY:   %s" % str(DoY(day)))
    print()

    # Test 3: Multi-date calcJD
    day = np.array([np.datetime64('2019-03-08') + np.timedelta64(i, 'D') for i in range(3)])
    print('=================================================')
    print()
    print("Test no.3 - calcJD applied to more regular dates")
    print()
    print("Date: %s" % str(day))
    print("Actual DoY:   %s" % str(calcJD(day)))
    print()

    # Test 4: Multi-date Extraterrestrial Radiation
    day = np.array([np.datetime64('2019-03-08') + np.timedelta64(i, 'h') for i in range(24)])
    print('=================================================')
    print()
    print("Test no.4 - Exraterrestrial Radiation computed on a day, hourly step")
    print()
    Ra = ExtraterrestrialRadiation(day, 3600, 45.5, 9.5, 1.0)
    for i in range(len(day)):
        print("%s -> %f" % (str(day[i]), Ra[i]))
    print()

    # Test 5: Single-date Extraterrestrial Radiation, checking latitude effect, winter time
    day = np.array([np.datetime64('2019-01-01T12:00:00')])
    lat = [-90.0 + i for i in range(181)]
    print('=================================================')
    print()
    print("Test no.5 - Exraterrestrial Radiation computed at noon, various latitudes, on 01. 01. 2019")
    print()
    for i in range(len(lat)):
        Ra = ExtraterrestrialRadiation(day, 3600, lat[i], 9.5, 1.0)
        print("%f -> %f" % (lat[i], Ra[0]))
    print()

    # Test 6: Single-date Extraterrestrial Radiation, checking latitude effect, summer time
    day = np.array([np.datetime64('2019-07-01T12:00:00')])
    lat = [-90.0 + i for i in range(181)]
    print('=================================================')
    print()
    print("Test no.6 - Exraterrestrial Radiation computed at noon, various latitudes, on 01. 07. 2019")
    print()
    for i in range(len(lat)):
        Ra = ExtraterrestrialRadiation(day, 3600, lat[i], 9.5, 1.0)
        print("%f -> %f" % (lat[i], Ra[0]))
    print()

    # Test 7: Single-date Extraterrestrial Radiation, checking longitude effect, summer time, mid latitude, Northern
    day = np.array([np.datetime64('2019-07-01T12:00:00')])
    lon = [-180.0 + i for i in range(361)]
    print('=================================================')
    print()
    print("Test no.7 - Exraterrestrial Radiation computed at noon, various longitudes, lat=45, on 01. 07. 2019")
    print()
    for i in range(len(lon)):
        Ra = ExtraterrestrialRadiation(day, 3600, 45.0, lon[i], 0.0)
        print("%f -> %f" % (lon[i], Ra[0]))
    print()

    # Test 8: Single-date Extraterrestrial Radiation, checking one longitude effect, summer time, mid latitude, Northern
    day = np.array([np.datetime64('2019-07-01T12:00:00')])
    lon = 0.0008
    print('=================================================')
    print()
    print("Test no.7 - Exraterrestrial Radiation computed at noon, various longitudes, lat=45, on 01. 07. 2019")
    print()
    Ra = ExtraterrestrialRadiation(day, 3600, 45.0, lon, 0.0)
    print("Expected: non-zero")
    print("%f -> %f" % (lon, Ra[0]))
    print()

    # Prepare to leave
    print('=================================================')
