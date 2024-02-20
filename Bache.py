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
        self.imagen_original_shape = 480, 848  # Pasar la forma de la imagen original al inicializar
        self.bag_de_origen = bag_de_origen
        self.ruta_nube_puntos = None
        self.imagenRGB = imagenRGB
        self.coordenadas = np.array(coordenadas)[:, [1, 0]] if coordenadas is not None else np.empty((0, 2), dtype=int)
        # El id del bache es la ruta de la imagen pero solo el nombre del archivo "rgbimage.png" pero sin la extension
        self.radio_maximo = 0
        self.diametro_bache = 0
        self.centro_circulo = (0, 0)

        self.ConvPx2M = ConvertirPixelesAMetros()
        self.altura_captura = 0
        self.escale_horizontal = 0
        self.escala_vertical = 0

        #SeccionDeFiltros
        self.nube_puntos = None
        self.ransac = RANSAC()  # Instancia de RANSAC
        self.filtro_outliers = FiltroOutliers()  # Instancia de FiltroOutliers
        self.point_cloud_filter = PointCloudFilter()  # Instancia de PointCloudFilter



    def get_id_bache(self):
        return self.id_bache
        
    def set_imagenRGB(self):
        #apartir de la ruta de la bolsa de origen, se obtiene la ruta de la imagen RGB
        self.imagenRGB = self.bag_de_origen + "/Imagen"       
    def set_nube_puntos(self):
        # Construye la ruta de la nube de puntos
        # Asumiendo que `self.bag_de_origen` es la carpeta que contiene tanto la carpeta 'Imagen' como la carpeta 'PLY'
        # y que `self.imagenRGB` es solo el nombre del archivo con su extensión
        
        nombre_archivo_sin_extension = self.id_bache
        #quitarle el indice final al id del bache
        nombre_archivo_sin_extension = nombre_archivo_sin_extension[:-2]
        ruta_nube_puntos = os.path.join(self.bag_de_origen, "PLY", nombre_archivo_sin_extension + ".ply")
        
        if os.path.exists(ruta_nube_puntos):
            self.ruta_nube_puntos = ruta_nube_puntos
        else:
            print(f"No se encontró la nube de puntos para {self.imagenRGB}")





    def calcular_contorno(self):
        # Suponiendo que 'self.coordenadas' ya contiene las coordenadas del contorno del bache
        if self.coordenadas.size == 0:
            raise ValueError("No hay coordenadas para calcular el contorno.")
        
        # Crear una imagen en negro con las mismas dimensiones que la imagen original
        mask = np.zeros(self.imagen_original_shape[:2], dtype=np.uint8)


        #Colorear los puntos especificos en las coordenadas
        for x, y in self.coordenadas:
            mask[y ,x] = 255

        # Encontrar los contornos en la máscara
        contornos, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        # Seleccionar el contorno más grande (el contorno externo)
        contorno_externo = max(contornos, key=cv.contourArea).squeeze()
        if contorno_externo.ndim == 1:
            contorno_externo = contorno_externo.reshape(-1, 1, 2)
        self.contorno = contorno_externo
        

    def calcular_radio_maximo(self):
        if len(self.contorno) == 0:
            raise ValueError("El contorno debe ser calculado antes de calcular el radio máximo.")

        # Crea una imagen en negro con las mismas dimensiones que la imagen original
        imagen_contorno = np.zeros(self.imagen_original_shape[:2], dtype=np.uint8)

        # Rellenar el contorno para obtener todos los puntos dentro del bache
        cv.drawContours(imagen_contorno, [self.contorno], -1, color=255, thickness=-1)

        # Ahora self.contorno contiene todos los puntos dentro del bache.
        # Debemos encontrar el punto más alejado de cualquier borde, que será el centro del círculo máximo inscrito.
        # Esto se puede hacer buscando el punto más lejano dentro del contorno rellenado a los bordes del contorno original.
        # Se asume que self.contorno ya ha sido calculado y es el contorno externo del bache.
        
        # Encontrar todos los puntos dentro del contorno rellenado
        puntos_dentro_del_contorno = np.argwhere(imagen_contorno == 255)

        for punto in puntos_dentro_del_contorno:
            dist = cv.pointPolygonTest(self.contorno, (int(punto[1]), int(punto[0])), True)
            if dist > self.radio_maximo:
                self.radio_maximo = dist
                self.centro_circulo = (int(punto[1]), int(punto[0]))

        # Si después de iterar no se ha encontrado ningún punto dentro del contorno,
        # entonces hay un error en la lógica o en los datos del contorno
        if self.radio_maximo == 0:
            raise ValueError("No se encontraron puntos dentro del contorno para calcular el radio máximo.")
        

        self.set_nube_puntos()  # Obtener la ruta de la nube de puntos PLY
        # Finalmente, convertir el radio máximo de píxeles a metros
        self.set_altura_captura()   # Consigo la altura de captura de la nube de puntos PLY
        #altura, anchura = self.imagen_original_shape

        self.ConvPx2M.calcular_escala(self.altura_captura)  # Calculo las escalas de conversión de píxeles a metros basadas en la altura de captura.
        self.set_escala_horizontal()
        self.radio_maximo = self.ConvPx2M.convertir_radio_pixeles_a_metros(self.radio_maximo, self.escale_horizontal)
        
        #Convertir el radio maximo de a mm
        self.radio_maximo = self.radio_maximo * 1000
        
        self.get_diametro_bache()
        


    def procesar_nube_puntos(self):
            """
            Procesa la nube de puntos utilizando RANSAC para segmentar y nivelar el terreno.
            """
            self.cargar_nube_puntos()

            if self.nube_puntos is None:
                print("Nube de puntos no cargada.")
                return

            # Cargar la nube de puntos desde el archivo
            #pcd = self.nube_puntos
            # Procesa la nube de puntos completa con RANSAC
            pcd_nivelado, plano = self.ransac.procesar_nube_completa(self.nube_puntos)

            # Actualiza la nube de puntos de la instancia con la nube procesada y nivelada
            self.nube_puntos_procesada = pcd_nivelado
  
            #Aplicar filtro de ROI
            self.convertir_coordenadas_a_metros_y_crear_nube()
            self.convertir_coordenadas_contorno_a_metros_y_centrar()
            self.nube_puntos_procesada= self.point_cloud_filter.filter_points_with_contour(self.nube_puntos_procesada, self.coordenadas_contorno_metros_centro)
            print("El tamaño de la nube de puntos es: ", len(self.nube_puntos_procesada.points))

            #filtro de outliers
            #self.nube_puntos_procesada = self.filtro_outliers.eliminar_outliers(self.nube_puntos_procesada)
            #Vizualizar np
            #self.point_cloud_filter.visualize_point_cloud(self.nube_puntos_procesada)

            return self.nube_puntos_procesada

    def cargar_nube_puntos(self):
        self.nube_puntos = o3d.io.read_point_cloud(self.ruta_nube_puntos)

    def visualizar_nube_puntos(self, nube_puntos=None):
        if nube_puntos is None:
            nube_puntos = self.nube_puntos
        o3d.visualization.draw_geometries([nube_puntos])

    def convertir_coordenadas_a_metros(self):
        puntos_metros = []
        for punto in self.contorno:
            punto_metro_x = punto[0] * self.escale_horizontal
            punto_metro_y = punto[1] * self.escala_vertical
            puntos_metros.append([punto_metro_x, punto_metro_y])
        self.coordenadas_metros = puntos_metros

    def dibujar_contorno(self, imagen):
        if self.contorno == []:
            raise ValueError("Contorno no ha sido calculado.")
        imagen = cv.imread(imagen)
        
        cv.drawContours(imagen, [self.contorno], -1, (0, 255, 0), 1)
        return imagen

    def dibujar_radio_maximo(self, imagen):
        if self.radio_maximo == 0:
            raise ValueError("Radio máximo no ha sido calculado.")
        imagen = cv.imread(imagen)
        
        cv.circle(imagen, self.centro_circulo, int(self.radio_maximo), (0, 255, 0), 2)
        return imagen
    
    def set_altura_captura(self):
        #Aqui mismo hare todo el proceso chsm
        self.altura_captura = self.ConvPx2M.estimar_altura_de_captura(self.ruta_nube_puntos)

    def set_escala_horizontal(self):
         self.escale_horizontal, self.escala_vertical = self.ConvPx2M.calcular_escala(self.altura_captura)
    
    def get_diametro_bache(self):
        self.diametro_bache = self.radio_maximo * -2
        return self.diametro_bache

    

    def get_imagenRGB(self):
        # Devuelve la ruta de la imagen RGB
        return self.imagenRGB
    
    def convertir_coordenadas_a_metros_y_crear_nube(self):
        puntos_metros = []
        for punto in self.contorno:
            punto_metro_x = punto[0] * self.escale_horizontal
            punto_metro_y = punto[1] * self.escala_vertical
            # Añade la altura en el eje z
            puntos_metros.append([punto_metro_x, punto_metro_y, 1.0])
        # Crear la nube de puntos
        nube_puntos = o3d.geometry.PointCloud()
        nube_puntos.points = o3d.utility.Vector3dVector(puntos_metros)
        # Visualizar la nube de puntos
        #o3d.visualization.draw_geometries([nube_puntos])
        
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
