
from luna.common.exceptions import ConsistencyException
from luna.spacetime.time import s_from_dt
from luna.common.exceptions import InputException
from luna.datatypes.dimensional import Point

#--------------------------
#    Logger
#--------------------------

import logging
logger = logging.getLogger(__name__)


def compute_1D_coverage(dataSeries, start_Point, end_Point, trustme=False):
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
     
    # Sanity checks
    if not trustme:
        if dataSeries is None:
            raise InputException('You must provide dataSeries, got None')
            
        if start_Point is None or end_Point is None:
            raise NotImplementedError('Sorry, you must set start/end for now.')
      
        if not isinstance(start_Point, Point):
            raise InputException('start_Point not of type Point, got {}'.format(type(start_Point)))

        if not isinstance(end_Point, Point):
            raise InputException('end_Point not of type Point, got {}'.format(type(end_Point)))

    # Support vars
    prev_dataPoint_valid_until = None
    missing_coverage = None
    validity_region_presence = None

    for this_dataPoint in dataSeries:
        
        #logger.debug('HARD DEBUG %s %s %s', this_dataPoint.Point_part, this_dataPoint.validity_region.start, this_dataPoint.validity_region.end)
        
        # If no start point has been set, just use the first one in the data
        #if start_Point is None:
        #    start_Point = dataSeries.Point_part
        # TODO: add support also for dynamically setting the end_Point to allow empty start_Point/end_Point input        
        
        # Are we before the start_Point? 
        if this_dataPoint.Point_part < start_Point:
            
            # Just set the previous Point valid unit
            try:  
                prev_dataPoint_valid_until = this_dataPoint.validity_region.end
                if validity_region_presence is False:
                    raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
                validity_region_presence = True
            except AttributeError:
                if validity_region_presence is True:
                    raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
                prev_dataPoint_valid_until = this_dataPoint.Point_part
                validity_region_presence = False
            # Then continue
            continue

        # Are we after the end_Point? 
        elif this_dataPoint.Point_part > end_Point:
            # TODO: implement proper logic, see the AVG operation.
            continue

        # Otherwise, we are in the middle (or after the end)?
        else:

            # Set this Point's validity
            try:          
                this_dataPoint_valid_from  = this_dataPoint.validity_region.start
                this_dataPoint_valid_until = this_dataPoint.validity_region.end
                if validity_region_presence is False:
                    raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
                validity_region_presence = True
            except AttributeError:
                if validity_region_presence is True:
                    raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
                this_dataPoint_valid_from  = this_dataPoint.Point_part
                this_dataPoint_valid_until = this_dataPoint.Point_part
                validity_region_presence = False
                
        # Okay, now we have all the values we need:
        # 1) prev_dataPoint_valid_until
        # 2) this_dataPoint_valid_from

        # Compute coverage
        # TODO: and idea could also to initialize Spans and sum them
        if prev_dataPoint_valid_until is None:
            value = this_dataPoint_valid_from.values[0] - start_Point.values[0]
        else:
            value = this_dataPoint_valid_from.values[0] - prev_dataPoint_valid_until.values[0]
            
        # If for whatever reason the validity regions overlap we don't want to end up in
        # invalidating the coverage calculation by summing negative numbers
        if value > 0:
            if missing_coverage is None:
                missing_coverage = value
            else:
                missing_coverage = missing_coverage + value

        # Update previous dataPoint Validity:
        prev_dataPoint_valid_until = this_dataPoint_valid_until

    # Compute the coverage until the end point
    if prev_dataPoint_valid_until is not None:
        if prev_dataPoint_valid_until < end_Point and prev_dataPoint_valid_until > start_Point:
            if missing_coverage is not None:
                missing_coverage += (end_Point - prev_dataPoint_valid_until).values[0]
            else:
                missing_coverage = (end_Point - prev_dataPoint_valid_until).values[0]
        else:
            # No data at all:
            return 0.0
    else:
        # No data at all:
        return 0.0

    # Convert missing_coverage_s_is in percentage
    if missing_coverage is not None:
        coverage = 1.0 - float(missing_coverage) / ( end_Point.values[0] - start_Point.values[0] ) 
        if coverage <0 or coverage >1:
            for item in dataSeries:
                print item, missing_coverage
            raise ConsistencyException('Got Negative coverage!! {}'.format(coverage))
    else:
        coverage = 1.0
        
    # Return
    logger.debug('compute_1D_coverage: Returning %s (%s percent)', coverage, coverage*100.0)
    return coverage









