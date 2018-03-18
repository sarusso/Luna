#------------------------------------
# Logging
#------------------------------------
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("luna")


#------------------------------------
# Generate RAW data
#------------------------------------
from luna.datatypes.dimensional import DataTimePoint
from luna.datatypes.dimensional import DataTimePointSeries

# Generate a point every 6 seconds for about 10 minutes
dataTimePointSeries = DataTimePointSeries()
for i in range(104):
    data = {'temperature_C': [20.0+i]} 
    dataTimePoint = DataTimePoint(t    = 1436021994 + (i*6),
                                  tz   = "Europe/Rome",
                                  data = data)
    dataTimePointSeries.append(dataTimePoint)



print('DEMO: Generated dataTimeSeries: {}'.format(dataTimePointSeries))


#------------------------------------
# Initializa a (temporary) storage
#------------------------------------
from luna.storages.sqlite.storage import SQLiteStorage
storage = SQLiteStorage(in_memory=True, can_initialize=True)


#------------------------------------
# Store Point data
#------------------------------------
storage.put(dataTimePointSeries, id='328or6c269')
print('DEMO: Stored dataTimeSeries: ok')


#------------------------------------
# Get (all) RAW data
#------------------------------------
dataTimePointSeries =  storage.get(id='328or6c269', tz='Europe/London')
print('DEMO: Loaded dataTimeSeries: {}'.format(dataTimePointSeries))
dataTimePointSeries.force_load()
print('DEMO: Loaded dataTimeSeries (load forced): {}'.format(dataTimePointSeries))

for dataTimePoint in dataTimePointSeries:
    print('DEMO: dataTimePoint @ t={} (dt={}), data="{}"'.format(dataTimePoint.t, dataTimePoint.dt, dataTimePoint.data))





