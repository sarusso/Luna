
**WARNING: this is alpha software under heavy development.**  
**First beta release is foreseen for October 2015.**

If you are interested in contributing please drop me a line at stefano.russo@gmail.com.


Luna
===

Luna is an high-level, highly customisable data analytics framework. Its roots are based on the physics and math which governs the reality around us, ensuring a coherent handling of almost any kind of data. The result is an extremely flexible framework that can suit a huge variety of use cases.


Just to give an idea, one of the most basic data structures of Luna is the Space, a representation of a mathematical n-dimensional space; while one of the most evolved ones is the PhysicalDataTimeSeries, a time series specifically designed to hold physical quantities which is very useful for the sensors data in the Internet of Things world. 

The core purpose of Luna is simple: take data out from a storage, process/aggregate it with some operations, put data in a storage.

The precessing/aggregation operations are user-defined (thus Luna is a framework and not a library) and can span from a simple average to complex machine learning models. 

The storage is also user-defined and can include on a broad set of technologies, like an MQTT stream, an Hadoop MapReduce input, a Cassandra NoSQL Database, a Redis cache, and of course the more classical SQL solutions as SQLite, Postgres, Oracle just to name a few.

A suite of precessing/aggregation operations and of common storages is provided with Luna.

Luna is very very well designed from a scalability point of view: there are no bottlenecks, and all the data processing pipeline can be run in a streaming-fashion way (i.e. using Hadoop Streaming to process Terabytes of data). It anyway runs of the box on your Laptop using SQLite for storing data, and it can be integrated in bigger projects just by writing a custom storage module.

Testing ![](https://api.travis-ci.org/sarusso/Luna.svg) 
---
Every commit on Luna codebase is tested with Travis-CI. This ensures a 
basic Continuos Integration check. [Check status on Travis](https://travis-ci.org/sarusso/Luna/).


Documentation
---
Coming soon


Demos
---
Coming soon






