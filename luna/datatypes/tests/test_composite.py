import unittest
from luna.datatypes.composite import DataTimeSeries, DataTimePoint, DataTimeSlot, TimePoint, DataPoint
from luna.datatypes.dimensional import Point, Slot
from luna.datatypes.auxiliary import Span, SlotSpan
from luna.common.exceptions import InputException
from luna.spacetime.time import TimeSlotSpan


class test_dataPoint(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_init(self):
        
        dataPoint1 = DataPoint(label_t=63636, data='string_data')
        dataPoint2 = DataPoint(label_t=63636, data=None)
        dataPoint3 = DataPoint(label_t=63636, data=None, validity_region_span=SlotSpan(value=[60]))
        
        self.assertEqual(dataPoint1.data,'string_data')
        self.assertEqual(dataPoint2.data,None)
        self.assertEqual(dataPoint3.data,None)
        
        # TODO: fix this
        # print dataPoint1.validity_region 
        # print dataPoint3.validity_region.start
        
        
        #TimeSlot(span=TimeSlotSpan('1m'))


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


