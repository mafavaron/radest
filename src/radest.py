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
    SOLAR_CONSTANT = 1.e6 * 49.2/3600   # W/m2

    # Calcunate the day-in-year and solar declination
    doy = DoY(time_stamp)
    solar_declination = 0.409 * np.sin(2*np.pi /365 * doy - 1.39)

    # Compute Julian day
    timenow = (time_stamp - np.datetime64(time_stamp, 'D'))/np.timedelta(3600.0,'s') - zone
    JD = calcJD(time_stamp)

    # Inverse squared relative distance factor for Su n -Earth
    dr = 1.0 + 0.033 * np.cos(2.0 * np.pi * doy / 365.0)

    # Calculate geographical positioning parameters (with a "-" sign for longitudes, according to ASCE conventions)
    central_meridian_longitude = -zone * 15.0
    if central_meridian_longitude < 0.0:
        central_meridian_longitude += 360.0
    local_longitude = -lon
    if local_longitude < 0.0:
        local_longitude += 360.0

    # Compute hour at mid of averaging time
    t1 = averaging_period / 3600.0
    t = timenow + zone + 0.5 * t1

    # Calculate seasonal correction for solar time
    b = 2.0 * np.pi * (doy - 81) / 364.0
    Sc = 0.1645 * np.sin(2.0 * b) - 0.1255 * np.cos(b) - 0.025 * np.sin(b)

    # Solar time angle at midpoint of averaging time
    omega = (np.pi / 12.0) * ((t + 0.06667 * (central_meridian_longitude - local_longitude) + Sc) - 12.0)

    # Solar time angle at beginning and end of averaging period
    omega1 = omega - np.pi * t1 / 24.0
    omega2 = omega + np.pi * t1 / 24.0

    # Adjust angular end points to exclude nighttime hours
    omegaS = np.acos(-np.tan(lat * np.pi / 180.0) * np.tan(solar_declination))    # Sunset angle
    if omega1 < -omegaS:
        omega1 = -omegaS
    if omega2 < -omegaS:
        omega2 = -omegaS
    if omega1 > omegaS:
        omega1 = omegaS
    if omega2 > omegaS:
        omega2 = omegaS
    if omega1 > omega2:
        omega1 = omega2

    # Compute extraterrestrial radiation
    ra = 12.0 / np.pi * SOLAR_CONSTANT * dr * (
        (omega2-omega1) * np.sin(lat * np.pi / 180.0) * np.sin(solar_declination) +
        np.cos(lat * np.pi / 180.0) * np.cos(solar_declination) * (np.sin(omega2) - np.sin(omega1))
    )

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

    # Prepare to leave
    print('=================================================')
