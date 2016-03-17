from luna.common.exceptions import InputException

#----------------------------------------
#    Region Spans
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
    
    def __init__(self, *args, **kwargs):
        
        trustme = kwargs.pop('trustme', False)
        
        # Set value
        self.value = kwargs.pop('value', None)
        
        if self.value is None:
            raise InputException('{}: a value is mandatory'.format(self.__class__.__name__))
 
        # Do we have args or kwargs left?
        if args:
            raise InputException('{}: some args are left: {}'.format(self.__class__.__name__, args))
        if kwargs:
            raise InputException('{}: some kwargs are left: {}'.format(self.__class__.__name__, kwargs))       
        
    # Representation
    def __repr__(self):
        return '{} of value: {}'.format(self.__class__.__name__, self.value)
    
#     @property
#     def value(self):
#         try:
#             return self.value
#         except AttributeError:
#             raise NotImplementedError('{}: You cannot use a Span without implementing it (self.value not found)'.format(self.__class__.__name__))

    # Get start/end
    def get_start(self, end):
        raise NotImplementedError('You cannot use all Span functions without fully implementing it (get_start() not found)')
    
    def get_end(self, start):
        raise NotImplementedError('You cannot use all Span functions without fully implementing it (get_end() not found)')
    
    # Equality 
    def __eq__(self, other):
        return (self.value == other.value)

    # Un-equality
    def __ne__(self, other):
        return (not self.__eq__(other))

    # Symmetry
    @property
    def is_symmetric(self):  
        raise NotImplementedError('{}: You cannot use all Span functions without fully implementing it (self.is_symmetric property not found)'.format(self.__class__.__name__))



class SlotSpan(Span):
    '''A Slot Span is basically a unit for defining the "length" of an hyper-rectangle: the Slot (or interval).
    In practice, this class of objects allows to measure the "length" of a segment, an area, a volume (depending
    on the space in which it lives in). Since the Slot (interval) has a start and an end, which are the vertex
    Points of minimum and maximum, the natural definition of the Span for the Slot is the distance, on each
    dimension, of the end from the start. The value of the span is therefore the deltas.
    
    You can initialize the SlotSpan giving just the value, or the start-end vertexes.
    '''
    
    def __init__(self, *args, **kwargs):   
        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False
        
        # TODO: values -> deltas?
        
        # Values in the kwargs 
        start = kwargs.pop('start', None)
        end   = kwargs.pop('end', None) 
        
        # A slot Span does not require a start and an end, but they can be used to compute the span itself.
        # In practice, you need or start-end or the span value.
        
        # If we do not have the value, let's compute it from start-end
        if ('value' not in kwargs) or  ('value' in kwargs and kwargs['value'] is None):
            if start is None or end is None:
                raise InputException('If you do not provide the value, you must provide the start and the end')
            else:
                kwargs['value'] = [value for value in (end - start).values]
                
        # Cheks to perform if we have the value 
        else:
            if not trustme:
                
                # The slot value must be a list of floating points
                if not isinstance (kwargs['value'], list):
                    raise InputException('{}: my value must be a list of floating. Got "{}" ({})'.format(self.__class__.__name__, type(kwargs['value']), kwargs['value']))
                
                
                #Check that no start-end has been provided (for consistency)
                if start or end:
                    raise InputException('If you provide the value you cannot provide the start or the end')
            
        # Call parent Init    
        super(SlotSpan, self).__init__(*args, **kwargs)


    # Handle symmetry property
    @property
    def is_symmetric(self):   
        first_value = None
        for value in self.value:
            if first_value is None:
                first_value = value
                continue
            else:
                if first_value != value:
                    return False            
        return True



#----------------------------------------
#    Region Shapes
#----------------------------------------


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



#----------------------------------------
#    Sensors
#----------------------------------------

# TODO: SensorTypes as object with inheritance..?
 
class SensorType(object):
 
    def __init__(self, name, datatype):
        self.id = id
        self.datatype = datatype
     
    def aggregate(self):
        pass
     
    def _aggregate(self, data):
        self.aggregate()
        # TODO: Check that proper aggregated_labels were produced
         
     
 
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




















    
