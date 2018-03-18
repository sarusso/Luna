#------------------------------------
# Logging
#------------------------------------
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("luna")

#------------------------------------
# Define a demo sensor
#------------------------------------
from luna.sensors import PhysicalDataTimeSensor
from luna.spacetime.time import TimeSlotSpan
from luna.datatypes.dimensional import TimeSlot

class TemperatureSensorV1(PhysicalDataTimeSensor):

    # Assign unique type_ID to sensor type
    type_ID = 5

    # Set metrics
    Points_data_labels = ['temperature_C']
    Slots_data_labels  = ['temperature_C_AVG', 
                          'temperature_C_MIN',
                          'temperature_C_MAX']
    # Set time zone
    timezone = 'Europe/Rome'

    # Set validty of the points (5 seconds)
    Points_validity_region = TimeSlot(span='5s')

#------------------------------------
# Initialize the demo sensor
#------------------------------------
sensor = TemperatureSensorV1('sensor_id_1')

#------------------------------------
# Generate RAW data
#------------------------------------
from luna.datatypes.dimensional import PhysicalData, DataTimeSeries, PhysicalDataTimePoint

# Generate a point every 6 seconds for about 10 minutes
dataTimeSeries = DataTimeSeries()
for i in range(104):
    data = PhysicalData( labels = ['temperature_C'], values = [20.0+i] ) 
    physicalDataTimePoint = PhysicalDataTimePoint(t    = 1436021994 + (i*6),
                                                  tz   = "Europe/Rome",
                                                  data = data)
    dataTimeSeries.append(physicalDataTimePoint)

print('DEMO: Generated dataTimeSeries: {}'.format(dataTimeSeries))

#------------------------------------
# Initializa a (temporary) storage
#------------------------------------
from luna.storages.sqlite import sensor_storage as storage
dataTimeSeriesSQLiteStorage = storage.DataTimeSeriesSQLiteStorage(in_memory=True, can_initialize=True)

#------------------------------------
# Store RAW data
#------------------------------------
dataTimeSeriesSQLiteStorage.put(dataTimeSeries, sensor=sensor)
print('DEMO: Stored dataTimeSeries: ok')

#------------------------------------
# Get (all) RAW data
#------------------------------------
dataTimeSeries =  dataTimeSeriesSQLiteStorage.get(sensor=sensor)
print('DEMO: Loaded dataTimeSeries: {}'.format(dataTimeSeries))
dataTimeSeries.force_load()
print('DEMO: Loaded dataTimeSeries (load forced): {}'.format(dataTimeSeries))

#------------------------------------
# Aggregate data
#------------------------------------
from luna.spacetime.time import dt
from_dt = dt(2015,7,4,17,0,0, tz=sensor.timezone)
to_dt = dt(2015,7,4,17,10,0, tz=sensor.timezone)

#------------------------------------
# Initialize aggregator process
#------------------------------------
from luna.aggregators.components import DataTimeSeriesAggregatorProcess

dataTimeSeriesAggregatorProcess = DataTimeSeriesAggregatorProcess(timeSlotSpan      = TimeSlotSpan('5m'),
                                                                  Sensor            = sensor,
                                                                  data_to_aggregate = PhysicalDataTimePoint)

#------------------------------------
# Start aggregator process
#------------------------------------   
print ('DEMO: Starting aggregation')
dataTimeSeriesAggregatorProcess.start(dataTimeSeries   = dataTimeSeries,
                                      start_dt         = from_dt,
                                      end_dt           = to_dt,
                                      rounded          = True,
                                      threaded         = False)

#------------------------------------
# Get results from the aggregation
#------------------------------------  

# Since points were generated every 6 seconds but their validity was only 5 secs,
# there will be no 100% coverage.

results_dataTimeSeries = dataTimeSeriesAggregatorProcess.get_results()
print ('DEMO: Getting results:')
for item in results_dataTimeSeries:
    print(' First result: {} data content: {}'.format(item, item.data.content))

#------------------------------------
# Store aggregated data
#------------------------------------
dataTimeSeriesSQLiteStorage.put(results_dataTimeSeries, sensor=sensor)
print('DEMO: Stored results_dataTimeSeries: ok')

#------------------------------------
# Get aggregated data
#------------------------------------
results_dataTimeSeries =  dataTimeSeriesSQLiteStorage.get(sensor       = sensor,
                                                          from_dt      = from_dt,
                                                          to_dt        = to_dt,
                                                          timeSlotSpan = TimeSlotSpan('5m'))

print('DEMO: Loaded results_dataTimeSeries: {}'.format(results_dataTimeSeries))
results_dataTimeSeries.force_load()
print('DEMO: Loaded dataTimeSeries (load forced): {}'.format(results_dataTimeSeries))

