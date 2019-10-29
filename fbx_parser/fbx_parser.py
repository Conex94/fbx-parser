'''
IMPORTANT NOTE

This python FBX importer Only works for
the FBX-ASCII format of Version 6.1.0 from 2006

It will later be modified to work with the latest version too
'''

from sys import argv
import os
import time



#todo: Implement Data parse error
class DataParseError(Exception):
    def __init__(self, function_name, data):
        '''
        :param functionname:
        :param data:
        '''
        msg = "{} failed with data: {}".format(function_name, data)
        super(DataParseError, self).__init__(msg)
        self.data = data
        self.function_name = function_name

class DataWriteError(Exception):
    def __init__(self, data):
        '''
        :param data:
        '''
        msg = "Failed to write data: {} to file".format(data)
        super(DataWriteError, self).__init__(msg)
        self.data = data

class Vector3:
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None

    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

class Vector2:
    def __init__(self):
        self.x = None
        self.y = None

    def __init__(self,x,y):
        self.x = x
        self.y = y

class VertexData:
    def __init__(self):
        self.points     = list()
        self.uvs        = list()
        self.normals    = list()

class Material:
    def __init__(self):
        self.color_name     = None
        self.bump_name      = None
        self.spec_name      = None
        self.shader_name    = None
        self.shader_index   = None
        self.bump_power     = None
        self.spec_power     = None

class Face:
    def __init__(self):
        self.appliedShader  = None
        self.point_indices  = list()
        self.uv_indices     = list()
        self.vn_indices     = list()

class FaceAsLines:
    def __init__(self):
        self.facelines      = list()
        self.appliedshader  = None

class PoseNodeString:
    def __init__(self):
        self.posenodelines  = list()

class PoseNode:
    def __init__(self):
        self.nodename       = str()
        self.matrix         = list()

class JointAnimationData:
    def __init__(self):
        self.jointname          = None
        self.translate_x        = list()
        self.translate_x_key    = list()
        self.translate_y        = list()
        self.translate_y_key    = list()
        self.translate_z        = list()
        self.translate_z_key    = list()

        self.rotate_x       = list()
        self.rotate_x_key   = list()
        self.rotate_y       = list()
        self.rotate_y_key   = list()
        self.rotate_z       = list()
        self.rotate_z_key   = list()

        self.scale_x        = list()
        self.scale_x_key    = list()
        self.scale_y        = list()
        self.scale_y_key    = list()
        self.scale_z        = list()
        self.scale_z_key    = list()

        self.beginframe = 0
        self.endframe = 0

class Connection:
    def __init__(self):
        self.parent = ''
        self.child = ''

    def __repr__(self):
        return 'Parent: {} : Child: {}'.format(self.parent, self.child)

class Shader:
    def __init__(self):
        self.reltexturename = None

class MeshLinesPacked:

    def __init__(self, name: str, vertline : list()
                 ,vindexline: list(), normlines : list()
                 ,uvlines : list(), uvindexlines: list()):
        self.mesh_name = name
        self.verticelines = vertline
        self.vindex_lines = vindexline
        self.normals_lines = normlines
        self.uv_lines = uvlines
        self.uv_index_lines = uvindexlines

class DeformerNodesString:
    def __init__(self):
        self.lines = list()

class Deformer:
    def __init__(self):
        self.indexes = list()
        self.weights = list()
        self.deformername = str
        self.transform = list()
        self.transformlink = list()

class MeshDataStatic:
    def __init__(self):
        self.meshname = str
        self.points = list()
        self.p_index = list()
        self.uv = list()
        self.uv_index = list()
        self.normals = list()

class TextureData:
    def __init__(self):
        self.relfilenames = list()

class AnimatedDeformerString:
    def __init__(self):
        self.lines = list()

class SubChannelString:
    def __init__(self):
        self.lines = list()

class AnimatedDeformer:
    def __init__(self):
        self.deformername = str
        self.channel_translate = Channel()
        self.channel_rotate = Channel()
        self.channel_scale = Channel()

class Channel:
    def __init__(self):
        self.channel_x = SubChannel()
        self.channel_y = SubChannel()
        self.channel_z = SubChannel()

class ChannelString:
    def __init__(self):
        self.lines = list()

class SubChannel:
    def __init__(self):
        self.keydistances = list()
        self.keyvalue = list()

class KeyValBox:
    def __init__(self):
        self.values = list()
        self.keys = list()

class Group:
    def __init__(self):
        self.faces = list()
        self.groupname = None

class GroupFacelinesSeperated:
    def __init__(self):
        self.facesingroup = list()
        self.groupname = None

class ObjModel:
    def __init__(self):
        self.vertexdata = None
        self.groupdata = list()
        self.materialpath = None
        self.materials = list()

class FBX_FILE:
    def __init__(self):
        self.fbx_data = dict()


class FbxParser:
    def convert(self, file_in : str, outfile : str, converttype : int):
        with open(file_in, 'r') as fin:
            lines = fin.readlines()

        if converttype == 0:
            self.convert_mesh(outfile, lines)

        if converttype == 1:
            self.convert_skinned(outfile, lines)

        if converttype == 2:
            self.convert_animation(outfile, lines)

    def createposenodes(self, strnodes : list()):
        '''
        create the pose nodes from a list of posenode strings

        :param strnodes:
        :return:
        '''

        try:
            nodes = list()

            for nodestr in strnodes:
                node = PoseNode()

                for line in nodestr.posenodelines:
                    if line.startswith("Node: "):
                        nodeline = line.strip()[7: line.__len__()-1]
                        node.nodename = nodeline

                matrixline = ''
                readmatrix = False

                for line in nodestr.posenodelines:
                    if line.startswith("Matrix: "):
                        readmatrix = True
                        nodeline = line.strip()[8:]
                        matrixline += nodeline
                        continue

                    if readmatrix: matrixline += line

                    if "}" in line: break

                matrixl = matrixline.split(",")
                floats = list()
                for i in range(0,matrixl.__len__()):
                    floats.append(float(matrixl[i]))

                node.matrix = floats
                nodes.append(node)

            return nodes

        except Exception as e:
            print('Could not create nodes list from Posestring nodes')
            raise e

    def extractArray(self, lines : list(), indexmode : bool):
        '''
        This list converts a list of lines to a list of floats/ints
        While also Translating the "indexed mode" from the fbx file,
        to the actual index listing.

        Hint: Fbx indexed points go in triangles/squares
              this means it has to be tagged somehow, therefor
              if its a triangle, the last Index of each triangle is
              the negative number of the actual index with 1 added
              example:  0,1,-3  ( the 3rd index is negative -> triangle)
              this means the actual index is  -3 * (-1) = 3   then 3 -1 = 2
              so it would be : 0, 1, 2

        :param lines:
        :param indexmode:
        :return:
        '''

        try:
            resline = ''
            for line in lines:
                resline += line + ','

            floats = resline.replace(' ','').split(",")

            float_list = list()
            integer_list = list()
            theindex = 0
            for f in floats:
                if indexmode is False:
                    if not f == '':
                        float_list.append(float(f))
                        theindex += 1

                else:
                    if not f == '':
                        thei = int(f)
                        if thei < 0:
                            integer_list.append(thei * (-1)-1)
                        if thei >= 0:
                            integer_list.append(thei)

            if indexmode is True:
                return integer_list
            else:
                return float_list

        except Exception as e:
            print('Failed to extract array')
            print(theindex)
            raise e

    def animated_deformer_to_animation_data(self, defs : list()):
        '''
        Take the animated deformers and create a list of animation with channels from it

        :param defs: Animated deformer data
        :return list of JointAnimationData:
        '''

        print('Converting animated Transformer to animation data')

        try:
            j_anim_data = list()

            for i in range(0, defs.__len__()):
                data_single = JointAnimationData()

                data_single.jointName = defs[i].deformername
                data_single.translate_x = defs[i].channeltranslate.channelx.keyvalues
                data_single.translate_x_key = defs[i].channeltranslate.channelx.keydistances

                data_single.translate_y = defs[i].channeltranslate.channely.keyvalues
                data_single.translate_y_key = defs[i].channeltranslate.channely.keydistances

                data_single.translate_z = defs[i].channeltranslate.channelz.keyvalues
                data_single.translate_z_key = defs[i].channeltranslate.channelz.keydistances


                data_single.rotate_x = defs[i].channelrotate.channelx.keyvalues
                data_single.rotate_x_key = defs[i].channelrotate.channelx.keydistances

                data_single.rotate_y = defs[i].channelrotate.channely.keyvalues
                data_single.rotate_y_key = defs[i].channelrotate.channely.keydistances

                data_single.rotate_z = defs[i].channelrotate.channelz.keyvalues
                data_single.rotate_z_key = defs[i].channelrotate.channelz.keydistances


                data_single.scale_x = defs[i].channelscale.channelx.keyvalues
                data_single.scale_x_key = defs[i].channelscale.channelx.keydistances

                data_single.scale_y = defs[i].channelscale.channely.keyvalues
                data_single.scale_y_key = defs[i].channelscale.channely.keydistances

                data_single.scale_z = defs[i].channelscale.channelz.keyvalues
                data_single.scale_z_key = defs[i].channelscale.channelz.keydistances

                j_anim_data.append(data_single)

            print('Succesfully created JointAnimationDataList.')
            return j_anim_data

        except Exception as e:
            print('Failed to create JointAnimationDataList')
            raise e

    def create_connections(self, cons : list()):
        '''
        Create connections list from the connections string array

        :param cons:
        :return list of Connection objects:
        '''
        try:
            print("Starting to create Connections list from Connection list as String")

            connections = list()

            for line in cons:
                if line.strip().startswith("Connect: "):
                    if "Deformer::" in line or "SubDeformer::" in line:
                        continue

                    con = Connection()
                    thisline = line.strip()[8:]
                    splited = thisline.split(",")

                    splited[0] = splited[0].strip()[1: splited[0].__len__() - 2]
                    splited[1] = splited[1].strip()[1: splited[1].__len__() - 2]
                    splited[2] = splited[2].strip()[1: splited[2].__len__() - 2]

                    con.child = splited[2]
                    con.parent = splited[1]

                    connections.append(con)

            print("Succesfully created Connections list")
            return connections

        except Exception as e:
            print('Failed to create connections list')
            raise e

    def create_mesh_data_static(self, modelmeshpack : MeshLinesPacked):
        '''
        Create the MeshDataStatic frmthe ModelMeshPack Object

        :param modelmeshpack:
        :return ModelMeshStatic:
        '''

        try:
            point_list = self.extractArray(modelmeshpack.verticelines, False)
            print('Point extracted')
        except Exception as e:
            print("Failed to parse Points")
            raise e

        try:
            point_index_list = self.extractArray(modelmeshpack.vindex_lines, True)
            print("point index succesful")
        except Exception as e:
            print("Failed to parse point indices")
            raise e

        try:
            uv_list = self.extractArray(modelmeshpack.uv_lines, False)
            print("uv succesful")

        except Exception as e:
            print("Failed to parse uvs")
            raise e

        try:
            uv_indices = self.extractArray(modelmeshpack.uv_index_lines, True)
            print("uv index succesful")

        except Exception as e:
            print("Failed to parse uv indices")
            raise e

        try:
            normals_floats = self.extractArray(modelmeshpack.normals_lines, False)
            print("normals suc")
        except Exception as e:
            print("Failed to parse normals")
            raise e

        mesh = MeshDataStatic()
        mesh.normals = normals_floats
        mesh.p_index = point_index_list
        mesh.points = point_list
        mesh.uv = uv_list
        mesh.uv_index = uv_indices
        mesh.meshname = modelmeshpack.mesh_name

        return mesh

    def extractkeys(self, lines : list()):
        '''
        Extract keys, convert from... microseconds? to frames
        :param lines:
        :return:
        '''
        try:

            box = KeyValBox()
            resultString = ""
            read = False
            for line in lines:
                if line.strip().startswith("Key: "):
                    read = True

                if line.strip().startswith("Color: "):
                    read = False

                if read is True:
                    resultString += line.strip()

            keystrings = resultString.strip()[4:].split(",")
            vals = list()
            keys = list()

            try:
                i = 0
                while i < keystrings.__len__():
                    float_val = float(keystrings[i + 1].strip())

                    key_int = int(keystrings[i + 0].strip())
                    int_val = ((key_int - 1924423250) / 1924423250) + 1
                    vals.append(float_val)
                    keys.append(int_val)
                    i += 7
                if keys.__len__() < 2 and keys.__len__() > 0:
                    vals.append(vals[0])
                    keys.append(keys[0])


            except Exception as e:
                print('Couldnt resolve keys to frames, adding empty values for both')
                box.keys = []
                box.values = []
                return box

            box.keys = keys
            box.values = vals

            return box
        except Exception as e:
            print('Failed to resolve keys')
            raise e

    def get_animated_deformer_String(self, lines : list()):
        '''
        This function creates a list of AnimatedDeformers from a list of
        lines

        :param lines:
        :return:
        '''
        try:

            take_perjointdata = list()
            begins = list()
            ends =list()

            brackets = 0

            for i in range(0,lines.__len__()):
                line = lines[i]
                if line.strip().startswith('Takes: '):
                    continue
                if line.strip().startswith('Take: '):
                    continue

                if 'Model: \"' in line and '{' in line:
                    brackets+=1
                    begins.append(i)

                elif '{' in line and not 'Model: \"' in line:
                    brackets += 1
                else: pass

                if '}' in line:
                    brackets -= 1
                    if brackets == 0:
                        ends.append(i)

            for i in range(0, begins.__len__()):
                node = AnimatedDeformerString()

                j = begins[i]
                while j < ends[i]:

                    node.lines.append(lines[j])
                    j += 1

                take_perjointdata.append(node)

            animated_deformers = list()

            for deformer in take_perjointdata:
                try:
                    animated_deformers.append(self.create_animated_deformer(deformer))

                except Exception as e:
                    print('Failed to get animated deformer string')
                    raise e

            if animated_deformers.__len__() < 1:
                print('animation contains no data')
                raise Exception('FBX File probaly has no Animation Data...')
            return animated_deformers

        except Exception as e:
            print('Failed to get animated deformers string')
            raise e

    def create_animated_deformer(self, def_string : AnimatedDeformerString):
        '''
        This function takes deformerStrings and turns them into Full
        Deformer objects, which are ready to be written to file

        :param def_string:
        :return:
        '''


        len = def_string.lines[0].strip().__len__()
        deformer_name = def_string.lines[0].strip()[8: len - 3]
        channel_T = ChannelString()
        sub_t_x = SubChannelString()
        sub_t_y = SubChannelString()
        sub_t_z = SubChannelString()

        channel_R = ChannelString()
        sub_r_x = SubChannelString()
        sub_r_y = SubChannelString()
        sub_r_z = SubChannelString()

        channel_S = ChannelString()
        sub_s_x = SubChannelString()
        sub_s_y = SubChannelString()
        sub_s_z = SubChannelString()

        bracketcounter = 0

        #for Translates
        for line in def_string.lines:
            if line.strip().startswith('Channel: \"T\"'):
                bracketcounter += 1
                channel_T.lines.append(line)
                continue

            if '{' in line.strip() and bracketcounter > 0:
                bracketcounter += 1

            if '}' in line.strip() and bracketcounter > 0:
                bracketcounter -= 1

            if bracketcounter > 0:
                channel_T.lines.append(line)

        #for Rotations
        for line in def_string.lines:
            if line.strip().startswith('Channel: \"R\"'):
                bracketcounter += 1
                channel_R.lines.append(line)
                continue

            if '{' in line.strip() and bracketcounter > 0:
                bracketcounter += 1

            if '}' in line.strip() and bracketcounter > 0:
                bracketcounter -= 1

            if bracketcounter > 0:
                channel_R.lines.append(line)

        #for Scale
        for line in def_string.lines:
            if line.strip().startswith('Channel: \"S\"'):
                bracketcounter += 1
                channel_S.lines.append(line)
                continue

            if '{' in line.strip() and bracketcounter > 0:
                bracketcounter += 1

            if '}' in line.strip() and bracketcounter > 0:
                bracketcounter -= 1

            if bracketcounter > 0:
                channel_S.lines.append(line)


        #dissecting the translate lines from the transform channel
        bracketcounter = 0
        i = 0
        while i <  channel_T.lines.__len__():
            if channel_T.lines[i].strip().startswith('Channel \"T\" {'):
                continue
            if channel_T.lines[i].strip().startswith('Channel \"X\" {'):
                bracketcounter+= 1
                sub_t_x.lines.__add__(channel_T.lines[i])
                continue

            if "{" in channel_T.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_T.lines[i].strip():
                bracketcounter -= 1

            if "Channel: \"Y\" {" in channel_T.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_t_x.lines.append(channel_T.lines[i])

            i += 1

        while i < channel_T.lines.__len__():

            if channel_T.lines[i].strip().startswith('Channel \"Y\" {'):
                bracketcounter+= 1
                sub_t_y.lines.__add__(channel_T.lines[i])
                continue

            if "{" in channel_T.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_T.lines[i].strip():
                bracketcounter -= 1

            if "Channel: \"Z\" {" in channel_T.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_t_y.lines.append(channel_T.lines[i])

            i += 1

        bracketcounter = 0 #haa? why?
        while i < channel_T.lines.__len__():

            if channel_T.lines[i].strip().startswith('Channel \"Z\" {'):
                bracketcounter+= 1
                sub_t_z.lines.__add__(channel_T.lines[i])
                continue

            if "{" in channel_T.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_T.lines[i].strip():
                bracketcounter -= 1

            if "Color: " in channel_T.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_t_z.lines.append(channel_T.lines[i])

            i += 1


        #dissecting the rotate lines from the transform channel

        bracketcounter = 0
        i = 0
        while i <  channel_T.lines.__len__():
            if channel_R.lines[i].strip().startswith('Channel \"R\" {'):
                continue
            if channel_R.lines[i].strip().startswith('Channel \"X\" {'):
                bracketcounter+= 1
                sub_r_x.lines.__add__(channel_R.lines[i])
                continue

            if "{" in channel_R.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_R.lines[i].strip():
                bracketcounter -= 1

            if "Channel: \"Y\" {" in channel_R.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_r_x.lines.append(channel_R.lines[i])

            i += 1

        while i < channel_R.lines.__len__():

            if channel_R.lines[i].strip().startswith('Channel \"Y\" {'):
                bracketcounter+= 1
                sub_r_y.lines.__add__(channel_R.lines[i])
                continue

            if "{" in channel_R.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_R.lines[i].strip():
                bracketcounter -= 1

            if "Channel: \"Z\" {" in channel_R.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_r_y.lines.append(channel_R.lines[i])

            i += 1

        bracketcounter = 0 #haa? why?
        while i < channel_R.lines.__len__():

            if channel_R.lines[i].strip().startswith('Channel \"Z\" {'):
                bracketcounter+= 1
                sub_r_z.lines.__add__(channel_R.lines[i])
                continue

            if "{" in channel_R.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_R.lines[i].strip():
                bracketcounter -= 1

            if "Color: " in channel_R.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_r_z.lines.append(channel_R.lines[i])

            i += 1


        #dissecting the scale lines from the transform channel

        bracketcounter = 0
        i = 0
        while i <  channel_S.lines.__len__():
            if channel_S.lines[i].strip().startswith('Channel \"R\" {'):
                continue
            if channel_S.lines[i].strip().startswith('Channel \"X\" {'):
                bracketcounter+= 1
                sub_s_x.lines.__add__(channel_S.lines[i])
                continue

            if "{" in channel_S.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_S.lines[i].strip():
                bracketcounter -= 1

            if "Channel: \"Y\" {" in channel_S.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_s_x.lines.append(channel_S.lines[i])

            i += 1

        while i < channel_S.lines.__len__():

            if channel_S.lines[i].strip().startswith('Channel \"Y\" {'):
                bracketcounter+= 1
                sub_s_y.lines.__add__(channel_S.lines[i])
                continue

            if "{" in channel_S.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_S.lines[i].strip():
                bracketcounter -= 1

            if "Channel: \"Z\" {" in channel_S.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_s_y.lines.append(channel_S.lines[i])

            i += 1

        bracketcounter = 0 #haa? why?
        while i < channel_S.lines.__len__():

            if channel_S.lines[i].strip().startswith('Channel \"Z\" {'):
                bracketcounter+= 1
                sub_s_z.lines.__add__(channel_S.lines[i])
                continue

            if "{" in channel_S.lines[i].strip():
                bracketcounter += 1

            if "}" in channel_S.lines[i].strip():
                bracketcounter -= 1

            if "Color: " in channel_S.lines[i].strip():
                break

            if bracketcounter > 0:
                sub_s_z.lines.append(channel_S.lines[i])

            i += 1


        sub_t_x_bin = SubChannel()
        sub_t_y_bin = SubChannel()
        sub_t_z_bin = SubChannel()

        sub_r_x_bin = SubChannel()
        sub_r_y_bin = SubChannel()
        sub_r_z_bin = SubChannel()

        sub_s_x_bin = SubChannel()
        sub_s_y_bin = SubChannel()
        sub_s_z_bin = SubChannel()

        try:
            box_t_x = self.extractkeys(sub_t_x.lines)
            box_t_y = self.extractkeys(sub_t_y.lines)
            box_t_z = self.extractkeys(sub_t_z.lines)

            sub_t_x_bin.keydistances = box_t_x.keys
            sub_t_x_bin.keyvalue = box_t_x.values
            sub_t_y_bin.keydistances = box_t_y.keys
            sub_t_y_bin.keyvalue = box_t_y.values
            sub_t_z_bin.keydistances = box_t_z.keys
            sub_t_z_bin.keyvalue = box_t_z.values
        except:
            pass
        try:
            box_r_x = self.extractkeys(sub_r_x.lines)
            box_r_y = self.extractkeys(sub_r_y.lines)
            box_r_z = self.extractkeys(sub_r_z.lines)

            sub_r_x_bin.keydistances = box_r_x.keys
            sub_r_x_bin.keyvalue = box_r_x.values
            sub_r_y_bin.keydistances = box_r_y.keys
            sub_r_y_bin.keyvalue = box_r_y.values
            sub_r_z_bin.keydistances = box_r_z.keys
            sub_r_z_bin.keyvalue = box_r_z.values

        except:
            pass

        try:
            box_s_x = self.extractkeys(sub_s_x.lines)
            box_s_y = self.extractkeys(sub_s_y.lines)
            box_s_z = self.extractkeys(sub_s_z.lines)

            sub_s_x_bin.keydistances = box_s_x.keys
            sub_s_x_bin.keyvalue = box_s_x.values
            sub_s_y_bin.keydistances = box_s_y.keys
            sub_s_y_bin.keyvalue = box_s_y.values
            sub_s_z_bin.keydistances = box_s_z.keys
            sub_s_z_bin.keyvalue = box_s_z.values
        except:
            pass

        T_bin = Channel()
        R_bin = Channel()
        S_bin = Channel()

        T_bin.channel_x = sub_t_x_bin
        T_bin.channel_y = sub_t_y_bin
        T_bin.channel_z = sub_t_z_bin

        R_bin.channel_x = sub_r_x_bin
        R_bin.channel_y = sub_r_y_bin
        R_bin.channel_z = sub_r_z_bin

        S_bin.channel_x = sub_s_x_bin
        S_bin.channel_y = sub_s_y_bin
        S_bin.channel_z = sub_s_z_bin

        deformer = AnimatedDeformer()

        deformer.channel_translate = T_bin
        deformer.channel_rotate = R_bin
        deformer.channel_scale = S_bin
        deformer.deformername = deformer_name

        return deformer

    #FBX get functions
    def createmodelmeshlinespacked(self, meshlines : list()):
        '''
        This function takes the lines taken from the fbx file,
        then extracts lines for each of the meshdata,
        vertice data might span over several lines, same goes for
        uvindex, uv, normals, vertex indices.

        Put those lines to their accor  ding place for further,
        processing

        :param meshlines:
        :return:
        '''

        try:
            readvertices = False
            readvertexindex = False
            readnormals = False
            read_uv = False
            read_uv_index = False

            verticelines = list()
            vindex_lines = list()
            normals_lines = list()
            uv_lines = list()
            uv_index_lines = list()

            if meshlines.__len__() < 1:
                print('No Mesh data')
                raise Exception('No Mesh data in meshlines')

            name = meshlines[0][8:]
            name = name[0: name.find("\"")]

            for line in meshlines:
                #Get mesh data lines from the file, for vertices,
                #until we reach PolygonVertexIndex, which indicates the end
                if line.startswith("Vertices: "):
                    readvertices = True

                if "PolygonVertexIndex: " in line:
                    readvertices = False

                if readvertices:
                    if "Vertices: " in line:
                        verticelines.append(line[10:])
                    else:
                        verticelines.append(line)



                #Get mesh data lines from the file, for Point Indices,
                #until we reach Edges, which indicates the end
                if line.startswith("PolygonVertexIndex: "):
                    readvertexindex = True

                if "Edges: " in line or 'GeometryVersion' in line:
                    readvertexindex = False

                if readvertexindex:
                    if "PolygonVertexIndex: " in line:
                        vindex_lines.append(line[20:])
                    else:
                        vindex_lines.append(line)


                #Get mesh data lines from the file, for Normals Indices,
                #until we reach a } in the file, which indicates the end
                if line.startswith("Normals: "):
                    readnormals = True

                if "}" in line:
                    readnormals = False

                if readnormals:
                    if "Normals: " in line:
                        normals_lines.append(line[9:])
                    else:
                        normals_lines.append(line)

                #Get mesh data lines from the file, for UV now,
                #until we reach a } in the file, which indicates the end
                if line.startswith("UV: ") and uv_lines.__len__() < 1:
                    read_uv = True

                if "UVIndex: " in line:
                    read_uv = False

                if read_uv:
                    if line.startswith('UV: '):
                        uv_lines.append(line[4:])
                    else:
                        uv_lines.append(line)


                #Get mesh data lines from the file, for UV Index now,
                #until we reach a } in the file, which indicates the end
                if 'UVIndex: ' in line and uv_index_lines.__len__() < 1:
                    read_uv_index = True

                if "}" in line:
                    read_uv_index = False

                if read_uv_index:
                    if line.startswith('UVIndex: '):
                        uv_index_lines.append(line[9:])
                    else:
                        uv_index_lines.append(line)
            #loop ends


            #Assemble the MeshLinesPacked, whcih contains
            #string lists for each the meshs data
            pack = MeshLinesPacked(name = name, vertline= verticelines,
                                    vindexline= vindex_lines,
                                    normlines= normals_lines,
                                    uvlines= uv_lines,
                                    uvindexlines= uv_index_lines)

            return pack
        except Exception as e:
            print('Failed to get meshlinespacked')
            raise e

    def getbindposelines(self, wholelines : list()):
        '''
        Get the bindpose lines in blocks and return a list of
        objects, one object for each block of lines for one particular
        posenode


        :return:
        '''

        try:
            posenodes_lines = list()
            start_reading = False

            i = 0
            while i < wholelines.__len__()-1:
                if wholelines[i].strip().startswith('PoseNode:  {'):
                    start_reading = True

                if start_reading:
                    posenodes_lines.append(wholelines[i].strip())

                if '}' in wholelines[i] and '}' in wholelines[i+1]:
                    start_reading = False

                i+=1

            posenode_list = list()
            pose = PoseNodeString()

            #Get each block of poses from the lines
            i = 0
            while i < posenodes_lines.__len__():
                if posenodes_lines[i].startswith('PoseNode: '):
                    pose = PoseNodeString()

                while True:
                    pose.posenodelines.append(posenodes_lines[i])
                    i += 1

                    if posenodes_lines[i].strip().startswith('}'):
                        break

                posenode_list.append(pose)

                i += 1


            return posenode_list

        except Exception as e:
            print('Failed to get bindposelines')
            raise e

    def getconnections(self, wholelines: list()):
        '''
        Get the connection lines from the fbx lines
        :param wholelines:
        :return:
        '''
        try:
            connections = list()
            bracket_counter = 0
            connectionopen = False
            for i in range(0,wholelines.__len__()-1):

                if "Connections:  {" in wholelines[i]:
                    bracket_counter += 1
                    connectionopen = True

                elif "}" in wholelines[i] and connectionopen is True:
                    bracket_counter -= 1
                elif "{" in wholelines[i] and connectionopen is True:
                    bracket_counter += 1
                else:
                    pass

                if bracket_counter > 0 and connectionopen:
                    connections.append(wholelines[i])

                if bracket_counter < 1 and connectionopen:
                    connectionopen = False

            return connections
        except Exception as e:
            print('Failed to get connections')
            raise e

    def getdeformers(self, wholelines: list()):
        '''
        Get deformer lines from fbx lines
        :param wholelines:
        :return:
        '''
        try:
            defor_lines = list()
            bracket_counter = 0
            deformeropen = False

            for i in range(0, wholelines.__len__()-1):
                currentline = wholelines[i]

                if  'Deformer: ' in currentline and \
                    'SubDeformer::' in currentline and \
                    '\"Cluster\"' in currentline and \
                    '{' in currentline:

                    bracket_counter += 1
                    deformeropen = True

                elif '}' in currentline and deformeropen:
                    bracket_counter -= 1
                elif '{' in currentline and deformeropen:
                    bracket_counter += 1
                else: pass

                if bracket_counter > 0 and deformeropen:
                    defor_lines.append(currentline)

                if bracket_counter < 1 and deformeropen:
                    deformeropen = False

            return defor_lines
        except Exception as e:
            print('Failed to get deformers')
            raise e

    def gettakes(self, wholelines: list()):
        '''
        Get take lines from fbx lines
        :param wholelines:
        :return:
        '''

        try:

            takelines = list()
            bracket_counter = 0
            readtakes = False

            i = 0

            while i < wholelines.__len__()-1:
                currentline = wholelines[i]

                if  'Takes:  {' in currentline:
                    bracket_counter += 1
                    readtakes = True

                elif '}' in currentline and readtakes is True:
                    bracket_counter -= 1
                elif '{' in currentline and readtakes is True:
                    bracket_counter += 1
                else:
                    pass

                if bracket_counter > 0 and readtakes is True:
                    takelines.append(currentline)

                if bracket_counter < 1 and readtakes is True:
                    readtakes = False

                i += 1

            return takelines
        except Exception as e:
            print('Failed to get takes')
            raise e

    def gettexture(self, wholelines: list()):
        '''
        Get textre lines from fbx lines
        :param wholelines:
        :return:
        '''

        try:

            texturelines = list()
            bracket_counter = 0
            readtexture = False

            for i in range(0, wholelines.__len__()-1):
                currentline = wholelines[i]

                if  'Texture: ' in currentline and "Texture::" in currentline and '\"TextureVideoClip\"' in currentline and \
                    '{' in currentline:

                    bracket_counter += 1
                    readtexture = True

                elif '}' in currentline and readtexture:
                    bracket_counter -= 1
                elif '{' in currentline and readtexture:
                    bracket_counter += 1
                else: pass

                if bracket_counter > 0 and readtexture:
                    texturelines.append(currentline)

                if bracket_counter < 1 and readtexture:
                    readtexture = False

            return texturelines
        except Exception as e:
            print('Failed to get takes')
            raise e

    def gettextureinfo(self, strings : list()):
        '''
        get texture path and name from texture lines

        :param strings:
        :return shader object:
        '''
        try:
            s = Shader()

            for line in strings:
                if line.strip().startswith("RelativeFilename: "):
                    theline = line.strip()[19:]
                    s.reltexturename = theline[0: theline.__len__()-1]
                    break

            return s
        except Exception as e:
            print("Failed to get texture info")
            raise e

    def getdeformernodes(self, lines : list()):
        '''
        Get the Deformer nodes from from the lines

        :param lines:
        :return:
        '''

        try:
            def_nodes_string = list()
            node = DeformerNodesString()
            bracketcounter = 0

            for line in lines:
                if line.strip().startswith("Deformer: \"SubDeformer"):
                    if node.lines.__len__() > 1:
                        def_nodes_string.append(node)

                    node = DeformerNodesString()
                    bracketcounter += 1

                if line.strip().startswith('}'):
                    bracketcounter -= 1

                node.lines.append(line)

            return def_nodes_string


        except Exception as e:
            print('Failed to get deformer nodes')
            raise e

    def makedeformers(self, defs : list()):
        '''
        Make the deformers from lines of deformer strings

        :param defs:
        :return:
        '''

        try:
            deformers = list()

            for def_single in defs:
                print(def_single.lines)
                deformer = Deformer()

                indices_line = ""
                weight_line = ""
                readIndexes = False
                readWeights = False
                read_trans_lines = False
                read_trans_lines_link = False
                transformLines = ""
                transformLinesLink = ""

                for line in def_single.lines:
                    if line.strip().startswith('Deformer: '):
                        deformer.deformername = line[10:].strip().split(' ')[1]
                        namelen_minus_two = deformer.deformername.__len__() -2
                        deformer.deformername = deformer.deformername[1:namelen_minus_two]

                    if line.strip().startswith('Transform: '):
                        read_trans_lines = True

                    if line.strip().startswith('TransformLink: '):
                        read_trans_lines = False
                        read_trans_lines_link = True

                    if line.strip().startswith('}'):
                        read_trans_lines = False

                    if read_trans_lines:
                        transformLines += line

                    if read_trans_lines_link:
                        transformLinesLink += line

                    if line.strip().startswith('Indexes: '):
                        readIndexes = True

                    if line.strip().startswith('Weights: '):
                        readIndexes = False
                        readWeights = True

                    if line.strip().startswith('Transform:'):
                        readWeights = False

                    if readIndexes:
                        indices_line += line.strip()

                    if readWeights:
                        weight_line += line.strip()

                #end of this loop

                w, i = list(), list()

                if weight_line.__len__() > 0:
                    w = weight_line[9:].split(',')

                if indices_line.__len__() > 0:
                    i = indices_line[9:].split(',')


                for l in w:
                    deformer.weights.append(float(l))

                if w.__len__() < 1:
                    deformer.weights.append(0.0)

                for l in i:
                    deformer.indexes.append(int(l))

                if i.__len__() < 1:
                    deformer.indexes.append(0)

                translines_split = transformLines.replace(" ", "", 99999)[10:].split(",")
                for  t in translines_split:
                    deformer.transform.append(float(t))

                translineslink_split = transformLinesLink.replace(" ", "", 99999)[14:].split(",")
                for  t in translineslink_split:
                    deformer.transformlink.append(float(t))

                deformers.append(deformer)

            return deformers
        except Exception as e:
            print('Failed to make deformers from deformers-string')
            raise e



    def write_mesh_file(self, filename, header_mesh_tup):
        '''
        Write the mesh lines to file, finally
        :param filename:
        :param file_lines:
        :return:
        '''
        try:
            print('Writing Mesh data to file: {}.'.format(filename))


            full = '{}{}{}'.format("<HEADER>\n" +header_mesh_tup[0][0],header_mesh_tup[0][1] + "</HEADER>\n", header_mesh_tup[1])

            with open(filename, 'w', encoding='UTF-8') as outfile:
                outfile.write(full)
            print('Done Writing Mesh data to file: {}.'.format(filename))
        except Exception as e:
            print('Failed to write mesh to file: {} with error {}'.format(filename, e))
            raise e

    def write_skinned_file(self, filename, hmdpc_tuple: tuple()):
        '''
        Write the skinned mesh data to file
        :param filename:
        :param mesh_deformer_pose_tuple: (mesh_string, deformer_string, posenodes_String)
        :return:
        '''
        try:
            header, mesh_string, deformers_string, poses_string, connection_string = hmdpc_tuple
            full_data = '{}{}{}{}{}{}'.format("<HEADER>\n" + header[0],header[1] + "</HEADER>\n", mesh_string, deformers_string, poses_string, connection_string)

            print('Writing Skinned data to file: {}.'.format(filename))

            with open(filename, 'w', encoding='UTF-8') as outfile:
                outfile.write(full_data)

            print('Done Writing Skinned data to file: {}.'.format(filename))
        except Exception as e:
            print('Failed to write Skinned to file: {} with error {}'.format(filename, e))
            raise e

    def create_skinned_dict(self, skinned_mesh_tup: tuple()):
        staticmodel, materialname, deformers, connections, poseNodes_model = skinned_mesh_tup

        header = {'meshname' : staticmodel.meshname, 'material' : materialname.replace('.tga', '') }
        dic = {}
        dic['header'] = header




        return dic

    def write_meshdata_lines(self, staticmodel: MeshDataStatic, textureinfo: Shader):
        '''
        This function takes a Modelmesh object and textureinfo Object to write the
        parsed mesh object to a file

        Throws an Exception if it fails, returns void else

        :param staticmodel:
        :param textureinfo:
        :param filename:
        :return void:
        '''

        # Check if the modeldata is valid with > 0
        if (staticmodel.points.__len__() > 0
                and staticmodel.p_index.__len__() > 0
                and staticmodel.normals.__len__() > 0
                and staticmodel.uv.__len__() > 0
                and staticmodel.uv_index.__len__() > 0):

            # Start creating the string format by appending

            # setup and colortexturepath
            full = ''

            # start appending the modeldata, points, indices
            # Points first
            full += "<POINTS>\n"
            points_as_str = []
            for x in staticmodel.points:
                points_as_str.append('{:.4f}'.format(x))
            p_lines = '\n'.join(points_as_str)
            full += p_lines
            full += "\n"
            full += "</POINTS>\n"

            # Point indices now
            full += "<POINTI>\n"
            pindices_as_str = []
            for x in staticmodel.p_index:
                pindices_as_str.append('{:d}'.format(x))
            pi_lines = '\n'.join(pindices_as_str)
            full += pi_lines
            full += "\n"
            full += "</POINTI>\n"

            full += "<NORMAL>\n"
            normal_as_str = []
            for x in staticmodel.normals:
                normal_as_str.append('{:.4f}'.format(x))
                normal = '\n'.join(normal_as_str)
            full += normal
            full += "\n"
            full += "</NORMAL>\n"

            full += "<UV>\n"
            uv_as_str = []
            for x in staticmodel.uv:
                uv_as_str.append('{:.4f}'.format(x))
                uv = '\n'.join(uv_as_str)
            full += uv
            full += "\n"
            full += "</UV>\n"

            full += "<UVI>\n"
            uvi_as_str = []
            for x in staticmodel.uv_index:
                uvi_as_str.append('{:d}'.format(x))
                uvi = '\n'.join(uvi_as_str)
            full += uvi
            full += "\n"
            full += "</UVI>\n"

            return full

        else:
            l = list()
            l.extend([staticmodel.points, staticmodel.p_index, staticmodel.normals, staticmodel.uv,
                      staticmodel.uv_index])
            raise DataParseError(l)

    def write_connections_lines(self, connections: list()):
        '''
        Write the Connections for the Deformerskeleton to the file, with parent : child for each line

        :param connections:
        :param filename:
        :return void:
        '''

        full = ''
        if connections.__len__() < 1:
            raise DataParseError('No connection-lines contained')

        # Determine which prefix the string got since there can be
        # some prefix on the Modelname, then append the lines
        full += "<CONNECTIONS>\n"
        for i in range(0, connections.__len__()):
            p, c = '', ''
            if "Model::" in connections[i].parent:
                p = connections[i].parent[7:]
                c = connections[i].child[7:]

            if "Material::" in connections[i].parent:
                p = connections[i].parent
                c = connections[i].child

            if "Texture::" in connections[i].parent:
                p = connections[i].parent
                c = connections[i].child

            if "Video::" in connections[i].parent:
                p = connections[i].parent
                c = connections[i].child

            full += c
            full += ' '
            full += p
            full += "\n"

        full += "</CONNECTIONS>\n"

        return full

    def write_deformers_lines(self, deformers: list()):
        '''
        Write the Deformers, including the weight information for the Deformerskeleton to the file

        :param deformers:
        :param filename:
        :return:
        '''
        full = ''

        if deformers.__len__() < 1:
            print('Writing Deformer-data failed, no data present')
            raise DataWriteError(deformers)

        # Create the full Deformerlist as a string
        full += '<DEFORMERS>\n'
        for i in range(0, deformers.__len__()):
            print('Writing Deformer: {} to string'.format(deformers[i].deformername))
            if "SubDeformer::Cluster_" in deformers[i].deformername:
                full += '<DEFORMER>\n'
                full += 'NAME: '
                full += deformers[i].deformername[21:]
                full += '\n'
            else:
                continue

            # Write Transform matrix to file
            full += "<TRANSFORM>\n"
            for x in range(0, deformers[i].transform.__len__()):
                full += str(deformers[i].transform[x])
                full += '\n'
            full += "</TRANSFORM>\n"

            # Write Transformlink matrix to file
            full += "<TRANSFORMLINK>\n"
            for x in range(0, deformers[i].transformlink.__len__()):
                full += str(deformers[i].transformlink[x])
                full += '\n'
            full += "</TRANSFORMLINK>\n"

            # Write weight values to file
            full += "<WEIGHT>\n"
            for x in range(0, deformers[i].weights.__len__()):
                full += str(deformers[i].weights[x])
                full += '\n'
            full += "</WEIGHT>\n"

            # Write index values to file
            full += "<INDEX>\n"
            for x in range(0, deformers[i].indexes.__len__()):
                full += str(deformers[i].indexes[x])
                full += '\n'
            full += "</INDEX>\n"
            full += '</DEFORMER>\n'

        full += '</DEFORMERS>\n'

        return full

    def write_posenodes_lines(self, posenodes: list()):
        '''
        Write posenodes to file

        :param posenodes:
        :param filename:
        :return:
        '''

        full = ''
        if posenodes.__len__() < 1:
            print('Writing posenodes failed, no data present')
            raise DataWriteError(posenodes)

        full += '<POSENODES>\n'
        for i in range(0, posenodes.__len__()):
            if "Model::" in str(posenodes[i].nodename):
                full += '<POSENODE>\n'
                full += 'NAME: {}\n'.format(posenodes[i].nodename[7:])
                full += '<MATRIX>\n'
                for x in range(0, posenodes[i].matrix.__len__()):
                    full += str(posenodes[i].matrix[x]) + '\n'
                full += '</MATRIX>\n'
                full += '</POSENODE>\n'
            else:
                continue
        full += '</POSENODES>\n'

        return full

    def write_animation_file(self, animated_deformers: list(), filename: str):
        '''
        Write the animation to a file

        :param animated_deformers:
        :param filename:
        :return:
        '''
        print('Starting to write animation  {} to file...'.format(filename))

        if animated_deformers.__len__() < 1:
            print('Cannot write empty animation data')
            raise Exception('Empty Animation data cannot be written to file')

        try:
            full = ''

            if animated_deformers.__len__() < 1:
                print('Writing Deformer-data failed, no data present')
                raise DataWriteError(animated_deformers)

            for i in range(0, animated_deformers.__len__()):
                full += '<JOINT>\n'
                name = animated_deformers[i].deformername[7:]

                full += 'NAME: '
                full += name
                full += '\n'

                # write trans x lines
                full += '<TRANS_X_VAL>\n'
                for j in range(0, animated_deformers[i].channel_translate.channel_x.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_translate.channel_x.keyvalue[j])
                    full += "\n"
                full += "</TRANS_X_VAL>\n"

                full += '<TRANS_X_DIS>\n'
                for j in range(0, animated_deformers[i].channel_translate.channel_x.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_translate.channel_x.keydistances[j]))
                    full += "\n"
                full += "</TRANS_X_DIS>\n"

                # write trans y lines
                full += '<TRANS_Y_VAL>\n'
                for j in range(0, animated_deformers[i].channel_translate.channel_y.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_translate.channel_y.keyvalue[j])
                    full += "\n"
                full += "</TRANS_Y_VAL>\n"

                full += '<TRANS_Y_DIS>\n'
                for j in range(0, animated_deformers[i].channel_translate.channel_y.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_translate.channel_y.keydistances[j]))
                    full += "\n"
                full += "</TRANS_Y_DIS>\n"

                # write trans z lines
                full += '<TRANS_Z_VAL>\n'
                for j in range(0, animated_deformers[i].channel_translate.channel_z.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_translate.channel_z.keyvalue[j])
                    full += "\n"
                full += "</TRANS_Z_VAL>\n"

                full += '<TRANS_Z_DIS>\n'
                for j in range(0, animated_deformers[i].channel_translate.channel_z.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_translate.channel_z.keydistances[j]))
                    full += "\n"
                full += "</TRANS_Z_DIS>\n"

                # write rot x  lines
                full += '<ROT_X_VAL>\n'
                for j in range(0, animated_deformers[i].channel_rotate.channel_x.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_rotate.channel_x.keyvalue[j])
                    full += "\n"
                full += "</ROT_X_VAL>\n"

                full += '<ROT_X_DIS>\n'
                for j in range(0, animated_deformers[i].channel_rotate.channel_x.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_rotate.channel_x.keydistances[j]))
                    full += "\n"
                full += "</ROT_X_DIS>\n"

                # write rot y  lines
                full += '<ROT_Y_VAL>\n'
                for j in range(0, animated_deformers[i].channel_rotate.channel_y.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_rotate.channel_y.keyvalue[j])
                    full += "\n"
                full += "</ROT_Y_VAL>\n"

                full += '<ROT_Y_DIS>\n'
                for j in range(0, animated_deformers[i].channel_rotate.channel_y.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_rotate.channel_y.keydistances[j]))
                    full += "\n"
                full += "</ROT_Y_DIS>\n"

                # write rot z  lines
                full += '<ROT_Z_VAL>\n'
                for j in range(0, animated_deformers[i].channel_rotate.channel_z.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_rotate.channel_z.keyvalue[j])
                    full += "\n"
                full += "</ROT_Z_VAL>\n"

                full += '<ROT_Z_DIS>\n'
                for j in range(0, animated_deformers[i].channel_rotate.channel_z.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_rotate.channel_z.keydistances[j]))
                    full += "\n"
                full += "</ROT_Z_DIS>\n"

                # write scale x lines
                full += '<SCALE_X_VAL>\n'
                for j in range(0, animated_deformers[i].channel_scale.channel_x.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_scale.channel_x.keyvalue[j])
                    full += "\n"
                full += "</SCALE_X_VAL>\n"

                full += '<SCALE_X_DIS>\n'
                for j in range(0, animated_deformers[i].channel_scale.channel_x.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_scale.channel_x.keydistances[j]))
                    full += "\n"
                full += "</SCALE_X_DIS>\n"

                # write scale y lines
                full += '<SCALE_Y_VAL>\n'
                for j in range(0, animated_deformers[i].channel_scale.channel_x.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_scale.channel_x.keyvalue[j])
                    full += "\n"
                full += "</SCALE_Y_VAL>\n"

                full += '<SCALE_Y_DIS>\n'
                for j in range(0, animated_deformers[i].channel_scale.channel_y.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_scale.channel_y.keydistances[j]))
                    full += "\n"
                full += "</SCALE_Y_DIS>\n"

                # write scale z lines
                full += '<SCALE_Z_VAL>\n'
                for j in range(0, animated_deformers[i].channel_scale.channel_z.keyvalue.__len__()):
                    full += str(animated_deformers[i].channel_scale.channel_z.keyvalue[j])
                    full += "\n"
                full += "</SCALE_Z_VAL>\n"

                full += '<SCALE_Z_DIS>\n'
                for j in range(0, animated_deformers[i].channel_scale.channel_z.keydistances.__len__()):
                    full += str(int(animated_deformers[i].channel_scale.channel_z.keydistances[j]))
                    full += "\n"
                full += "</SCALE_Z_DIS>\n"

                full += "</JOINT>\n"

            with open(filename, 'w', encoding='UTF-8') as outfile:
                outfile.write(full)
                outfile.close()  # I know...

            print('Succesfully wrote animation data: {} to file.'.format(filename))

            return

        except Exception as e:
            print('There was a problem writing Deformer data to file')
            raise e

    def convert_skinned(self, name, lines):
        '''
        This function will only parse animation

        :param name:
        :param lines:
        :return:
        '''

        '''
                This function will only parse static mesh
                :param lines:
                :return:
                '''
        mesh_lines = []
        scopecounter = 0
        start_adding = False

        # Get only the mesh lines from the file
        for line in lines:
            newline = line.strip()

            if newline.startswith(';'):
                continue

            if "Model" in newline and " \"Mesh\"" in newline and '{' in newline:
                start_adding = True
                mesh_lines.append(newline)
                scopecounter += 1
                continue

            if start_adding and scopecounter > 0:
                mesh_lines.append(newline)
                if '{' in newline:
                    scopecounter += 1

                if '}' in newline:
                    scopecounter -= 1

        texture_lines       = self.gettexture(lines)
        texture_data        = self.gettextureinfo(texture_lines)
        mesh_pack           = self.createmodelmeshlinespacked(mesh_lines)
        staticmodel         = self.create_mesh_data_static(mesh_pack)

        string_pose_Nodes       = self.getbindposelines(lines)
        string_defor_nodes      = self.getdeformers(lines)
        deformerNodes_seperated = self.getdeformernodes(string_defor_nodes)
        fbx_get_connections     = self.getconnections(lines)

        poseNodes_model     = self.createposenodes(string_pose_Nodes)
        connections         = self.create_connections(fbx_get_connections)
        deformers           = self.makedeformers(deformerNodes_seperated)

        #return this as a tuple
        connection_string   = self.write_connections_lines(connections)
        deformers_string    = self.write_deformers_lines(deformers)
        poses_string        = self.write_posenodes_lines(poseNodes_model)
        mesh_string         = self.write_meshdata_lines(staticmodel, texture_data)

        header = ('meshname: {}\n'.format(staticmodel.meshname), 'material: {}\n'.format(texture_data.reltexturename.split('\\')[-1]))

        full_tup = (header, mesh_string, deformers_string, poses_string, connection_string)

        final_dict = self.create_skinned_dict( (staticmodel, texture_data.reltexturename.split('\\')[-1], deformers, connections, poseNodes_model))

        self.write_skinned_file(name,full_tup)

    def convert_animation(self, name, lines):
        '''
        This function will only parse animation

        :param name:
        :param lines:
        :return:
        '''

        takes = self.gettakes(lines)
        animated_deformers_done = self.get_animated_deformer_String(takes)
        self.write_animation_file(animated_deformers_done, name + ".animation")

    def convert_mesh(self,name,lines):
        '''
        This function will only parse static mesh
        :param lines:
        :return:
        '''
        mesh_lines = []
        scopecounter = 0
        start_adding = False

        #Get only the mesh lines from the file
        for line in lines:
            newline = line.strip()

            if newline.startswith(';'):
                continue

            if  "Model" in newline and " \"Mesh\"" in newline and '{' in newline:

                start_adding = True
                mesh_lines.append(newline)
                scopecounter += 1
                continue

            if start_adding and scopecounter > 0:
                mesh_lines.append(newline)
                if '{' in newline:
                    scopecounter += 1

                if '}' in newline:
                    scopecounter -= 1

        texture_lines = self.gettexture(lines)
        texture_data = self.gettextureinfo(texture_lines)
        mesh_pack    = self.createmodelmeshlinespacked(mesh_lines)
        staticmodel = self.create_mesh_data_static(mesh_pack)
        mesh_string = self.write_meshdata_lines(staticmodel, texture_data)

        header = ('meshname: {}\n'.format(staticmodel.meshname),'material: {}\n'.format(texture_data.reltexturename.split('\\')[-1]))

        self.write_mesh_file(name, (header, mesh_string ))

if __name__ == '__main__':
    arguments = argv

    objectonly = False
    animation = False
    skinned = False

    in_name= None
    out_path= None
    filename = None
    parser = FbxParser()

    if len(arguments) < 6:
        raise ValueError("Argument Error,", "Not enough parameters given")

    if 'o' in arguments[1]:
        objectonly = True

    if 'a' in arguments[1]:
        animation= True

    if 's' in arguments[1]:
        skinned = True

    if '-in' in arguments[2]:
        in_name = arguments[3]
    else:
        raise ValueError("Missing in-file name")

    if '-out' in arguments[4]:
        out_path = arguments[5]
    else:
        raise ValueError("Missing out-dir name")
    filename = in_name.replace('.fbx', '')

    with open(in_name, 'r') as f:
        lines = f.readlines()

    if objectonly:
        parser.convert_mesh(out_path + '//' + filename + '.mesh', lines)

    if skinned:
        parser.convert_skinned(out_path + '//' + filename + '.mesh', lines)

    if animation:
        parser.convert_animation(out_path + '//' + filename, lines)

