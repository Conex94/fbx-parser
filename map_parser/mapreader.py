#!/usr/bin/env python

#

'''
This python FBX importer works for
the FBX-ASCII format of Version 6.1.0 from 2006
'''

import os
from sys import argv

class FBX_MAP_READER:
    '''
    This parser will be used to read maps out of fbx files
    '''

    @staticmethod
    def read_file(filepath : str):
        '''
        Reads the lines of the fbx file
        :param filepath:
        :return: fbx-file-lines
        '''
        if os.path.isfile(filepath):
            print("Reading fbx file: {}".format(filepath))
            with open(filepath, 'r') as fin:
                fbx_data = fin.readlines()

            for i in range(0,fbx_data.__len__()):
                fbx_data[i] = fbx_data[i].strip().replace('\n','')
        else:
            print("Failed to open file: {}".format(filepath))
            raise FileNotFoundError()

        return fbx_data

    @staticmethod
    def get_fbx_scope(fbx_lines: str, scope_indicator : str):
        '''
        Extract the header scope from fbx lines
        :param fbx-lines
        return headerlines'''

        if not any(fbx_lines):
            raise ValueError('No fbx-lines available, cannot get scope for {}'.format(scope_indicator))

        newlines = list()
        bracket_counter = 0
        scopeopen = False

        for i in range(0, fbx_lines.__len__() - 1):
            if "{}:  {".format(scope_indicator) in fbx_lines[i]:
                bracket_counter += 1
                scopeopen = True
            elif "}" in fbx_lines[i] and scopeopen is True:
                bracket_counter -= 1
            elif "{" in fbx_lines[i] and scopeopen is True:
                bracket_counter += 1

            if bracket_counter > 0 and scopeopen:
                newlines.append(fbx_lines[i])

            if bracket_counter < 1 and scopeopen:
                scopeopen = False

        return newlines[1:-1]

    @staticmethod
    def get_fbxheaderlines(fbx_lines : str):
        '''
        Extract the header scope from fbx lines
        :param fbx-lines
        return headerlines'''

        if not any(fbx_lines):
            raise ValueError('No fbx-lines available, cannot get Header lines')

        newlines = list()
        bracket_counter = 0
        scopeopen = False

        for i in range(0,fbx_lines.__len__()-1):

            if "FBXHeaderExtension:  {" in fbx_lines[i]:
                    bracket_counter += 1
                    scopeopen = True
            elif "}" in fbx_lines[i] and scopeopen is True:
                bracket_counter -= 1
            elif "{" in fbx_lines[i] and scopeopen is True:
                bracket_counter += 1

            if bracket_counter > 0 and scopeopen:
                newlines.append(fbx_lines[i])

            if bracket_counter < 1 and scopeopen:
                scopeopen = False

        return newlines[1:-1]

    @staticmethod
    def get_fbxdefinitionlines(fbx_lines : str):
        if not any(fbx_lines):
            raise ValueError('No fbx-lines available, cannot get Definitions')

        newlines = list()
        bracket_counter = 0
        scopeopen = False

        for i in range(0, fbx_lines.__len__() - 1):
            if "Definitions:  {" in fbx_lines[i]:
                bracket_counter += 1
                scopeopen = True
            elif "}" in fbx_lines[i] and scopeopen is True:
                bracket_counter -= 1
            elif "{" in fbx_lines[i] and scopeopen is True:
                bracket_counter += 1
            if bracket_counter > 0 and scopeopen:
                newlines.append(fbx_lines[i])
            if bracket_counter < 1 and scopeopen:
                scopeopen = False
        return newlines[1:-1]

    @staticmethod
    def get_fbxobjectslines(fbx_data):
        try:
            fbx_object_lines = list()
            newlines = list()
            bracket_counter = 0
            scopeopen = False
            for i in range(0, fbx_data.__len__() - 1):

                if "Objects:  {" in fbx_data[i]:
                    bracket_counter += 1
                    scopeopen = True

                elif "}" in fbx_data[i] and scopeopen is True:
                    bracket_counter -= 1
                elif "{" in fbx_data[i] and scopeopen is True:
                    bracket_counter += 1
                else:
                    pass

                if bracket_counter > 0 and scopeopen:
                    newlines.append(fbx_data[i])

                if bracket_counter < 1 and scopeopen:
                    scopeopen = False

            fbx_object_lines = newlines[1:-1]
            return fbx_object_lines
        except Exception as e:
            print('Failed to get Objects')
            raise e

    @staticmethod
    def get_fbxrelationslines(fbx_data):
        try:
            newlines = list()
            bracket_counter = 0
            scopeopen = False

            for i in range(0, fbx_data.__len__() - 1):
                if "Relations:  {" in fbx_data[i]:
                    bracket_counter += 1
                    scopeopen = True

                elif "}" in fbx_data[i] and scopeopen is True:
                    bracket_counter -= 1
                elif "{" in fbx_data[i] and scopeopen is True:
                    bracket_counter += 1
                else:
                    pass

                if bracket_counter > 0 and scopeopen:
                    newlines.append(fbx_data[i])

                if bracket_counter < 1 and scopeopen:
                    scopeopen = False

            return newlines[1:-1]

        except Exception as e:
            print('Failed to get Objects')
            raise e

    @staticmethod
    def get_fbxconnectionslines(fbx_data : list):
        try:
            newlines = list()
            bracket_counter = 0
            scopeopen = False
            for i in range(0, fbx_data.__len__() - 1):

                if "Connections:  {" in fbx_data[i]:
                    bracket_counter += 1
                    scopeopen = True

                elif "}" in fbx_data[i] and scopeopen is True:
                    bracket_counter -= 1
                elif "{" in fbx_data[i] and scopeopen is True:
                    bracket_counter += 1
                else:
                    pass

                if bracket_counter > 0 and scopeopen:
                    newlines.append(fbx_data[i])

                if bracket_counter < 1 and scopeopen:
                    scopeopen = False

            return newlines[1:-1]

        except Exception as e:
            print('Failed to get Objects')
            raise e

    @staticmethod
    def get_fbxmateriallines(fbx_data : list):
        try:
            newlines = list()
            bracket_counter = 0
            scopeopen = False
            for i in range(0, fbx_data.__len__() - 1):
                if "Material: " in fbx_data[i] and not "LayerElementMaterial" in fbx_data[i]:
                    bracket_counter += 1
                    scopeopen = True

                elif "}" in fbx_data[i] and scopeopen is True:
                    bracket_counter -= 1
                elif "{" in fbx_data[i] and scopeopen is True:
                    bracket_counter += 1
                else:
                    pass

                if bracket_counter > 0 and scopeopen:
                    newlines.append(fbx_data[i])

                if bracket_counter < 1 and scopeopen:
                    scopeopen = False

            return newlines

        except Exception as e:
            print('Failed to get Objects')
            raise e

    @staticmethod
    def seperate_materials(obj_scopes: list):

        materials_dict = dict()
        for obj in obj_scopes:
            if "Material: " in obj[0]:
                name = obj[0].split(',')[0].split(' ')[1].replace('\"', '')
                for line in obj:
                    if "ShadingModel: " in line:
                        shading_model = line.split(' ')[1].replace('\"', '')

                shading_dict = { 'shading_model' : shading_model}
                materials_dict.update({ name : shading_dict})

            if "Video: " in obj[0]:
                name = obj[0].split(' ')[1].split(',')[0].replace('\"', '')
                for line in obj:
                    if "RelativeFilename: " in line:
                        filename = line.split(' ')[1].replace('\"','')

                video_dict = {'relative_filename': filename}
                materials_dict.update({name: video_dict})

            if "Texture: " in obj[0]:
                name = obj[0].split(' ')[1].split(',')[0].replace('\"', '')
                for line in obj:
                    if "TextureName: " in line:
                        tex_name = line.split(' ')[1].replace('\"', '')

                tex_dict = {'filename': tex_name}
                materials_dict.update( {name: tex_dict})

        return materials_dict

    @staticmethod
    def seperate_fbx_objects(fbx_object_lines : list):
        fbx_objects_line_scoped = list()
        brackets = 0
        scope_list = list()

        for i in range(0,fbx_object_lines.__len__()):
            if "{" in fbx_object_lines[i]:
                brackets += 1
            if "}" in fbx_object_lines[i]:
                brackets -= 1

            scope_list.append(fbx_object_lines[i])

            if brackets == 0:
                fbx_objects_line_scoped.append(scope_list)
                scope_list = list()

        return fbx_objects_line_scoped

    @staticmethod
    def dissect_fbx_object_list(fbx_objects_line_scoped):

        dict_of_finished_fbx_objects = dict()

        for i in fbx_objects_line_scoped:
            #only model objects now
            if not "Camera" in i[0] and 'Model: ' in i[0]:

                returned_obj = FBX_MAP_READER.create_fbx_object_from_object_scope(i)
                dict_of_finished_fbx_objects.update( { returned_obj['name'] : returned_obj })

        return dict_of_finished_fbx_objects

    @staticmethod
    def create_fbx_object_from_object_scope(fbx_object_single):
        '''
        :param fbx_object_single:
        :return:
        '''
        scopes = list()
        tempscopes = list()
        brackets = 0
        fill_scopes = False
        unscoped_lines = list()

        for i in range(1,fbx_object_single.__len__()-1):
            ln = fbx_object_single[i]
            if "{" in ln and ( "Properties60"           in ln or
                               "LayerElementNormal"     in ln or
                               "LayerElementUV"         in ln or
                               "LayerElementSmoothing"  in ln or
                               "LayerElementMaterial"   in ln or
                               "LayerElementTexture"    in ln):
                fill_scopes = True
                brackets += 1
            if "}" in fbx_object_single[i]:
                brackets -= 1

            if fill_scopes:
                tempscopes.append(fbx_object_single[i])
            else:
                unscoped_lines.append(fbx_object_single[i])

            if brackets == 0:
                if any(tempscopes):
                    scopes.append(tempscopes)
                    tempscopes = list()
                fill_scopes = False

        #construct the object here and get all relevant data out of it.
        finished_fbx_data = FBX_MAP_READER.extract_object_data_from_lines(fbx_object_single[0], scopes, unscoped_lines)

        return finished_fbx_data

    @staticmethod
    def create_connection_dict(connection_lines):
        '''
        :param fbx_object_single:
        :return:
        '''
        connections = list()
        ret_dict = dict()

        for i in range(1,connection_lines.__len__()-1):
            ln = connection_lines[i]

            line_split = ln.strip().replace('\"', ''). \
                replace('Model::', ''). \
                replace('Material::', ''). \
                replace('Texture::', ''). \
                replace('Video::', '').split(',')

            child = line_split[1].strip()
            parent = line_split[2].strip()
            d = { 'child' : child, 'parent' : parent}

            connections.append(d)

        ret_dict.update({'connections' : connections})

        return ret_dict

    @staticmethod
    def extract_object_data_from_lines(first_line = str(), subscopes = list(), unscoped_lines = list()):
        fbx_model_object = dict()
        doname = True
        dopoints = True
        donormal = True
        douv = True

        if doname:
            #get the name of object
            name = first_line.strip().split(' ')[1].replace(',',' ').replace('\'',' ')
            name = name.replace('\"',' ').strip().replace('Model::','')
            fbx_model_object.update( {'name': name} )

        if dopoints:
            #get points
            start_read_verts = False
            start_read_vert_index = False
            start_read_verts = False
            vertlines = list()
            vertindices = list()
            for l in unscoped_lines:
                if 'Vertices:' in l:
                    start_read_verts = True
                    vertlines.append(l)
                    continue

                if 'PolygonVertexIndex: ' in l:
                    start_read_verts = False
                    start_read_vert_index = True
                    vertindices.append(l.replace('\n','').strip())
                    continue

                if 'GeometryVersion: ' in l or 'Edges: ' in l:
                    break

                if start_read_verts:
                    vertlines.append(l.replace('\n','').strip())

                if start_read_vert_index:
                    vertindices.append(l.replace('\n','').strip())

            verts_string_list = ''.join(vertlines).strip().replace('Vertices: ', '').replace('\n','').replace('\r','').replace('\t','').split(',')
            vert_index_string_list = ''.join(vertindices).strip().replace('PolygonVertexIndex: ', '').replace('\n','').replace('\r','').replace('\t','').split(',')


            #get the point and uv data
            point_list = list() #list of Vector3
            point_index_list = list() #list of ints
            point_list_unrolled = list() #unrolled list of points

            #FOR NOW, ONLY TRIANGLE MESH ALLOWED!

            i = 0
            while i < verts_string_list.__len__():
                val0 = float(verts_string_list[i+0].strip())
                val1 = float(verts_string_list[i+1].strip())
                val2 = float(verts_string_list[i+2].strip())

                point = dict()
                point.update( { 'x' : val0 })
                point.update( { 'y' : val1 })
                point.update( { 'z' : val2 })

                point_list.append(point)
                i+= 3

            for x in vert_index_string_list:
                index = int(x)
                point_index_list.append(index)
                if index < 0:
                    index *= -1
                    index -= 1

                point_list_unrolled.append(point_list[index])

            fbx_model_object.update({'indices': point_index_list})
            fbx_model_object.update({'points': point_list})
            fbx_model_object.update({'indexed_points': point_list_unrolled})

        if donormal:
            normal_layers = dict()

            for scope in subscopes:
                if 'LayerElementNormal: ' in scope[0]:
                    layer_number = int(scope[0].split(' ')[1].strip())
                    normal_scope = scope

                    single_layer_key = "normal_layer_{}".format(layer_number)
                    single_layer_value = FBX_MAP_READER.parse_normal_sub_scope(normal_scope)
                    normal_layers.update({ single_layer_key : single_layer_value })

        if douv:
            uv_layers = dict()

            for scope in subscopes:
                if 'LayerElementUV: ' in scope[0]:
                    layer_number = int(scope[0].split(' ')[1].strip())
                    uv_scope = scope


                    single_layer_key = "uv_layer_{}".format(layer_number)
                    single_layer_value =  FBX_MAP_READER.parse_uv_sub_scope(uv_scope)
                    uv_layers.update( { single_layer_key: single_layer_value})

        fbx_model_object.update({ 'uv_layers' : uv_layers} )
        fbx_model_object.update({ 'normal_layers' : normal_layers } )

        return fbx_model_object

    @staticmethod
    def parse_normal_sub_scope(normal_scope : list()):
        read_normal_lines = False
        normal_lines = list()
        normals = list()

        for line in normal_scope:
            line = line.strip().replace('\n', '').replace('\t', '')
            if 'MappingInformationType' in line:
                mapping_type = line.split(' ')[1].replace(':', '').replace('\"', '')

            if 'ReferenceInformationType' in line:
                reference_type = line.split(' ')[1].replace(':', '').replace('\"', '')

            if "Normals" in line:
                read_normal_lines = True

            if "}" in line and read_normal_lines:
                read_normal_lines = False
                normals_string = ''.join(normal_lines).replace('Normals: ', '').replace('\n', '', ).replace(' ', '')
                normals_string_array = normals_string.split(',')

                for i in range(0, len(normals_string_array), 3):
                    point_vec = dict()

                    point_vec.update({'x': float(normals_string_array[i])})
                    point_vec.update({'y': float(normals_string_array[i + 1])})
                    point_vec.update({'z': float(normals_string_array[i + 2])})

                    normals.append(point_vec)

            if read_normal_lines:
                normal_lines.append(line)

        return normals

    @staticmethod
    def parse_uv_sub_scope(uv_scope : list()):
        read_uv_lines = False
        uv_lines = list()
        uvs = list()

        read_uvi_lines = False
        uvi_lines = list()
        uvis = list()

        uvi_layer_obj = dict()

        for line in uv_scope:
            line = line.strip().replace('\n', '').replace('\t', '')
            if 'MappingInformationType' in line:
                mapping_type = line.split(' ')[1].replace(':', '').replace('\"', '')
            if 'Name: ' in line:
                name = line.split(' ')[1].replace('\"', '')

            if 'ReferenceInformationType' in line:
                reference_type = line.split(' ')[1].replace(':', '').replace('\"', '')

            if line.startswith("UV: "):
                read_uv_lines = True

            if line.startswith("UVIndex: "):
                read_uvi_lines = True

            if "UVIndex:" in line and read_uv_lines:
                read_uv_lines = False
                uvs_string = ''.join(uv_lines).replace('UV: ', '').replace('\n', '', ).replace(' ', '')
                uvs_string_array = uvs_string.split(',')

                for i in range(0, len(uvs_string_array), 2):
                    point_vec = dict()
                    point_vec.update({'x': float(uvs_string_array[i + 0]) })
                    point_vec.update({'y': float(uvs_string_array[i + 1]) })

                    uvs.append( point_vec )

            if "}" in line and read_uvi_lines:
                read_uvi_lines = False
                uvis_string = ''.join(uvi_lines).replace('UVIndex: ', '').replace('\n', '', ).replace(' ', '')
                uvis_string_array = uvis_string.split(',')

                for i in range(0, len(uvis_string_array), 1):
                    uvis.append(int(uvis_string_array[i]))

            if read_uv_lines: uv_lines.append(line)
            if read_uvi_lines: uvi_lines.append(line)

        uvi_layer_obj.update( { 'name' : name})
        uvi_layer_obj.update( { 'uv' : uvs})
        uvi_layer_obj.update( { 'uv_index' : uvis})

        return uvi_layer_obj

    @staticmethod
    def dict_to_lines(data):
        lines =list()

        for k in data:
            lines.append("<{}>".format(k.upper()))

            if 'connections' in k:
                for l in data[k]:
                    lines.append("<RELATION>".format(k.upper()))
                    lines.append('parent: ' + l['parent'])
                    lines.append('child: ' + l['child'])
                    lines.append("</RELATION>".format(k.upper()))

            if 'objects' in k:
                for l in data[k]:
                    lines.append('<MESH>')
                    mesh = data[k][l]
                    for keys in mesh:
                        if 'name' in keys:
                            lines.append('name: {}'.format(mesh[keys]))
                        if 'indices' in keys:
                            b = [str(x) for x in mesh[keys]]
                            lines.append('indices: {}'.format(','.join(b )))
                        if 'points' in keys and not 'index' in keys:
                            string_points_list = list()
                            for vertex in  mesh[keys]:
                                string_points_list.append(vertex['x'])
                                string_points_list.append(vertex['y'])
                                string_points_list.append(vertex['z'])
                            str_pts_new = [str(x) for x in string_points_list]
                            lines.append('points: {}'.format(','.join(str_pts_new)))

                        if 'indexed_points' in keys:
                            string_points_list = list()
                            for vertex in  mesh[keys]:
                                string_points_list.append(vertex['x'])
                                string_points_list.append(vertex['y'])
                                string_points_list.append(vertex['z'])
                            str_pts_new = [str(x) for x in string_points_list]
                            lines.append('indexed: {}'.format(','.join(str_pts_new)))

                        if 'uv_layers' in keys:
                            lines.append("<UVLAYERS>")
                            uv_layers = mesh[keys]
                            for layer in uv_layers:
                                lines.append("<LAYER>")
                                for uv_vert in uv_layers[layer]:

                                    if  'uv' in uv_vert and not 'index' in uv_vert:
                                        uv_verts = list()
                                        for uv_vert in uv_layers[layer][uv_vert]:
                                            uv_verts.append(str(uv_vert['x']))
                                            uv_verts.append(str(uv_vert['y']))

                                        lines.append('uv: {}'.format(','.join(uv_verts)))

                                    if  'name' in uv_vert:
                                        thename =  uv_layers[layer][uv_vert]
                                        lines.append('name: {}'.format(thename))
                                    if  'uv_index' in uv_vert :
                                        uv_verts = list()
                                        for uv_vert in uv_layers[layer][uv_vert]:
                                            uv_verts.append(str(uv_vert))

                                        lines.append('uv_index: {}'.format(','.join(uv_verts)))

                                lines.append("</LAYER>")

                            lines.append("<UVLAYERS>")

                            print(keys)
                            pass


                    lines.append('</MESH>')
            if 'materials' in k:
                for l in data[k]:
                    if 'Material::' in l:
                        lines.append('<MATSCOPE>')
                        lines.append('mattype: material')
                        lines.append("name: " + l)
                        lines.append("shading: {}".format(data[k][l]['shading_model'] ) )
                        lines.append('</MATSCOPE>')

                    if 'Texture::' in l:
                        lines.append('<MATSCOPE>')
                        lines.append('mattype: texture')
                        lines.append("name: " + l)
                        lines.append("filename: {}".format(data[k][l]['filename'] ) )
                        lines.append('</MATSCOPE>')

                    if 'Video::' in l:
                        lines.append('<MATSCOPE>')
                        lines.append('mattype: texture')
                        lines.append("name: " + l)
                        lines.append("relative_filename: {}".format(data[k][l]['relative_filename'] ) )
                        lines.append('</MATSCOPE>')

            lines.append("</{}>".format(k.upper()))

        return lines

    @staticmethod
    def run_map_parser(arguments):
        args_dict = dict()

        if len(arguments) < 2:
            arguments.clear()
            arguments.append('-if')
            arguments.append('shadowtest.fbx')

        for i in range(0, len(arguments), 2):
            if '-if' in arguments[i+0]:
                keystr = arguments[i+0]
                args_dict.update({keystr: arguments[i+1]})
            else:
                print('Missing argument: -if')
                print('Arguments are: {}'.format(args_dict))
                exit(1)

        print(args_dict)

        filenamein = args_dict['-if']
        filenameout = filenamein.split('.')[0]

        fbx_file_scopes_as_string = dict()

        #get all lines from file
        fbx_data            = FBX_MAP_READER.read_file(filenamein)

        #get fbx Objects as scopes
        object_lines        = FBX_MAP_READER.get_fbxobjectslines(fbx_data)
        objects_lines_scoped = FBX_MAP_READER.seperate_fbx_objects(object_lines)

        #get the lines of the header
        header_lines        = FBX_MAP_READER.get_fbxheaderlines(fbx_data)

        #get definition lines
        definiton_lines     = FBX_MAP_READER.get_fbxdefinitionlines(fbx_data)

        #get object lines and create objects in dict format
        finished_fbx_meshes   = FBX_MAP_READER.dissect_fbx_object_list(objects_lines_scoped)

        #get relation lines and create list of relation dicts
        relation_lines      = FBX_MAP_READER.get_fbxrelationslines(fbx_data)

        #get connections and create dict
        connection_lines    = FBX_MAP_READER.get_fbxconnectionslines(fbx_data)
        connections_dict    = FBX_MAP_READER.create_connection_dict(connection_lines)

        materials_dict   = FBX_MAP_READER.seperate_materials(objects_lines_scoped)

        #FBX_MAP_READER.seperate_fbx_objects()

        out_dict = dict()
        out_dict.update(connections_dict)
        out_dict.update({'objects': finished_fbx_meshes})
        out_dict.update({'materials': materials_dict})

        lines = FBX_MAP_READER.dict_to_lines(out_dict)

        for i in range(0, len(lines)):
            lines[i] += "\n"

        with open(filenameout + ".json", 'w') as d:
            import json
            d.write(json.dumps(out_dict, indent=4))

        with open(filenameout + ".custom", 'w') as d:
            d.writelines(lines)

if __name__ == '__main__':
    arguments = list(argv[1:])

    if len(arguments) % 2 == 0:
        FBX_MAP_READER.run_map_parser(arguments)
