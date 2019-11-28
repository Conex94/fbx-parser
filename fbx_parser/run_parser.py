import unittest
import argparse

from fbx_parser_rework import FbxParser


def run_animation_parser_notest():
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
                        default="", help='Pick between map or model')

    results = parser.parse_args()

    results.path_in = '..//testfiles//tests_meshanim_parser//input_files//fbxfiles'
    results.filename_in = 'test_animation.fbx'
    results.path_out = '..//testfiles//tests_meshanim_parser//output_files//animation'
    results.filename_out = 'animation'

    fbxparser._convert_auto(results)


def run_static_parser_notest():
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

    results.path_in = '..//testfiles//tests_meshanim_parser//input_files//fbxfiles'
    results.filename_in = 'test_sphere.fbx'
    results.path_out = '..//testfiles//tests_meshanim_parser//output_files//models'
    results.filename_out = 'sphere'

    fbxparser._convert_auto(results)

def run_skinned_parser_notest():
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

    results.path_in = '..//testfiles//tests_meshanim_parser//input_files//fbxfiles'
    results.filename_in = 'test_single_skinned.fbx'
    results.path_out = '..//testfiles//tests_meshanim_parser//output_files//models'
    results.filename_out = 'single_skinned'

    fbxparser._convert_auto(results)

if __name__ == '__main__':
    #run_animation_parser_notest()
    #run_static_parser_notest()
    run_skinned_parser_notest()
