from luna.datatypes.dimensional import PhysicalData, TimePoint, TimeSlot
from luna.datatypes.dimensional import DataTimeSeries, PhysicalDataTimePoint, PhysicalDataTimeSlot, DataTimePoint, DataPoint, DataTimeSlot
from luna.storage import Storage
from luna.spacetime.time import s_from_dt, dt_from_s
from luna.datatypes.dimensional import StreamingDataTimeSeries, DataTimeStream
from luna.common.exceptions import InputException, ConsistencyException, StorageException
import sqlite3
import os
import math
from collections import namedtuple
import psycopg2
import psycopg2.extras


# Logger
import logging
logger = logging.getLogger(__name__)

LUNA_DIR  = '.luna'
USER_HOME = os.path.expanduser("~")
LUNA_HOME = os.path.join(USER_HOME,LUNA_DIR)

#-------------------------
# Utility functions
#-------------------------

def trunc(invalue, digits):
    return int(invalue*math.pow(10,digits))/math.pow(10,digits);
    
def fix_label_from_sqlite(label):
    return label.replace('__','-')

def fix_label_to_sqlite(label):
    return label.replace('-','__').lower()
    


#------------------------------------------------#
#          WARNING: alpha code                   #
#------------------------------------------------#

# TODO: naming?
# PostgresDataTimeStream -> PostgresDataStream
# DataTimeSeriesPostgresStorage -> PostgresStorage


#-------------------------
# Data stream
#-------------------------

class PostgresDataTimeStream(DataTimeStream):
    ''' Data time stream implementation in Postgres'''
     
    def __init__(self, cur, query, sensor, data_type, labels=None, truncate=None, timeSlotSpan=None):
               
        # Save sensor
        self.sensor = sensor


        # Check valid type 
        if not ( issubclass(data_type, DataTimePoint)  or issubclass(data_type, DataTimeSlot) ):
            raise InputException('With this datastream type must be instance of DataTimePoint or DataTimeSlot')

        self.cur       = cur        
        self.query     = query
        self.query_cur = None
        self.data_type = data_type
        self.truncate  = truncate
        self.labels    = None
        self.source_acceses = 0
        self.timeSlotSpan = timeSlotSpan
        
        # TODO: Call parent init, use kwargs, pop var names, etc.
        #super(PostgresDataTimeStream, self).__init__(*args, **kwargs)
        
        
    # Iterator
    def __iter__(self):
        self.query_cur = self.cur.execute(self.query)
        self.source_acceses += 1
        return self

    def __next__(self):
        
        # TODO: do we like a while True here?
        while True:
            
            try:
                # Python 2.x
                # The following will raise StopIteration for us to stop the iterator
                db_data = self.query_cur.next()
            
            except AttributeError:
                # Python 3.x
                db_data = self.query_cur.fetchone()
                if not db_data:
                    raise StopIteration()

            if not self.labels:
                if issubclass(DataTimePoint, self.data_type):
                    self.labels = self.sensor.Points_data_labels  
                elif issubclass(DataTimeSlot, self.data_type):
                    self.labels = self.sensor.Slots_data_labels
                else:
                    raise ConsistencyException('Got unknown type: {}'.format(self.data_type))
    
            # We will have to instantiate the TimePoint from the db data.
    
            # Note:
            # self.sensor.data_type      = PhysicalDataTimePoint
            # self.sensor.data_data_type = PhysicalDimensionalData
        
            DataTime_Point_or_Slot = None
        
            # Hanlde the case of the Points
            if issubclass(DataTimePoint, self.data_type):
                values = list(db_data[2:])
                # Skip if the data is saved as None
                if None in values:
                    continue
                try:
                    data = self.sensor.Points_type.data_type(labels=self.labels, values = values)
                except InputException as e:
                    logger.error("Could not initialize {} with labels={} and values={}, got error: {}".format(self.sensor.Points_type.data_type, self.labels, values, e)) 
                else:
                    DataTime_Point_or_Slot = self.sensor.Points_type(t                    = db_data[0],
                                                                     tz                   = self.sensor.timezone,
                                                                     data                 = data,
                                                                     validity_region      = self.sensor.Points_validity_region)
    
            # Hanlde the case of the Slots
            elif issubclass(DataTimeSlot, self.data_type):
                values = list(db_data[4:-1])
                # Skip if the data is saved as None
                if None in values:
                    continue
                try:
                    data = self.sensor.Slots_type.data_type(labels=self.labels, values=values)
                except InputException as e:
                    logger.error("Could not initialize {} with labels={} and values={}, error: '{}'".format(self.sensor.Slots_type.data_type, self.labels, values, e)) 
                else:
                    if self.timeSlotSpan is not None:
                        DataTime_Point_or_Slot = self.sensor.Slots_type(start    = TimePoint(t=db_data[0], tz = "Europe/Rome"),
                                                                        end      = TimePoint(t=db_data[1], tz = "Europe/Rome"),
                                                                        data     = data,
                                                                        span     = self.timeSlotSpan,
                                                                        coverage = db_data[-1])
                    else:
                        DataTime_Point_or_Slot = self.sensor.Slots_type(start    = TimePoint(t=db_data[0], tz = "Europe/Rome"),
                                                                        end      = TimePoint(t=db_data[1], tz = "Europe/Rome"),
                                                                        data     = data,
                                                                        coverage = db_data[-1])
            else:
                raise ConsistencyException('Unknown type, got {}'.format(self.data_type))  
            
            # This get when a validty of a Point ends. For TimeSlots and seconds, it is a bit of overhead
            #_ = DataTime_Point_or_Slot.validity_interval.duration_s()
            if DataTime_Point_or_Slot is None:
                raise StopIteration()
            return DataTime_Point_or_Slot     

    # Python 2.x
    def next(self):
        return self.__next__()
    
    def get_statistics(self):
        return {'source_acceses': self.source_acceses}

#-------------------------
# Main storage class
#-------------------------

class PostgresStorage(Storage):
    def __init__(self, can_initialize=False, host=None, port=None, dbname=None, username=None, password=None):

        # Sanity checks
        # TODO...

        conn_string = "host='{0}' port='{1}' dbname='{2}' user='{3}' password='{4}'".format(host, port, dbname, username, password)
        logger.info("Connecting to database: {0}".format(conn_string.replace(password, '******')))
        
        # Get a connection, if a connect cannot be made an exception will be raised here
        self.conn = psycopg2.connect(conn_string)
      
        # Named tuples cursor
        #self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
         
        # Dict tuples cursor
        #self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        self.schema = 'public'
 
        # Right to initialize
        self.can_initialize = can_initialize


#-------------------------
# Time 
#-------------------------

class DataTimeSeriesPostgresStorage(PostgresStorage):


    #--------------------
    # STRUCTURE
    #--------------------

    def check_structure_for_DataTimePoints(self, sensor, can_initialize=False):
        raise NotImplementedError()
            

    def initialize_structure_for_DataTimePoints(self, cur, sensor):
        raise NotImplementedError()


    def check_structure_for_DataTimeSlots(self, sensor, can_initialize=False):
        '''Check that the structure of the storage exists for a given sensor'''
        
        # Get the cursor
        cur = self.conn.cursor()    
        
        # Check if right table exists:
        query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables  WHERE  table_schema = '{}' AND  table_name = '{}_DataTimeSlots' );".format(self.schema, sensor.__class__.__name__) 
        
        # Transform to lowercase
        query = query.lower()
        
        cur.execute(query)
        exists = cur.fetchone()[0]

        if not exists:
            if self.can_initialize or can_initialize:
                logger.info('Could not find table for sensor %s, creating it...', sensor.__class__.__name__)
                try:
                    self.initialize_structure_for_DataTimeSlots(cur, sensor)
                except Exception as e:
                    print e
                return True
            else:
                return False
        else:
            return True

            
    def initialize_structure_for_DataTimeSlots(self, cur, sensor):
        
        # Prepare the query for table structure
        labels_list = ' REAL, '.join([fix_label_to_sqlite(label) for label in sensor.Slots_data_labels]) + ' REAL, '
        query = "CREATE TABLE {}_DataTimeSlots(start_ts INTEGER NOT NULL, end_ts INTEGER NOT NULL, sid TEXT NOT NULL, span TEXT NOT NULL, {} coverage REAL, PRIMARY KEY (start_ts, end_ts, sid, span));".format(sensor.__class__.__name__, labels_list)
        
        # Transform to lowecase
        query = query.lower()
        
        # Execute
        logger.info('Query: %s', query)
        cur.execute(query)
        
        # Commit 
        self.conn.commit()


    #--------------------
    #  PUT
    #--------------------    
    def put(self, DataTimeSeries, sensor=None, trustme=False, can_initialize=False):
  
        # If empty return immediately as we cannot make any consideration
        if DataTimeSeries.is_empty():
            return

        # If not sensor is given then abort for now
        if not sensor:
            raise NotImplementedError('Cannot yet store data without a sensor')
            
            # The following is just a stub for an experimental approach. 
            # To implement it we should prepare a table with TEXT fields with csv or similar... or maybe not?
            # in the end the get does not require a sensor type.. and here we create on the fly
            from luna.sensors import Sensor
            class NoSensor(Sensor):
                DataTimePoint
                data_type = DataTimePoint
                data_data_type = DataPoint
                Points_validity_interval = 0
                Point_lables = DataTimeSeries.data.labels 
                Slot_lables  = DataTimeSeries.data.labels 
            sensor =  NoSensor('cbqiy66')

        
        # TODO: DataTimeSeries[0] does not work anymore with the slots
        # TODO: add TimeDataStream.reset() to start over (useful in DataTimeSeries.data.type where only the forst element is checked)
         
        # Check for labels consistency
        if isinstance(DataTimeSeries.data.first, TimePoint):
            if DataTimeSeries.data.labels != sensor.Points_data_labels:
                raise InputException('Inconsistent labels: sensor says "{}", but in the DataTimeSeries I found "{}"'.format(sensor.Points_data_labels, DataTimeSeries.data.labels))
  
        elif isinstance(DataTimeSeries.data.first, TimeSlot):
            if DataTimeSeries.data.labels != sensor.Slots_data_labels:
                raise InputException('Inconsistent labels: sensor says "{}", but in the DataTimeSeries I found "{}"'.format(sensor.Slots_data_labels, DataTimeSeries.data.labels))
        
        else:
            raise InputException('Sorry, I cannot store a DataTimeSeries with data of type "{}"'.format(DataTimeSeries.data.first))

        # For each put there might be different storgae structure 
        storage_structure_checked = False if not trustme else True
        
        # Initialize cursor:
        cur = self.conn.cursor()
        for item in DataTimeSeries:
            
            # With which kind of data are we dealing with?
            if isinstance(item, TimePoint):
                raise NotImplementedError()

            elif isinstance(item, TimeSlot):
                
                if not storage_structure_checked:
                    # Check structure for point of this sensorallowing to create if does not exists
                    if not self.check_structure_for_DataTimeSlots(sensor, can_initialize=can_initialize):
                        raise StorageException('{}: Sorry, the DataTimeSlots structure for the sensor {} is not found and I am not allowed to create it (can_initialize is set to "{}")'.format(self.__class__.__name__, sensor, can_initialize))
                    storage_structure_checked = True

                # UPDATE table SET field='C', field2='Z' WHERE id=3;
                # INSERT INTO table (id, field, field2)
                #        SELECT 3, 'C', 'Z'
                #        WHERE NOT EXISTS (SELECT 1 FROM table WHERE id=3);
                
                # Prepare # for update
                labels_sql_safe = [fix_label_to_sqlite(label) for label in sensor.Slots_data_labels]
                values_sql_safe = [str(value) if value is not None else 'NULL' for value in item.data.values]

                # Prepare for insert
                labels_list = ', '.join(labels_sql_safe)
                values_list = ', '.join(values_sql_safe)
                
                logger.debug("Inserting slot with start=%s, end=%s, lables=%s, values=%s", item.start, item.end, labels_list, values_list)
                
                
                labels_and_values_list = ', '.join(['{}={}'.format(label, values_sql_safe[i]) for i, label in enumerate(labels_sql_safe)])
                    

                logger.debug("Inserting slot with start=%s, end=%s, lables_values=%s", item.start, item.end, labels_and_values_list)

                if item.coverage is None:
                    query_update = "UPDATE {}_DataTimeSlots SET {} WHERE start_ts={} AND end_ts={} AND sid='{}' AND span='{}'".format(sensor.__class__.__name__, labels_and_values_list, item.start.t, item.end.t, sensor.id, item.span)      
                    query_insert = "INSERT INTO {0}_DataTimeSlots (start_ts, end_ts, sid, span, {5}) SELECT {1}, {2},'{3}','{4}',{6} WHERE NOT EXISTS (SELECT 1 FROM {0}_DataTimeSlots WHERE start_ts={1} AND end_ts={2} AND sid={3} AND span={4}) ".format(sensor.__class__.__name__,item.start.t,item.end.t,sensor.id,item.span,labels_list,values_list)

                else:
                    query_update = "UPDATE {}_DataTimeSlots SET {}, coverage={} WHERE start_ts={} AND end_ts={} AND sid='{}' AND span='{}'".format(sensor.__class__.__name__, labels_and_values_list, item.coverage, item.start.t, item.end.t, sensor.id, item.span)      
                    query_insert = "INSERT INTO {0}_DataTimeSlots (start_ts, end_ts, sid, span, {5}, coverage) SELECT {1}, {2},'{3}','{4}',{6},{7} WHERE NOT EXISTS (SELECT 1 FROM {0}_DataTimeSlots WHERE start_ts={1} AND end_ts={2} AND sid='{3}' AND span='{4}') ".format(sensor.__class__.__name__,item.start.t,item.end.t,sensor.id,item.span,labels_list,values_list,item.coverage)
    

                logger.debug('Query update: %s', query_update)
                logger.debug('Query insert: %s', query_insert)
                cur.execute(query_update)
                cur.execute(query_insert)  
    
            else:
                raise InputException('{}: Sorry, data type {} is not support by this storage'.format(self.__class__.__name__, type(item)))
        
        # TODO: move to commit only this transaction and not everything in self.conn
        self.conn.commit()

        return sensor.id


    #--------------------
    #  GET
    #--------------------      
    def get(self, data_id=None, sensor=None, from_dt=None, to_dt=None, timeSlotSpan=None, cached=False, trustme=False, last=False):
        if not data_id and not sensor:
            raise InputException('Please give at least one of data_id and sensor')
        
        if data_id and not sensor:
            raise NotImplementedError('Cannot yet get data without a sensor')
            #sensor =  NoSensor('cbqiy66') <- COuld be an approach?
        
        # is data_id deprecated?
        
        # Load data. from and to are UTC. left included, right excluded, as always.
        
        # Decide if to load Points or Slots 
        if not timeSlotSpan:
            return self._get_DataTimePoints(data_id=data_id, sensor=sensor, from_dt=from_dt, to_dt=to_dt, cached=cached, trustme=trustme, last=last)
        else:
            return self._get_DataTimeSlots(data_id=data_id, sensor=sensor, from_dt=from_dt, to_dt=to_dt, timeSlotSpan=timeSlotSpan, cached=cached, trustme=trustme, last=last)
            

    #---------------------
    # Get DataTimePoints
    #---------------------
    def _get_DataTimePoints(self, data_id=None, sensor=None, from_dt=None, to_dt=None, cached=False, trustme=False, last=False):
        raise NotImplementedError()


    #---------------------
    # Get DataTimeSlots
    #---------------------
    def _get_DataTimeSlots(self, data_id=None, sensor=None, from_dt=None, to_dt=None, timeSlotSpan=None, cached=False, trustme=False, last=False):

        # Initialize cursor
        cur = self.conn.cursor()

        # Check for data structure in the db
        if not trustme:
            if not self.check_structure_for_DataTimeSlots(sensor, can_initialize=False):
                raise StorageException('{}: Sorry, DataTimeSlots the structure for the sensor {} is not found.'.format(self.__class__.__name__, sensor))

# TODO: re-enable cross check!!
#         # Get column names
#         labels = []
#         for i, item in enumerate(cur.execute('PRAGMA table_info({}_DataTimeSlots);'.format(sensor.__class__.__name__))):
#             if i>1:
#                 labels.append(fix_label_from_sqlite(item[1]))
# 
#         # Check that we have every required labels in the storage        
#         for label in sensor.Slots_data_labels:
#             if label.lower() not in labels:
#                 raise ConsistencyException('Sensor label "{}" not found in  {}'.format(label, labels))
 
        labels = sensor.Slots_data_labels
 
        # Get the last point
        if last:
            query  = "SELECT end_ts from {}_DataTimeSlots WHERE sid='{}' AND span='{}' ORDER BY end_ts DESC LIMIT 1".format(sensor.__class__.__name__.lower(), sensor.id, timeSlotSpan)
            cur.execute(query)
            result = cur.fetchone()
            if not result:
                return None
            else:
                return dt_from_s(result[0],tz=sensor.timezone)

        # Prepare the query for the PostgresDataTimeStream 
        if from_dt and to_dt:
            from_s = s_from_dt(from_dt)
            to_s   = s_from_dt(to_dt)
            query  = 'SELECT * from {}_DataTimeSlots WHERE sid="{}" AND span="{}" AND start_ts >= {} and end_ts <= {} ORDER BY start_ts'.format(sensor.__class__.__name__, sensor.id, timeSlotSpan, from_s, to_s)
            query  = query.lower() 
        elif (not from_dt and to_dt) or (from_dt and not to_dt):
            raise InputException('Sorry, please give both from_dt and to_dt or none.')
        else:
            # Select all data
            query = 'SELECT * from {}_DataTimeSlots WHERE sid="{}" AND span="{}" ORDER BY start_ts'.format(sensor.__class__.__name__, sensor.id, timeSlotSpan)
            query  = query.lower() 

        # Create the DataStream
        dataTimeStream = PostgresDataTimeStream(cur=cur, query=query, sensor=sensor, data_type=DataTimeSlot, labels=labels, timeSlotSpan=timeSlotSpan)

        # Create a StreamingDataTimeSeries with the above DataStream
        stramingDataTimeSeries = StreamingDataTimeSeries(dataTimeStream=dataTimeStream, cached=cached)

        return stramingDataTimeSeries















