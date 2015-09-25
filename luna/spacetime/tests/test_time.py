import unittest
from luna.datatypes.composite import TimeSeries, DataTimePoint
from luna.common.exceptions import InputException
from luna.spacetime.time import dt, TimeInterval, correct_dt_dst, timezonize
import datetime

class test_time(unittest.TestCase):

    def setUp(self):       
        pass

    def test_correct_dt_dst(self):
        
        # 2015-03-29 01:15:00+01:00
        dateTime =  dt(2015,3,29,1,15,0, tzinfo='Europe/Rome')
        
        # 2015-03-29 02:15:00+01:00, Wrong, does not exists and cannot be corrected
        dateTime = dateTime + datetime.timedelta(hours=1)
        with self.assertRaises(InputException):
            correct_dt_dst(dateTime)

        # 2015-03-29 03:15:00+01:00, Wrong and can be corrected
        dateTime = dateTime + datetime.timedelta(hours=1)
        self.assertEqual(correct_dt_dst(dateTime), dt(2015,3,29,3,15,0, tzinfo='Europe/Rome'))


    def test_dt(self):
        
        # TODO: understand if it is fine to test with string representation. Can we use native datetime?
        
        # Test UTC
        dateTime = dt(2015,3,29,2,15,0, tzinfo='UTC')
        self.assertEqual(str(dateTime), '2015-03-29 02:15:00+00:00')
        
        # Test UTC forced
        dateTime = dt(2015,3,29,2,15,0)
        self.assertEqual(str(dateTime), '2015-03-29 02:15:00+00:00')
        
        # Test with  timezone
        dateTime = dt(2015,3,25,4,15,0, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '2015-03-25 04:15:00+01:00')
        dateTime = dt(2015,9,25,4,15,0, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '2015-09-25 04:15:00+02:00')

        #---------------------
        # Test border cases
        #---------------------
        
        # Not existent time raises
        with self.assertRaises(InputException):
            _ = dt(2015,3,29,2,15,0, tzinfo='Europe/Rome')
         
        # Not existent time does not raises   
        dateTime = dt(2015,3,29,2,15,0, tzinfo='Europe/Rome', trustme=True)
        self.assertEqual(dateTime.year, 2015)
        self.assertEqual(dateTime.month, 3)
        self.assertEqual(dateTime.day, 29)
        self.assertEqual(dateTime.hour, 2)
        self.assertEqual(dateTime.minute, 15)
        self.assertEqual(str(dateTime.tzinfo), 'Europe/Rome')

        # Very past years (no DST)
        dateTime = dt(1856,12,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '1856-12-01 16:46:00+00:50')

        dateTime = dt(1926,12,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '1926-12-01 16:46:00+01:00')

        dateTime = dt(1926,8,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '1926-08-01 16:46:00+01:00')
        
        # Very future years (no DST
        dateTime = dt(3567,12,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '3567-12-01 16:46:00+01:00')

        dateTime = dt(3567,8,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '3567-08-01 16:46:00+01:00')

 
    def test_TimeInterval(self):
        
        # Complex time intervals are not supported
        with self.assertRaises(InputException):
            _ = TimeInterval('15m', '20s')

        # Not valid 'q' type
        with self.assertRaises(InputException):
            _ = TimeInterval('15q')

        # String init
        timeInterval1 = TimeInterval('15m')
        self.assertEqual(timeInterval1.string, '15m')

        timeInterval2 = TimeInterval('15m_30s_3u')
        self.assertEqual(timeInterval2.string, '15m_30s_3u')
        
        timeInterval3 = TimeInterval(days=1)
        
        # Sum with other TimeIntervals
        self.assertEqual((timeInterval1+timeInterval2+timeInterval3).string, '1D_30m_30s_3u')

        # Sum with datetime (also on DST change)
        timeInterval = TimeInterval('1h')
        dateTime1 = dt(2015,10,25,0,15,0, tzinfo='Europe/Rome')
        dateTime2 = dateTime1 + timeInterval
        dateTime3 = dateTime2 + timeInterval
        dateTime4 = dateTime3 + timeInterval
        dateTime5 = dateTime4 + timeInterval

        self.assertEquals(str(dateTime1), '2015-10-25 00:15:00+02:00')
        self.assertEquals(str(dateTime2), '2015-10-25 01:15:00+02:00')
        self.assertEquals(str(dateTime3), '2015-10-25 02:15:00+02:00')
        self.assertEquals(str(dateTime4), '2015-10-25 02:15:00+01:00')
        self.assertEquals(str(dateTime5), '2015-10-25 03:15:00+01:00')


    def test_dt_math(self):

        # Test complex timeIntervals not handable
        timeInterval = TimeInterval('1D_3h_5m')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        
        with self.assertRaises(InputException):
            _ = timeInterval.floor_dt(dateTime)

        # Test in normal conditions (hours)
        timeInterval = TimeInterval('1h')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        self.assertEqual(timeInterval.floor_dt(dateTime), dt(2015,1,1,16,0,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeInterval.ceil_dt(dateTime), dt(2015,1,1,17,0,0, tzinfo='Europe/Rome'))
          
        # Test in normal conditions (minutes)
        timeInterval = TimeInterval('15m')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        self.assertEqual(timeInterval.floor_dt(dateTime), dt(2015,1,1,16,30,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeInterval.ceil_dt(dateTime), dt(2015,1,1,16,45,0, tzinfo='Europe/Rome'))

        # Test in normal conditions (seconds)
        timeInterval = TimeInterval('30s')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        self.assertEqual(timeInterval.floor_dt(dateTime), dt(2015,1,1,16,37,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeInterval.ceil_dt(dateTime), dt(2015,1,1,16,37,30, tzinfo='Europe/Rome'))
        
        # Test across DST change (hours)
        timeInterval = TimeInterval('1h')
        
        dateTime1 = dt(2015,10,25,0,15,0, tzinfo='Europe/Rome')
        dateTime2 = dateTime1 + timeInterval        
        dateTime3 = dateTime2 + timeInterval
        dateTime4 = dateTime3 + timeInterval

        dateTime1_rounded = dt(2015,10,25,0,0,0, tzinfo='Europe/Rome')
        dateTime2_rounded = dateTime1_rounded + timeInterval        
        dateTime3_rounded = dateTime2_rounded + timeInterval
        dateTime4_rounded = dateTime3_rounded + timeInterval
        dateTime5_rounded = dateTime4_rounded + timeInterval
        
        # 2015-10-25 01:15:00+02:00  
        self.assertEqual(timeInterval.floor_dt(dateTime2), dateTime2_rounded)
        self.assertEqual(timeInterval.ceil_dt(dateTime2), dateTime3_rounded)
        
        # 2015-10-25 02:15:00+02:00
        self.assertEqual(timeInterval.floor_dt(dateTime3), dateTime3_rounded)
        self.assertEqual(timeInterval.ceil_dt(dateTime3), dateTime4_rounded)
        
        # 2015-10-25 02:15:00+01:00
        self.assertEqual(timeInterval.floor_dt(dateTime4), dateTime4_rounded)
        self.assertEqual(timeInterval.ceil_dt(dateTime4), dateTime5_rounded)



    def test_shift_dt(self):
        
        # TODO
        pass
        
        #timeInterval = TimeInterval('15m')
        #dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        #dateTime_rounded = dt(2015,1,1,16,0,0, tzinfo='Europe/Rome')
        
        #print shift_dt(dateTime, timeInterval, 4)
        #print shift_dt(dateTime, timeInterval, -2)

        #print shift_dt(dateTime_rounded, timeInterval, 4)
        #print shift_dt(dateTime_rounded, timeInterval, -2)

        # Test shift across DST change

    def tearDown(self):
        pass























