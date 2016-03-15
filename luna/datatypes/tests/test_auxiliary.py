import unittest
from luna.datatypes.auxiliary import PhysicalQuantity
from luna.common.exceptions import InputException

class test_adimensional(unittest.TestCase):

    def setUp(self):       
        pass

    def test_PhisicalQuantity(self):

        quantity1 = PhysicalQuantity('power_W')
        self.assertEqual(quantity1.name, 'power')
        self.assertEqual(quantity1.unit, 'W')
        self.assertEqual(quantity1.op, None)
               
        quantity1 = PhysicalQuantity('power_W_INST')
        self.assertEqual(quantity1.name, 'power')
        self.assertEqual(quantity1.unit, 'W')
        self.assertEqual(quantity1.op, None)

        quantity2 = PhysicalQuantity('energy_kWh_AVG')
        self.assertEqual(quantity2.name, 'energy')
        self.assertEqual(quantity2.unit, 'kWh')
        self.assertEqual(quantity2.op, 'AVG')

        with self.assertRaises(InputException):
            _ = PhysicalQuantity('power_W_j_h_d')



    def tearDown(self):
        pass























