
#---------------------------------------------------
#
#   P r e  -  P r i m i t i v e
#   d a t a    t y p e s
#
#---------------------------------------------------

class AdimensionalData(object):
    '''Data without a dimension (int, float, string, image, ...)'''
    
    def __init__(self):
        pass
    
    pass


#---------------------------------------------------
#
#   P r i m i t i v e,    A d i m e n s i o n a l
#   d a t a    t y p e s
#
#---------------------------------------------------

class IntData(AdimensionalData, int):
    pass
  
class FloatData(AdimensionalData, float):
    pass

class ImageData(AdimensionalData):
    pass

