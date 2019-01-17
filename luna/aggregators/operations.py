from luna.datatypes.dimensional import DataTimeSeries
from luna.common.exceptions import ConsistencyException
from luna.aggregators.utilities import clean_and_reconstruct

# Logger
import logging
logger = logging.getLogger(__name__)


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
        
        # Support vars
        sum = 0.0
        
        logger.debug('')
        logger.debug('====================================  START  =====================================')
        logger.debug('from: {}'.format(start_Point.dt))
        logger.debug('to:   {}'.format(end_Point.dt))
        
        # Support vars
        start_Point_t   = start_Point.t # start_Point.operation_value works as well (why?)
        end_Point_t     = end_Point.t   # end_Point.operation_value works as well (why?)
        start_Point_dt  = start_Point.dt
        end_Point_dt    = end_Point.dt
        weighted        = None
        operation_label = None
        slot_lenght_t   = end_Point.t - start_Point.t
        slot_value_weighted = 0
        
        # A couple of checks based on the first point
        # TOOD: can we have a time series with mixed point with validty regions and no? If s, this check is weak.
        for this_dataPoint in dataSeries:
            
            # Set operation_label
            operation_label = this_dataPoint.data.lazy_filter_label
            
            # Set if weighetd avg or not
            if weighted is None:
                try:
                    this_dataPoint.validity_region
                    weighted = True
                except AttributeError:
                    weighted = False
            break
        
        #=============================
        # Not Weighted
        #=============================
        if not weighted:    
            for this_dataPoint in dataSeries:
                sum += this_dataPoint.data.operation_value
            return sum/len(dataSeries)


        #=============================
        # Weighted
        #=============================
        logger.debug(dataSeries)
        
        cleaned_dataSeries = clean_and_reconstruct(dataSeries, start_Point_dt, end_Point_dt)

        for subslot in cleaned_dataSeries:
            logger.debug('    {}'.format(subslot))
            
            subslot_lenght_t = (subslot.end-subslot.start).t
            subslot_value_weighted = subslot.data[operation_label] * subslot_lenght_t 
            
            logger.debug('      subslot_lenght_t:       {}'.format(subslot_lenght_t))
            logger.debug('      subslot.data[label]:    {:.20f}'.format(subslot.data[operation_label]))
            logger.debug('      subslot_value_weighted: {:.20f}'.format(subslot_value_weighted))
            
            slot_value_weighted += subslot_value_weighted 

        slot_value = slot_value_weighted / slot_lenght_t
        logger.debug('   ----------------------->  {:.20f} '.format(slot_value))
        
        logger.debug('====================================  END  =====================================')
        
        return slot_value




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











