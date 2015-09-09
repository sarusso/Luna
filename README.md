

Luna
===

Luna is an high-level, highly customizable data analytcis framewrok. Its roots are based on the physics which governs the reality around us, ensuring a coherent handling of almost any kind of data. The result is an extremely flexible framework that can suit a huge variety of use cases.

The pourpose of luna is simple: take data out from a storage, aggregate it with some operations, put data in a storage.

The aggregation operations are user-defined (thus Luna is a framework and not a library) and can span from a simple average to complex machine learing models.

The storage is also user-defined and can include on a broad set of technolgies, like an MQTT stream, an Hadoop MapReduce input, a Cassandra NoSQL Database, a Redis cache, and of course the more classical SQL solutions as SQLite, Postgres, Oracle.

Luna is very very well designed from a sacalibility point of view: there are no bottlenecks, and all the data processing pipeline can be run in a streming-fashion (i.e. using Hadoop Streaming to process Terabytes of data). It anyway runs of the box on your Laptop using SQLite for storing data, and it can be integrated in bigger projects just by writing a custom storage module.








