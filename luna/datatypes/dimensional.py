
from luna import PERFORMANCE_TIPS_ENABLED
from luna.spacetime.time import timezonize, dt_from_t, s_from_dt
from luna.common.exceptions import InputException, ConsistencyException
from datetime import datetime
from luna.datatypes.auxiliary import SlotType, TimeSlotType, SurfaceSlotType, SpaceSlotType
from luna.datatypes.adimensional import PhysicalQuantity
from luna.datatypes.auxiliary import Interval

from luna.datatypes.auxiliary import RegionType
from luna.datatypes.auxiliary import SlotType
from luna.datatypes.auxiliary import TimeSlotType

# Logger
import logging
logger = logging.getLogger(__name__)


# NOTE (notation)
# time (t) is ALWAYS seconds, according to SI.
# datetime (dt) is the representation of time according to the human being.
# datetimes without a timezone are NOT allowed.


#--------------------------------
#  Base class
#--------------------------------

# Base class to handle all dimensional (labels/values) object
class Base(object):

    def __init__(self, **kwargs):

        # Trust me switch
        trustme = kwargs.pop('trustme', False)
 
        # Consistency checks        
        if not trustme:

            # Check that no more (not handled) args are left in the kwargs:
            if len(kwargs) != 0:
                raise InputException('{}: Unhandled args: {}'.format(self.classname, kwargs))

    # Who we are, do we have labels?
    @property 
    def has_labels(self):
        try:
            return self._has_labels
        except AttributeError:
            self._has_labels = True if hasattr(self, 'labels') else False
            return self._has_labels

    # Who we are, do we have values?
    @property 
    def has_values(self):
        try:
            return self._has_values
        except AttributeError:
            self._has_values = True if hasattr(self, 'values') else False
            return self._has_values


    # String representation
    def __repr__(self):
        repr_str = self.classname
        
        if self.has_labels:
            repr_str += ', labels: {}'.format(self.labels)

        if self.has_values:
            repr_str += ', values: {}'.format(self.values)
        
        return repr_str

    # Euqality 
    def __eq__(self, other):
        if (self.has_labels and self.has_values):
            return ((self.labels == other.labels) and (self.values == other.values))
        elif self.has_labels:
            return (self.labels == other.labels)   
        elif self.has_values:
            return (self.values == other.values)
        else:
            raise ConsistencyException('I have no values and no labels, my equality is not defined.')

    # Un-equality
    def __ne__(self, other):
        return (not self.__eq__(other))
            
    # Compatibility check for labels
    def _labels_are_compatible_with(self, other, raises=False):
        # TODO: catch attribute errors?
        if self.labels != other.labels:
            if raises:
                comp_str = ''
                for i in range(len(self.labels)):
                    comp_str += str(self.labels[i]) + ' (' + str(type(self.labels[i])) + '), '
                comp_str = comp_str[:-2]
                comp_str += ' <-- Vs --> '
                for i in range(len(other.labels)):
                    comp_str += str(other.labels[i]) + ' (' + str(type(other.labels[i])) + '), ' 
                comp_str = comp_str[:-2]
                    
                raise InputException("{}: Error, my labels are not compatible with labels I got: {}".format(self.classname, comp_str))
            return False
        else:
            return True        

    # Compatibility check for values
    def _values_are_compatible_with(self, other, raises=False):
        # TODO: catch attribute errors?
        if len(self.values) != len(other.values):
            if raises:
                raise InputException('Error, my values have a different lenght than the other element values I got.')
            return False
        else:
            return True

    # Compatibility check 
    def is_compatible_with(self, other, raises=False):
        '''Check compatibility with 'dimensional' objects (Spaces, Coordintaes, Regions, Points, Slots...).'''
        
        if self.has_labels and self.has_values:
            return (self._labels_are_compatible_with(other, raises=raises) and self._values_are_compatible_with(other, raises=raises))  
        elif self.has_labels:
            return (self._labels_are_compatible_with(other, raises=raises))
        elif self.has_values:
            return (self._values_are_compatible_with(other, raises=raises))
        else:
            raise ConsistencyException('I have no values and no labels, my compatibility is not defined.')        


    # Valuesdict
    @property 
    def valuesdict(self):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access valuesdict since we do not have both labels and values')
            
        class ValuesList(list):  
            def set_linked(self, linked):
                self.linked = linked
                return self
            def __getattr__(self, attr):
                try: 
                    return self.linked.values[self.linked.labels.index(attr)]    
                except ValueError:
                    raise ValueError('{} has no label named "{}"'.format(self.linked.__class__.__name__, attr))
            # TODO: be able to access values['x']

        return ValuesList(self._values).set_linked(self)


    # Content
    @property
    def content(self):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access content since we do not have both labels and values')
        
        class Content(object):    
            def __init__(self, linked):
                self.linked = linked
            def __getattr__(self, attr):
                return self.linked.values[self.linked.labels.index(attr)]
        
        return Content(linked=self)   

    # Utilites
    @property
    def valuesbylabel(self):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access valuesbylabel since we do not have both labels and values')
        
        return self.valuesdict

    def valueforlabel(self, label):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access valueforlabel since we do not have both labels and values')
        
        return self._values[self._labels.index(label)]

    @property
    def classname(self):
        return self.__class__.__name__



#--------------------------------
#  Diemnsional objects
#--------------------------------

class Space(Base):
    '''A Space. It is defined by it dimensions labels cardinality and names'''

    def __init__(self, **kwargs):
   
        # Set attributes
        self._labels = kwargs.pop('labels', [])

        # Trustme swithch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Consistency checks
        if not trustme:
            
            # Check that labels are set       
            if not self._labels:
                raise InputException('{}: Got No labels'.format(self.classname))
    
        # Call parent init
        super(Space, self).__init__(**kwargs)
                
    # Labels property    
    @property
    def labels(self):
        return self._labels


class Coordinates(Base):
    '''A coordinates list. If contextualized in a Space with labels, each coordinate will also have its own label and it will be accessible by label.
    Inpractical terms, by "contextualized in a Space" means to extend a Space object or to be base classes together with a Space object.'''

    def __init__(self, **kwargs):
       
        # Handle arguments
        if ('values' not in kwargs) and ('labels' not in kwargs):
            # Smart init  
            smartinit = True
            _labels = []
            _values = []
             
            for arg in kwargs:
                if arg.startswith('label_'):
                    label_name = arg[6:]
                    _labels.append(label_name)
                    _values.append(kwargs[arg])
             
            if not _values:         
                raise InputException('You are not using the labels/values args but I did not neither find any smart label_ keyword. Got keywords: {}'.format(kwargs))
             
            # At the end, remove the processed args from the kwargs:
            for label in _labels:
                kwargs.pop('label_'+label)
            
            # Assign the values to this object..
            self._values = _values
            
            # ..and add back the labels into the kwargs (in caso of an overddie, it is fine)
            kwargs['labels'] = _labels
            
            # Warn for  performance at the end
            if PERFORMANCE_TIPS_ENABLED:
                logger.info("You are initializing DimensionalData without labels but using smart inits. This slows down, use labels and values.") 

        else:
            smartinit = False       
            # Set values
            self._values = kwargs.pop('values', [])
            if not isinstance(self._values,list):
                raise InputException('I got values which are not a list (got "{}" of type "{}")'.format(self._values, type(self._values)))

        # Check that values have been set somehow
        if not self.values:
            raise InputException('{}: Got No values'.format(self.classname))

        # Call parent constructor
        super(Coordinates, self).__init__(**kwargs)

        # Trick to bypass the impossibility of popping the 'label' kwarg from the Space object init
        # http://stackoverflow.com/questions/8972866/correct-way-to-use-super-argument-passing     
        if self.has_labels:
            kwargs.pop('labels', None)
        
        # Trustme swithch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Consistency checks
        if not trustme:

            # Check that values are set       
            if not self._labels:
                raise InputException("Got no values")

            # If we are contextualized into a Space we have labels check their consistency        
            if self.has_labels and not smartinit:
                
                # Check for Labels and Values of same lenght is smart inti was not used 
                if len(self._labels) != len(self._values):
                    raise InputException("labels and values have different lenght, got labels={} and values={}".format(self._labels, self._values))
               
            # Check for int or float type of the values
            for i, item in enumerate(self._values):
                if not (isinstance(item, int) or isinstance(item, float)):
                    raise InputException('Wrong data of type "{}" with value "{}" in dimension with label "{}", only int and float types are valid values for DimensionalData'.format(type(item), item, self._labels[i]))

    # Values property
    @property
    def values(self):
        return self._values


class Point(Coordinates, Space):
    '''A point in a n-dimensional space with some coordinates'''
    
    def __init__(self, *args, **kwargs):
        
        # Validity slot of the point
        self.validity_interval = kwargs.pop('validity_interval', None)
        
        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Consistency checks
        if not trustme:     
            if self.validity_interval and not isinstance(self.validity_interval, Interval):
                raise InputException('Point validty interval must be a Interval, got {}'.format(type(self.validity_interval)))

        super(Point, self).__init__(*args, **kwargs)


class Region(Space):
    '''A Region in a n-dimensional space. It can be both floating or anchored. Type is mandatory.'''

    # Equality to take into account the type and if the Region is anchored or not
    def __eq__(self, other):
        # Check equality on type
        if self.type or other.type:
            if self.type != other.type:
                return False    
        # Check equality on anchor 
        if self.anchor or other.anchor:
            if self.anchor != other.anchor:
                return False    
        return super(Region, self).__eq__(other)

    # Un-equality not necessary, inherits from the Base
    #def __ne__(self, other):
    #    return (not self.__eq__(other))

 
    def __init__(self, *args, **kwargs):

        # Region type (i.e. 2x4, or 4x8, or 15d, or 124s, or just 3 in case of a sphere)
        self.type  = kwargs.pop('type', None)

        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Consistency checks
        if not trustme:     

            # TODO: Support regions without a type?
            if not self.type:
                raise InputException('{}: The "type" attribute is required.'.format(self.classname))
            else:
                assert isinstance(self.type, RegionType), "Region type not of RegionType instance"
                
            if not 'anchor' in kwargs and not 'labels' in kwargs:
                raise InputException('You need to privide me an anchor or the labels of the space where I will live in')

        # Anchor & orientation
        self.anchor_to(kwargs.pop('anchor', None), kwargs.pop('orientation', None), trustme=trustme)

        if self.anchor and 'labels' in kwargs:
            if not trustme:
                # Check consistency between anchor and labels
                assert (self.anchor.labels == kwargs['labels'])
                
        if self.anchor and 'labels' not in kwargs:
            kwargs['labels'] = self.anchor.labels

        super(Region, self).__init__(*args, **kwargs)

    # Function to anchor a floating Region
    def anchor_to(self, anchor=None, orientation=None, trustme=False):
        if hasattr(self, 'anchor') and self.anchor:
            raise InputException('{} is already anchored (to {})'.format(self.classname, self.anchor))
        if hasattr(self, 'orientation') and self.orientation:
            raise ConsistencyException('{} has no anchor but orientation?! (orientation = {})'.format(self.classname, self.orientiation))
        
        self.anchor = anchor
        self.orientation = orientation    

        if not trustme:
            if self.anchor:
                assert (isinstance(self.anchor, Point)), 'Given nchor is not of type Point, got {}'.format(type(self.anchor))
            
            if hasattr(self, 'labels'):
                # Check consisteny between my labels and anchor labels
                if self.anchor.labels != self.labels:
                    raise InputException('{} my anchor labels ({}) are different than my already set labels ({})'.format(self.classname, self.anchor.labels, self.labels))
                
            self.type.validate_anchor(self.anchor)               # Not sure, anchor lives int he same space in which the region lives so validation shoudl be automatic
            self.type.validate_orientation(self.orientation)     # Actually, the question is: Does this type know how to anchor to this anchor? i.a. A TimeSLotType cannot anchor ina  3d space.
            

            

class Slot(Region):
    '''A slot in a n-dimensional space, with a start and an end. It is a region wth a hyperectangular shape.
    - Start and end must be Points referred to the space where the slot lives in.
    - The slot is always left included, right excluded. kwargs: start, end, type, args are the same in the same order.
    - The type of a slot is not mandartory in case you set the end, but it will be anyway created as there cannot be a slot without a type'''
    
    default_SlotType = SlotType
    default_SlotType_unit = ''

    def __init__(self, *args, **kwargs):

        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        if not trustme:
            # Quick sanity checks. We allow a slot without a start, as it is basically a floating region.
            # We also allow to set at build time start and end and let type be derived accordingly.
            if 'type' not in kwargs:
                if ('start' not in kwargs) or ('end' not in kwargs):
                    raise InputException('{}: type not set and not start-end given.'.format(self.classname))


        # If start is set it becomes the anchor of the slot region
        start = kwargs.pop('start', None)
        if start:
            assert isinstance(start, Point), "Slot start not of Point instance"                
            kwargs['anchor'] = start

        # End is handled by a property
        end = kwargs.pop('end', None)
        self._end = end
        if end:
            assert isinstance(self._end, Point), "Slot end not of Point instance"
        
        # If end is given, check compatibility between start and end
        if not trustme and start and end:
            start.is_compatible_with(end, raises=True)                
        
        # If we have no type, we set it anyway by using start and end. Note: ath this stage we have only the self.end and the start, not the self.end.
        if start and end and 'type' not in kwargs:
            type_derived = True
            if len(start.values) == 1:
                kwargs['type'] = self.default_SlotType( str((end.values[0] - start.values[0])) + self.default_SlotType_unit)
            else:
                kwargs['type'] = self.default_SlotType( str(start.values) + ' - ' + str(end.values) + self.default_SlotType_unit)
        else:
            type_derived = False        

        # Call DimensionalData constructor
        super(Slot, self).__init__(*args, **kwargs)
        
        # Consistency checks
        if not trustme: 
             
            # If both end and type are set, check consistency
            if end and not type_derived:
                obtained_end = kwargs['type'].get_end(start=start)
                if self._end and (self._end != obtained_end):
                    raise InputException("Error: inconsistent start-end-type ({}, {}, {}), expected end based on type is {}".format(start, self._end, kwargs['type'], kwargs['type'].get_end(start=start)))
                         
            # Check that start is before end
            if type_derived:
                for i in range(len(self.start.values)):
                    if not self.start.values[i] < self.end.values[i]:
                        raise InputException('{}: Start equal or after end on dimension #{}'.format(self.classname,i))
                

    # Handle end 
    @property
    def end(self):
        if not self.start:
            return None
        
        if self._end:
            return self._end
        else:
            # Cache it...
            self._end = self.type.get_end(start=self.start)
            return self._end

    # The anchor is the start
    @property
    def start(self):
        return self.anchor

    @property
    def deltas(self):
        return [ (self.end.values[i] - self.start.values[i]) for i in range(len(self.start.values))]


#-------------------
# Specializations
#-------------------

# A) Places in a n-dimensional space

class TimePoint(Point):
    ''' A point in a 1-dimensional space, the time.'''
       
    
    def __init__(self, *args, **kwargs):

        # Handle timezone. If no timezone is given, no timezone is storead and UTC is assumed
        if 'tz' in kwargs:
            
            # Validate timezone
            timezonize(kwargs['tz'])

            # For now, we store the timezone as String. Beacause it is easier and:         
            # sys.getsizeof(timezonize('UTC')) -> 64 bytes
            # sys.getsizeof(chronos.timezonize('Europe/Rome')) -> 64 bytes
            # sys.getsizeof('Europe/Rome') -> 48 bytes
            # sys.getsizeof('UTC') -> 40 bytes
            # sys.getsizeof('America/Argentina/ComodRivadavia') -> 69 bytes
            #
            # The next step is to enumerate timezones from the pytz package, i.e.
            # http://stackoverflow.com/questions/13866926/python-pytz-list-of-timezones
            # and then of course: sys.getsizeof(1) -> 24 Bytes (Python uses float double precision everywhere..)
            
            self._tz = kwargs.pop('tz')
            
        try:
            kwargs['values'] = [kwargs.pop('t')]
            kwargs['labels'] = ['t']
        except KeyError:
            pass

        if ('values' not in kwargs) or (not kwargs['values']):
            raise InputException('Got no values at all. My kwargs: {}'.format(kwargs))

        # Convert datetime to seconds in case:
        t = kwargs['values'][0]
        if isinstance(t, datetime):
            if PERFORMANCE_TIPS_ENABLED:
                logger.info("You are initializing a TimePoint with a DateTime, this is not performant, use int/float epoch")       

            # Get timezone from the DatetTime if any, and if not already set explicitly with tz arg, use it as reference tz
            if t.tzinfo:
                tz = str(t.tzinfo) 
                try:
                    _ = self._tz
                except AttributeError:
                    self._tz = tz
            # Set internal epoch timestamp    
            t = s_from_dt(t)

        # Prepare args and kwargs for Point constructor
        kwargs['values'] = [t]
        kwargs['labels'] = ['t']

        # Call Point init
        super(TimePoint, self).__init__(*args, **kwargs)
        
        # Ensure labels=["t"]
        assert(self.labels==['t'])
        assert(len(self.values)==1)


    # Shortcut for accessing the time dimension:
    @property
    def t(self):
        return self.values[0]




    def __repr__(self):
        return '{} ({})'.format(self.classname, self.dt)
 

    @property
    def dt(self):
        return dt_from_t(self.t, self.tz)

    @property
    def tz(self):
        try:
            return self._tz
        except AttributeError:
            return 'UTC'


class SurfacePoint(Point):
    '''Point in a 2-dimesnioanl space, the surface.'''
      
    # Ensure labels=["x","y","z"]
    def __init__(self, *argv, **kwargs):
        assert(self.labels==["x","y"])
        super(SpacePoint, self).__init__(*argv, **kwargs)    


class SpacePoint(Point):
    '''Point in a 3-dimesnioanl space, the space.'''
      
    # Ensure labels=["x","y","z"]
    def __init__(self, *argv, **kwargs):
        assert(self.labels==["x","y","z"])
        super(SpacePoint, self).__init__(*argv, **kwargs)    


class TimeSlot(Slot):
    '''A slot in a 1-dimensional space, the time.
    If the type is set, the start and end has to be rounded to the time artithmetic since epoch, i.e. with a 1 hour TimeSlotType start and end must start at 0 minutes and 0 seconds.
    If the type is set, the end can be automatically computed.
    '''
 
    default_SlotType = TimeSlotType
    default_SlotType_unit = 's'
        
    # Ensure start,end = TimePoint()
    def __init__(self, *args, **kwargs):
        
        # Handle a floating TimeSlot. The Slot (actually, the Region) an anchor (if not floating) 
        # or the labels of the space where it will live in (if floating)
        if 'start' not in kwargs:
            kwargs['labels'] = 't'
        
        super(TimeSlot, self).__init__(*args, **kwargs)
        
        # Checks
        if self.start: assert(isinstance(self.start, TimePoint))
        if self.end: assert(isinstance(self.end, TimePoint))
        if self.type: assert(isinstance(self.type, TimeSlotType))
        
    def __repr__(self):
        return '{}: from {} to {} with {}'.format(self.classname, self.start.dt, self.end.dt, self.type)
 
    @property
    def tz(self):
        # Timezone is taken from the start
        return self.start.tz


class SurfaceSlot(Point):
    '''A slot  in a 3-dimensional space, the space.'''

    # Ensure start,end = SpacePoint()
    def __init__(self, *argv, **kwargs):
        
        super(SpaceSlot, self).__init__(*argv, **kwargs)
        
        # Checks
        assert(isinstance(self.start, SurfacePoint))
        if self._end: assert(isinstance(self.end, SurfacePoint))
        if self.type: assert(isinstance(self.type, SurfaceSlotType))

class SpaceSlot(Point):
    '''A slot  in a 3-dimensional space, the space.'''

    
    def __init__(self, *argv, **kwargs):
        
        super(SpaceSlot, self).__init__(*argv, **kwargs)
        
        # Checks
        assert(isinstance(self.start, SpacePoint))
        if self._end: assert(isinstance(self.end, SpacePoint))
        if self.type: assert(isinstance(self.type, SpaceSlotType))






#---------------------------------------------
# Physical quantities
#---------------------------------------------

class PhysicalSpace():
    '''A space where phisical data lives in. Labels must be:
         a) PhysicalQuantity objects, or
         b) valid string representations of physical quantities (according to PhysicalQuantity objects)
         
         PhysicalDataPoint != DataPhysicalPoint
         '''
    
class PhysicalData(Coordinates, Space):
    '''Dimensional data where the labels must be:
         a) PhysicalQuantity objects, or
         b) valid string representations of physical quantities (according to PhysicalQuantity objects)'''

    def __init__(self, *argv, **kwargs):  
        super(PhysicalData, self).__init__(*argv, **kwargs)
        
        # NOTE! ! The following is just a check. A nicer approach could be to use  PhysicalQuantities as labels,
        # but they would be havier. On the other hand, storing string representatiosn means
        # that every time you want to obtain info from a phyisical quantity you must instantiate 
        # a PhyisicalQuantity object: what is better, initialize n timees (using the regexs in PhyisicalQuantity)
        # ore initiliaze once and store? TODO: Perform some real-world test ina  TimeSeries.
        
        # Anyway: you are free to instantiate a PhysicalDimensionalData ubject using PhysicalQuantity objects as labels.
        # It is up to you and your use case to decide if to use string representations or PhysicalQuantity objects! 
        
        # ALSO, taken form from old PhysicalDataPoint: Lazy phyisicalquantity? i.e. use the regex only if accessing what it requires
        # to be applied? In this case, it would be just a 'decorator' over the string which activates in case of necessity.
        # But in this approach PhyisicalQuantity should extend strings. Check!
        # TODO: imporve? Implement LazyPhysicalQuantity properly? 
        #if self.data.labels and not isinstance(self.data.labels[0], PhysicalQuantity):
        #    self.data.labels = [LazyPhysicalQuantity(label) for label in self.data.labels] 
        
        for item in self.labels:
            if not isinstance(item, PhysicalQuantity): 
                _ = PhysicalQuantity(item)  
    
    def __repr__(self):
        return '{}, labels: {}, values: {}'.format(self.classname, self.labels, self.values)

















