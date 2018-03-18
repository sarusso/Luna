#------------------------------------
# Logging
#------------------------------------
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("luna")


#------------------------------------
# Generate RAW data
#------------------------------------
from luna.datatypes.dimensional import DataTimeSlot
from luna.datatypes.dimensional import DataTimeSlotSeries
from luna.datatypes.dimensional import TimePoint

# Generate a point every 6 seconds for about 10 minutes
dataTimeSlotSeries = DataTimeSlotSeries()
for i in range(104):
    data = {'temperature_C': [20.0+i]} 
    dataTimeSlot = DataTimeSlot(start = TimePoint(t=1436051994 + (i*6), tz   = "Europe/Rome"),
                                 end   = TimePoint(t=1436051994 + (i*6) +1, tz   = "Europe/Rome",),
                                 data = data)
    dataTimeSlotSeries.append(dataTimeSlot)



print('DEMO: Generated dataTimeSeries: {}'.format(dataTimeSlotSeries))


#------------------------------------
# Initializa a Postgres storage
#------------------------------------
from luna.storages.postgres.storage import PostgresStorage
storage = PostgresStorage(host='localhost', port=5432, db_name='DBNAME', db_user='DBUSER', db_pass='DBPASS', can_initialize=True)
 
 
#------------------------------------
# Store Slot data
#------------------------------------
storage.put(dataTimeSlotSeries, id='1000001')
print('DEMO: Stored dataTimeSeries: ok')
 
 
#------------------------------------
# Get (all) RAW data
#------------------------------------
dataTimeSlotSeries =  storage.get(id='1000001', timeSpan='1s', tz='Europe/London')
print('DEMO: Loaded dataTimeSeries: {}'.format(dataTimeSlotSeries))
#dataTimeSlotSeries.force_load()
#print('DEMO: Loaded dataTimeSeries (load forced): {}'.format(dataTimeSlotSeries))
 
for dataTimeSlot in dataTimeSlotSeries:
    print('DEMO: dataTimeSlot @ start_t={}, end_t={} (start_dt="{}", end_dt="{}"), data="{}"'.format(dataTimeSlot.start.t,
                                                                                                     dataTimeSlot.end.t,
                                                                                                     dataTimeSlot.start.dt,
                                                                                                     dataTimeSlot.end.dt,
                                                                                                     dataTimeSlot.data))





