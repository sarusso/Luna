import unittest
from luna.datatypes.composite import TimeSeries, DataTimePoint
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException
from luna.spacetime.time import dt

class test_dimensional(unittest.TestCase):

    def setUp(self):       
        pass

    def test_Base(self):
        pass

    def test_Space(self):
        pass
        
    def test_Coordinates(self):
        pass
        
    def test_Point(self):
        
        # Test set
        point1 = Point(labels=["a","b"], values=[1,2])
        point2 = Point(labels=["a","b"], values=[1,2])
        point3 = Point(labels=["a","c"], values=[1,2])        
        point4 = Point(labels=["a","b"], values=[1,3]) 
        point5 = Point(labels=["a"], values=[1])
        point6 = Point(labels=["a"], values=[2])

        # Test init
        with self.assertRaises(InputException):
            Point(labels=["a","b"], values=[1,3,5])
        with self.assertRaises(InputException):
            Point(labels=["a","b","c"], values=[1,3])
            
        # Test only int and float are accepeted values for Point
        Point(labels=["a","b","c"], values=[1,6363.76,3])
        with self.assertRaises(InputException):
            Point(labels=["a","b","c"], values=[1,'hey!',3])

        # Test equality
        self.assertEqual(point1, point2)
        self.assertNotEqual(point1, point3)
        self.assertNotEqual(point1, point4)
        self.assertNotEqual(point1, point5)
        self.assertNotEqual(point1, point6)

        # Test compatibility
        self.assertTrue(point1.is_compatible_with(point2))
        self.assertFalse(point1.is_compatible_with(point3))
        self.assertTrue(point1.is_compatible_with(point4))
        self.assertFalse(point1.is_compatible_with(point5))
        self.assertFalse(point1.is_compatible_with(point6))
        with self.assertRaises(InputException):
            self.assertFalse(point1.is_compatible_with(point5, raises=True))
 
        # Test labels and values:
        self.assertEqual(point1.labels,["a", "b"]) 
        self.assertEqual(point1.values,[1, 2]) 
 
        # Test error if unhandledl kwarg is given:
        with self.assertRaises(InputException):
            _ = Point(labels=["a","c"], values=[1,2], unhandledarg=65.7) 
 
        # Test accessing values by index
        self.assertEqual(point1.valuesdict.a,1)
 
        with self.assertRaises(ValueError):
            _ = point1.valuesdict.g

        ### The following might just go away.. ###

        # Test valuefor():
        self.assertEqual(point1.valueforlabel('a'),1)    

        # Test content:
        point7 = Point(label_a=2,label_b=5,label_c=8)
        self.assertEqual(point7.content.a,2)
        self.assertEqual(point7.content.b,5)
        self.assertEqual(point7.content.c,8)


    def test_Slot(self):

        # Test set
        start_Point1 = Point(labels=["a","b"], values=[5,8])
        start_Point2 = Point(labels=["a"], values=[3])
        end_Point1 = Point(labels=["a","b"], values=[9,13])
        end_Point2 = Point(labels=["a","b"], values=[9,14])
        end_Point3 = Point(labels=["a"], values=[9])
        
        slot1 = Slot(start=start_Point1, end=end_Point1)
        slot2 = Slot(start=start_Point1, end=end_Point1)
        slot3 = Slot(start=start_Point1, end=end_Point2)
        slot4 = Slot(start=start_Point2, end=end_Point3)
        

        # Raise if not compatible start - end
        with self.assertRaises(InputException):       
            _ = Slot(start=start_Point1, end=end_Point3)
        
        # Test init 
        slot1_1 = Slot(start=start_Point1, end=end_Point1)
        slot1_2 = Slot(start=start_Point1, end=end_Point1)
        
        self.assertEqual(slot1_1,slot1_2)
        
        with self.assertRaises(InputException):
            _ = Slot(start=start_Point1, end=end_Point3)
        
        with self.assertRaises(AssertionError):
            _ = Slot(start=start_Point1, end=2)
            
        with self.assertRaises(AssertionError):
            _ = Slot(start=1, end=start_Point2)

        # Test equality
        self.assertEqual(slot1,slot2)
        
        # This is the only test we have for dimensional data _ne_. TODO: Add tests
        #with self.assertRaises(AssertionError):
        #    self.assertNotEqual(slot1,slot2)
        
        # TODO: FIX THIS (and the above mess, WHY there is an AssertionError?!
        #self.assertNotEqual(slot1,slot2)    
        self.assertEqual(slot1,slot2) 
        

            
        self.assertNotEqual(slot1,slot3)
        self.assertNotEqual(slot1,slot4)

        # Test lables
        self.assertEqual(slot1.labels, ['a','b'])
        
        # Test values
        # No if Slot extends Region
        #self.assertEqual(slot1.values, [5, 8])
        #
        # Test accessing values by index
        #self.assertEqual(slot1.valuesdict.a,5)

        # TODO: Missing tests with type (the tests are in test_TimeSlot), we should define a TestSlotType SlotType mock or something...
        
        # Test deltas
        self.assertEquals(slot1.deltas, [4,5])
        
        # Test impossibility of re-anchoring a TimeSlot
        with self.assertRaises(InputException):
            slot1.anchor_to(start_Point1)
        
        # Not anchored Slot
        slot5 = Slot(type=SlotType('test'), labels=['a','b'])
        self.assertEqual(slot5.anchor, None)
        self.assertEqual(slot5.orientation, None)
        self.assertEqual(slot5.start, None)
        self.assertEqual(slot5.end, None)

        # Anchor the slot
        slot5.anchor_to(start_Point1)
        self.assertEqual(slot5.anchor, start_Point1)
        self.assertEqual(slot5.orientation, None)
             
        self.assertEqual(slot5.start, start_Point1)

        with self.assertRaises(NotImplementedError): # TODO: Actually
            _ = slot5.end

        # Deltas are not defined if end is not implemented
        with self.assertRaises(NotImplementedError): # TODO: Actually
            _ = slot5.deltas

        # TODO: Define SimpleSlotType(str([5,6])] to do the above tests also with deltas etc?


    def test_TimePoint(self):
        
        # Init with seconds
        timePoint = TimePoint(t=73637738)
        self.assertEqual(timePoint.t, 73637738)
        self.assertEqual(str(timePoint.dt), '1972-05-02 06:55:38+00:00')
        self.assertEqual(str(timePoint.tz), 'UTC')

        # Init with seconds and microseconds
        timePoint = TimePoint(t=73637738.987654)
        self.assertEqual(timePoint.t, 73637738.987654)
        self.assertEqual(str(timePoint.dt), '1972-05-02 06:55:38.987654+00:00')
        self.assertEqual(str(timePoint.tz), 'UTC')

        # Init with seconds and Timezone
        timePoint = TimePoint(t=73637738, tz="Europe/Rome")
        self.assertEqual(timePoint.t, 73637738)
        self.assertEqual(str(timePoint.dt), '1972-05-02 07:55:38+01:00')
        self.assertEqual(str(timePoint.tz), 'Europe/Rome')


        # Init with timezone-naive datetime (UTC forced)
        timestamp_dt = datetime(2015,2,27,13,54,32)
        timePoint = TimePoint(t=timestamp_dt)
        self.assertEqual(timePoint.t, 1425045272)
        self.assertEqual(timePoint.dt, dt(2015,2,27,13,54,32, tzinfo='UTC'))
        self.assertEqual(str(timePoint.tz), 'UTC')
               
        # Init with datetime on UTC
        timestamp_dt = dt(2015,2,27,13,54,32, tzinfo='UTC')
        timePoint = TimePoint(t=timestamp_dt)
        self.assertEqual(timePoint.t, 1425045272)
        self.assertEqual(timePoint.dt, timestamp_dt)
        self.assertEqual(str(timePoint.tz), 'UTC')

        # Init with datetime on Europe/Rome
        timestamp_dt = dt(2015,2,27,13,54,32, tzinfo='Europe/Rome')
        timePoint = TimePoint(t=timestamp_dt)
        self.assertEqual(timePoint.t, 1425041672)
        self.assertEqual(timePoint.dt, timestamp_dt)
        self.assertEqual(str(timePoint.tz), 'Europe/Rome')

        # Init with datetime forcing another timezone
        timePoint = TimePoint(t=dt(2015,2,27,13,54,32, tzinfo='Europe/London'), tz='Europe/Rome')
        self.assertEqual(timePoint.t, 1425045272)
        self.assertEqual(str(timePoint.dt), '2015-02-27 14:54:32+01:00')
        self.assertEqual(str(timePoint.tz), 'Europe/Rome')     

        # Init with datetime with also microseconds
        timestamp_dt = dt(2015,2,27,13,54,32,566879, tzinfo='UTC')
        timePoint = TimePoint(t=timestamp_dt)  
        self.assertEqual(timePoint.t, 1425045272.566879)
        self.assertEqual(timePoint.dt, timestamp_dt)
        self.assertEqual(str(timePoint.tz), 'UTC')


    def test_SpacePoint(self):
        pass

    def test_TimeSlot(self):
        start_timePoint = TimePoint(t=dt(2015,2,27,13,0,0, tzinfo='UTC'))
        end_timePoint = TimePoint(t=dt(2015,2,27,14,0,0, tzinfo='UTC'))
        
        # Test basic behaviour with no type
        timeSlot = TimeSlot(start=start_timePoint, end=end_timePoint)
        self.assertEqual(timeSlot.start, start_timePoint)
        self.assertEqual(timeSlot.end, end_timePoint)
 
        # Test behaviour with start-end-type  
        timeSlotType = TimeSlotType("1h")
        _ = TimeSlot(start=start_timePoint, end=end_timePoint, type=timeSlotType)
        
        # Test behaviour with inconsistent start-end-type  
        timeSlotType = TimeSlotType("15m")        
        with self.assertRaises(InputException):
            _ = TimeSlot(start=start_timePoint, end=end_timePoint, type=timeSlotType)

        # Test behaviour with start-type, no end  
        timeSlotType = TimeSlotType("1h")
        timeSlot = TimeSlot(start=start_timePoint, type=timeSlotType)
        self.assertEqual(timeSlot.end, end_timePoint)


        # Test 'floating' timeslot
        timeSlotType = TimeSlotType("1h")
        timeSlot = TimeSlot(type=timeSlotType)


    def test_SpaceSlot(self):
        pass


    def test_PhysicalDimensionalData(self):
        
        _ = PhysicalDimensionalData(labels=['power_W'], values=[2.65])

        with self.assertRaises(InputException):
            _ = PhysicalDimensionalData(labels=['power_W_jhd'], values=[2.65])

    def tearDown(self):
        pass























