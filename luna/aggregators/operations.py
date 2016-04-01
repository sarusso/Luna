

class Operation(object):
    
    @staticmethod
    def compute_on_Points(dataSeries, operate_on, start_Point, end_Point):
        raise NotImplementedError()
    
    @staticmethod
    def compute_on_Slots(dataSeries, operate_on, start_Point, end_Point):
        raise NotImplementedError()


class AVG(Operation):
    
    @staticmethod
    def compute_on_Points(dataSeries, operate_on, start_Point, end_Point):
        sum = 0.0
        print 
        for item in dataSeries:
            # TODO: weight the average accoridng to the time interval between points.
            # Also, operations should be aware of prev and next datapoints.
            sum += item.data[operate_on] 
        return sum/len(dataSeries)

    @staticmethod
    def compute_on_Slots(dataSeries, operate_on, start_Point, end_Point):
        return None


class MIN(Operation):

    @staticmethod
    def compute_on_Points(dataSeries, operate_on, start_Point, end_Point):
        min = None
        for dataTimePoint in dataSeries:
            if min is None:
                min = dataTimePoint.data[operate_on]
            elif dataTimePoint.data[operate_on] < min:
                min = dataTimePoint.data[operate_on]
            else:
                pass
        return min

    @staticmethod
    def compute_on_Slots(dataSeries, operate_on, start_Point, end_Point):
        return None


class MAX(Operation):
    
    @staticmethod
    def compute_on_Points(dataSeries, operate_on, start_Point, end_Point):
        max = None
        for item in dataSeries:
            if max is None:
                max = item.data[operate_on]
            elif item.data[operate_on] > max:
                max = item.data[operate_on]
            else:
                pass
        return max

    @staticmethod
    def compute_on_Slots(dataSeries, operate_on, start_Point, end_Point):
        return None











