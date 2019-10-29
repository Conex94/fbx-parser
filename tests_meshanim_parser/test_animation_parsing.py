import unittest
from fbx_parser import FbxParser

class Test_Animation_Convert(unittest.TestCase):

    def test_convert_animation_06(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:
            with open('input/skeleton_pointing.fbx') as f:
                lines = f.readlines()
            parser = FbxParser()
            parser.convert_animation('output/skeleton_pointing', lines)
        except:
            self.assertTrue(False)

    def test_convert_animation_05(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:
            with open('input/skeleton_anim_new.fbx') as f:
                lines = f.readlines()

            parser = FbxParser()
            parser.convert_animation('output/skeleton_anim_new', lines)
        except:
            self.assertTrue(False)

    def test_convert_animation_04(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:
            with open('input/gun_anim.fbx') as f:
                lines = f.readlines()
            parser = FbxParser()
            parser.convert_animation('output/gun_anim', lines)
        except:
            self.assertTrue(False)

    def test_convert_animation_03(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:
            with open('input/character_running.fbx') as f:
                lines = f.readlines()
            parser = FbxParser()
            parser.convert_animation('output/character_running', lines)
        except:
            self.assertTrue(False)

    def test_convert_animation_02(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:
            with open('input/character_breathing.fbx') as f:
                lines = f.readlines()
            parser = FbxParser()
            parser.convert_animation('output/character_breathing', lines)
        except:
            self.assertTrue(False)

    def test_convert_animation_01(self):
        '''
        Very shallow test to see if the convert animation passes
        :return:
        '''
        try:
            with open('input/animation_1000.fbx') as f:
                lines = f.readlines()
            parser = FbxParser()
            parser.convert_animation('output/animation_1000', lines)
        except:
            self.assertTrue(False)

