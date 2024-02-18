import numpy as np
import cv2 as cv
import os
import matplotlib.pyplot as plt
from ConvertirPixelesAMetros import ConvertirPixelesAMetros

class Bache:
    def __init__(self,bag_de_origen,imagenRGB, coordenadas=None):
        self.imagen_original_shape = 480, 848  # Pasar la forma de la imagen original al inicializar
        self.bag_de_origen = bag_de_origen
        self.nube_puntos = None
        self.imagenRGB = imagenRGB
        self.coordenadas = np.array(coordenadas)[:, [1, 0]] if coordenadas is not None else np.empty((0, 2), dtype=int)
        # El id del bache es la ruta de la imagen pero solo el nombre del archivo "rgbimage.png" pero sin la extension
        self.id_bache = os.path.splitext(os.path.basename(self.imagenRGB))[0]
        self.radio_maximo = 0
        self.diametro_bache = 0
        self.centro_circulo = (0, 0)

        self.ConvPx2M = ConvertirPixelesAMetros()
        self.altura_captura = 0
        self.escale_horizontal = 0
        self.escala_vertical = 0

    def set_id_bache(self):
        #El id del bache es la ruta de la imagen + el indice de la coordenada
        pass

    def set_imagenRGB(self):
        #apartir de la ruta de la bolsa de origen, se obtiene la ruta de la imagen RGB
        self.imagenRGB = self.bag_de_origen + "/Imagen"       
    def set_nube_puntos(self):
        # Construye la ruta de la nube de puntos
        # Asumiendo que `self.bag_de_origen` es la carpeta que contiene tanto la carpeta 'Imagen' como la carpeta 'PLY'
        # y que `self.imagenRGB` es solo el nombre del archivo con su extensión
        
        nombre_archivo_sin_extension = self.id_bache
        ruta_nube_puntos = os.path.join(self.bag_de_origen, "PLY", nombre_archivo_sin_extension + ".ply")
        
        if os.path.exists(ruta_nube_puntos):
            self.nube_puntos = ruta_nube_puntos
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
        self.altura_captura = self.ConvPx2M.estimar_altura_de_captura(self.nube_puntos)

    def set_escala_horizontal(self):
         self.escale_horizontal, self.escala_vertical = self.ConvPx2M.calcular_escala(self.altura_captura)
    
    def get_diametro_bache(self):
        self.diametro_bache = self.radio_maximo * -2
        return self.diametro_bache

    def get_imagenRGB(self):
        # Devuelve la ruta de la imagen RGB
        return self.imagenRGB