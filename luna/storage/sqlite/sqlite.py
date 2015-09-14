from luna.datatypes.dimensional import PhysicalDimensionalData, TimePoint, TimeSlot
from luna.datatypes.composite import TimeSeries, PhysicalDataTimePoint, PhysicalDataTimeSlot, DataTimePoint, DataPoint, DataTimeSlot
from luna.storage import Storage
from luna.spacetime.time import s_from_dt
from luna.datatypes.composite import StreamingTimeSeries, DataTimeStream
from luna.common.exceptions import InputException, ConsistencyException, StorageException
import sqlite3
import os
import math

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
    


#------------------------------------------------#
#          WARNING: alpha code                   #
#------------------------------------------------#


# SQLiteDataTimeStream -> SQLiteDataStream
# TimeSeriesSQLiteStorage -> SQLiteStorage





#-------------------------
# Data stream
#-------------------------

class SQLiteDataTimeStream(DataTimeStream):
    ''' Data time stream implementation in SQLite'''
     
    def __init__(self, query_cur, sensor, type, labels=None, truncate=None):
        
        self.sensor    = sensor
        self.query_cur = query_cur
        
        if type not in ['Points','Slots']:
            raise InputException('type must be either Points or Slots')
            
        self.type = type
        self.truncate = truncate
        self.labels = labels
        
    # Iterator
    def __iter__(self):
        return self

    def __next__(self):
        
        # The following will raise StopIteration for us to stop the iterator
        db_data = self.query_cur.next()
        
        force_sensors_names = False
        
        if not self.labels:
            if self.type == 'Points':
                self.labels = self.sensor.Points_data_labels  
            elif self.type == 'Slots':
                self.labels = self.sensor.Slots_data_labels 
            else:
                raise ConsistencyException('Got unknown type: {}'.format(self.type))


        # We will have to instantiate the TimePoint from the db data.

        # Note:
        # self.sensor.data_type      = PhysicalDataTimePoint
        # self.sensor.data_data_type = PhysicalDimensionalData

        if self.type == 'Points':
            values = list(db_data[2:])
            data = self.sensor.data_data_type(labels=self.labels, values = values)
            DataTime_Point_or_Slot = self.sensor.data_type(t=db_data[0], tz = "Europe/Rome", data=data) #TODO: validity_interval=self.sensor.Points_validity_interval)

        elif self.type == 'Slots':
            values = list(db_data[4:])
            
            data = self.sensor.data_data_type(labels=self.labels, values = values)
            DataTime_Point_or_Slot = self.sensor.data_slot_type(start = TimePoint(t=db_data[0], tz = "Europe/Rome"),
                                                                end   = TimePoint(t=db_data[1], tz = "Europe/Rome"),
                                                                data=data, ) # TODO: add type=SlotType(type_shprtname_from_db)
            
        # This get when a validty of a Point ends. For TimeSlots and seconds, it is a bit of overhead
        #_ = DataTime_Point_or_Slot.validity_interval.duration_s()

        return DataTime_Point_or_Slot     

    # Python 2.x
    def next(self):
        return self.__next__()

#-------------------------
# Main storage class
#-------------------------

class SQLiteStorage(Storage):
    def __init__(self, db_file=None, in_memory=False, right_to_initialize=False):
        
        if in_memory:
            db_path = ':memory:'
            logger.debug('Initializing SQLiteStorage with in memory db')
        else:
            if db_file:
                db_path = db_file
            else:
                db_path = LUNA_HOME + '/Luna_SQLiteStorage.db'
            
            if not os.path.exists(LUNA_HOME):
                os.makedirs(LUNA_HOME)
            
            logger.debug('Initializing SQLiteStorage with db path = %s', db_path)
            
        # Initiliaze connection
        self.conn = sqlite3.connect(db_path)
        
        # Right to initialize
        self.right_to_initialize = right_to_initialize


#-------------------------
# Time 
#-------------------------

class TimeSeriesSQLiteStorage(SQLiteStorage):


    #--------------------
    # STRUCTURE
    #--------------------

    def check_structure_for_DataTimePoints(self, sensor, right_to_initialize=False):
        '''Check that the structure of the storage exists for a given sensor'''
        
        # Check if right table exists:
        cur = self.conn.cursor()    
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}_DataTimePoints';".format(sensor.__class__.__name__))
        if not cur.fetchone():
            if self.right_to_initialize or right_to_initialize:
                logger.debug('Could not find table for thing %s, creating it...', sensor.__class__.__name__)
                self.initialize_structure_for_DataTimePoints(cur, sensor)
                return True
            else:
                return False
        else:
            return True
            
    def initialize_structure_for_DataTimePoints(self, cur, sensor):
        # Create the table
        cur.execute("CREATE TABLE {}_DataTimePoints(ts INTEGER NOT NULL, sid TEXT NOT NULL, flowrate_m3s REAL, PRIMARY KEY (ts, sid));".format(sensor.__class__.__name__))              


    def check_structure_for_DataTimeSlots(self, sensor, right_to_initialize=False):
        '''Check that the structure of the storage exists for a given sensor'''
        logger.debug('Checking structure with right_to_initialize=%s', right_to_initialize)
        # Check if right table exists:
        cur = self.conn.cursor()    
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}_DataTimeSlots';".format(sensor.__class__.__name__))
        if not cur.fetchone():
            if self.right_to_initialize or right_to_initialize:
                logger.debug('Could not find table for thing %s, creating it...', sensor.__class__.__name__)
                self.initialize_structure_for_DataTimeSlots(cur, sensor)
                return True
            else:
                return False
        else:
            return True
            
    def initialize_structure_for_DataTimeSlots(self, cur, sensor):
        labels_list = ' REAL, '.join(sensor.Slots_data_labels) + ' REAL, '
        cur.execute("CREATE TABLE {}_DataTimeSlots(start_ts INTEGER NOT NULL, end_ts INTEGER NOT NULL, sid TEXT NOT NULL, type TEXT NOT NULL, {} PRIMARY KEY (start_ts, end_ts, sid, type));".format(sensor.__class__.__name__, labels_list))              


    #--------------------
    #  PUT
    #--------------------    
    def put(self, timeSeries, sensor=None, trustme=False, right_to_initialize=False):
  
        # If empty return immediately as we cannot make any consideration
        if timeSeries.is_empty():
            return

        # If not sensor is given then abort for now
        if not sensor:
            raise NotImplementedError('Cannot yet store data without a sensor')
            
            # The following is just a stub an experimental approach. 
            # To implement it we should prepare a table with TEXT fields with csv or similar... or maybe not?
            # in the end the get does not require a sensor type.. and here we create on the fly
            from luna.sensors import Sensor
            class NoSensor(Sensor):
                DataTimePoint
                data_type = DataTimePoint
                data_data_type = DataPoint
                Points_validity_interval = 0
                Point_lables = timeSeries.data.labels 
                Slot_lables  = timeSeries.data.labels 
            sensor =  NoSensor('cbqiy66')

        
        # TODO: timeSeries[0] does not work anymore with the slots
        # TODO: add TimeDataStream.reset() to start over (useful in timeSeries.data.type where only the forst element is checked)
         
        # Check for labels consistency
        if isinstance(timeSeries.data.first, TimePoint):
            if timeSeries.data.labels != sensor.Points_data_labels:
                raise InputException('Inconsistent labels: sensor says "{}", but in the TimeSeries I found "{}"'.format(sensor.Points_data_labels, timeSeries.data.labels))
  
        elif isinstance(timeSeries.data.first, TimeSlot):
            if timeSeries.data.labels != sensor.Slots_data_labels:
                raise InputException('Inconsistent labels: sensor says "{}", but in the TimeSeries I found "{}"'.format(sensor.Slots_data_labels, timeSeries.data.labels))
        
        else:
            raise InputException('Sorry, I cannot store a TimeSeries with data of type "{}"'.format(timeSeries.data.first))

        # For each put there might be different storgae structure 
        storage_structure_checked = False if not trustme else True
        
        # Initialize cursor:
        cur = self.conn.cursor()
        for item in timeSeries:
            
            # With which kind of data are we dealing with?
            if isinstance(item, TimePoint):
                 
                if not storage_structure_checked:
                    # Check structure for point of this sensorallowing to create if does not exists
                    if not self.check_structure_for_DataTimePoints(sensor, right_to_initialize=right_to_initialize):
                        raise StorageException('{}: Sorry, the DataTimePoints structure for the sensor {} is not found and I am not allowed to create it (right_to_initialize is set to "{}")'.format(self.__class__.__name__, sensor, right_to_initialize))
                    storage_structure_checked = True
                
                logger.debug("Inserting point with t=%s, %s", item.t, item.data.values[0])
                cur.execute("INSERT OR REPLACE INTO {}_DataTimePoints(ts, sid, flowrate_m3s) VALUES ({},'{}',{})".format(sensor.__class__.__name__, item.t, sensor.id,  item.data.values[0]))       

            elif isinstance(item, TimeSlot):
                
                if not storage_structure_checked:
                    # Check structure for point of this sensorallowing to create if does not exists
                    if not self.check_structure_for_DataTimeSlots(sensor, right_to_initialize=right_to_initialize):
                        raise StorageException('{}: Sorry, the DataTimeSlots structure for the sensor {} is not found and I am not allowed to create it (right_to_initialize is set to "{}")'.format(self.__class__.__name__, sensor, right_to_initialize))
                    storage_structure_checked = True
                
                logger.debug("Inserting slot with start=%s, end=%s, %s", item.start, item.end, item.data.values[0])
                labels_list = ', '.join(sensor.Slots_data_labels)
                values_list = ', '.join([str(value) for value in item.data.values])
                cur.execute("INSERT OR REPLACE INTO {}_DataTimeSlots(start_ts, end_ts, sid, type, {}) VALUES ({}, {},'{}','{}',{})".format(sensor.__class__.__name__, labels_list, item.start.t, item.end.t, sensor.id, item.type.name, values_list))       
                
            else:
                raise InputException('{}: Sorry, data type {} is not support by this storage'.format(self.__class__.__name__, type(item)))
        
        # TODO: move to commit only this transaction and not everything in self.conn
        self.conn.commit()

        return sensor.id


    #--------------------
    #  GET
    #--------------------      
    def get(self, data_id=None, sensor=None, from_dt=None, to_dt=None, timeSlotType=None, cached=False, trustme=False):
        
        if not data_id and not sensor:
            raise InputException('Please give at least one of data_id and sensor')
        
        if data_id and not sensor:
            raise NotImplementedError('Cannot yet get data without a sensor')
            #sensor =  NoSensor('cbqiy66')
        
        # Load data. from and to are UTC. left included, right excluded, as always.
        
        # Decide if to load Points or Slots 
        if not timeSlotType:
            return self._get_DataTimePoints(data_id=data_id, sensor=sensor, from_dt=from_dt, to_dt=to_dt, timeSlotType=timeSlotType, cached=cached, trustme=trustme)
        else:
            return self._get_DataTimeSlots(data_id=data_id, sensor=sensor, from_dt=from_dt, to_dt=to_dt, timeSlotType=timeSlotType, cached=cached, trustme=trustme)
            

    #---------------------
    # Get DataTimePoints
    #---------------------
    def _get_DataTimePoints(self, data_id=None, sensor=None, from_dt=None, to_dt=None, timeSlotType=None, cached=False, trustme=False):

        # Initialize cursor
        cur = self.conn.cursor()

        # Check for data structure in the db
        if not trustme:
            if not self.check_structure_for_DataTimePoints(sensor, right_to_initialize=False):
                raise StorageException('{}: Sorry, the DataTimePoints structure for the sensor {} is not found.'.format(self.__class__.__name__, sensor))

        # Get column names
        labels = []
        for i, item in enumerate(cur.execute('PRAGMA table_info({});'.format(sensor.__class__.__name__))):
            if i>1:
                labels.append(item[1])
     
        # Use the iterator of SQLite (streming)
        if from_dt and to_dt:
            from_s = s_from_dt(from_dt)
            to_s   = s_from_dt(to_dt)
            query_cur = cur.execute('SELECT * from {}_DataTimePoints where sid="{}" and ts >= {} and ts < {}'.format(sensor.__class__.__name__, sensor.id, from_s, to_s))
        elif (not from_dt and to_dt) or (from_dt and not to_dt):
            raise InputException('Sorry, please give both from_dt and to_dt or none.')
        else:
            # Select all data
            query_cur = cur.execute('SELECT * from {}_DataTimePoints where sid="{}"'.format(sensor.__class__.__name__, sensor.id))

        # Create the DataStream
        dataTimeStream = SQLiteDataTimeStream(query_cur=query_cur, sensor=sensor, type='Points', labels=labels)

        # Create a StreamingTimeSeries with the above DataStream
        stramingTimeSeries = StreamingTimeSeries(dataTimeStream=dataTimeStream, cached=cached)

        return stramingTimeSeries


    #---------------------
    # Get DataTimeSlots
    #---------------------
    def _get_DataTimeSlots(self, data_id=None, sensor=None, from_dt=None, to_dt=None, timeSlotType=None, cached=False, trustme=False):

        # Initialize cursor
        cur = self.conn.cursor()

        # Check for data structure in the db
        if not trustme:
            if not self.check_structure_for_DataTimeSlots(sensor, right_to_initialize=False):
                raise StorageException('{}: Sorry, DataTimeSlots the structure for the sensor {} is not found.'.format(self.__class__.__name__, sensor))

        # Get column names
        labels = []
        for i, item in enumerate(cur.execute('PRAGMA table_info({});'.format(sensor.__class__.__name__))):
            if i>1:
                labels.append(item[1])
     
        # Use the iterator of SQLite (streming)
        if from_dt and to_dt:
            from_s = s_from_dt(from_dt)
            to_s   = s_from_dt(to_dt)
            query_cur = cur.execute('SELECT * from {}_DataTimeSlots where sid="{}" and type="{}" and start_ts >= {} and end_ts <= {}'.format(sensor.__class__.__name__, sensor.id, timeSlotType.name, from_s, to_s))
        elif (not from_dt and to_dt) or (from_dt and not to_dt):
            raise InputException('Sorry, please give both from_dt and to_dt or none.')
        else:
            # Select all data
            query_cur = cur.execute('SELECT * from {}_DataTimeSlots where sid="{}" and type="{}"'.format(sensor.__class__.__name__, sensor.id, timeSlotType.name))

        # Create the DataStream
        dataTimeStream = SQLiteDataTimeStream(query_cur=query_cur, sensor=sensor, type='Slots', labels=labels)

        # Create a StreamingTimeSeries with the above DataStream
        stramingTimeSeries = StreamingTimeSeries(dataTimeStream=dataTimeStream, cached=cached)

        return stramingTimeSeries















