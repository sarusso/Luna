
**WARNING: this is alpha software under heavy development.**  
**First beta release is foreseen for January 2016.**

If you are interested in contributing please drop me a line at stefano.russo@gmail.com.


Luna
====

Luna is an high-level, highly customisable data analytics framework. Its roots are based on the physics and math which governs the reality around us, ensuring a coherent handling of almost any kind of data. The result is an extremely flexible framework that can suit a huge variety of use cases.


Just to give an idea, one of the most basic data structures of Luna is the Space, a representation of a mathematical n-dimensional space; while one of the most evolved ones is the PhysicalDataTimeSeries, a time series specifically designed to hold physical quantities which is very useful for the sensors data in the Internet of Things world. 

The core purpose of Luna is simple: process/aggregate data with some operations, with an extensive support for data storages.

The precessing/aggregation operations are user-defined (thus Luna is a framework and not a library) and can span from a simple average to complex machine learning models. 

The storage is also user-defined and can include on a broad set of technologies, like an MQTT stream, an Hadoop MapReduce input, a Cassandra NoSQL Database, a Redis cache, and of course the more classical SQL solutions as SQLite, Postgres, Oracle just to name a few.

A suite of precessing/aggregation operations and of common storages is provided with Luna.

Luna is very very well designed from a scalability point of view: there are no bottlenecks, and all the data processing pipeline can be run in a streaming-fashion way (i.e. using Hadoop Streaming to process Terabytes of data). It anyway runs of the box on your Laptop using SQLite for storing data, and it can be integrated in bigger projects just by writing a custom storage module.

# Testing ![](https://api.travis-ci.org/sarusso/Luna.svg) 

Every commit on Luna codebase is tested with Travis-CI. This ensures a 
basic Continuos Integration check. [Check status on Travis](https://travis-ci.org/sarusso/Luna/).


# Quick Start

```python
#------------------------------------
# Logging
#------------------------------------
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("luna")

#------------------------------------
# Define a demo sensor
#------------------------------------
from luna.sensors import TimeBasedPhysicalDataSensor

class TemperatureSensorV1(TimeBasedPhysicalDataSensor):

    # Assign unique type_ID to sensor type
    type_ID = 5

    # Set metrics
    Points_data_labels = ['temperature_C']
    Slots_data_labels  = ['temperature_C_i_AVG', 
                          'temperature_C_i_MIN',
                          'temperature_C_i_MAX']

#------------------------------------
# Generate data
#------------------------------------
from luna.datatypes.composite import DataTimeSeries, PhysicalDataTimePoint
from luna.datatypes.dimensional import PhysicalData

# Generate 10 points TimeSeries with temperature sensor
dataTimeSeries = DataTimeSeries()
for i in range(100):
    data = PhysicalData( labels = ['temperature_C'], values = [20.6+i] ) 
    physicalDataTimePoint = PhysicalDataTimePoint(t = 1436022000 + (i*6),
                                                  tz="Europe/Rome", data=data)
    dataTimeSeries.append(physicalDataTimePoint)

print 'Generated timeSeries:', dataTimeSeries

#------------------------------------
# Initializa a (temporary) storage
#------------------------------------
from luna.storage.sqlite import sqlite
dataTimeSeriesSQLiteStorage = sqlite.DataTimeSeriesSQLiteStorage(in_memory=True,
                                                         right_to_initialize=True)

#------------------------------------
# Store data
#------------------------------------
dataTimeSeriesSQLiteStorage.put(dataTimeSeries, sensor=TemperatureSensorV1('sensor_id_1'))
print 'Stored timeSeries: ok'

#------------------------------------
# Get (all) data
#------------------------------------
time_series_out =  dataTimeSeriesSQLiteStorage.get(sensor=TemperatureSensorV1('sensor_id_1'))
print 'Loaded timeSeries:', time_series_out
time_series_out.force_load()
print 'Loaded timeSeries (load forced):', time_series_out

#------------------------------------
# Aggregate data
#------------------------------------
# Coming soon ...

```


# Documentation

## Operations and Generators ordering

The aggregators use operations and aggregators to aggregate the data. The operations are applied to a single quanity to generate another quantity,
while aggregators can be applied to more than one quantity (but generates only one quantity as the operations).

Standard aggregators and operations are privided in Luna. If you just aggregate a dataTimeSeries, by default only the AVG operation is applied.
To perfomr more complex aggregations you need to define a Sensor object. In the Sensor object, the Slots_data_labels list drives the aggregation.
Let's consider the following sensor as example:
For example, a Slots_data_labels with the following values:
    
    MyEnergySensor(PhysicalDataTimeSensor):
    
       Points_data_labels = ['power_W']
       Slots_data_labels  = ['power_W_AVG', 'power_W_MIN', 'power_W_MAX', 'energy_kWh_TOT']
    
When aggregating from points to slots, the aggregator will apply the AVG. MIN and MAX operations to the power, and 
will generate the new quantity energy_kWh_TOT using its generator. You can use standard operation and generators, 
or you can overwrite them in your Sensor class.

For example, if you modify your MyEnergySensor class to look like the following:

    MyEnergySensor(PhysicalDataTimeSensor):
    
        Points_data_labels = ['power_W']
        Slots_data_labels  = ['power_W_AVG', 'power_W_MIN', 'power_W_MAX', 'energy_kWh_TOT']
       
        class AVG(Operation):
            @staticmethod
            def generate(dataSeries, start_Point, end_Point, aggregated_datas):
                pass
       
        class energy_kWh_TOT(PhysicalQuantityGenerator):
       
            @staticmethod
            def compute_on_Points(dataSeries, start_Point, end_Point):
                pass

            @staticmethod
            def compute_on_Slots(dataSeries, start_Point, end_Point):
                pass

then Luna will use your AVG operation ad your energy_kWh_TOT generator. Please note that the order of the Slots_data_labels defines the order of the
operations/generators.

# Demos

Coming soon...


# Licensing
Luna is licensed under the Apache License, Version 2.0. See
[LICENSE](https://raw.githubusercontent.com/sarusso/Luna/master/LICENSE) for the full
license text.





