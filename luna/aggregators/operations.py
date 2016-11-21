
from luna.datatypes.dimensional import DataTimeSeries
from luna.common.exceptions import ConsistencyException

class Operation(object):
    
    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point):
        raise NotImplementedError()
    
    @staticmethod
    def compute_on_Slots(dataSeries, start_Point, end_Point):
        raise NotImplementedError()


class AVG(Operation):
    
    @staticmethod
    def compute_on_Points(dataSeries, start_Point, end_Point):
           
        sum = 0.0
        
        # Compute total lenght
        total_weight   = (end_Point.operation_value - start_Point.operation_value)
        prev_dataPoint = None
        prev_weight    = None
        prev_value     = None
        weighted       = None
        
        for this_dataPoint in dataSeries:
            
            # Set if weighetd avg or not
            if weighted is None:
                try:
                    this_dataPoint.validity_region
                    weighted = True
                except AttributeError:
                    weighted = False                
                
            if weighted:
                # Special case of only one point:
                if len(dataSeries) == 1:
                    
                    sum = this_dataPoint.operation_value
                    
                    if this_dataPoint.validity_region.start < start_Point:
                        # Weight differently
                        pass
                    if this_dataPoint.validity_region.end > end_Point:
                        # Weight differently
                        pass
                    
                    # Ok, break.
                    break
                
                # Special case of the first point and more than one point
                if prev_dataPoint is None:
                    prev_dataPoint = this_dataPoint
                    continue
                
     
                # If we have two points..
                prev_dataPoint_validiy_region_start = prev_dataPoint.validity_region.start
                prev_dataPoint_validiy_region_end   = prev_dataPoint.validity_region.end       
                this_dataPoint_validiy_region_start = this_dataPoint.validity_region.start
                this_dataPoint_validiy_region_end   = this_dataPoint.validity_region.end

                # Set correct limits                
                if prev_dataPoint_validiy_region_start < start_Point:
                    prev_dataPoint_validiy_region_start = start_Point
                if this_dataPoint_validiy_region_start < start_Point:
                    this_dataPoint_validiy_region_start = start_Point              
                if prev_dataPoint_validiy_region_end > end_Point:
                    prev_dataPoint_validiy_region_end = end_Point                            
                if this_dataPoint_validiy_region_end > end_Point:
                    this_dataPoint_validiy_region_end = end_Point   
                
                # Set correct prev_end:
                prev_dataPoint_validiy_region_end = prev_dataPoint_validiy_region_end if  this_dataPoint_validiy_region_start > prev_dataPoint_validiy_region_end else this_dataPoint_validiy_region_start
                
                # Set correct weight
                if this_dataPoint_validiy_region_start < prev_dataPoint_validiy_region_end: # gt is correctly handled
                    #case='A'
                    prev_weight = (this_dataPoint_validiy_region_start.operation_value - prev_dataPoint_validiy_region_start.operation_value) # ..Sub is not?
                else:
                    #case='B'
                    prev_weight = (prev_dataPoint_validiy_region_end.operation_value - prev_dataPoint_validiy_region_start.operation_value)
                    
                if prev_weight<0:
                    # This happens in case the prev point is not contained at all (including the validity region) in the current slot.
                    # Set prev_weight= 0 to skip the point. TODO: improve this part
                    prev_weight = 0
                    
                    # DEBUG of the above
                    #print 'case:', case
                    #print 'this_dataPoint_validiy_region_start.operation_value', this_dataPoint_validiy_region_start.operation_value
                    #print 'prev_dataPoint_validiy_region_start.operation_value', prev_dataPoint_validiy_region_start.operation_value 
                    #print 'prev_dataPoint_validiy_region_end.operation_value', prev_dataPoint_validiy_region_end.operation_value      
                    #for point in dataSeries:
                    #    print point
                    #    print point.validity_region.start
                    #    print point.validity_region.end  
                    #raise ConsistencyException('Got negative weight: {}. Boundary conditions: prev_dataPoint={}, this_dataPoint={}'.format(prev_weight, prev_dataPoint, this_dataPoint))
                
                # Compute
                sum += ( prev_weight * prev_dataPoint.data.operation_value )
                
                # Reassign
                prev_dataPoint = this_dataPoint
          
            else:
                sum += this_dataPoint.data.operation_value
    
        if weighted:
            # Last step in case of no 'next' point:
            if prev_weight is not None and prev_dataPoint.Point_part <= end_Point:
                
                # Set correct limits                
                if prev_dataPoint_validiy_region_start < start_Point:
                    prev_dataPoint_validiy_region_start = start_Point
                if this_dataPoint_validiy_region_start < start_Point:
                    this_dataPoint_validiy_region_start = start_Point              
                prev_weight = (prev_dataPoint_validiy_region_end.operation_value - prev_dataPoint_validiy_region_start.operation_value)
                
                # Set and add sum
                prev_value  = this_dataPoint.data.operation_value
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











