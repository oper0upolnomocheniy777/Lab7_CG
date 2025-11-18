import numpy as np

class OBJLoader:
    def __init__(self):
        pass
    
    def load_obj(self, filename):
        """
        Load OBJ file with support for:
        - vertices (v)
        - texture coordinates (vt)
        - vertex normals (vn)
        - faces with various formats (f)
        - materials (mtllib, usemtl)
        - objects (o)
        - smoothing groups (s)
        """
        vertices = []
        texture_coords = []
        normals = []
        faces = []
        
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                keyword = parts[0]
                data = parts[1:]
                
                if keyword == 'v':
                    # Vertex: v x y z [w]
                    if len(data) >= 3:
                        vertex = [float(data[0]), float(data[1]), float(data[2])]
                        vertices.append(vertex)
                
                elif keyword == 'vt':
                    # Texture coordinate: vt u v [w]
                    if len(data) >= 2:
                        tex_coord = [float(data[0]), float(data[1])]
                        texture_coords.append(tex_coord)
                
                elif keyword == 'vn':
                    # Vertex normal: vn i j k
                    if len(data) >= 3:
                        normal = [float(data[0]), float(data[1]), float(data[2])]
                        normals.append(normal)
                
                elif keyword == 'f':
                    # Face: can have various formats:
                    # f v1 v2 v3 ...
                    # f v1/vt1 v2/vt2 v3/vt3 ...
                    # f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...
                    # f v1//vn1 v2//vn2 v3//vn3 ...
                    if len(data) >= 3:
                        face_vertices = []
                        for part in data:
                            # Parse vertex indices
                            vertex_parts = part.split('/')
                            
                            # Vertex index (always required)
                            if vertex_parts[0]:
                                vertex_idx = int(vertex_parts[0]) - 1  # Convert to 0-based
                                face_vertices.append(vertex_idx)
                        
                        faces.append(face_vertices)
        
        return np.array(vertices), faces
    
    def load_obj_advanced(self, filename):
        """
        Advanced loader that handles more OBJ features
        Returns vertices, faces, and additional information
        """
        vertices = []
        texture_coords = []
        normals = []
        faces = []
        current_material = None
        current_object = None
        
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split()
                    if not parts:
                        continue
                    
                    keyword = parts[0]
                    data = parts[1:]
                    
                    if keyword == 'v':
                        if len(data) >= 3:
                            vertex = [float(data[0]), float(data[1]), float(data[2])]
                            vertices.append(vertex)
                    
                    elif keyword == 'vt':
                        if len(data) >= 2:
                            tex_coord = [float(data[0]), float(data[1])]
                            texture_coords.append(tex_coord)
                    
                    elif keyword == 'vn':
                        if len(data) >= 3:
                            normal = [float(data[0]), float(data[1]), float(data[2])]
                            normals.append(normal)
                    
                    elif keyword == 'f':
                        if len(data) >= 3:
                            face_vertices = []
                            for part in data:
                                vertex_parts = part.split('/')
                                
                                # Handle different face formats
                                if len(vertex_parts) == 1:
                                    # f v1 v2 v3
                                    vertex_idx = int(vertex_parts[0]) - 1
                                    face_vertices.append(vertex_idx)
                                elif len(vertex_parts) >= 2:
                                    # f v1/vt1 v2/vt2 v3/vt3
                                    # f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3
                                    # f v1//vn1 v2//vn2 v3//vn3
                                    if vertex_parts[0]:  # Vertex index
                                        vertex_idx = int(vertex_parts[0]) - 1
                                        face_vertices.append(vertex_idx)
                            
                            if len(face_vertices) >= 3:
                                # Convert polygon to triangles if needed
                                if len(face_vertices) == 3:
                                    faces.append(face_vertices)
                                elif len(face_vertices) == 4:
                                    # Quad to two triangles
                                    faces.append([face_vertices[0], face_vertices[1], face_vertices[2]])
                                    faces.append([face_vertices[0], face_vertices[2], face_vertices[3]])
                                else:
                                    # N-gon to triangles using fan triangulation
                                    for i in range(1, len(face_vertices) - 1):
                                        faces.append([face_vertices[0], face_vertices[i], face_vertices[i + 1]])
                
                except Exception as e:
                    print(f"Warning: Error parsing line {line_num}: {line}")
                    print(f"Error: {e}")
                    continue
        
        return np.array(vertices), faces, texture_coords, normals
    
    def load_simple_obj(self, filename):
        """Simple loader that extracts only vertices and faces"""
        vertices = []
        faces = []
        
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('v ') and not line.startswith('vt ') and not line.startswith('vn '):
                    coords = list(map(float, line.split()[1:4]))
                    vertices.append(coords)
                elif line.startswith('f '):
                    face_data = line.split()[1:]
                    face_vertices = []
                    
                    for vertex_str in face_data:
                        # Extract vertex index (first part before any '/')
                        vertex_idx = int(vertex_str.split('/')[0]) - 1
                        face_vertices.append(vertex_idx)
                    
                    if len(face_vertices) >= 3:
                        faces.append(face_vertices)
        
        return np.array(vertices), faces