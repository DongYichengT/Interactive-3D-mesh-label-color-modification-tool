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
        print(f"文件 '{file_path}' 不存在或不是.obj文件")
        return
     
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    print(f"打开文件：{file_path}")
    color_mapping = np.array([
                                [0, 0.03, 0.04],  # 黑色 0  +x 
                                [255, 255, 255], # 白色 1  -x
                                [255, 0, 0],  # 红色  2 +y
                                [255, 255, 0],  # 黄色 3 -y
                                [0, 255, 0],  # 绿色 4 +z
                                [0, 0, 255],  # 蓝色 5 -z
                                [128, 0, 128],  # 紫色 6
                                [255, 165, 0],  # 橙色 7
                                [0, 128, 128],  # 青色 8
                            ])

    label_pattern = os.path.splitext(file_path)[0] + "_Tri_labeling*.txt"
    mesh = om.read_trimesh(file_path)
    vertices = mesh.points()
    faces = mesh.fv_indices()
    vertex_face_indices = mesh.vf_indices()
    face_adjacency = mesh.ff_indices()
    
    # 改变面的标签的按钮            
    axes = ["x","-x","y","-y","z","-z", "custom1", "custom2", "custom3"]
    colors = ["black","white","red","yellow","green","blue", "purple", "orange", "cyan"]
    label_files = None       # 所有标签文件名
    label_data = []   # 所有标签文件里的标签
    selected_label_index = 0               # 选择了第几个label文件进行改变
    is_edit_mode = False       # 勾选该选项才能改变label
    new_label_value = None         # 需要改变为的label值
    modified_faces = []          # 记录依次改变了哪些面id
    updated_labels = None        # 所有面的新label值
    n = None
    k_neighborhood = 0
    

    def get_k_neighborhood(k, face_id):
        if k == 2:
            arr = vertex_face_indices[faces[face_id]]
            return np.unique(arr[arr != -1])
        result = [face_id]
        for _ in range(k):
            result = result + np.concatenate(face_adjacency[result]).tolist()  # 使用np.concatenate来展平
        return np.unique(result)

    def update_labels():
        nonlocal new_label_value, updated_labels, n, label_files, label_data, selected_label_index, is_edit_mode, modified_faces, vertices, faces, k_neighborhood, dir_path
        for i, axis in enumerate(axes):
            if ps.imgui.Button(f"{colors[i]} : {axis} --- {i}") :
                new_label_value = i
        # 勾选该选项才能改变label                  
        _, is_edit_mode = ps.imgui.Checkbox("edit_mode:  Tick the box and press the letter key C", is_edit_mode)

        # 当前的标签文件 
        changed, selected_label_index = ps.imgui.SliderInt("selected_label_index", selected_label_index, v_min=0, v_max=len(label_files)-1)
        if changed:
            print(f"当前改变label的txt为: {label_files[selected_label_index]}")
            ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(selected_label_index)  +"---"+ label_files[selected_label_index], color_mapping[label_data[selected_label_index]], defined_on='faces',enabled=True)
            print("重新读取txtlabel，拖动进度条前请先保存更改")
            updated_labels = copy.deepcopy(label_data[selected_label_index])
            modified_faces = []

        # 选择几领域的面 
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

        # 保存
        if ps.imgui.Button("save_in_current_txt"):
            np.savetxt(dir_path + "/"+ label_files[selected_label_index], updated_labels, fmt='%d')
            print(f"保存成功: {label_files[selected_label_index]}")
            label_data[selected_label_index] = updated_labels
        if ps.imgui.Button("save_in_custom"):
            mesh_name = file_name.split(".")[0]
            np.savetxt(dir_path + "/"+  mesh_name+ "_Tri_labeling_Custom.txt", updated_labels, fmt='%d')
            print(f"保存成功: {file_name}_Tri_labeling.txt")

            if mesh_name+ "_Tri_labeling_Custom.txt" not in label_files:
                print(label_files)
                label_files.append(mesh_name+ "_Tri_labeling_Custom.txt")
                label_data.append(updated_labels)
                print(f"添加新的label文件: {mesh_name+ '_Tri_labeling_Custom.txt'}")
                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(len(label_files)-1)  +"---"+ mesh_name+ "_Tri_labeling_Custom.txt", color_mapping[updated_labels], defined_on='faces')
            else:
                index = label_files.index(mesh_name+ "_Tri_labeling_Custom.txt")
                label_data[index] = updated_labels
                ps.get_surface_mesh(file_name + "-Tri").add_color_quantity(str(index)  +"---"+ mesh_name+ "_Tri_labeling_Custom.txt", color_mapping[updated_labels], defined_on='faces')

        # 回退机制
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
    # 查找所有符合条件的文件，提取不带路径的文件名和对应路径
    label_files = [os.path.basename(f) for f in glob.glob(label_pattern) ]
    print(f"找到的label文件: {label_files}")

    for i, label_file in enumerate(label_files):
            labels = np.loadtxt(dir_path + "/"+ label_file, dtype=int)
            if  mesh.n_faces() != labels.shape[0]:
                print(f"注意！:txt里面的标签数量和面的数量不匹配 '{label_file}'")
                print("面的数量为", mesh.n_faces)
                print("labels的数量为", labels.shape[0])
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
                    print(f"注意！:txt里面没有_Tri_labeling.txt '{label_pattern}'")
        ps.set_user_callback(update_labels)
    else:
        print(f"未找到匹配的 label 文件，模式: '{label_pattern}'")
        ps.get_surface_mesh(file_name + "-Tri").set_edge_width(1)

    ps.show()
    ps.remove_all_structures()
    ps.clear_user_callback()


def modify_labels_in_directory(base_path):
    '''依次读取基本路径里面的每个三角形网格和标签,然后交互改变标签颜色'''
    file_list = os.listdir(base_path)
    for file_name in file_list:
        if file_name.endswith(".obj"):
            modify_labels(os.path.join(base_path, file_name))
            print(f"已完成: {file_name}")

if __name__ == "__main__":
    # 指定路径
    input_path = r"D:\polycube_data"

    # 检查路径是文件还是目录
    if os.path.isfile(input_path) and input_path.endswith(".obj"):
        modify_labels(input_path)
    elif os.path.isdir(input_path):
        modify_labels_in_directory(input_path)
    else:
        print(f"路径无效: {input_path}")