import unittest
from luna.datatypes.dimensional import TimePoint
from luna.datatypes.dimensional import DataTimePoint, PhysicalData, PhysicalDataTimePoint, DataTimeSeries, TimeSlot
from luna.aggregators.utilities import compute_1D_coverage, clean_and_reconstruct
from luna.common.exceptions import InputException
from luna.spacetime.time import dt, TimeSlotSpan, correct_dt_dst, timezonize, s_from_dt
import datetime
import logging
import os

# Logging
log_level = os.environ.get('LUNA_LOG_LEVEL', 'CRITICAL')
logging.basicConfig(level=log_level)
logger = logging.getLogger("luna")


#====================
# Test 1D coverage
#====================
class test_compute_1D_coverage(unittest.TestCase):

    def setUp(self):       
        
        # TimeSeries from 16:58:00 to 17:32:00 (Europe/Rome)
        self.dataTimeSeries1 = DataTimeSeries()
        start_t = 1436022000 - 120
        validity_region = TimeSlot(span='1m')          
        for i in range(35):
            data = PhysicalData( labels = ['power_W'], values = [154+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t    = start_t + (i*60),
                                                          tz   ="Europe/Rome",
                                                          data =data,
                                                          validity_region = validity_region)
            self.dataTimeSeries1.append(physicalDataTimePoint)
        
        # TimeSeries from 17:00:00 to 17:30:00 (Europe/Rome)
        self.dataTimeSeries2 = DataTimeSeries()
        start_t = 1436022000
        validity_region = TimeSlot(span='1m')          
        for i in range(34):
            data = PhysicalData( labels = ['power_W'], values = [154+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t    = start_t + (i*60),
                                                          tz   = "Europe/Rome",
                                                          data = data,
                                                          validity_region = validity_region)
            self.dataTimeSeries2.append(physicalDataTimePoint)

        # TimeSeries from 17:00:00 to 17:20:00 (Europe/Rome)
        self.dataTimeSeries3 = DataTimeSeries()
        start_t = 1436022000 - 120
        validity_region = TimeSlot(span='1m')          
        for i in range(23):
            data = PhysicalData( labels = ['power_W'], values = [154+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t    = start_t + (i*60),
                                                          tz   = "Europe/Rome",
                                                          data = data,
                                                          validity_region = validity_region)
            self.dataTimeSeries3.append(physicalDataTimePoint) 
        
        # TimeSeries from 17:10:00 to 17:30:00 (Europe/Rome)
        self.dataTimeSeries4 = DataTimeSeries()
        start_t = 1436022000 + 600
        validity_region = TimeSlot(span='1m')          
        for i in range(21):
            data = PhysicalData( labels = ['power_W'], values = [154+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t    = start_t + (i*60),
                                                          tz   = "Europe/Rome",
                                                          data = data,
                                                          validity_region = validity_region)
            self.dataTimeSeries4.append(physicalDataTimePoint)

        # TimeSeries from 16:58:00 to 17:32:00 (Europe/Rome)
        self.dataTimeSeries5 = DataTimeSeries()
        start_t = 1436022000 - 120
        validity_region = TimeSlot(span='1m')          
        for i in range(35):
            if i > 10 and i <21:
                continue
            data = PhysicalData( labels = ['power_W'], values = [154+i] ) 
            physicalDataTimePoint = PhysicalDataTimePoint(t    = start_t + (i*60),
                                                          tz   ="Europe/Rome",
                                                          data =data,
                                                          validity_region = validity_region)
            self.dataTimeSeries5.append(physicalDataTimePoint)


        
    def test_compute_1D_coverage_basic(self):
        
        #----------------------------
        # Test wrong init parameters
        #----------------------------
        with self.assertRaises(InputException):
            compute_1D_coverage(dataSeries = None, start_Point = None, end_Point = None)  
        with self.assertRaises(NotImplementedError):
            compute_1D_coverage(dataSeries = self.dataTimeSeries1, start_Point = None, end_Point = None)  
        with self.assertRaises(InputException):
            compute_1D_coverage(dataSeries = self.dataTimeSeries1, start_Point = 5, end_Point = TimePoint(t=3)) 
        with self.assertRaises(InputException):
            compute_1D_coverage(dataSeries = self.dataTimeSeries1, start_Point = TimePoint(t=3), end_Point = 5) 


        #----------------------------
        # Test logic
        #----------------------------
        
        # Full coverage (coverage=1.0)
        start_Point = TimePoint(t=1436022000,      tz='Europe/Rome')  # 2015-07-04 17:00:00+02:00
        end_Point   = TimePoint(t=1436022000+1800, tz='Europe/Rome')  # 2015-07-04 17:30:00+02:00
        Slot_coverage = compute_1D_coverage(dataSeries  = self.dataTimeSeries1,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)  
        self.assertEqual(Slot_coverage, 1.0)
         
        # A) Full coverage (coverage=1.0) again, to test repeatability 
        start_Point = TimePoint(t=1436022000,      tz='Europe/Rome')  # 2015-07-04 17:00:00+02:00
        end_Point   = TimePoint(t=1436022000+1800, tz='Europe/Rome')  # 2015-07-04 17:30:00+02:00
        Slot_coverage = compute_1D_coverage(dataSeries  = self.dataTimeSeries1,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)  
        self.assertEqual(Slot_coverage, 1.0)        
 
        # B) Full coverage (coverage=1.0) witjout prev/next in the timeSeries 
        start_Point = TimePoint(t=1436022000,      tz='Europe/Rome')  # 2015-07-04 17:00:00+02:00
        end_Point   = TimePoint(t=1436022000+1800, tz='Europe/Rome')  # 2015-07-04 17:30:00+02:00
        Slot_coverage = compute_1D_coverage(dataSeries  = self.dataTimeSeries2,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)  
        self.assertEqual(Slot_coverage, 1.0)  

        # C) Missing ten minutes over 30 at the end (coverage=0.683))
        start_Point = TimePoint(t=1436022000,      tz='Europe/Rome')  # 2015-07-04 17:00:00+02:00
        end_Point   = TimePoint(t=1436022000+1800, tz='Europe/Rome')  # 2015-07-04 17:30:00+02:00
        Slot_coverage = compute_1D_coverage(dataSeries  = self.dataTimeSeries3,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)
        # 20 minutes plus other 30 secs validity for the 20th point over 30 minutes
        self.assertEqual(Slot_coverage, ( ((20*60.0)+30.0) / (30*60.0)) ) 


        # D) Missing ten minutes over 30 at the beginning (coverage=0.683)
        start_Point = TimePoint(t=1436022000,      tz='Europe/Rome')  # 2015-07-04 17:00:00+02:00
        end_Point   = TimePoint(t=1436022000+1800, tz='Europe/Rome')  # 2015-07-04 17:30:00+02:00
        Slot_coverage = compute_1D_coverage(dataSeries  = self.dataTimeSeries4,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)
        # 20 minutes plus other 30 secs (previous) validity for the 10th point over 30 minutes
        self.assertEqual(Slot_coverage, ( ((20*60.0)+30.0) / (30*60.0)) ) 


        # E) Missing eleven minutes over 30 in the middle (coverage=0.66)
        start_Point = TimePoint(t=1436022000,      tz='Europe/Rome')  # 2015-07-04 17:00:00+02:00
        end_Point   = TimePoint(t=1436022000+1800, tz='Europe/Rome')  # 2015-07-04 17:30:00+02:00
        Slot_coverage = compute_1D_coverage(dataSeries  = self.dataTimeSeries5,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)
        # 20 minutes plus other 30 secs (previous) validity for the 10th point over 30 minutes
        self.assertAlmostEqual(Slot_coverage, (2.0/3.0))



    def test_compute_1D_coverage_advanced(self):
        
        # TODO: Move above with other time series
        from luna.sensors import PhysicalDataTimeSensor
        class SimpleSensor15m(PhysicalDataTimeSensor):
            type_ID = 1
            Points_data_labels = ['temp_C']
            Points_validity_region = TimeSlot(span='15m')
            Slots_data_labels =  ['temp_C_AVG', 'temp_C_MIN', 'temp_C_MAX']
            timezone = 'Europe/Rome'  
        
        sensor = SimpleSensor15m('084EB18E44FFA/7-MB-1')
        from_dt = dt(2019,10,1,1,0,0, tzinfo=sensor.timezone)
        to_dt   = dt(2019,10,1,6,0,0, tzinfo=sensor.timezone)

        dataTimeSeries = DataTimeSeries()
        slider_dt = from_dt
        count = 0
        while slider_dt < to_dt:
            
            if count not in [1, 6, 7, 8, 9, 10]:
                data = PhysicalData( labels = ['temp_C'], values = [25.5] ) 
                physicalDataTimePoint = PhysicalDataTimePoint(dt   = slider_dt,
                                                              data = data,
                                                              validity_region = sensor.Points_validity_region)
                dataTimeSeries.append(physicalDataTimePoint)
            
            slider_dt = slider_dt + TimeSlotSpan('15m')
            count += 1


        # Missing half slot before slot re-start
        start_Point = TimePoint(dt=dt(2019,10,1,3,30,0, tzinfo=sensor.timezone))
        end_Point   = TimePoint(dt=dt(2019,10,1,3,45,0, tzinfo=sensor.timezone))
        Slot_coverage = compute_1D_coverage(dataSeries  = dataTimeSeries,
                                            start_Point = start_Point,
                                            end_Point   = end_Point)
        
        
        self.assertAlmostEqual(Slot_coverage, (0.5))

        #print('------------------------------')
        #print(dataTimeSeries)
        #for point in dataTimeSeries:
        #    pass
        #    #print(point, point.validity_region)
        #print('------------------------------')
        #print(Slot_coverage)
        #print('------------------------------')

        
        
    def tearDown(self):
        pass










#=============================
# Test clean and reconstruct  
#=============================
class test_clean_and_reconstruct(unittest.TestCase):

    def setUp(self):
        from luna.sensors import PhysicalDataTimeSensor
        class SimpleSensor15m(PhysicalDataTimeSensor):
            type_ID = 1
            Points_data_labels = ['temp_C']
            Points_validity_region = TimeSlot(span='15m')
            Slots_data_labels =  ['temp_C_AVG', 'temp_C_MIN', 'temp_C_MAX']
            timezone = 'Europe/Rome'  
        
        self.sensor = SimpleSensor15m('084EB18E44FFA/7-MB-1')

    
    def test_clean_and_reconstruct_basic(self):

        # No data
        dataTimePointSeries = DataTimeSeries()
        clean_and_reconstruct(dataTimePointSeries)
        
        
        # One point
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        clean_and_reconstruct(dataTimePointSeries)
        
        
        # Two points
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))          
        clean_and_reconstruct(dataTimePointSeries)
        
        
        # Three points
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))        
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,15,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))   
        clean_and_reconstruct(dataTimePointSeries)
        
        
        # Four  points
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))        
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,15,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,30,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))          
        clean_and_reconstruct(dataTimePointSeries)
        
        
        # No strange things
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))        
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,15,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,30,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))  


        cleaned_dataTimeSlotSeries = clean_and_reconstruct(dataTimePointSeries)

        #print('-----------------------------')
        #for slot in cleaned_dataTimeSlotSeries:
        #    print slot
        #print('-----------------------------')


        # Overlap Case 1)
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='30m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='30m')))        
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,15,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='30m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,30,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='30m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='30m')))  
  
  
        cleaned_dataTimeSlotSeries = clean_and_reconstruct(dataTimePointSeries)
 
        #print('-----------------------------')
        #for slot in cleaned_dataTimeSlotSeries:
        #    print slot
        #print('-----------------------------')   


        # Missing data Case 1)
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [20] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [21] ),
                                                         validity_region = TimeSlot(span='15m'))) 
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,30,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [23] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [24] ),
                                                         validity_region = TimeSlot(span='15m')))  
  
  
        cleaned_dataTimeSlotSeries = clean_and_reconstruct(dataTimePointSeries)
 
        print('-----------------------------')
        for slot in cleaned_dataTimeSlotSeries:
            print slot, slot.data
        print('-----------------------------')  


        # Missing data Case 2)
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [21] ),
                                                         validity_region = TimeSlot(span='15m'))) 
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [23] ),
                                                         validity_region = TimeSlot(span='15m')))
  
  
        cleaned_dataTimeSlotSeries = clean_and_reconstruct(dataTimePointSeries)
 
        print('-----------------------------')
        for slot in cleaned_dataTimeSlotSeries:
            print slot, slot.data
        print('-----------------------------')  



        # From case 1)
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))        
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,15,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,30,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))  
  
  
        cleaned_dataTimeSlotSeries = clean_and_reconstruct(dataTimePointSeries, from_dt=dt(2019,10,1,0,45,0))
 
        print('-----------------------------')
        for slot in cleaned_dataTimeSlotSeries:
            print slot, slot.data
        print('-----------------------------')  


        # From case 2)
        dataTimePointSeries = DataTimeSeries()
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,0,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,0,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))        
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,15,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,30,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))    
        dataTimePointSeries.append(PhysicalDataTimePoint(dt = dt(2019,10,1,1,45,0),
                                                         data = PhysicalData( labels = ['temp_C'], values = [25.5] ),
                                                         validity_region = TimeSlot(span='15m')))  
  
  
        cleaned_dataTimeSlotSeries = clean_and_reconstruct(dataTimePointSeries, from_dt=dt(2019,10,1,0,16,0))
 
        print('-----------------------------')
        for slot in cleaned_dataTimeSlotSeries:
            print slot, slot.data
        print('-----------------------------')   
        
        #self.assertAlmostEqual(Slot_coverage, (0.5))

        #print('------------------------------')
        #print(dataTimeSeries)
        #for point in dataTimeSeries:
        #    pass
        #    #print(point, point.validity_region)
        #print('------------------------------')
        #print(Slot_coverage)
        #print('------------------------------')

        
        
    def tearDown(self):
        pass













