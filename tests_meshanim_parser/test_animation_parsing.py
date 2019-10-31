import unittest
import argparse

from fbx_parser.fbx_parser_rework import FbxParser

class fbx_parser_tests(unittest.TestCase):

    def test_convert_animation(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:

            fbxparser = FbxParser()

            parser = argparse.ArgumentParser()

            parser.add_argument('--inpath', action='store', dest='path_in',
                                default=".", help='Select the path of the file to parse')

            parser.add_argument('--infile', action='store', dest='filename_in',
                                default="None.fbx", help='Select the file to parse')

            parser.add_argument('--outpath', action='store', dest='path_out',
                                default=".", help='Choose the output folder')

            parser.add_argument('--outfile', action='store', dest='filename_out',
                                default=".", help='Enter the target filename')

            parser.add_argument('--mode', action='store', dest='mode',
                                default="model", help='Pick between map or model')

            results = parser.parse_args()

            results.path_in = 'input_files//fbxfiles'
            results.filename_in = 'test_animation.fbx'
            results.path_out = 'output_files//animation'
            results.filename_out = 'animation'

            fbxparser._convert_auto(results)

            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_convert_static(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:
            fbxparser = FbxParser()

            parser = argparse.ArgumentParser()

            parser.add_argument('--inpath', action='store', dest='path_in',
                                default=".", help='Select the path of the file to parse')

            parser.add_argument('--infile', action='store', dest='filename_in',
                                default="None.fbx", help='Select the file to parse')

            parser.add_argument('--outpath', action='store', dest='path_out',
                                default=".", help='Choose the output folder')

            parser.add_argument('--outfile', action='store', dest='filename_out',
                                default=".", help='Enter the target filename')

            parser.add_argument('--mode', action='store', dest='mode',
                                default="model", help='Pick between map or model')

            results = parser.parse_args()

            results.path_in = 'input_files//fbxfiles'
            results.filename_in = 'test_sphere.fbx'
            results.path_out = 'output_files//models'
            results.filename_out = 'sphere'

            fbxparser._convert_auto(results)

            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_convert_skinned(self):
        '''
        Clear the Test Output files
        :return:
        '''
        try:

            fbxparser = FbxParser()

            parser = argparse.ArgumentParser()

            parser.add_argument('--inpath', action='store', dest='path_in',
                                default=".", help='Select the path of the file to parse')

            parser.add_argument('--infile', action='store', dest='filename_in',
                                default="None.fbx", help='Select the file to parse')

            parser.add_argument('--outpath', action='store', dest='path_out',
                                default=".", help='Choose the output folder')

            parser.add_argument('--outfile', action='store', dest='filename_out',
                                default=".", help='Enter the target filename')

            parser.add_argument('--mode', action='store', dest='mode',
                                default="model", help='Pick between map or model')

            results = parser.parse_args()

            results.path_in = 'input_files//fbxfiles'
            results.filename_in = 'test_skinned.fbx'
            results.path_out = 'output_files//models'
            results.filename_out = 'skinned'

            fbxparser._convert_auto(results)

            self.assertTrue(True)
        except:
            self.assertTrue(False)

