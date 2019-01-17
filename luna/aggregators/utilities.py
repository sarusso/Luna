
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
    empty_dataSeries = True
    next_processed = False

    logger.debug('Called compute_1D_coverage from {} to {}'.format(start_Point, end_Point))

    #---------------------------
    #  START cycle over points
    #---------------------------
    for this_dataPoint in dataSeries:
        
        # Hard debug
        #logger.debug('HARD DEBUG %s %s %s', this_dataPoint.Point_part, this_dataPoint.validity_region.start, this_dataPoint.validity_region.end)
        
        # If no start point has been set, just use the first one in the data
        #if start_Point is None:
        #    start_Point = dataSeries.Point_part
        # TODO: add support also for dynamically setting the end_Point to allow empty start_Point/end_Point input        
        
        #-----------------
        #  BEFORE START
        #-----------------
        # Are we before the start_Point? 
        if this_dataPoint.Point_part < start_Point:
            
            # Just set the previous Point valid until
            try:  
                prev_dataPoint_valid_until = this_dataPoint.validity_region.end
                if validity_region_presence is False:
                    raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
                validity_region_presence = True
            except AttributeError:
                if validity_region_presence is True:
                    raise InputException('Got DataPoint without a validity region but the previous one(s) did not have it') 
                prev_dataPoint_valid_until = this_dataPoint.Point_part
                validity_region_presence = False
            
            # If prev point too far, skip it
            if validity_region_presence:
                if prev_dataPoint_valid_until <= start_Point:
                    prev_dataPoint_valid_until = None

            continue


        #-----------------
        #  AFTER END
        #-----------------
        # Are we after the end_Point? In this case, we can treat it as if we are in the middle-
        elif this_dataPoint.Point_part >= end_Point:

            if not next_processed: 
                this_dataPoint_valid_from  = this_dataPoint.validity_region.start
                this_dataPoint_valid_until = this_dataPoint.validity_region.end # Not really necessary, but for consistency and to skip an if later
                next_processed = True
                
                # If "next" point too far, skip it:
                if this_dataPoint_valid_from > end_Point:
                    continue
            else:
                continue


        #-----------------
        #  IN THE MIDDLE
        #-----------------
        # Otherwise, we are in the middle?
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
        
        # Also, if we are here it also means that we have valid data
        if empty_dataSeries:
            empty_dataSeries=False

        # Compute coverage
        # TODO: and idea could also to initialize Spans and sum them
        if prev_dataPoint_valid_until is None:
            value = this_dataPoint_valid_from.t - start_Point.t
            
        else:
            value = this_dataPoint_valid_from.t - prev_dataPoint_valid_until.t
            
        # If for whatever reason the validity regions overlap we don't want to end up in
        # invalidating the coverage calculation by summing negative numbers
        if value > 0:
            if missing_coverage is None:
                missing_coverage = value
            else:
                missing_coverage = missing_coverage + value

        # Update previous dataPoint Validity:
        prev_dataPoint_valid_until = this_dataPoint_valid_until
        
    #---------------------------
    #   END cycle over points
    #---------------------------

    # Compute the coverage until the end point
    if prev_dataPoint_valid_until is not None:
        if end_Point > prev_dataPoint_valid_until:
            if missing_coverage is not None:
                missing_coverage += (end_Point - prev_dataPoint_valid_until).values[0]
            else:
                missing_coverage = (end_Point - prev_dataPoint_valid_until).values[0]
    
    # Convert missing_coverage_s_is in percentage
        
    if empty_dataSeries:
        coverage = 0.0 # Return zero coverage if empty
    
    elif missing_coverage is not None :
        coverage = 1.0 - float(missing_coverage) / ( end_Point.values[0] - start_Point.values[0] ) 
        
        # Fix boundaries # TODO: understand better this part
        if coverage < 0:
            coverage = 0.0
            #raise ConsistencyException('Got Negative coverage!! {}'.format(coverage))
        if coverage > 1:
            coverage = 1.0
            #raise ConsistencyException('Got >1 coverage!! {}'.format(coverage))
    
    else:
        coverage = 1.0
        
    # Return
    logger.debug('compute_1D_coverage: Returning %s (%s percent)', coverage, coverage*100.0)
    return coverage







from luna.datatypes.dimensional import DataTimePoint, PhysicalData, PhysicalDataTimePoint, DataTimeSeries, TimeSlot, PhysicalDataTimeSlot, TimePoint
from luna.spacetime.time import dt

def clean_and_reconstruct(dataTimePointSeries, from_dt=None, to_dt=None):
    
    # Log
    logger.debug('Called clean_and_reconstruct on {}'.format(dataTimePointSeries))
    
    # Support structure
    class SimpleDataTimePoint(object):
        
        def __init__(self, dataTimePoint):
            self.ts         = dataTimePoint.timePoint
            self.valid_from = dataTimePoint.validity_region.start
            self.valid_to   = dataTimePoint.validity_region.end
            self.data       = dataTimePoint.data


    # Support functions  
    def overlap(first_dataTimePoint, second_dataTimePoint):
        '''Detects an overlp between validity regions of two points'''
        
        if first_dataTimePoint > second_dataTimePoint:
            raise InputException('Second datTimePoint preceeds the first, please invert them in the call')
        
        # Note: equal is OK regions, slots etc. are always left excluded
        if first_dataTimePoint.validity_region.end > second_dataTimePoint.validity_region.start:
            logger.debug(' Detected overlap between {} and {}'.format(first_dataTimePoint, second_dataTimePoint))
            return True
        else:
            return False

    def fix_overlap_with_next(simpleDataTimePoint, this_dataTimePoint, next_dataTimePoint):
        offset_t = (this_dataTimePoint.validity_region.end.t - next_dataTimePoint.validity_region.start.t)/2
        new_valid_to_t = this_dataTimePoint.validity_region.end.t - offset_t
        new_valid_to = TimePoint(t=new_valid_to_t)
        logger.debug('  Old valid to: {}, new valid_to: {}'.format(this_dataTimePoint.validity_region.end, new_valid_to))
        simpleDataTimePoint.valid_to = new_valid_to

    def fix_overlap_with_prev(simpleDataTimePoint, this_dataTimePoint, prev_dataTimePoint):
        offset_t = (prev_dataTimePoint.validity_region.end.t - this_dataTimePoint.validity_region.start.t)/2
        new_valid_from_t = this_dataTimePoint.validity_region.start.t + offset_t
        new_valid_from = TimePoint(t=new_valid_from_t)
        logger.debug('  Old valid from: {}, new valid_from: {}'.format(this_dataTimePoint.validity_region.start, new_valid_from))
        simpleDataTimePoint.valid_from = new_valid_from

    def missing_data(this_dataTimePoint, next_dataTimePoint):
        if this_dataTimePoint.validity_region.end.t < next_dataTimePoint.validity_region.start.t:
            logger.debug(' Detected missing data between {} and {}'.format(this_dataTimePoint.validity_region.end.dt, next_dataTimePoint.validity_region.start.dt))
            return True
        else:
            return False
    
    def reconstruct_missing_data(simpleSeries, this_dataTimePoint, next_dataTimePoint):
        offset_t = (next_dataTimePoint.validity_region.start.t - this_dataTimePoint.validity_region.end.t)/2       
        reconstructed_timestamp_t = this_dataTimePoint.validity_region.end.t + offset_t
        reconstructed_timestamp =  TimePoint(t=reconstructed_timestamp_t)
        
        # Reconstruct data
        #PhysicalData( labels = ['temp_C'], values = [25.5] )
        reconstructed_values = []
        for label in this_dataTimePoint.data.labels:
            reconstructed_value = (this_dataTimePoint.data[label] + next_dataTimePoint.data[label])/2
            reconstructed_values.append(reconstructed_value)
            
        reconstructed_data = this_dataTimePoint.data.__class__(labels=this_dataTimePoint.data.labels, values=reconstructed_values)
        reconstructed_dataTimePoint = this_dataTimePoint.__class__(dt = reconstructed_timestamp.dt,
                                                                   data = reconstructed_data,
                                                                   validity_region = TimeSlot(span='{}u'.format(int(offset_t*2*1000000))))
        
        logger.debug(' Reconstructed dataTimePoint {} from {} to {}'.format(reconstructed_dataTimePoint, reconstructed_dataTimePoint.validity_region.start.dt, reconstructed_dataTimePoint.validity_region.end.dt))

        simpleSeries.append(SimpleDataTimePoint(reconstructed_dataTimePoint))
        #pass


   
    # Support vars
    simpleSeries = [] 
    
 
    # Start    
    for i, this_dataTimePoint in enumerate(dataTimePointSeries):
        logger.debug('--------------------------------------------------------------------------------')
        logger.debug('{}'.format(this_dataTimePoint))
        logger.debug(' {}'.format(this_dataTimePoint.validity_region.start))
        logger.debug(' {}'.format(this_dataTimePoint.timePoint))
        logger.debug(' {}'.format(this_dataTimePoint.validity_region.end))

        #==============================
        # Special case: only one point
        #==============================
        if len(dataTimePointSeries) == 1:
            
            # Create SimpleDataTimePoint
            simpleDataTimePoint = SimpleDataTimePoint(this_dataTimePoint)
  
            # Append to simpleSeries
            simpleSeries.append(simpleDataTimePoint)
        

        #==============================
        # Special case: first point
        #==============================

        # This is the first point
        elif i == 0:
            
            # Set the next
            next_dataTimePoint = dataTimePointSeries.byindex(i+1)

            # Create SimpleDataTimePoint
            simpleDataTimePoint = SimpleDataTimePoint(this_dataTimePoint)
        
            # Do we have any overlap with the next?
            if overlap(this_dataTimePoint, next_dataTimePoint):
                fix_overlap_with_next(simpleDataTimePoint, this_dataTimePoint, next_dataTimePoint)
            
            # Append to simpleSeries
            simpleSeries.append(simpleDataTimePoint)

            # Do we have missing data with the next?
            if missing_data(this_dataTimePoint, next_dataTimePoint):
                reconstruct_missing_data(simpleSeries, this_dataTimePoint, next_dataTimePoint)
         

        #==============================
        # Special case: last point
        #==============================
        elif i == len(dataTimePointSeries)-1:
            
            # Set the prev
            prev_dataTimePoint = dataTimePointSeries.byindex(i-1)

            # Create SimpleDataTimePoint
            simpleDataTimePoint = SimpleDataTimePoint(this_dataTimePoint)

            # Do we have any overlap with the prev?
            if overlap(prev_dataTimePoint, this_dataTimePoint):
                fix_overlap_with_prev(simpleDataTimePoint, this_dataTimePoint, prev_dataTimePoint)
 
            # Append to simpleSeries
            simpleSeries.append(simpleDataTimePoint)



        #==============================
        # Standard case
        #==============================
        else:

            # Set the prev
            prev_dataTimePoint = dataTimePointSeries.byindex(i-1)
           
            # Set the next
            next_dataTimePoint = dataTimePointSeries.byindex(i+1)

            # Create SimpleDataTimePoint
            simpleDataTimePoint = SimpleDataTimePoint(this_dataTimePoint)

            # Do we have any overlap with the prev?
            if overlap(prev_dataTimePoint, this_dataTimePoint):
                fix_overlap_with_prev(simpleDataTimePoint, this_dataTimePoint, prev_dataTimePoint)

            # Do we have any overlap with the next?
            if overlap(this_dataTimePoint, next_dataTimePoint):
                fix_overlap_with_next(simpleDataTimePoint, this_dataTimePoint, next_dataTimePoint)
            
            # Append to simpleSeries
            simpleSeries.append(simpleDataTimePoint)
            
            # Do we have missing data with the next?
            if missing_data(this_dataTimePoint, next_dataTimePoint):
                reconstruct_missing_data(simpleSeries, this_dataTimePoint, next_dataTimePoint)



    logger.debug('--------------------------------------------------------------------------------')

    # NOTE: in theory, in the following, in case of no data you could right or left fill and cover 
    # entire segments completely dislocated in respect to the time series. Coverage would be zero.

    
    if from_dt is not None:
        
        # Do we have data?
        if from_dt > simpleSeries[-1].valid_to.dt:
            return None
        
        # Do we have to truncate, add a point at the beginning in leftfill or do nothing?
        if simpleSeries[0].valid_from.dt >= from_dt:
            # Add a point in leftfill
            logger.debug('Will add a point in leftfill from {} to {}'.format(from_dt, simpleSeries[0].valid_from.dt)) 
            
            # Compute span
            from_t = TimePoint(dt=from_dt).t
            offset_t = (simpleSeries[0].valid_from.t - from_t)/2
            timestamp_t = from_t + offset_t
            timestamp_dt = TimePoint(t=timestamp_t).dt 
            
            # Create dataTimePoint
            leftfilled_dataTimePoint = dataTimePointSeries.byindex(0).__class__(dt = timestamp_dt,
                                                                                data = simpleSeries[0].data,
                                                                                validity_region = TimeSlot(span='{}u'.format(int(offset_t*2*1000000))))
            # Convert to simple point
            leftfilled_simpleDataTimePoint = SimpleDataTimePoint(leftfilled_dataTimePoint)
            
            # Add to simple list
            simpleSeries = [leftfilled_simpleDataTimePoint] + simpleSeries
            
        
        else:
            # Find where the from_dt falls and truncate the Point there.
            for i, simpleDataTimePoint in enumerate(simpleSeries):
                logger.debug(simpleDataTimePoint.valid_from.dt)
                logger.debug(from_dt)
                logger.debug(simpleDataTimePoint.valid_to.dt)
                if simpleDataTimePoint.valid_from.dt <= from_dt and from_dt < simpleDataTimePoint.valid_to.dt:
                    logger.debug('Will truncate at #{}, {}'.format(i,simpleDataTimePoint.ts)) 
                    simpleDataTimePoint.valid_from = TimePoint(dt=from_dt)
                    simpleSeries = simpleSeries[i:]
                    break    
        
    if to_dt is not None:

        # Do we have data?
        if to_dt < simpleSeries[0].valid_from.dt:
            return None
               
        # Do we have to truncate, add a point at the end in right or do nothing?
        if simpleSeries[-1].valid_to.dt < to_dt:
            
            # Add a Point in leftfill
            logger.debug('Will add a point in rightfill from {} to {}'.format(simpleSeries[-1].valid_to.dt, to_dt)) 
            
            # Compute span
            to_t = TimePoint(dt=to_dt).t
            offset_t = (to_t - simpleSeries[-1].valid_to.t)/2
            timestamp_t = simpleSeries[-1].valid_to.t + offset_t
            timestamp_dt = TimePoint(t=timestamp_t).dt 
            
            # Create dataTimePoint
            rightfilled_dataTimePoint = dataTimePointSeries.byindex(0).__class__(dt = timestamp_dt,
                                                                                data = simpleSeries[-1].data,
                                                                                validity_region = TimeSlot(span='{}u'.format(int(offset_t*2*1000000))))
            # Convert to simple point
            rightfilled_simpleDataTimePoint = SimpleDataTimePoint(rightfilled_dataTimePoint)
            
            # Add to simple list
            simpleSeries.append(rightfilled_simpleDataTimePoint)
            
        
        else:
            # Find where the to_dt falls and truncate the Point there.
            for i, simpleDataTimePoint in enumerate(simpleSeries):
                logger.debug('---')
                logger.debug(simpleDataTimePoint.valid_from.dt)
                logger.debug(to_dt)
                logger.debug(simpleDataTimePoint.valid_to.dt)
                if simpleDataTimePoint.valid_from.dt < to_dt and to_dt < simpleDataTimePoint.valid_to.dt:
                    logger.debug('Will truncate at #{}, {}'.format(i,simpleDataTimePoint.ts)) 
                    simpleDataTimePoint.valid_to = TimePoint(dt=to_dt)  
                    simpleSeries = simpleSeries[:i+1]
                    break      
        

    
    logger.debug('Now building dataTimeSlotSeries')
    dataTimeSlotSeries = DataTimeSeries()
    for simpleDataTimePoint in simpleSeries:
        logger.debug(' Adding Slot {} to {}'.format(simpleDataTimePoint.valid_from, simpleDataTimePoint.valid_to))
        dataTimeSlotSeries.append(PhysicalDataTimeSlot(start = simpleDataTimePoint.valid_from,
                                                       end   = simpleDataTimePoint.valid_to,
                                                       data  = simpleDataTimePoint.data))
    
    return dataTimeSlotSeries            









