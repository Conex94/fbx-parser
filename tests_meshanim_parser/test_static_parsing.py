import unittest
from fbx_parser import FbxParser


#todo: implement unittests
class Test_Static_Convert(unittest.TestCase):
    def test_convert_static01(self):
        '''
        Very shallow test to see if the convert static goes through
        :return:
        '''
        try:
            with open('input/static_low.fbx') as f:
                lines = f.readlines()

            parser = FbxParser()
            parser.convert_mesh('output/static_low.mesh', lines)
        except:
            self.assertTrue(False)

    def test_convert_static02(self):
        '''
         Very shallow test to see if the convert static goes through
        :return:
        '''
        try:
            with open('input/static_high.fbx') as f:
                lines = f.readlines()

            parser = FbxParser()
            #parser.convert_mesh('output/static_high.mesh', lines)
        except:
            self.assertTrue(False)
