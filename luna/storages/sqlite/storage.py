from luna.datatypes.dimensional import PhysicalData, TimePoint, TimeSlot
from luna.datatypes.dimensional import DataTimeSeries, PhysicalDataTimePoint, PhysicalDataTimeSlot, DataTimePoint, DataPoint, DataTimeSlot
from luna.datatypes.dimensional import DataTimeSeries as DataTimePointSeries
from luna.storages import Storage
from luna.spacetime.time import s_from_dt, dt_from_s, timezonize, TimeSlotSpan
from luna.datatypes.dimensional import StreamingDataTimeSeries, DataTimeStream
from luna.common.exceptions import InputException, ConsistencyException, StorageException
import sqlite3
import os
import math
import json
 

# Logger
import logging
logger = logging.getLogger(__name__)

LUNA_DIR  = '.luna'
USER_HOME = os.path.expanduser("~")
LUNA_HOME = os.path.join(USER_HOME,LUNA_DIR)

#=========================
# Utility functions
#=========================

def trunc(invalue, digits):
    return int(invalue*math.pow(10,digits))/math.pow(10,digits);
    
def fix_label_from_sqlite(label):
    return label.replace('__','-')

def fix_label_to_sqlite(label):
    return label.replace('-','__').lower()

def sqlvalue(value):
    if value is None:
        return 'NULL'
    elif value in [True,False]:
        return '{}'.format(str(value).upper())
    else:
        return '\'{}\''.format(value)  


#=----------------------------------------------=#
#          WARNING: alpha code                   #
#=----------------------------------------------=#

# TODO: naming?
# SQLiteDataTimeStream -> SQLiteDataStream
# DataTimeSeriesSQLiteStorage -> SQLiteStorage


#=========================
#  Data stream
#=========================
class SQLiteDataTimeStream(DataTimeStream):
    ''' Data time stream implementation in SQLite'''
     
    def __init__(self, cur, query, id, labels=None, truncate=None, timeSpan=None, tz=None):
               
        # Save id
        self.id = id
        
        # Set values
        self.cur       = cur        
        self.query     = query
        self.query_cur = None
        self.truncate  = truncate
        self.tz        = tz
        self.labels    = None
        self.src_hits  = 0
        self.timeSpan  = timeSpan

        # TODO: Call parent init, use kwargs, pop var names, etc.
        #super(SQLiteDataTimeStream, self).__init__(*args, **kwargs)
        
        
    # Iterator
    def __iter__(self):
        self.query_cur = self.cur.execute(self.query)
        self.src_hits += 1
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

            # Log
            #logger.debug(db_data)
            # (1436021994, None, 1436021994.0, 1436021994.0, u'328or6c269', u'{"temperature_C": [20.0]}', None, u'FALSE')
            #logger.debug(db_data[5])
            DataTime_Point_or_Slot = None
        
            # Hanlde the case of the Points
            if not self.timeSpan:
                
                # Init data
                data = json.loads(db_data[5])

                # Create object                
                DataTime_Point_or_Slot = DataTimePoint(t                    = db_data[0],
                                                       tz                   = self.tz,
                                                       data                 = data,
                                                       validity_region      = None) #TimeSlot/TimeSlotSpan

            # Handle the case of the Slots
            else:
                
                # Init data
                data = json.loads(db_data[5])
   
                DataTime_Point_or_Slot = DataTimeSlot(start    = TimePoint(t=db_data[0], tz = self.tz),
                                                      end      = TimePoint(t=db_data[1], tz = self.tz),
                                                      span     = self.timeSpan,
                                                      data     = data,
                                                      coverage = db_data[6])
  
            # This get when a validty of a Point ends. For TimeSlots and seconds, it is a bit of overhead
            #_ = DataTime_Point_or_Slot.validity_interval.duration_s()
            if DataTime_Point_or_Slot is None:
                raise StopIteration()
            return DataTime_Point_or_Slot     

    # Python 2.x
    def next(self):
        return self.__next__()
    
    def get_statistics(self):
        return {'src_hits': self.src_hits}




#=========================
#  Main storage
#=========================

class SQLiteStorage(Storage):
    def __init__(self, db_file=None, in_memory=False, can_initialize=False):
        
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
            
            logger.debug('Initializing SQLiteStorage with DB path = %s', db_path)
            
        # Initiliaze connection
        self.conn = sqlite3.connect(db_path)
        
        # Right to initialize
        self.can_initialize = can_initialize


    #--------------------
    # Structure
    #--------------------

    def check_structure_for_DataTimePoints(self, can_initialize=None):
        '''Check that the structure of the storage exists for a given sensor'''     
        # Check if right table exists:
        cur = self.conn.cursor()    
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DataTimePoints';")
        if not cur.fetchone():
            if (self.can_initialize and can_initialize==None) or can_initialize:
                logger.debug('Could not find table for DataTimePoints, creating it...')
                self.initialize_structure_for_DataTimePoints(cur)
                return True
            else:
                return False
        else:
            return True
            
    def initialize_structure_for_DataTimePoints(self, cur):
        # Create the table
        query = ("CREATE TABLE DataTimePoints("
                 "t INTEGER NOT NULL,"
                 "validity_span TEXT,"
                 "validity_start_t REAL NOT NULL,"
                 "validity_end_t REAL NOT NULL,"
                 "id TEXT NOT NULL,"
                 "data TEXT,"
                 "extra TEXT,"
                 "hf BOOL,"
                 "PRIMARY KEY (t, validity_start_t, validity_end_t, id));") 
        logger.debug('Query: %s', query)
        cur.execute(query)                

    def check_structure_for_DataTimeSlots(self, can_initialize=None):
        '''Check that the structure of the storage exists for a given sensor'''
        # Check if right table exists:
        cur = self.conn.cursor()    
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DataTimeSlots';")
        if not cur.fetchone():
            if (self.can_initialize and can_initialize==None) or can_initialize:
                logger.debug('Could not find table for DataTimeSlots, creating it...')
                self.initialize_structure_for_DataTimeSlots(cur)
                return True
            else:
                return False
        else:
            return True
            
    def initialize_structure_for_DataTimeSlots(self, cur):
        # Create the table
        query = ("CREATE TABLE DataTimeSlots("
                 "start_t REAL NOT NULL,"
                 "end_t REAL NOT NULL,"
                 "span TEXT NOT NULL,"
                 "tz TEXT NOT NULL,"
                 "id TEXT NOT NULL,"
                 "data TEXT,"
                 "coverage REAL,"
                 "extra TEXT,"
                 "hf BOOL,"
                 "PRIMARY KEY (start_t, end_t, span, tz, id)"
                 ");")
        logger.debug('Query: %s', query)
        cur.execute(query)              


    #--------------------
    #  PUT
    #--------------------    
    def put(self, what, id, trustme=False, can_initialize=None):
  
        # Do we know what to add?
        if isinstance(what.data.first, TimePoint):
            logger.debug('Putting DataTimePointSeries')

        elif isinstance(what.data.first, TimeSlot):
            logger.debug('Putting DataTimeSlotSeries')
                
        else:
            raise InputException('Sorry, I cannot store a DataTimeSeries with data of type "{}"'.format(what.data.first))

        # For each put there might be different storgae structure 
        storage_structure_checked = False if not trustme else True
        
        # Initialize cursor:
        cur = self.conn.cursor()
        for item in what:
            
            # With which kind of data are we dealing with?
            if isinstance(item, TimePoint):
                 
                if not storage_structure_checked:
                    # Check structure for point of this sensorallowing to create if does not exists
                    if not self.check_structure_for_DataTimePoints(can_initialize=can_initialize):
                        raise StorageException('{}: Sorry, the DataTimePoints structure for DataTimePoints is not found and I am not allowed to create it (can_initialize is set to "{}")'.format(self.__class__.__name__, can_initialize))
                    storage_structure_checked = True
                
                # Insert
                logger.debug("Inserting DataTimePoint with t=%s, data=%s, extra=%s", item.t, item.data, None)
                
                query = ("INSERT OR REPLACE INTO DataTimePoints(t, validity_span, validity_start_t, validity_end_t, id, data, extra, hf) "
                        "VALUES ({},{},{},{},'{}','{}',{},'{}')").format(float(item.t), sqlvalue(None), float(item.t), float(item.t), id, json.dumps(item.data), sqlvalue(None), sqlvalue(False))
                logger.debug('Query: %s', query)
                cur.execute(query)       

            elif isinstance(item, TimeSlot):
                
                if not storage_structure_checked:
                    # Check structure for point of this sensorallowing to create if does not exists
                    if not self.check_structure_for_DataTimeSlots(can_initialize=can_initialize):
                        raise StorageException('{}: Sorry, the DataTimeSlots structure for the DataTimeSlots is not found and I am not allowed to create it (can_initialize is set to "{}")'.format(self.__class__.__name__, can_initialize))
                    storage_structure_checked = True
                
                # Log
                #logger.debug(item)
                #logger.debug(item.start)
                #logger.debug(item.end)
                #logger.debug(item.span)
                #logger.debug(item.tz)
                #logger.debug(item.coverage)
                
                # Handle timezone
                if item.span.is_logical():
                    tz = item.tz
                else:
                    tz = 'UTC'
                 
                query = ("INSERT OR REPLACE INTO DataTimeSlots(start_t, end_t, span, tz, id, data, coverage, extra, hf) "
                         "VALUES ({},{},'{}','{}','{}','{}',{},{},'{}')").format(float(item.start.t), float(item.end.t), item.span, str(tz), id, json.dumps(item.data), sqlvalue(item.coverage), sqlvalue(None), sqlvalue(False))
                logger.debug('Query: %s', query)
                cur.execute(query)                                  

            else:
                raise InputException('{}: Sorry, data type {} is not support by this storage'.format(self.__class__.__name__, type(item)))
        
        # TODO: move to commit only this transaction and not everything in self.conn
        self.conn.commit()


    #--------------------
    #  GET
    #--------------------      
    def get(self, id=None, from_t=None, to_t=None, from_dt=None, to_dt=None, timeSpan=None, cached=False, trustme=False, last=False, tz=None):

        # Set UTC if no timezone
        if not tz:
            tz='UTC'

        # Sanity check on id
        if not id:
            raise InputException('Please give me an id.')

        # Sanity checks on from_t and from_dt
        if from_t and from_dt:
            raise InputException('Got both from_t and from_dt, please choose one.')
        if from_dt:
            from_t = s_from_dt(from_dt)
        if from_t and not from_dt:  
            try:
                from_t = float(from_t)
            except:
                raise InputException('Argument "from_t" is not int or float (got type "{}" with value "{}").'.format(from_t.__class__.__name__,from_t))
            
        # Sanity checks on to_t and to_dt
        if to_t and to_dt:
            raise InputException('Got both from_t and from_dt, please choose one.')
        if to_dt:
            from_t = s_from_dt(from_dt) 
        if to_t and not to_dt:    
            try:
                to_t = float(to_t)
            except:
                raise InputException('Argument "to_t" is not int or float (got type "{}" with value "{}").'.format(to_t.__class__.__name__,to_t))

        # Load data from Points or Slots. From_t and to_t are UTC epoch seconds float. Left included, right excluded, as always.
        if not timeSpan:
            return self._get_DataTimePoints(id=id, from_t=from_t, to_t=to_t, cached=cached, trustme=trustme, last=last, tz=tz)
        else:
            return self._get_DataTimeSlots(id=id, from_t=from_t, to_t=to_t, timeSpan=timeSpan, cached=cached, trustme=trustme, last=last, tz=tz)
            

    #---------------------
    # Get DataTimePoints
    #---------------------
    def _get_DataTimePoints(self, id=None, from_t=None, to_t=None, cached=False, trustme=False, last=False, tz=None):

        if last:
            raise NotImplementedError('Not yet')

        # Handle timezone
        if tz is None:
            tz=timezonize('UTC')
        else:
            tz=timezonize(tz)

        # Initialize cursor
        cur = self.conn.cursor()

        # Check for data structure in the db
        if not trustme:
            if not self.check_structure_for_DataTimePoints(can_initialize=False):
                raise StorageException('{}: Sorry, DataTimePoints structure not found.')

        # Use the iterator of SQLite (streming)
        if from_t and to_t:
            query  = 'SELECT * from DataTimePoints WHERE id="{}" AND validity_start_t >= {} AND validity_end_t < {} ORDER BY t'.format(id, from_t, to_t)
        elif (not from_t and to_t) or (from_t and not to_t):
            raise InputException('Sorry, please give both from_dt and to_dt or none.')
        else:
            # Select all data
            query = 'SELECT * FROM DataTimePoints WHERE id="{}" ORDER BY t'.format( id)

        # Create the DataStream
        dataTimeStream = SQLiteDataTimeStream(cur=cur, query=query, id=id, tz=tz)

        # Create a StreamingDataTimeSeries with the above DataStream
        stramingDataTimeSeries = StreamingDataTimeSeries(dataTimeStream=dataTimeStream, cached=cached)

        return stramingDataTimeSeries


    #---------------------
    # Get DataTimeSlots
    #---------------------
    def _get_DataTimeSlots(self, id=None, from_t=None, to_t=None, timeSpan=None, cached=False, trustme=False, last=False, tz=None):

        if last:
            raise NotImplementedError('Not yet')

        # timeSpan To object
        timeSpan  = TimeSlotSpan(timeSpan)
        
        # Handle query timezone
        if timeSpan.is_logical():
            if not tz:
                raise InputException('Sorry, cannot get DatTimeSlots with a logical span and no explicitly timezone set')
            else:
                # Set query timezone equal to the one asked by the user
                qtz = tz
        else:
            # Set query timezone to UTC
            qtz = 'UTC'

        # tz and qtz to objects
        tz = timezonize(tz)
        qtz = timezonize(qtz)

        # Initialize cursor
        cur = self.conn.cursor()

        # Check for data structure in the db
        if not trustme:
            if not self.check_structure_for_DataTimeSlots(can_initialize=False):
                raise StorageException('{}: Sorry, DataTimeSlots structure not found.')

        # Prepare the query for the SQLiteDataTimeStream 
        if from_t and to_t:
            query  = 'SELECT * from DataTimeSlots WHERE id="{}" AND span="{}" AND start_t >= {} and end_t <= {} and tz="{}" ORDER BY start_t'.format(id, timeSpan, from_t, to_t, qtz)
        elif (not from_t and to_t) or (from_t and not to_t):
            raise InputException('Sorry, please give both from_dt and to_dt or none.')
        else:
            # Select all data
            query = 'SELECT * from DataTimeSlots WHERE id="{}" AND span="{}" and tz="{}" ORDER BY start_t'.format(id, timeSpan, qtz)

        # Create the DataStream
        dataTimeStream = SQLiteDataTimeStream(cur=cur, query=query, id=id, timeSpan=timeSpan, tz=tz)
        
        # Create a StreamingDataTimeSeries with the above DataStream
        stramingDataTimeSeries = StreamingDataTimeSeries(dataTimeStream=dataTimeStream, cached=cached)

        return stramingDataTimeSeries

