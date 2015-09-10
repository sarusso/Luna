from luna.datatypes.dimensional import PhysicalDimensionalData, TimePoint
from luna.datatypes.composite import TimeSeries, PhysicalDataTimePoint, PhysicalDataTimeSlot
from luna.storage import Storage



class CassandraStorage(Storage):
    def __init__(self, seeds=None):
        pass
       
    

class TimeSeriesCassandraStorage(CassandraStorage):
    

    def put(self, timeSeries, tid):
        pass
    
    
    def get(self, tid, from_dt, to_dt, timeSlotType=None):
        
        
        #--------------------
        # Super Mock
        #--------------------
        
        if timeSlotType:
            timeSeries = TimeSeries(index=True)
            for i in range(10):
                data = PhysicalDimensionalData( labels = ['temp_C_i_AVG', 'temp_C_i_MIN', 'temp_C_i_MAX'], values = [20.6+i, 20.6+i-1, 20.6+i+1] ) 
                physicalDataTimeSlot = PhysicalDataTimeSlot(start = TimePoint(t=1436022000 + (i*3600), tz="Europe/Rome"), data=data, type=timeSlotType)
                timeSeries.append(physicalDataTimeSlot)
            return timeSeries


            
        else:
            
            timeSeries = TimeSeries()
            for i in range(10*60):
                data = PhysicalDimensionalData( labels = ['temp_C'], values = [20.6+i/10.0] ) 
                physicalDataTimePoint = PhysicalDataTimePoint(t = 1436022000 + (i*60), tz="Europe/Rome", data=data)
                timeSeries.append(physicalDataTimePoint)
            return timeSeries




































