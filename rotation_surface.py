import numpy as np
import math

class RotationSurface:
    def __init__(self):
        pass
    
    def create_rotation_surface(self, profile_points, axis='y', segments=16):
        """
        Create a rotation surface from profile points
        
        Args:
            profile_points: List of (x, y) points defining the profile
            axis: Axis of rotation ('x', 'y', or 'z')
            segments: Number of rotation segments
        """
        vertices = []
        faces = []
        
        angle_step = 2 * math.pi / segments
        
        # Generate vertices
        for i in range(segments):
            angle = i * angle_step
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            
            for x, y in profile_points:
                if axis == 'x':
                    # Rotate around X axis
                    vertex = [x, y * cos_angle, y * sin_angle]
                elif axis == 'y':
                    # Rotate around Y axis (most common)
                    vertex = [x * cos_angle, y, x * sin_angle]
                elif axis == 'z':
                    # Rotate around Z axis
                    vertex = [x * cos_angle, x * sin_angle, y]
                else:
                    raise ValueError("Axis must be 'x', 'y', or 'z'")
                
                vertices.append(vertex)
        
        # Generate faces (quads between segments)
        profile_len = len(profile_points)
        for i in range(segments):
            for j in range(profile_len - 1):
                # Current segment indices
                idx1 = i * profile_len + j
                idx2 = i * profile_len + j + 1
                
                # Next segment indices (wrap around)
                next_i = (i + 1) % segments
                idx3 = next_i * profile_len + j + 1
                idx4 = next_i * profile_len + j
                
                # Create two triangles for the quad
                faces.append([idx1, idx2, idx3])
                faces.append([idx1, idx3, idx4])
        
        return np.array(vertices), faces
    
    def create_cylinder(self, radius=1, height=2, segments=16):
        """Create a cylinder using rotation surface"""
        profile_points = [
            (0, -height/2),
            (radius, -height/2),
            (radius, height/2),
            (0, height/2)
        ]
        return self.create_rotation_surface(profile_points, 'y', segments)
    
    def create_sphere(self, radius=1, segments=16):
        """Create a sphere using rotation surface"""
        profile_points = []
        for i in range(segments // 2 + 1):
            angle = math.pi * i / (segments // 2)
            x = radius * math.sin(angle)
            y = radius * math.cos(angle)
            profile_points.append((x, y))
        return self.create_rotation_surface(profile_points, 'y', segments)