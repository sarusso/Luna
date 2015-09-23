import unittest
from luna.datatypes.composite import TimeSeries, DataTimePoint, PhysicalDataTimePoint, PhysicalDataTimeSlot, StreamingTimeSeries
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException, StorageException
from luna.spacetime.time import dt
from luna.datatypes.dimensional import TimePoint, Point, PhysicalData
from luna.sensors import VolumetricSensorV1
from luna.storage.sqlite import sqlite


# TODO: this should be a generic storgae test, which is applied to the various modules (whcih can be write or read only)


#------------------------------------
# Logging
#------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("luna")


#------------------------------------
# Tests
#------------------------------------

class test_sqlite(unittest.TestCase):

    def setUp(self):       
        pass


    def test_Init(self):    
        _ = sqlite.TimeSeriesSQLiteStorage(in_memory=True)

    def test_PutGet_DataTimePoints(self):
        
        timeSeriesSQLiteStorage = sqlite.TimeSeriesSQLiteStorage(in_memory=True)
        
        # Generate 10 points TimeSeries with flowrate sensor
        timeSeries = TimeSeries()
        for i in range(10):
            data = PhysicalData( labels = ['flowrate_m3s'], values = [20.6+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
            timeSeries.append(physicalDataTimePoint)

        # Generate 10 points TimeSeries with light sensor
        timeSeries_light = TimeSeries()
        for i in range(10):
            data = PhysicalData( labels = ['light_pct'], values = [60.6+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
            timeSeries_light.append(physicalDataTimePoint)
        
        # Test put data without sensor (not implemented for now)
        with self.assertRaises(NotImplementedError):
            data_id_1 = timeSeriesSQLiteStorage.put(timeSeries)
        
        # Test volumetric sensor
        volumetricSensorV1_1 = VolumetricSensorV1('lu65na')
        volumetricSensorV1_2 = VolumetricSensorV1('lu34na')
        
        # Test labels inconsistency
        with self.assertRaises(InputException):
            timeSeriesSQLiteStorage.put(timeSeries_light, sensor=volumetricSensorV1_1)
        
        # Test put data with sensor and no right to create structure
        with self.assertRaises(StorageException):
            timeSeriesSQLiteStorage.put(timeSeries, sensor=volumetricSensorV1_1)

        # Test get with sensor and no structure in the storage
        with self.assertRaises(StorageException):
            _  = timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, cached=True)

        # Test put data with sensor and right to create structure AND get with sensor and without from_dt/to_dt
        # TODO: this is not correct unit test of the put and get. It is testing them at the same time!
        timeSeriesSQLiteStorage.put(timeSeries, sensor=volumetricSensorV1_1, right_to_initialize=True)
        out_streamingTimeSeries  = timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, cached=True)
        self.assertEqual(out_streamingTimeSeries, timeSeries)

        # Test get of no data:
        out_streamingTimeSeries  = timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_2, cached=True)

        # We can check the equality again a simple TimeSeries
        empyt_timeSeries = TimeSeries()
        self.assertNotEqual(out_streamingTimeSeries, empyt_timeSeries)

        # The following test is just for confirm of the above steps. Should not be here in a proper unittesting approach.
        self.assertNotEqual(out_streamingTimeSeries, timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, cached=True))

        # Now test the get with start_dt and end_dt     
        from_dt = dt(2015,7,4,17,3,0, tzinfo='Europe/Rome')
        to_dt   = dt(2015,7,4,17,6,0, tzinfo='Europe/Rome')        
        out_streamingTimeSeries  = timeSeriesSQLiteStorage.get( sensor  = volumetricSensorV1_1,
                                                                from_dt = from_dt,
                                                                to_dt   = to_dt,
                                                                cached = True)
        timeSeries_filtered = timeSeries.filter(from_dt = from_dt, to_dt=to_dt)
        self.assertEqual(out_streamingTimeSeries, timeSeries_filtered)


    def test_PutGet_DataTimeSlots(self):
        
        timeSeriesSQLiteStorage = sqlite.TimeSeriesSQLiteStorage(in_memory=True)
        
        # Generate 10 slots TimeSeries with flowrate sensor aggregated data
        timeSeries = TimeSeries()
        for i in range(10):
            data = PhysicalData(labels = ['flowrate_m3s_i_AVG', 'flowrate_m3s_i_MIN', 'flowrate_m3s_i_MAX', 'volume_m3_e_TOT'],
                                            values = [20.6+i,20.6+i,20.6+i,20.6+i] ) 
            physicalDataTimeSlot = PhysicalDataTimeSlot(start = TimePoint(t=1436022000 + (i*60),tz="Europe/Rome"), 
                                                        end = TimePoint(t=1436022000 + ((i+1)*60), tz="Europe/Rome"),
                                                        data=data, type=TimeSlotType('60s'))
            timeSeries.append(physicalDataTimeSlot)        

        # Generate 10 points TimeSeries with light sensor aggregated data
        timeSeries_light = TimeSeries()
        for i in range(10):
            data = PhysicalData(labels = ['light_pct_i_AVG'], values = [20.6+i] ) 
            physicalDataTimeSlot = PhysicalDataTimeSlot(start = TimePoint(t=1436022000 + (i*60),tz="Europe/Rome"), 
                                                        end = TimePoint(t=1436022000 + ((i+1)*60), tz="Europe/Rome"),
                                                        data=data, type=TimeSlotType('60s'))
            timeSeries_light.append(physicalDataTimeSlot)      
        
  
        # Test put data without sensor (not implemented for now)
        with self.assertRaises(NotImplementedError):
            data_id_1 = timeSeriesSQLiteStorage.put(timeSeries)
        
        # Test volumetric sensor
        volumetricSensorV1_1 = VolumetricSensorV1('lu65na')
        volumetricSensorV1_2 = VolumetricSensorV1('lu34na')

        # Test labels inconsistency
        with self.assertRaises(InputException):
            timeSeriesSQLiteStorage.put(timeSeries_light, sensor=volumetricSensorV1_1)
        
        # Test put data with sensor and no right to create structure
        with self.assertRaises(StorageException):
            timeSeriesSQLiteStorage.put(timeSeries, sensor=volumetricSensorV1_1)

        # Test get with sensor and no structure in the storage
        with self.assertRaises(StorageException):
            _  = timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, timeSlotType=TimeSlotType('60s'), cached=True)

        # Test put data with sensor and right to create structure AND get with sensor and without from_dt/to_dt
        # TODO: this is not correct unit test of the put and get. It is testing them at the same time!
        timeSeriesSQLiteStorage.put(timeSeries, sensor=volumetricSensorV1_1, right_to_initialize=True)
        out_streamingTimeSeries  = timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, timeSlotType=TimeSlotType('60s'), cached=True)
        self.assertEqual(out_streamingTimeSeries, timeSeries)

        # Test get of no data:
        out_streamingTimeSeries  = timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_2, timeSlotType=TimeSlotType('60s'), cached=True)

        # We can check the equality again a simple TimeSeries
        empyt_timeSeries = TimeSeries()
        self.assertNotEqual(out_streamingTimeSeries, empyt_timeSeries)

        # The following test is just for confirm of the above steps. Should not be here in a proper unittesting approach.
        self.assertNotEqual(out_streamingTimeSeries, timeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, timeSlotType=TimeSlotType('60s'), cached=True))

        # Now test the get with start_dt and end_dt     
        from_dt = dt(2015,7,4,17,3,0, tzinfo='Europe/Rome')
        to_dt   = dt(2015,7,4,17,6,0, tzinfo='Europe/Rome')        
        out_streamingTimeSeries  = timeSeriesSQLiteStorage.get( sensor  = volumetricSensorV1_1,
                                                                from_dt = from_dt,
                                                                to_dt   = to_dt,
                                                                timeSlotType = TimeSlotType('60s'),
                                                                cached = True)
        timeSeries_filtered = timeSeries.filter(from_dt = from_dt, to_dt=to_dt)
        self.assertEqual(out_streamingTimeSeries, timeSeries_filtered)

    def tearDown(self):
        pass























