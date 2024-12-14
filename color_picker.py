import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
import math
import time

class ColorPicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Sameer's Color Picker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Initialize variables
        self.images = []  # List to store multiple images
        self.current_image_index = -1
        self.zoom_level = 1.0
        self.target_zoom = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.target_pan_x = 0
        self.target_pan_y = 0
        self.is_animating = False
        self.animation_start_time = 0
        self.animation_duration = 0.3  # seconds

        # Style configuration
        self._setup_styles()
        
        # Create UI elements
        self._create_layout()
        
        # Bind events
        self._bind_events()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 28, 'bold'), 
                       foreground='#333333', background='#f0f0f0')
        style.configure('Subtitle.TLabel', font=('Helvetica', 14), 
                       foreground='#666666', background='#f0f0f0')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0', 
                       foreground='#333333')
        style.configure('TButton', padding=10)

    def _create_layout(self):
        # Main layout
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Container for panels
        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Left panel (Image display)
        self._create_left_panel(container)

        # Right panel (Controls)
        self._create_right_panel(container)

    def _create_left_panel(self, container):
        self.left_panel = ttk.Frame(container)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Canvas for image display
        self.canvas_frame = ttk.Frame(self.left_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='white',
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground='#cccccc'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _create_right_panel(self, container):
        self.right_panel = ttk.Frame(container, width=300)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.right_panel.pack_propagate(False)

        # Upload button
        self.upload_btn = ttk.Button(
            self.right_panel,
            text="Upload Images",
            command=self.upload_images
        )
        self.upload_btn.pack(fill=tk.X, pady=(0, 10))

        # Navigation buttons
        self._create_navigation_frame()
        
        # Magnifier
        self._create_magnifier_frame()
        
        # Color information
        self._create_color_info_frame()
        
        # Zoom controls
        self._create_zoom_controls()

    def _create_navigation_frame(self):
        nav_frame = ttk.Frame(self.right_panel)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.prev_btn = ttk.Button(nav_frame, text="◀ Previous", 
                                  command=self.prev_image)
        self.prev_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        self.next_btn = ttk.Button(nav_frame, text="Next ▶", 
                                  command=self.next_image)
        self.next_btn.pack(side=tk.RIGHT, expand=True, padx=2)

    def _create_magnifier_frame(self):
        magnifier_frame = ttk.LabelFrame(self.right_panel, text="Magnifier", 
                                       padding=5)
        magnifier_frame.pack(fill=tk.X, pady=(0, 10))

        self.magnifier = tk.Canvas(
            magnifier_frame,
            width=250,
            height=250,
            bg='white',
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground='#cccccc'
        )
        self.magnifier.pack(pady=(2, 2))

    def _create_color_info_frame(self):
        self.color_frame = ttk.LabelFrame(self.right_panel, 
                                        text="Color Information", 
                                        padding=10)
        self.color_frame.pack(fill=tk.X, pady=(0, 10))

        self.color_preview = tk.Canvas(
            self.color_frame,
            width=250,
            height=100,
            bg='white',
            relief='solid',
            bd=1
        )
        self.color_preview.pack(pady=(0, 10))

        self.rgb_label = ttk.Label(
            self.color_frame, 
            text="RGB: ---, ---, ---",
            font=('Helvetica', 12),
            foreground='#333333'
        )
        self.rgb_label.pack(pady=3)
        
        self.hex_label = ttk.Label(
            self.color_frame, 
            text="HEX: #------",
            font=('Helvetica', 12),
            foreground='#333333'
        )
        self.hex_label.pack(pady=3)

    def _create_zoom_controls(self):
        zoom_frame = ttk.LabelFrame(self.right_panel, text="Zoom Controls", 
                                  padding=10)
        zoom_frame.pack(fill=tk.X, pady=(0, 10))

        self.zoom_in_btn = ttk.Button(zoom_frame, text="🔍 Zoom In", 
                                    command=self.zoom_in)
        self.zoom_in_btn.pack(fill=tk.X, pady=3)

        self.zoom_out_btn = ttk.Button(zoom_frame, text="🔍 Zoom Out", 
                                     command=self.zoom_out)
        self.zoom_out_btn.pack(fill=tk.X, pady=3)

        self.reset_zoom_btn = ttk.Button(zoom_frame, text="↺ Reset Zoom", 
                                       command=self.reset_zoom)
        self.reset_zoom_btn.pack(fill=tk.X, pady=3)

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self.get_color)
        self.canvas.bind("<Button-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<ButtonRelease-3>", self.end_pan)
        self.canvas.bind("<MouseWheel>", self.mouse_zoom)
        self.canvas.bind("<Button-4>", self.mouse_zoom)
        self.canvas.bind("<Button-5>", self.mouse_zoom)
        self.canvas.bind("<Control-MouseWheel>", self.trackpad_zoom)
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.canvas.bind("<Motion>", self.update_magnifier)

    def animate(self, duration=0.3):
        if not self.is_animating:
            self.animation_start_time = time.time()
            self.animation_duration = duration
            self.is_animating = True
            self._animate_frame()

    def _animate_frame(self):
        if not self.is_animating:
            return

        current_time = time.time()
        progress = min((current_time - self.animation_start_time) / 
                      self.animation_duration, 1.0)
        
        # Easing function (ease-out-quad)
        t = 1 - (1 - progress) * (1 - progress)

        # Animate zoom
        if self.zoom_level != self.target_zoom:
            self.zoom_level = self._lerp(self.zoom_level, self.target_zoom, t)

        # Animate pan
        if self.pan_offset_x != self.target_pan_x or \
           self.pan_offset_y != self.target_pan_y:
            self.pan_offset_x = self._lerp(self.pan_offset_x, self.target_pan_x, t)
            self.pan_offset_y = self._lerp(self.pan_offset_y, self.target_pan_y, t)

        self.display_current_image()

        if progress < 1.0:
            self.root.after(16, self._animate_frame)  # ~60fps
        else:
            self.is_animating = False

    def _lerp(self, start, end, t):
        return start + (end - start) * t

    def upload_images(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_paths:
            self.images = []
            for path in file_paths:
                cv_image = cv2.imread(path)
                if cv_image is not None:
                    self.images.append(cv_image)
            
            if self.images:
                self.current_image_index = 0
                self.reset_view()
                self.display_current_image()

    def reset_view(self):
        """Reset zoom and pan to default values"""
        self.zoom_level = 1.0
        self.target_zoom = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.target_pan_x = 0
        self.target_pan_y = 0

    def display_current_image(self):
        if 0 <= self.current_image_index < len(self.images):
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(self.images[self.current_image_index], 
                                   cv2.COLOR_BGR2RGB)
            
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Resize image to fit canvas while maintaining aspect ratio
            height, width = rgb_image.shape[:2]
            scale = min(canvas_width/width, canvas_height/height)
            new_width = int(width * scale * self.zoom_level)
            new_height = int(height * scale * self.zoom_level)
            
            rgb_image = cv2.resize(rgb_image, (new_width, new_height))
            
            # Convert to PhotoImage for canvas
            self.image = Image.fromarray(rgb_image)
            self.photo = ImageTk.PhotoImage(self.image)
            
            # Update canvas with pan offset
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width//2 + self.pan_offset_x,
                canvas_height//2 + self.pan_offset_y,
                anchor="center",
                image=self.photo
            )

    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.reset_view()
            self.animate(duration=0.3)

    def next_image(self):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.reset_view()
            self.animate(duration=0.3)

    def zoom_in(self):
        self.target_zoom = min(self.zoom_level * 1.2, 5.0)
        self.animate(duration=0.2)

    def zoom_out(self):
        self.target_zoom = max(self.zoom_level / 1.2, 0.1)
        self.animate(duration=0.2)

    def reset_zoom(self):
        self.target_zoom = 1.0
        self.target_pan_x = 0
        self.target_pan_y = 0
        self.animate(duration=0.3)

    def mouse_zoom(self, event):
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            self.target_zoom = min(self.zoom_level * 1.1, 5.0)
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            self.target_zoom = max(self.zoom_level / 1.1, 0.1)
        self.animate(duration=0.15)

    def trackpad_zoom(self, event):
        if event.delta:
            scale = 0.002
            self.target_zoom = min(max(
                self.zoom_level * (1 + event.delta * scale), 
                0.1), 5.0)
            self.animate(duration=0.1)

    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.start_offset_x = self.pan_offset_x
        self.start_offset_y = self.pan_offset_y

    def pan(self, event):
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.pan_offset_x = self.start_offset_x + dx
        self.pan_offset_y = self.start_offset_y + dy
        self.display_current_image()

    def end_pan(self, event):
        self.target_pan_x = self.pan_offset_x
        self.target_pan_y = self.pan_offset_y
        self.animate(duration=0.2)

    def get_color(self, event):
        if self.current_image_index >= 0:
            bbox = self.canvas.bbox("all")
            if bbox:
                img_x = bbox[0]
                img_y = bbox[1]
                img_width = bbox[2] - bbox[0]
                img_height = bbox[3] - bbox[1]

                rel_x = (event.x - img_x) / img_width
                rel_y = (event.y - img_y) / img_height

                height, width = self.images[self.current_image_index].shape[:2]
                x = int(rel_x * width)
                y = int(rel_y * height)

                if 0 <= x < width and 0 <= y < height:
                    bgr_color = self.images[self.current_image_index][y, x]
                    rgb_color = tuple(reversed(bgr_color))
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb_color)

                    self.rgb_label.config(
                        text=f"RGB: {rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}")
                    self.hex_label.config(text=f"HEX: {hex_color}")
                    self.color_preview.configure(bg=hex_color)

    def update_magnifier(self, event):
        if self.current_image_index >= 0:
            bbox = self.canvas.bbox("all")
            if bbox:
                img_x = bbox[0]
                img_y = bbox[1]
                img_width = bbox[2] - bbox[0]
                img_height = bbox[3] - bbox[1]

                rel_x = (event.x - img_x) / img_width
                rel_y = (event.y - img_y) / img_height

                height, width = self.images[self.current_image_index].shape[:2]
                x = int(rel_x * width)
                y = int(rel_y * height)

                if 0 <= x < width and 0 <= y < height:
                    region_size = 20
                    x_start = max(0, x - region_size//2)
                    y_start = max(0, y - region_size//2)
                    x_end = min(width, x + region_size//2)
                    y_end = min(height, y + region_size//2)

                    region = self.images[self.current_image_index][y_start:y_end, 
                                                                 x_start:x_end]
                    region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
                    magnified_region = cv2.resize(region_rgb, (150, 150), 
                                                interpolation=cv2.INTER_NEAREST)

                    # Add crosshair
                    magnified_region = cv2.line(magnified_region, 
                                              (75, 0), (75, 150), (255, 0, 0), 1)
                    magnified_region = cv2.line(magnified_region, 
                                              (0, 75), (150, 75), (255, 0, 0), 1)

                    magnified_image = Image.fromarray(magnified_region)
                    magnified_photo = ImageTk.PhotoImage(magnified_image)

                    self.magnifier.delete("all")
                    self.magnifier.config(width=150, height=150)
                    self.magnifier.create_image(75, 75, anchor="center", 
                                              image=magnified_photo)
                    self.magnifier.image = magnified_photo

def main():
    root = tk.Tk()
    app = ColorPicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()