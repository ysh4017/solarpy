# coding: utf-8

"""
    Tests of the solar radiation model, based on Duffie, J.A., and
    Beckman, W. A., 1974, "Solar energy thermal processes"
"""


from solarpy.radiation import *
from numpy import sin, cos, deg2rad, rad2deg, array
from numpy.testing import (assert_equal, assert_almost_equal,
                           assert_array_almost_equal)
from datetime import datetime
import unittest as ut
import io
import sys


class Test_B_nth_day(ut.TestCase):
    """
    Tests B(n) values.
    """
    def test_single_days(self):
        date = datetime(2019, 1, 1)  # Jan 1
        expected_value = 0
        assert_equal(B_nth_day(date), expected_value)

        date = datetime(2019, 12, 31)  # Dec 31
        expected_value = 6.2659711
        assert_almost_equal(B_nth_day(date), expected_value, 6)

    def test_array(self):
        date = array([datetime(2019, 1, 1), datetime(2019, 12, 31)])
        expected_value = array([0, 6.2659711])
        assert_almost_equal(B_nth_day(date), expected_value, 6)

    def test_exception(self):
        self.assertRaises(TypeError, B_nth_day, 6)


class Test_Gon(ut.TestCase):
    """
    Tests radiation on a plane normal values.
    """
    def test_min(self):
        # array with all days
        dates = array([datetime(datetime.now().year, 1, 1) +
                       timedelta(days=i) for i in range(365)])
        self.assertTrue((Gon(dates) > 1320).all())

    def test_max(self):
        # array with all days
        dates = array([datetime(datetime.now().year, 1, 1) +
                       timedelta(days=i) for i in range(365)])
        self.assertTrue((Gon(dates) < 1420).all())

    def test_Jan1(self):
        date = datetime(2019, 1, 1)  # January 1
        expected_value = 1415
        self.assertAlmostEqual(Gon(date), expected_value, delta=1)

    def test_summerSolstice(self):
        date = datetime(2019, 6, 20)  # June 20
        expected_value = 1322
        self.assertAlmostEqual(Gon(date), expected_value, delta=1)

    def test_exception(self):
        self.assertRaises(TypeError, Gon, 'a')


class Test_Eq_time(ut.TestCase):
    """
    Tests equation of time values.
    """
    def test_min(self):
        # array with all days
        dates = array([datetime(datetime.now().year, 1, 1) +
                       timedelta(days=i) for i in range(365)])
        self.assertTrue((Eq_time(dates) > -15).all())

    def test_max(self):
        # array with all days
        dates = array([datetime(datetime.now().year, 1, 1) +
                       timedelta(days=i) for i in range(365)])
        self.assertTrue((Eq_time(dates) < 17).all())

    def test_Jan1(self):
        date = datetime(2019, 1, 1)  # January 1
        expected_value = -3
        self.assertAlmostEqual(Eq_time(date), expected_value, delta=1)

    def test_summerSolstice(self):
        date = datetime(2019, 6, 20)  # June 20
        expected_value = -1
        self.assertAlmostEqual(Eq_time(date), expected_value, delta=1)

    def test_exception(self):
        self.assertRaises(TypeError, Eq_time, 'a')


class Test_declination(ut.TestCase):
    """
    Tests equation of time values.
    """
    def test_min(self):
        # array with all days
        dates = array([datetime(datetime.now().year, 1, 1) +
                       timedelta(days=i) for i in range(365)])
        self.assertTrue((rad2deg(declination(dates)) > -24).all())

    def test_max(self):
        # array with all days
        dates = array([datetime(datetime.now().year, 1, 1) +
                       timedelta(days=i) for i in range(365)])
        self.assertTrue((rad2deg(declination(dates)) < 24).all())

    def test_Jan1(self):
        date = datetime(2019, 1, 1)  # January 1
        expected_value = deg2rad(-23)
        self.assertAlmostEqual(declination(date), expected_value, 1)

    def test_summerSolstice(self):
        date = datetime(2019, 6, 20)  # June 20
        expected_value = deg2rad(23)
        self.assertAlmostEqual(declination(date), expected_value, 1)

    def test_Feb13(self):  # Example 1.6.1
        date = datetime(2019, 2, 13)  # Feb 13
        expected_value = deg2rad(-14)
        self.assertAlmostEqual(declination(date), expected_value, 1)

    def test_Mar16(self):  # Example 1.6.3
        date = datetime(2019, 3, 16)  # March 16
        expected_value = deg2rad(-2.4)
        self.assertAlmostEqual(declination(date), expected_value, 1)

    def test_exception(self):
        self.assertRaises(TypeError, declination, 12)


class Test_solar_time(ut.TestCase):
    """
    Tests solar time function. Values from Duffie and Beckman example 1.5.1
    """
    def test_Feb3(self):
        lng = 89.4
        date = datetime(2019, 2, 3, 10, 30)  # standard time 10:30
        expected_value = datetime(2019, 2, 3, 10, 18, 54)
        # compare ignoring microseconds (as in the example)
        self.assertEqual(standard2solar_time(date, lng).replace(microsecond=0),
                         expected_value)

    def test_exception(self):
        self.assertRaises(TypeError, standard2solar_time, 12, 8.3)


class Test_hour_angle(ut.TestCase):
    """
    Tests hour angle function. Values from Duffie and Beckman
    """
    def test_examples(self):
        # noon
        date = datetime(2019, 1, 1, 12, 0)
        expected_value = deg2rad(0)
        self.assertEqual(hour_angle(date), expected_value)

        # Example 1.6.1
        date = datetime(2019, 1, 1, 10, 30)
        expected_value = deg2rad(-22.5)
        self.assertEqual(hour_angle(date), expected_value)

        # Example 1.6.2a
        date = datetime(2019, 1, 1, 9, 30)
        expected_value = deg2rad(-37.5)
        self.assertEqual(hour_angle(date), expected_value)

        # Example 1.6.2b
        date = datetime(2019, 1, 1, 18, 30)
        expected_value = deg2rad(97.5)
        self.assertEqual(hour_angle(date), expected_value)

        # Example 1.6.3
        date = datetime(2019, 1, 1, 16, 0)
        expected_value = deg2rad(60)
        self.assertEqual(hour_angle(date), expected_value)

        # Example 1.7.1
        date = datetime(2019, 1, 1, 14, 0)
        expected_value = deg2rad(30)
        self.assertEqual(hour_angle(date), expected_value)

    def test_exception(self):
        self.assertRaises(TypeError, hour_angle, 121)


class Test_angle_of_incidence(ut.TestCase):
    """
    Tests angle of incidence function. Values from Duffie and Beckman
    example 1.6.1
    """
    def test_example(self):
        date = datetime(2019, 2, 13, 10, 30)  # Feb 13, 10:30 am (solar)
        lat = 43
        beta = 45
        surf_az = 15
        expected_value = deg2rad(35)
        self.assertAlmostEqual(theta(date, lat, beta, surf_az),
                               expected_value, 2)

    def test_exception(self):
        self.assertRaises(TypeError, theta, 121, 1, 1, 1)


class Test_zenith_angle(ut.TestCase):
    """
    Tests zenith angle function. Values from Duffie and Beckman
    """
    def test_examples(self):
        # noon at summer solstice and lat = 23.4º
        date = datetime(2019, 6, 20, 12, 0)  # Jun 20, 12:00 am (solar)
        lat = 23.45
        expected_value = deg2rad(0)
        self.assertAlmostEqual(theta_z(date, lat), expected_value, 2)

        # Example 1.6.2a
        date = datetime(2019, 2, 13, 9, 30)  # Feb 13, 9:30 am (solar)
        lat = 43
        expected_value = deg2rad(66.5)
        self.assertAlmostEqual(theta_z(date, lat), expected_value, 2)

        # Example 1.6.2b
        date = datetime(2019, 7, 1, 18, 30)  # Jul 1, 18:30 am (solar)
        lat = 43
        expected_value = deg2rad(79.6)
        self.assertAlmostEqual(theta_z(date, lat), expected_value, 2)

        # Example 1.6.3
        date = datetime(2019, 3, 16, 16, 0)  # Mar 16, 16:00 am (solar)
        lat = 43
        expected_value = deg2rad(70.3)
        self.assertAlmostEqual(theta_z(date, lat), expected_value, 2)

    def test_exception(self):
        self.assertRaises(TypeError, theta_z, 121, 1)


class Test_solar_azimuth(ut.TestCase):
    """
    Tests solar azimuth angle function. Values from Duffie and Beckman
    """
    def test_noon(self):
        # different values of (date, lat) at noon
        hour, minute = 12, 0  # noon

        # northern hemisphere
        expected_value = deg2rad(0)

        date = datetime(2019, 1, 1, hour, minute)  # Jan 1
        lat = 0
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        date = datetime(2019, 4, 1, hour, minute)  # Apr 1
        lat = 30
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        date = datetime(2019, 8, 1, hour, minute)  # Aug 1
        lat = 60
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        date = datetime(2019, 10, 1, hour, minute)  # Oct 1
        lat = 90
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        # northern hemisphere
        expected_value = deg2rad(180)

        date = datetime(2019, 4, 1, hour, minute)  # Apr 1
        lat = -30
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        date = datetime(2019, 8, 1, hour, minute)  # Aug 1
        lat = -60
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        date = datetime(2019, 10, 1, hour, minute)  # Oct 1
        lat = -90
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

    def examples(self):
        # Example 1.6.2a
        date = datetime(2019, 2, 13, 9, 30)  # Feb 13, 9:30am
        lat = 43
        expected_value = deg2rad(-40.0)
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        # Example 1.6.2b
        date = datetime(2019, 7, 1, 18, 30)  # Jul 1, 1:30am
        lat = 43
        expected_value = deg2rad(112.0)
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

        # Example 1.6.3
        date = datetime(2019, 3, 16, 16, 0)  # Mar 16, 16:00am
        lat = 43
        expected_value = deg2rad(66.8)
        self.assertAlmostEqual(solar_azimuth(date, lat), expected_value, 2)

    def test_exception(self):
        self.assertRaises(TypeError, solar_azimuth, 121, 1)


class Test_solar_altitude(ut.TestCase):
    """
    Tests solar azimuth angle function. Values from Duffie and Beckman
    """
    def examples(self):
        # Example 1.6.3
        date = datetime(2019, 7, 1, 16, 0)  # Mar 16, 16:00am
        lat = 43
        expected_value = deg2rad(19.7)
        self.assertAlmostEqual(solar_altitude(date, lat), expected_value, 2)

    def test_exception(self):
        self.assertRaises(TypeError, solar_altitude, 121, 1)


class Test_sunset_hour_angle(ut.TestCase):
    """
    Tests sunset hour angle function. Values from Duffie and Beckman
    """
    def test_errors(self):
        date = datetime(2019, 1, 1)
        self.assertRaises(NoSunsetNoSunrise, sunset_hour_angle, date, 80)

        date = datetime(2019, 6, 20)
        self.assertRaises(NoSunsetNoSunrise, sunset_hour_angle, date, -75)

    def test_examples(self):
        # Example 1.6.3
        date = datetime(2019, 3, 16)
        lat = 43
        expected_value = deg2rad(87.8)
        self.assertAlmostEqual(sunset_hour_angle(date, lat), expected_value, 1)

    def test_exception(self):
        self.assertRaises(TypeError, sunset_hour_angle, 121, 1)


class Test_sunset_time(ut.TestCase):
    """
    Tests sunset time function. Values from Duffie and Beckman
    """
    def test_examples(self):
        # Example 1.6.3
        n = day_of_the_year(3, 16)
        lat = 43
        expected_value = 17
        self.assertAlmostEqual(sunset_time(n, lat).hour,
                               expected_value, 2)
        expected_value = 52  # diferent year than boook!
        self.assertAlmostEqual(sunset_time(n, lat).minute,
                               expected_value, 2)

    def test_NoSunsetNoSunrise(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        n = day_of_the_year(8, 1)  # summer
        lat = 89  # North-Pole
        msg = "Permanent night (or day) on this latitude on this day\n"
        sunset_time(n, lat)
        self.assertEqual(capturedOutput.getvalue(), msg)


class Test_sunrise_hour_angle(ut.TestCase):
    """
    Tests sunrise hour angle function. Values from Duffie and Beckman
    """
    def test_errors(self):
        self.assertRaises(NoSunsetNoSunrise, sunrise_hour_angle, 1, 80)
        self.assertRaises(NoSunsetNoSunrise, sunrise_hour_angle, 171, -75)

    def test_examples(self):
        # Example 1.6.3
        n = day_of_the_year(3, 16)
        lat = 43
        expected_value = deg2rad(-87.8)
        self.assertAlmostEqual(sunrise_hour_angle(n, lat),
                               expected_value, 1)


class Test_sunrise_time(ut.TestCase):
    """
    Tests sunrise time function. Values from Duffie and Beckman
    """
    def test_examples(self):
        # Example 1.6.3
        n = day_of_the_year(3, 16)
        lat = 43
        expected_value = 6
        self.assertAlmostEqual(sunrise_time(n, lat).hour,
                               expected_value, 2)
        expected_value = 7  # diferent year than boook!
        self.assertAlmostEqual(sunrise_time(n, lat).minute,
                               expected_value, 2)

    def test_NoSunsetNoSunrise(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        n = day_of_the_year(8, 1)  # summer
        lat = 89  # North-Pole
        msg = "Permanent night (or day) on this latitude on this day\n"
        sunrise_time(n, lat)
        self.assertEqual(capturedOutput.getvalue(), msg)


def test_daylight_hours():
    """
    Tests daylight hours function
    """
    # South Pole in the summer
    n = 1
    lat = -80
    expected_value = 24
    assert_almost_equal(daylight_hours(n, lat), expected_value)

    # South Pole in the winter
    n = 180
    lat = -85
    expected_value = 0
    assert_almost_equal(daylight_hours(n, lat), expected_value)

    # North Pole in the winter
    n = 1
    lat = 82
    expected_value = 0
    assert_almost_equal(daylight_hours(n, lat), expected_value)

    # North Pole in the summer
    n = 180
    lat = 78
    expected_value = 24
    assert_almost_equal(daylight_hours(n, lat), expected_value)

    # Equator in the summer
    n = 185
    lat = 0
    expected_value = 12
    assert_almost_equal(daylight_hours(n, lat), expected_value)

    # Equator in the winter
    n = 350
    lat = 0
    expected_value = 12
    assert_almost_equal(daylight_hours(n, lat), expected_value)


def test_solar_vector_NED():
    """
    Test function that calculates solar vector in ned frame
    """
    # summer solstice, solar noon, lat=declination
    n = day_of_the_year(6, 21)   # June 21
    lat = 23 + 26/60 + 14/3600  # obliquity in 2019
    hour, minute = 12, 0
    expected_value = array([0, 0, -1])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # permanent darkness: south pole in winter
    n = 165
    lat = -80
    hour, minute = 12, 0
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 200
    lat = -70
    hour, minute = 17, 0
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # permanent darkness: north pole in winter
    n = 1
    lat = 83
    hour, minute = 10, 0
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 300
    lat = 76
    hour, minute = 19, 0
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # night: north hemisphere
    n = 5
    lat = 33
    ss_t = sunset_time(n, lat)
    hour, minute = ss_t.hour, ss_t.minute + 1  # 1min after sunset
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 210
    lat = 15
    sr_t = sunrise_time(n, lat)
    hour, minute = sr_t.hour, sr_t.minute - 1  # 1min before sunrise
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # night: south hemisphere
    n = 34
    lat = -63
    ss_t = sunset_time(n, lat)
    hour, minute = ss_t.hour, ss_t.minute + 1  # 1min after sunset
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    n = 264
    lat = -15
    sr_t = sunrise_time(n, lat)
    hour, minute = sr_t.hour, sr_t.minute - 1  # 1min before sunrise
    expected_value = array([0, 0, 0])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)

    # permanent light
    n = day_of_the_year(6, 20)  # summer solstice
    lat = 90
    hour, minute = 12, 0  # solar noon
    alt = deg2rad(23 + 26/60 + 14/3600)
    expected_value = array([-cos(alt), 0, -sin(alt)])
    assert_array_almost_equal(solar_vector_NED(n, lat, hour, minute),
                              expected_value, 3)


class Test_air_mass_KY1989(ut.TestCase):
    """
    Tests air mass function based on the work of Kasten and Young (1989)
    """
    def test_errors(self):
        self.assertRaises(ValueError, air_mass_KastenYoung1989, 0, -1)

    def test_limit_values(self):
        # air mass through zenit direction at sea level
        theta_z = 0
        h = 0
        expected_value = 1
        self.assertAlmostEqual(air_mass_KastenYoung1989(theta_z, h),
                               expected_value, 3)

        # air mass through zenit direction at exosphere
        # requieres deactivation of limit parameter
        theta_z = 0
        h = 1e8  # 10.000 km
        expected_value = 0
        self.assertAlmostEqual(air_mass_KastenYoung1989(theta_z, h, False),
                               expected_value)

        # model limits (zenith=91.5)
        theta_z = 94
        h = 0
        expected_value = air_mass_KastenYoung1989(91.5, h)
        self.assertEqual(air_mass_KastenYoung1989(theta_z, h),
                         expected_value)


class Test_air_mass_Y1994(ut.TestCase):
    """
    Tests air mass function based on the work of Young (1994)
    """
    def test_limit_values(self):
        # air mass through zenit direction at sea level
        theta_z = 0
        expected_value = 1
        self.assertAlmostEqual(air_mass_Young1994(theta_z), expected_value, 4)


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
        self.assertRaises(ValueError, beam_irradiance, h, n, lat,
                          hour, minute)

        # erroneus day of the year
        h = 0
        n = 367
        lat = -63
        hour, minute = 10, 0
        self.assertRaises(ValueError, beam_irradiance, h, n, lat,
                          hour, minute)

        # erroneus latitude
        h = 0
        n = 171
        lat = -91
        hour, minute = 10, 0
        self.assertRaises(ValueError, beam_irradiance, h, n, lat,
                          hour, minute)

    def test_limit_values(self):
        # sun below the horizon
        h = 0
        n = 171
        lat = -67
        hour, minute = 12, 0
        expected_value = 0
        self.assertEqual(beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        h = 10000
        n = 1
        lat = 87
        hour, minute = 12, 0
        expected_value = 0
        self.assertEqual(beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        # north pole winter nigth
        h = 1000
        n = 320
        lat = 80
        hour, minute = 5, 0
        expected_value = 0
        self.assertEqual(beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        # south pole winter nigth
        h = 5000
        n = 150
        lat = -85
        hour, minute = 22, 0
        expected_value = 0
        self.assertEqual(beam_irradiance(h, n, lat, hour, minute),
                         expected_value)

        # TODO: more test!


def test_irradiance_on_plane():
    """
    Test function that calculates solar irradiance in a plane defined
    by its normal vector
    """

    # Northern Hemisphere #
    # summer solstice, solar noon, lat=declination, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = 23 + 26/60 + 14/3600
    hour, minute = 12, 0
    expected_value = beam_irradiance(h, n, lat, hour, minute)
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # summer solstice, solar noon, lat=declination, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = 23 + 26/60 + 14/3600
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # summer solstice, night, lat=declination, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = 23 + 26/60 + 14/3600
    hour, minute = 0, 0
    expected_value = beam_irradiance(h, n, lat, hour, minute)
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # summer solstice, night, lat=declination, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = 23 + 26/60 + 14/3600
    hour, minute = 0, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, permanent darkness, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = 70
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, permanent darkness, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = 70
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, night, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = 40
    hour, minute = 3, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, night, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = 40
    hour, minute = 3, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # any day, solar noon, any latitude, plane sideways
    vnorm = array([0, 1, 0])
    h = 0
    n = day_of_the_year(4, 1)
    lat = 47.3
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # Southern Hemisphere #
    # summer solstice, solar noon, lat=declination, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = -(23 + 26/60 + 14/3600)
    hour, minute = 12, 0
    expected_value = beam_irradiance(h, n, lat, hour, minute)
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # summer solstice, solar noon, lat=declination, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = -(23 + 26/60 + 14/3600)
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # summer solstice, night, lat=declination, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = -(23 + 26/60 + 14/3600)
    hour, minute = 0, 0
    expected_value = beam_irradiance(h, n, lat, hour, minute)
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # summer solstice, night, lat=declination, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(12, 22)
    lat = -(23 + 26/60 + 14/3600)
    hour, minute = 0, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, permanent darkness, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = -70
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, permanent darkness, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = -70
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, night, plane right-side-up
    vnorm = array([0, 0, -1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = -40
    hour, minute = 3, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # winter solstice, night, plane upside-down
    vnorm = array([0, 0, 1])
    h = 20000
    n = day_of_the_year(6, 20)
    lat = -40
    hour, minute = 3, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)

    # any day, solar noon, any latitude, plane sideways
    vnorm = array([0, 1, 0])
    h = 0
    n = day_of_the_year(10, 5)
    lat = -13.1
    hour, minute = 12, 0
    expected_value = 0
    assert_almost_equal(irradiance_on_plane(vnorm, h, n, lat, hour, minute),
                        expected_value, 3)
