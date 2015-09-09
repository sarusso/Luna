from luna.datatypes.dimensional import PhysicalDimensionalData, TimePoint
from luna.datatypes.composite import TimeSeries, PhysicalDataTimePoint, PhysicalDataTimeSlot
from luna.storage import Storage
from luna.spacetime.time import s_from_dt
from luna.datatypes.composite import StreamingTimeSeries, DataTimeStream
from luna.common.exceptions import InputException, ConsistencyException
import sqlite3
import os

# Logger
import logging
logger = logging.getLogger(__name__)

LUNA_DIR  = '.luna'
USER_HOME = os.path.expanduser("~")
LUNA_HOME = os.path.join(USER_HOME,LUNA_DIR)


#------------------------------------------------#
#          WARNING: alpha code                   #
#------------------------------------------------#


class SQLiteStorage(Storage):
    def __init__(self, db_file=None):
        
        
        db_path = LUNA_HOME + '/Luna_SQLiteStorage.db'
        
        if not os.path.exists(LUNA_HOME):
            os.makedirs(LUNA_HOME)
        
        logger.debug('Initializing SQLiteStorage with db path = %s', db_path)
        
        # Initiliaze connesciotn
        self.conn = sqlite3.connect(db_path)
        


class SQLiteDataTimeStream(DataTimeStream):

    def __init__(self, query_cur, sensor, type):
        
        self.sensor    = sensor
        self.query_cur = query_cur
        
        if type not in ['Points','Slots']:
            raise InputException('type must be either Points or Slots')
            
        self.type = type
        
    # Iterator
    def __iter__(self):
        return self

    def next(self):
        
        # The following will raise StopIteration for us to stop the iterator
        db_data = self.query_cur.next()
        
        if self.type == 'Points':
            labels = self.sensor.Points_data_labels
        
        elif self.type == 'Slots':
            labels = self.sensor.Slots_data_labels 
        else:
            raise ConsistencyException('Got unknown type: {}'.format(self.type))

        # We will have to instantiate the TimePoint from the db data.

        # Note:
        # self.sensor.data_type      = PhysicalDataTimePoint
        # self.sensor.data_data_type = PhysicalDimensionalData
        
        data = self.sensor.data_data_type(labels=labels, values = db_data[2:])
        DataTime_Point_or_Slot = self.sensor.data_type(t=db_data[0], tz = "Europe/Rome", data=data, validity_interval=self.sensor.Points_validity_interval)
        
        # This get when a validty of a Point ends. For TimeSlots and seconds, it is a bit of overhead
        #_ = DataTime_Point_or_Slot.validity_interval.duration_s()
        
        return DataTime_Point_or_Slot       
    

class TimeSeriesSQLiteStorage(SQLiteStorage):
    
    def put(self, timeSeries, sensor, timeSlotType=None):
  
        if not timeSlotType:
 
            # Check if right table exists:
            cur = self.conn.cursor()    
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(sensor.__class__.__name__))
            if not cur.fetchone():
                logger.debug('Could not find table for thing %s, creating it...', sensor.__class__.__name__)
                # Create the table
                cur.execute("CREATE TABLE {}(ts INTEGER NOT NULL, sid TEXT NOT NULL, flowrate_lm_i REAL, PRIMARY KEY (ts, sid));".format(sensor.__class__.__name__))              
    
            for item in timeSeries:
                # TODO: the following raises a bug
                #print item.data.data
                logger.debug("Inserting %s, %s", item.t, item.data.values[0])
                cur.execute("INSERT OR REPLACE INTO {} (ts, sid, flowrate_lm_i) VALUES ({},'{}',{})".format(sensor.__class__.__name__, item.t, sensor.id,  item.data.values[0]))       
            
            self.conn.commit()
        else:
            raise NotImplementedError('Not yet Slots')
            # TimeSlotType!!!!!!!
            # Is the Timeslot deducible form the TimeSereis? SHould be..  
    
    def get(self, sensor,  from_dt, to_dt, timeSlotType=None):
        
        # Load data. froma nd to are UTC. left included, right excluded, as always.
        
        from_s = s_from_dt(from_dt)
        to_s   = s_from_dt(to_dt)
        
        cur = self.conn.cursor()
        
        if not timeSlotType:
            
            # Use the iterator of SQLite (streming)
            query_cur = cur.execute('SELECT * from {} where sid="{}" and ts >= {} and ts < {}'.format(sensor.__class__.__name__, sensor.id, from_s, to_s))
    
            # Create the DataStream
            dataTimeStream = SQLiteDataTimeStream(query_cur=query_cur, sensor=sensor, type='Points')
    
            # Create a StreamingTimeSeries with the above DataStream
            stramingTimeSeries = StreamingTimeSeries(dataTimeStream=dataTimeStream)

        else:
            raise NotImplementedError('Not yet Slots')
            # TimeSlotType!!!!!!!
            # Use print sensor.type_ID


        
        return stramingTimeSeries

















