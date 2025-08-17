# Interactive-3D-mesh-label-color-modification-tool

## 📄 Project Introduction
This project aims to develop a Python-based 3D mesh visualization and annotation tool. Leveraging the OpenMesh and Polyscope libraries, it implements the following core features:
- Interactively select and modify label colors for 3D mesh faces
- Supports batch color modification using k-neighborhood filtering
- Real-time visualization and label saving

## ✨ Core Functionality
| Functional Modules | Implementation Details |
|-------------------|--------------------------------------------------------------------------|
| Interactive Label Modification | Select faces by clicking on them, supporting both single and k-neighborhood selection modes |
| Color Mapping System | 10 preset color schemes, supports custom RGB value input |
| Undo/Redo Mechanism | History Stack (5 levels deep) |
| Multiple Format Support | OBJ Mesh Files + TXT Label Files |
| Real-time Visualization | Polyscope Rendering Engine (supports rotation, translation, and zooming) |

## 🛠️ Technical Architecture
```Python
Required library versions:
Numpy >= 1.21.0
Polyscope >= 1.3.0
OpenMesh 8.1 (requires compilation and installation)
Libigl >= 2.4.0 (requires compilation and installation)
