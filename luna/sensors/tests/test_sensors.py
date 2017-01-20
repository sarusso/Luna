import unittest
from luna.datatypes.dimensional import DataTimeSeries, DataTimePoint, PhysicalDataTimePoint, PhysicalDataTimeSlot, StreamingDataTimeSeries
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException, StorageException
from luna.spacetime.time import dt, TimeSlotSpan
from luna.datatypes.dimensional import TimePoint, Point, PhysicalData
from luna.sensors import PhysicalDataTimeSensor
from luna.storage.sqlite import sqlite


# TODO: this should be a generic storgae test, which is applied to the various modules (whcih can be write or read only)


#------------------------------------
# Logging
#------------------------------------

# Enable only critical logging in unit tests by default
logging.basicConfig(level=logging.CRITICAL) 
logger = logging.getLogger("luna")


#------------------------------------
# Tests
#------------------------------------

class test_sensors(unittest.TestCase):

    def setUp(self):       
        pass


    def test_define_new_Sensor_Volumetric(self):
        
        class VolumetricSensorV1(PhysicalDataTimeSensor):

            # Assign unique type_ID to this sensor type
            type_ID = 5
        
            # Set Points expected lables
            Points_data_labels = ['flowrate_m3s']
            
            # Set Slots operators
            Slots_data_labels  = ['flowrate_m3s_AVG', 'flowrate_m3s_MIN', 'flowrate_m3s_MAX', 'volume_m3_TOT'] 
            
            # Set Validty interval
            Points_validity_interval =  TimeSlotSpan('60s')

        # Test volumetric sensor
        volumetricSensorV1_1 = VolumetricSensorV1('lu65na')
        volumetricSensorV1_2 = VolumetricSensorV1('lu34na')
        
        self.assertEqual(volumetricSensorV1_1.id, 'lu65na')
        self.assertEqual(volumetricSensorV1_2.id, 'lu34na')
        
        self.assertEqual(volumetricSensorV1_1.Points_data_labels, ['flowrate_m3s'])
        self.assertEqual(volumetricSensorV1_2.Slots_data_labels, ['flowrate_m3s_AVG', 'flowrate_m3s_MIN', 'flowrate_m3s_MAX', 'volume_m3_TOT'])


    def test_define_new_Sensor_Electric(self):
        
        class ElectricEnergySensorV1(PhysicalDataTimeSensor):

            # Assign unique type_ID to this sensor type
            type_ID = 6
        
            # Set Points expected lables
            Points_data_labels = ['power_W']
            
            # Set Slots operators
            Slots_data_labels  = ['power_W_AVG', 'power_W_MIN', 'power_W_MAN', 'energy_kWh_TOT'] 
            
            # Set Validity interval
            Points_validity_interval =  TimeSlotSpan('60s')

            # Define custom operation required for energy_kWh_TOT:
            def energy_kWh(self, points_dataTimeSeries, slot_dataTimeSerie):
                return slot_dataTimeSerie
        
        
        electricEnergySensorV1 = ElectricEnergySensorV1('0112233445566/1-MB-3')
        
        # Check ID
        self.assertEqual(electricEnergySensorV1.id, '0112233445566/1-MB-3') 
        
        
    def tearDown(self):
        pass























