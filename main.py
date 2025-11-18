import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from model_loader import OBJLoader
from rotation_surface import RotationSurface
from function_surface import FunctionSurface
from affine_transformations import AffineTransform
from obj_writer import OBJWriter
import os

class ModelViewer3D:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Model Viewer - Программа для работы с 3D графикой")
        self.root.geometry("1200x800")
        
        self.current_vertices = None
        self.current_faces = None
        self.current_model_type = None
        self.current_filename = None
        self.original_vertices = None  # Сохраняем оригинальные вершины для сброса
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls with scrollbar
        left_container = ttk.Frame(main_frame, width=320)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_container.pack_propagate(False)  # Prevent shrinking
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(left_container, width=300, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Control frame inside scrollable area
        control_frame = ttk.LabelFrame(scrollable_frame, text="Управление")
        control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Program description
        desc_frame = ttk.LabelFrame(control_frame, text="О программе")
        desc_frame.pack(fill=tk.X, pady=5, padx=5)
        
        desc_text = (
            "Программа для работы с 3D графикой:\n"
            "1. Загрузка/сохранение OBJ моделей\n"
            "2. Создание фигур вращения\n" 
            "3. Построение графиков функций\n"
            "4. Аффинные преобразования"
        )
        desc_label = ttk.Label(desc_frame, text=desc_text, wraplength=280, justify=tk.LEFT)
        desc_label.pack(fill=tk.X, pady=5, padx=5)
        
        # Model info section
        info_frame = ttk.LabelFrame(control_frame, text="Информация о модели")
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.info_label = ttk.Label(info_frame, text="Модель не загружена", wraplength=280, justify=tk.LEFT)
        self.info_label.pack(fill=tk.X, pady=5, padx=5)
        
        # Model loading section
        load_frame = ttk.LabelFrame(control_frame, text="Загрузка/Сохранение моделей")
        load_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(load_frame, text="Загрузить OBJ модель", 
                  command=self.load_obj).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(load_frame, text="Сохранить модель в OBJ", 
                  command=self.save_obj).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(load_frame, text="Сбросить преобразования", 
                  command=self.reset_transformations).pack(fill=tk.X, pady=2, padx=5)
        
        # Rotation surface section
        rotation_frame = ttk.LabelFrame(control_frame, text="Фигура вращения")
        rotation_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(rotation_frame, text="Точки образующей (x,y):").pack(anchor=tk.W, padx=5)
        self.profile_entry = ttk.Entry(rotation_frame, width=25)
        self.profile_entry.insert(0, "0,0 1,0 1,1 0,1")
        self.profile_entry.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Label(rotation_frame, text="Ось вращения:").pack(anchor=tk.W, padx=5)
        self.axis_var = tk.StringVar(value="y")
        axis_frame = ttk.Frame(rotation_frame)
        axis_frame.pack(fill=tk.X, padx=5)
        ttk.Radiobutton(axis_frame, text="X", variable=self.axis_var, value="x").pack(side=tk.LEFT)
        ttk.Radiobutton(axis_frame, text="Y", variable=self.axis_var, value="y").pack(side=tk.LEFT)
        ttk.Radiobutton(axis_frame, text="Z", variable=self.axis_var, value="z").pack(side=tk.LEFT)
        
        ttk.Label(rotation_frame, text="Количество сегментов:").pack(anchor=tk.W, padx=5)
        self.segments_entry = ttk.Entry(rotation_frame, width=10)
        self.segments_entry.insert(0, "16")
        self.segments_entry.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Button(rotation_frame, text="Создать фигуру вращения", 
                  command=self.create_rotation_surface).pack(fill=tk.X, pady=5, padx=5)
        
        # Function surface section
        function_frame = ttk.LabelFrame(control_frame, text="График функции")
        function_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(function_frame, text="Функция f(x,y):").pack(anchor=tk.W, padx=5)
        self.function_entry = ttk.Entry(function_frame, width=25)
        self.function_entry.insert(0, "np.sin(np.sqrt(x**2 + y**2))")
        self.function_entry.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Label(function_frame, text="Диапазон X:").pack(anchor=tk.W, padx=5)
        self.x_range_entry = ttk.Entry(function_frame, width=20)
        self.x_range_entry.insert(0, "-3,3")
        self.x_range_entry.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Label(function_frame, text="Диапазон Y:").pack(anchor=tk.W, padx=5)
        self.y_range_entry = ttk.Entry(function_frame, width=20)
        self.y_range_entry.insert(0, "-3,3")
        self.y_range_entry.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Label(function_frame, text="Количество разбиений:").pack(anchor=tk.W, padx=5)
        self.subdivisions_entry = ttk.Entry(function_frame, width=10)
        self.subdivisions_entry.insert(0, "20")
        self.subdivisions_entry.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Button(function_frame, text="Построить график функции", 
                  command=self.create_function_surface).pack(fill=tk.X, pady=5, padx=5)
        
        # Affine transformations section
        transform_frame = ttk.LabelFrame(control_frame, text="Аффинные преобразования")
        transform_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Translation
        ttk.Label(transform_frame, text="Перемещение (dx,dy,dz):").pack(anchor=tk.W, padx=5)
        trans_frame = ttk.Frame(transform_frame)
        trans_frame.pack(fill=tk.X, padx=5)
        self.trans_x = ttk.Entry(trans_frame, width=6)
        self.trans_x.insert(0, "0.0")
        self.trans_x.pack(side=tk.LEFT, padx=2)
        self.trans_y = ttk.Entry(trans_frame, width=6)
        self.trans_y.insert(0, "0.0")
        self.trans_y.pack(side=tk.LEFT, padx=2)
        self.trans_z = ttk.Entry(trans_frame, width=6)
        self.trans_z.insert(0, "0.0")
        self.trans_z.pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_frame, text="Применить перемещение", 
                  command=self.translate_model).pack(fill=tk.X, pady=2, padx=5)
        
        # Rotation
        ttk.Label(transform_frame, text="Поворот (градусы):").pack(anchor=tk.W, padx=5)
        rot_frame = ttk.Frame(transform_frame)
        rot_frame.pack(fill=tk.X, padx=5)
        self.rot_x = ttk.Entry(rot_frame, width=6)
        self.rot_x.insert(0, "0.0")
        self.rot_x.pack(side=tk.LEFT, padx=2)
        self.rot_y = ttk.Entry(rot_frame, width=6)
        self.rot_y.insert(0, "0.0")
        self.rot_y.pack(side=tk.LEFT, padx=2)
        self.rot_z = ttk.Entry(rot_frame, width=6)
        self.rot_z.insert(0, "0.0")
        self.rot_z.pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_frame, text="Применить поворот", 
                  command=self.rotate_model).pack(fill=tk.X, pady=2, padx=5)
        
        # Scaling
        ttk.Label(transform_frame, text="Масштаб (sx,sy,sz):").pack(anchor=tk.W, padx=5)
        scale_frame = ttk.Frame(transform_frame)
        scale_frame.pack(fill=tk.X, padx=5)
        self.scale_x = ttk.Entry(scale_frame, width=6)
        self.scale_x.insert(0, "1.0")
        self.scale_x.pack(side=tk.LEFT, padx=2)
        self.scale_y = ttk.Entry(scale_frame, width=6)
        self.scale_y.insert(0, "1.0")
        self.scale_y.pack(side=tk.LEFT, padx=2)
        self.scale_z = ttk.Entry(scale_frame, width=6)
        self.scale_z.insert(0, "1.0")
        self.scale_z.pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_frame, text="Применить масштаб", 
                  command=self.scale_model).pack(fill=tk.X, pady=2, padx=5)
        
        # Reset button
        ttk.Button(control_frame, text="Сбросить вид", 
                  command=self.reset_view).pack(fill=tk.X, pady=10, padx=5)
        
        # Right panel - 3D Plot
        plot_container = ttk.Frame(main_frame)
        plot_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_plot(plot_container)
        
    def setup_plot(self, parent):
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Model Viewer - Загрузите модель для начала работы')
        
        # Embed plot in tkinter
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_plot.draw()
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def load_obj(self):
        """Загрузка OBJ файла"""
        filename = filedialog.askopenfilename(
            title="Выберите OBJ файл",
            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")]
        )
        if filename:
            self.load_obj_file(filename)
    
    def load_obj_file(self, filename):
        """Загрузка OBJ файла с расширенным парсером"""
        try:
            loader = OBJLoader()
            vertices, faces, texture_coords, normals = loader.load_obj_advanced(filename)
            
            self.current_vertices = vertices
            self.original_vertices = vertices.copy()  # Сохраняем оригинал
            self.current_faces = faces
            self.current_model_type = "loaded"
            self.current_filename = filename
            
            # Update info
            info_text = f"Файл: {os.path.basename(filename)}\n"
            info_text += f"Вершин: {len(vertices)}\n"
            info_text += f"Граней: {len(faces)}\n"
            if texture_coords:
                info_text += f"Текстурных координат: {len(texture_coords)}\n"
            if normals:
                info_text += f"Нормалей: {len(normals)}"
            
            self.info_label.config(text=info_text)
            self.plot_model()
            messagebox.showinfo("Успех", f"Модель загружена: {len(vertices)} вершин, {len(faces)} граней")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить модель: {str(e)}")
    
    def save_obj(self):
        """Сохранение модели в OBJ файл"""
        if self.current_vertices is None:
            messagebox.showwarning("Предупреждение", "Нет модели для сохранения")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Сохранить OBJ файл",
            defaultextension=".obj",
            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")]
        )
        if filename:
            try:
                writer = OBJWriter()
                writer.write_obj(filename, self.current_vertices, self.current_faces)
                messagebox.showinfo("Успех", f"Модель сохранена в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить модель: {str(e)}")
    
    def reset_transformations(self):
        """Сброс всех преобразований к исходному состоянию"""
        if self.original_vertices is not None:
            self.current_vertices = self.original_vertices.copy()
            self.plot_model()
            messagebox.showinfo("Успех", "Все преобразования сброшены")
        else:
            messagebox.showwarning("Предупреждение", "Нет загруженной модели для сброса")
    
    def create_rotation_surface(self):
        """Создание фигуры вращения"""
        try:
            profile_text = self.profile_entry.get()
            axis = self.axis_var.get()
            segments = int(self.segments_entry.get())
            
            # Parse profile points
            points = []
            for point_str in profile_text.split():
                x, y = map(float, point_str.split(','))
                points.append((x, y))
            
            if len(points) < 2:
                messagebox.showerror("Ошибка", "Необходимо указать как минимум 2 точки образующей")
                return
            
            rotation_surface = RotationSurface()
            vertices, faces = rotation_surface.create_rotation_surface(points, axis, segments)
            
            self.current_vertices = vertices
            self.original_vertices = vertices.copy()  # Сохраняем оригинал
            self.current_faces = faces
            self.current_model_type = "rotation"
            self.current_filename = None
            
            self.info_label.config(text=f"Фигура вращения\nВершин: {len(vertices)}\nГраней: {len(faces)}")
            self.plot_model()
            
            messagebox.showinfo("Успех", 
                              f"Фигура вращения создана: {len(vertices)} вершин, {len(faces)} граней")
                              
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать фигуру вращения: {str(e)}")
    
    def create_function_surface(self):
        """Построение графика функции"""
        try:
            function_text = self.function_entry.get()
            x_range = tuple(map(float, self.x_range_entry.get().split(',')))
            y_range = tuple(map(float, self.y_range_entry.get().split(',')))
            subdivisions = int(self.subdivisions_entry.get())
            
            if len(x_range) != 2 or len(y_range) != 2:
                messagebox.showerror("Ошибка", "Диапазоны должны быть указаны как два числа через запятую")
                return
            
            function_surface = FunctionSurface()
            vertices, faces = function_surface.create_function_surface(
                function_text, x_range, y_range, subdivisions
            )
            
            self.current_vertices = vertices
            self.original_vertices = vertices.copy()  # Сохраняем оригинал
            self.current_faces = faces
            self.current_model_type = "function"
            self.current_filename = None
            
            self.info_label.config(text=f"График функции\nВершин: {len(vertices)}\nГраней: {len(faces)}")
            self.plot_model()
            
            messagebox.showinfo("Успех", 
                              f"График функции создан: {len(vertices)} вершин, {len(faces)} граней")
                              
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график функции: {str(e)}")
    
    def plot_model(self):
        """Отрисовка 3D модели"""
        self.ax.clear()
        
        if self.current_vertices is not None and self.current_faces is not None:
            vertices = np.array(self.current_vertices)
            faces = self.current_faces
            
            # Calculate bounds for auto-scaling
            if len(vertices) > 0:
                min_coords = vertices.min(axis=0)
                max_coords = vertices.max(axis=0)
                center = (min_coords + max_coords) / 2
                max_range = (max_coords - min_coords).max() / 2
                
                # Set limits with some padding
                padding = max_range * 0.1
                self.ax.set_xlim(center[0] - max_range - padding, center[0] + max_range + padding)
                self.ax.set_ylim(center[1] - max_range - padding, center[1] + max_range + padding)
                self.ax.set_zlim(center[2] - max_range - padding, center[2] + max_range + padding)
            
            # Plot faces
            for face in faces:
                if len(face) >= 3:  # Ensure at least 3 vertices
                    try:
                        polygon = vertices[face]
                        self.ax.plot_trisurf(
                            polygon[:, 0], polygon[:, 1], polygon[:, 2],
                            alpha=0.7, shade=True, color='lightblue', edgecolor='blue', linewidth=0.3
                        )
                    except Exception as e:
                        # Fallback: plot edges only for problematic faces
                        for i in range(len(face)):
                            start_idx = face[i]
                            end_idx = face[(i + 1) % len(face)]
                            if start_idx < len(vertices) and end_idx < len(vertices):
                                start = vertices[start_idx]
                                end = vertices[end_idx]
                                self.ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], 'b-', linewidth=0.5)
        
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        title = '3D Model Viewer'
        if self.current_filename:
            title += f' - {os.path.basename(self.current_filename)}'
        elif self.current_model_type == "rotation":
            title += ' - Фигура вращения'
        elif self.current_model_type == "function":
            title += ' - График функции'
        elif self.current_model_type == "loaded":
            title += ' - Загруженная модель'
        
        self.ax.set_title(title)
        self.canvas_plot.draw()
    
    def translate_model(self):
        """Применение перемещения к модели"""
        if self.current_vertices is None:
            messagebox.showwarning("Предупреждение", "Нет модели для преобразования")
            return
            
        try:
            dx = float(self.trans_x.get())
            dy = float(self.trans_y.get())
            dz = float(self.trans_z.get())
            
            transformer = AffineTransform()
            self.current_vertices = transformer.translate(self.current_vertices, dx, dy, dz)
            self.plot_model()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные значения перемещения")
    
    def rotate_model(self):
        """Применение поворота к модели"""
        if self.current_vertices is None:
            messagebox.showwarning("Предупреждение", "Нет модели для преобразования")
            return
            
        try:
            rx = float(self.rot_x.get())
            ry = float(self.rot_y.get())
            rz = float(self.rot_z.get())
            
            transformer = AffineTransform()
            self.current_vertices = transformer.rotate(self.current_vertices, rx, ry, rz)
            self.plot_model()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные значения поворота")
    
    def scale_model(self):
        """Применение масштабирования к модели"""
        if self.current_vertices is None:
            messagebox.showwarning("Предупреждение", "Нет модели для преобразования")
            return
            
        try:
            sx = float(self.scale_x.get())
            sy = float(self.scale_y.get())
            sz = float(self.scale_z.get())
            
            transformer = AffineTransform()
            self.current_vertices = transformer.scale(self.current_vertices, sx, sy, sz)
            self.plot_model()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные значения масштаба")
    
    def reset_view(self):
        """Сброс вида камеры"""
        if self.current_vertices is not None and len(self.current_vertices) > 0:
            vertices = np.array(self.current_vertices)
            min_coords = vertices.min(axis=0)
            max_coords = vertices.max(axis=0)
            center = (min_coords + max_coords) / 2
            max_range = (max_coords - min_coords).max() / 2
            
            padding = max_range * 0.1
            self.ax.set_xlim(center[0] - max_range - padding, center[0] + max_range + padding)
            self.ax.set_ylim(center[1] - max_range - padding, center[1] + max_range + padding)
            self.ax.set_zlim(center[2] - max_range - padding, center[2] + max_range + padding)
        else:
            self.ax.set_xlim(-2, 2)
            self.ax.set_ylim(-2, 2)
            self.ax.set_zlim(-2, 2)
        
        self.canvas_plot.draw()

def main():
    root = tk.Tk()
    app = ModelViewer3D(root)
    root.mainloop()

if __name__ == "__main__":
    main()