
from luna.common.exceptions import ConsistencyException

#--------------------------
#    Logger
#--------------------------

import logging
logger = logging.getLogger(__name__)


def compute_coverage(dataTimeSeries, start_dt, end_dt, prev_dataTimePoint, next_dataTimePoint):
    '''Compute the data coverage of a dataTimeSeries based on the points validity_interval.
    
    Args:
        dataTimeSeries(dataTimeSeries): the DataTimeSeries
        start_dt(datetime): start of the coverage calculation
        end_dt(datetime): end of the coverage calculation
        prev_dataTimePoint(dataTimePoint): previous DataTimePoint
        next_dataTimePoint(dataTimePoint): next DataTimePoint
    
    Raises:
        InputException: if some argument is passed in a wrong format
        
    Returns:
        float: float value betweeo 0.0 and 1.0
    '''
  
    logger.info('--------------called compute coverage--------------')




    # Support vars
    prev_set_by_myself      = False
    dataTimePoint_processed = None
    
    prev_valid_until_dt = None
    next_valid_from_dt  = None

    for dataTimePoint in dataTimeSeries:

        if start_dt is None:
            start_dt = dataTimePoint.dt
            
        if end_dt is None:
            end_dt   = dataTimePoint.dt

        print "--------- HARD DEBUG ------------"
        print "dataTimePoint.dt", dataTimePoint.dt
        print "dataTimePoint.validity_region.span", dataTimePoint.validity_region.span
        print "-------------------- ------------"       

        # Handle previous data point validity
        if dataTimePoint.dt < start_dt:
            if not prev_dataTimePoint:
                prev_set_by_myself  = True
                prev_valid_until_dt = dataTimePoint.dt # + span / 2
            else:
                if prev_set_by_myself:
                    prev_valid_until_dt = dataTimePoint.dt # - span / 2
                else:
                    prev_valid_until_dt = start_dt
                    
            continue
        elif dataTimePoint.dt >= start_dt and dataTimePoint.dt < end_dt:
            
            # Process here...
            print 'dataTimePoint', dataTimePoint
            print 'dataTimePoint_processed', dataTimePoint_processed
            print 'prev_valid_until_dt', prev_valid_until_dt
            print 'next_valid_from_dt', prev_valid_until_dt
        
        elif dataTimePoint.dt >= end_dt:
            if not prev_dataTimePoint:
                continue
        else:
            raise ConsistencyException('Internal consistency exception, check Luna source code! ({}, {})'.format(dataTimePoint.dt,start_dt))
        
        found_one = True
    
    # Process the last point
    print 'Done'
    return 1.0




def _compute_missing_coverage(prev_valid_until_dt, current_valid_from_dt, current_valid_until_dt, next_valid_from_dtp):
    return 0








