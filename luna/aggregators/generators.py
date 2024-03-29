from luna.datatypes.auxiliary import Quantity, PhysicalQuantity

#------------------------------
# Base classes
#------------------------------

class QuantityGenerator(object):
    '''A QuantityGenerator is an operation that generates a new Quantity. It is applied in the
    aggregation from Points to Slots. This class is here as logical placeholder for future extensions'''
    
    # Depends
    @property
    def depends(self):
        '''List of string representations of Quantities required'''
        raise NotImplementedError
    
    # Provides
    @property
    def provides(self):
        '''List of string representations of Quantities provided'''
        raise NotImplementedError 
    
    # Generator code
    @staticmethod
    def generate(dataSeries, aggregated_data, start_Point, end_Point):
        raise NotImplementedError()
    
    # Data type
    _data_type = Quantity


class PhysicalQuantityGenerator(object):
    '''A PhysicalQuantityGenerator is an operation that generates a new PhysicalQuantity, or and
    aggregated PhysicalQuantity (with an operation already applied to it). Generator are selected
    according to the Sensor objects and applied in the the aggregation from Points to Slots phase.
    
    Generated PhysicalQuantites can be both generated in the source Points DataTimeSeries or in
    the destination Slots DataTimeSeries, depending if they have an operation applied or not.

    For example, if your generator provides "power_W" this quantity will be added to the Points of the
    source DataTimeSeries, while if it generates 'energy_kWh_TOT' this quantity it will be added to the 
    destination Slots DataTimeSeries as there is an aggregation operation (TOT) applied to it.
    
    You can also depend on already aggregated quantities (i.e. power-l1_W_AVG, power-l2_W_AVG, power-l3_W_AVG)
    to provide another aggregated quantity (i.e. power_W_AVG), even if depending on the use case it might be
    better or necessary to perform the operation point by point (So generating power_W from power-l1_W, power-l2_W and
    power-l3_W and then applying power_W_AVG).
     '''
    
    # Depends
    @property
    def depends(self):
        '''List of string representations of PhysicalQuantities required'''
        raise NotImplementedError
    
    # Provides
    @property
    def provides(self):
        '''List of string representations of PhysicalQuantities provided'''
        raise NotImplementedError 
    
    # Generator code
    @staticmethod
    def generate(dataSeries, aggregated_data, start_Point, end_Point):
        raise NotImplementedError()
    
    # Data type
    _data_type = PhysicalQuantity


#------------------------------
# Standard generators
#------------------------------

class energy_kWh_TOT(PhysicalQuantityGenerator):
    '''Energy generator. Expect to work on power_W_AVG'''
    
    # Depends
    depends = ['power_W_AVG'] 

    # Generator code
    @staticmethod
    def generate(dataSeries, aggregated_data, start_Point, end_Point):
        return -9

















