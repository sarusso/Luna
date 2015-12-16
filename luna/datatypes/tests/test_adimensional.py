import unittest
from luna.datatypes.composite import DataTimePoint
from luna.datatypes.adimensional import *
from luna.common.exceptions import InputException
from luna.spacetime.time import dt

class test_adimensional(unittest.TestCase):

    def setUp(self):       
        pass

    def test_PhisicalQuantity(self):
        
        
        quantity1 = PhysicalQuantity('power_W')
        self.assertEqual(quantity1.name, 'power')
        self.assertEqual(quantity1.unit, 'W')
        self.assertEqual(quantity1.type, 'INTENSIVE')
        self.assertEqual(quantity1.op, None)

        quantity2 = PhysicalQuantity('energy_kWh_e_AVG')
        self.assertEqual(quantity2.name, 'energy')
        self.assertEqual(quantity2.unit, 'kWh')
        self.assertEqual(quantity2.type, 'EXTENSIVE')
        self.assertEqual(quantity2.op, 'AVG')


    def tearDown(self):
        pass























