"""
Glassmorphic Image Resizer
A beautiful iOS-inspired image resizing tool with glass design
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path

class GlassStyle:
    """iOS-inspired glass design colors and styles"""
    BG_PRIMARY = "#F5F5F7"
    BG_GLASS = "#FFFFFF"
    GLASS_ALPHA = 0.85
    ACCENT = "#007AFF"
    TEXT_PRIMARY = "#1D1D1F"
    TEXT_SECONDARY = "#6E6E73"
    BORDER = "#D2D2D7"
    SHADOW = "#00000015"

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer")
        self.root.geometry("900x700")
        self.root.configure(bg=GlassStyle.BG_PRIMARY)
        
        self.current_image = None
        self.image_path = None
        self.preview_image = None
        self.zoom_level = 1.0
        
        self.setup_ui()
        
        # Bind keyboard shortcuts for zoom
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())  # For keyboards without numpad
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        
    def setup_ui(self):
        """Create the main UI"""
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self.root, bg=GlassStyle.BG_PRIMARY, highlightthickness=0)
        
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Main container frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=GlassStyle.BG_PRIMARY)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Bind events for scrolling
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Main content frame with padding
        main_frame = tk.Frame(self.scrollable_frame, bg=GlassStyle.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title with zoom controls
        title_frame = tk.Frame(main_frame, bg=GlassStyle.BG_PRIMARY)
        title_frame.pack(pady=(0, 20), fill=tk.X)
        
        title = tk.Label(
            title_frame,
            text="Image Resizer",
            font=("SF Pro Display", 32, "bold"),
            bg=GlassStyle.BG_PRIMARY,
            fg=GlassStyle.TEXT_PRIMARY
        )
        title.pack(side=tk.LEFT)
        
        # Zoom controls
        zoom_frame = tk.Frame(title_frame, bg=GlassStyle.BG_PRIMARY)
        zoom_frame.pack(side=tk.RIGHT)
        
        zoom_label = tk.Label(
            zoom_frame,
            text="Zoom:",
            font=("SF Pro Display", 12),
            bg=GlassStyle.BG_PRIMARY,
            fg=GlassStyle.TEXT_SECONDARY
        )
        zoom_label.pack(side=tk.LEFT, padx=(0, 10))
        
        zoom_out_btn = tk.Button(
            zoom_frame,
            text="−",
            font=("SF Pro Display", 16, "bold"),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            activebackground=GlassStyle.BORDER,
            relief=tk.FLAT,
            borderwidth=1,
            highlightbackground=GlassStyle.BORDER,
            highlightthickness=1,
            width=2,
            cursor="hand2",
            command=self.zoom_out
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_display = tk.Label(
            zoom_frame,
            text="100%",
            font=("SF Pro Display", 12, "bold"),
            bg=GlassStyle.BG_PRIMARY,
            fg=GlassStyle.ACCENT,
            width=6
        )
        self.zoom_display.pack(side=tk.LEFT, padx=5)
        
        zoom_in_btn = tk.Button(
            zoom_frame,
            text="+",
            font=("SF Pro Display", 16, "bold"),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            activebackground=GlassStyle.BORDER,
            relief=tk.FLAT,
            borderwidth=1,
            highlightbackground=GlassStyle.BORDER,
            highlightthickness=1,
            width=2,
            cursor="hand2",
            command=self.zoom_in
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        reset_zoom_btn = tk.Button(
            zoom_frame,
            text="Reset",
            font=("SF Pro Display", 11),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            activebackground=GlassStyle.BORDER,
            relief=tk.FLAT,
            borderwidth=1,
            highlightbackground=GlassStyle.BORDER,
            highlightthickness=1,
            padx=8,
            cursor="hand2",
            command=self.reset_zoom
        )
        reset_zoom_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # File selection card
        self.create_file_selection_card(main_frame)
        
        # Image preview card
        self.create_preview_card(main_frame)
        
        # Controls card
        self.create_controls_card(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
    
    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 2.0:
            self.zoom_level += 0.1
            self.update_zoom()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.1
            self.update_zoom()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_level = 1.0
        self.update_zoom()
    
    def update_zoom(self):
        """Apply zoom level to the window"""
        # Update zoom display
        self.zoom_display.config(text=f"{int(self.zoom_level * 100)}%")
        
        # Calculate new window size based on zoom
        base_width = 900
        base_height = 700
        new_width = int(base_width * self.zoom_level)
        new_height = int(base_height * self.zoom_level)
        
        self.root.geometry(f"{new_width}x{new_height}")
        
        # Update scroll region
        self.on_frame_configure()
        
    def create_glass_frame(self, parent, height=None):
        """Create a glass-effect frame"""
        frame = tk.Frame(
            parent,
            bg=GlassStyle.BG_GLASS,
            highlightbackground=GlassStyle.BORDER,
            highlightthickness=1,
            relief=tk.FLAT
        )
        if height:
            frame.configure(height=height)
        return frame
    
    def create_file_selection_card(self, parent):
        """Create the file selection section"""
        file_frame = self.create_glass_frame(parent)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        inner_frame = tk.Frame(file_frame, bg=GlassStyle.BG_GLASS)
        inner_frame.pack(fill=tk.X, padx=25, pady=20)
        
        # Label
        label = tk.Label(
            inner_frame,
            text="Image File:",
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            width=15,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        # File path display
        self.file_path_label = tk.Label(
            inner_frame,
            text="No file selected",
            font=("SF Pro Display", 12),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_SECONDARY,
            anchor="w"
        )
        self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Select button
        select_btn = tk.Button(
            inner_frame,
            text="Browse...",
            font=("SF Pro Display", 12, "bold"),
            bg=GlassStyle.ACCENT,
            fg="white",
            activebackground="#0051D5",
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.select_image
        )
        select_btn.pack(side=tk.LEFT)
    
    def create_preview_card(self, parent):
        """Create the image preview section"""
        preview_frame = self.create_glass_frame(parent, height=300)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        preview_frame.pack_propagate(False)
        
        # Preview label
        self.preview_label = tk.Label(
            preview_frame,
            text="No image selected\n\nClick 'Select Image' to begin",
            font=("SF Pro Display", 14),
            fg=GlassStyle.TEXT_SECONDARY,
            bg=GlassStyle.BG_GLASS
        )
        self.preview_label.pack(expand=True)
        
    def create_controls_card(self, parent):
        """Create the controls section"""
        controls_frame = self.create_glass_frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        inner_frame = tk.Frame(controls_frame, bg=GlassStyle.BG_GLASS)
        inner_frame.pack(fill=tk.BOTH, padx=25, pady=25)
        
        # Format Selection
        self.create_dropdown_row(
            inner_frame, "Output Format:",
            ["JPEG", "PNG", "WEBP", "BMP", "TIFF"],
            0
        )
        
        # Aspect Ratio
        self.create_dropdown_row(
            inner_frame, "Aspect Ratio:",
            ["Original", "16:9", "4:3", "1:1", "9:16", "3:4", "Custom (pixels)", "Custom (ratio)"],
            1
        )
        
        # Custom dimensions in pixels (initially hidden)
        self.custom_pixels_frame = tk.Frame(inner_frame, bg=GlassStyle.BG_GLASS)
        
        # Width in pixels
        width_container = tk.Frame(self.custom_pixels_frame, bg=GlassStyle.BG_GLASS)
        width_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        tk.Label(
            width_container,
            text="Width (px):",
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        self.width_entry = self.create_entry(width_container)
        self.width_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Height in pixels
        height_container = tk.Frame(self.custom_pixels_frame, bg=GlassStyle.BG_GLASS)
        height_container.grid(row=0, column=1, sticky="ew")
        
        tk.Label(
            height_container,
            text="Height (px):",
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        self.height_entry = self.create_entry(height_container)
        self.height_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        self.custom_pixels_frame.columnconfigure(0, weight=1)
        self.custom_pixels_frame.columnconfigure(1, weight=1)
        
        # Custom aspect ratio (initially hidden)
        self.custom_ratio_frame = tk.Frame(inner_frame, bg=GlassStyle.BG_GLASS)
        
        ratio_container = tk.Frame(self.custom_ratio_frame, bg=GlassStyle.BG_GLASS)
        ratio_container.pack(fill=tk.X)
        
        tk.Label(
            ratio_container,
            text="Aspect Ratio:",
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        ratio_input_frame = tk.Frame(ratio_container, bg=GlassStyle.BG_GLASS)
        ratio_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.ratio_width_entry = self.create_entry(ratio_input_frame)
        self.ratio_width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            ratio_input_frame,
            text=":",
            font=("SF Pro Display", 16, "bold"),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=5)
        
        self.ratio_height_entry = self.create_entry(ratio_input_frame)
        self.ratio_height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            ratio_input_frame,
            text="(e.g., 21:9)",
            font=("SF Pro Display", 11),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_SECONDARY
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Compression/Quality
        self.create_quality_row(inner_frame, 2)
        
        # Max file size option
        self.create_max_size_row(inner_frame, 3)
        
    def create_dropdown_row(self, parent, label_text, options, row):
        """Create a labeled dropdown row"""
        row_frame = tk.Frame(parent, bg=GlassStyle.BG_GLASS)
        row_frame.grid(row=row, column=0, sticky="ew", pady=8)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            width=15,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'Glass.TCombobox',
            fieldbackground=GlassStyle.BG_GLASS,
            background=GlassStyle.BG_GLASS,
            borderwidth=1,
            relief=tk.FLAT
        )
        
        var = tk.StringVar(value=options[0])
        dropdown = ttk.Combobox(
            row_frame,
            textvariable=var,
            values=options,
            state="readonly",
            font=("SF Pro Display", 12),
            style='Glass.TCombobox',
            width=25
        )
        dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if label_text == "Output Format:":
            self.format_var = var
        elif label_text == "Aspect Ratio:":
            self.aspect_var = var
            dropdown.bind('<<ComboboxSelected>>', self.on_aspect_change)
        
        parent.columnconfigure(0, weight=1)
        
        return var
    
    def create_entry(self, parent):
        """Create a styled entry widget"""
        entry = tk.Entry(
            parent,
            font=("SF Pro Display", 12),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=0
        )
        return entry
    
    def create_quality_row(self, parent, row):
        """Create quality/compression slider"""
        row_frame = tk.Frame(parent, bg=GlassStyle.BG_GLASS)
        row_frame.grid(row=row, column=0, sticky="ew", pady=8)
        
        label = tk.Label(
            row_frame,
            text="Quality:",
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            width=15,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        slider_frame = tk.Frame(row_frame, bg=GlassStyle.BG_GLASS)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.quality_var = tk.IntVar(value=95)
        
        quality_slider = tk.Scale(
            slider_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=GlassStyle.BORDER,
            activebackground=GlassStyle.ACCENT,
            font=("SF Pro Display", 10)
        )
        quality_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.quality_label = tk.Label(
            slider_frame,
            text="95%",
            font=("SF Pro Display", 12, "bold"),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.ACCENT,
            width=5
        )
        self.quality_label.pack(side=tk.LEFT)
        
        quality_slider.configure(command=self.update_quality_label)
        
    def create_max_size_row(self, parent, row):
        """Create max file size option"""
        row_frame = tk.Frame(parent, bg=GlassStyle.BG_GLASS)
        row_frame.grid(row=row, column=0, sticky="ew", pady=8)
        
        self.use_max_size = tk.BooleanVar(value=False)
        
        check = tk.Checkbutton(
            row_frame,
            text="Max File Size (KB):",
            variable=self.use_max_size,
            font=("SF Pro Display", 13),
            bg=GlassStyle.BG_GLASS,
            fg=GlassStyle.TEXT_PRIMARY,
            activebackground=GlassStyle.BG_GLASS,
            selectcolor=GlassStyle.BG_GLASS,
            width=15,
            anchor="w",
            command=self.toggle_max_size
        )
        check.pack(side=tk.LEFT)
        
        self.max_size_entry = self.create_entry(row_frame)
        self.max_size_entry.insert(0, "500")
        self.max_size_entry.configure(state="disabled")
        self.max_size_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg=GlassStyle.BG_PRIMARY)
        button_frame.pack(fill=tk.X)
        
        # Process button (centered)
        self.process_btn = tk.Button(
            button_frame,
            text="Process & Save Image",
            font=("SF Pro Display", 14, "bold"),
            bg=GlassStyle.ACCENT,
            fg="white",
            activebackground="#0051D5",
            relief=tk.FLAT,
            borderwidth=0,
            padx=40,
            pady=14,
            cursor="hand2",
            state="disabled",
            command=self.process_image
        )
        self.process_btn.pack(expand=True)
        
    def update_quality_label(self, value):
        """Update quality percentage label"""
        self.quality_label.config(text=f"{int(float(value))}%")
        
    def toggle_max_size(self):
        """Toggle max file size entry"""
        if self.use_max_size.get():
            self.max_size_entry.configure(state="normal")
        else:
            self.max_size_entry.configure(state="disabled")
            
    def on_aspect_change(self, event=None):
        """Handle aspect ratio selection change"""
        aspect = self.aspect_var.get()
        
        # Hide both custom frames first
        self.custom_pixels_frame.grid_remove()
        self.custom_ratio_frame.grid_remove()
        
        if aspect == "Custom (pixels)":
            self.custom_pixels_frame.grid(row=4, column=0, sticky="ew", pady=8)
            if self.current_image:
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.current_image.width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.current_image.height))
        elif aspect == "Custom (ratio)":
            self.custom_ratio_frame.grid(row=4, column=0, sticky="ew", pady=8)
            
    def select_image(self):
        """Open file dialog to select image"""
        filetypes = [
            ("All Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("WebP", "*.webp"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff *.tif"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.image_path = filename
                self.current_image = Image.open(filename)
                
                # Update file path label with truncated filename
                file_name = os.path.basename(filename)
                if len(file_name) > 40:
                    file_name = file_name[:37] + "..."
                self.file_path_label.configure(
                    text=file_name,
                    fg=GlassStyle.TEXT_PRIMARY
                )
                
                self.display_preview()
                self.process_btn.configure(state="normal")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")
                
    def display_preview(self):
        """Display image preview"""
        if self.current_image:
            # Calculate preview size (max 280x280)
            img_copy = self.current_image.copy()
            img_copy.thumbnail((280, 280), Image.Resampling.LANCZOS)
            
            self.preview_image = ImageTk.PhotoImage(img_copy)
            self.preview_label.configure(
                image=self.preview_image,
                text="",
                bg=GlassStyle.BG_GLASS
            )
            
    def calculate_new_dimensions(self):
        """Calculate new dimensions based on aspect ratio"""
        if not self.current_image:
            return None, None
            
        aspect = self.aspect_var.get()
        original_w, original_h = self.current_image.size
        
        if aspect == "Original":
            return original_w, original_h
        elif aspect == "Custom (pixels)":
            try:
                w = int(self.width_entry.get())
                h = int(self.height_entry.get())
                return w, h
            except ValueError:
                return original_w, original_h
        elif aspect == "Custom (ratio)":
            try:
                ratio_w = int(self.ratio_width_entry.get())
                ratio_h = int(self.ratio_height_entry.get())
                
                # Calculate dimensions maintaining custom aspect ratio
                if original_w / original_h > ratio_w / ratio_h:
                    new_h = original_h
                    new_w = int(new_h * ratio_w / ratio_h)
                else:
                    new_w = original_w
                    new_h = int(new_w * ratio_h / ratio_w)
                    
                return new_w, new_h
            except (ValueError, ZeroDivisionError):
                return original_w, original_h
        else:
            # Parse aspect ratio
            ratio_w, ratio_h = map(int, aspect.split(':'))
            
            # Calculate dimensions maintaining aspect ratio
            if original_w / original_h > ratio_w / ratio_h:
                new_h = original_h
                new_w = int(new_h * ratio_w / ratio_h)
            else:
                new_w = original_w
                new_h = int(new_w * ratio_h / ratio_w)
                
            return new_w, new_h
            
    def process_image(self):
        """Process and save the image"""
        if not self.current_image:
            return
            
        # Get save location
        format_map = {
            "JPEG": [("JPEG", "*.jpg"), ("All Files", "*.*")],
            "PNG": [("PNG", "*.png"), ("All Files", "*.*")],
            "WEBP": [("WebP", "*.webp"), ("All Files", "*.*")],
            "BMP": [("BMP", "*.bmp"), ("All Files", "*.*")],
            "TIFF": [("TIFF", "*.tiff"), ("All Files", "*.*")]
        }
        
        output_format = self.format_var.get()
        default_ext = {
            "JPEG": ".jpg",
            "PNG": ".png",
            "WEBP": ".webp",
            "BMP": ".bmp",
            "TIFF": ".tiff"
        }
        
        filename = filedialog.asksaveasfilename(
            title="Save processed image",
            defaultextension=default_ext[output_format],
            filetypes=format_map[output_format]
        )
        
        if not filename:
            return
            
        try:
            # Calculate new dimensions
            new_w, new_h = self.calculate_new_dimensions()
            
            # Resize image
            if (new_w, new_h) != self.current_image.size:
                processed = self.current_image.resize(
                    (new_w, new_h),
                    Image.Resampling.LANCZOS
                )
            else:
                processed = self.current_image.copy()
            
            # Convert to RGB if saving as JPEG
            if output_format == "JPEG" and processed.mode in ("RGBA", "P", "LA"):
                rgb_image = Image.new("RGB", processed.size, (255, 255, 255))
                if processed.mode == "P":
                    processed = processed.convert("RGBA")
                rgb_image.paste(processed, mask=processed.split()[-1] if processed.mode in ("RGBA", "LA") else None)
                processed = rgb_image
            
            # Save with quality settings
            quality = self.quality_var.get()
            
            if output_format in ["JPEG", "WEBP"]:
                if self.use_max_size.get():
                    # Iteratively reduce quality to meet max file size
                    max_size_kb = int(self.max_size_entry.get())
                    current_quality = quality
                    
                    while current_quality > 10:
                        processed.save(filename, format=output_format, quality=current_quality, optimize=True)
                        file_size_kb = os.path.getsize(filename) / 1024
                        
                        if file_size_kb <= max_size_kb:
                            break
                        current_quality -= 5
                else:
                    processed.save(filename, format=output_format, quality=quality, optimize=True)
            else:
                processed.save(filename, format=output_format)
            
            messagebox.showinfo(
                "Success",
                f"Image saved successfully!\n\nLocation: {filename}\nSize: {os.path.getsize(filename) / 1024:.1f} KB"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image:\n{str(e)}")

def main():
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
