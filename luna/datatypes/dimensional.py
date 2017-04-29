
from luna import PERFORMANCE_TIPS_ENABLED
from luna.spacetime.time import timezonize, dt_from_t, s_from_dt, TimeSlotSpan
from luna.spacetime.space import SurfaceSpan, SpaceSpan
from luna.common.exceptions import InputException, ConsistencyException
from datetime import datetime
from luna.datatypes.auxiliary import PhysicalQuantity, Span, SlotSpan, RegionSpan

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

            # If we are have both lables and values, check their consistency        
            if self.has_labels and self.has_values:
                if len(self._labels) != len(self._values):
                    raise InputException("labels and values have different length, got labels={} and values={}".format(self._labels, self._values))

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
        if not isinstance(other, self.__class__):
            return False   
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

    # ..and Un-implement iterator to avoid misunderstandings
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
                    comp_str += str(self.labels[i]) + ' (' + str(self.labels[i].__class__.__name__) + '), '
                comp_str = comp_str[:-2]
                comp_str += ' <-- Vs --> '
                for i in range(len(other.labels)):
                    comp_str += str(other.labels[i]) + ' (' + str(other.labels[i].__class__.__name__) + '), ' 
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
        class Content(object):    # extend a dict?
            
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
            
            def dict(self):
                return {label:self.linked.valueforlabel(label) for label in self.linked.labels}
            
            def __repr__(self):
                return str(self.dict())  

            # Define equality and not-equality for the content    
            def __eq__(self,other):
                if isinstance(other, dict):
                    # Check that every item is present in the 'other' dict
                    for i, item in enumerate(self.linked.labels):
                        if item in other:
                            if  (not self.linked.values[i] == other[item]):
                                return False
                        else:
                            return False
                    # Now check that lengths are the same
                    if not len(other) == len(self.linked.labels):
                        return False
                    else:
                        return True
                # TODO: improve this check
                elif (other.__class__.__name__ == 'Content'):
                    return self.linked == other.linked
                else:
                    raise InputException('Sorry, I cannot compare with {}. Only Point.Content (accessible via Point.content) and Dict are supported)'.format(other.__class__.__name__))

            def __ne__(self,other):
                return (not self.__eq__(other))
                    
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
    '''A coordinates list. If used together with the Space object (as base classes for another object), 
    each coordinate will also have its own label (and it will be accessible by label). 
    Please note that you must extend first the coordinates, then the Space (i.e. Point(Coordinates, Space)'''
    
    def __init__(self, **kwargs):
           
        # Set values
        self._values = kwargs.pop('values', [])

        # Call parent constructor
        super(Coordinates, self).__init__(**kwargs)

        # Trick to bypass the impossibility of popping the 'labels' kwarg from the Space object init
        # http://stackoverflow.com/questions/8972866/correct-way-to-use-super-argument-passing     
        #if self.has_labels:
        #    kwargs.pop('labels', None)
        
        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Consistency checks
        if not trustme:

            # Check that values are set       
            if not self._labels:
                raise InputException("Got no values")
            
            # Check that values is a list
            if not isinstance(self._values,list):
                raise InputException('I got values which are not a list (got "{}" of type "{}")'.format(self._values, type(self._values)))

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
    
    # Init to handle init by dict
    def __init__(self, labels_values_dict=None, **kwargs):

        if labels_values_dict:
            # Trustme switch        
            trustme = kwargs['trustme'] if 'trustme' in kwargs else False
            
            if not trustme:
                if not isinstance(labels_values_dict, dict):
                    raise InputException('I got labels_values_dict which is not a dict (got "{}" of type "{}")'.format(labels_values_dict, type(labels_values_dict)))
            
            # Prepare
            _labels = []
            _values = []

            # Unpack (while sorting, which is fundamental)
            for label in sorted(labels_values_dict):
                _labels.append(label)
                _values.append(labels_values_dict[label])

            # Now add values and labels
            kwargs['values'] = _values
            kwargs['labels'] = _labels
        
            # TODO: disable some checks trougth a switch like this?
            # kwargs['used_values_and_labels'] =true

        # Call parent init
        super(Point, self).__init__(**kwargs)
    
    
    
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

    # Set datatypes
    Span_class   = RegionSpan
    Points_class = Point

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


    def __init__(self, *args, **kwargs):

        self.floating = False

        # Region shape (to be defined using the Shape objects)
        self.shape  = kwargs.pop('shape', None)

        # Region span (i.e. 2x4, or 4x8, or 15d, or 124s, or just 3 in case of a sphere)        
        self.span  = kwargs.pop('span', None)
     
                
        # Region anchor
        self.anchor = kwargs.pop('anchor', None)
        
        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

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
                if isinstance(self.span, str):
                    # If we have a string for the span, try to init the TimeSlotSpan from the string:
                    try:
                        self.span = self.Span_class(self.span)
                    except Exception as e:
                        raise InputException('{}: provided span ("{}" of type "str") cannot be used to initialize the span: {}'.format(self.classname, kwargs['span'], str(e)))
                else:              
                    if not isinstance(self.span, self.Span_class):
                        raise InputException('{}: Wrong span type, I was expecting {} but i got {}.'.format(self.classname, self.Span_class, type(self.span)))
                    
            # If anchor is set, check type:
            if self.anchor is not None:
                assert (isinstance(self.anchor, self.Points_class)), 'Given anchor is not of type Point, got {}'.format(type(self.anchor))
            else:
                self.floating = True

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
                if self.anchor is not None:
                    kwargs['labels'] = self.anchor.labels
    
        # Call parent Init
        super(Region, self).__init__(*args, **kwargs)
    
        if not hasattr(self, '_labels') and 'labels' in kwargs :
            # Check consistency of provided labels and anchor's labels. We do it here to have triggered
            # the validation of the labels in the meanwhile
                if self.anchor.labels != kwargs['labels']:
                    raise InputException('{} my anchor labels "{}" are different than the labels you provided me "{}"'.format(self.classname, self.anchor.labels, kwargs['labels']))

    # Symmetry. By default, not implemented.  
    @property
    def is_symmetric(self):
        raise NotImplementedError('Symmetry for a generic region is not defined, you should implement it')
    
    # Anchoring
    def _anchor_to(self, anchor):
        
        if not self.floating:
            raise Exception('Cannot anchor an already anchored region.')
             
        logger.debug('Anchoring to %s', anchor)
        
        # Check before anchoring
        if not isinstance(anchor, Point):
            raise InputException('Given anchor is not of type Point, got {}'.format(type(anchor)))

        # Set Anchor
        self.anchor = anchor
        self.floating = False

            

class Slot(Region):
    '''A Slot is a particular type of region, which has an hyper-rectangular shape.
    It is basically an interval (https://en.wikipedia.org/wiki/Interval_(mathematics)#Multi-dimensional_intervals)
    In addition to the Span (which in this case is a SlotSpan) also start and end are required, and they must be
    Points referred to the space where the slot lives in. You can omit one of the triplet start-end-span and it will
    be automatically computed.
    
    Please note that the slot is always intended to be with left included, right excluded.'''
    
    # Set datatypes
    Span_class   = SlotSpan
    Points_class = Point

    def __init__(self, *args, **kwargs):

        self.floating = False

        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        if not trustme:
            # Quick sanity checks. We allow a slot without a start, as it is basically a floating region.
            # We also allow to set at build time start and end and let span be derived accordingly.
            if 'span' not in kwargs:
                if ('start' not in kwargs) or ('end' not in kwargs):
                    raise InputException('{}: span not set and not start-end given.'.format(self.classname))


        # Handle start - end - anchor Check that we have at least two out of start-end-span
        start  = kwargs.pop('start', None)
        end    = kwargs.pop('end', None)
        span   = kwargs['span'] if 'span' in kwargs else None
        anchor = kwargs['anchor'] if 'anchor' in kwargs else None

        # Check for correct types. Note that Slot will take care of checking that at least two of the
        # start-end-span are set.

        if start is not None and not isinstance(start, self.Points_class):
            raise InputException('{}: provided start is not of type {}, got {}'.format(self.classname, self.Points_class, type(start)))

        if end is not None and not isinstance(end, self.Points_class):
            raise InputException('{}: provided end is not of type {}, got {}'.format(self.classname, self.Points_class, type(end)))

          
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
            kwargs['span'] = self.Span_class(start=start, end=end)

            # Set anchor
            kwargs['anchor'] = kwargs['span'].get_center(start=start)
                   
        else:
            self.floating = True
            pass
            # TODO: fix this. Span OR start-end OR ..? 
            #raise InputException('{}: Sorry, you have to provide me anchor+span, or start+span, or end+span, or start+end, or start+end+span'.format(self.__class__.__name__))
            

        # We are a slot, set this shape
        kwargs['shape'] = SlotShape

        # Call Father constructor
        super(Slot, self).__init__(*args, **kwargs)
            
    # Handle end 
    @property
    def end(self):
        if self.anchor is None:
            return None
        if hasattr(self, '_end'):
            return self._end
        else:
            # Cache it...
            self._end = self.span.get_end(center=self.anchor)
            return self._end

    # Handle start 
    @property
    def start(self):
        if self.anchor is None:
            return None
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
    # Also, here you should just use span.value instead of re-computing them.
    @property
    def deltas(self):
        return self.span.value
        #eturn [ (self.end.values[i] - self.start.values[i]) for i in range(len(self.start.values))]

    # A slot is symmetric only if the sides (deltas) are the same in length (and therefore the Slot is a n-square).    
    @property
    def is_symmetric(self):
        first_value = None
        for value in self.deltas:
            if first_value is None:
                first_value = value
                continue
            else:
                if first_value != value:
                    return False            
        return True



#-------------------
# Specializations
#-------------------

# A) Places in a n-dimensional space

class TimePoint(Point):
    ''' A point in a 1-dimensional space, the time.'''

    def __init__(self, *args, **kwargs):

        if 'trustme' in kwargs:
            trustme = kwargs['trustme']
        else:
            trustme = False
        
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

        # Try to get value from 't' arg, if successful set labels as well
        try:
            kwargs['values'] = [kwargs.pop('t')]
            kwargs['labels'] = ['t']

        except KeyError:
            try:
                # Otherwise try to get value from 'dt' arg, if successful convert to t and then set labels as well
                kwargs['values'] = [kwargs.pop('dt')]
            except KeyError:
                pass
            else:
                if PERFORMANCE_TIPS_ENABLED:
                    logger.info("TimePoint: You are initializing a TimePoint with a DateTime, this is not performant, use int/float epoch")

                if not trustme:

                    # Check time zone has been passed
                    if not kwargs['values'][0].tzinfo:
                        raise InputException('Sorry, no time zone set for datetime, this is not allowed in Luna (got tzinfo={})'.format(kwargs['values'][0].tzinfo))
                    
                    # Check for coherence of time zone
                    try:
                        if str(self._tz) != str(kwargs['values'][0].tzinfo):
                            raise InputException('Error, explicitly set time zone ({}) differs from datetime timezone ({})'.format(self._tz, kwargs['values'][0].tzinfo))
                    except AttributeError:
                        self._tz = kwargs['values'][0].tzinfo
    
                # Now convert and set labels
                kwargs['values'] = [s_from_dt(kwargs['values'][0])]
                kwargs['labels'] = ['t']

        else:
            if not trustme:
                # Check for no double assignment
                if 'dt' in kwargs:
                        raise InputException('Error: double time assignment (got both dt and t)')
        
        # Check for everything ok
        if not trustme:
            if ('values' not in kwargs) or (not kwargs['values']):
                raise InputException('TimePoint: Got no values at all. My kwargs: {}'.format(kwargs))

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
 
    # Set datatypes
    Span_class  = TimeSlotSpan
    Points_class = TimePoint

    def __init__(self, *args, **kwargs):
        
        # Check for labels correctness
        if 'labels' in kwargs and kwargs['labels'] != ['t']:
            raise InputException('{}: Got labels different than [\'t\'] (got {})'.format(self.classname, kwargs['labels']))
            
        # Define the static labels for this Region (the space where it lives in)
        kwargs['labels'] = ['t']
  
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


class SurfaceSlot(Slot):
    '''A slot in a 3-dimensional space, the space.'''

    # Ensure start,end = SpacePoint()
    def __init__(self, *argv, **kwargs):
        
        super(SpaceSlot, self).__init__(*argv, **kwargs)
        
        # Checks
        assert(isinstance(self.start, SurfacePoint))
        if self._end: assert(isinstance(self.end, SurfacePoint))
        if self.span: assert(isinstance(self.span, SurfaceSpan))

class SpaceSlot(Slot):
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
    pass

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




######################################################################
#
#             COMPOSITE
#
######################################################################


from datetime import datetime
from copy import copy, deepcopy

from luna.common.exceptions import InputException, ConsistencyException
from luna.spacetime.time import dt_from_s
from luna.datatypes.adimensional import *


#---------------------------------------------------
#
#   C o m p o s i t e    d a t a    t y p e s
#
#---------------------------------------------------

# Notation (naming) examples:
#  - Point -> TimePoint  -> DataTimePoint  -> PhysicalDataTimePoint
#  - Point -> SpacePoint -> DataSpacePoint -> PhysicalDataSpacePoint
#  - Point -> TimePoint  -> DataTimePoint  -> SpaceDataTimePoint

#---------------------------------------
# Base
#---------------------------------------

# Ancestors
class DataPoint(Point):
    '''A Point with some data attached, which can be both dimensional (i.e. another point) or 
    adimensional (i.e. an image). The DataPoint introduces also the concept of the validity region,
    which is defined based on the data it carries with him: the validity region (or uniformity region)
    is in fact the region in which the variation of the "measured" value is postulated to be negligible.
    Please note that the validity region _must_ be a symmetric Region. In addition to the validity region,
    another parameter required or defining the validity region is the region span, that can vary on a per-point
    basis (i.e. all the temperature sensors has a spherical validity Region,
    bit its shape can vary if they are indoor or outdoor. Or, more simply, the validity region is a temporal
    segment but it width can vary according to the circumstances. 
    Also note that even if the validity region
    must be a symmetric region, nothing prevents you to use assymetric region in particular implementations
    of the DataPoint. For example, in a TimeDataPoint you could use a validity region projected forward in
    time to achieve the so called event-based data streams.'''
    
    # New
    '''The validity region by default is a Slot, centered on the middle point, and the Span is a SlotSpan, but you can
    change it just by using the validty_region_class and validty_span_class validity_region_anchor ''' 

    def __init__(self, *argv, **kwargs):

        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False

        # Args for the DataPoint
        self.data   = kwargs.pop('data', None)

        # Init empty _validity_region:
        self._validity_region = None    
     
        # Set validty_region_span if present
        validity_region  = kwargs.pop('validity_region', None)
        if validity_region is not None:
            self._validity_region = validity_region

        # Consistency checks
        if not trustme:              
            
            # Check for presence of data
            if self.data is None:
                raise InputException('{}: Sorry, you need to specify some date, i got None'.format(self.classname)) 

        # Call parent Init
        super(DataPoint, self).__init__(*argv, **kwargs)


    # Representation (here we trick a bit if we have data with labels/value to obtain a more comfortable
    # string representation by using self.data.labels[0] and self.data.values[0] 
    def __repr__(self):
        try:
            if 'lables' in self.data:
                return '{}, labels: {}, values: {}, first data label: {}, with value: {}'.format(self.__class__.__name__, self.labels, self.values, self.data.labels[0], self.data.values[0])
            else:
                return '{}, labels: {}, values: {}, data: {}'.format(self.__class__.__name__, self.labels, self.values, self.data)
        except TypeError:
                return '{}, labels: {}, values: {}, data: {}'.format(self.__class__.__name__, self.labels, self.values, self.data)
                    
    
    # TODO: check this (and export the isintsnace check in the base classes). Also, call the super.__eq__ and then add these checks!


    def __eq__(self, other): 
        if not isinstance(self, other.__class__):
            return False
        return (self.values == other.values) and (self.labels == other.labels) and (self.data == other.data)       

    # Un-implment sum and subtraction as since now we carry data it just not make any sense
    def __sub__(self, other, trustme=False):
        raise NotImplemented('Subtracting two DataPoints does not make sense')
    def __sum__(self, other, trustme=False):
        raise NotImplemented('Subtracting two DataPoints does not make sense')

    @property
    def data_type(self):
        raise NotImplemented('{}: you cannot access the data_type attribute if you do not extend the basic DataPoint object specifying a type'.format(self.__class__.__name__))

    # Validity region.
    @property
    def validity_region(self):
        
        # Anchor the validity region to this Point if not already done
        if self._validity_region is not None:
            if self._validity_region.anchor is None:
                # We need to copy the region to let it be used by other Points!
                # TODO: this is a performance hit..
                self._validity_region = copy(self._validity_region)
                self._validity_region._anchor_to(self.Point_part)  
        return self._validity_region

    # Point_part (or, cast to Point)
    @property
    def Point_part(self):

        if not hasattr(self, '_point_part'):
            # self.__class__.__bases__[0] is the Point part (in Luna composite types always start from the Point)
            # Todo: introspection on class extensions, not nice.
            if hasattr(self,'tz'):
                self._point_part = self.__class__.__bases__[0](labels = self.labels, values=self.values, tz=self.tz, trustme=True)
            else:
                self._point_part = self.__class__.__bases__[0](labels = self.labels, values=self.values, trustme=True)
        return self._point_part

    def _get_Point_part(self, *args, **kwargs):
        return self.Point_part

    def filter_data_labels(self, labels):
        
        # TODO: use filtering (views), not copy
        filtered_dataPoint = deepcopy(self)
        
        # Restrict data and labels
        # TODO: might not work if PhysicalQuantites are used as labels 
        filtered_dataPoint.data._values = [self.data.values[self.data.labels.index(label)] for label in labels]
        filtered_dataPoint.data._labels = labels
        
        return filtered_dataPoint


class DataSlot(Slot):
    '''A Slot with some data attached, which can be both dimensional (i.e. another point) or undimensional (i.e. an image).
    The coverage is a metric to help you understand how much you can rely on the slot's data. Read the doc for more info on the coverage concept.'''

    def __init__(self, *argv, **kwargs):
        self.data     = kwargs.pop('data', None)
        self.coverage = kwargs.pop('coverage', None)
        super(DataSlot, self).__init__(*argv, **kwargs)    

    def __repr__(self):
        return '{}, labels: {}, values: {}, data_labels: {}, data_values: {}'.format(self.__class__.__name__, self.labels, self.values, self.data.labels, self.data.values)
    # TODO: check this (and export the isinstance check in the base classes). Also, call the super.__eq__ and then add these checks!

    def __eq__(self, other): 
        if not isinstance(self, other.__class__):
            return False
        return  (self.labels == other.labels) and (self.data == other.data)       

    @property
    def data_type(self):
        raise NotImplemented('{}: you cannot access the data_type attribute if you do not extend the basic DataSlot object specifying a type'.format(self.__class__.__name__))
 
# Composite
class DataTimePoint(TimePoint, DataPoint):
    '''A TimePoint with some data attached, which can be both dimensional (i.e. another point) or undimensional (i.e. an image)'''

    def __repr__(self):
        return '{} @ {}, first data label: {}, with value: {}'.format(self.__class__.__name__, dt_from_s(self.values[0], tz=self.tz), self.data.labels[0], self.data.values[0])



# Decided to remove them to allow a more agnostic approach using the region and the span
#     @property
#     def valid_from(self):
#         '''Returns the start of the validity for the point'''
#         if self.validity_region:
#             return self.dt - self.validity_region
#         else:
#             return self.dt
# 
#     @property
#     def valid_until(self):
#         '''Returns the start of the validity for the point'''
#         if self.validity_region:
#             return self.dt + self.validity_region
#         else:
#             return self.dt


class DataTimeSlot(TimeSlot, DataSlot):
    '''A TimeSlot with some data attached, which can be both dimensional (i.e. another point) or andimensional (i.e. an image)'''
    pass


#---------------------------------------
# Specialization: "dimensional" data
#---------------------------------------

# Ancestors..
class DimensionalDataPoint(DataPoint):  
    '''A Point with some "dimensional" (another Point) data attached.'''
    
    data_type = Point
    
    def __init__(self, *argv, **kwargs):
        if 'data' in kwargs and not isinstance(kwargs['data'], DimensionalDataPoint):
            raise InputException('No Point found in data')
        super(DimensionalDataPoint, self).__init__(*argv, **kwargs)

class DimensionalDataSlot(DataSlot):
    '''A Slot with some "dimensional" (a Point) data attached.'''
              
    data_type = Point
    
    def __init__(self, *argv, **kwargs):
        if 'data' in kwargs and not isinstance(kwargs['data'], Point):
            raise InputException('No Point found in data')
        super(DimensionalDataSlot, self).__init__(*argv, **kwargs)        


# Composite..
class DimensionalDataTimePoint(TimePoint, DimensionalDataPoint):
    '''A TimePoint with some "dimensional" data attached'''
    def __repr__(self):
        return '{} @ {}, first data label: {}, with value: {}'.format(self.__class__.__name__, dt_from_s(self.values[0], tz=self.tz), self.data.labels[0], self.data.values[0])
 
class DimensionalDataTimeSlot(TimeSlot, DimensionalDataSlot):
    '''A TimeSlot with some "dimensional" data attached'''
    def __repr__(self):
        return '{} @ {}, first data label: {}, with value: {}'.format(self.__class__.__name__, dt_from_s(self.values[0], tz=self.tz), self.data.labels[0], self.data.values[0])
 


#---------------------------------------
# Specialization: space handling
#---------------------------------------

# TODO: ...
# class DataSpacePoint(DataPoint, SpacePoint):
#     '''A SpacePoint with some data attached, wich can be both dimensional (i.e. another point) or undimensional (i.e. an image)'''
#     pass
# 
# class DataSpaceSlot(TimePoint, SpacePoint):
#     '''A SpaceSlot with some data attached, wich can be both dimensional (i.e. another point) or undimensional (i.e. an image)'''
#     pass


#---------------------------------------
# Specialization: physical quantities
#---------------------------------------


# Ancestors..
class PhysicalDataPoint(DataPoint):   
    '''A DataPoint where the data is PhysicalDimensionalData'''
    
    data_type = PhysicalData
    
    def __init__(self, *argv, **kwargs):
        if 'trustme' in kwargs and kwargs['trustme']:
            pass
        else:
            if 'data' in kwargs and not isinstance(kwargs['data'], PhysicalData):
                raise InputException('No PhysicalData found in data')
        super(PhysicalDataPoint, self).__init__(*argv, **kwargs)
           
class PhysicalDataSlot(DataSlot):
    '''A DataPoint where the data is PhysicalDimensionalData'''
    
    data_type = PhysicalData
    
    def __init__(self, *argv, **kwargs):
        if 'trustme' in kwargs and kwargs['trustme']:
            pass
        else:
            if 'data' in kwargs and not isinstance(kwargs['data'], PhysicalData):
                raise InputException('No PhysicalData found in data')
        super(PhysicalDataSlot, self).__init__(*argv, **kwargs)


# Composite..
class PhysicalDataTimePoint(TimePoint, PhysicalDataPoint):   
    pass

class PhysicalDataTimeSlot(TimeSlot, PhysicalDataSlot):
    pass



#---------------------------------------------------
#
#   Data Sets, Series, Time Series etc.
#
#---------------------------------------------------


class Set(object):
    '''An unordered ensemble of Points or Regions (or Slots). This is the base class for data ensables in Luna.'''

    # Un-implement operators which acts on the memory address as are meaningless in this context
    def __eq__(self, other):
        raise NotImplementedError()
    def __ne__(self, other):
        raise NotImplementedError()    
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


class DataSet(Set):
    '''An unordered ensemble of DataPoints or DataRegions (or DataSlots).'''
    pass

class Series(Set):
    '''An ordered ensemble (or sequence) of DataPoints or DataRegions (or DataSlots).'''
    pass

class DataSeries(Series):
    '''An (ordered) sequence of DataPoints or DataRegions (or DataSlots). The order may vary and the logic is left to the user
    (i.e. SurfaceDataPoints can be orderd by x or y depending on the implementation, exactly as a C matrix, while
    TimeDataPoints are ordered by time)'''
    pass

class TimeSeries(Series):
    '''A Series of TimePoints or TimeSlots (not TimeRegions as time is 1D and only
    regions with a "slotty" shape make sense). Please note that this TimeSeries does  not carry any data.
    According to Wikipedia, a TimeSeries is "a sequence of data points", but in Luna's logic it is
    just a sequence of (Time)Points. See DataTimeSeries for the common TimeSeries.'''
    pass

# TODO: should be DataTimeSeries(TimeSeries, DataSeries)?
class DataTimeSeries(TimeSeries):
    '''An DataSeries of DataTimePoints or DataTimeSlots (not DataTimeRegions as we are in 1D and only
    regions with a "slotty" shape make sense, so DataTimeSlots).. Definition from Wikipedia: 2a sequence of data points".
    In our logic is therfore an ordered set of DataTimePoints or DataTimeSlots (not DataTimeRegions as we are in 1D and only
    regions with a "slotty" shape make sense, so DataTimeSlots).'''

    _time_filter_enabled = True

    @property
    def data_type(self):

        if self.data.first:
            if isinstance(self.data.first, TimeSlot):
                return DataTimeSlot
            else:    
                return DataTimePoint
        else:
            return None
    
    def __repr__(self):
        # TODO: use the data_type
        if self._data:
            if isinstance(self._data[0], TimeSlot):
                return '{} of {} {} ({}), first TimeSlot start: {}, last TimeSlot start: {}, timezone: {}'.format(self.__class__.__name__, len(self._data), self._data[0].__class__.__name__, self._data[0].span, self._data[0].start.dt, self._data[-1].start.dt, self.tz)                
            else:    
                return '{} of {} {}, start: {}, end: {}, timezone: {}'.format(self.__class__.__name__, len(self._data), self._data[0].__class__.__name__, self._data[0].dt, self._data[-1].dt, self.tz)
        else:
            return '{} of 0 None, start: None, end: None, timezone: {}'.format(self.__class__.__name__, self.tz)

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False        
        return ((self._data == other._data) and (self.tz == other.tz))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._data)

    def __init__(self, tz=None, index=False, wrapped=None, filter_labels=None, filter_from_dt=None, filter_to_dt=None, data_label_to_lazy_filter=None):

        # Initialize data container
        self._data = []
        
        # Initialize time zone
        self._tz= tz
        
        # Initialize index if required
        if index:
            self.index = {}
        else:
            self.index = None
            
        # Handle wrapper and filtering 
        self.wrapped        = wrapped
        self.filter_labels  = filter_labels
        self.filter_from_dt = filter_from_dt
        self.filter_to_dt   = filter_to_dt
        self.data_label_to_lazy_filter = data_label_to_lazy_filter
        
    def __getattribute__(self, attr):
        # Handle wrap of myself 
        wrapped = object.__getattribute__(self, 'wrapped')
        # Hard Debug: logger.debug('Getting attr %s, wrapped=%s',attr, wrapped)
        if wrapped:
            # Wrapped object, filters and iterator status are stored in myself, not in the wrapped object
            if attr in ['wrapped', 'filter_labels', 'filter_from_dt', 'filter_to_dt', 'data_label_to_lazy_filter', '__iter__', '__next__', 'wrapper_current']:
                # Hard Debug: logger.debug('USING NOT WRAPPED %s', attr) 
                return object.__getattribute__(self, attr)
            else:
                # Proxy to the wrapped object
                return getattr(wrapped, attr)
        else:
            return object.__getattribute__(self, attr)
   
    @property
    def tz(self):
        if self._data:
            return self._data[-1].tz
        else:
            return self._tz
    
    def append(self, timeData_Point_or_Slot, trust_me=False):
        '''You can append TimeDataPoints and TimeDataSlots'''
        
        if not trust_me:
            
            # A) Check data types for DataTimePoint or DataTimeSLot
            #if not isinstance(timeData_Point_or_Slot, DataTimePoint) and not isinstance(timeData_Point_or_Slot, DataTimeSlot):
            #    raise Exception("Data type not supported (got {})".format(type(timeData_Point_or_Slot)))
            
            # B) Check for TimePoint os TimeSLot and that the DATA attribute is present
            if not isinstance(timeData_Point_or_Slot, TimePoint) and not isinstance(timeData_Point_or_Slot, TimeSlot):
                raise Exception("Got unsupported data type while appending to the DataTimeSeries (got {})".format(type(timeData_Point_or_Slot)))
            # Now try access data (Will automatically raise) TODO: improve
            _ = timeData_Point_or_Slot.data    


            if self._data:

                last_timeData_Point_or_Slot = self._data[-1]

                if isinstance (timeData_Point_or_Slot, TimeSlot):
                    this_t = timeData_Point_or_Slot.start.t
                    last_t = last_timeData_Point_or_Slot.start.t
                elif isinstance (timeData_Point_or_Slot, TimePoint):
                    this_t = timeData_Point_or_Slot.t
                    last_t = last_timeData_Point_or_Slot.t
                else:
                    raise InputException('Got {} ??'.format(type(last_timeData_Point_or_Slot)))

                # Check that the item being appended is the same type of the already added ones     
                if self._data and not isinstance(timeData_Point_or_Slot, last_timeData_Point_or_Slot.__class__):
                    raise InputException("Wrong data Type")
                
                # Check that we are adding time-ordered data. As TimeDataPoint and TimeDataSlot extends
                # TimePoint, we are sure that there is a time dimension ("t") to check
                if this_t <= last_t:
                    raise InputException("Sorry, you are trying to append data with a timestamp which preceeds (or is equal to) the last one stored. As last I have {}, and I got {}"
                                     .format(dt_from_s(last_t, tz=self.tz), dt_from_s(this_t, tz=self.tz)))
                
                # If the data of timeData_Point_or_Slot is dimensional (lives in a Space, ex DimensionalData), check compatibility
                if isinstance(timeData_Point_or_Slot.data, Space):
                    timeData_Point_or_Slot.data.is_compatible_with(last_timeData_Point_or_Slot.data, raises=True)
                
                # Check also the tz. We need to check with strings.. 
                # TOOD: improve this check?  
                if str(last_timeData_Point_or_Slot.tz) != str(timeData_Point_or_Slot.tz):
                    raise InputException('Error, you are trying to add data with timezone "{}" but I have timezone "{}"'.format(timeData_Point_or_Slot.tz, last_timeData_Point_or_Slot.tz))
        
            else:
                
                # Only check timezone consistence if any
                if self._tz and timeData_Point_or_Slot.tz != self.tz:       
                    raise InputException('Error, you are trying to add data with timezone "{}" but I have timezone "{}"'.format(timeData_Point_or_Slot.tz, self._tz))

        
        if self.index is not None:
            self.index[timeData_Point_or_Slot.t] = len(self._data)
          
        self._data.append(timeData_Point_or_Slot)
       
    #--------------       
    #  Iterator
    #--------------
    def __iter__(self):

        # Wrapper logic
        if self.wrapped:
            self.wrapper_current= -1
        else:
            self.current = -1
        
        return self

    def __next__(self, filter_from_dt=None, filter_to_dt=None, filter_labels=None, data_label_to_lazy_filter=None, current=None):
  
        # Wrapper logic
        if self.wrapped:
            self.wrapper_current += 1
            return self.wrapped.__next__(filter_from_dt=self.filter_from_dt, filter_to_dt=self.filter_to_dt, filter_labels=self.filter_labels, data_label_to_lazy_filter = self.data_label_to_lazy_filter,  current=self.wrapper_current-1)
        
        # Use current of our wrapper
        current =  current if current is not None else self.current
        
        # Iterator logic
        if current > len(self._data)-2:
            raise StopIteration
        else:
            if not self.wrapped:
                self.current += 1

            if filter_labels is not None or filter_from_dt is not None and self.filter_to_dt is not None or data_label_to_lazy_filter is not None:
                
                # Handle filtering
                if filter_labels:
                    return self._data[current+1].filter_data_labels(labels=filter_labels)
                elif data_label_to_lazy_filter:

                    # Set filtering and return
                    self._data[current+1].data.enable_lazy_filter_label(label=data_label_to_lazy_filter)                  
                    return self._data[current+1]
                
                else:
                    raise NotImplementedError('Filtering on is not yet implemented in this method')
            
            else:
                return self._data[current+1]

    # Python 2.x
    def next(self):
        return self.__next__()

    # Index
    def __getitem__(self, key):
        
        # Sanitize input 
        if isinstance(key, datetime):
            epoch_s = dt_from_s(key)
        elif isinstance(key, int):
            epoch_s = key
        else:
            raise InputException("key not int or datetime")

        # Use index table?
        if self.index is not None:
            return self._data[self.index[epoch_s]]

        # Search with bisection for the right element. Surely improvable
        # TODO: add timestamps <-> position in list mapping table?
        floor = 0
        ceil  = len(self._data)-1
        count = 0
        
        while True:          
            if count > len(self._data):
                raise Exception("Internal error when looking for the given timestamp (too many iterations)")
            
            # Bisection mid point:
            middle = floor + int((ceil-floor)/2)
            
            # Not found?
            if floor==ceil or floor==middle or ceil==middle:
                raise IndexError('Timestamp {} not found in TimeSeries!'.format(key))
            
            # We found?
            if self._data[floor].t == epoch_s: return self._data[floor]
            if self._data[ceil].t == epoch_s: return self._data[ceil]
            if self._data[middle].t == epoch_s: return self._data[middle]

            if epoch_s > self._data[middle].t:
                floor = middle
            elif epoch_s < self._data[middle].t:
                ceil = middle
            else:
                raise Exception("Internal error when looking for the given timestamp (unconsistent condition)")
            count += 1
            
    #------------------
    # ALPHA code
    #------------------
    
    # Data-access apart form timeSerie[timestamp] and iterator
    @property
    def items(self):
        return self._data


    # Data incapsulator
    class Data(object):
        def __init__(self,data):
            self.link = data
        
        @property
        def labels(self):
            if self.link:
                return self.link[0].data.labels
            else:
                return None
        
        @property
        def type(self):
            if self.link:
                return type(self.link[0])
            else:
                return None        

        @property
        def first(self):
            if self.link:
                return self.link[0]
            else:
                return None   


    @property
    def data(self):
        return self.Data(self._data)

    def is_empty(self):
        return (False if self._data else True)        



    #----------------
    # Filtering
    #----------------

    # TODO: name it cut/slice/subset?
    def filter(self, from_dt=None, to_dt=None, labels=None, trustme=False):
        
        # Sanity checks..
        if not trustme:
            if from_dt is None and to_dt is None and labels is None:
                raise InputException('At least one argument of the three is required: from_dt, to_dt, labels')
            
            if (from_dt is not None or to_dt is not None) and labels is not None:
                raise InputException('Sorry, you cannot filter both on time and on labels')
            
            if (from_dt is not None or to_dt is not None) and not self._time_filter_enabled:
                raise InputException('Sorry, on this kind of DataTimeSeries filtering in time is not supported')
        
        if (from_dt is not None or to_dt is not None):
            #--------------------------------------------
            # TODO: disable if streaming? Cannot work..
            #--------------------------------------------
            
            # Filter on time: initialize new DataTimeSeries to return as container
            filtered_timeSereies = DataTimeSeries(tz=self.tz, index=self.index)
            
            logger.debug('Filtering time series from %s to %s', from_dt, to_dt)
            for item in self:
                if isinstance(item, TimePoint):
                    if item.dt >= from_dt and item.dt < to_dt:
                        filtered_timeSereies.append(item)   
                elif isinstance(item, TimeSlot):
                    if item.start.dt >= from_dt and item.end.dt <= to_dt:
                        filtered_timeSereies.append(item)          
                else:
                    raise ConsistencyException('TimeSereie with neither TimePoint or TimeSlots?! It has {}'.format(type(item)))
            return filtered_timeSereies
                   
        else:
            return self.__class__(wrapped=self, filter_labels=labels)


    def lazy_filter_data_label(self,label):
        return self.__class__(wrapped=self, data_label_to_lazy_filter=label)

#class PhysicalDataTimeSeries(object):
#    '''An ordered serie of PhysicalDataTimePoints or PhysicalDataTimeSlots'''
#    # TODO: really implement this one..?
#    pass


#---------------------------------------------
# StreamingDataTimeSeries
#---------------------------------------------

# TODO: Put in auxiliary and improve (should extend DataStream)
class DataTimeStream(object):
    ''' A data time stream is a stream of DataTimePoints or DataTimeSlots. it has to be implemented by the data source (storage)'''
    
    # Iterator
    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    # Python 2.x
    def next(self):
        return self.__next__()

class StreamingDataTimeSeries(DataTimeSeries):
    '''In the streaming DataTimeSeries, the iterator is rewritten to use a DataTimeStream. Not-streaming operations
    (like accessing the index) are supported, but they triggers the complete navigation of the DataTimeStream which
    can be very large to be loaded in RAM, or just never ending in case of a real time stream'''
    
    _time_filter_enabled = False
    
    # Init to save the DataTimeStream   
    def __init__(self, *args, **kwargs):
        self.iterator = None
        self.user_cached = kwargs.pop('cached', False) # TODO: naming: user_cached means that the user WANTS the ts to be cached
        self.cached = False
        self.dataTimeStream = kwargs.pop('dataTimeStream')
        self.gone_trought_iterator = False
        super(StreamingDataTimeSeries, self).__init__(*args, **kwargs)

    def __repr__(self):
        if self.__data:
            return '{}, start={}, end={}'.format(self.__class__.__name__, self.__data[0], self.__data[-1])
        else:
            return '{}, start=NotImp, last seen=NotImp'.format(self.__class__.__name__)

    def __iter__(self):
        # Check if the iterator is going to use the cache, so do not even initialize the iterator of the dataTimeStream
        if not (self.cached and self.gone_trought_iterator):
            self.iterator = self.dataTimeStream.__iter__()
        else:
            logger.debug('Loading from cache, not using dataTimeStream iterator')
        # Set iteration staring position
        self.iterator_pos = -1
        return self

    def __next__(self):

        # If the time series is cached and we already gone trough all the iterator, just return the cache
        if self.cached and self.gone_trought_iterator:
            self.iterator_pos += 1
            try:
                return self.__data[self.iterator_pos]
            except IndexError:
                raise StopIteration
        
        # Otherwise, load all content
        else:
            try:
                next = self.iterator.next()
                if self.cached:
                    self.__data.append(next)
            except StopIteration:
                self.gone_trought_iterator = True
                raise
            return next

    # Python 2.x back-compatibility
    def next(self):
        return self.__next__()

    # ..but if someone access the _data somehow, we have to get the entire TimeSeries by going
    # trought all the iteraor, and we issue a warning
    
    @property
    def _data(self):

        if self.user_cached and not self.__data:
            # We are fine to cache the data, so use force load
            self.force_load()
        
        else:
            # Here to be warned every time that the the user access the time series in a not streaming fashion
            logger.warning('You are forcing a StreamingTimeSeries to work in a non-streaming way, I need to force-load it to perform this operation! Read the doc about force_load() for more info.')      
            
            if not self.__data:
                # TODO: Decide where to raise the warning
                # Here to be warned only the first time that the the user access the time series in a not streaming fashion
                #logger.warning('You are forcing a StreamingTimeSeries to work in a non-streaming way, I need to force-load it to perform this operation! Read the doc about force_load() for more info.')      
                self.force_load()
  
        return self.__data
        
    @_data.setter
    def _data(self, value):
        self.__data=value

    def force_load(self):
        
        logger.warning('Force-loading time series!')
        
        # Load content levereaging the internal iterator
        self.__data = [item for item in self]

        # When you force- load a StreamingDataTimeSeries, caching is automatically enabled.
        self.cached = True



 

























