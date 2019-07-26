# coding: utf-8

"""
    Test for the solar radiation model, based on Duffie, J.A., and
    Beckman, W. A., 1974, "Solar energy thermal processes"
"""

import solar_radiation as sr
from solar_radiation import NoSunsetNoSunrise

import numpy as np
from numpy.testing import (assert_equal, assert_almost_equal,
                           assert_array_almost_equal)
import unittest as ut


class Test_Ranges(ut.TestCase):
    """
    Tests ranges checks
    """
    def test_nth_day_range(self):
        self.assertRaises(ValueError, sr.check_nth_day_range, 0)
        self.assertRaises(ValueError, sr.check_nth_day_range, 366)

    def test_latitude_range(self):
        self.assertRaises(ValueError, sr.check_latitude_range, -91)
        self.assertRaises(ValueError, sr.check_latitude_range, 91)

    def test_longitude_range(self):
        self.assertRaises(ValueError, sr.check_longitude_range, -1)
        self.assertRaises(ValueError, sr.check_longitude_range, 360)


class Test_day_of_the_year(ut.TestCase):
    """
    Tests day of the year values.
    """
    def test_month_range(self):
        self.assertRaises(ValueError, sr.day_of_the_year, 0, 1)
        self.assertRaises(ValueError, sr.day_of_the_year, 13, 1)

    def test_day_range(self):
        self.assertRaises(ValueError, sr.day_of_the_year, 1, 0)  # Jan 0?
        self.assertRaises(ValueError, sr.day_of_the_year, 1, 32)  # Jan 32?
        self.assertRaises(ValueError, sr.day_of_the_year, 2, 31)  # Feb 31?

    def test_Jan1(self):
        month, day = 1, 1
        expected_value = 1  # January 1
        self.assertEqual(sr.day_of_the_year(month, day), expected_value)

    def test_Feb1(self):
        month, day = 2, 1
        expected_value = 32  # February 1
        self.assertEqual(sr.day_of_the_year(month, day), expected_value)

    def test_summerSolstice(self):
        month, day = 6, 20
        expected_value = 171  # summer solstice
        self.assertEqual(sr.day_of_the_year(month, day), expected_value)

    def test_Dec31(self):
        month, day = 12, 31
        expected_value = 365  # December 31
        self.assertEqual(sr.day_of_the_year(month, day), expected_value)


def test_B_nth_day():
    """
    Tests B(n) values.
    """
    n = 1
    expected_value = 0
    assert_equal(sr.B_nth_day(n), expected_value)

    n = 365
    expected_value = 6.2659711
    assert_almost_equal(sr.B_nth_day(n), expected_value, 6)


class Test_Gon(ut.TestCase):
    """
    Tests radiation on a plane normal values.
    """
    def test_min(self):
        a = np.arange(1, 366)  # array with all days
        self.assertTrue((sr.Gon(a) > 1320).all())

    def test_max(self):
        a = np.arange(1, 366)  # array with all days
        self.assertTrue((sr.Gon(a) < 1420).all())

    def test_Jan1(self):
        n = 1  # January 1
        expected_value = 1415
        self.assertAlmostEqual(sr.Gon(n), expected_value, delta=1)

    def test_summerSolstice(self):
        n = 171  # July 21
        expected_value = 1322
        self.assertAlmostEqual(sr.Gon(n), expected_value, delta=1)


class Test_Eq_time(ut.TestCase):
    """
    Tests equation of time values.
    """
    def test_min(self):
        a = np.arange(1, 366)  # array with all days
        self.assertTrue((sr.Eq_time(a) > -15).all())

    def test_max(self):
        a = np.arange(1, 366)  # array with all days
        self.assertTrue((sr.Eq_time(a) < 17).all())

    def test_Jan1(self):
        n = 1  # January 1
        expected_value = -3
        self.assertAlmostEqual(sr.Eq_time(n), expected_value, delta=1)

    def test_summerSolstice(self):
        n = 171  # July 21
        expected_value = -1
        self.assertAlmostEqual(sr.Eq_time(n), expected_value, delta=1)


class Test_declination(ut.TestCase):
    """
    Tests equation of time values.
    """
    def test_min(self):
        a = np.arange(1, 366)  # array with all days
        self.assertTrue((np.rad2deg(sr.declination(a)) > -24).all())

    def test_max(self):
        a = np.arange(1, 366)  # array with all days
        self.assertTrue((np.rad2deg(sr.declination(a)) < 24).all())

    def test_Jan1(self):
        n = 1  # January 1
        expected_value = np.deg2rad(-23)
        self.assertAlmostEqual(sr.declination(n), expected_value, 1)

    def test_summerSolstice(self):
        n = 171  # July 21
        expected_value = np.deg2rad(23)
        self.assertAlmostEqual(sr.declination(n), expected_value, 1)

    def test_Feb13(self):  # Example 1.6.1
        n = 44  # February 13
        expected_value = np.deg2rad(-14)
        self.assertAlmostEqual(sr.declination(n), expected_value, 1)

    def test_Mar16(self):  # Example 1.6.3
        n = sr.day_of_the_year(3, 16)  # March 16
        expected_value = np.deg2rad(-2.4)
        self.assertAlmostEqual(sr.declination(n), expected_value, 1)


class Test_solar_time(ut.TestCase):
    """
    Tests solar time function. Values from Duffie and Beckman example 1.5.1
    """
    def test_errors(self):
        n = 34
        lng = 89.4
        self.assertRaises(ValueError, sr.solar_time, n, -1, 0, lng)
        self.assertRaises(ValueError, sr.solar_time, n, 24, 0, lng)
        self.assertRaises(ValueError, sr.solar_time, n, 0, -1, lng)
        self.assertRaises(ValueError, sr.solar_time, n, 0, 60, lng)

    def test_Feb3(self):
        n = 34
        t_std_h, t_std_min = 10, 30  # standard time (hour, minute)
        lng = 89.4
        expected_value = (10, 18, 54)
        self.assertEqual(sr.solar_time(n, t_std_h, t_std_min, lng),
                         expected_value)


class Test_hour_angle(ut.TestCase):
    """
    Tests hour angle function. Values from Duffie and Beckman
    """
    def test_errors(self):
        self.assertRaises(ValueError, sr.hour_angle, -1, 0)
        self.assertRaises(ValueError, sr.hour_angle, 24, 0)
        self.assertRaises(ValueError, sr.hour_angle, 0, -1)
        self.assertRaises(ValueError, sr.hour_angle, 0, 60)

    def test_examples(self):
        # noon
        hour, minute = 12, 0
        expected_value = np.deg2rad(0)
        self.assertEqual(sr.hour_angle(hour, minute), expected_value)

        # Example 1.6.1
        hour, minute = 10, 30
        expected_value = np.deg2rad(-22.5)
        self.assertEqual(sr.hour_angle(hour, minute), expected_value)

        # Example 1.6.2a
        hour, minute = 9, 30
        expected_value = np.deg2rad(-37.5)
        self.assertEqual(sr.hour_angle(hour, minute), expected_value)

        # Example 1.6.2b
        hour, minute = 18, 30
        expected_value = np.deg2rad(97.5)
        self.assertEqual(sr.hour_angle(hour, minute), expected_value)

        # Example 1.6.3
        hour, minute = 16, 0
        expected_value = np.deg2rad(60)
        self.assertEqual(sr.hour_angle(hour, minute), expected_value)

        # Example 1.7.1
        hour, minute = 14, 0
        expected_value = np.deg2rad(30)
        self.assertEqual(sr.hour_angle(hour, minute), expected_value)


def test_angle_of_incidence():
    """
    Tests angle of incidence function. Values from Duffie and Beckman
    example 1.6.1
    """
    n = 44
    lat = 43
    beta = 45
    surf_az = 15
    hour, minute = 10, 30
    expected_value = np.deg2rad(35)
    assert_almost_equal(sr.theta(n, lat, beta, surf_az, hour, minute),
                        expected_value, decimal=3)


def test_zenith_angle():
    """
    Tests zenith angle function. Values from Duffie and Beckman
    """
    # noon at summer solstice and lat = 23.4º
    n = 171
    lat = 23.45
    hour, minute = 12, 0
    expected_value = np.deg2rad(0)
    assert_almost_equal(sr.theta_z(n, lat, hour, minute),
                        expected_value, decimal=2)

    # Example 1.6.2a
    n = 44
    lat = 43
    hour, minute = 9, 30
    expected_value = np.deg2rad(66.5)
    assert_almost_equal(sr.theta_z(n, lat, hour, minute),
                        expected_value, decimal=2)

    # Example 1.6.2b
    n = sr.day_of_the_year(7, 1)
    lat = 43
    hour, minute = 18, 30
    expected_value = np.deg2rad(79.6)
    assert_almost_equal(sr.theta_z(n, lat, hour, minute),
                        expected_value, decimal=2)

    # Example 1.6.3
    n = sr.day_of_the_year(3, 16)
    lat = 43
    hour, minute = 16, 0
    expected_value = np.deg2rad(70.3)
    assert_almost_equal(sr.theta_z(n, lat, hour, minute),
                        expected_value, decimal=2)


def test_solar_azimuth():
    """
    Tests solar azimuth angle function. Values from Duffie and Beckman
    """
    # different values of (n, lat) at noon
    hour, minute = 12, 0

    expected_value = np.deg2rad(0)
    n, lat = 1, 0
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)
    n, lat = 90, 30
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)
    n, lat = 180, 60
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)
    n, lat = 270, 90
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)

    expected_value = np.deg2rad(180)
    n, lat = 90, -30
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)
    n, lat = 180, -60
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)
    n, lat = 270, -90
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)

    # Example 1.6.2a
    n = 44
    lat = 43
    hour, minute = 9, 30
    expected_value = np.deg2rad(-40.0)
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)

    # Example 1.6.2b
    n = sr.day_of_the_year(7, 1)
    lat = 43
    hour, minute = 18, 30
    expected_value = np.deg2rad(112.0)
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)

    # Example 1.6.3
    n = sr.day_of_the_year(3, 16)
    lat = 43
    hour, minute = 16, 0
    expected_value = np.deg2rad(66.8)
    assert_almost_equal(sr.solar_azimuth(n, lat, hour, minute),
                        expected_value, decimal=2)


def test_solar_altitude():
    """
    Tests solar azimuth angle function. Values from Duffie and Beckman
    """
    # Example 1.6.3
    n = sr.day_of_the_year(3, 16)
    lat = 43
    hour, minute = 16, 0
    expected_value = np.deg2rad(19.7)
    assert_almost_equal(sr.solar_altitude(n, lat, hour, minute),
                        expected_value, decimal=2)


class Test_sunset_hour_angle(ut.TestCase):
    """
    Tests sunset hour angle function. Values from Duffie and Beckman
    """
    def test_errors(self):
        self.assertRaises(NoSunsetNoSunrise, sr.sunset_hour_angle, 1, 80)
        self.assertRaises(NoSunsetNoSunrise, sr.sunset_hour_angle, 171, -75)

    def test_examples(self):
        # Example 1.6.3
        n = sr.day_of_the_year(3, 16)
        lat = 43
        expected_value = np.deg2rad(87.8)
        self.assertAlmostEqual(sr.sunset_hour_angle(n, lat), expected_value, 1)


class Test_sunset_time(ut.TestCase):
    """
    Tests sunset time function. Values from Duffie and Beckman
    """
    def test_examples(self):
        # Example 1.6.3
        n = sr.day_of_the_year(3, 16)
        lat = 43
        expected_value = 17
        self.assertAlmostEqual(sr.sunset_time(n, lat).hour,
                               expected_value, 2)
        expected_value = 52  # diferent year than boook!
        self.assertAlmostEqual(sr.sunset_time(n, lat).minute,
                               expected_value, 2)


class Test_sunrise_hour_angle(ut.TestCase):
    """
    Tests sunrise hour angle function. Values from Duffie and Beckman
    """
    def test_errors(self):
        self.assertRaises(NoSunsetNoSunrise, sr.sunrise_hour_angle, 1, 80)
        self.assertRaises(NoSunsetNoSunrise, sr.sunrise_hour_angle, 171, -75)

    def test_examples(self):
        # Example 1.6.3
        n = sr.day_of_the_year(3, 16)
        lat = 43
        expected_value = np.deg2rad(-87.8)
        self.assertAlmostEqual(sr.sunrise_hour_angle(n, lat),
                               expected_value, 1)


class Test_sunrise_time(ut.TestCase):
    """
    Tests sunrise time function. Values from Duffie and Beckman
    """
    def test_examples(self):
        # Example 1.6.3
        n = sr.day_of_the_year(3, 16)
        lat = 43
        expected_value = 6
        self.assertAlmostEqual(sr.sunrise_time(n, lat).hour,
                               expected_value, 2)
        expected_value = 7  # diferent year than boook!
        self.assertAlmostEqual(sr.sunrise_time(n, lat).minute,
                               expected_value, 2)


def test_daylight_hours():
    """
    Tests daylight hours function
    """
    # South Pole in the summer
    n = 1
    lat = -80
    expected_value = 24
    assert_almost_equal(sr.daylight_hours(n, lat), expected_value)

    # South Pole in the winter
    n = 180
    lat = -85
    expected_value = 0
    assert_almost_equal(sr.daylight_hours(n, lat), expected_value)

    # North Pole in the winter
    n = 1
    lat = 82
    expected_value = 0
    assert_almost_equal(sr.daylight_hours(n, lat), expected_value)

    # North Pole in the summer
    n = 180
    lat = 78
    expected_value = 24
    assert_almost_equal(sr.daylight_hours(n, lat), expected_value)

    # Equator in the summer
    n = 185
    lat = 0
    expected_value = 12
    assert_almost_equal(sr.daylight_hours(n, lat), expected_value)

    # Equator in the winter
    n = 350
    lat = 0
    expected_value = 12
    assert_almost_equal(sr.daylight_hours(n, lat), expected_value)


def test_lla2ecef():
    """
    Test function that returns ecef position from lat, long, altitude
    """
    a = 6378137  # [m] Earth equatorial axis
    b = 6356752.3142  # [m] Earth polar axis

    # OX-axis
    lat = 0
    lng = 0
    h = 0
    expected_value = np.array([a, 0, 0])
    assert_array_almost_equal(sr.lla2ecef(lat, lng, h), expected_value, 4)

    lat = 0
    lng = 180
    h = 0
    expected_value = np.array([-a, 0, 0])
    assert_array_almost_equal(sr.lla2ecef(lat, lng, h), expected_value, 4)

    # OY-axis
    lat = 0
    lng = 90
    h = 0
    expected_value = np.array([0, a, 0])
    assert_array_almost_equal(sr.lla2ecef(lat, lng, h), expected_value, 4)

    lat = 0
    lng = 270
    h = 0
    expected_value = np.array([0, -a, 0])
    assert_array_almost_equal(sr.lla2ecef(lat, lng, h), expected_value, 4)

    # OZ-axis
    lat = 90
    lng = 0
    h = 0
    expected_value = np.array([0, 0, b])
    assert_array_almost_equal(sr.lla2ecef(lat, lng, h), expected_value, 4)

    lat = -90
    lng = 0
    h = 0
    expected_value = np.array([0, 0, -b])
    assert_array_almost_equal(sr.lla2ecef(lat, lng, h), expected_value, 4)


def test_ned2ecef():
    """
    Test function that transforms ned-basis vectors to ecef-basis
    """
    lat, lng = 0, 0

    v_ned = np.array([1, 0, 0])
    expected_value = np.array([0, 0, 1])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    v_ned = np.array([0, 1, 0])
    expected_value = np.array([0, 1, 0])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    v_ned = np.array([0, 0, 1])
    expected_value = np.array([-1, 0, 0])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    lat, lng = 0, 90

    v_ned = np.array([1, 0, 0])
    expected_value = np.array([0, 0, 1])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    v_ned = np.array([0, 1, 0])
    expected_value = np.array([-1, 0, 0])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    v_ned = np.array([0, 0, 1])
    expected_value = np.array([0, -1, 0])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    lat, lng = 90, 0

    v_ned = np.array([1, 0, 0])
    expected_value = np.array([-1, 0, 0])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    v_ned = np.array([0, 1, 0])
    expected_value = np.array([0, 1, 0])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)

    v_ned = np.array([0, 0, 1])
    expected_value = np.array([0, 0, -1])
    assert_array_almost_equal(sr.ned2ecef(v_ned, lat, lng), expected_value)


def test_solar_vector_NED():
    """
    Test function that calculates solar vector in ned frame
    """
    # summer solstice, solar noon, lat=declination
    n = sr.day_of_the_year(6, 21)   # June 21
    lat = 23 + 26/60 + 14/3600  # obliquity in 2019
    hour, minute = 12, 0
    expected_value = np.array([0, 0, -1])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # permanent darkness: south pole in winter
    n = 165
    lat = -80
    hour, minute = 12, 0
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 200
    lat = -70
    hour, minute = 17, 0
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # permanent darkness: north pole in winter
    n = 1
    lat = 83
    hour, minute = 10, 0
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 300
    lat = 76
    hour, minute = 19, 0
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # night: north hemisphere
    n = 5
    lat = 33
    ss_t = sr.sunset_time(n, lat)
    hour, minute = ss_t.hour, ss_t.minute + 1  # 1min after sunset
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 210
    lat = 15
    sr_t = sr.sunrise_time(n, lat)
    hour, minute = sr_t.hour, sr_t.minute - 1  # 1min before sunrise
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # night: south hemisphere
    n = 34
    lat = -63
    ss_t = sr.sunset_time(n, lat)
    hour, minute = ss_t.hour, ss_t.minute + 1  # 1min after sunset
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 264
    lat = -15
    sr_t = sr.sunrise_time(n, lat)
    hour, minute = sr_t.hour, sr_t.minute - 1  # 1min before sunrise
    expected_value = np.array([0, 0, 0])
    assert_array_almost_equal(sr.solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)


class Test_air_mass_KY1989(ut.TestCase):
    """
    Tests air mass function based on the work of Kasten and Young (1989)
    """
    def test_errors(self):
        self.assertRaises(ValueError, sr.air_mass_KastenYoung1989, 0, -1)

    def test_limit_values(self):
        # air mass through zenit direction at sea level
        theta_z = 0
        h = 0
        expected_value = 1
        self.assertAlmostEqual(sr.air_mass_KastenYoung1989(theta_z, h),
                               expected_value, 3)

        # air mass through zenit direction at exosphere
        theta_z = 0
        h = 1e8  # 10.000 km
        expected_value = 0
        self.assertAlmostEqual(sr.air_mass_KastenYoung1989(theta_z, h),
                               expected_value)

        # model limits (zenith=91.5)
        theta_z = 94
        h = 0
        expected_value = sr.air_mass_KastenYoung1989(91.5, h)
        self.assertEqual(sr.air_mass_KastenYoung1989(theta_z, h),
                         expected_value)


class Test_beam_irradiance(ut.TestCase):
    """
    Tests beam_irradiance function based on the work of Aglietti et al (2009)
    """
    def test_errors(self):
        # erroneus altitud
        h = -10
        n = 171
        lat = -63
        hour, minute = 10, 0
        self.assertRaises(ValueError, sr.beam_irradiance, h, n, lat,
                                                          hour, minute)

        # erroneus day of the year
        h = 0
        n = 367
        lat = -63
        hour, minute = 10, 0
        self.assertRaises(ValueError, sr.beam_irradiance, h, n, lat,
                                                          hour, minute)

        # erroneus latitude
        h = 0
        n = 171
        lat = -91
        hour, minute = 10, 0
        self.assertRaises(ValueError, sr.beam_irradiance, h, n, lat,
                                                          hour, minute)

    def test_limit_values(self):
        # sun below the horizon
        h = 0
        n = 171
        lat = -67
        hour, minute = 12, 0
        expected_value = 0
        self.assertEqual(sr.beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        h = 10000
        n = 1
        lat = 87
        hour, minute = 12, 0
        expected_value = 0
        self.assertEqual(sr.beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        # north pole winter nigth
        h = 1000
        n = 320
        lat = 80
        hour, minute = 5, 0
        expected_value = 0
        self.assertEqual(sr.beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        # south pole winter nigth
        h = 5000
        n = 150
        lat = -85
        hour, minute = 22, 0
        expected_value = 0
        self.assertEqual(sr.beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        # TODO: more test!