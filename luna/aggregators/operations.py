

class Operation(object):
    
    @staticmethod
    def compute_on_Points(dataTimeSeries, operate_on, prev_dataTimePoint, next_dataTimePoint, start_dt, end_dt):
        raise NotImplementedError()
    
    @staticmethod
    def compute_on_Slots(dataTimeSeries, operate_on):
        raise NotImplementedError()


class AVG(Operation):
    
    @staticmethod
    def compute_on_Points(dataTimeSeries, operate_on, prev_dataTimePoint, next_dataTimePoint, start_dt, end_dt):
        sum = 0.0
        print 
        for item in dataTimeSeries:
            # TODO: weight the average accoridng to the time interval between points.
            # Also, operations should be aware of prev and next datapoints.
            sum += item.data[operate_on] 
        return sum/len(dataTimeSeries)

    @staticmethod
    def compute_on_Slots(dataTimeSeries, operate_on):
        return None


class MIN(Operation):

    @staticmethod
    def compute_on_Points(dataTimeSeries, operate_on, prev_dataTimePoint, next_dataTimePoint, start_dt, end_dt):
        min = None
        for dataTimePoint in dataTimeSeries:
            if min is None:
                min = dataTimePoint.data[operate_on]
            elif dataTimePoint.data[operate_on] < min:
                min = dataTimePoint.data[operate_on]
            else:
                pass
        return min

    @staticmethod
    def compute_on_Slots(dataTimeSeries, operate_on):
        return None


class MAX(Operation):
    
    @staticmethod
    def compute_on_Points(dataTimeSeries, operate_on, prev_dataTimePoint, next_dataTimePoint, start_dt, end_dt):
        max = None
        for item in dataTimeSeries:
            if max is None:
                max = item.data[operate_on]
            elif item.data[operate_on] > max:
                max = item.data[operate_on]
            else:
                pass
        return max

    @staticmethod
    def compute_on_Slots(dataTimeSeries, operate_on):
        return None











