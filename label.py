# coding=gbk  
import numpy as np
import igl
import os
import openmesh as om
import polyscope as ps


def modify_labels(file_path):
    
    import copy
    import glob
    if not os.path.exists(file_path) or not file_path.endswith(".obj"):
        print(f"�ļ� '{file_path}' �����ڻ���.obj�ļ�")
        return
     
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    print(f"���ļ���{file_path}")
    color_mapping = np.array([
                                [0, 0.03, 0.04],  # ��ɫ 0  +x 
                                [255, 255, 255], # ��ɫ 1  -x
                                [255, 0, 0],  # ��ɫ  2 +y
                                [255, 255, 0],  # ��ɫ 3 -y
                                [0, 255, 0],  # ��ɫ 4 +z
                                [0, 0, 255],  # ��ɫ 5 -z
                                [128, 0, 128],  # ��ɫ 6
                                [255, 165, 0],  # ��ɫ 7
                                [0, 128, 128],  # ��ɫ 8
                            ])

    label_pattern = os.path.splitext(file_path)[0] + "_Tri_labeling*.txt"
    mesh = om.read_trimesh(file_path)
    vertices = mesh.points()
    faces = mesh.fv_indices()
    vertex_face_indices = mesh.vf_indices()
    face_adjacency = mesh.ff_indices()
    
    # �ı���ı�ǩ�İ�ť            
    axes = ["x","-x","y","-y","z","-z", "custom1", "custom2", "custom3"]
    colors = ["black","white","red","yellow","green","blue", "purple", "orange", "cyan"]
    label_files = None       # ���б�ǩ�ļ���
    label_data = []   # ���б�ǩ�ļ���ı�ǩ
    selected_label_index = 0               # ѡ���˵ڼ���label�ļ����иı�
    is_edit_mode = False       # ��ѡ��ѡ����ܸı�label
    new_label_value = None         # ��Ҫ�ı�Ϊ��labelֵ
    modified_faces = []          # ��¼���θı�����Щ��id
    updated_labels = None        # ���������labelֵ
    n = None
    k_neighborhood = 0
    

    def get_k_neighborhood(k, face_id):
        if k == 2:
            arr = vertex_face_indices[faces[face_id]]
            return np.unique(arr[arr != -1])
        result = [face_id]
        for _ in range(k):
            result = result + np.concatenate(face_adjacency[result]).tolist()  # ʹ��np.concatenate��չƽ
        return np.unique(result)

    def update_labels():
        nonlocal new_label_value, updated_labels, n, label_files, label_data, selected_label_index, is_edit_mode, modified_faces, vertices, faces, k_neighborhood, dir_path
        for i, axis in enumerate(axes):
            if ps.imgui.Button(f"{colors[i]} : {axis} --- {i}") :
                new_label_value = i
        # ��ѡ��ѡ����ܸı�label                  
        _, is_edit_mode = ps.imgui.Checkbox("edit_mode:  Tick the box and press the letter key C", is_edit_mode)

        # ��ǰ�ı�ǩ�ļ� 
        changed, selected_label_index = ps.imgui.SliderInt("selected_label_index", selected_label_index, v_min=0, v_max=len(label_files)-1)
        if changed:
            print(f"��ǰ�ı�label��txtΪ: {label_files[selected_label_index]}")
            ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(selected_label_index)  +"---"+ label_files[selected_label_index], color_mapping[label_data[selected_label_index]], defined_on='faces',enabled=True)
            print("���¶�ȡtxtlabel���϶�������ǰ���ȱ������")
            updated_labels = copy.deepcopy(label_data[selected_label_index])
            modified_faces = []

        # ѡ��������� 
        _, k_neighborhood = ps.imgui.SliderInt("k_neighborhood of face", k_neighborhood, v_min=0, v_max=10)
        
        if ( ps.imgui.IsKeyPressed(ps.get_key_code('c')) or ps.imgui.IsKeyPressed(ps.get_key_code('C'))) and new_label_value is not None and is_edit_mode == True:
            world_pos = ps.screen_coords_to_world_position(ps.imgui.GetMousePos())
            if any(x != float('inf') for x in world_pos) :
                _, face_idx, _ = igl.point_mesh_squared_distance(np.array(world_pos), vertices, faces)
                if k_neighborhood !=0:
                    face_idx = get_k_neighborhood(k_neighborhood, face_idx)
                if updated_labels is None:
                    updated_labels = copy.deepcopy(label_data[selected_label_index])
                updated_labels[face_idx] = new_label_value
                modified_faces.append(face_idx.tolist())

                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(selected_label_index)  +"---"+ label_files[selected_label_index], color_mapping[updated_labels], defined_on='faces',enabled=True)

        # ����
        if ps.imgui.Button("save_in_current_txt"):
            np.savetxt(dir_path + "/"+ label_files[selected_label_index], updated_labels, fmt='%d')
            print(f"����ɹ�: {label_files[selected_label_index]}")
            label_data[selected_label_index] = updated_labels
        if ps.imgui.Button("save_in_custom"):
            mesh_name = file_name.split(".")[0]
            np.savetxt(dir_path + "/"+  mesh_name+ "_Tri_labeling_Custom.txt", updated_labels, fmt='%d')
            print(f"����ɹ�: {file_name}_Tri_labeling.txt")

            if mesh_name+ "_Tri_labeling_Custom.txt" not in label_files:
                print(label_files)
                label_files.append(mesh_name+ "_Tri_labeling_Custom.txt")
                label_data.append(updated_labels)
                print(f"����µ�label�ļ�: {mesh_name+ '_Tri_labeling_Custom.txt'}")
                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(len(label_files)-1)  +"---"+ mesh_name+ "_Tri_labeling_Custom.txt", color_mapping[updated_labels], defined_on='faces')
            else:
                index = label_files.index(mesh_name+ "_Tri_labeling_Custom.txt")
                label_data[index] = updated_labels
                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(index)  +"---"+ mesh_name+ "_Tri_labeling_Custom.txt", color_mapping[updated_labels], defined_on='faces')

        # ���˻���
        if ps.imgui.Button("undo_label:  Or press the letter key B") or ps.imgui.IsKeyPressed(ps.get_key_code('b')) or  ps.imgui.IsKeyPressed(ps.get_key_code('B')) and  updated_labels is not None and len(modified_faces) > 0 :
            face_id = modified_faces[-1]
            updated_labels[face_id] = label_data[selected_label_index][face_id]
            modified_faces.pop()
            ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(selected_label_index)  +"---"+ label_files[selected_label_index], color_mapping[updated_labels], defined_on='faces',enabled=True)

    ps.init()
    ps.set_navigation_style("free")
    ps.set_ground_plane_mode("none")

    ps.register_surface_mesh(file_name + "-Tri", vertices, faces, edge_width=1.6)
    ps.reset_camera_to_home_view()
    # �������з����������ļ�����ȡ����·�����ļ����Ͷ�Ӧ·��
    label_files = [os.path.basename(f) for f in glob.glob(label_pattern) ]
    print(f"�ҵ���label�ļ�: {label_files}")

    for i, label_file in enumerate(label_files):
            labels = np.loadtxt(dir_path + "/"+ label_file, dtype=int)
            if  mesh.n_faces() != labels.shape[0]:
                print(f"ע�⣡:txt����ı�ǩ���������������ƥ�� '{label_file}'")
                print("�������Ϊ", mesh.n_faces)
                print("labels������Ϊ", labels.shape[0])
                label_files.pop(i)
            else :
                label_data.append(labels)

    if label_files:
        for i, label_file in enumerate(label_files):
            if label_file.endswith("_Tri_labeling.txt"):
                selected_label_index = i
                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(
                str(i) +"---"+label_file, color_mapping[label_data[i]], defined_on='faces',enabled=True)
                updated_labels = copy.deepcopy(label_data[i])
            else:
                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(
                        str(i)  +"---"+ label_file, color_mapping[label_data[i]], defined_on='faces')
                if updated_labels is None:
                    print(f"ע�⣡:txt����û��_Tri_labeling.txt '{label_pattern}'")
        ps.set_user_callback(update_labels)
    else:
        print(f"δ�ҵ�ƥ��� label �ļ���ģʽ: '{label_pattern}'")
        ps.get_surface_mesh(file_name + "-Tri").set_edge_width(1)

    ps.show()
    ps.remove_all_structures()
    ps.clear_user_callback()


def modify_labels_in_directory(base_path):
    '''���ζ�ȡ����·�������ÿ������������ͱ�ǩ,Ȼ�󽻻��ı��ǩ��ɫ'''
    file_list = os.listdir(base_path)
    for file_name in file_list:
        if file_name.endswith(".obj"):
            modify_labels(os.path.join(base_path, file_name))
            print(f"�����: {file_name}")

if __name__ == "__main__":
    # ָ��·��
    input_path = r"D:\polycube_data"

    # ���·�����ļ�����Ŀ¼
    if os.path.isfile(input_path) and input_path.endswith(".obj"):
        modify_labels(input_path)
    elif os.path.isdir(input_path):
        modify_labels_in_directory(input_path)
    else:
        print(f"·����Ч: {input_path}")