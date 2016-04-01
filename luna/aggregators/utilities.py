
from luna.common.exceptions import ConsistencyException
from luna.spacetime.time import s_from_dt

#--------------------------
#    Logger
#--------------------------

import logging
logger = logging.getLogger(__name__)


# OLD approach:
#def compute_coverage(dataTimeSeries, start_dt, end_dt, prev_dataTimePoint, next_dataTimePoint):
#        prev_dataTimePoint(dataTimePoint): previous DataTimePoint
#        next_dataTimePoint(dataTimePoint): next DataTimePoint


def compute_1D_coverage(dataSeries, start_Point, end_Point):
    '''Compute the data coverage of a 1-dimensional dataSeries based on the points validity_region.
    The computation is done in a streaming fashion so it scales.
    
    Args:
        dataSeries(dataSeries): the DataSeries
        start_Point(Point): start Point for the coverage calculation
        end_Point(Point): end Point for the coverage calculation

    Raises:
        InputException: if some argument is passed in a wrong format
        
    Returns:
        float: float value between 0.0 and 1.0
    '''
  
  
    if start_Point is None or end_Point is None:
        raise NotImplementedError('Sorry, you must set start/end for now.')
  
    logger.debug('--------------called compute coverage--------------')


    # Support vars
    prev_dataPoint_valid_until = None
    missing_coverage = None
    
    print '-> start_Point', start_Point
    
    for this_dataPoint in dataSeries:


        print 'this_dataPoint', this_dataPoint

        # If no start point has been set, just use the first one in the data
        #if start_Point is None:
        #    start_Point = dataSeries.Point_part
        # TODO: add support also for dynamically setting the end_Point to allow empty start_Point/end_Point input        
        
        # Are we before the start_Point? 
        if this_dataPoint.Point_part < start_Point:            
            
            # Just set the previous Point valid unit
            prev_dataPoint_valid_until = this_dataPoint.validity_region.end
            
            # Then continue
            continue

        # Otherwise, we are in the middle (or after the end)?
        else:

            # Set this Point's validity            
            this_dataPoint_valid_from = this_dataPoint.validity_region.start
            this_dataPoint_valid_until = this_dataPoint.validity_region.end


        #====================
        # START working area
        #====================

        #else:
        #    raise ConsistencyException('Internal consistency exception, check Luna source code! ({}, {})'.format(dataTimePoint.dt,start_dt))
           
        # Process here
        #print "------------------------------------ HARD DEBUG ---------------------------------------"
        #print "dataTimePoint.dt", dataTimePoint.dt
        #print "dataTimePoint.validity_region", dataTimePoint.validity_region
        #print "dataTimePoint.validity_region.span", dataTimePoint.validity_region.span
        #print "dataTimePoint.validity_region.anchor", dataTimePoint.validity_region.anchor
        #print "dataTimePoint.validity_region.end", dataTimePoint.validity_region.end
        #print "-> dataTimePoint.validity_region.start", dataTimePoint.validity_region.start
        #print "-> prev_valid_until                   ", prev_valid_until
        
        #====================
        #  END  working area
        #====================
 
 
        # Okay, now we have all the values we need:
        # 1) prev_dataPoint_valid_unitl
        # 2) this_dataPoint_valid_from

        # Compute coverage
        # TODO: and idea could also to initialize Spans and sum them
        if not prev_dataPoint_valid_until:
            missing_coverage = this_dataPoint_valid_from - start_Point
        else:
            value = this_dataPoint_valid_from - prev_dataPoint_valid_until
            
            # If for whatever reason the validity regions overlap we don't want to end up in
            # invalidating the coverage calculation by summing negative numbers
            if value > 0:
                if missing_coverage is None:
                    missing_coverage = value
                else:
                    missing_coverage = missing_coverage + value

        # Update previous dataPoint Validity:
        prev_dataPoint_valid_until = this_dataPoint_valid_until

    print '-> end_Point', end_Point


    # Convert missing_coverage_s_is in percentage
    if missing_coverage is not None:
        coverage = 1.0 - float(missing_coverage.values[0] ) / ( end_Point.values[0] - start_Point.values[0] ) 
    else:
        coverage = 0.0
        
    # Return
    print coverage
    logger.debug('compute_1D_coverage: Returning %s (%s percent)', coverage, coverage*100.0)
    return coverage



# TODO: the following is necessary?
def _compute_missing_coverage(prev_valid_until_dt, current_valid_from_dt, current_valid_until_dt, next_valid_from_dtp):
    return 0








