from model import Yolo_SAHI
from layout import Interface

# Crear instancia de Interfaz y obtener las rutas y resolución
interface_controller = Interface()
images_folder_path, path_model, resolution ,results_path= interface_controller.get_paths_and_resolution()

# Verificar que ambas rutas y resolución han sido seleccionadas
if images_folder_path and path_model:
    # Crear objeto SAHI con la ruta del modelo, carpeta de imágenes y resolución
    sahi = Yolo_SAHI(model_path=path_model, images_folder_path=images_folder_path, resolution=resolution,results_path=results_path)

    # Procesar todas las imágenes en la carpeta y obtener el número de imágenes procesadas y archivos generados
    processed_image_count, json_count, kml_count = sahi.process_folder()


    # Mostrar ventana de resultados con el número de imágenes procesadas, JSON y KML generados
    interface_controller.mostrar_resultados(processed_image_count, json_count, kml_count)
else:
     print("No se seleccionaron todas las rutas necesarias para el procesamiento.")
