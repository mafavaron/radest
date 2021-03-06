#!/usr/bin/env python3

# radest.py - Pure Python module, providing simple estimate og
#             global (inbound short-wave) solar radiation
# given the station time stamps, geographical position and
# height above ground.
#
# Original Fortran code from:
#
#   https://github.com/serv_terr/pbl_met
#
# This code's location:
#
#   https://github.com/mafavaron/radest
#
# This is open-source software, covered by the MIT license.
# Copyright information and license text follow.

# Copyright 2019 Mauri Favaron
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall
# be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


import math
import numpy as np


def DoY(time_stamp):
    """ Computes day-of-year.

    Parameters
    ----------

    time_stamp : numpp.array(numpy.datetime64)
        Vector, containing the time stamps to be processed.

    Returns

    numpy.array(int)
        Vector, containing day of year for each input time stamps,
        in same order.
    """

    base_time = time_stamp.astype('datetime64[Y]')
    delta_times = (time_stamp - base_time)
    num_days  = (delta_times/np.timedelta64(1,'D')).astype(int) + 1

    return num_days


def calcJD(time_stamp):
    """Computes the Julian Day

    Parameters
    ----------

    time_stamp : numpp.array(numpy.datetime64)
        Vector, containing the time stamps to be processed.

    Returns

    numpy.array(int)
        Vector, containing the julian day for each input time stamps,
        in same order.
    """

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


def ExtraterrestrialRadiation(time_stamp, averaging_period, lat, lon, zone):
    """Estimates extraterrestrial solar radiation by ASCE method

    Parameters
    ----------

    timeStamp : numpy.array(numpy.datetime64)
        Anticipated time stamp of period to get radiation at

    averagingPeriod : int
        Length of period (s)

    lat : double
        Local latitude(degrees, positive northwards)

    lon : double
        Local longitude(degrees, positive eastwards)

    zone : int
        Time zone number(hours, positive Eastwards, in range - 12 to 12)

    Returns
    -------

    numpy.array(double)
        Vector containing extraterrestrial radiation (W/m2)
    """

    # Constants
    SOLAR_CONSTANT = 1.e5 * 49.2/3600   # W/m2

    # Calculate the day-in-year and solar declination
    doy = DoY(time_stamp)
    solar_declination = 0.409 * np.sin(2*np.pi /365 * doy - 1.39)

    # Compute Julian day
    day_start = np.array([np.datetime64(time_stamp[i], 'D') for i in range(len(time_stamp))])
    one_hour  = np.timedelta64(3600,'s')
    timenow   = (time_stamp - day_start)/one_hour
    timenow   -= zone
    JD = calcJD(time_stamp)

    # Inverse squared relative distance factor for Sun-Earth
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
    delta_lon = math.fabs(central_meridian_longitude - local_longitude) % 360.0
    if delta_lon > 180.0:
        intermediate = 360.0 - delta_lon
    else:
        intermediate = delta_lon
    if ((delta_lon > 0.0) and (delta_lon <= 180.0)) or ((delta_lon <= -180.0) and (delta_lon >= -360.0)):
        sign =  1.0
    else:
        sign = -1.0
    delta_lon = sign * intermediate
    omega = (np.pi / 12.0) * ((t + 0.06667 * delta_lon + Sc) - 12.0)

    # Solar time angle at beginning and end of averaging period
    omega1 = omega - np.pi * t1 / 24.0
    omega2 = omega + np.pi * t1 / 24.0

    # Adjust angular end points to exclude nighttime hours
    omegaS = np.arccos(-np.tan(lat * np.pi / 180.0) * np.tan(solar_declination))    # Sunset angle
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


def GlobalRadiation(ra, z):
    """Reduce extraterrestrial radiation to in-atmosphere value

    Parameters
    ----------

    ra : numpy.array(double)
        Estimate of extraterrestrial radiation (W/m2)

    z : double
        Height above mean sea level (m)

    Returns
    -------

    numpy.array(double)
        Estimate of global solar radiation (W/m2)
    """

    rg = ra * (0.75 + 2.0e-5*z)

    return rg


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

    # Test 9: Single-date Global Radiation, checking height effect, summer time, mid latitude, Northern
    day = np.array([np.datetime64('2019-07-01T12:00:00')])
    lon = 0.0008
    print('=================================================')
    print()
    print("Test no.7 - Exraterrestrial Radiation computed at noon, various longitudes, lat=45, on 01. 07. 2019")
    print()
    Ra = ExtraterrestrialRadiation(day, 3600, 45.0, 9.0, 0.0)
    for i in range(20):
        z = i * 100
        Rg = GlobalRadiation(Ra, z)
        print("%f -> %f" % (z, Rg[0]))
    print()

    # Prepare to leave
    print('=================================================')
