import unittest
from luna.datatypes.composite import DataTimePoint
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException
from luna.spacetime.time import dt, TimeSlotSpan

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
  
        # Test __getitem__
        self.assertEqual(point1['a'], 1)
        
        with self.assertRaises(ValueError):
            _ = point1['g']

        # Test valueforlabel()
        self.assertEqual(point1.valueforlabel('a'),1)
        with self.assertRaises(ValueError):
            point1.valueforlabel('g')
  
        # Test content:
        point7 = Point(label_a=2, label_b=5, label_c=8)
        self.assertEqual(point7.content.a, 2)
        self.assertEqual(point7.content.b, 5)
        self.assertEqual(point7.content.c, 8)
        self.assertEqual(str(point7.content), str({'a': 2, 'c': 8, 'b': 5}))
        self.assertEqual(point7.content.a, 2)
        self.assertEqual(point7.content.b, 5)
        self.assertEqual(point7.content.c, 8)
        
        tot = 0
        for item in point7.content:
            if tot == 0:
                self.assertEqual(item, {'a': 2})
            if tot == 1:
                self.assertEqual(item, {'b': 5})
            if tot == 2:
                self.assertEqual(item, {'c': 8})
            tot +=1                
        self.assertEqual(tot,3)

        # Test sum and subtraction:
        point8 = Point(label_a=12,label_b=5,label_c=3)
        point9 = Point(label_a=8,label_b=3,label_c=1)
        
        self.assertEquals((point8-point9).values,[4,2,2])

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
        
        
        # Test that the span has been correctly set:
        # TODO: Maybe compare with another Span object here? like SlotSpan([4,5])?
        self.assertEqual(slot1.span.value, [4,5])

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
        
        # Not anchored Slot raise an error:
        with self.assertRaises(InputException):
            _ = Slot(span=Span(value=[2,3]), labels=['a','b'])
        
        #-----------------------------------------------------------------------------
        # TODO: fix the tests by removing the ones here and adding new proper ones
        #-----------------------------------------------------------------------------

        #self.assertEqual(slot5.anchor, None)
        #self.assertEqual(slot5.orientation, None)
        #self.assertEqual(slot5.start, None)
        #self.assertEqual(slot5.end, None)

        # Anchor the slot
        #slot5.anchor_to(start_Point1)
        #self.assertEqual(slot5.anchor, start_Point1)
        #self.assertEqual(slot5.orientation, None)
             
        #self.assertEqual(slot5.start, start_Point1)

        #with self.assertRaises(NotImplementedError): # TODO: Actually
        #    _ = slot5.end

        # Deltas are not defined if end is not implemented
        # TODO: deltas?! Wheer we need hem?!
        #with self.assertRaises(NotImplementedError): # TODO: Actually
        #    _ = slot5.deltas

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

        # Init with Timezone-naive datetime not allowed (not UTC forced)
        timestamp_dt = datetime(2015,2,27,13,54,32)
        with self.assertRaises(InputException):
            _ = TimePoint(dt=timestamp_dt)
    
        # Init with datetime on UTC
        timestamp_dt = dt(2015,2,27,13,54,32, tzinfo='UTC')
        timePoint = TimePoint(dt=timestamp_dt)
        self.assertEqual(timePoint.t, 1425045272)
        self.assertEqual(timePoint.dt, timestamp_dt)
        self.assertEqual(str(timePoint.tz), 'UTC')

        # Init with datetime on Europe/Rome
        timestamp_dt = dt(2015,2,27,13,54,32, tz='Europe/Rome')
        timePoint = TimePoint(dt=timestamp_dt)
        self.assertEqual(timePoint.t, 1425041672)
        self.assertEqual(timePoint.dt, timestamp_dt)
        self.assertEqual(str(timePoint.tz), 'Europe/Rome')

        # Init with datetime on another timezone not allowed (not forcing another timezone)
        with self.assertRaises(InputException):
            _ = TimePoint(dt=dt(2015,2,27,13,54,32, tz='Europe/London'), tz='Europe/Rome')

        # Init with datetime with also microseconds
        timestamp_dt = dt(2015,2,27,13,54,32,566879, tzinfo='UTC')
        timePoint = TimePoint(dt=timestamp_dt)
        self.assertEqual(timePoint.t, 1425045272.566879)
        self.assertEqual(timePoint.dt, timestamp_dt)
        self.assertEqual(str(timePoint.tz), 'UTC')


    def test_SpacePoint(self):
        pass

    def test_TimeSlot(self):
        start_timePoint = TimePoint(dt=dt(2015,2,27,13,0,0, tzinfo='UTC'))
        end_timePoint = TimePoint(dt=dt(2015,2,27,14,0,0, tzinfo='UTC'))
        
        # Test basic behaviour with no span
        timeSlot = TimeSlot(start=start_timePoint, end=end_timePoint)
        self.assertEqual(timeSlot.start, start_timePoint)
        self.assertEqual(timeSlot.end, end_timePoint)
 
        # Test behaviour with start-end-span  
        timeSlotSpan = TimeSlotSpan("1h")
        _ = TimeSlot(start=start_timePoint, end=end_timePoint, span=timeSlotSpan)
        
        # Test behaviour with inconsistent start-end-span  
        timeSlotSpan = TimeSlotSpan("15m")        
        with self.assertRaises(InputException):
            _ = TimeSlot(start=start_timePoint, end=end_timePoint, span=timeSlotSpan)

        # Test behaviour with start-span, no end  
        timeSlotSpan = TimeSlotSpan("1h")
        timeSlot = TimeSlot(start=start_timePoint, span=timeSlotSpan)
        self.assertEqual(timeSlot.end, end_timePoint)


        # Test that a 'floating' timeslot is not allowed:
        timeSlotSpan = TimeSlotSpan("1h")
        with self.assertRaises(InputException):
            timeSlot = TimeSlot(span=timeSlotSpan)


    def test_SpaceSlot(self):
        pass


    def test_PhysicalData(self):
        
        _ = PhysicalData(labels=['power_W'], values=[2.65])

        with self.assertRaises(InputException):
            _ = PhysicalData(labels=['power_W_j_h_d'], values=[2.65])


    def test_Span(self):
        
        #--------------------
        # Test Span
        #--------------------
        
        # Initialize the Span in the wrong way
        with self.assertRaises(InputException):
            _ = Span()

        with self.assertRaises(InputException):
            _ = Span('spareArg')
        
        # Initialize the Span  
        span = Span(value=5)
        
        # Test the value
        self.assertEqual(span.value, 5)
        
        # Test the representation
        self.assertEqual(str(span), 'Span of value: 5')


        # Test methods and properties to be implemented
        with self.assertRaises(NotImplementedError):
            _ = span.get_start(end=None)        
        
        with self.assertRaises(NotImplementedError):
            _ = span.get_end(start=None)    

        with self.assertRaises(NotImplementedError):
            _ = span.is_symmetric


        

        #--------------------
        # Test Slot Span
        #--------------------        

        # Initialize the SlotSpan in the wrong way
        with self.assertRaises(InputException):
            _ = SlotSpan()
            
        with self.assertRaises(InputException):  
            _ = SlotSpan(start=Point(label_a=2,label_b=1), end=Point(label_a=5,label_z=5)) # label_z is wrong
        
        # Initialize the SlotSpan
        slotSpan1 = SlotSpan(value=[5,5])
        slotSpan2 = SlotSpan(start=Point(label_a=2,label_b=1), end=Point(label_a=5,label_b=5))
        
        # TODO: with the following two we are actually indirectly testing the Point subtraction, move somewhere else..
        slotSpan3 = SlotSpan(start=Point(label_a=5,label_b=5), end=Point(label_a=5,label_b=5))
        slotSpan4 = SlotSpan(start=Point(label_a=8,label_b=10), end=Point(label_a=5,label_b=5))
        
        # Test wrong Init
        
        # Test the values
        self.assertEqual(slotSpan1.value, [5,5])
        self.assertEqual(slotSpan2.value, [3,4])

        # TODO: with the following two we are actually indirectly testing the Point subtraction, move somewhere else..
        self.assertEqual(slotSpan3.value, [0,0])
        self.assertEqual(slotSpan4.value, [-3,-5])
        
        # Get start / end are not yet implemented (but they could be quite easily)
        

        with self.assertRaises(NotImplementedError):
            _ = span.get_start(end=None)        
        
        with self.assertRaises(NotImplementedError):
            _ = span.get_end(start=None)    

        # Test the symmetry check
        self.assertTrue(slotSpan1.is_symmetric)     # [5,5]
        self.assertFalse(slotSpan2.is_symmetric)    # [3,4]
        self.assertTrue(slotSpan3.is_symmetric)     # [0,0]
        self.assertFalse(slotSpan4.is_symmetric)    # [-3,-5]

    def tearDown(self):
        pass























