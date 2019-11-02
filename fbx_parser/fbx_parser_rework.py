__author__ = "Nouri Aissaoui"
__copyright__ = "Copyright 2019, Bluegem Engine"
__credits__ = ["Nouri Aissaoui"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Nouri Aissaoui"
__email__ = "nouria1@hotmail.com"
__status__ = "Production"

'''
IMPORTANT NOTE

This python FBX importer Only works for
the FBX-ASCII format of Version 6.1.0 from 2006
'''

import os
import time
import argparse

class FbxParser:

    def _create_posenodes(self, strnodes):
        '''
        Create the pose-nodes from a list of posenode strings
        :param strnodes:
        :return dictionairy of pose-node-dicts:
        '''

        nodes = list()

        for nodestr in strnodes:
            node = { }

            for line in nodestr['lines']:
                if line.startswith("Node: "):
                    nodeline = line.strip()[7: line.__len__()-1]
                    node['name'] = nodeline

            matrixline = ''
            readmatrix = False

            for line in nodestr['lines']:
                if line.startswith("Matrix: "):
                    readmatrix = True
                    nodeline = line.strip()[8:]
                    matrixline += nodeline
                    continue

                if readmatrix:
                     matrixline += line

                if "}" in line: break

            matrixl = matrixline.split(",")
            floats = list()
            for i in range(0,matrixl.__len__()):
                floats.append(float(matrixl[i]))

            node['matrix'] = floats

            nodes.append(node)

        return {'posenodes' : nodes }

    def _extractArray(self, lines : list(), indexmode : bool):
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

    def _extractkeys(self, lines : list()):
        '''
        Extract keys, convert from... microseconds? to frames
        :param lines:
        :return:
        '''
        try:

            box = {}
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
                box['keys'] = list()
                box['values'] = list()
                return box

            box['keys'] = keys
            box['values'] = vals

            return box
        except Exception as e:
            print('Failed to resolve keys')
            raise e

    def _create_animated_deformer(self, def_string):
        '''
        This function takes deformerStrings and turns them into Full
        Deformer objects, which are ready to be written to file

        :param def_string:
        :return:
        '''


        len = def_string[0].strip().__len__()
        deformer_name = def_string[0].strip()[8: len - 3]
        channel_T = list()
        sub_t_x = list()
        sub_t_y = list()
        sub_t_z = list()

        channel_R = list()
        sub_r_x = list()
        sub_r_y = list()
        sub_r_z = list()

        channel_S = list()
        sub_s_x = list()
        sub_s_y = list()
        sub_s_z = list()

        bracketcounter = 0

        #for Translates
        for line in def_string:
            if line.strip().startswith('Channel: \"T\"'):
                bracketcounter += 1
                channel_T.append(line)
                continue

            if '{' in line.strip() and bracketcounter > 0:
                bracketcounter += 1

            if '}' in line.strip() and bracketcounter > 0:
                bracketcounter -= 1

            if bracketcounter > 0:
                channel_T.append(line)

        #for Rotations
        for line in def_string:
            if line.strip().startswith('Channel: \"R\"'):
                bracketcounter += 1
                channel_R.append(line)
                continue

            if '{' in line.strip() and bracketcounter > 0:
                bracketcounter += 1

            if '}' in line.strip() and bracketcounter > 0:
                bracketcounter -= 1

            if bracketcounter > 0:
                channel_R.append(line)

        #for Scale
        for line in def_string:
            if line.strip().startswith('Channel: \"S\"'):
                bracketcounter += 1
                channel_S.append(line)
                continue

            if '{' in line.strip() and bracketcounter > 0:
                bracketcounter += 1

            if '}' in line.strip() and bracketcounter > 0:
                bracketcounter -= 1

            if bracketcounter > 0:
                channel_S.append(line)

        #dissecting the translate lines from the transform channel
        bracketcounter = 0
        i = 0
        while i <  channel_T.__len__():
            if channel_T[i].strip().startswith('Channel \"T\" {'):
                continue
            if channel_T[i].strip().startswith('Channel \"X\" {'):
                bracketcounter+= 1
                sub_t_x.__add__(channel_T[i])
                continue

            if "{" in channel_T[i].strip():
                bracketcounter += 1

            if "}" in channel_T[i].strip():
                bracketcounter -= 1

            if "Channel: \"Y\" {" in channel_T[i].strip():
                break

            if bracketcounter > 0:
                sub_t_x.append(channel_T[i])

            i += 1

        while i < channel_T.__len__():

            if channel_T[i].strip().startswith('Channel \"Y\" {'):
                bracketcounter+= 1
                sub_t_y.__add__(channel_T[i])
                continue

            if "{" in channel_T[i].strip():
                bracketcounter += 1

            if "}" in channel_T[i].strip():
                bracketcounter -= 1

            if "Channel: \"Z\" {" in channel_T[i].strip():
                break

            if bracketcounter > 0:
                sub_t_y.append(channel_T[i])

            i += 1

        bracketcounter = 0 #haa? why?
        while i < channel_T.__len__():

            if channel_T[i].strip().startswith('Channel \"Z\" {'):
                bracketcounter+= 1
                sub_t_z.__add__(channel_T[i])
                continue

            if "{" in channel_T[i].strip():
                bracketcounter += 1

            if "}" in channel_T[i].strip():
                bracketcounter -= 1

            if "Color: " in channel_T[i].strip():
                break

            if bracketcounter > 0:
                sub_t_z.append(channel_T[i])
            i += 1

        #dissecting the rotate lines from the transform channel

        bracketcounter = 0
        i = 0
        while i <  channel_T.__len__():
            if channel_R[i].strip().startswith('Channel \"R\" {'):
                continue
            if channel_R[i].strip().startswith('Channel \"X\" {'):
                bracketcounter+= 1
                sub_r_x.__add__(channel_R[i])
                continue

            if "{" in channel_R[i].strip():
                bracketcounter += 1

            if "}" in channel_R[i].strip():
                bracketcounter -= 1

            if "Channel: \"Y\" {" in channel_R[i].strip():
                break

            if bracketcounter > 0:
                sub_r_x.append(channel_R[i])

            i += 1

        while i < channel_R.__len__():

            if channel_R[i].strip().startswith('Channel \"Y\" {'):
                bracketcounter+= 1
                sub_r_y.__add__(channel_R[i])
                continue

            if "{" in channel_R[i].strip():
                bracketcounter += 1

            if "}" in channel_R[i].strip():
                bracketcounter -= 1

            if "Channel: \"Z\" {" in channel_R[i].strip():
                break

            if bracketcounter > 0:
                sub_r_y.append(channel_R[i])

            i += 1

        bracketcounter = 0
        while i < channel_R.__len__():

            if channel_R[i].strip().startswith('Channel \"Z\" {'):
                bracketcounter+= 1
                sub_r_z.__add__(channel_R[i])
                continue

            if "{" in channel_R[i].strip():
                bracketcounter += 1

            if "}" in channel_R[i].strip():
                bracketcounter -= 1

            if "Color: " in channel_R[i].strip():
                break

            if bracketcounter > 0:
                sub_r_z.append(channel_R[i])
            i += 1

        #dissecting the scale lines from the transform channel

        bracketcounter = 0
        i = 0
        while i <  channel_S.__len__():
            if channel_S[i].strip().startswith('Channel \"R\" {'):
                continue
            if channel_S[i].strip().startswith('Channel \"X\" {'):
                bracketcounter+= 1
                sub_s_x.__add__(channel_S[i])
                continue

            if "{" in channel_S[i].strip():
                bracketcounter += 1

            if "}" in channel_S[i].strip():
                bracketcounter -= 1

            if "Channel: \"Y\" {" in channel_S[i].strip():
                break

            if bracketcounter > 0:
                sub_s_x.append(channel_S[i])
            i += 1

        while i < channel_S.__len__():

            if channel_S[i].strip().startswith('Channel \"Y\" {'):
                bracketcounter+= 1
                sub_s_y.__add__(channel_S[i])
                continue

            if "{" in channel_S[i].strip():
                bracketcounter += 1

            if "}" in channel_S[i].strip():
                bracketcounter -= 1

            if "Channel: \"Z\" {" in channel_S[i].strip():
                break

            if bracketcounter > 0:
                sub_s_y.append(channel_S[i])
            i += 1

        bracketcounter = 0 #haa? why?
        while i < channel_S.__len__():
            if channel_S[i].strip().startswith('Channel \"Z\" {'):
                bracketcounter+= 1
                sub_s_z.__add__(channel_S[i])
                continue
            if "{" in channel_S[i].strip():
                bracketcounter += 1

            if "}" in channel_S[i].strip():
                bracketcounter -= 1

            if "Color: " in channel_S[i].strip():
                break

            if bracketcounter > 0:
                sub_s_z.append(channel_S[i])
            i += 1

        sub_t_x_bin = { 'keydistances' : list(), 'keyvalues' : list() }
        sub_t_y_bin = { 'keydistances' : list(), 'keyvalues' : list() }
        sub_t_z_bin = { 'keydistances' : list(), 'keyvalues' : list() }

        sub_r_x_bin = { 'keydistances' : list(), 'keyvalues' : list() }
        sub_r_y_bin = { 'keydistances' : list(), 'keyvalues' : list() }
        sub_r_z_bin = { 'keydistances' : list(), 'keyvalues' : list() }

        sub_s_x_bin = { 'keydistances' : list(), 'keyvalues' : list() }
        sub_s_y_bin = { 'keydistances' : list(), 'keyvalues' : list() }
        sub_s_z_bin = { 'keydistances' : list(), 'keyvalues' : list() }


        box_t_x = self._extractkeys(sub_t_x)
        box_t_y = self._extractkeys(sub_t_y)
        box_t_z = self._extractkeys(sub_t_z)

        sub_t_x_bin['keydistances'] = box_t_x['keys']
        sub_t_x_bin['keyvalues']    = box_t_x['values']
        sub_t_y_bin['keydistances'] = box_t_y['keys']
        sub_t_y_bin['keyvalues']    = box_t_y['values']
        sub_t_z_bin['keydistances'] = box_t_z['keys']
        sub_t_z_bin['keyvalues']    = box_t_z['values']



        box_r_x = self._extractkeys(sub_r_x)
        box_r_y = self._extractkeys(sub_r_y)
        box_r_z = self._extractkeys(sub_r_z)

        sub_r_x_bin['keydistances'] = box_r_x['keys']
        sub_r_x_bin['keyvalues']    = box_r_x['values']
        sub_r_y_bin['keydistances'] = box_r_y['keys']
        sub_r_y_bin['keyvalues']    = box_r_y['values']
        sub_r_z_bin['keydistances'] = box_r_z['keys']
        sub_r_z_bin['keyvalues']    = box_r_z['values']


        box_s_x = self._extractkeys(sub_s_x)
        box_s_y = self._extractkeys(sub_s_y)
        box_s_z = self._extractkeys(sub_s_z)

        sub_s_x_bin['keydistances'] = box_s_x['keys']
        sub_s_x_bin['keyvalues']    = box_s_x['values']
        sub_s_y_bin['keydistances'] = box_s_y['keys']
        sub_s_y_bin['keyvalues']    = box_s_y['values']
        sub_s_z_bin['keydistances'] = box_s_z['keys']
        sub_s_z_bin['keyvalues']    = box_s_z['values']

        T_bin = {}
        R_bin = {}
        S_bin = {}

        T_bin['channel_x'] = sub_t_x_bin
        T_bin['channel_y'] = sub_t_y_bin
        T_bin['channel_z'] = sub_t_z_bin

        R_bin['channel_x'] = sub_r_x_bin
        R_bin['channel_y'] = sub_r_y_bin
        R_bin['channel_z'] = sub_r_z_bin

        S_bin['channel_x'] = sub_s_x_bin
        S_bin['channel_y'] = sub_s_y_bin
        S_bin['channel_z'] = sub_s_z_bin

        deformer = {}
        deformer['channel_translate']   = T_bin
        deformer['channel_rotate']      = R_bin
        deformer['channel_scale']       = S_bin
        deformer['deformername']        = deformer_name

        return deformer

    def _get_mesh_name(self, meshlines : list()) -> str():
        '''
        Get the name of the mesh

        :param meshlines:
        :return:
        '''

        if meshlines.__len__() < 1:
            raise Exception('No Mesh data in meshlines')

        name = meshlines[0][8:]
        name = name[0: name.find("\"")]

        return name

    def _get_mesh_data(self, meshlines : list()) -> dict():
        '''
        Extract the mesh data from the lines

        :param fbx mesh lines:
        :return mesh-dict:
        '''

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

        for line in meshlines:
            # Get mesh data lines from the file, for vertices,
            # until we reach PolygonVertexIndex, which indicates the end
            if line.startswith("Vertices: "):
                readvertices = True

            if "PolygonVertexIndex: " in line:
                readvertices = False

            if readvertices:
                if "Vertices: " in line:
                    verticelines.append(line[10:])
                else:
                    verticelines.append(line)

            # Get mesh data lines from the file, for Point Indices,
            # until we reach Edges, which indicates the end
            if line.startswith("PolygonVertexIndex: "):
                readvertexindex = True

            if "Edges: " in line or 'GeometryVersion' in line:
                readvertexindex = False

            if readvertexindex:
                if "PolygonVertexIndex: " in line:
                    vindex_lines.append(line[20:])
                else:
                    vindex_lines.append(line)

            # Get mesh data lines from the file, for Normals Indices,
            # until we reach a } in the file, which indicates the end
            if line.startswith("Normals: "):
                readnormals = True

            if "}" in line:
                readnormals = False

            if readnormals:
                if "Normals: " in line:
                    normals_lines.append(line[9:])
                else:
                    normals_lines.append(line)

            # Get mesh data lines from the file, for UV now,
            # until we reach a } in the file, which indicates the end
            if line.startswith("UV: ") and uv_lines.__len__() < 1:
                read_uv = True

            if "UVIndex: " in line:
                read_uv = False

            if read_uv:
                if line.startswith('UV: '):
                    uv_lines.append(line[4:])
                else:
                    uv_lines.append(line)

            # Get mesh data lines from the file, for UV Index now,
            # until we reach a } in the file, which indicates the end
            if 'UVIndex: ' in line and uv_index_lines.__len__() < 1:
                read_uv_index = True

            if "}" in line:
                read_uv_index = False

            if read_uv_index:
                if line.startswith('UVIndex: '):
                    uv_index_lines.append(line[9:])
                else:
                    uv_index_lines.append(line)

        #Now parse the mesh lines into lists of points/integers
        pointsString = ''.join(verticelines).replace('\n','')
        pointList =list(map(float,  pointsString.split(',')))

        pointiString = ''.join(vindex_lines).replace('\n','')
        pointiList = list(map(int, pointiString.split(',')))

        normalsString = ''.join(normals_lines).replace('\n','')
        normalsList = list(map(float, normalsString.split(',')))

        uvString = ''.join(uv_lines).replace('\n','')
        uvList = list(map(float, uvString.split(',')))

        uviString = ''.join(uv_index_lines).replace('\n','')
        uviList = list(map(int, uviString.split(',')))

        #replace the negative indicies in Points with positive indexes and do -1,
        #since the format can use quads or tris, the negative number indicates a tri or quad indexing
        #since we ONLY use tris, we can easily replace the negative numbers with the right one.
        newpointi = []
        for x in pointiList:
            if x < 0:
                y = x*-1 -1
                newpointi.append(y)
            else:
                newpointi.append(x)

        mesh_dict = {'points':  pointList,
                     'pointsi': newpointi,
                     'normals': normalsList,
                     'uv':      uvList,
                     'uvi':     uviList}

        return mesh_dict

    def _get_bindpose_lines(self, wholelines):
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
            pose = { }

            #Get each block of poses from the lines
            i = 0
            while i < posenodes_lines.__len__():
                if posenodes_lines[i].startswith('PoseNode: '):
                    pose = { 'lines' : list(), }

                while True:
                    pose['lines'].append(posenodes_lines[i])
                    i += 1

                    if posenodes_lines[i].strip().startswith('}'):
                        break

                posenode_list.append(pose)
                i += 1

            return posenode_list

        except Exception as e:
            print('Failed to get bindposelines')
            raise e

    def _get_connections(self, wholelines: list()):
        '''
            parse the connection lines from the fbx lines
            :param: fbx lines
            :return: connections dict
            '''

        connections = list()
        bracket_counter = 0
        connectionopen = False

        for i in range(0, wholelines.__len__() - 1):

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

        conn_new = list()

        for line in connections:
            if line.strip().startswith("Connect: "):
                if "Deformer::" in line or "SubDeformer::" in line:
                    continue

                con = { 'child' : '' , 'parent' : '' }
                thisline = line.strip()[8:]
                splited = thisline.split(",")

                splited[0] = splited[0].strip()[1: splited[0].__len__() - 2]
                splited[1] = splited[1].strip()[1: splited[1].__len__() - 2]
                splited[2] = splited[2].strip()[1: splited[2].__len__() - 2]

                con['child'] = splited[2]
                con['parent'] = splited[1]

                conn_new.append(con)

        return conn_new

    def _parse_take(self, lines: list()):
        '''
        Get take lines from fbx lines
        :param wholelines:
        :return:
        '''

        takelines = list()
        bracket_counter = 0
        readtakes = False

        i = 0

        while i < lines.__len__() - 1:
            currentline = lines[i]

            if 'Takes:  {' in currentline:
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

        #Now parse the take lines
        take_perjointdata = list()
        begins = list()
        ends = list()

        brackets = 0

        for i in range(0, takelines.__len__()):
            line = takelines[i]
            if line.strip().startswith('Takes: '):
                continue
            if line.strip().startswith('Take: '):
                continue

            if 'Model: \"' in line and '{' in line:
                brackets += 1
                begins.append(i)

            elif '{' in line and not 'Model: \"' in line:
                brackets += 1
            else:
                pass

            if '}' in line:
                brackets -= 1
                if brackets == 0:
                    ends.append(i)

        for i in range(0, begins.__len__()):
            node = list()

            j = begins[i]
            while j < ends[i]:
                node.append(takelines[j])
                j += 1

            take_perjointdata.append(node)

        animated_deformers = list()

        for deformer in take_perjointdata:
            animated_deformers.append(self._create_animated_deformer(deformer))

        return animated_deformers

    def _getmaterialname(self, fbxlines: list()):
        '''
        get the material file name
        :param fbxlines
        :return material file name:
        '''

        matlines = list()
        bracket_counter = 0
        readtexture = False
        materialline = str()
        for i in range(0, fbxlines.__len__() - 1):
            currentline = fbxlines[i]

            if 'Texture: ' in currentline and "Texture::" in currentline and \
                    '\"TextureVideoClip\"' in currentline and \
                    '{' in currentline:

                bracket_counter += 1
                readtexture = True

            elif '}' in currentline and readtexture:
                bracket_counter -= 1
            elif '{' in currentline and readtexture:
                bracket_counter += 1
            else:
                pass

            if bracket_counter > 0 and readtexture:
                matlines.append(currentline)

            if bracket_counter < 1 and readtexture:
                readtexture = False

        for line in matlines:
            if line.strip().startswith("RelativeFilename: "):
                theline = line.strip()[19:]
                materialline = theline[0: theline.__len__() - 1]
                break
        return materialline

    def _get_deformernodes(self, lines):
        '''
        Get deformer lines from fbx lines
        :param wholelines:
        :return:
        '''

        defor_lines = list()
        bracket_counter = 0
        deformeropen = False

        for i in range(0, lines.__len__()-1):
            currentline = lines[i]

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

        '''
        Get the Deformer nodes from the lines

        :param lines:
        :return:
        '''

        def_nodes_string = list()
        node = { 'lines' : []}
        bracketcounter = 0

        for line in defor_lines:
            if line.strip().startswith("Deformer: \"SubDeformer"):
                if node['lines'].__len__() > 1:
                    def_nodes_string.append(node)

                node  = { 'lines' : [] }
                bracketcounter += 1

            if line.strip().startswith('}'):
                bracketcounter -= 1

            node['lines'].append(line)

        return def_nodes_string

    def _parse_deformers(self, defs : list()):
        '''
        Make the deformers from lines of deformer strings

        :param defs:
        :return:
        '''

        deformers = list()

        for def_single in defs:
            deformer = {'transform': [], 'name': '', 'weights' : [], 'indexes' : [], 'transformlink' : []}

            indices_line = ""
            weight_line = ""
            readIndexes = False
            readWeights = False
            read_trans_lines = False
            read_trans_lines_link = False
            transformLines = ""
            transformLinesLink = ""

            for line in def_single['lines']:
                if line.strip().startswith('Deformer: '):
                    deformer['name'] = line[10:].strip().split(' ')[1]
                    namelen_minus_two = deformer['name'].__len__() -2
                    deformer['name'] = deformer['name'][1:namelen_minus_two]



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

            w, i = list(), list()

            if weight_line.__len__() > 0:
                w = weight_line[9:].split(',')

            if indices_line.__len__() > 0:
                i = indices_line[9:].split(',')

            for l in w:
                deformer['weights'].append(float(l))
            if w.__len__() < 1:
                deformer['weights'].append(0.0)

            for l in i:
                deformer['indexes'].append(int(l))
            if i.__len__() < 1:
                deformer['indexes'].append(0)

            translines_split = transformLines.replace(" ", "", 99999)[10:].split(",")
            for  t in translines_split:
                deformer['transform'].append(float(t))

            translineslink_split = transformLinesLink.replace(" ", "", 99999)[14:].split(",")
            for  t in translineslink_split:
                deformer['transformlink'].append(float(t))

            deformers.append(deformer)

        return deformers

    def _get_mesh_lines(self, lines):
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

        return mesh_lines

    def _unroll_mesh(self, defornodes, mesh):

        uvsUnrolled         = []
        pointsUnrolled      = []


        mesh['points_3d'] = [] #list of tuple for x,y,z
        mesh['uv_2d'] = [] #list of tuple for x,y

        counter = 0
        while counter < len(mesh['points']):
            point = (mesh['points'][counter],mesh['points'][counter+1],mesh['points'][counter+2])
            mesh['points_3d'].append(point)

            counter+=3

        counter = 0
        while counter < len(mesh['uv']):
            point = (mesh['uv'][counter],mesh['uv'][counter+1])
            mesh['uv_2d'].append(point)
            counter+=2

        for i in range(0, len(mesh['pointsi'])):
            Entry = mesh['points_3d'][mesh['pointsi'][i]]
            pointsUnrolled.append(Entry)

        for i in range(0, len(mesh['uvi'])):
            Entry = mesh['uv_2d'][mesh['uvi'][i]]
            uvsUnrolled.append(Entry)

        weightsUnrolled=  [ [] for a in mesh['points_3d']]
        indexesUnrolled=  [ [] for a in mesh['points_3d']]

        for x in defornodes:
            for y in range(0, len(x['weights'])):
                current_weight = x['weights'][y]
                current_index = x['indexes'][y]
                if current_weight > 0.05 and \
                len(indexesUnrolled[current_index]) < 4 and \
                len(weightsUnrolled[current_index]) < 4:
                    weightsUnrolled[current_index].append(current_weight)
                    indexesUnrolled[current_index].append(current_index)

        mesh['points_unrolled'] = pointsUnrolled
        mesh['uv_unrolled']     = uvsUnrolled
        mesh['index_unrolled']  = indexesUnrolled
        mesh['weight_unrolled'] = weightsUnrolled

    def _convert_auto(self, arguments):
        '''
        Lets try parsing different modes and check the outcome, then we will decide on
        the result to keep
        :param lines:
        :return:
        '''
        start = time.time()
        lines = self._open_file(arguments.path_in, arguments.filename_in)

        meshWorks = False
        try:
            meshLines           = self._get_mesh_lines(lines)
            matFilename         = self._getmaterialname(lines)
            meshDict            = self._get_mesh_data(meshLines)
            meshName            = self._get_mesh_name(meshLines)

            meshWorks = True
        except:
            pass

        skinnedWorks = False
        try:

            stringPoseNodes     = self._get_bindpose_lines(lines)
            poseNodesDict       = self._create_posenodes(stringPoseNodes)

            stringDeforNodes    = self._get_deformernodes(lines)
            deformerNodes       = self._parse_deformers(stringDeforNodes)

            self._unroll_mesh(deformerNodes, meshDict)

            connectionsDict     = self._get_connections(lines)
            if any(deformerNodes) and any(poseNodesDict) and any(connectionsDict):
                skinnedWorks = True
            else:
                skinnedWorks = False
        except:
            pass

        animWorks = False

        try:
            animation_take = self._parse_take(lines)
            if not any(animation_take):
                animWorks = False
            else:
                animWorks = True
        except:
            pass

        if animWorks:
            out_dict = {'name': None,'animation': None,}
            out_dict['animation'] = animation_take

            import json
            self._write_file(json.dumps(out_dict, indent=4), arguments.path_out, arguments.filename_out + '.anim')

        if meshWorks:
            out_dict = { 'name': None, 'materialfile': None,'mesh': None}
            out_dict['mesh'] = meshDict
            out_dict['name'] = meshName
            out_dict['materialfile'] = matFilename

            import json
            self._write_file(json.dumps(out_dict, indent=4), arguments.path_out, arguments.filename_out + '.mesh')

        if skinnedWorks:
            out_dict = {'name' : None, 'mesh': None, 'materialfile': None, 'deformers': None, 'posenodes': None, 'connections': None}
            out_dict['mesh'] = meshDict
            out_dict['name'] = meshName
            out_dict['deformers'] = deformerNodes
            out_dict['posenodes'] = poseNodesDict
            out_dict['connections'] = connectionsDict
            out_dict['materialfile'] = matFilename
            import json
            self._write_file(json.dumps(out_dict, indent=4), arguments.path_out, arguments.filename_out + '.mesh')

        print(meshDict)
        end = time.time()
        print("Done Converting file: Time Taken: {}".format(end - start))

    def _open_file(self, path, filename) -> list():
        '''
        Open the FBX file
        :param path: file path
        :param filename: file name
        :return:
        '''

        start = time.time()

        #add the .fbx if it isnt in the name
        if not '.fbx' in filename:
            filename = "{}{}".format(filename, '.fbx')

        pathname = os.path.join(path,filename)

        with open(pathname, 'r') as fin:
            file_lines = fin.readlines()

        end = time.time()

        return file_lines

    def _write_file(self, data, path, filename) -> list():
        '''
        Write a File
        :param path: file path
        :param filename: file name
        :return:
        '''

        start = time.time()

        #add the .fbx if it isnt in the name
        if not '.fbx' in filename:
            filename = "{}".format(filename)

        pathname = os.path.join(path,filename)

        with open(pathname, 'w') as fout:
            fout.write(data)
        end = time.time()

if __name__ == '__main__':

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

    fbxparser = FbxParser()
    results = parser.parse_args()
    fbxparser.convert(results)

