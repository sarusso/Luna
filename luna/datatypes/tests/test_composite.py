import unittest
from luna.datatypes.composite import TimeSeries, DataTimePoint, DataTimeSlot, TimePoint
from luna.datatypes.dimensional import Point
from luna.datatypes.auxiliary import TimeSlotType
from luna.common.exceptions import InputException

class test_dataTimePoint_TimeSeries(unittest.TestCase):

    def setUp(self):
        
        # Ref Time Series #1
        timeSeries = TimeSeries(index=False)
        for i in range(10000):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            dataTimePoint = DataTimePoint(t = 1000000000 + (i*60), tz="Europe/Rome", data=data, )
            timeSeries.append(dataTimePoint)
        self.ref_timeSeries_1 = timeSeries
        
        # Ref Time Series #1
        timeSeries = TimeSeries(index=True)
        for i in range(10000):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            dataTimePoint = DataTimePoint(t = 1000000000 + (i*60), tz="Europe/Rome", data=data, )
            timeSeries.append(dataTimePoint)
        self.ref_timeSeries_2 = timeSeries

    def test_init(self):
        pass
     
    def test_equality(self):
        self.assertEqual(self.ref_timeSeries_1 , self.ref_timeSeries_2)

    def test_iterator(self):
        for i, dataTimePoint in enumerate(self.ref_timeSeries_1):
            self.assertEqual(dataTimePoint.t, 1000000000 + (i*60))  
              
    def test_index(self):
        
        # Test without index
        for i in range(10000):
            self.assertEqual(self.ref_timeSeries_1[1000000000 + (i*60)].t, 1000000000 + (i*60))

        # Test with index
        for i in range(10000):
            self.assertEqual(self.ref_timeSeries_2[1000000000 + (i*60)].t, 1000000000 + (i*60))

    def test_append_consistency(self):
        
        data1 = Point(labels=["x","y", "z"], values=[1,2,3])
        data2 = Point(labels=["x","y", "z"], values=[4,5,6])
        data3 = Point(labels=["x","y"], values=[7,8]) 
        dataTimePoint1=DataTimePoint(t=60, data=data1, tz="Europe/Rome")
        dataTimePoint2=DataTimePoint(t=120, data=data2, tz="UTC")
        dataTimePoint3=DataTimePoint(t=180, data=data3, tz="Europe/Rome")
        timeSeries=TimeSeries()
        timeSeries.append(dataTimePoint1)
        
        with self.assertRaises(InputException):
            timeSeries.append(dataTimePoint2)
        
        with self.assertRaises(InputException):
            timeSeries.append(dataTimePoint3)


    def tearDown(self):
        pass





class test_timeDataSlot_TimeSeries(unittest.TestCase):

    def test_one(self):
        
        
        # Test without TimeSlotType
        timeSeries = TimeSeries(index=False)
        for i in range(10):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            timeDataSlot = DataTimeSlot(start = TimePoint(t = 1000000020 + (i*60), tz="Europe/Rome"),
                                        end   = TimePoint(t = 1000000020 + (i+1)*60, tz="Europe/Rome"),
                                        data  = data)
            timeSeries.append(timeDataSlot)
            
        self.assertEqual(timeSeries.tz, "Europe/Rome")

        # Test with TimeSLotType
        timeSeries = TimeSeries(index=False) # TODO: if you omit this line you get an error (point added < start: add test and better printing for the slots)
        for i in range(10):
            data = Point(labels=["power_W", "current_A", "voltage_V"], values=[113.67+i, 3124.67+i, 23.76+i])
            timeDataSlot = DataTimeSlot(start = TimePoint(t = 1000000020 + (i*60), tz="Europe/Rome"),
                                        end   = TimePoint(t = 1000000020 + (i+1)*60, tz="Europe/Rome"),
                                        data  = data,
                                        type  = TimeSlotType("1m"))
            timeSeries.append(timeDataSlot)
            
        self.assertEqual(timeSeries.tz, "Europe/Rome")

 

# TODO: missing tests for class PhysicalDataPoint (test_PhysicalDataPoint)


