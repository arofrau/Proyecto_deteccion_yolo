from gmplot import gmplot
from pyproj import Proj, transform
import math


class Geolocation:
    def __init__(self, imagen, pixels_ancho, pixels_alto):
        self.imagen = imagen
        self.pixels_ancho = pixels_ancho
        self.pixels_alto = pixels_alto

    @staticmethod
    def convertir_a_grados(val):
        return val[0] + (val[1] / 60.0) + (val[2] / 3600.0)

    def conseguir_datos_exif(self):
        try:
            exif_data = self.imagen._getexif()
            if not exif_data:
                raise ValueError("No se encontraron datos EXIF en la imagen.")

            gps_info = exif_data.get(34853)  # Tag para GPSInfo
            if not gps_info:
                raise ValueError("No se encontraron datos GPS en la imagen.")

            lat = self.convertir_a_grados(gps_info[2]) * (-1 if gps_info[1] == 'S' else 1)
            lon = self.convertir_a_grados(gps_info[4]) * (-1 if gps_info[3] == 'W' else 1)
            return lat, lon

        except Exception as e:
            print(f"Advertencia: {e}")
            return None, None

    def calcular_utm(self, lat, lon):
        zona_UTM = int((lon + 180) / 6) + 1
        wgs84 = Proj(proj='latlong', datum='WGS84')
        utm = Proj(proj='utm', zone=zona_UTM, datum='WGS84', south=lat < 0)
        return transform(wgs84, utm, lon, lat), utm

    @staticmethod
    def calcular_extremos(altura_dron, angulo, pixels_ancho, pixels_alto):
        distancia_extremo = altura_dron * math.tan(math.radians(angulo))
        extremo_x = distancia_extremo * math.cos(math.radians(36.87))
        extremo_y = distancia_extremo * math.sin(math.radians(36.87))
        return 2 * extremo_x / pixels_ancho, 2 * extremo_y / pixels_alto

    def calcular_esquinas(self, utm_x, utm_y, anchuraMxP, alturaMxP):
        offsets = [
            (-self.pixels_ancho / 2, self.pixels_alto / 2),
            (self.pixels_ancho / 2, self.pixels_alto / 2),
            (-self.pixels_ancho / 2, -self.pixels_alto / 2),
            (self.pixels_ancho / 2, -self.pixels_alto / 2),
        ]
        return [
            (utm_x + x * anchuraMxP, utm_y + y * alturaMxP)
            for x, y in offsets
        ]

    def obtener_geolocalizacion(self):
        lat, lon = self.conseguir_datos_exif()
        if lat is None or lon is None:
            return None, None

        (utm_x, utm_y), utm_proj = self.calcular_utm(lat, lon)
        anchuraMxP, alturaMxP = self.calcular_extremos(14, 42, self.pixels_ancho, self.pixels_alto)

        esquinas_utm = self.calcular_esquinas(utm_x, utm_y, anchuraMxP, alturaMxP)
        wgs84 = Proj(proj='latlong', datum='WGS84')
        esquinas_lat_lon = [transform(utm_proj, wgs84, x, y) for x, y in esquinas_utm]

        self.generar_mapa(lat, lon, esquinas_lat_lon)
        return esquinas_lat_lon[-1]

    def generar_mapa(self, lat, lon, esquinas):
        api_key = 'Your_api_key_here'
        gmap = gmplot.GoogleMapPlotter(lat, lon, 12, apikey=api_key)
        gmap.map_type = 'satellite'

        colores = ['green', 'blue', 'orange', 'red']
        for (lat_esquina, lon_esquina), color in zip(esquinas, colores):
            gmap.marker(lat_esquina, lon_esquina, color=color)

        gmap.plot(
            [lat for lat, _ in esquinas] + [esquinas[0][0]],
            [lon for _, lon in esquinas] + [esquinas[0][1]],
            color='blue', edge_width=2.5
        )
        gmap.draw("location.html")
