import numpy as np
import math

class AffineTransform:
    def __init__(self):
        pass
    
    def translate(self, vertices, dx, dy, dz):
        """Translate vertices by (dx, dy, dz)"""
        if len(vertices) == 0:
            return vertices
            
        # Простое сложение - правильный способ для перемещения
        translated_vertices = vertices.copy()
        translated_vertices[:, 0] += dx  # X
        translated_vertices[:, 1] += dy  # Y  
        translated_vertices[:, 2] += dz  # Z
        
        return translated_vertices
    
    def rotate(self, vertices, rx, ry, rz):
        """Rotate vertices by rx, ry, rz degrees around X, Y, Z axes"""
        if len(vertices) == 0:
            return vertices
            
        # Convert to radians
        rx_rad = math.radians(rx)
        ry_rad = math.radians(ry)
        rz_rad = math.radians(rz)
        
        # Rotation matrices
        rot_x = np.array([
            [1, 0, 0],
            [0, math.cos(rx_rad), -math.sin(rx_rad)],
            [0, math.sin(rx_rad), math.cos(rx_rad)]
        ])
        
        rot_y = np.array([
            [math.cos(ry_rad), 0, math.sin(ry_rad)],
            [0, 1, 0],
            [-math.sin(ry_rad), 0, math.cos(ry_rad)]
        ])
        
        rot_z = np.array([
            [math.cos(rz_rad), -math.sin(rz_rad), 0],
            [math.sin(rz_rad), math.cos(rz_rad), 0],
            [0, 0, 1]
        ])
        
        # Combine rotations (правильный порядок: Z * Y * X)
        rotation_matrix = rot_z @ rot_y @ rot_x
        
        # Apply rotation
        rotated_vertices = vertices @ rotation_matrix.T
        
        return rotated_vertices
    
    def scale(self, vertices, sx, sy, sz):
        """Scale vertices by (sx, sy, sz) relative to model center"""
        if len(vertices) == 0:
            return vertices
            
        # Масштабирование относительно центра модели
        center = np.mean(vertices, axis=0)
        
        # Сначала перемещаем в начало координат, масштабируем, затем возвращаем обратно
        vertices_centered = vertices - center
        
        # Простое умножение для масштабирования
        vertices_scaled = vertices_centered.copy()
        vertices_scaled[:, 0] *= sx  # X
        vertices_scaled[:, 1] *= sy  # Y
        vertices_scaled[:, 2] *= sz  # Z
        
        return vertices_scaled + center

    def scale_origin(self, vertices, sx, sy, sz):
        """Scale vertices relative to origin (0,0,0)"""
        if len(vertices) == 0:
            return vertices
            
        # Простое умножение для масштабирования относительно начала координат
        scaled_vertices = vertices.copy()
        scaled_vertices[:, 0] *= sx  # X
        scaled_vertices[:, 1] *= sy  # Y
        scaled_vertices[:, 2] *= sz  # Z
        
        return scaled_vertices