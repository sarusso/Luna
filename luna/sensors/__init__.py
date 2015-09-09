from luna.datatypes.composite import DataTimePoint, DataTimeSlot
from luna.datatypes.composite import PhysicalDataPoint, PhysicalDataSlot, DimensionalDataTimePoint, PhysicalDimensionalData
from luna.datatypes.composite import TimeSeries
from luna.datatypes.composite import PhysicalDataTimePoint
from luna.datatypes.dimensional import TimeSlot
from luna.spacetime.time import TimeInterval
from luna.aggregators import operations


class Sensor(object):
    '''This is a  base class that define a sensor. In Luna, a Sensor is a thing that produce some data, and ca represent
    whatever you feel like - a Sensor, a log collector, a webcam.. 
    '''
    
    # An instantiated sensor will have a (unique) id
    def __init__(self, id):
        self.id = id
    
    # A sensor has its own type_ID and prodeuce some data:    
        
    @property
    def type_ID(self): #TODO: Sure!?
        raise NotImplementedError

    @property
    def data_type(self):
        raise NotImplementedError

    # .. and for now they are not implemented and that's it.
    

class TimeBasedSensor(Sensor):
    ''' A time-based sensor is a sensor thta produces time-based data.'''
    
    data_type = DataTimePoint # Could alse be DataTimeSlot
    
    
class TimeBasedDimensionalDataSensor(TimeBasedSensor):
    '''This Sensor is menat to produce dimensional data. DimensionalData is menat to be int or float data, and the most common
    example is latituted and longitude'''
    
    data_type = DimensionalDataTimePoint
    
    @property
    def Points_data_labels(self):
        raise NotImplementedError        

    # We can define common operations on Dimensional data, as MIN, MAX, AVG when we aggregate Points in Slots:
    Points_data_to_Slots_data_ops = ['MIN', 'MAX', 'AVG']

    # We can let extension of this class to have extra (and user-defined) ops:
    Points_data_to_Slots_data_extra_ops =[]

    # We also need a mapping telling which operations have to be applied on which label, and which label generates.
    # By defualt, whe apply the ops to each label

    # Note: Once a slot is created, the operations are not modifiable wnymore whan aggregating from Slots to a bigger Slot.
    # i.e. if you create MIN MAX AVG when aggregatting from Points to Slots, you will always carry them in the aggregations

    # By default, we apply the Points_to_Slots_ops to every label
    
    # TODO: this mapping has to be a MATRIX!!!
   
    Points_to_Slots_ops_mapping = {}
    '''
    power_W -> power_W_MIN, power_W_MAX, power_W_AVG
    power_W_peaks
    '''
    #Points_to_Slots_ops_mapping = {label:Points_to_Slots_ops_mapping for label in Points_data_labels}


    # A DimensionalDataSensor one aggregated in a Slot has some Slot dat labels once aggregated:
    @property
    def Slots_data_labels(self):
        Slots_data_labels = ['....compute them....']
        return Slots_data_labels
        


   
class TimeBasedPhysicalDataSensor(TimeBasedSensor):
    '''This Sensor is menat to produce physical data. PhysicalData is a particular type of Dimensional Data where each dimensiona
    has to be a valid PhysicalQuantity. A common example is a Sensor which monitor water flow and temperature: The PhysicalData would be
    bi-dimensional (one dimension is the flow, the second dimesnion is the temperature). The TimeBasedPhysicalDataSensor knows how to aggrgeate
    intensive and extensive metrics.'''
    
    data_type   = PhysicalDataTimePoint
    data_data_type = PhysicalDimensionalData
    
    # TODO: handle intensive/extensive here?


class VolumetricSensorV1(TimeBasedPhysicalDataSensor):

    # Assign unique type_ID to thing type
    type_ID = 5
    
    # Set (override) data_content_Points_labels
    Points_data_labels = ['flowrate_m3s'] #Mandatory
    Points_validity_interval =  TimeInterval('60s') # Validty Slot type, or don't set it or set it to None if you implement it in the storage to have variable validity
    
    Slots_data_labels  = ['flowrate_m3s_i_AVG', 'flowrate_m3s_i_MIN', 'flowrate_m3s_i_MAX', 'volume_m3_e_TOT']


















    
