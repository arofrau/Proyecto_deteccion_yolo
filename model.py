import os
import cv2
from sahi.models.yolov8 import Yolov8DetectionModel
from sahi.predict import get_sliced_prediction, get_prediction
from sahi.utils.file import save_json
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import simplekml
from geolocalitation import Geolocation

class Yolo_SAHI:
    def __init__(self, model_path,images_folder_path,resolution,results_path):
        self.model_path = model_path
        self.images_folder_path = images_folder_path
        self.resolution = resolution  # Almacenar la resolución de entrenamiento
        self.results_path = results_path

        self.processed_image_count = 0 # Contador de imagenes predecidas generadas
        self.json_count = 0  # Contador de archivos JSON generados
        self.kml_count = 0  # Contador de archivos KML generados

        self.dpi = 96

    def get_PixelCentral(self,image_path):
        image_Calculated = cv2.imread(image_path)
        height, width = image_Calculated.shape[:2]
        center_x = width // 2
        center_y = height // 2
        print(f"Width: {width} pixels")
        print(f"Height: {height} pixels")
        return width, height, center_x, center_y

    def crear_resultados(self):
        if not os.path.exists(self.results_path):
            os.makedirs(self.results_path)

    def process_image(self, image_path):
        yolo_model = Yolov8DetectionModel(
            model_path=self.model_path,
            confidence_threshold=0.3,
            device='cuda'
        )
        image = Image.open(image_path)
        img_height, img_width = image.size

        slice_height = self.resolution
        slice_width = int(self.resolution * img_width / img_height)

        # print(f"Dimensiones de la imagen: {img_width}x{img_height}")
        # print(f"Dimensiones del slice: {slice_width}x{slice_height}")

        if img_height <= slice_height and img_width <= slice_width:
            # print("La imagen es más pequeña o igual al tamaño de entrenamiento, usando detección sin SAHI.")
            result = get_prediction(
                image=image_path,
                detection_model=yolo_model
            )
        else:
            # print("Usando SAHI para segmentar la imagen.")
            result = get_sliced_prediction(
                image=image_path,
                detection_model=yolo_model,
                slice_height=slice_height,
                slice_width=slice_width,
                overlap_height_ratio=0.2,
                overlap_width_ratio=0.2
            )

        self.processed_image_count += 1

        output_json_path = os.path.join(self.results_path, f"{os.path.splitext(os.path.basename(image_path))[0]}.json")
        save_json(result.to_coco_annotations(), output_json_path)
        self.json_count += 1



        draw = ImageDraw.Draw(image)
        for prediction in result.object_prediction_list:
            bbox = prediction.bbox
            minx, miny, maxx, maxy = int(bbox.minx), int(bbox.miny), int(bbox.maxx), int(bbox.maxy)
            draw.rectangle([(minx, miny), (maxx, maxy)], outline="red", width=3)

            # Crear un fondo semi-transparente para el texto
            text_label = f"{prediction.category}: {prediction.score.value:.2f}"
            # Obtener el cuadro delimitador del texto
            bbox_text = draw.textbbox((minx, miny - 10), text_label)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]

            background_box = [(minx, miny - text_height - 5), (minx + text_width, miny)]

            # Dibujar el fondo del texto
            draw.rectangle(background_box, fill=(255, 0, 0, 128))  # Fondo rojo semi-transparente
            draw.text((minx, miny - text_height - 5), text_label, fill="white")  # Cambiar a texto blanco

        output_image_path = os.path.join(self.results_path, f"predictions_{os.path.basename(image_path)}")
        image.save(output_image_path)

        if self.calculo_coordenadas(result, image, img_width, img_height):
            self.kml_count += 1

    def calculo_coordenadas(self, result, image, ancho, alto):
        kml = simplekml.Kml()
        coordenadas_geograficas = []

        for prediction in result.object_prediction_list:
            bbox = prediction.bbox
            minx, miny, maxx, maxy = int(bbox.minx), int(bbox.miny), int(bbox.maxx), int(bbox.maxy)
            center_x = (minx + maxx) // 2
            center_y = (miny + maxy) // 2
            lon = center_x - ancho
            lat = center_y - alto

            try:
                geo = Geolocation(image, lon, lat)
                coordenadas_lat, coordenadas_lon = geo.obtener_geolocalizacion()

                if coordenadas_lat is not None and coordenadas_lon is not None:
                    coordenadas_geograficas.append((coordenadas_lat, coordenadas_lon))

            except Exception as e:
                print(f"Advertencia: No se pudo calcular la geolocalización. Error: {e}")
                return False

        if coordenadas_geograficas:
            for lat, lon in coordenadas_geograficas:
                kml.newpoint(name="Predicción", coords=[(lon, lat)])

            kml_path = os.path.join(self.results_path, f"coordenadas_{os.path.splitext(os.path.basename(image.filename))[0]}.kml")
            kml.save(kml_path)
            # print(f"Archivo KML guardado: {kml_path}")
            return True

        return False

    def visualize_predictions(self, imagen_np, predictions):
        # Convertir la imagen de NumPy (cv2) a PIL
        image_pil = Image.fromarray(cv2.cvtColor(imagen_np, cv2.COLOR_BGR2RGB))

        # Obtener dimensiones desde PIL
        plt.figure(figsize=(image_pil.width / self.dpi, image_pil.height / self.dpi), dpi=self.dpi)

        # Dibujar las predicciones en la imagen
        for prediction in predictions:
            bbox = prediction.bbox
            pt1 = (int(bbox.minx), int(bbox.miny))
            pt2 = (int(bbox.maxx), int(bbox.maxy))
            cv2.rectangle(imagen_np, pt1, pt2, (255, 0, 0), 2)
            label = f"{prediction.category}: {prediction.score.value:.2f}"
            cv2.putText(imagen_np, label, pt1, cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        plt.imshow(imagen_np)
        plt.axis('off')
        plt.show()

    def save_subimages(self,image, output_path, slice_height=1760, slice_width=1318):
        self.crear_resultados()
        img_width, img_height = image.size

        for i in range(0, img_height, slice_height):
            for j in range(0, img_width, slice_width):
                box = (j, i, j + slice_width, i + slice_height)
                subimage = image.crop(box)
                subimage_path = os.path.join(output_path, f"subimage_{i}_{j}.jpg")
                subimage.save(subimage_path)

    def process_folder(self):
        # Crear carpeta de resultados
        self.crear_resultados()

        # Recorrer todas las imágenes en la carpeta
        for filename in os.listdir(self.images_folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_path = os.path.join(self.images_folder_path, filename)
               # print(f"Procesando imagen: {image_path}")
                self.process_image(image_path)
        return self.processed_image_count, self.json_count, self.kml_count