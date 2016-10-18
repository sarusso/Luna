from luna.datatypes.dimensional import TimePoint, TimeSlot
from luna.datatypes.dimensional import DataTimePoint, DataTimeSlot, PhysicalData, DataTimeSeries, DataPoint, DataSlot
from luna.datatypes.auxiliary import PhysicalQuantity
from luna.common.exceptions import ConsistencyException, ConfigurationException, InputException, NoDataException
from luna.aggregators.utilities import compute_1D_coverage
from luna.spacetime.time import s_from_dt

#--------------------------
#    Logger
#--------------------------

import logging
logger = logging.getLogger(__name__)


#-------------------------------------
# Aggregators
#-------------------------------------

# An Aggregator processes some data (DataPoints or DataSlots) encapsulated in a
# Set(DataSet/Series/DataSeries/DataTimeSeries) and return a Region/Slot.
# The operation that the aggregator will perform are defined in the Sensor object,
# and in particular in all its extensions. See the sensors package for more info.

class Aggregator(object):
    '''Base Aggregator class'''
    pass

# Should be: PhysicalDataTimePointsAggregator ( and PhysicalDataTimeSeries)
 
 

class DataTimePointsAggregator(Aggregator):
    '''Aggregate DataTimePoints of a DataTimeSeries into a DataTimeSlot
    The Aggregator is STATELESS'''
    
    # TODO: Merge me into a DataTimeSeriesAggregator, using the data type to understand how to aggregate? 
 
    def __init__(self, Sensor):
        self.Sensor = Sensor
    
    def aggregate(self, dataTimeSeries, start_dt, end_dt, timeSlotSpan, raise_if_no_data=False):

        #-------------------
        # Sanity checks
        #-------------------

        # First of all Ensure we are operating on PhysicalData (so we eill have PhysicalQuantities),
        # otherwise raise an error:
        if self.Sensor.Points_type.data_type != PhysicalData:
            raise NotImplementedError('Sorry, only PhysicalData data type is supported for now. Adding support for generic data is not too much complicated anyway')


        #-------------------
        # Support vars
        #-------------------
        Slot_data_labels_to_generate = self.Sensor.Slots_data_labels
        Slot_data_labels             = [] # TODO: REMOVE, this is the same as Slot_data_labels_to_generate
        Slot_data_values             = []
        
        # Create start and end Points. TODO: is this not performant, also with the time zone? 
        start_Point = TimePoint(t=s_from_dt(start_dt), tz=start_dt.tzinfo)
        end_Point   = TimePoint(t=s_from_dt(end_dt), tz=start_dt.tzinfo)

        #-------------------
        # Compute coverage
        #-------------------
        Slot_coverage = compute_1D_coverage(dataSeries  = dataTimeSeries,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)

        # If no coverage return list of None in None data is allowed, otherwise raise.
        if Slot_coverage == 0.0:
            if raise_if_no_data:
                raise NoDataException('This slot has coverage of 0.0, cannot compute any data! (start={}, end={})'.format(start_Point, end_Point))
            else:
                Slot_physicalData = self.Sensor.Points_type.data_type(labels  = Slot_data_labels_to_generate,
                                                                      values  = [None for _ in Slot_data_labels_to_generate], # Force "trustme" to allow None in data
                                                                      trustme = True)
                
                dataTimeSlot = self.Sensor.Slots_type(start    = start_Point,
                                                      end      = end_Point,
                                                      data     = Slot_physicalData,
                                                      span     = timeSlotSpan,
                                                      coverage = 0.0) 
                
                logger.info('Done aggregating, slot: %s', dataTimeSlot)
                return dataTimeSlot

        #--------------------------------------------
        # Understand the labels to produce and to 
        # operate on according to the sensor type
        #--------------------------------------------
        
        # TODO: define a mapping somwhere and perform this operations only once.

        for Slot_data_label_to_generate in Slot_data_labels_to_generate:
            
            handled      = False
            Generator    = None
            Operation    = None
            operate_on   = None
            
            # Labels could already be PhysicalQuantiy objects
            if not isinstance(Slot_data_label_to_generate, PhysicalQuantity):
                physicalQuantity_to_generate = PhysicalQuantity(Slot_data_label_to_generate)
        
            if physicalQuantity_to_generate.op is None:
                raise ConfigurationException('Sorry, PhysicalQuantity "{}" has no operation defined, cannot aggregate.'.format(physicalQuantity_to_generate))


            #--------------------------------------
            #   Handle generators
            #--------------------------------------

            # Is this physicalQuantity generated by a custom generator defined inside the sensor class?
            try:
                # TODO: Use the 'provides' logic
                Generator = getattr(self.Sensor, Slot_data_label_to_generate)
                handled = True
            except AttributeError:
                pass

            
            # Is this physicalQuantity generated by a standard generator?
            try:
                from luna.aggregators import generators
                Generator = getattr(generators, Slot_data_label_to_generate)
                handled = True
            except AttributeError:
                pass

            #--------------------------------------
            #   Handle operations
            #--------------------------------------

            # Is this physicalQuantity_to_generate generated  by applying the operation to another
            # physicalQuantity_to_generate defined in the Points?
            
            for Point_physicalQuantity in self.Sensor.Points_data_labels:
                
                # Standard operation
                if physicalQuantity_to_generate.name_unit == Point_physicalQuantity:
                    try:
                        from luna.aggregators import operations
                        Operation = getattr(operations, physicalQuantity_to_generate.op)
                    except AttributeError:
                        # TODO: add more info (i.e. sensor class etc?)
                        raise ConfigurationException('Sorry, I cannot find any valid operation for {} in luna.aggregators.operations'.format(physicalQuantity_to_generate.op))
    
                    operate_on = Point_physicalQuantity
                    handled = True
                    break
                 
            logger.debug('For generating %s I will use generator %s and operation %s', physicalQuantity_to_generate, Generator, Operation)


            #----------------------
            # Now compute
            #----------------------

            if not handled:
                # TODO: add more info (i.e. sensor class etc?)
                raise ConfigurationException('Could not handle "{}", as I did not find any way to generate it. Please check your configuration for this sensor'.format(Slot_data_label_to_generate))

            # Set if streaming Operation/generator: 
            try:
                Generator_is_streaming = Generator.is_stremaing
            except AttributeError:
                Generator_is_streaming = False
            try:
                Operation_is_streaming = Operation.is_stremaing
            except AttributeError:
                Operation_is_streaming = False

            if Generator and not Generator_is_streaming:
                
                logger.debug('Running generator %s on to generate %s', Generator, Slot_data_label_to_generate)

                # A generator also requires access to the aggregated data, so we initialize it also here**
                Slot_physicalData = self.Sensor.Points_type.data_type(labels = Slot_data_labels,
                                                                      values = Slot_data_values)
                # Run the generator
                result = Generator.generate(dataSeries      = dataTimeSeries,
                                            start_Point     = start_Point,
                                            end_Point       = end_Point,
                                            aggregated_data = Slot_physicalData)


                # Ok, append the operation/generator results to the labels and values
                logger.debug('Done running generator')
                Slot_data_labels.append(Slot_data_label_to_generate)
                Slot_data_values.append(result)

            elif Operation and not Operation_is_streaming:
                
                logger.debug('Running operation %s on %s to generate %s', Operation, operate_on, Slot_data_label_to_generate)
                
                # Run the operation
                result = Operation.compute_on_Points(dataSeries  = dataTimeSeries.lazy_filter_data_label(label=operate_on),
                                                     start_Point = start_Point,
                                                     end_Point   = end_Point)
            
                # Ok, append the operation/generator results to the labels and values
                logger.debug('Done running operation')
                Slot_data_labels.append(Slot_data_label_to_generate)
                Slot_data_values.append(result)
                
            else:
                raise ConsistencyException('No generator nor Operation?! (maybe got streaming which is not yet supported)')
            
  

          
        #----------------------
        # Build results
        #----------------------

        Slot_physicalData = self.Sensor.Points_type.data_type(labels = Slot_data_labels,
                                                              values = Slot_data_values)
        
        dataTimeSlot = self.Sensor.Slots_type(start    = start_Point,
                                              end      = end_Point,
                                              data     = Slot_physicalData,
                                              span     = timeSlotSpan,
                                              coverage = Slot_coverage)

        # Return results
        logger.info('Done aggregating, slot: %s', dataTimeSlot)
        return dataTimeSlot
    

class DataTimeSlotsAggregator(Aggregator):
    '''Aggregate DataTimeSlots of a DataTimeSeries into a wider DataTimeSlot.
    The Aggregator is STATELESS'''
    
    # TODO: Merge me into a DataTimeSeriesAggregator, using the data type to understand how to aggregate? 

    pass


#-------------------------------------
# Aggregators Porcesses
#-------------------------------------

class DataTimeSeriesAggregatorProcess(object):
    '''A DataTimeSeriesAggregatorProcess run one or more DataTimePointsAggregator or DataTimeSlotsAggregator
    to generate a DataTimeSeries of DataTimeSlots. The destination DataTimeSlot drives the process (i.e. 
    aggregate in 15 minutes slots). The DataTimeSeriesAggregatorProcess is STATEFUL'''

    
    def __init__(self, timeSlotSpan, Sensor, data_to_aggregate, raise_if_no_data=False):
        ''' Initiliaze the aggregator process, of a given timeSlotSpan.'''

        # Arguments
        self.timeSlotSpan            = timeSlotSpan
        self.Sensor                  = Sensor
        self.data_to_aggregate       = data_to_aggregate
        self.raise_if_no_data         = raise_if_no_data
        
        # Internal vars
        self.results_dataTimeSeries  = DataTimeSeries()
        self._aggregator             = None
        self.Aggregator              = None
        
        # Sanity checks
        if not self.data_to_aggregate:
            raise ConsistencyException("No data type set: got (got {})".format(self.data_to_aggregate))
        # Check for the DataTimePoint concept being extended (including combinations)
        elif issubclass(self.data_to_aggregate, DataPoint) and issubclass(self.data_to_aggregate, TimePoint):
            self.Aggregator = DataTimePointsAggregator
        # Check for the DataTimeSlot concept being extended (including combinations)
        elif issubclass(self.data_to_aggregate, DataSlot) and issubclass(self.data_to_aggregate, TimeSlot):
            self.Aggregator = DataTimeSlotsAggregator
        else:
            raise ConsistencyException("Un-handable data type: got no DataTimePoint, no DataTimeSlot and not None (got {})".format(self.data_to_aggregate)) 

    @property   
    def aggregator(self):
        
        # Instantiate the proper aggregator class if not already done
        if not self._aggregator:
            self._aggregator = self.Aggregator(Sensor=self.Sensor)
        return self._aggregator


    #------------------
    #  Start process
    #------------------
    def start(self, dataTimeSeries, start_dt, end_dt, rounded=False, threaded=False, callback=None, callback_trigger=None):
        ''' Start the aggregator process. if start is not set, the first datapoint is used. If end is not set,
        once the process will provide the results until the last datapoint (useful for online processing)
        '''

        # For now start/end not set is not supported:
        if not start_dt or not end_dt:
            raise NotImplementedError('Empty start/end not yet implemented') 

        # Handle the rounded case
        if rounded:
            start_dt = self.timeSlotSpan.round_dt(start_dt) if start_dt else None
            end_dt   = self.timeSlotSpan.round_dt(end_dt) if end_dt   else None
            if start_dt == end_dt:
                raise InputException('Sorry, after rounding start_dt and end_dt they are the same point! ({})'.format(start_dt))
        else:
            # Check for consistency
            if start_dt is not None:
                if start_dt != self.timeSlotSpan.round_dt(start_dt):
                    raise InputException('Sorry, provided start_dt is not consistent with the timeSlotSpan ({})'.format(start_dt))
                
            if end_dt is not None:
                if end_dt != self.timeSlotSpan.round_dt(end_dt):
                    raise InputException('Sorry, provided end_dt is not consistent with the timeSlotSpan ({})'.format(end_dt))        
        
        # Set some support varibales
        slot_start_dt      = None
        slot_end_dt        = None
        prev_dataTimePoint      = None
        filtered_dataTimeSeries = DataTimeSeries()
        process_ended      = False

        # Ok, start running the aggregators in a streaming-fashion way,
        # so going trought all the data in the time series
        logger.info('Aggregation process started from {} to {} with a sensor of class {} on {}'.format(start_dt,
                                                                                                       end_dt,
                                                                                                       self.Sensor.__class__.__name__,
                                                                                                       dataTimeSeries))
        # Counters
        callback_counter = 1
        count = 0
        
        for dataTimePoint in dataTimeSeries:

            # Increase counter
            count +=1
            
            # Set start_dt if not already done
            if not start_dt:
                start_dt = self.timeSlotSpan.timeInterval.round_dt(dataTimePoint.dt) if rounded else dataTimePoint.dt
            
            if not slot_end_dt:   
                slot_end_dt = start_dt

            # First, check if we have some points to discard at the beginning       
            if dataTimePoint.dt < start_dt:
                # If we are here it means we are going data belonging to a previous slot
                # (probably just spare data loaded to have access to the prev_datapoint)  
                prev_dataTimePoint = dataTimePoint
                #logger.debug print 'dataTimePoint.dt (disc): ', dataTimePoint.dt
                continue

            # Similar concept for the end
            if dataTimePoint.dt >= end_dt:
                if process_ended:
                    continue


            # Here we manage all the cases according to start/end, missing slots etc.
            # We have also to create empty slots at the beginning, at the end and in the middle.
            # An empty slot will have every required value (according to DataSlots_labels) set to None.
            # Even if the dataTimeSeries is completely empty, we have the DataSlots_labelsthatnks to
            # the Sensor object which is mandatory. And in future maybe even encapsulated in the time series.

            #----------------------------
            # Slots handling
            #----------------------------

            # The following procedure works in general for slots at the beginning and in the middle.
            # The approach is to detect if the current slot is "outdated" and spin a new one if so.

            if dataTimePoint.dt > slot_end_dt:
                # If the current slot is outdated:
                              
                # 1) Add this last point to the dataTimeSeries:
                filtered_dataTimeSeries.append(dataTimePoint)
                 
                #2) keep spinning new slots until the current data point falls in one of them.
                
                # NOTE: Read the following "while" more as an "if" which can also lead to spin multiple
                # slot if there are empty slots between the one being closed and the dataTimePoint.dt.
                # TODO: leave or remove the above if for code readability?
                
                while slot_end_dt < dataTimePoint.dt:
                    
                    # If we are in the pre-first slot, just silently spin a new slot:
                    if slot_start_dt is not None:
                                
                        logger.info('SlotStream: this slot (start={}, end={}) is closed, now aggregating it..'.format(slot_start_dt, slot_end_dt))

                        # Aggregate
                        aggregator_results = self.aggregator.aggregate(dataTimeSeries     = filtered_dataTimeSeries,
                                                                       start_dt           = slot_start_dt,
                                                                       end_dt             = slot_end_dt,
                                                                       timeSlotSpan       = self.timeSlotSpan,
                                                                       raise_if_no_data   = self.raise_if_no_data)
                        # .. and append results 
                        self.results_dataTimeSeries.append(aggregator_results)
                        
                        # Also, handle the callback
                        callback_counter +=1
                        if callback_trigger and callback_counter > callback_trigger:
                            if callback:
                                callback(self, triggerer=self)
                                callback_counter = 1
                    
                    # Create a new slot
                    slot_start_dt = slot_end_dt
                    slot_end_dt   = slot_start_dt + self.timeSlotSpan
                    
                    # Create a new filtered_dataTimeSeries as part of the 'create a new slot' procedure
                    filtered_dataTimeSeries = DataTimeSeries()
                    
                    # Append the previous dataprev_dataTimePoint to the new DataTimeSeries
                    if prev_dataTimePoint:
                        filtered_dataTimeSeries.append(prev_dataTimePoint)

                    logger.info('SlotStream: Spinned a new slot (start={}, end={})'.format(slot_start_dt, slot_end_dt))
                    
                    # If last slot mark process as ended:
                    if dataTimePoint.dt >= end_dt:
                        process_ended = True
                    
       
       
            #----------------------------
            # Time series filtering
            #----------------------------
        
            # Append this point
            filtered_dataTimeSeries.append(dataTimePoint)
            
            # ..and save as previous point
            prev_dataTimePoint =  dataTimePoint           


        #----------------------------
        # Last slots
        #----------------------------        
        force_close_last=False      
        if force_close_last:

            # 1) Close the last slot and aggreagte it. You should never do it unless you knwo what you are doing
            if filtered_dataTimeSeries:
    
                logger.info('SlotStream: this slot (start={}, end={}) is closed, now aggregating it..'.format(slot_start_dt, slot_end_dt))
      
                # Aggregate
                aggregator_results =  self.aggregator.aggregate(dataTimeSeries     = filtered_dataTimeSeries,
                                                                start_dt           = slot_start_dt,
                                                                end_dt             = slot_end_dt,
                                                                timeSlotSpan       = self.timeSlotSpan)
                
                # .. and append results
                self.results_dataTimeSeries.append(aggregator_results)
                
                # Also, handle the callback
                callback_counter +=1
                if callback_trigger and callback_counter > callback_trigger:
                    if callback:
                        callback(self, triggerer=self)
                        callback_counter = 1
                

            # 2) Handle missing slots until the requested end (end_dt)
            # TODO...


        logger.info('Aggregation process ended, processed {} DataTimePoints.'.format(count))
 
    #------------------
    #  Get results
    #------------------
    def get_results(self, until=None):
        if until:
            raise NotImplementedError('getting partial results is not yet supported')
        
        # "Save" current results
        results = self.results_dataTimeSeries
        
        # Empty current results
        self.results_dataTimeSeries =  DataTimeSeries()
        
        return results




#-----------------------
# Utility functions
#-----------------------
def obtain_data_type(dataTimeSeries):
    # Are we processing a DataTimeSeries of Points or Slots?
    if dataTimeSeries.data_type == DataTimePoint:
        return DataTimePoint
        
    elif dataTimeSeries.data_type == DataTimeSlot:
        return DataTimeSlot
        
    elif dataTimeSeries.data_type == None:
        return None
    
    else:
        raise ConsistencyException("Got no DataTimePoint, no DataTimeSlot and not None {}".format(type(dataTimeSeries.data_type))) 

                    












