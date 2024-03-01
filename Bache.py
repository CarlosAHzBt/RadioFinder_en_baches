import numpy as np
import cv2 as cv
import os
import matplotlib.pyplot as plt
from ConvertirPixelesAMetros import ConvertirPixelesAMetros
from FiltrosDeProcesamiento.FiltrosDeProcesamiento import PointCloudFilter
from FiltrosDeProcesamiento.Ransac import RANSAC
from FiltrosDeProcesamiento.FIltroOutliers import FiltroOutliers
import open3d as o3d

class Bache:
    def __init__(self, bag_de_origen, imagenRGB, id_bache, coordenadas=None):
        self.id_bache = id_bache
        self.imagen_original_shape = (480, 848)  # Pasar la forma de la imagen original al inicializar
        self.bag_de_origen = bag_de_origen
        self.ruta_nube_puntos = None
        self.imagenRGB = imagenRGB
        self.coordenadas = np.array(coordenadas)[:, [1, 0]] if coordenadas is not None else np.empty((0, 2), dtype=int)
        self.radio_maximo = 0
        self.diametro_bache = 0
        self.centro_circulo = (0, 0)
        self.profundidad_del_bache=0

        self.ConvPx2M = ConvertirPixelesAMetros()
        self.altura_captura = 0
        self.escale_horizontal = 0
        self.escala_vertical = 0

        self.nube_puntos = None
        self.nube_puntos_procesada = None
        self.ransac = RANSAC()
        self.filtro_outliers = FiltroOutliers()
        self.point_cloud_filter = PointCloudFilter()

    def get_id_bache(self):
        return self.id_bache

    def set_imagenRGB(self):
        self.imagenRGB = os.path.join(self.bag_de_origen, "Imagen", "rgbimage.png")

    def set_ruta_nube_puntos(self):
        nombre_archivo_sin_extension = self.id_bache[:-2]
        ruta_nube_puntos = os.path.join(self.bag_de_origen, "PLY", f"{nombre_archivo_sin_extension}.ply")
        if os.path.exists(ruta_nube_puntos):
            self.ruta_nube_puntos = ruta_nube_puntos
        else:
            print(f"No se encontró la nube de puntos para {self.imagenRGB}")

    def calcular_contorno(self):
        if self.coordenadas.size == 0:
            raise ValueError("No hay coordenadas para calcular el contorno.")
        mask = np.zeros(self.imagen_original_shape[:2], dtype=np.uint8)
        for x, y in self.coordenadas:
            mask[y ,x] = 255
        contornos, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        contorno_externo = max(contornos, key=cv.contourArea).squeeze()
        if contorno_externo.ndim == 1:
            contorno_externo = contorno_externo.reshape(-1, 1, 2)
        self.contorno = contorno_externo

    def calcular_radio_maximo(self):
        if len(self.contorno) == 0:
            raise ValueError("El contorno debe ser calculado antes de calcular el radio máximo.")
        imagen_contorno = np.zeros(self.imagen_original_shape[:2], dtype=np.uint8)
        cv.drawContours(imagen_contorno, [self.contorno], -1, color=255, thickness=-1)
        puntos_dentro_del_contorno = np.argwhere(imagen_contorno == 255)
        for punto in puntos_dentro_del_contorno:
            dist = cv.pointPolygonTest(self.contorno, (int(punto[1]), int(punto[0])), True)
            if dist > self.radio_maximo:
                self.radio_maximo = dist
                self.centro_circulo = (int(punto[1]), int(punto[0]))
        if self.radio_maximo == 0:
            raise ValueError("No se encontraron puntos dentro del contorno para calcular el radio máximo.")
        self.set_ruta_nube_puntos()
        self.set_altura_captura(self.ruta_nube_puntos)
        self.ConvPx2M.calcular_escala(self.altura_captura)
        self.set_escala_horizontal()
        self.radio_maximo = self.ConvPx2M.convertir_radio_pixeles_a_metros(self.radio_maximo, self.escale_horizontal)
        self.radio_maximo *= 1000
        self.get_diametro_bache()

    def procesar_nube_puntos(self):
        self._cargar_nube_puntos()
        if self.nube_puntos is None:
            print("Nube de puntos no cargada.")
            return
        pcd_nivelado, plano = self.ransac.procesar_nube_completa(self.nube_puntos)
        self.nube_puntos_procesada = pcd_nivelado
        #Estimar altura de captura de la nube de puntos nivelada
        self.set_altura_captura(self.ruta_nube_puntos)
        self.convertir_coordenadas_contorno_a_metros_y_centrar()
        self.point_cloud_filter.visuzlizar_imgen_rgb(self.imagenRGB, self.coordenadas_contorno_metros_centro)
        self.nube_puntos_procesada = self.point_cloud_filter.filter_points_with_bounding_box(self.nube_puntos, self.coordenadas_contorno_metros_centro)
        print("El tamaño de la nube de puntos es: ", len(self.nube_puntos_procesada.points))
        return self.nube_puntos_procesada

    def _cargar_nube_puntos(self):
        self.nube_puntos = o3d.io.read_point_cloud(self.ruta_nube_puntos)

    def set_altura_captura(self,nube_puntos):
        self.altura_captura = self.ConvPx2M.estimar_altura_de_captura(nube_puntos)

    def set_escala_horizontal(self):
         self.escale_horizontal, self.escala_vertical = self.ConvPx2M.calcular_escala(self.altura_captura)

    def get_diametro_bache(self):
        self.diametro_bache = self.radio_maximo * -2
        return self.diametro_bache

    def convertir_coordenadas_contorno_a_metros_y_centrar(self):
        ancho_imagen, alto_imagen = self.imagen_original_shape[1], self.imagen_original_shape[0]
        centro_x, centro_y = ancho_imagen / 2, alto_imagen / 2
        coordenadas_contorno_metros_centro = []
        for punto in self.contorno:
            x_centro = punto[0] - centro_x
            y_centro = punto[1] - centro_y
            x_metros = x_centro * self.escale_horizontal
            y_metros = y_centro * self.escala_vertical 
            coordenadas_contorno_metros_centro.append([x_metros, y_metros])
        self.coordenadas_contorno_metros_centro = coordenadas_contorno_metros_centro
        #Dibujar ambas coordenadas en una imagen tanto del contorno como de las coordenadas en metros
        #imagen_contorno = np.zeros(self.imagen_original_shape[:2], dtype=np.uint8)
        #cv.drawContours(imagen_contorno, [self.contorno], -1, color=255, thickness=1)
        #imagen_contorno_metros = np.zeros(self.imagen_original_shape[:2], dtype=np.uint8)
        #for punto in self.coordenadas_contorno_metros_centro:
        #    x = int(punto[0] / self.escale_horizontal + centro_x)
        #    y = int(punto[1] / self.escala_vertical + centro_y)
        #    imagen_contorno_metros[y, x] = 255
        #plt.figure()
        #plt.subplot(1, 2, 1)
        #plt.imshow(imagen_contorno, cmap="gray")
        #plt.title("Contorno")
        #plt.subplot(1, 2, 2)
        #plt.imshow(imagen_contorno_metros, cmap="gray")
        #plt.title("Contorno en metros")
        #plt.show()
        

    def visualizar_nube_de_puntos(self, pcd):
        o3d.visualization.draw_geometries([pcd])

    def estimar_profundidad(self):
        #self.visualizar_nube_de_puntos(self.nube_puntos_procesada)
        #Se hace una resta entre la altura de captura y el punto con menor valor en el eje Z de la nube de puntos
        puntos = np.asarray(self.nube_puntos_procesada.points)
        #Ver nube de puntos procesada
        self.visualizar_nube_de_puntos(self.nube_puntos_procesada)
        #Se abre la nube de putnos procesada y se obtiene el punto con menor valor en el eje Z
        if puntos.size > 0:
            minimo = np.min(puntos[:, 2])
        else:
            print("El array puntos está vacío.")
        minimo = None
        minimo = np.min(puntos[:, 2])
        #Se hace la resta
        self.profundidad_del_bache = self.altura_captura - minimo

    