import unittest
from fbx_parser import FbxParser


#todo: implement unittests
class Test_Skinned_Convert(unittest.TestCase):

    def test_convert_deformer_01(self):
        '''
        Very shallow test to see if the convert deformer passes
        :return:
        '''
        try:
            with open('input/deformer_low.fbx') as f:
                lines = f.readlines()

            parser = FbxParser()
            parser.convert_skinned('output/deformer_low', lines)
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_convert_deformer_02(self):
        '''
        Very shallow test to see if the convert deformer passes
        :return:
        '''
        try:
            with open('input/deformer_low.fbx') as f:
                lines = f.readlines()

            parser = FbxParser()
            parser.convert_skinned('output/deformer_high', lines)
            self.assertTrue(True)
        except:
            self.assertTrue(False)
