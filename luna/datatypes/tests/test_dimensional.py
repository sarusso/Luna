import unittest
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
            point1.is_compatible_with(point5, raises=True)
 
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
        point7   = Point({'a':2, 'b':5, 'c':8})
        self.assertEqual(point7.content.a, 2)
        self.assertEqual(point7.content.b, 5)
        self.assertEqual(point7.content.c, 8)

        # Test content equality checks
        self.assertEqual(point7.content, {'a': 2, 'c': 8, 'b': 5})
        self.assertEqual(point7.content, {'a': 2, 'b': 5, 'c': 8})
        self.assertEqual(point7.content, Point({'a':2, 'b':5, 'c':8}).content)
        
        
        # Test content Un-equality checks
        self.assertNotEqual(point7.content, {'a': 2, 'c': 75, 'b': 5})
        self.assertNotEqual(point7.content, {'a': 2, 'c': 8, 'b': 5, 'd': 6})
        self.assertNotEqual(point7.content, {'a': 2, 'b': 5})
        self.assertNotEqual(point7.content, Point({'a': 2, 'c': 75, 'b': 5}).content)
        self.assertNotEqual(point7.content, Point({'a': 2, 'c': 8, 'b': 5, 'd': 6}).content)
        self.assertNotEqual(point7.content, Point({'a': 2, 'b': 5}).content)

        # Test Point iterator
        content = {}
        for item in point7.content:
            content.update(item)
        self.assertEqual(content, {'a': 2, 'c': 8, 'b': 5})

        # Test sum and subtraction:
        point8 = Point({'a':12, 'b':5 , 'c':3})
        point9 = Point({'a':8, 'b':3 , 'c':1})

        self.assertEqual((point8-point9).values,[4,2,2])

    def test_Slot(self):

        # Test set
        start_Point1 = Point(labels=["a","b"], values=[5,8])
        start_Point2 = Point(labels=["a"], values=[3])
        end_Point1 = Point(labels=["a","b"], values=[9,13])
        end_Point2 = Point(labels=["a","b"], values=[9,14])
        end_Point3 = Point(labels=["a"], values=[9])
        end_Point4 = Point(labels=["a","b"], values=[7,10])
        

        # Floating Slot
        slot0 = Slot(span=SlotSpan(value=[4,5]), labels=['a', 'b'])
        
        # Slots with start and end
        slot1 = Slot(start=start_Point1, end=end_Point1)
        slot2 = Slot(start=start_Point1, end=end_Point1)
        slot3 = Slot(start=start_Point1, end=end_Point2)
        slot4 = Slot(start=start_Point2, end=end_Point3)
        slot5 = Slot(start=start_Point1, end=end_Point4) 
        
        
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
        
        with self.assertRaises(InputException):
            _ = Slot(start=start_Point1, end=2)
            
        with self.assertRaises(InputException):
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
        
        # Test deltas
        self.assertEqual(slot1.deltas, [4,5])
        self.assertEqual(slot0.deltas, [4,5])
        
        # Slots are also allowed with just the span..
        slot = Slot(span=SlotSpan(value=[2,3]), labels=['a','b'])
        self.assertEqual(slot.anchor, None)
        
        #..and can be anchored afterwards:
        slot._anchor_to(start_Point1)
        self.assertEqual(slot.anchor, start_Point1)


        # Test the symmetry check
        self.assertFalse(slot1.is_symmetric) # delats = [4.0, 5.0]
        self.assertTrue(slot5.is_symmetric)  # deltas = [2.0, 2.0]
        self.assertFalse(slot0.is_symmetric)  # deltas = [  4,   5]



        # TODO: Missing tests with type (the tests are in test_TimeSlot), we should define a TestSlotType SlotType mock or something...                       
        # TODO: test that you cannot ask for start/end if the slot is not anchored.
        
        
        
        #-----------------------------------------------------------------------------
        # TODO: fix the tests by removing the ones here and adding new proper ones
        #-----------------------------------------------------------------------------

        self.assertEqual(slot0.anchor, None)
        self.assertEqual(slot5.anchor, Point(labels=["a","b"], values=[6,9]))
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
        center_timePoint = TimePoint(dt=dt(2015,2,27,13,30,0, tzinfo='UTC'))
        end_timePoint = TimePoint(dt=dt(2015,2,27,14,0,0, tzinfo='UTC'))
        
        # Test basic behavior with no span but start/end (not floating)
        timeSlot = TimeSlot(start=start_timePoint, end=end_timePoint)
        self.assertEqual(timeSlot.start, start_timePoint)
        self.assertEqual(timeSlot.end, end_timePoint)
 

        # Test basic behavior with span but floating
        timeSlot_floating = TimeSlot(span=TimeSlotSpan('1m'), labels=['t'])
        timeSlot_floating = TimeSlot(span=TimeSlotSpan('1m'))
        
        with self.assertRaises(InputException):
            _ = TimeSlot(span=TimeSlotSpan('1m'), labels=['a'])
        
        #self.assertEqual(timeSlot_floating) WORKING HERE
        
 
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


        # Test that a 'floating' timeslot is allowed:        
        timeSlot = TimeSlot(span="1h")
        self.assertEqual(timeSlot.anchor, None)
        self.assertEqual(timeSlot.start, None)
        self.assertEqual(timeSlot.end, None)
        self.assertEqual(timeSlot.center, None)

        # but it can be anchored (by default to the center)
        timeSlot._anchor_to(center_timePoint)
        self.assertEqual(timeSlot.anchor, center_timePoint)
        self.assertEqual(timeSlot.start, start_timePoint)
        self.assertEqual(timeSlot.center, center_timePoint)
        self.assertEqual(timeSlot.end, end_timePoint)
        
        # TODO: cannot compare with None and Points (try this: self.assertEqual(timeSlot.anchor, center_timePoint))
        
  

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


        #--------------------
        # Test Slot Span
        #--------------------        

        # Initialize the SlotSpan in the wrong way
        with self.assertRaises(InputException):
            _ = SlotSpan()
            
        with self.assertRaises(InputException):  
            _ = SlotSpan(start=Point({'a': 1, 'b':1}), end=Point({'a': 5, 'z':5})) # label_z is wrong
        
        # Initialize the SlotSpan
        slotSpan1 = SlotSpan(value=[5,5])
        slotSpan2 = SlotSpan(start=Point({'a': 2, 'b':1}), end=Point({'a': 5, 'b':5}))
        
        # TODO: with the following two we are actually indirectly testing the Point subtraction, move somewhere else..
        slotSpan3 = SlotSpan(start=Point({'a':5, 'b':5}), end=Point({'a': 5, 'b':5}))
        slotSpan4 = SlotSpan(start=Point({'a':8, 'b':10}), end=Point({'a': 5, 'b':5}))
        
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


    def tearDown(self):
        pass









from luna.datatypes.dimensional import DataTimeSeries, DataTimePoint, DataTimeSlot, TimePoint, DataPoint
from luna.datatypes.dimensional import Point, Slot, TimeSlot
from luna.datatypes.auxiliary import Span, SlotSpan
from luna.common.exceptions import InputException
from luna.spacetime.time import TimeSlotSpan


class test_dataPoint(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_init(self):
        
        with self.assertRaises(InputException):
            _ = DataPoint({'g': 1000}, data=None)
         
                    
        dataPoint1 = DataPoint({'g': 1000}, data='string_data1')
        dataPoint2 = DataPoint({'g': 1000}, data='string_data2')
        dataPoint3 = DataPoint({'g': 1000}, data='string_data3',
                                validity_region = Slot(span=SlotSpan(value=[60]), labels=['g']))
        
        self.assertEqual(dataPoint1.data,'string_data1')
        self.assertEqual(dataPoint2.data,'string_data2')
        self.assertEqual(dataPoint3.data,'string_data3')
        
        # TODO: here we are indirectly testing the valitiy region, which is the slot
        self.assertTrue(isinstance(dataPoint3.validity_region, Slot))
        self.assertEqual(dataPoint3.validity_region.start, Point({'g': 970}))
        self.assertEqual(dataPoint3.validity_region.center, Point({'g': 1000}))
        self.assertEqual(dataPoint3.validity_region.anchor, Point({'g': 1000}))
        self.assertEqual(dataPoint3.validity_region.end, Point({'g': 1030}))
        
        
        
        
class test_dataTimePoint(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_init(self):
        
        # TODO: fix this, should work:
        # DataTimePoint(label_t=1000, data='string_data')
        
        with self.assertRaises(InputException):
            _ = DataTimePoint(t=1000, data=None)

        with self.assertRaises(InputException):
            _ = DataTimePoint({'g': 1000}, data='string_data')     
                    
        dataTimePoint1 = DataTimePoint(t=1000, data='string_data1')
        dataTimePoint2 = DataTimePoint(t=1000, data='string_data2')
        dataTimePoint3 = DataTimePoint(t=1000, data='string_data3', validity_region=TimeSlot(span=TimeSlotSpan('60s')))
        
        self.assertEqual(dataTimePoint1.data,'string_data1')
        self.assertEqual(dataTimePoint2.data,'string_data2')
        self.assertEqual(dataTimePoint3.data,'string_data3')
        
        # TODO: here we are indirectly testing the validity region, which is the slot
        self.assertTrue(isinstance(dataTimePoint3.validity_region, TimeSlot))
        self.assertEqual(dataTimePoint3.validity_region.start, TimePoint(t=970))
        self.assertEqual(dataTimePoint3.validity_region.center, TimePoint(t=1000))
        self.assertEqual(dataTimePoint3.validity_region.anchor, TimePoint(t=1000))
        self.assertEqual(dataTimePoint3.validity_region.end, TimePoint(t=1030))


        # The following test interpolability of the concept, i.e. a SlotSpan applied to DataTimePoint
        # TODO: to make it work, implement the persistent trustme switch in DataPoint
        #dataTimePoint4 = DataTimePoint(t=1000, data='string_data3', validity_region_span=SlotSpan(value=[60]), trustme=True)
        #self.assertEqual(dataTimePoint4.data,'string_data3')
        #self.assertTrue(isinstance(dataTimePoint4.validity_region, Slot))
        #self.assertEqual(dataTimePoint4.validity_region.start, TimePoint(t=970))
        #self.assertEqual(dataTimePoint4.validity_region.center, TimePoint(t=1000))
        #self.assertEqual(dataTimePoint4.validity_region.anchor, TimePoint(t=1000))
        #self.assertEqual(dataTimePoint4.validity_region.end, TimePoint(t=1030))


    def tearDown(self):
        pass


class test_dataTimePoint_DataTimeSeries(unittest.TestCase):

    def setUp(self):
        
        # Ref Time Series #1
        dataTimeSeries = DataTimeSeries(index=False)
        for i in range(10000):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            dataTimePoint = DataTimePoint(t = 1000000000 + (i*60), tz="Europe/Rome", data=data, )
            dataTimeSeries.append(dataTimePoint)
        self.ref_dataTimeSeries_1 = dataTimeSeries
        
        # Ref Time Series #1
        dataTimeSeries = DataTimeSeries(index=True)
        for i in range(10000):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            dataTimePoint = DataTimePoint(t = 1000000000 + (i*60), tz="Europe/Rome", data=data, )
            dataTimeSeries.append(dataTimePoint)
        self.ref_dataTimeSeries_2 = dataTimeSeries

    def test_init(self):
        pass
    
    def test_equality(self):
        self.assertEqual(self.ref_dataTimeSeries_1 , self.ref_dataTimeSeries_2)

    def test_iterator(self):
        for i, dataTimePoint in enumerate(self.ref_dataTimeSeries_1):
            self.assertEqual(dataTimePoint.t, 1000000000 + (i*60))  
    
    def test_unroll(self):
        # Test unroll
        for item in self.ref_dataTimeSeries_1:
            last_item1 = item
        for item in self.ref_dataTimeSeries_1:
            last_item2 = item
        self.assertEqual(last_item1,last_item2)
              
    def test_index(self):
        
        # Test without index
        for i in range(10000):
            self.assertEqual(self.ref_dataTimeSeries_1[1000000000 + (i*60)].t, 1000000000 + (i*60))

        # Test with index
        for i in range(10000):
            self.assertEqual(self.ref_dataTimeSeries_2[1000000000 + (i*60)].t, 1000000000 + (i*60))

    def test_append_consistency(self):
        
        data1 = Point(labels=["x","y", "z"], values=[1,2,3])
        data2 = Point(labels=["x","y", "z"], values=[4,5,6])
        data3 = Point(labels=["x","y"], values=[7,8]) 
        dataTimePoint1=DataTimePoint(t=60, data=data1, tz="Europe/Rome")
        dataTimePoint2=DataTimePoint(t=120, data=data2, tz="UTC")
        dataTimePoint3=DataTimePoint(t=180, data=data3, tz="Europe/Rome")
        dataTimeSeries=DataTimeSeries()
        dataTimeSeries.append(dataTimePoint1)
        
        with self.assertRaises(InputException):
            dataTimeSeries.append(dataTimePoint2)
        
        with self.assertRaises(InputException):
            dataTimeSeries.append(dataTimePoint3)


    def tearDown(self):
        pass




class test_dataTimeSlot_DataTimeSeries(unittest.TestCase):

    def test_one(self):
               
        # Test without TimeSlotType
        dataTimeSeries = DataTimeSeries(index=False)
        for i in range(10):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            dataTimeSlot = DataTimeSlot(start = TimePoint(t = 1000000020 + (i*60), tz="Europe/Rome"),
                                        end   = TimePoint(t = 1000000020 + (i+1)*60, tz="Europe/Rome"),
                                        data  = data)
            dataTimeSeries.append(dataTimeSlot)
            
        self.assertEqual(dataTimeSeries.tz, "Europe/Rome")

        # Test with TimeSLotType
        dataTimeSeries = DataTimeSeries(index=False) # TODO: if you omit this line you get an error (point added < start: add test and better printing for the slots)
        for i in range(10):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            dataTimeSlot = DataTimeSlot(start = TimePoint(t = 1000000020 + (i*60), tz="Europe/Rome"),
                                        end   = TimePoint(t = 1000000020 + (i+1)*60, tz="Europe/Rome"),
                                        data  = data,
                                        span  = TimeSlotSpan("1m"))
            dataTimeSeries.append(dataTimeSlot)
            
        self.assertEqual(dataTimeSeries.tz, "Europe/Rome")

 

# TODO: missing tests for class PhysicalDataPoint (test_PhysicalDataPoint)















