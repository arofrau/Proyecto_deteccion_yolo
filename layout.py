import tkinter as tk
from tkinter import filedialog, Scrollbar
from PIL import Image, ImageTk
import os

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interfaz de Detección de Imágenes")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f7")

        # Variables para almacenar las rutas y la resolución
        self.image_folder_path = None
        self.model_path = None
        self.result_path = None
        self.thumbnail_size = (100, 100)
        self.model_resolution = tk.IntVar(value=1760)
        self.create_scrollable_frame()

        # Crear elementos de la interfaz
        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self.scrollable_frame, bg="#2d6a4f")
        header_frame.pack(fill="x")

        label = tk.Label(
            header_frame, text="Seleccione los archivos necesarios:",
            font=("Helvetica", 14, "bold"), fg="white", bg="#2d6a4f", padx=10, pady=10
        )
        label.pack()

        main_frame = tk.Frame(self.scrollable_frame, bg="#f0f4f7", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Botón para seleccionar la carpeta de imágenes
        image_folder_button = tk.Button(
            main_frame, text="📁 Seleccionar carpeta de imágenes", font=("Helvetica", 11),
            command=self.get_image_folder, bg="#ffcb77", fg="#2d3142", relief="groove", cursor="hand2"
        )
        image_folder_button.pack(pady=10, fill="x")

        self.image_folder_label = tk.Label(main_frame, text="Carpeta de imágenes no seleccionada", fg="gray",
                                           bg="#f0f4f7", font=("Helvetica", 10, "italic"))
        self.image_folder_label.pack()

        # Frame para el Canvas y la Scrollbar
        self.scroll_frame = tk.Frame(main_frame)
        self.scroll_frame.pack(pady=10)

        # Canvas para mostrar miniaturas de imágenes en la carpeta
        self.thumbnail_canvas = tk.Canvas(self.scroll_frame, bg="#e0e0e0")
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = Scrollbar(self.scroll_frame, orient="vertical", command=self.thumbnail_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self.thumbnail_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Botón para seleccionar el modelo
        model_button = tk.Button(
            main_frame, text="📄 Seleccionar modelo (.pt)", font=("Helvetica", 11),
            command=self.get_model_path, bg="#ffcb77", fg="#2d3142", relief="groove", cursor="hand2"
        )
        model_button.pack(pady=10, fill="x")

        self.model_label = tk.Label(main_frame, text="Modelo no seleccionado", fg="gray", bg="#f0f4f7",
                                    font=("Helvetica", 10, "italic"))
        self.model_label.pack()

        # Botón para seleccionar donde ira la carpeta de resultados
        result_path_button = tk.Button(
            main_frame, text="📁 Seleccionar carpeta de resultados", font=("Helvetica", 11),
            command=self.get_resultados_path, bg="#ffcb77", fg="#2d3142", relief="groove", cursor="hand2"
        )
        result_path_button.pack(pady=10, fill="x")

        self.result_path_label = tk.Label(main_frame, text="Carpeta de resultados no seleccionada", fg="gray",
                                          bg="#f0f4f7", font=("Helvetica", 10, "italic"))
        self.result_path_label.pack()
        ####

        resolution_label = tk.Label(main_frame, text="Resolución de entrenamiento del modelo:", bg="#f0f4f7",
                                    font=("Helvetica", 11))
        resolution_label.pack(pady=5)
        resolution_entry = tk.Entry(main_frame, textvariable=self.model_resolution, font=("Helvetica", 10),
                                    justify="center")
        resolution_entry.pack(pady=5)

        self.confirm_button = tk.Button(
            main_frame, text="✅ Confirmar selección", font=("Helvetica", 12, "bold"),
            command=self.confirm_selection, state=tk.DISABLED, bg="#007f5f", fg="white", relief="ridge", cursor="hand2"
        )
        self.confirm_button.pack(pady=20, fill="x")

    def get_image_folder(self):
        # Seleccionar carpeta con askdirectory
        folder_path = filedialog.askdirectory(title="Selecciona la carpeta con imágenes")
        if folder_path:
            self.image_folder_path = folder_path
            self.image_folder_label.config(text=self.truncate_path(folder_path), fg="black")
            self.display_image_thumbnails(folder_path)
            self.check_paths()

    def display_image_thumbnails(self, folder_path):
        # Limpiar el Canvas
        self.thumbnail_canvas.delete("all")

        # Obtener archivos de imagen en la carpeta
        image_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
        ]

        # Cargar y mostrar miniaturas en el Canvas
        x, y = 10, 10
        self.thumbnails = []
        for image_file in image_files:
            img = Image.open(image_file)
            img.thumbnail(self.thumbnail_size)
            img_tk = ImageTk.PhotoImage(img)
            self.thumbnails.append(img_tk)  # Necesario para mantener una referencia a las imágenes

            # Dibujar cada imagen en el Canvas
            self.thumbnail_canvas.create_image(x, y, anchor="nw", image=img_tk)
            x += self.thumbnail_size[0] + 10  # Desplazar a la derecha

            # Si se llega al final de la fila, iniciar nueva fila
            if x > self.thumbnail_canvas.winfo_width() - self.thumbnail_size[0]:
                x = 10
                y += self.thumbnail_size[1] + 10

        # Configurar el tamaño del Canvas
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox("all"))

    def get_model_path(self):
        file_path = filedialog.askopenfilename(title="Selecciona el modelo", filetypes=[("Modelos YOLO", "*.pt")])
        if file_path:
            self.model_path = file_path
            self.model_label.config(text=self.truncate_path(file_path), fg="black")
            self.check_paths()

    def get_resultados_path(self):
        folder_path = filedialog.askdirectory(title="Selecciona la carpeta base para resultados")
        if folder_path:
            self.result_path = self.create_result_folder(folder_path)
            self.result_path_label.config(text=self.truncate_path(self.result_path), fg="black")
            self.check_paths()

    def create_result_folder(self, base_path):
        """
        Crea una carpeta 'result' en la ubicación seleccionada.
        Si 'result' ya existe, crea 'result1', 'result2', etc.
        """
        base_folder_name = "result"
        folder_path = os.path.join(base_path, base_folder_name)

        # Incrementar sufijo si ya existe la carpeta
        counter = 0
        while os.path.exists(folder_path):
            counter += 1
            folder_path = os.path.join(base_path, f"{base_folder_name}{counter}")

        # Crear la carpeta final
        os.makedirs(folder_path)
        print(f"Carpeta de resultados creada: {folder_path}")
        return folder_path

    def check_paths(self):
        if self.image_folder_path and self.model_path:
            self.confirm_button.config(state=tk.NORMAL)

    def confirm_selection(self):
        if self.image_folder_path and self.model_path:
            self.root.quit()

    def truncate_path(self, path, max_length=40):
        if len(path) > max_length:
            return '...' + path[-max_length:]
        return path

    def get_paths_and_resolution(self):
        self.root.mainloop()
        return self.image_folder_path, self.model_path, self.model_resolution.get(), self.result_path

    def create_scrollable_frame(self):
        # Crear un canvas y un frame para el contenido scrollable
        self.canvas = tk.Canvas(self.root, bg="#f0f4f7", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f4f7")

        # Configurar scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empaquetar canvas y scrollbar
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Crear un window dentro del canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Ajustar el tamaño del frame cuando cambien los contenidos
        self.scrollable_frame.bind(
            "<Configure>",
            self._on_frame_configure
        )

        # Ajustar el ancho del canvas al redimensionar la ventana
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )

        # Permitir scroll con el mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _on_frame_configure(self, event):
        # Ajustar el área del scrollable_frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def _on_canvas_configure(self, event):
        # Ajustar el ancho del frame al tamaño del canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Habilitar scroll con la rueda del mouse
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def mostrar_resultados(self, processed_image_count, json_count, kml_count):
        resultado_root = tk.Toplevel(self.root)
        resultado_root.title("Resultados del Procesamiento")
        resultado_root.geometry("400x250")
        resultado_root.configure(bg="#dff9fb")

        title_label = tk.Label(resultado_root, text="¡Procesamiento Completado!", font=("Helvetica", 14, "bold"),
                               bg="#dff9fb", fg="#130f40")
        title_label.pack(pady=10)

        details_text = (
            f"Se han generado los siguientes archivos:\n\n"
            f"Imágenes procesadas: {processed_image_count}\n"
            f"Archivos JSON generados: {json_count}\n"
            f"Archivos KML generados: {kml_count}\n\n"
            "Puedes encontrarlos en la carpeta de resultados."
        )
        details_label = tk.Label(resultado_root, text=details_text, font=("Helvetica", 10), bg="#dff9fb", fg="#30336b",
                                 justify="left")
        details_label.pack(pady=10)

        close_button = tk.Button(resultado_root, text="Cerrar",
                                 command=lambda: [resultado_root.destroy(), self.root.destroy()],
                                 font=("Helvetica", 12), bg="#130f40", fg="white")
        close_button.pack(pady=10)

        resultado_root.mainloop()