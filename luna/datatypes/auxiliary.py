from luna.common.exceptions import InputException

#----------------------------------------
#    Region Types 
#----------------------------------------


class RegionType(object):
    
    def __eq__(self, other):
        return (self.name == other.name)

    def __ne__(self, other):
        return (self.name != other.name)

    def __init__(self, name):
        if not name:
            raise InputException('{} requires a (unique) name'.fomat(self))
        self.name = name

    def __repr__(self):
        return '{} of {}'.format(self.__class__.__name__, self.name)


    def validate_anchor(self, anchor):
        return True
        #raise NotImplementedError('This is an abstract method, you hwave to implement it!')

    def validate_orientation(self, anchor):
        return True
        #raise NotImplementedError('This is an abstract method, you hwave to implement it!')


#----------------------------------------
#    Slot Types 
#----------------------------------------


  
class SlotType(RegionType):

    def get_end(self, start):
        raise NotImplementedError

    def rebase(self, point):
        raise NotImplementedError

    def navigate(self, point, shift):
        raise NotImplementedError



class TimeSlotType(SlotType):
    
    labels='t'
    
    def __init__(self, *args, **kwargs):        
        super(TimeSlotType, self).__init__(*args, **kwargs)
        from luna.spacetime.time import TimeInterval
        self.timeInterval = TimeInterval(self.name)
    
    def get_end(self, start):
        from luna.datatypes.dimensional import TimePoint
        return TimePoint(t=self.timeInterval.shift_dt(start.dt, times=1))

    def rebase(self, point):
        from luna.datatypes.dimensional import TimePoint
        return TimePoint(t=self.timeInterval.floor_dt(point.dt))



# TODO: understand how to navigate a slot. Does it make sense? Do we need a pointer or something?
#    def navigate(self, point, shift):
#        from luna.datatypes.dimensional import TimePoint
#        return TimePoint(self.old_timeSlot.rebase_date(point.dt, shift=shift))
            

class SurfaceSlotType(SlotType):
    pass
    
class SpaceSlotType(SlotType):
    pass
    

#----------------------------------------
#    Sensors
#----------------------------------------

# SensorTypes as object with inheritance..?
 
class SensorType(object):
 
    def __init__(self, name, datatype):
        self.id = id
        self.datatype = datatype
     
    def aggregate(self):
        pass
     
    def _aggregate(self, data):
        self.aggregate()
        # Check that proper aggregated_labels were produced
         
     
 
class Sensor(object):
     
    def __init__(self, id, type):
        self.id   = id
        self.type = type
     
     
class TemperatureSensorType(SensorType):
    
    def aggregate(self, timeSeries):
        pass
 
 
 
 
    
#-------------------------------
#   Interval (deprecated)
#-------------------------------

# NOTE: dimensional data on the dimensions shoudl accept int, float or intervals?
class Interval(object):
    '''An interval is has a start, and end and a duration. It is referred to a dimension, therefore it is basically an int or a float.
    In its basic implementation it is nothing more than this'''
    
    # Maybe just say that this is a duration and not a interval in the mathematic connotation?
    
    def __init__(self, duration=None, start=None, end=None):
        self.start = start # hmm
        self.end = end     # hmm
        self.duration = duration

class RelativeInterval(Interval):
    pass

class FloatingInterval(object):
    pass

class Interval1(FloatingInterval):
    pass



















    
