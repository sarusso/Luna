import unittest
from luna.datatypes.composite import DataTimeSeries, DataTimePoint, PhysicalDataTimePoint, PhysicalDataTimeSlot, StreamingDataTimeSeries
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException, StorageException
from luna.spacetime.time import dt, TimeSlotSpan
from luna.datatypes.dimensional import TimePoint, Point, PhysicalData
from luna.sensors import PhysicalDataTimeSensor
from luna.storage.sqlite import sqlite
from luna.aggregators.generators import PhysicalQuantityGenerator
from luna.aggregators.components import DataTimeSeriesAggregatorProcess
import os

datasets_path= '/'.join(os.path.realpath(__file__).split('/')[0:-1]) + '/datasets/'

#------------------------------------
# Define test sensor
#------------------------------------

class EnergyElectricExtendedTriphase(PhysicalDataTimeSensor):

    # Assign unique type_ID to this sensor type
    type_ID = 5

    # Set Points expected lables
    Points_data_labels = [ "power-l1_W", 
                           "current-l1_A", 
                           "voltage-l1_V",
                           "rpower-l1_VAr",
                           # ---------------- 
                           "power-l2_W", 
                           "current-l2_A", 
                           "voltage-l2_V",
                           "rpower-l2_VAr",
                           # ----------------
                           "power-l3_W", 
                           "current-l3_A", 
                           "voltage-l3_V",
                           "rpower-l3_VAr" ]
    
    # Set Slots operators
    Slots_data_labels =  [ "power-l1_W_AVG", "power-l1_W_MIN", "power-l1_W_MAX",
                           "current-l1_A_AVG", 
                           "voltage-l1_V_AVG",
                           "rpower-l1_VAr_AVG",
                           # ---------------- 
                           "power-l2_W_AVG", "power-l2_W_MIN", "power-l2_W_MAX",
                           "current-l2_A_AVG", 
                           "voltage-l2_V_AVG",
                           "rpower-l2_VAr_AVG",
                           # ----------------
                           "power-l3_W_AVG", "power-l3_W_MIN", "power-l3_W_MAX",
                           "current-l3_A_AVG", 
                           "voltage-l3_V_AVG",
                           "rpower-l3_VAr_AVG",
                           # ----------------
                           "power_W_AVG",
                            ]
       
    # Set validity region span for points
    Points_validity_region_span = TimeSlotSpan('2m')
    
    # Fixed timezone:
    timezone = "Europe/Rome"
    
    class power_W_AVG(PhysicalQuantityGenerator):
        '''Power generator for the triphase sensor. Expects to work on power-l1_W_AVG, power-l2_W_AVG and power-l3_W_AVG'''

        # Generator code
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):
            return 10


#------------------------------------
# Tests
#------------------------------------

class test_aggregators(unittest.TestCase):

    def setUp(self):       
        pass


    def test_Extended_Aggregation(self):    

        # Define sensor and boundaries
        sensor = EnergyElectricExtendedTriphase('084EB18E44FFA/7-MB-1')
        from_dt = dt(2016,3,25,9,58,0, tzinfo=sensor.timezone) # last was at 2016-03-25T14:09:45+00:00
        to_dt   = dt(2016,3,25,10,32,0, tzinfo=sensor.timezone)
        
        # Load dataset
        dataTimeSeriesSQLiteStorage = sqlite.DataTimeSeriesSQLiteStorage(in_memory=False, right_to_initialize=True, db_file=datasets_path + 'dataset1.sqlite')
        out_streamingDataTimeSeries = dataTimeSeriesSQLiteStorage.get(sensor=sensor)

        dataTimeSeriesAggregatorProcess = DataTimeSeriesAggregatorProcess(timeSlotSpan      = TimeSlotSpan('15m'),
                                                                          Sensor            = sensor,
                                                                          data_to_aggregate = PhysicalDataTimePoint)


        # Aggregate
        dataTimeSeriesAggregatorProcess.start(dataTimeSeries = out_streamingDataTimeSeries,
                                              start_dt       = from_dt,
                                              end_dt         = to_dt,
                                              rounded        = True,
                                              threaded       = False)
        
        # Get results
        aggregated_dataTimeSeries = dataTimeSeriesAggregatorProcess.get_results(until=None)
        
        # Quick check results using string representations
        i = 0
        for slot in aggregated_dataTimeSeries:
            if i == 0:
                self.assertEqual(str(slot), '''PhysicalDataTimeSlot: from 2016-03-25 10:00:00+01:00 to 2016-03-25 10:15:00+01:00 with span of 15m and coverage of 1.0''')
                self.assertEqual(str(slot.data.content),'''{'voltage-l2_V_AVG': 225.25098735321004, 'power-l3_W_MIN': 239.921875, 'power-l1_W_MAX': 1397.734375, 'current-l2_A_AVG': 4.33984155812967, 'current-l1_A_AVG': 5.129787381841492, 'rpower-l1_VAr_AVG': -944.949067679558, 'power-l3_W_AVG': 513.0145029310386, 'power_W_AVG': 10, 'voltage-l1_V_AVG': 226.96192316719885, 'voltage-l3_V_AVG': 225.65243985509946, 'current-l3_A_AVG': 2.7271999970325416, 'rpower-l3_VAr_AVG': -161.74076312154696, 'power-l3_W_MAX': 1508.359375, 'power-l2_W_MIN': 763.359375, 'power-l1_W_AVG': 579.0542988645415, 'power-l2_W_MAX': 1786.484375, 'power-l2_W_AVG': 877.2142610497237, 'power-l1_W_MIN': 459.453125, 'rpower-l2_VAr_AVG': -255.91030723613812}''') 
            elif i == 1:
                self.assertEqual(str(slot), '''PhysicalDataTimeSlot: from 2016-03-25 10:15:00+01:00 to 2016-03-25 10:30:00+01:00 with span of 15m and coverage of 1.0''')
                self.assertEqual(str(slot.data.content),'''{'voltage-l2_V_AVG': 225.05988972978878, 'power-l3_W_MIN': 242.65625, 'power-l1_W_MAX': 2622.1875, 'current-l2_A_AVG': 6.159258524577058, 'current-l1_A_AVG': 6.836917453341555, 'rpower-l1_VAr_AVG': -947.703125, 'power-l3_W_AVG': 1022.2148435804556, 'power_W_AVG': 10, 'voltage-l1_V_AVG': 226.6195936414945, 'voltage-l3_V_AVG': 225.09531690809425, 'current-l3_A_AVG': 5.0118459065758305, 'rpower-l3_VAr_AVG': -127.13845494588334, 'power-l3_W_MAX': 3423.203125, 'power-l2_W_MIN': 763.046875, 'power-l1_W_AVG': 1037.8454871283664, 'power-l2_W_MAX': 2827.265625, 'power-l2_W_AVG': 1269.431423611111, 'power-l1_W_MIN': 508.90625, 'rpower-l2_VAr_AVG': -259.2868923611111}''')
            else:
                raise Exception('Test failed')
            i +=1
                
        if i != 2:
            raise Exception('Test failed')




