from luna.common.exceptions import InputException

#----------------------------------------
#    Region Shapes / Spans
#----------------------------------------

class Span(object):
    '''A Span: "The full extent of something from end to end; the amount of space that something covers".
    In practice, this class of objects allows to define the "length" of a segment, an area, a volume (depending
    on the space in which it lives in). In other words, spans are used to define the "length" of the Regions.
    They are therefore just an index: in simple regions (like a segment) the distance is used, while in more
    complicated regions (with for example a "cloudy shape") more sophisticated span indexes can be applied.
    In first approximation, however, the span can be always considered to be the hyper-rectangle (or Slot/
    Interval) containing the region. In this case just use the SlotSpan object using the "upper" and the lower
    Points that defines the Slot in which the region is contained.'''
    
    # TODO: In mathematical terms, is a primitive and very wide concept of a "distance". Sure? no,
    # because the distance is a single number while the span can have a number for each dimension.
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return self.name
    
    @property
    def value(self):
        try:
            return self._value
        except AttributeError:
            raise NotImplementedError('You cannot use a Span without implementing it (self._value not found)')

    # Get start/end
    def get_start(self, end):
        raise NotImplementedError('You cannot use a Span without implementing it (get_start() not found)')
    
    def get_end(self, start):
        raise NotImplementedError('You cannot use a Span without implementing it (get_start() not found)')
    
    # Equality 
    def __eq__(self, other):
        return (self._value == other._value)

    # Un-equality
    def __ne__(self, other):
        return (not self.__eq__(other))

class SlotSpan(Span):
    '''A Slot Span is basically a unit for defining the "length" of an hyper-rectangle: the Slot(or interval).
    In practice, this class of objects allows to measure the "length" of a segment, an area, a volume (depending
    on the space in which it lives in). The Slot (interval) has a start and an end, which are the vertex Points of 
    minimum and maxiumim, therefore the natural definition of the span for the slot is the distance, on each
    dimension, of the end from the start.'''
    
    def __init__(self, **kwargs):    
        start = kwargs.pop('start', None)
        end   = kwargs.pop('end', None)
        
        if start is None:
            raise InputException('Start is required')
        if end is None:
            raise InputException('Start is required')
        
        # Compute the value of the span
        self._value = [value for value in (end - start).values]

        # Set name (required by the base class). TODO: does this slows down? Probably yes..
        kwargs['name'] = str(self._value)

        # Call father Init    
        super(SlotSpan, self).__init__(**kwargs)


class RegionShape(object):
    
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
        #raise NotImplementedError('This is an abstract method, you have to implement it!')

    def validate_orientation(self, anchor):
        return True
        #raise NotImplementedError('This is an abstract method, you have to implement it!')


class SlotShape(RegionShape):
    
    def __init__(self, *args, **kwargs):
        kwargs['name'] = 'SlotShape'
        super(SlotShape, self).__init__(*args, **kwargs)


# #----------------------------------------
# #    Slot Types 
# #----------------------------------------
# 
# 
#   
# class SlotType(RegionType):
# 
#     def get_end(self, start):
#         raise NotImplementedError
# 
#     def rebase(self, point):
#         raise NotImplementedError
# 
#     def navigate(self, point, shift):
#         raise NotImplementedError
# 
# 
# 
# class TimeSlotType(SlotType):
#     
#     labels='t'
#     
#     def __init__(self, *args, **kwargs):        
#         super(TimeSlotType, self).__init__(*args, **kwargs)
#         from luna.spacetime.time import TimeSpan
#         self.timeInterval = TimeSpan(self.name)
#     
#     def get_end(self, start):
#         from luna.datatypes.dimensional import TimePoint
#         return TimePoint(t=self.timeInterval.shift_dt(start.dt, times=1))
# 
#     def rebase(self, point):
#         from luna.datatypes.dimensional import TimePoint
#         return TimePoint(t=self.timeInterval.floor_dt(point.dt))



# TODO: understand how to navigate a slot. Does it make sense? Do we need a pointer or something?
#    def navigate(self, point, shift):
#        from luna.datatypes.dimensional import TimePoint
#        return TimePoint(self.old_timeSlot.rebase_date(point.dt, shift=shift))
            

# class SurfaceSlotType(SlotType):
#     pass
#     
# class SpaceSlotType(SlotType):
#     pass
    

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
 


#---------------------------------------------
# Quantities
#---------------------------------------------

class Quantity(object):
    '''A quantity. Must have a name and can have an operation
    associated (i.e. CountedCars, CountedCars_AVG, CountedCars_TOT)'''
    
    # TODO: move he name part here form the PhysicalQuantity
    pass

    separator = '_'


#---------------------------------------------
# Physical  quantities
#---------------------------------------------

class PhysicalQuantity(Quantity):
    '''A physical quantity. Must have a name, a unit of measurement
    and can have an operation associated (i.e. power_W, power_W_AVG, power_W_TOT)''' 
    
    def __repr__(self):
        return '{}'.format(self.string)

    def __eq__(self, other): 
        return self.string == other.string

    def __ne__(self, other): 
        return self.string != other.string
     
    
    def __init__(self, string, trustme=False):
    
        self.string        = string
        self.string_pieces = None
        if not trustme:
            string_pieces = string.split(self.separator)
            
            if  len(string_pieces) == 2:
                # TODO: Validate unit 
                pass
            elif len(string_pieces) == 3:
                # TODO: Validate unit
                # TODO: Validate operator
                pass
            else:
                raise InputException('Wrong PhysicalQuantity name format: {}'.format(string))
    
    @property
    def name(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split(self.separator)
        return self.string_pieces[0]

    @property
    def unit(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split(self.separator)
        return self.string_pieces[1]

    @property
    def op(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split(self.separator)
        if len(self.string_pieces) == 2:
            return None
        else:
            if self.string_pieces[2] == 'INST':
                return None
            else:
                return self.string_pieces[2]
            
    @property
    def name_unit(self):
        return self.name + self.separator + self.unit




















    
