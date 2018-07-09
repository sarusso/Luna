from luna.datatypes.dimensional import PhysicalData, TimePoint, TimeSlot
from luna.datatypes.dimensional import DataTimeSeries, PhysicalDataTimePoint, PhysicalDataTimeSlot, DataTimePoint, DataPoint, DataTimeSlot
from luna.storages import Storage
from luna.spacetime.time import s_from_dt, dt_from_s
from luna.datatypes.dimensional import StreamingDataTimeSeries, DataTimeStream
from luna.common.exceptions import InputException, ConsistencyException, StorageException
import sqlite3
import os
import math
from collections import namedtuple
import psycopg2
import psycopg2.extras

from luna.storages.sqlite.storage import SQLiteStorage


# Logger
import logging
logger = logging.getLogger(__name__)

LUNA_DIR  = '.luna'
USER_HOME = os.path.expanduser("~")
LUNA_HOME = os.path.join(USER_HOME,LUNA_DIR)


#-------------------------
# Main storage class
#-------------------------

class PostgresStorage(SQLiteStorage):
    
    def check_table_exists_query(self, table):
        # Check if table exists:
        query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}' );".format(self.schema, table) 
        return query

    class Connection(object):
        
        # Try-except everything here based on http://initd.org/psycopg/docs/module.html#psycopg2.Error
        
        def __init__(self,conn_string, db_pass):
            
            # Set conn string
            self.conn_string = conn_string
            
            # Log
            logger.info("Initializing connection wrapper to: {0}".format(self.conn_string.replace(db_pass, '******')))
            
            # Connect
            self._connect()
        
        def _reconnect(self):
            logger.info('Re-connecting')
            self._connect()
        
        def _connect(self):
            self.wrapped_conn = psycopg2.connect(self.conn_string)
            
        def cursor(self):
            
            try:
                return self.wrapped_conn.cursor()
            except Exception as e:
                logger.error('Connection wrapper error on cursor: "{}"'.format(e))
                conn_closed = self.wrapped_conn.closed
                if conn_closed:
                    logger.info('Will reconnect as closed="{}"'.format(conn_closed))
                    self._reconnect()

        def rollback(self):
            try:
                return self.wrapped_conn.rollback()        
            except Exception as e:
                logger.error('Connection wrapper error on rollback: "{}"'.format(e))
                conn_closed = self.wrapped_conn.closed
                if conn_closed:
                    logger.info('Will reconnect as closed="{}"'.format(conn_closed))
                    self._reconnect()
                
        def commit(self):
            try:
                return self.wrapped_conn.commit()  
            except Exception as e:
                logger.error('Connection wrapper error on commit: "{}"'.format(e))
                conn_closed = self.wrapped_conn.closed
                if conn_closed:
                    logger.info('Will reconnect as closed="{}"'.format(conn_closed))
                    self._reconnect()

    def __init__(self, can_initialize=False, host=None, port=None, db_name=None, db_user=None, db_pass=None):

        conn_string = "host='{0}' port='{1}' dbname='{2}' user='{3}' password='{4}'".format(host, port, db_name, db_user, db_pass)
        
        # Get a connection, if a connect cannot be made an exception will be raised here
        self.conn = self.Connection(conn_string, db_pass)
      
        # Named tuples cursor
        #self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
         
        # Dict tuples cursor
        #self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        self.schema = 'public'
 
        # Right to initialize
        self.can_initialize = can_initialize

        # Set Type
        self.TYPE='Postgres'

