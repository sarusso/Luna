
from luna.datatypes.dimensional import DataTimeSeries
from luna.common.exceptions import ConsistencyException
from luna.common.exceptions import InputException
from luna.datatypes.dimensional import Point

import logging
logger = logging.getLogger(__name__)

class Operation(object):
    
    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point):
        raise NotImplementedError()
    
    @staticmethod
    def compute_on_Slots(dataSeries, start_Point, end_Point):
        raise NotImplementedError()


class AVG_OLD(Operation):
    
    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point):
           
        sum = 0.0
        
        # Compute total lenght
        total_weight   = (end_Point.operation_value - start_Point.operation_value)
        past_dataTimePoint = None
        prev_weight    = None
        prev_value     = None
        weighted       = None
        
        logger.debug('Called AVG from {} to {}'.format(start_Point, end_Point))
        
        for this_dataTimePoint in dataSeries:

            logger.debug('-------------------')
            logger.debug('prev: {}'.format(past_dataTimePoint))
            logger.debug('this: {}'.format(this_dataTimePoint))
            logger.debug('-------------------')
            
            # Set if weighted avg or not
            if weighted is None:
                try:
                    this_dataTimePoint.validity_region
                    weighted = True
                except AttributeError:
                    weighted = False                
                
            if weighted:
                # Special case of only one point:
                if len(dataSeries) == 1:
                    
                    sum = this_dataTimePoint.operation_value
                    
                    if this_dataTimePoint.validity_region.start < start_Point:
                        # Weight differently
                        pass
                    if this_dataTimePoint.validity_region.end > end_Point:
                        # Weight differently
                        pass
                    
                    # Ok, break.
                    break
                
                # Special case of the first point and more than one point
                if past_dataTimePoint is None:
                    past_dataTimePoint = this_dataTimePoint
                    continue
     
                # If we have two points..
                past_dataTimePoint_validity_region_start = past_dataTimePoint.validity_region.start
                past_dataTimePoint_validity_region_end   = past_dataTimePoint.validity_region.end       
                this_dataTimePoint_validity_region_start = this_dataTimePoint.validity_region.start
                this_dataTimePoint_validity_region_end   = this_dataTimePoint.validity_region.end

                # Set correct limits                
                if past_dataTimePoint_validity_region_start < start_Point:
                    past_dataTimePoint_validity_region_start = start_Point
                if this_dataTimePoint_validity_region_start < start_Point:
                    this_dataTimePoint_validity_region_start = start_Point              
                if past_dataTimePoint_validity_region_end > end_Point:
                    past_dataTimePoint_validity_region_end = end_Point                            
                if this_dataTimePoint_validity_region_end > end_Point:
                    this_dataTimePoint_validity_region_end = end_Point   
                
                # Set correct prev_end:
                past_dataTimePoint_validity_region_end = past_dataTimePoint_validity_region_end if  this_dataTimePoint_validity_region_start > past_dataTimePoint_validity_region_end else this_dataTimePoint_validity_region_start
                
                # Set correct weight
                if this_dataTimePoint_validity_region_start < past_dataTimePoint_validity_region_end: # gt is correctly handled
                    #case='A'
                    prev_weight = (this_dataTimePoint_validity_region_start.operation_value - past_dataTimePoint_validity_region_start.operation_value) # ..Sub is not?
                else:
                    #case='B'
                    prev_weight = (past_dataTimePoint_validity_region_end.operation_value - past_dataTimePoint_validity_region_start.operation_value)
                    
                if prev_weight<0:
                    # This happens in case the prev point is not contained at all (including the validity region) in the current slot.
                    # Set prev_weight= 0 to skip the point. TODO: improve this part
                    prev_weight = 0
                    
                    # DEBUG of the above
                    #print 'case:', case
                    #print 'this_dataTimePoint_validity_region_start.operation_value', this_dataTimePoint_validity_region_start.operation_value
                    #print 'past_dataTimePoint_validity_region_start.operation_value', past_dataTimePoint_validity_region_start.operation_value 
                    #print 'past_dataTimePoint_validity_region_end.operation_value', past_dataTimePoint_validity_region_end.operation_value      
                    #for point in dataSeries:
                    #    print point
                    #    print point.validity_region.start
                    #    print point.validity_region.end  
                    #raise ConsistencyException('Got negative weight: {}. Boundary conditions: past_dataTimePoint={}, this_dataTimePoint={}'.format(prev_weight, past_dataTimePoint, this_dataTimePoint))
                
                # Compute
                sum += ( prev_weight * past_dataTimePoint.data.operation_value )
                
                # Reassign
                past_dataTimePoint = this_dataTimePoint
          
            else:
                sum += this_dataTimePoint.data.operation_value
    
        if weighted:
            # Last step in case of no 'next' point:
            if prev_weight is not None and past_dataTimePoint.Point_part <= end_Point:
                
                # Set correct limits                
                if past_dataTimePoint_validity_region_start < start_Point:
                    past_dataTimePoint_validity_region_start = start_Point
                if this_dataTimePoint_validity_region_start < start_Point:
                    this_dataTimePoint_validity_region_start = start_Point              
                prev_weight = (past_dataTimePoint_validity_region_end.operation_value - past_dataTimePoint_validity_region_start.operation_value)
                
                # Set and add sum
                prev_value  = this_dataTimePoint.data.operation_value
                sum += (prev_weight*prev_value)
        
            
            return sum/total_weight
    
        else:        
            return sum/len(dataSeries)


    @staticmethod
    def compute_on_Slots(dataSeries, start_Point, end_Point):
        return None


class MIN(Operation):

    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point):
        min = None
        for dataTimePoint in dataSeries:
            if min is None:
                min = dataTimePoint.data.operation_value
            elif dataTimePoint.data.operation_value < min:
                min = dataTimePoint.data.operation_value
            else:
                pass
        return min

    @staticmethod
    def compute_on_Slots(dataSeries, start_Point, end_Point):
        return None


class MAX(Operation):
    
    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point):
        max = None
        for item in dataSeries:
            if max is None:
                max = item.data.operation_value
            elif item.data.operation_value > max:
                max = item.data.operation_value
            else:
                pass
        return max

    @staticmethod
    def compute_on_Slots(dataSeries, start_Point, end_Point):
        return None





def has_validity_region(dataTimePoint):
    try:
        if dataTimePoint.validity_region.start == dataTimePoint.validity_region.end:
            return False
    except AttributeError:
        return False
    return True





def clean_dataTimePointSeries(dataTimePointSeries, start_timePoint=None, end_timePoint=None):
    '''Clean a dataTimePointSeries and returns a uniform dataTimeSlotSeries'''

    from luna.datatypes.dimensional import DataTimeSlot, TimePoint
    
    # Init result
    dataTimePointSeries_cleaned = DataTimeSeries(index=False)

    # Support vars
    validity_region_presence = None
    past_dataTimePoint = None
    
    # Do we have validity regions?
    for this_dataTimePoint in dataTimePointSeries: 
        if has_validity_region(this_dataTimePoint):
            validity_region_presence=True
        else:
            validity_region_presence=False
        break
    
    if validity_region_presence:
        logger.debug('Cleaning and reconstructing missing values with validity regions')
        for i, this_dataTimePoint in enumerate(dataTimePointSeries):
            logger.debug(' this: {}'.format(this_dataTimePoint))
            # Check validity region consistency
            if has_validity_region(this_dataTimePoint) and validity_region_presence is False:
                raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
            if not has_validity_region(this_dataTimePoint) and validity_region_presence is True:
                raise InputException('Got DataPoint without a validity region but the previous one(s) did not have it') 


            #==============================
            # First iteration?
            #==============================
            
            if not past_dataTimePoint:
                
                # Set Point_class
                Point_class = this_dataTimePoint.data.__class__

                if this_dataTimePoint.Point_part > start_timePoint:
                    # This is the case where we don't have a prev. Can happen only once.
                    logger.debug('  ADDING leftfileld missing (prev) POINT from {} to {}, value={}'.format(start_timePoint, this_dataTimePoint.validity_region.start, this_dataTimePoint.data.operation_value))

                    missing_dataTimeSlot = DataTimeSlot(start = start_timePoint,
                                                        end   = this_dataTimePoint.validity_region.start,
                                                        data  = Point_class(labels=[this_dataTimePoint.data.lazy_filter_label], values=[this_dataTimePoint.data.operation_value]))
                    
                    # In tis case, add it straight away.
                    dataTimePointSeries_cleaned.append(missing_dataTimeSlot)
                    
                # Set past point and continue. DO not set the past slot, this step is una tantum.
                past_dataTimePoint = this_dataTimePoint
                
            else:
                
                #==============================
                # Are we dealing with a Prev?
                #==============================
                if past_dataTimePoint.Point_part < start_timePoint:
                    logger.debug('Dealing with a prev')
                    
                    # Missing data?
                    if (past_dataTimePoint.validity_region.end != this_dataTimePoint.validity_region.start):
                        
                        # Validity region of the Prev not entering this Slot (left included)
                        if past_dataTimePoint.validity_region.end < start_timePoint:
                            missing_validity_region_start = start_timePoint
                        
                        # Validity region of the Prev entering this Slot (left included)
                        else:
                            missing_validity_region_start = past_dataTimePoint.validity_region.end
                        
                        
                        #===========================================
                        # Special case where we have already a Next
                        #===========================================
                        
                        if this_dataTimePoint.Point_part >= end_timePoint: 
                            # TODO: Remove non computing data if coverage=None to make it work
                            # TODO: consider also possible overlaps of prev and next validty regions
                        
                            # Validity region of the Next not entering this Slot (right excluded)
                            if this_dataTimePoint.validity_region.start >= end_timePoint:
                                missing_validity_region_end = end_timePoint
                            
                            # Validity region of theNext entering this Slot (right excluded)
                            else:
                                missing_validity_region_end  = this_dataTimePoint.validity_region.start
                        
                        else:
                            missing_validity_region_end  = this_dataTimePoint.validity_region.end

                        reconstructed_value = (past_dataTimePoint.data.operation_value + this_dataTimePoint.data.operation_value)/2.0
                        logger.debug('  ADDING missing (post-prev) POINT from {} to {}, value={}'.format(missing_validity_region_start, missing_validity_region_end, reconstructed_value))
                        missing_dataTimeSlot = DataTimeSlot(start = missing_validity_region_start,
                                                            end   = missing_validity_region_end,
                                                            data  = Point_class(labels=[this_dataTimePoint.data.lazy_filter_label], values=[this_dataTimePoint.data.operation_value]))
                        
                        # Set past
                        past_dataTimePoint = this_dataTimePoint
                        past_dataTimeSlot  = missing_dataTimeSlot

                #==============================
                # Are we dealing with a Next?
                #==============================
                elif this_dataTimePoint.Point_part >= end_timePoint:
                    
                    # Check that we are in a real Next situation
                    if this_dataTimePoint < end_timePoint:
                        raise ConsistencyException('I ended up in a slot with no visibility of a Next')
                        # Basically, you can never be in a "rightfill" situation as time do have a privileged direction, and it is forward
                        # In other words, we need to wait for the future to happen before taking any decision, therefore there will be always a "Next"
                                            
                    logger.debug('Dealing with a next')

                    # Missing data?
                    if (past_dataTimeSlot.end != this_dataTimePoint.validity_region.start):

                        # Validity region of the Next not entering this Slot (right excluded)
                        if this_dataTimePoint.validity_region.start >= end_timePoint:
                            missing_validity_region_end = end_timePoint
                        
                        # Validity region of the Next entering this Slot (right excluded)
                        else:
                            missing_validity_region_end = this_dataTimePoint.validity_region.start

                        missing_validity_region_end  = this_dataTimePoint.validity_region.start
                        
                        reconstructed_value = (past_dataTimeSlot.data[0] + this_dataTimePoint.data.operation_value)/2.0

                        logger.debug('  ADDING missing (pre-next) POINT from {} to {}, value={}'.format(past_dataTimeSlot.end, this_dataTimePoint.validity_region.start, reconstructed_value))

                        missing_dataTimeSlot = DataTimeSlot(start = past_dataTimePoint.validity_region.end,
                                                            end   = this_dataTimePoint.validity_region.start,
                                                            data  = Point_class(labels=[this_dataTimePoint.data.lazy_filter_label], values=[this_dataTimePoint.data.operation_value]))

                        dataTimePointSeries_cleaned.append(missing_dataTimeSlot)
                        # Ok, completed (just break, do not set past)
                        break

                else:
                    #============================
                    #  All points in the middle
                    #============================

                    logger.debug('Not dealing with a particular case')
                    this_validity_region_start = this_dataTimePoint.validity_region.start
                    this_validity_region_end = this_dataTimePoint.validity_region.end
                    
                    logger.debug('  past_validity_region_start: {}'.format(past_dataTimeSlot.start))
                    logger.debug('  past_validity_region_end: {}'.format(past_dataTimeSlot.start))
                    logger.debug('  this_validity_region_start: {}'.format(this_validity_region_start))
                    logger.debug('  this_validity_region_end:   {}'.format(this_validity_region_end))
                    
                    #_____________________
                    # Shrink for start-end
                    
                    # Do we have to shrink down because of a start_timePoint?
                    if this_validity_region_start < start_timePoint:
                        this_validity_region_start = start_timePoint
                        
                    # Do we have to shrink down because of a end_timePoint?
                    if this_validity_region_end > end_timePoint:
                        this_validity_region_end = end_timePoint                      
                    
                    
                    #______________
                    # Missing data?
                    
                    if (past_dataTimeSlot.end < this_validity_region_start):
                        
                        # Here we can append the past slot
                        dataTimePointSeries_cleaned.append(past_dataTimeSlot)
                        
                        newvalue = (past_dataTimeSlot.data[0]+ this_dataTimePoint.data.operation_value)/2.0
                        logger.debug('  ADDING missing (middle) POINT from {} to {}, value={}'.format(past_dataTimeSlot.end, this_validity_region_start, newvalue))
                        dataTimeSlot = DataTimeSlot(start = past_dataTimeSlot.end,
                                                    end   = this_validity_region_start,
                                                    data  = Point_class(labels=[this_dataTimePoint.data.lazy_filter_label], values=[this_dataTimePoint.data.operation_value]))
                        

                        # Set new past slot
                        past_dataTimeSlot = dataTimeSlot


                    #_________
                    # Overlap?
                    
                    elif (past_dataTimeSlot.end > this_dataTimePoint.validity_region.start):
                        #raise Exception('Overlap! ({} <-> {})'.format(past_dataTimePoint.validity_region.end, this_dataTimePoint.validity_region.start))
                        
                        joint_t = past_dataTimeSlot.end.t + ((past_dataTimeSlot.end.t - this_dataTimePoint.validity_region.start.t)/2)
                        joint_timePoint = TimePoint(t=joint_t, tz=past_dataTimeSlot.end.tz)
                        
                        logger.debug('  changing past_dataTimeSlot end to {}'.format(joint_timePoint))
                        # Create new past_dataTimeSlot to replace the one with the wrong (overlapped) end
                        past_dataTimeSlot = DataTimeSlot(start = past_dataTimeSlot.start,
                                                         end   = joint_timePoint,
                                                         data  = past_dataTimeSlot.data)
                        
                        # Append the new past slot (with the new end to avoid the overlap)
                        dataTimePointSeries_cleaned.append(past_dataTimeSlot)
                        
                        # Set new this_validity_region_start
                        this_validity_region_start = joint_timePoint


                    #______________________________
                    # Nothing relevant (on borders)
                    else:
                        # Just append the past slot
                        dataTimePointSeries_cleaned.append(past_dataTimeSlot)
                        
                    #__________________________
                    # handle this_dataTimePoint
                    
                    # Ok, here we have the slots until now (past and newly generated to cover missing data) ready.

                    logger.debug('  this_validity_region_start (recomputed): {}'.format(this_validity_region_start))
                    logger.debug('  this_validity_region_end   (recomputed): {}'.format(this_validity_region_end))

                
                    logger.debug('  ADDING this POINT from {} to {}, value={}'.format(this_validity_region_start, this_validity_region_end, this_dataTimePoint.data.operation_value))
                    dataTimeSlot = DataTimeSlot(start = this_validity_region_start,
                                                end   = this_validity_region_end,
                                                data  = Point_class(labels=[this_dataTimePoint.data.lazy_filter_label], values=[this_dataTimePoint.data.operation_value]))
                    past_dataTimeSlot = dataTimeSlot
                    dataTimePointSeries_cleaned.append(dataTimeSlot)
            
                    # Log
                    #logger.debug('Point #{} of {}'.format(i, len(dataTimePointSeries)))

                    # Set past
                    past_dataTimePoint = this_dataTimePoint
                        
            return dataTimePointSeries_cleaned
        
        else:
            raise NotImplementedError('Cleaning time series with points without validity region not yet supported')
 






class AVG(Operation):
    
    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point, trustme=False):
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
        
        # Use more friendly names. TODO: Introduce dataTimePointSeries and dataTimeSlotSeries,  add a single compute method with polymorphism and support simple dataSeries as well
        dataTimePointSeries = dataSeries
        start_timePoint = start_Point
        end_timePoint = end_Point
        
        logger.debug('===========================================================================================================')
        logger.debug('Called AVG from {} to {}'.format(start_timePoint, end_timePoint))
        logger.debug('===========================================================================================================')
        logger.debug(' Called on items:')
        for item in dataSeries:
            logger.debug('  {}'.format(item))
        logger.debug('===========================================================================================================')
        # Sanity checks
        if not trustme:
            if dataTimePointSeries is None:
                raise InputException('You must provide dataTimePointSeries, got None')
                
            if start_timePoint is None or end_timePoint is None:
                raise NotImplementedError('Sorry, you must set start/end for now.')
          
            if not isinstance(start_timePoint, Point):
                raise InputException('start_timePoint not of type Point, got {}'.format(type(start_timePoint)))
    
            if not isinstance(end_timePoint, Point):
                raise InputException('end_timePoint not of type Point, got {}'.format(type(end_timePoint)))
    

    
    
        #------------------------------------
        #   Compute with validity regions
        #------------------------------------
        
        
        dataTimePointSeries_cleaned = clean_dataTimePointSeries(dataTimePointSeries, start_timePoint, end_timePoint)
        
        #logger.debug('--------------- CLEANED ----------------------------')
        #for item in dataTimePointSeries_cleaned:
        #    logger.debug(item)
        #logger.debug('----------------------------------------------------')
                

        average = 5
        
        return average
 


    @staticmethod
    def compute_on_Slots(dataSeries, start_Point, end_Point):
        return None





#     def compute_on_Points(dataSeries, start_Point, end_Point, trustme=False):
#         '''Compute the data coverage of a 1-dimensional dataSeries based on the points validity_region.
#         The computation is done in a streaming fashion so it scales.
#         
#         Args:
#             dataSeries(dataSeries): the DataSeries
#             start_Point(Point): start Point for the coverage calculation
#             end_Point(Point): end Point for the coverage calculation
#     
#         Raises:
#             InputException: if some argument is passed in a wrong format
#             
#         Returns:
#             float: float value between 0.0 and 1.0
#         '''
#          
#         # Sanity checks
#         if not trustme:
#             if dataSeries is None:
#                 raise InputException('You must provide dataSeries, got None')
#                 
#             if start_Point is None or end_Point is None:
#                 raise NotImplementedError('Sorry, you must set start/end for now.')
#           
#             if not isinstance(start_Point, Point):
#                 raise InputException('start_Point not of type Point, got {}'.format(type(start_Point)))
#     
#             if not isinstance(end_Point, Point):
#                 raise InputException('end_Point not of type Point, got {}'.format(type(end_Point)))
#     
#         # Support vars
#         past_dataTimePoint = None
#         missing_coverage = None
#         validity_region_presence = None
#         empty_dataSeries = True
#         next_processed = False
#     
#         logger.debug('Called AVG from {} to {}'.format(start_Point, end_Point))
#     
#         #---------------------------
#         #  START cycle over points
#         #---------------------------
#         for this_dataTimePoint in dataSeries:
#             
#             # Hard debug
#             #logger.debug('HARD DEBUG %s %s %s', this_dataTimePoint.Point_part, this_dataTimePoint.validity_region.start, this_dataTimePoint.validity_region.end)
#             
#             # If no start point has been set, just use the first one in the data
#             #if start_Point is None:
#             #    start_Point = dataSeries.Point_part
#             # TODO: add support also for dynamically setting the end_Point to allow empty start_Point/end_Point input        
#             
#             #-----------------
#             #  BEFORE START
#             #-----------------
#             # Are we before the start_Point? 
#             if this_dataTimePoint.Point_part < start_Point:
#                 
#                 # Check validity region consistency
#                 try:
#                     this_dataTimePoint.validity_region.start
#                     if validity_region_presence is False:
#                         raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
#                     validity_region_presence = True
#                 except AttributeError:
#                     if validity_region_presence is True:
#                         raise InputException('Got DataPoint without a validity region but the previous one(s) did not have it') 
#                     validity_region_presence = False
#                     
#                 # Set prev dataTimePoint
#                 past_dataTimePoint = this_dataTimePoint
#     
#                 # note: past_dataTimePoint.validity_region.end
#                 continue
#     
#     
#             #-----------------
#             #  AFTER END
#             #-----------------
#             # Are we after the end_Point? In this case, we can treat it as if we are in the middle-
#             elif this_dataTimePoint.Point_part >= end_Point:
#     
#                 if not next_processed: 
#                     next_processed = True
#     
#                 else:
#                     continue
#     
#     
#             #-----------------
#             #  IN THE MIDDLE
#             #-----------------
#             # Otherwise, we are in the middle?
#             else:
#     
#                 # Sanity check
#                 try:          
#                     this_dataTimePoint.validity_region.start
#                     if validity_region_presence is False:
#                         raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
#                     validity_region_presence = True
#                 except AttributeError:
#                     if validity_region_presence is True:
#                         raise InputException('Got DataPoint with a validity region but the previous one(s) did not have it') 
#                     validity_region_presence = False
#     
#             # R
#     
#     
#             # Okay, now we have all the values we need:
#             # 1) past_dataTimePoint
#             # 2) this_dataTimePoint
#             
#             # Also, if we are here it also means that we have valid data
#             if empty_dataSeries:
#                 empty_dataSeries=False
#     
#             # Compute (weighted) average
#             # TODO: and idea could also to initialize Spans and sum them
#             logger.debug('---------------------------  START   -------------------------------------------------')
#             
#             # Setup support vars
#             if past_dataTimePoint is None:
#                 prev_value = this_dataTimePoint.data.operation_value
#                 prev_value_valid_until = start_Point
#                 prev_weigh = None
# 
#             else:
#                 
#                 
#                 prev_value = past_dataTimePoint.data.operation_value
#                 prev_value_valid_until = past_dataTimePoint.validity_region.start
#                 
#             # Compute
#             
#             
#             
#             
#             weight = this_dataTimePoint.validity_region.end.t - this_dataTimePoint.validity_region.start.t
#             
#             logger.debug(weight)   
#             logger.debug(this_dataTimePoint.data.operation_value)    
#             value= 5
#             logger.debug('---------------------------   END    -------------------------------------------------')
#             
#             # Update previous dataTimePoint Validity:
#             past_dataTimePoint = this_dataTimePoint
#             
#         #---------------------------
#         #   END cycle over points
#         #---------------------------
#     
#         return value













