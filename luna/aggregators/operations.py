
from luna.datatypes.composite import DataTimeSeries

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
        for item in dataSeries:
            try:
                # TODO: weight the average accoridng to the time interval between points.
                # Also, operations should be aware of prev and next datapoints.
                
                item.validity_region.valid_until
                item.validity_region.valid_from
                sum += item.data.operation_value
                
            except AttributeError:
                sum += item.data.operation_value
    
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











