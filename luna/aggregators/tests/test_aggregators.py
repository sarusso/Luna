import unittest
from luna.datatypes.dimensional import DataTimeSeries, DataTimePoint, PhysicalDataTimePoint, PhysicalDataTimeSlot, StreamingDataTimeSeries
from luna.datatypes.dimensional import *
from luna.common.exceptions import InputException, StorageException
from luna.spacetime.time import dt, TimeSlotSpan
from luna.datatypes.dimensional import TimePoint, Point, PhysicalData
from luna.sensors import PhysicalDataTimeSensor
from luna.storage.sqlite import sqlite
from luna.aggregators.generators import PhysicalQuantityGenerator
from luna.aggregators.components import DataTimeSeriesAggregatorProcess
import os


#------------------------------------
# Logging
#------------------------------------

#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger("luna")



datasets_path= '/'.join(os.path.realpath(__file__).split('/')[0:-1]) + '/datasets/'

#------------------------------------
# Define test sensors
#------------------------------------

class SimpleSensor(PhysicalDataTimeSensor):
    type_ID = 1
    Points_data_labels = ['temp_C']
    Points_validity_region = TimeSlot(span='1m')
    Slots_data_labels =  ['temp_C_AVG', 'temp_C_MIN', 'temp_C_MAX']
    timezone = 'Europe/Rome'

class EnergyElectricExtendedTriphase(PhysicalDataTimeSensor):

    # Assign unique type_ID to this sensor type
    type_ID = 5

    # Set Points expected labels
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
    Slots_data_labels =  [ # == Operations ==
                           "power-l1_W_AVG", "power-l1_W_MIN", "power-l1_W_MAX",
                           "current-l1_A_AVG", "current-l1_A_MIN", "current-l1_A_MAX",
                           "voltage-l1_V_AVG", "voltage-l1_V_MIN", "voltage-l1_V_MAX",
                           "rpower-l1_VAr_AVG", "rpower-l1_VAr_MIN", "rpower-l1_VAr_MAX",
                           # ---------------- 
                           "power-l2_W_AVG", "power-l2_W_MIN", "power-l2_W_MAX",
                           "current-l2_A_AVG", "current-l2_A_MIN", "current-l2_A_MAX",
                           "voltage-l2_V_AVG", "voltage-l2_V_MIN", "voltage-l2_V_MAX",
                           "rpower-l2_VAr_AVG", "rpower-l2_VAr_MIN", "rpower-l2_VAr_MAX",
                           # ----------------
                           "power-l3_W_AVG", "power-l3_W_MIN", "power-l3_W_MAX",
                           "current-l3_A_AVG", "current-l3_A_MIN", "current-l3_A_MAX",
                           "voltage-l3_V_AVG", "voltage-l3_V_MIN", "voltage-l3_V_MAX",
                           "rpower-l3_VAr_AVG", "rpower-l3_VAr_MIN", "rpower-l3_VAr_MAX",
                           # == Generators ==
                           "power_W_AVG", "power_W_MIN", "power_W_MAX",
                           "current_A_AVG", "current_A_MIN", "current_A_MAX",
                           "voltage_V_AVG", "voltage_V_MIN", "voltage_V_MAX",
                           "rpower_VAr_AVG", "rpower_VAr_MIN", "rpower_VAr_MAX"]
       
    # Set validity region span for points
    Points_validity_region = TimeSlot(span='2m')
    
    # Fixed timezone:
    timezone = "Europe/Rome"
    
    # Generators for Power
    class power_W_AVG(PhysicalQuantityGenerator):
        '''Power AVG generator for the triphase sensor. Expects to work on power-l1_W_AVG, power-l2_W_AVG and power-l3_W_AVG'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):   # TODO:   dataSeries-> Points_dataSeries, aggregated_data -> Slot something
            return aggregated_data.content['power-l1_W_AVG'] + aggregated_data.content['power-l2_W_AVG'] + aggregated_data.content['power-l3_W_AVG']

    class power_W_MIN(PhysicalQuantityGenerator):
        '''Power MIN generator for the triphase sensor. Expects to work on power-l1_W_MIN, power-l2_W_MIN and power-l3_W_MIN'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['power-l1_W_MIN'] + aggregated_data.content['power-l2_W_MIN'] + aggregated_data.content['power-l3_W_MIN']
    
    class power_W_MAX(PhysicalQuantityGenerator):
        '''Power MAX generator for the triphase sensor. Expects to work on power-l1_W_MAX, power-l2_W_MAX and power-l3_W_MAX'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['power-l1_W_MAX'] + aggregated_data.content['power-l2_W_MAX'] + aggregated_data.content['power-l3_W_MAX']

    # Generators for Current
    class current_A_AVG(PhysicalQuantityGenerator):
        '''current AVG generator for the triphase sensor. Expects to work on current-l1_A_AVG, current-l2_A_AVG and current-l3_A_AVG'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):   # TODO:   dataSeries-> Points_dataSeries, aggregated_data -> Slot something
            return aggregated_data.content['current-l1_A_AVG'] + aggregated_data.content['current-l2_A_AVG'] + aggregated_data.content['current-l3_A_AVG']

    class current_A_MIN(PhysicalQuantityGenerator):
        '''current MIN generator for the triphase sensor. Expects to work on current-l1_A_MIN, current-l2_A_MIN and current-l3_A_MIN'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['current-l1_A_MIN'] + aggregated_data.content['current-l2_A_MIN'] + aggregated_data.content['current-l3_A_MIN']
    
    class current_A_MAX(PhysicalQuantityGenerator):
        '''current MAX generator for the triphase sensor. Expects to work on current-l1_A_MAX, current-l2_A_MAX and current-l3_A_MAX'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['current-l1_A_MAX'] + aggregated_data.content['current-l2_A_MAX'] + aggregated_data.content['current-l3_A_MAX']

    # Generators for Voltage
    class voltage_V_AVG(PhysicalQuantityGenerator):
        '''voltage AVG generator for the triphase sensor. Expects to work on voltage-l1_V_AVG, voltage-l2_V_AVG and voltage-l3_V_AVG'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):   # TODO:   dataSeries-> Points_dataSeries, aggregated_data -> Slot something
            return aggregated_data.content['voltage-l1_V_AVG'] + aggregated_data.content['voltage-l2_V_AVG'] + aggregated_data.content['voltage-l3_V_AVG']

    class voltage_V_MIN(PhysicalQuantityGenerator):
        '''voltage MIN generator for the triphase sensor. Expects to work on voltage-l1_V_MIN, voltage-l2_V_MIN and voltage-l3_V_MIN'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['voltage-l1_V_MIN'] + aggregated_data.content['voltage-l2_V_MIN'] + aggregated_data.content['voltage-l3_V_MIN']
    
    class voltage_V_MAX(PhysicalQuantityGenerator):
        '''voltage MAX generator for the triphase sensor. Expects to work on voltage-l1_V_MAX, voltage-l2_V_MAX and voltage-l3_V_MAX'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['voltage-l1_V_MAX'] + aggregated_data.content['voltage-l2_V_MAX'] + aggregated_data.content['voltage-l3_V_MAX']


    # Generators for RPower
    class rpower_VAr_AVG(PhysicalQuantityGenerator):
        '''rpower AVG generator for the triphase sensor. Expects to work on rpower-l1_VAr_AVG, rpower-l2_VAr_AVG and rpower-l3_VAr_AVG'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):   # TODO:   dataSeries-> Points_dataSeries, aggregated_data -> Slot something
            return aggregated_data.content['rpower-l1_VAr_AVG'] + aggregated_data.content['rpower-l2_VAr_AVG'] + aggregated_data.content['rpower-l3_VAr_AVG']

    class rpower_VAr_MIN(PhysicalQuantityGenerator):
        '''rpower MIN generator for the triphase sensor. Expects to work on rpower-l1_VAr_MIN, rpower-l2_VAr_MIN and rpower-l3_VAr_MIN'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['rpower-l1_VAr_MIN'] + aggregated_data.content['rpower-l2_VAr_MIN'] + aggregated_data.content['rpower-l3_VAr_MIN']
    
    class rpower_VAr_MAX(PhysicalQuantityGenerator):
        '''rpower MAX generator for the triphase sensor. Expects to work on rpower-l1_VAr_MAX, rpower-l2_VAr_MAX and rpower-l3_VAr_MAX'''
        @staticmethod
        def generate(dataSeries, aggregated_data, start_Point, end_Point):    
            return aggregated_data.content['rpower-l1_VAr_MAX'] + aggregated_data.content['rpower-l2_VAr_MAX'] + aggregated_data.content['rpower-l3_VAr_MAX']    


#------------------------------------
# Tests
#------------------------------------

class test_aggregators(unittest.TestCase):

    def setUp(self):       
        pass

    def test_Simple_Aggregation(self):   

        sensor = SimpleSensor('084EB18E44FFA/7-MB-1')
        from_dt = dt(2016,3,25,9,58,0, tzinfo=sensor.timezone) # last was at 2016-03-25T14:09:45+00:00
        to_dt   = dt(2016,3,25,10,32,0, tzinfo=sensor.timezone)

        dataTimeSeries = DataTimeSeries()
        slider_dt = from_dt
        while slider_dt < to_dt:
            
            data = PhysicalData( labels = ['temp_C'], values = [25.5] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(dt   = slider_dt,
                                                          data = data,
                                                          validity_region = sensor.Points_validity_region)
            dataTimeSeries.append(physicalDataTimePoint)
            slider_dt = slider_dt + TimeSlotSpan('1m')
            
        dataTimeSeriesAggregatorProcess = DataTimeSeriesAggregatorProcess(timeSlotSpan      = TimeSlotSpan('15m'),
                                                                          Sensor            = sensor,
                                                                          data_to_aggregate = PhysicalDataTimePoint)


        # Aggregate
        dataTimeSeriesAggregatorProcess.start(dataTimeSeries = dataTimeSeries,
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
                self.assertEqual(str(slot), '''PhysicalDataTimeSlot: from 2016-03-25 10:00:00+01:00 to 2016-03-25 10:15:00+01:00 with span of 15m''')
                self.assertEqual(slot.data.content, {'temp_C_MAX': 25.5, 'temp_C_AVG': 25.5, 'temp_C_MIN': 25.5})
                self.assertEqual(slot.coverage, 1.0)
            elif i == 1:
                self.assertEqual(str(slot), '''PhysicalDataTimeSlot: from 2016-03-25 10:15:00+01:00 to 2016-03-25 10:30:00+01:00 with span of 15m''')
                self.assertEqual(slot.data.content, {'temp_C_MAX': 25.5, 'temp_C_AVG': 25.5, 'temp_C_MIN': 25.5})
                self.assertEqual(slot.coverage, 1.0)
            else:
                raise Exception('Test failed')
            i +=1
                
        if i != 2:
            raise Exception('Test failed')




    def test_Extended_Aggregation(self):    

        # Define sensor and boundaries
        sensor = EnergyElectricExtendedTriphase('084EB18E44FFA/7-MB-1')
        from_dt = dt(2016,3,25,9,58,0, tzinfo=sensor.timezone) # last was at 2016-03-25T14:09:45+00:00
        to_dt   = dt(2016,3,25,10,32,0, tzinfo=sensor.timezone)
        
        # Load dataset
        dataTimeSeriesSQLiteStorage = sqlite.DataTimeSeriesSQLiteStorage(in_memory=False, can_initialize=True, db_file=datasets_path + 'dataset1.sqlite')
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
        
        # Quick check of results using string representations
        i = 0
        for slot in aggregated_dataTimeSeries:

            if i == 0:
                self.assertEqual(str(slot), '''PhysicalDataTimeSlot: from 2016-03-25 10:00:00+01:00 to 2016-03-25 10:15:00+01:00 with span of 15m''')
                self.assertEqual(slot.data.content, {'current-l1_A_MIN': 4.73419189453, 'power_W_MAX': 4692.578125, 'current-l2_A_AVG': 4.0533920211715415, 'power-l1_W_AVG': 540.6015902259898, 'power-l3_W_AVG': 470.55743272105127, 'voltage-l1_V_MIN': 225.48248291, 'current-l1_A_MAX': 7.78015136719, 'rpower-l3_VAr_AVG': -157.16330377842402, 'power_W_MIN': 1462.734375, 'power-l2_W_AVG': 819.5026008426315, 'rpower-l1_VAr_MIN': -984.765625, 'voltage-l2_V_AVG': 210.6090310856981, 'current_A_AVG': 11.355183299930056, 'voltage-l1_V_MAX': 228.475524902, 'current_A_MIN': 9.98733520507, 'voltage_V_AVG': 633.851065817629, 'rpower-l1_VAr_MAX': -832.109375, 'power-l3_W_MAX': 1508.359375, 'power-l1_W_MIN': 459.453125, 'current-l2_A_MAX': 8.64349365234, 'power-l1_W_MAX': 1397.734375, 'current-l1_A_AVG': 4.792555512310997, 'current_A_MAX': 27.026062011729998, 'current-l3_A_AVG': 2.509235766447517, 'power-l2_W_MAX': 1786.484375, 'voltage_V_MIN': 671.593444824, 'current-l2_A_MIN': 3.82629394531, 'voltage-l2_V_MAX': 227.123535156, 'voltage-l3_V_MAX': 226.735778809, 'rpower_VAr_AVG': -1278.5843967083001, 'voltage-l2_V_MIN': 223.11126709, 'rpower_VAr_MIN': -1558.984375, 'rpower-l2_VAr_MIN': -271.875, 'power-l3_W_MIN': 239.921875, 'rpower_VAr_MAX': -936.796875, 'rpower-l1_VAr_AVG': -882.3312162472556, 'voltage-l3_V_AVG': 211.01158331126413, 'rpower-l3_VAr_MIN': -302.34375, 'current-l3_A_MAX': 10.6024169922, 'power_W_AVG': 1830.6616237896726, 'rpower-l2_VAr_MAX': -138.125, 'voltage-l3_V_MIN': 222.999694824, 'power-l2_W_MIN': 763.359375, 'rpower-l2_VAr_AVG': -239.08987668262057, 'voltage_V_MAX': 682.3348388669999, 'voltage-l1_V_AVG': 212.23045142066678, 'current-l3_A_MIN': 1.42684936523, 'rpower-l3_VAr_MAX': 33.4375}) 
                self.assertEqual(slot.coverage, 1.0)
            elif i == 1:
                self.assertEqual(str(slot), '''PhysicalDataTimeSlot: from 2016-03-25 10:15:00+01:00 to 2016-03-25 10:30:00+01:00 with span of 15m''')
                self.assertEqual(slot.data.content, {'current-l1_A_MIN': 4.96215820312, 'power_W_MAX': 8872.65625, 'current-l2_A_AVG': 5.699640351268045, 'power-l1_W_AVG': 964.0598380394166, 'power-l3_W_AVG': 953.2915566854815, 'voltage-l1_V_MIN': 224.033081055, 'current-l1_A_MAX': 12.7659606934, 'rpower-l3_VAr_AVG': -118.72267023945415, 'power_W_MIN': 1514.609375, 'power-l2_W_AVG': 1173.7198022850064, 'rpower-l1_VAr_MIN': -998.515625, 'voltage-l2_V_AVG': 210.49519544251942, 'current_A_AVG': 16.774708245197594, 'voltage-l1_V_MAX': 228.413879395, 'current_A_MIN': 10.259704589840002, 'voltage_V_AVG': 632.8933605279044, 'rpower-l1_VAr_MAX': -835.15625, 'power-l3_W_MAX': 3423.203125, 'power-l1_W_MIN': 508.90625, 'current-l2_A_MAX': 13.1994628906, 'power-l1_W_MAX': 2622.1875, 'current-l1_A_AVG': 6.397570106683291, 'current_A_MAX': 39.8182678223, 'current-l3_A_AVG': 4.677497787246258, 'power-l2_W_MAX': 2827.265625, 'voltage_V_MIN': 667.559875488, 'current-l2_A_MIN': 3.86245727539, 'voltage-l2_V_MAX': 226.949768066, 'voltage-l3_V_MAX': 227.482421875, 'rpower_VAr_AVG': -1255.8022510368125, 'voltage-l2_V_MIN': 221.975952148, 'rpower_VAr_MIN': -1618.28125, 'rpower-l2_VAr_MIN': -316.953125, 'power-l3_W_MIN': 242.65625, 'rpower_VAr_MAX': -830.15625, 'rpower-l1_VAr_AVG': -891.1710790467758, 'voltage-l3_V_AVG': 210.47687837363117, 'rpower-l3_VAr_MIN': -302.8125, 'current-l3_A_MAX': 13.8528442383, 'power_W_AVG': 3091.0711970099046, 'rpower-l2_VAr_MAX': -81.875, 'voltage-l3_V_MIN': 221.550842285, 'power-l2_W_MIN': 763.046875, 'rpower-l2_VAr_AVG': -245.90850175058262, 'voltage_V_MAX': 682.846069336, 'voltage-l1_V_AVG': 211.92128671175377, 'current-l3_A_MIN': 1.43508911133, 'rpower-l3_VAr_MAX': 86.875})
                self.assertEqual(slot.coverage, 1.0)
            else:
                raise Exception('Test failed')
            i +=1
                
        if i != 2:
            raise Exception('Test failed')




