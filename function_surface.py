import numpy as np
import math

class FunctionSurface:
    def __init__(self):
        pass
    
    def create_function_surface(self, function_str, x_range=(-3, 3), y_range=(-3, 3), subdivisions=20):
        """
        Create a surface from a function z = f(x, y)
        
        Args:
            function_str: String representation of the function (using x and y)
            x_range: Tuple (x_min, x_max)
            y_range: Tuple (y_min, y_max)
            subdivisions: Number of subdivisions in each direction
        """
        vertices = []
        faces = []
        
        x_min, x_max = x_range
        y_min, y_max = y_range
        
        # Create grid
        x = np.linspace(x_min, x_max, subdivisions)
        y = np.linspace(y_min, y_max, subdivisions)
        
        # Evaluate function
        for i in range(subdivisions):
            for j in range(subdivisions):
                x_val = x[i]
                y_val = y[j]
                
                try:
                    # Safe evaluation of the function
                    z_val = eval(function_str, {"np": np, "math": math, "x": x_val, "y": y_val})
                except:
                    z_val = 0
                
                vertices.append([x_val, y_val, z_val])
        
        # Create faces (quads)
        for i in range(subdivisions - 1):
            for j in range(subdivisions - 1):
                idx1 = i * subdivisions + j
                idx2 = i * subdivisions + j + 1
                idx3 = (i + 1) * subdivisions + j + 1
                idx4 = (i + 1) * subdivisions + j
                
                # Create two triangles for the quad
                faces.append([idx1, idx2, idx3])
                faces.append([idx1, idx3, idx4])
        
        return np.array(vertices), faces
    
    def create_paraboloid(self, subdivisions=20):
        """Create a paraboloid surface"""
        return self.create_function_surface("x**2 + y**2", (-1, 1), (-1, 1), subdivisions)
    
    def create_sinc_function(self, subdivisions=20):
        """Create a sinc function surface"""
        return self.create_function_surface("np.sin(np.sqrt(x**2 + y**2)) / (np.sqrt(x**2 + y**2) + 1e-8)", 
                                          (-3, 3), (-3, 3), subdivisions)
    
    def create_ripple(self, subdivisions=20):
        """Create a ripple surface"""
        return self.create_function_surface("np.sin(x**2 + y**2)", (-2, 2), (-2, 2), subdivisions)