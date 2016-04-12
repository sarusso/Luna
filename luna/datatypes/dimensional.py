
from luna import PERFORMANCE_TIPS_ENABLED
from luna.spacetime.time import timezonize, dt_from_t, s_from_dt, TimeSlotSpan
from luna.spacetime.space import SurfaceSpan, SpaceSpan
from luna.common.exceptions import InputException, ConsistencyException
from datetime import datetime
from luna.datatypes.auxiliary import PhysicalQuantity, Span, SlotSpan

from luna.datatypes.auxiliary import RegionShape, SlotShape

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

# Base class to handle all dimensional (labels/values) object.
# Please not that this is just a "support" class.
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
            self._has_labels = True if hasattr(self, '_labels') else False
            return self._has_labels

    # Who we are, do we have values?
    @property 
    def has_values(self):
        try:
            return self._has_values
        except AttributeError:
            self._has_values = True if hasattr(self, '_values') else False
            return self._has_values


    # String representation
    def __repr__(self):
        repr_str = self.classname
        
        if self.has_labels:
            repr_str += ', labels: {}'.format(self.labels)

        if self.has_values:
            repr_str += ', values: {}'.format(self.values)
        
        return repr_str

    # Equality 
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

    # ..and Un-implement operators which acts on the memory address as are meaningless in this context
    def __gt__(self, other):
        raise NotImplementedError()
    def __ge__(self, other):
        raise NotImplementedError()
    def __lt__(self, other):
        raise NotImplementedError()
    def __le__(self, other):
        raise NotImplementedError()

    # ..and Un-implement iterator
    def __iter__(self):
        raise NotImplementedError('Iterator is not implemented')        
    def __next__(self):
        raise NotImplementedError('Iterator is not implemented')
    def next(self):
        raise NotImplementedError('Iterator is not implemented')
            
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
        if not type(self) is type(other):
            if raises:
                raise InputException('Got incompatible type: I am "{}" and I am not compatible with "{}"'.format(self.classname, other.__class__.__name__))
            else:
                return False
        if self.has_labels and self.has_values:
            return (self._labels_are_compatible_with(other, raises=raises) and self._values_are_compatible_with(other, raises=raises))  
        elif self.has_labels:
            return (self._labels_are_compatible_with(other, raises=raises))
        elif self.has_values:
            return (self._values_are_compatible_with(other, raises=raises))
        else:
            raise ConsistencyException('I have no values and no labels, my compatibility is not defined.')        

    # Class name shortcut
    @property
    def classname(self):
        return self.__class__.__name__


    #-----------------------
    # Content management
    #-----------------------

    # Content object
    @property
    def content(self):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access content since labels and values are not both set')
        # Define content support object
        class Content(object):    
            
            def __init__(self, linked):
                self.linked = linked
            
            def __getattr__(self, attr):
                return self.linked.values[self.linked.labels.index(attr)]
            
            def __getitem__(self, item):
                return self.linked.__getitem__(item)
            
            def __iter__(self):
                self.current = -1
                return self
            
            def __next__(self):
                # TODO: Add filtering here?
                if self.current > len(self.linked.labels)-2:
                    raise StopIteration
                else:
                    self.current += 1
                    return {self.linked.labels[self.current]: self.linked.values[self.current]}
            
            def next(self): # Python 2.x
                return self.__next__()
            
            def __repr__(self):
                return str({label:self.linked.valueforlabel(label) for label in self.linked.labels})  
        
        return Content(linked=self)
    
    # Get item
    def __getitem__(self, label):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access content since we do not have both labels and values')
        try:
            return self._values[self._labels.index(label)]
        except ValueError:
            raise ValueError('{} has no label named "{}"'.format(self.classname, label))

    # Value for label
    def valueforlabel(self, label):
        if not self.has_labels or not self.has_values:
            raise AttributeError('Cannot access valueforlabel since we do not have both labels and values (has_labels={}, has_values={})'.format(self.has_labels, self.has_values))
        try:
            return self._values[self._labels.index(label)]
        except ValueError:
            raise ValueError('{} has no label named "{}"'.format(self.classname, label))


    # Lazy filtering ON
    def enable_lazy_filter_label(self, label):
        self.lazy_filter_label = label

    # Lazy filtering OFF
    def disable_lazy_filter_label(self):
        self.lazy_filter_label = None



#--------------------------------
#  Dimensional objects
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
            
            # Check that labels are set and that they are a list   
            if not self._labels:
                raise InputException('{}: Got No labels'.format(self.classname))
            if not isinstance(self._labels, list):
                raise InputException('{}: Labels are not of type list, got ({})'.format(self.classname, type(self._labels)))
        
        # Call parent Init
        super(Space, self).__init__(**kwargs)
                
    # Labels property    
    @property
    def labels(self):
        try:
            return self._labels
        except AttributeError:
            raise ConsistencyException('{}: No _labels (yet) defined, you hit a bug.'.format(self.__class__.__name__))



class Coordinates(Base):
    '''A coordinates list. If contextualized in a Space with labels, each coordinate will also have its own label and it will be accessible by label.
    In practical terms, by "contextualized in a Space" means to extend a Space object or to be base classes together with a Space object.'''

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
            
            # ..and add back the labels into the kwargs (in case of an override, it is fine)
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
                    raise InputException('Wrong data of type "{}" with value "{}" in dimension with label "{}", only int and float types are valid values for DimensionalData'.format(item.__class__.__name__, item, self._labels[i]))


    # TODO: Maybe would be better to move this one in the base class since it involves filtering against labels?
    
    # Values property
    @property
    def values(self):           
        return self._values

    # Operation value property
    @property
    def operation_value(self):
        try:
            if self.lazy_filter_label:
                return self.valueforlabel(self.lazy_filter_label)
        except AttributeError:
            pass
        
        if len(self._values) > 1:
            raise AttributeError('Sorry, the "value" property is implemented for 1-D Points only (this is a {}-D Point).'.format(len(self._values)))
        return self._values[0]
    

class Point(Coordinates, Space):
    '''A point in a n-dimensional space with some coordinates'''
    
    # Sum and subtraction are defined in the classic, vectorial way.
    
    def __add__(self, other, trustme=False):
        # Check compatibility
        if not trustme:
            self.is_compatible_with(other, raises=True) 
        new_values = []
        for i in range(len(self.values)):
            new_values.append(self.values[i] + other.values[i]) 
        return self.__class__(labels=self.labels, values=new_values)
    
    def __sub__(self, other, trustme=False):
        # Check compatibility
        if not trustme:
            self.is_compatible_with(other, raises=True) 
        new_values = []
        for i in range(len(self.values)):
            new_values.append(self.values[i] - other.values[i]) 
        return self.__class__(labels=self.labels, values=new_values)        

    def __gt__(self, other):
        if len(self.labels)>1:
            raise NotImplementedError('Sorry, <, >, <= and >= operators for the Point are defined in only 1 dimension for now.')
        else:
            return other.values[0] < self.values[0]
          
    def __ge__(self, other):
        if len(self.labels)>1:
            raise NotImplementedError('Sorry, <, >, <= and >= operators for the Point are defined in only 1 dimension for now.')
        else:
            return not self.values[0] < other.values[0]
        
    def __lt__(self, other):
        if len(self.labels)>1:
            raise NotImplementedError('Sorry, <, >, <= and >= operators for the Point are defined in only 1 dimension for now.')
        else:
            return self.values[0] < other.values[0]
        
    def __le__(self, other):
        if len(self.labels)>1:
            raise NotImplementedError('Sorry, <, >, <= and >= operators for the Point are defined in only 1 dimension for now.')
        else:
            return not self.values[0] > other.values[0]

    
class Region(Space):
    '''A Region in a n-dimensional space. It can be both floating or anchored. Shape and Span are mandatory. Anchor is optional'''

    # First of all define if teh Region is symmetric or not. By default it is not.
    is_symmetric = False

    # Equality to take into account the type and if the Region is anchored or not
    def __eq__(self, other):
        # Check equality on shape
        if self.shape or other.shape:
            if self.shape != other.shape:
                return False         
        # Check equality on span
        if self.span or other.span:
            if self.span != other.span:
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

        # Region shape (to be defined using the Shape objects)
        self.shape  = kwargs.pop('shape', None)

        # Region span (i.e. 2x4, or 4x8, or 15d, or 124s, or just 3 in case of a sphere)        
        self.span  = kwargs.pop('span', None)

        # Region anchor
        self.anchor = kwargs.pop('anchor', None)
        
        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Check old init
        if 'orientation' in kwargs:
            raise InputException('{}: sorry, orientation is deprecated'.format(self.classname))

        # Consistency checks
        if not trustme:     

            # Check shape is set and is of the right 
            if not self.shape:
                raise InputException('{}: The "shape" attribute is required.'.format(self.classname))
            else:
                assert issubclass(self.shape, RegionShape), "Region shape not of RegionShape instance"

            # Check span is set
            if not self.span:
                raise InputException('{}: The "span" attribute is required.'.format(self.classname))
            else:
                assert isinstance(self.span, Span), "Region shape not of RegionShape instance"
                
            # Check anchor is set:
            if self.anchor is None:
                raise InputException('{}: The "anchor" attribute is required.'.format(self.classname))
            else:
                assert (isinstance(self.anchor, Point)), 'Given anchor is not of type Point, got {}'.format(type(self.anchor))

        # TODO: avoid saving the labels twice in case of anchor and no labels?
        
        # Check if labels are already set by some child class # TODO: move this in the Space?
        if hasattr(self, '_labels'):
            if 'labels' in kwargs:
                raise InputException('{} sorry, I already have labels set "{}", you cannot give me other ones (I got "{}")'.format(self.classname, self.labels, kwargs['labels']))
            else:
                if self.anchor.labels != self.labels:
                    raise InputException('{}: my anchor labels "{}" are different than my already set labels "{}"'.format(self.classname, self.anchor.labels, self.labels))

       
        else:
            # Otherwise, dynamically set labels from the anchor if they are not provided:
            if 'labels' not in kwargs:
                kwargs['labels'] = self.anchor.labels
    
        # Call parent Init
        super(Region, self).__init__(*args, **kwargs)
    
        if not hasattr(self, '_labels') and 'labels' in kwargs :
            # Check consistency of provided labels and anchor's labels. We do it here to have triggered
            # the validation of the labels in the meanwhile
                if self.anchor.labels != kwargs['labels']:
                    raise InputException('{} my anchor labels "{}" are different than the labels you provided me "{}"'.format(self.classname, self.anchor.labels, kwargs['labels']))

        


            

class Slot(Region):
    '''A Slot is a particular type of region, which has an hyper-rectangular shape.
    It is basically an interval (https://en.wikipedia.org/wiki/Interval_(mathematics)#Multi-dimensional_intervals)
    In addition to the Span (which in this case is a SlotSpan) also start and end are required, and they must be
    Points referred to the space where the slot lives in. You can omit one of the triplet start-end-span and it will
    be automatically computed.
    
    Please not that the slot is always intended to be with left included, right excluded.'''
    
    # Set which Span object to use
    Span_object = SlotSpan

    def __init__(self, *args, **kwargs):

        

        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        if not trustme:
            # Quick sanity checks. We allow a slot without a start, as it is basically a floating region.
            # We also allow to set at build time start and end and let span be derived accordingly.
            if 'span' not in kwargs:
                if ('start' not in kwargs) or ('end' not in kwargs):
                    raise InputException('{}: type not set and not start-end given.'.format(self.classname))


        # Hanlde start - end - anchor Check that we have at least two out of start-end-span
        start  = kwargs.pop('start', None)
        end    = kwargs.pop('end', None)
        span   = kwargs['span'] if 'span' in kwargs else None
        anchor = kwargs['anchor'] if 'anchor' in kwargs else None

        # Consistency checks
        if not trustme: 
            if span:
                assert isinstance(span, Span), "Provided Slot anchor not of Span instance"
            if anchor:
                assert isinstance(anchor, Point), "Provided Slot anchor not of Point instance"
            if start:
                assert isinstance(start, Point), "Provided Slot start not of Point instance"
            if end:
                assert isinstance(end, Point), "Provided Slot end not of Point instance" 
              
        #---------------------------------------
        # 1) Special case: we have the anchor
        #---------------------------------------
        # If so check that no start-end have been provided.
        # Note: start and end are handled by properties!
        if anchor:

            if start is not None or end is not None:
                raise InputException('{}: Sorry, if you directly provide the anchor you cannot provide start or end'.format(self.classname))

            if not span:
                raise InputException('{}: I got the anchor but not the span which is required in this context!'.format(self.classname))
        
        #---------------------------------------
        # 2) Do we have start, end, and span?
        #---------------------------------------
        elif start is not None and end is not None and span is not None:
            
            # Set anchor
            kwargs['anchor'] = span.get_center(start=start)
            
            # Check consistency between the three
            if not trustme:
                if span.get_end(start=start) != end:
                    raise InputException('{}: Error: inconsistent start/end with span (start={}, end={}, span={}), expected end based on span should be {}'.format(self.__class__.__name__, start, end, span, span.get_end(start=start)))


        #---------------------------------------
        # 3) Do we have start and span?
        #---------------------------------------
        elif start is not None and span is not None:
            
            # Set anchor
            kwargs['anchor'] = span.get_center(start=start)
            
        #---------------------------------------
        # 4) Do we have end and span?
        #---------------------------------------
        elif end is not None and span is not None:
            
            # Set anchor
            kwargs['anchor'] = span.get_center(end=end)
        
        #---------------------------------------
        # 5) Do we have only start and end?
        #---------------------------------------
        elif start is not None and end is not None:
            
            if not trustme:
                
                # Compatibility check:
                start.is_compatible_with(end, raises=True)         
                
                # Check that start is before end
                for i in range(len(start.values)):
                    if not start.values[i] < end.values[i]:
                        raise InputException('{}: Start equal or after end on dimension #{}'.format(self.classname,i))

            # If we have no span, we set it anyway by using "start" and "end".
            # "start" and "end" are indeed Points for which the subtraction is defined,
            # and for which the string representation is also defined.
            kwargs['span'] = self.Span_object(start=start, end=end)

            # Set anchor
            kwargs['anchor'] = kwargs['span'].get_center(start=start)
                   
        else:
            raise InputException('{}: Sorry, you have to provide me anchor+span, or start+span, or end+span, or start+end, or start+end+span'.format(self.__class__.__name__))

        # We are a slot, set this shape
        kwargs['shape'] = SlotShape

        # Call Father constructor
        super(Slot, self).__init__(*args, **kwargs)
            
    # Handle end 
    @property
    def end(self):
        if hasattr(self, '_end'):
            return self._end
        else:
            # Cache it...
            self._end = self.span.get_end(center=self.anchor)
            return self._end

    # Handle start 
    @property
    def start(self):
        if hasattr(self, '_start'):
            return self._start
        else:
            # Cache it...
            self._start= self.span.get_start(center=self.anchor)
            return self._start

    # Handle center 
    @property
    def center(self):
        return self.anchor

    # TODO: deltas are an interesting concept, which should be used in the span.
    # Also, here you should just use span.value instad of re-computing them.
    @property
    def deltas(self):
        return [ (self.end.values[i] - self.start.values[i]) for i in range(len(self.start.values))]

    # A slot is symmetric only if its span also is (and therefore the Slot is a n-square).    
    @property
    def is_symmetric(self):
        return self.span.is_symmetric


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
            raise InputException('TimePoint: Got no values at all. My kwargs: {}'.format(kwargs))

        # Convert datetime to seconds in case (TODO# not clean approach at all!! maybe use 'dt' label? Mybe ysut drop support?):
        t = kwargs['values'][0]
        if isinstance(t, datetime):
            if PERFORMANCE_TIPS_ENABLED:
                logger.info("TimePoint: You are initializing a TimePoint with a DateTime, this is not performant, use int/float epoch")       

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
    '''Point in a 2-dimensional space, the surface.'''
      
    # Ensure labels=["x","y","z"]
    def __init__(self, *argv, **kwargs):
        assert(self.labels==["x","y"])
        super(SpacePoint, self).__init__(*argv, **kwargs)    


class SpacePoint(Point):
    '''Point in a 3-dimensional space, the space.'''
      
    # Ensure labels=["x","y","z"]
    def __init__(self, *argv, **kwargs):
        assert(self.labels==["x","y","z"])
        super(SpacePoint, self).__init__(*argv, **kwargs)    


class TimeSlot(Slot):
    '''A slot in a 1-dimensional space, the time. it uses the TimeInterval object from the spacetime package.
    If the type is set, the start and end has to be rounded to the time artithmetic since epoch, i.e. with
    a 1 hour TimeSlotType start and end must start at 0 minutes and 0 seconds. If the type is set, the end 
    can be automatically computed.
    '''
 
    # Set which Span object to use
    Span_object = TimeSlotSpan
        
    # Ensure start,end = TimePoint()
    def __init__(self, *args, **kwargs):
        
        # Define the static labels for this Region (the space where it lives in)
        kwargs['labels'] = ['t']
              
        # Check for correct types. Note that Slot will take care of checking that at least two of the
        # start-end-span are set.
        if 'anchor' in kwargs and not isinstance(kwargs['anchor'], TimePoint):
            raise InputException('{}: provided anchor is not of type TimePoint, got '.format(self.classname), type(kwargs['anchor']))

        if 'start' in kwargs and not isinstance(kwargs['start'], TimePoint):
            raise InputException('{}: provided start is not of type TimePoint, got '.format(self.classname), type(kwargs['start']))

        if 'end' in kwargs and not isinstance(kwargs['end'], TimePoint):
            raise InputException('{}: provided end is not of type TimePoint, got '.format(self.classname), type(kwargs['end']))

        if 'span' in kwargs and not isinstance(kwargs['span'], TimeSlotSpan):
            raise InputException('{}: provided span is not of type TimeSlotSpan, got '.format(self.classname), type(kwargs['span']))
                
        # Call parent Init
        super(TimeSlot, self).__init__(*args, **kwargs)

        
    def __repr__(self):
        # The representation works even if only the span is set. TODO: understand if this is what we want..
        if self.start is not None:
            return '{}: from {} to {} with span of {} and coverage of {}'.format(self.classname, self.start.dt, self.end.dt, self.span, self.coverage)
        else:
            return '{}: with {} and coverage of {}'.format(self.classname, self.span, self.coverage)
 
    @property
    def tz(self):
        # Timezone is taken from the start
        return self.start.tz


class SurfaceSlot(Point):
    '''A slot in a 3-dimensional space, the space.'''

    # Ensure start,end = SpacePoint()
    def __init__(self, *argv, **kwargs):
        
        super(SpaceSlot, self).__init__(*argv, **kwargs)
        
        # Checks
        assert(isinstance(self.start, SurfacePoint))
        if self._end: assert(isinstance(self.end, SurfacePoint))
        if self.span: assert(isinstance(self.span, SurfaceSpan))

class SpaceSlot(Point):
    '''A slot  in a 3-dimensional space, the space.'''

    
    def __init__(self, *argv, **kwargs):
        
        super(SpaceSlot, self).__init__(*argv, **kwargs)
        
        # Checks
        assert(isinstance(self.start, SpacePoint))
        if self._end: assert(isinstance(self.end, SpacePoint))
        if self.span: assert(isinstance(self.span, SpaceSpan))






#---------------------------------------------
# Physical quantities
#---------------------------------------------

class PhysicalSpace(Space):
    '''A space where phisical data lives in. Labels must be:
         a) PhysicalQuantity objects, or
         b) valid string representations of physical quantities (according to PhysicalQuantity objects)
         
         PhysicalDataPoint != DataPhysicalPoint
         '''
    #def __init__(self, *argv, **kwargs):  
    #    super(PhysicalSpace, self).__init__(*argv, **kwargs)

class PhysicalData(Coordinates, PhysicalSpace):
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

















