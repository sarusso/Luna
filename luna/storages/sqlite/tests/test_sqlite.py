import unittest
from luna.datatypes.dimensional import DataTimeSeries, DataTimePoint, PhysicalDataTimePoint, PhysicalDataTimeSlot, StreamingDataTimeSeries
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException, StorageException
from luna.spacetime.time import dt, TimeSlotSpan
from luna.datatypes.dimensional import TimePoint, Point, PhysicalData
from luna.sensors import PhysicalDataTimeSensor
from luna.storages.sqlite import sensor_storage, storage
import json

# TODO: this should be a generic storage test system, which should be then applied
# to the various modules (that can be write or read only)


#------------------------------------
# Logging
#------------------------------------

# Enable only critical logging in unit tests by default
logging.basicConfig(level=logging.CRITICAL) 
logger = logging.getLogger("luna")


#------------------------------------
# Define demo sensor
#------------------------------------

class VolumetricSensorV1(PhysicalDataTimeSensor):

    # Assign unique type_ID to this sensor type
    type_ID = 5

    # Set Points expected lables
    Points_data_labels = ['flowrate_m3s']
    
    # Set Slots operators
    Slots_data_labels  = ['flowrate_m3s_AVG', 'flowrate_m3s_MIN', 'flowrate_m3s_MAX', 'volume_m3_TOT'] 
    
    # Set validity region span for points
    Points_validity_region = TimeSlot(span='1m')
    
    # Fixed timezone:
    timezone = "Europe/Rome"


#------------------------------------
# Sensor Storage Tests
#------------------------------------

class test_sqlite_sensor_storage(unittest.TestCase):

    def setUp(self):       
        pass


    def test_Init(self):    
        _ = sensor_storage.DataTimeSeriesSQLiteStorage(in_memory=True)

    def test_PutGet_DataTimePoints(self):
        
        dataTimeSeriesSQLiteStorage = sensor_storage.DataTimeSeriesSQLiteStorage(in_memory=True)
        
        # Generate 10 points DataTimeSeries with flowrate sensor
        dataTimeSeries = DataTimeSeries()
        for i in range(10):
            data = PhysicalData( labels = ['flowrate_m3s'], values = [20.6+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
            dataTimeSeries.append(physicalDataTimePoint)

        # Generate 10 points DataTimeSeries with light sensor
        dataTimeSeries_light = DataTimeSeries()
        for i in range(10):
            data = PhysicalData( labels = ['light_pct'], values = [60.6+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
            dataTimeSeries_light.append(physicalDataTimePoint)
        
        # Test put data without sensor (not implemented for now)
        with self.assertRaises(NotImplementedError):
            data_id_1 = dataTimeSeriesSQLiteStorage.put(dataTimeSeries)
        
        # Test volumetric sensor
        volumetricSensorV1_1 = VolumetricSensorV1('lu65na')
        volumetricSensorV1_2 = VolumetricSensorV1('lu34na')
        
        # Test labels inconsistency
        with self.assertRaises(InputException):
            dataTimeSeriesSQLiteStorage.put(dataTimeSeries_light, sensor=volumetricSensorV1_1)
        
        # Test put data with sensor and no right to create structure
        with self.assertRaises(StorageException):
            dataTimeSeriesSQLiteStorage.put(dataTimeSeries, sensor=volumetricSensorV1_1)

        # Test get with sensor and no structure in the storage
        with self.assertRaises(StorageException):
            _  = dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, cached=True)

        # Test put data with sensor and right to create structure AND get with sensor and without from_dt/to_dt
        # TODO: this is not correct unit test of the put and get. It is testing them at the same time!
        dataTimeSeriesSQLiteStorage.put(dataTimeSeries, sensor=volumetricSensorV1_1, can_initialize=True)
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, cached=True)
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries)

        # Test get of no data:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_2, cached=True)

        # We can check the equality against a simple DataTimeSeries
        empyt_dataTimeSeries = DataTimeSeries()
        self.assertEqual(out_streamingDataTimeSeries, empyt_dataTimeSeries)

        # The following test is just for confirm of the above steps. Should not be here in a proper unittesting approach.
        self.assertNotEqual(out_streamingDataTimeSeries, dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, cached=True))

        # Now test the get with start_dt and end_dt     
        from_dt = dt(2015,7,4,17,3,0, tzinfo='Europe/Rome')
        to_dt   = dt(2015,7,4,17,6,0, tzinfo='Europe/Rome')        
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get( sensor  = volumetricSensorV1_1,
                                                                from_dt = from_dt,
                                                                to_dt   = to_dt,
                                                                cached = True)
        dataTimeSeries_filtered = dataTimeSeries.filter(from_dt = from_dt, to_dt=to_dt)
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)


    def test_PutGet_DataTimeSlots(self):
        
        dataTimeSeriesSQLiteStorage = sensor_storage.DataTimeSeriesSQLiteStorage(in_memory=True)
        
        # Generate 10 slots DataTimeSeries with flowrate sensor aggregated data
        dataTimeSeries = DataTimeSeries()
        for i in range(10):
            data = PhysicalData(labels = ['flowrate_m3s_AVG', 'flowrate_m3s_MIN', 'flowrate_m3s_MAX', 'volume_m3_TOT'],
                                            values = [20.6+i,20.6+i,20.6+i,20.6+i] ) 
            physicalDataTimeSlot = PhysicalDataTimeSlot(start = TimePoint(t=1436022000 + (i*60),tz="Europe/Rome"), 
                                                        end = TimePoint(t=1436022000 + ((i+1)*60), tz="Europe/Rome"),
                                                        data=data, span=TimeSlotSpan('60s'))
            dataTimeSeries.append(physicalDataTimeSlot)        

        # Generate 10 points DataTimeSeries with light sensor aggregated data
        dataTimeSeries_light = DataTimeSeries()
        for i in range(10):
            data = PhysicalData(labels = ['light_pct_AVG'], values = [20.6+i] ) 
            physicalDataTimeSlot = PhysicalDataTimeSlot(start = TimePoint(t=1436022000 + (i*60),tz="Europe/Rome"), 
                                                        end = TimePoint(t=1436022000 + ((i+1)*60), tz="Europe/Rome"),
                                                        data=data, span=TimeSlotSpan('60s'))
            dataTimeSeries_light.append(physicalDataTimeSlot)      
        
  
        # Test put data without sensor (not implemented for now)
        with self.assertRaises(NotImplementedError):
            data_id_1 = dataTimeSeriesSQLiteStorage.put(dataTimeSeries)
        
        # Test volumetric sensor
        volumetricSensorV1_1 = VolumetricSensorV1('lu65na')
        volumetricSensorV1_2 = VolumetricSensorV1('lu34na')

        # Test labels inconsistency
        with self.assertRaises(InputException):
            dataTimeSeriesSQLiteStorage.put(dataTimeSeries_light, sensor=volumetricSensorV1_1)
        
        # Test put data with sensor and no right to create structure
        with self.assertRaises(StorageException):
            dataTimeSeriesSQLiteStorage.put(dataTimeSeries, sensor=volumetricSensorV1_1)

        # Test get with sensor and no structure in the storage
        with self.assertRaises(StorageException):
            _  = dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, timeSlotSpan=TimeSlotSpan('60s'), cached=True)

        # Test put data with sensor and right to create structure AND get with sensor and without from_dt/to_dt
        # TODO: this is not correct unit test of the put and get. It is testing them at the same time!
        dataTimeSeriesSQLiteStorage.put(dataTimeSeries, sensor=volumetricSensorV1_1, can_initialize=True)
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, timeSlotSpan=TimeSlotSpan('60s'), cached=True)
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries)

        # Test get of no data:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_2, timeSlotSpan=TimeSlotSpan('60s'), cached=True)

        # We can check the equality against a simple DataTimeSeries
        empyt_dataTimeSeries = DataTimeSeries()
        self.assertEqual(out_streamingDataTimeSeries, empyt_dataTimeSeries)

        # The following test is just for confirm of the above steps. Should not be here in a proper unittesting approach.
        self.assertNotEqual(out_streamingDataTimeSeries, dataTimeSeriesSQLiteStorage.get(sensor=volumetricSensorV1_1, timeSlotSpan=TimeSlotSpan('60s'), cached=True))

        # Now test the get with start_dt and end_dt     
        from_dt = dt(2015,7,4,17,3,0, tzinfo='Europe/Rome')
        to_dt   = dt(2015,7,4,17,6,0, tzinfo='Europe/Rome')        
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get( sensor  = volumetricSensorV1_1,
                                                                from_dt = from_dt,
                                                                to_dt   = to_dt,
                                                                timeSlotSpan = TimeSlotSpan('60s'),
                                                                cached = True)
        dataTimeSeries_filtered = dataTimeSeries.filter(from_dt = from_dt, to_dt=to_dt)
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)
        
        # Also test that if we go trough the cached streaminTimeSeries again, we get the same result:
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)
        
        
        # Now get the time series without caching:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get( sensor  = volumetricSensorV1_1,
                                                        from_dt = from_dt,
                                                        to_dt   = to_dt,
                                                        timeSlotSpan = TimeSlotSpan('60s'))
        
        # Check that we can compare it as is even if it is not cached:
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)

        # Check that we can compare it again:
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)        

        
        # Now get AGAIn the time series without caching:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get( sensor  = volumetricSensorV1_1,
                                                        from_dt = from_dt,
                                                        to_dt   = to_dt,
                                                        timeSlotSpan = TimeSlotSpan('60s'))
        
        # But this time do not test any comparisons (that triggers the caching of the TimeSeries),
        # instead test that going trough it twice we achieve the same result (under the hood we go twice in the DB):
        
        items_A = [item for item in out_streamingDataTimeSeries]
        items_B = [item for item in out_streamingDataTimeSeries]
        
        self.assertEqual(items_A, items_B)

        # WARNING: This is specific to SLQlite and its dataTimeStream
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 2)
        
        # Now foce load te time series:
        out_streamingDataTimeSeries.force_load()

        # After force-loading, another soruce acces is performed
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 3)
        
        items_C = [item for item in out_streamingDataTimeSeries]
        
        self.assertEqual(items_A, items_C)

        # Generating the list items_C after a force_load should not generate a new source_access
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 3)

        # Perform again the iterator check:
        items_A = [item for item in out_streamingDataTimeSeries]
        items_B = [item for item in out_streamingDataTimeSeries]
        
        self.assertEqual(items_A, items_B)
 
        # And ensure that the source accesses is still set to three
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 3)
     

    def tearDown(self):
        pass









#------------------------------------
# Sensor Storage Tests
#------------------------------------

class test_sqlite_storage(unittest.TestCase):

    def setUp(self):       
        pass


    def test_Init(self):    
        _ = storage.SQLiteStorage(in_memory=True)

    def test_PutGet_DataTimePoints(self):
        
        dataTimeSeriesSQLiteStorage = storage.SQLiteStorage(in_memory=True)
        
        # Generate 10 points DataTimeSeries with flowrate
        dataTimeSeries = DataTimeSeries()
        for i in range(10):
            data = json.dumps({'flowrate_m3s': 20.6+i})
            dataTimePoint = DataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
            dataTimeSeries.append(dataTimePoint)

        # Generate 10 points DataTimeSeries with light
        dataTimeSeries_light = DataTimeSeries()
        for i in range(10):
            data = json.dumps({'light_pct': 60.6+i})
            dataTimePoint = DataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
            dataTimeSeries_light.append(dataTimePoint)
        
        # Test put data without id (not implemented for now)
        with self.assertRaises(NotImplementedError):
            data_id_1 = dataTimeSeriesSQLiteStorage.put(dataTimeSeries)
        
        # Test put data with id and no right to create structure
        with self.assertRaises(StorageException):
            dataTimeSeriesSQLiteStorage.put(dataTimeSeries, id='0000001')

        # Test get with id and no structure in the storage
        with self.assertRaises(StorageException):
            _  = dataTimeSeriesSQLiteStorage.get(id='0000001', cached=True)

        # Test put data with id and right to create structure AND get with id and without from_dt/to_dt
        # TODO: this is not correct unit test of the put and get. It is testing them at the same time!
        dataTimeSeriesSQLiteStorage.put(dataTimeSeries, id='0000001', can_initialize=True)
        out_streamingDataTimeSeries_UTC  = dataTimeSeriesSQLiteStorage.get(id='0000001', cached=True)
        out_streamingDataTimeSeries      = dataTimeSeriesSQLiteStorage.get(id='0000001', cached=True, tz='Europe/Rome')
        
        # Check len
        self.assertEqual(len(out_streamingDataTimeSeries), len(dataTimeSeries))
        self.assertEqual(len(out_streamingDataTimeSeries_UTC), len(dataTimeSeries))
        
        # Quick test
        for i, dataPoint in enumerate(dataTimeSeries):
            self.assertEqual(out_streamingDataTimeSeries[dataPoint.t].t, dataPoint.t)
            self.assertEqual(out_streamingDataTimeSeries[dataPoint.t].data, dataPoint.data)

        # Quick test
        for i, dataPoint in enumerate(dataTimeSeries):
            self.assertEqual(out_streamingDataTimeSeries_UTC[dataPoint.t].t, dataPoint.t)
            self.assertEqual(out_streamingDataTimeSeries[dataPoint.t].data, dataPoint.data)

        # Time Series equality does not work anymore (therefore the above quick tests)
        #self.assertEqual(out_streamingDataTimeSeries_UTC, dataTimeSeries)
        #self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries)
        
        # Test get of no data:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(id='0000002', cached=True)

        # We can check the equality against a simple DataTimeSeries
        empyt_dataTimeSeries = DataTimeSeries()
        self.assertEqual(out_streamingDataTimeSeries, empyt_dataTimeSeries)

        # The following test is just for confirm of the above steps. Should not be here in a proper unittesting approach.
        self.assertNotEqual(out_streamingDataTimeSeries, dataTimeSeriesSQLiteStorage.get(id='0000001', cached=True))

        # Now test the get with start_dt and end_dt     
        from_dt = dt(2015,7,4,17,3,0, tzinfo='Europe/Rome')
        to_dt   = dt(2015,7,4,17,6,0, tzinfo='Europe/Rome')        
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get( id='0000001',
                                                                from_dt = from_dt,
                                                                to_dt   = to_dt,
                                                                cached = True)
        dataTimeSeries_filtered = dataTimeSeries.filter(from_dt = from_dt, to_dt=to_dt)
        
        # Quick test
        for i, dataPoint in enumerate(dataTimeSeries_filtered):
            self.assertEqual(out_streamingDataTimeSeries[dataPoint.t].t, dataPoint.t)
            self.assertEqual(out_streamingDataTimeSeries[dataPoint.t].data, dataPoint.data)

        # Time Series equality does not work anymore (therefore the above quick tests)
        #self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)


    def test_PutGet_DataTimeSlots(self):
        
        dataTimeSeriesSQLiteStorage = storage.SQLiteStorage(in_memory=True)
        
        # Generate 10 slots DataTimeSeries with flowrate aggregated data
        dataTimeSeries = DataTimeSeries()
        for i in range(10):
            data = json.dumps({'flowrate_m3s_AVG':20.6+i, 'flowrate_m3s_MIN':20.6+i, 'flowrate_m3s_MAX':20.6+i, 'volume_m3_TOT':20.6+i})
            dataTimeSlot = DataTimeSlot(start = TimePoint(t=1436022000 + (i*60),tz="Europe/Rome"), 
                                        end   = TimePoint(t=1436022000 + ((i+1)*60), tz="Europe/Rome"),
                                        data  = data, span=TimeSlotSpan('60s'))
            dataTimeSeries.append(dataTimeSlot)        

        # Generate 10 points DataTimeSeries with light aggregated data
        dataTimeSeries_light = DataTimeSeries()
        for i in range(10):
            data = json.dumps({'light_pct_AVG':20.6+i}) 
            dataTimeSlot = DataTimeSlot(start = TimePoint(t=1436022000 + (i*60),tz="Europe/Rome"), 
                                        end   = TimePoint(t=1436022000 + ((i+1)*60), tz="Europe/Rome"),
                                        data  = data, span=TimeSlotSpan('60s'))
            dataTimeSeries_light.append(dataTimeSlot)      
        
  
        # Test put data without id (not implemented for now)
        with self.assertRaises(NotImplementedError):
            data_id_1 = dataTimeSeriesSQLiteStorage.put(dataTimeSeries)

        # Test put data with id and no right to create structure
        with self.assertRaises(StorageException):
            dataTimeSeriesSQLiteStorage.put(dataTimeSeries, id='0000001')

        # Test get with id and no structure in the storage
        with self.assertRaises(StorageException):
            _  = dataTimeSeriesSQLiteStorage.get(id='0000001', timeSpan='60s', cached=True)

        # Test put data with id and right to create structure AND get with id and without from_dt/to_dt
        # TODO: this is not correct unit test of the put and get. It is testing them at the same time!
        dataTimeSeriesSQLiteStorage.put(dataTimeSeries, id='0000001', can_initialize=True)
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(id='0000001', timeSpan='60s', cached=True)
        
        # Check length
        self.assertEqual(len(out_streamingDataTimeSeries), len(dataTimeSeries))

        return

        #=====================================================
        #  TODO: Finish adapting the tests for this storage
        #=====================================================
        
        # Quick test
        #for i, dataPoint in enumerate(dataTimeSeries):
        #    print dataPoint
        #    #self.assertEqual(.t, dataPoint.strat.t)
        #    #self.assertEqual(out_streamingDataTimeSeries[dataPoint.start.t].data, dataPoint.data)

        # Time Series equality does not work anymore (therefore the above quick tests)        
        #self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries)

        # Test get of no data:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(id='0000002', timeSpan='60s', cached=True)

        # We can check the equality against a simple DataTimeSeries
        empyt_dataTimeSeries = DataTimeSeries()
        self.assertEqual(out_streamingDataTimeSeries, empyt_dataTimeSeries)

        # The following test is just for confirm of the above steps. Should not be here in a proper unittesting approach.
        self.assertNotEqual(out_streamingDataTimeSeries, dataTimeSeriesSQLiteStorage.get(id='0000001', timeSpan='60s', cached=True))

        # Now test the get with start_dt and end_dt     
        from_dt = dt(2015,7,4,17,3,0, tzinfo='Europe/Rome')
        to_dt   = dt(2015,7,4,17,6,0, tzinfo='Europe/Rome')        
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(id='0000001',
                                                                from_dt  = from_dt,
                                                                to_dt    = to_dt,
                                                                timeSpan = '60s',
                                                                cached   =  True)
        dataTimeSeries_filtered = dataTimeSeries.filter(from_dt = from_dt, to_dt=to_dt)
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)
        
        # Also test that if we go trough the cached streaminTimeSeries again, we get the same result:
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)
        
        
        # Now get the time series without caching:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(id='0000001',
                                                        from_dt = from_dt,
                                                        to_dt   = to_dt,
                                                        timeSpan = '60s')
        
        # Check that we can compare it as is even if it is not cached:
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)

        # Check that we can compare it again:
        self.assertEqual(out_streamingDataTimeSeries, dataTimeSeries_filtered)        

        
        # Now get AGAIn the time series without caching:
        out_streamingDataTimeSeries  = dataTimeSeriesSQLiteStorage.get(id='0000001',
                                                        from_dt = from_dt,
                                                        to_dt   = to_dt,
                                                        timeSpan = '60s')
        
        # But this time do not test any comparisons (that triggers the caching of the TimeSeries),
        # instead test that going trough it twice we achieve the same result (under the hood we go twice in the DB):
        
        items_A = [item for item in out_streamingDataTimeSeries]
        items_B = [item for item in out_streamingDataTimeSeries]
        
        self.assertEqual(items_A, items_B)

        # WARNING: This is specific to SLQlite and its dataTimeStream
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 2)
        
        # Now foce load te time series:
        out_streamingDataTimeSeries.force_load()

        # After force-loading, another soruce acces is performed
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 3)
        
        items_C = [item for item in out_streamingDataTimeSeries]
        
        self.assertEqual(items_A, items_C)

        # Generating the list items_C after a force_load should not generate a new source_access
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 3)

        # Perform again the iterator check:
        items_A = [item for item in out_streamingDataTimeSeries]
        items_B = [item for item in out_streamingDataTimeSeries]
        
        self.assertEqual(items_A, items_B)
 
        # And ensure that the source accesses is still set to three
        self.assertEqual(out_streamingDataTimeSeries.dataTimeStream.get_statistics()['source_acceses'], 3)
     

    def tearDown(self):
        pass





















