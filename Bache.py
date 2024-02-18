import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

class Bache:
    def __init__(self, id_bache, coordenadas=None):
        self.id_bache = id_bache
        self.coordenadas = np.array(coordenadas)[:, [1, 0]] if coordenadas is not None else np.empty((0, 2), dtype=int)
        self.contorno = []
        self.radio_maximo = 0
        self.centro_circulo = (0, 0)
        self.imagen_original_shape = 480, 848  # Pasar la forma de la imagen original al inicializar
    
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
    
    def get_bag_de_origen(self):
        # Devuelve la ruta de la imagen de origen
        return self.bag_de_origen
    
    # ... otros métodos ...
