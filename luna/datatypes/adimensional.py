
from luna.common.exceptions import InputException


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
#   P r i m i t i v e,    U n d i m e n s i o n a l
#   d a t a    t y p e s
#
#---------------------------------------------------


class IntData(AdimensionalData, int):
    pass
  
class FloatData(AdimensionalData, float):
    pass

class ImageData(AdimensionalData):
    pass





# TODO: move in DimensionalData?

#---------------------------------------------
# Physical  quantities
#---------------------------------------------

class PhysicalQuantity(AdimensionalData):
    '''A physical quantity. Must have a name, and unit of measurement and a type(intensive/extensive)''' 
    
    def __repr__(self):
        return '{}'.format(self.string)

    def __eq__(self, other): 
        return self.string == other.string

    def __ne__(self, other): 
        return self.string != other.string
     
    
    def __init__(self, string, trustme=False):
    
        self.string        = string
        self.string_pieces = None
        if not trustme:
            string_pieces = string.split('_')
            
            if  len(string_pieces) == 2:
                # TODO: Validate unit 
                pass
            elif len(string_pieces) == 4:
                # TODO: Validate unit
                # TODO: Validate intensive or extensive
                # TODO: Validate operation
                pass
            else:
                raise InputException('Wrong PhysicalQuantity name format: {}'.format(string))
    
    @property
    def name(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split('_')
        return self.string_pieces[0]

    @property
    def unit(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split('_')
        return self.string_pieces[1]

    @property
    def type(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split('_')
        if len(self.string_pieces) == 2:
            return 'INTENSIVE'
        else:
            return 'INTENSIVE' if self.string_pieces[2] == 'i' else 'EXTENSIVE'
 
    @property
    def op(self):
        if not self.string_pieces:
            self.string_pieces = self.string.split('_')
        if len(self.string_pieces) == 2:
            return None
        else:
            return self.string_pieces[3]



    
    




















    





