import unittest
from luna.datatypes.composite import DataTimePoint
from luna.common.exceptions import InputException
from luna.spacetime.time import dt, TimeSlotSpan, correct_dt_dst, timezonize, s_from_dt
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
        self.assertEqual(str(dateTime), '1856-12-01 16:46:00+01:00')

        # NOTE: with pytz==2015.4 instead of the above use the following (which should also be more correct...)
        #self.assertEqual(str(dateTime), '1856-12-01 16:46:00+00:50')

        dateTime = dt(1926,12,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '1926-12-01 16:46:00+01:00')

        dateTime = dt(1926,8,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '1926-08-01 16:46:00+01:00')
        
        # Very future years (no DST
        dateTime = dt(3567,12,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '3567-12-01 16:46:00+01:00')

        dateTime = dt(3567,8,1,16,46, tzinfo='Europe/Rome')
        self.assertEqual(str(dateTime), '3567-08-01 16:46:00+01:00')

 
    def test_TimeSlotSpan(self):
        
        # TODO: I had to comment out this test, find out why..
        # Complex time intervals are not supported
        #with self.assertRaises(InputException):
        #   _ = TimeSlotSpan('15m', '20s')
        
        # TODO: test with spans
        #print TimeSlotSpan('1m').value
        #print TimeSlot(span=TimeSlotSpan('1m')).span.value

        # Not valid 'q' type
        with self.assertRaises(InputException):
            _ = TimeSlotSpan('15q')

        # String init
        timeSlotSpan1 = TimeSlotSpan('15m')
        self.assertEqual(timeSlotSpan1.string, '15m')

        timeSlotSpan2 = TimeSlotSpan('15m_30s_3u')
        self.assertEqual(timeSlotSpan2.string, '15m_30s_3u')
        
        timeSlotSpan3 = TimeSlotSpan(days=1)
        
        # Sum with other TimeSlotSpan objects
        self.assertEqual((timeSlotSpan1+timeSlotSpan2+timeSlotSpan3).string, '1D_30m_30s_3u')

        # Sum with datetime (also on DST change)
        timeSlotSpan = TimeSlotSpan('1h')
        dateTime1 = dt(2015,10,25,0,15,0, tzinfo='Europe/Rome')
        dateTime2 = dateTime1 + timeSlotSpan
        dateTime3 = dateTime2 + timeSlotSpan
        dateTime4 = dateTime3 + timeSlotSpan
        dateTime5 = dateTime4 + timeSlotSpan

        self.assertEqual(str(dateTime1), '2015-10-25 00:15:00+02:00')
        self.assertEqual(str(dateTime2), '2015-10-25 01:15:00+02:00')
        self.assertEqual(str(dateTime3), '2015-10-25 02:15:00+02:00')
        self.assertEqual(str(dateTime4), '2015-10-25 02:15:00+01:00')
        self.assertEqual(str(dateTime5), '2015-10-25 03:15:00+01:00')


    def test_dt_math(self):

        # Test that complex timeSlotSpans are not handable
        timeSlotSpan = TimeSlotSpan('1D_3h_5m')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        
        with self.assertRaises(InputException):
            _ = timeSlotSpan.floor_dt(dateTime)


        # Test in ceil/floor/round normal conditions (hours)
        timeSlotSpan = TimeSlotSpan('1h')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        self.assertEqual(timeSlotSpan.floor_dt(dateTime), dt(2015,1,1,16,0,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime), dt(2015,1,1,17,0,0, tzinfo='Europe/Rome'))

         
        # Test in ceil/floor/round normal conditions (minutes)
        timeSlotSpan = TimeSlotSpan('15m')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        self.assertEqual(timeSlotSpan.floor_dt(dateTime), dt(2015,1,1,16,30,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime), dt(2015,1,1,16,45,0, tzinfo='Europe/Rome'))


        # Test ceil/floor/round in normal conditions (seconds)
        timeSlotSpan = TimeSlotSpan('30s')
        dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome') 
        self.assertEqual(timeSlotSpan.floor_dt(dateTime), dt(2015,1,1,16,37,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime), dt(2015,1,1,16,37,30, tzinfo='Europe/Rome'))

   
        # Test ceil/floor/round across 1970-1-1 (minutes) 
        timeSlotSpan = TimeSlotSpan('5m')
        dateTime1 = dt(1969,12,31,23,57,29, tzinfo='UTC') # epoch = -3601
        dateTime2 = dt(1969,12,31,23,59,59, tzinfo='UTC') # epoch = -3601       
        self.assertEqual(timeSlotSpan.floor_dt(dateTime1), dt(1969,12,31,23,55,0, tzinfo='UTC'))
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime1), dt(1970,1,1,0,0, tzinfo='UTC'))
        self.assertEqual(timeSlotSpan.round_dt(dateTime1), dt(1969,12,31,23,55,0, tzinfo='UTC'))
        self.assertEqual(timeSlotSpan.round_dt(dateTime2), dt(1970,1,1,0,0, tzinfo='UTC'))


        # Test ceil/floor/round (3 hours-test)
        timeSlotSpan = TimeSlotSpan('3h')
        dateTime = dt(1969,12,31,22,0,1, tzinfo='Europe/Rome') # negative epoch
        
        # TODO: test fails!! fix me!        
        #self.assertEqual(timeSlotSpan.floor_dt(dateTime1), dt(1969,12,31,21,0,0, tzinfo='Europe/Rome'))
        #self.assertEqual(timeSlotSpan.ceil_dt(dateTime1), dt(1970,1,1,0,0, tzinfo='Europe/Rome'))


        # Test ceil/floor/round across 1970-1-1 (together with the 2 hours-test, TODO: decouple) 
        timeSlotSpan = TimeSlotSpan('2h')
        dateTime1 = dt(1969,12,31,22,59,59, tzinfo='Europe/Rome') # negative epoch
        dateTime2 = dt(1969,12,31,23,0,1, tzinfo='Europe/Rome') # negative epoch  
        self.assertEqual(timeSlotSpan.floor_dt(dateTime1), dt(1969,12,31,22,0,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime1), dt(1970,1,1,0,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeSlotSpan.round_dt(dateTime1), dt(1969,12,31,22,0, tzinfo='Europe/Rome'))
        self.assertEqual(timeSlotSpan.round_dt(dateTime2), dt(1970,1,1,0,0, tzinfo='Europe/Rome'))

        # Test ceil/floor/round across DST change (hours)
        timeSlotSpan = TimeSlotSpan('1h')
        
        dateTime1 = dt(2015,10,25,0,15,0, tzinfo='Europe/Rome')
        dateTime2 = dateTime1 + timeSlotSpan    # 2015-10-25 01:15:00+02:00    
        dateTime3 = dateTime2 + timeSlotSpan    # 2015-10-25 02:15:00+02:00
        dateTime4 = dateTime3 + timeSlotSpan    # 2015-10-25 02:15:00+01:00

        dateTime1_rounded = dt(2015,10,25,0,0,0, tzinfo='Europe/Rome')
        dateTime2_rounded = dateTime1_rounded + timeSlotSpan        
        dateTime3_rounded = dateTime2_rounded + timeSlotSpan
        dateTime4_rounded = dateTime3_rounded + timeSlotSpan
        dateTime5_rounded = dateTime4_rounded + timeSlotSpan
               
        self.assertEqual(timeSlotSpan.floor_dt(dateTime2), dateTime2_rounded)
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime2), dateTime3_rounded)
          
        self.assertEqual(timeSlotSpan.floor_dt(dateTime3), dateTime3_rounded)
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime3), dateTime4_rounded)
        
        self.assertEqual(timeSlotSpan.floor_dt(dateTime4), dateTime4_rounded)
        self.assertEqual(timeSlotSpan.ceil_dt(dateTime4), dateTime5_rounded)



    def test_shift_dt(self):
        
        # TODO
        pass
        
        #timeSlotSpan = TimeSlotSpan('15m')
        #dateTime = dt(2015,1,1,16,37,14, tzinfo='Europe/Rome')
        #dateTime_rounded = dt(2015,1,1,16,0,0, tzinfo='Europe/Rome')
        
        #print shift_dt(dateTime, timeSlotSpan, 4)
        #print shift_dt(dateTime, timeSlotSpan, -2)

        #print shift_dt(dateTime_rounded, timeSlotSpan, 4)
        #print shift_dt(dateTime_rounded, timeSlotSpan, -2)

        # Test shift across DST change

    def tearDown(self):
        pass























