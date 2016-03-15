from luna.datatypes.composite import DataTimePoint, DataTimeSlot
from luna.datatypes.composite import PhysicalDataPoint, PhysicalDataSlot, DimensionalDataTimePoint, PhysicalData, PhysicalDataTimeSlot
from luna.datatypes.composite import PhysicalDataTimePoint
from luna.datatypes.dimensional import TimeSlot, TimePoint
from luna.spacetime.time import TimeSlotSpan
from luna.aggregators import operations


class Sensor(object):
    '''This is a  base class that define a sensor. In Luna, a Sensor is
    just a thing that produce some data.
    '''
    
    # An instantiated sensor will have a (unique) id. This is also
    # necessary for storing data (it is used as a primary key)
    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return '{} - {}'.format(self.__class__.__name__, self.id)
    
    # A sensor has its own type_ID and produce some data:    
        
    @property
    def type_ID(self):
        raise NotImplementedError

    @property
    def Points_type(self):
        raise NotImplementedError

    @property
    def Slots_type(self):
        raise NotImplementedError    
    

class TimeSensor(Sensor):
    ''' A time-based sensor is a sensor that produces only time events. A plausible example
    could be a person counter at a shop entrance, and  and it would be typically bound with 
    a TimeSeries (note: not a DataTimeSeries). It is anyway not a real-world example, as some data
    would be always be attached to an event at the end (a '1' in the above example, for instance)'''

    Points_type = TimePoint
    Slots_type  = TimeSlot

    
class DataTimeSensor(TimeSensor):
    '''A time-based data sensor is a sensor that produces time-based data.'''

    # Here we set that Points and slots must be carry data, by setting the type...
    Points_type = DataTimePoint
    Slots_type  = DataTimeSlot

    # ...but we do not say anything about the labels that will be used to actually label the data.

    @property
    def Points_data_labels(self):
        raise NotImplementedError

    @property
    def Slots_data_labels(self):
        raise NotImplementedError

    # The validity interval value has also to be set. It is per-sensor,
    # as it is assumed that every physical sensor behaves in the same way.
    # You can also set it to None and use a dynamic (per Point) validty
    # interval according to the storage, but this feature is still in alpha phase.
    # The validity interval is a very delicate concept to be crefully evaluated
    # according to the discretization of the continuum space, please refer
    # to the documentation for more informations
    
    @property
    def Points_validity_interval(self):
        raise NotImplementedError  
    
class PhysicalDataTimeSensor(DataTimeSensor):
    '''A time-based data sensor is a sensor that produces time-based physical data.'''

    # Here we set that Points and slots must be carry physical data
    Points_type = PhysicalDataTimePoint
    Slots_type  = PhysicalDataTimeSlot
    
    # ..the lables has still to be set.

    # Plus, we have a call to understand the minimal set of PhysicalQuantities required
    # So the ones from which everything else is computed (Sure?).. at least for the slot..
    


# For and example usage, see the unit test of this package,
# where you will find a VolumetricSensorV1 sensor implemented.



    
