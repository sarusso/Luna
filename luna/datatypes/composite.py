
from datetime import datetime
from luna.common.exceptions import InputException, ConsistencyException
from luna.spacetime.time import dt_from_s
from luna.datatypes.adimensional import *
from luna.datatypes.dimensional import *


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
    another required parameter is the validity span, which is required for defining the validity region and
    that and dat vary on a per-point basis (i.e. all the temperature sensors has a spherical validity Region,
    bit its shape can vary if they are indoor or outdoor. Or, more simply, the validity region is a temporal
    segment but it width can vary according to the circumstances. One final note: even if the validity region
    must be a symmetric region, nothing prevents you to use assymetric region in particular implementations
    of the DataPoint. For example, in a TimeDataPoint you could use a validity region projected forward in
    time to achieve the so called event-based data streams.'''
    
    # New
    '''The validity region by default is a Slot, centered on the middle point, and the Span is a SlotSpan, but you can
    change it just by using the validty_region_class and validty_span_class validity_region_anchor ''' 
    
    
    validity_region_class  = Slot

    def __init__(self, *argv, **kwargs):

        # Trustme switch        
        trustme = kwargs['trustme'] if 'trustme' in kwargs else False
        
        # Args for the DataPoint
        self.data   = kwargs.pop('data', None)
        
        # If validity_region_class is passed, override and set the new one (and check if necessary)
        if 'validity_region_class' in kwargs:
            self.validity_region_class = kwargs.pop('validity_region_class')

        # Set validty_region_span
        validity_region_span  = kwargs.pop('validity_region_span', None)
        
        # Set the span only if it is not None
        if validity_region_span is not None:
            self.validity_region_span = validity_region_span
            
        # Consistency checks
        if not trustme:              
            
            # Check valid validity_region_class
            if not issubclass(self.validity_region_class, Region):
                raise InputException('Point validity region class must be a subclass of Region, got {}'.format(type(self.validity_region)))  
            
            # If we are have a validity span and therefore a validity region:  
            if validity_region_span is not None:
                
                # Check valid Span
                if not isinstance(self.validity_region_span, Span):
                    raise InputException('Point validity region span must be a subclass of Span, got {}'.format(type(self.validity_region_span)))  


        # Call parent Init
        super(DataPoint, self).__init__(*argv, **kwargs)

        # Consistency checks (after parent Init)
        if not trustme:  
            # If we are have a validity span and therefore a validity region:  
            if validity_region_span is not None:
                # Check symmetry # TODO: this check raise the creation of the validity Region object. Change logic for performance? 
                if self.validity_region and not self.validity_region.is_symmetric:
                    raise InputException('The the validity region _must_ be a symmetric Region, the one you provided it is not.')



    def __repr__(self):
        return '{}, labels: {}, values: {}, first data label: {}, with value: {}'.format(self.__class__.__name__, self.labels, self.values, self.data.labels[0], self.data.values[0])
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

    # Validity region. TODO: Save it in a _validty_region variable for performance?
    @property
    def validity_region(self):
        
        # Center on lower corner
        return self.validity_region_class(start=self, span=self.validity_region_span)

        

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
    '''A TimePoint with some data attached, wich can be both dimensional (i.e. another point) or undimensional (i.e. an image)'''
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
    '''A TimeSlot with some data attached, wich can be both dimensional (i.e. another point) or undimensional (i.e. an image)'''
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
        if 'data' in kwargs and not isinstance(kwargs['data'], PhysicalData):
            raise InputException('No PhysicalData found in data')
        super(PhysicalDataPoint, self).__init__(*argv, **kwargs)
           
class PhysicalDataSlot(DataSlot):
    '''A DataPoint where the data is PhysicalDimensionalData'''
    
    data_type = PhysicalData
    
    def __init__(self, *argv, **kwargs):
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
    '''An unordered ensemble of Points or Regions (or Slots).'''
    pass

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
                return '{} of {} {} ({}), first TimeSlot start: {}, last TimeSLot start: {}, timezone: {}'.format(self.__class__.__name__, len(self._data), self._data[0].__class__.__name__, self._data[0].span, self._data[0].start.dt, self._data[-1].start.dt, self.tz)                
            else:    
                return '{} of {} {}, start: {}, end: {}, timezone: {}'.format(self.__class__.__name__, len(self._data), self._data[0].__class__.__name__, self._data[0].dt, self._data[-1].dt, self.tz)
        else:
            return '{} of 0 None, start: None, end: None, timezone: {}'.format(self.__class__.__name__, self.tz)

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False        
        return ((self._data == other._data) and (self.tz == other.tz))

    def __neq__(self, other):
        return not self.__eq(other)

    def __len__(self):
        return len(self._data)

    def __init__(self, tz=None, index=False):
        
        # Initialize data container
        self._data = []
        
        # Initialize time zone
        self._tz= tz
        
        # Initialize index if required
        if index:
            self.index = {}
        else:
            self.index = None
            
        # initialize filtering
        self.filter_labels  = None
        self.filter_from_dt = None
        self.filter_to_dt   = None 
   
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
                
                # Check also the tz
                if last_timeData_Point_or_Slot.tz != timeData_Point_or_Slot.tz:
                    raise InputException('Error, you are trying to add data with timezone "{}" but I have timezone "{}"'.format(timeData_Point_or_Slot.tz, last_timeData_Point_or_Slot.tz))
        
            else:
                
                # Only check timezone consistence if any
                if self._tz and timeData_Point_or_Slot.tz != self.tz:       
                    raise InputException('Error, you are trying to add data with timezone "{}" but I have timezone "{}"'.format(timeData_Point_or_Slot.tz, self._tz))

        
        if self.index is not None:
            self.index[timeData_Point_or_Slot.t] = len(self._data)
          
        self._data.append(timeData_Point_or_Slot)
              
    # Iterator
    def __iter__(self):
        self.current = -1
        return self

    def __next__(self):
        if self.current > len(self._data)-2:
            raise StopIteration
        else:
            self.current += 1
            if self.filter_labels is None and self.filter_from_dt is None and self.filter_to_dt is None:  
                return self._data[self.current]
            else:
                if self.filter_from_dt or self.filter_to_dt:
                    raise NotImplementedError('Filtering on is not yet implemented')


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

    def filter_on(self, from_dt=None, to_dt=None, labels=None):
        logger.info('Activating filtering for dataTimeSeries')
        if labels:
            self.filter_labels  = labels
        if from_dt:
            self.filter_from_dt = from_dt
        if to_dt:
            self.filter_to_dt   = to_dt
        # Raise Exception. not yet implemented..
        raise NotImplementedError('Filtering on is not yet implemented')

    def filter_off(self):
        logger.info('Activating filtering for dataTimeSeries')
        self.labels  = None
        self.filter_from_dt = None
        self.filter_to_dt   = None
        # Raise Exception. not yet implemented..
        raise NotImplementedError('Filtering is not yet implemented')
    
    # TODO: name it cut/slice/subset?
    def filter(self, from_dt, to_dt):
        
        #--------------------------------------------
        # TODO: disable if streaming? Cannot work..
        #--------------------------------------------
        
        # Initialize new TimeSeries to return as container
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


#class PhysicalDataTimeSeries(object):
#    '''An ordered serie of PhysicalDataTimePoints or PhysicalDataTimeSlots'''
#    # TODO: really implement this one..?
#    pass


#---------------------------------------------
# StreamingDataTimeSeries
#---------------------------------------------

# Put in auxiliary and improve (should extend DataStream)
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
            return '{}, start={}, last seen={}'.format(self.__class__.__name__, self.__data[0], self.__data[-1])
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
                
        # Load content levereaging the internal iterator
        self.__data = [item for item in self]

        # When you force- load a StreamingDataTimeSeries, caching is automatically enabled.
        self.cached = True



 














