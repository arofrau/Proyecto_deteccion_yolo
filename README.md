# Detección de objetos y geolocalización
Este proyecto emplea las librerias ultralytics y los modelos YOLOv8 y YOLOv11 para detectar objetos, en este caso naranjas, y posteriormente geolocalizarlos.

El dataset empleado esta formado de 350 imagenes recortadas a una resolución de 1760x1318.

## Modelos
Los se entrenaron con una resolción de 1760, con un batch_size de 16 y por 350 epocas.
Tras el entrenamiento estos son los resultados

| Modelos  | Accuracy | Recall | Precision  | F1 Score  |
|------------|------------|------------|------------|------------|
| Yolov8 | 0.74 | 0.78 | 0.77 | 0.77 |
| Yolov11 | 0.81 | 0.88 | 0.81 | 0.84 |

## Codigo de detección[Yolo_Sahi] 
Este script se utiliza para procesar imágenes en una carpeta, detectando objetos usando el modelo YOLOv8. Si la imagen es demasiado grande, se segmenta en subimágenes utilizando SAHI para evitar que el modelo se quede sin memoria. Los resultados se guardan en formato JSON y KML, con información sobre las coordenadas geográficas asociadas a las predicciones.
### Componentes y Funciones:

  ### Yolo_SAHI Class

#### `__init__(self, model_path, images_folder_path, resolution, results_path)`
Inicializa los parámetros como la ruta del modelo YOLOv8, la carpeta de imágenes, la resolución de los "slices" y la carpeta para guardar los resultados.

#### `get_PixelCentral(image_path)`
Calcula y devuelve el centro de la imagen, así como sus dimensiones en píxeles.

#### `crear_resultados()`
Crea la carpeta de resultados si no existe.

#### `process_image(image_path)`
Procesa una imagen, realizando la predicción de objetos y guardando los resultados en formato JSON. Si la imagen es demasiado grande, se segmenta y se utiliza SAHI para obtener las predicciones.

#### `calculo_coordenadas(result, image, ancho, alto)`
Calcula las coordenadas geográficas de las predicciones utilizando la clase `Geolocation`, y guarda las coordenadas en un archivo KML.

#### `visualize_predictions(imagen_np, predictions)`
Muestra las predicciones sobre la imagen utilizando `matplotlib`, dibujando los cuadros delimitadores y las etiquetas de los objetos detectados.

#### `save_subimages(image, output_path, slice_height, slice_width)`
Divide la imagen en subimágenes de tamaño específico y las guarda en la carpeta de resultados.

#### `process_folder()`
Procesa todas las imágenes en la carpeta de entrada, llamando a la función `process_image` para cada una.
# Geolocation: Geolocalización y Mapa con EXIF y UTM

La clase `Geolocation` se utiliza para extraer datos GPS de una imagen, calcular las coordenadas UTM a partir de las coordenadas geográficas y generar un mapa con los límites de la imagen utilizando Google Maps. Es útil para obtener información geolocalizada de imágenes y mostrar la ubicación de las esquinas de una imagen aérea o satelital.
## Descripción de la Clase

###  `__init__(self, imagen, pixels_ancho, pixels_alto)`
El constructor de la clase recibe la imagen (con datos EXIF de GPS) y las dimensiones de la imagen en píxeles (ancho y alto). Estos valores son utilizados para calcular las coordenadas geográficas y los límites de la imagen.

### `convertir_a_grados(val)`
Convierte una tupla de grados, minutos y segundos (DMS) en grados decimales. Esta conversión es necesaria para interpretar los datos GPS extraídos de los EXIF de la imagen.

###  `conseguir_datos_exif()`
Extrae los datos EXIF de la imagen, específicamente la información de GPS (latitud y longitud). Si no se encuentran los datos, devuelve `None` para ambas coordenadas.

###  `calcular_utm(lat, lon)`
Convierte las coordenadas geográficas (latitud y longitud) a coordenadas UTM (Universal Transverse Mercator). Esto se utiliza para obtener una representación más precisa de las ubicaciones en el sistema UTM.

###  `calcular_extremos(altura_dron, angulo, pixels_ancho, pixels_alto)`
Calcula los extremos de la imagen, es decir, las distancias desde el centro de la imagen hacia las esquinas, utilizando la altura del dron y el ángulo de visión. Este cálculo es esencial para determinar cómo se proyecta la imagen en el terreno.

###.`calcular_esquinas(utm_x, utm_y, anchuraMxP, alturaMxP)`
Calcula las coordenadas UTM de las cuatro esquinas de la imagen, a partir de la posición central (utm_x, utm_y) y el tamaño de la imagen en metros por píxel.

###  `obtener_geolocalizacion()`
Obtiene la geolocalización de la imagen al extraer los datos EXIF, calcular las coordenadas UTM y determinar las esquinas de la imagen en el sistema de coordenadas WGS84 (latitud y longitud). Devuelve las coordenadas de la última esquina.

###  `generar_mapa(lat, lon, esquinas)`
Genera un mapa utilizando la API de Google Maps, donde marca las esquinas de la imagen en diferentes colores  y traza un polígono conectando las esquinas. El mapa se guarda en un archivo `location.html`.

## Instalación de dependencias

Para instalar las dependencias necesarias para este proyecto, asegúrate de tener `pip` instalado y ejecuta el siguiente comando:


``pip install -r requirements.txt``


