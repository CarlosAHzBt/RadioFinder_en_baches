from ModeloSegmentacion import ModeloSegmentacion
from CargarModelo import CargarModelo
from Bache import Bache
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

def procesar_imagen(ruta_imagen):
    segmentador = ModeloSegmentacion(modelo_entrenado)
    coordenadas_baches = segmentador.obtener_coordenadas_baches(ruta_imagen)

    #Recorrer el array de coornedadas_baches y crear una instancia de la clase Bache por cada coordenada donde id_bache sera el nombre de la imagen mas un indice_0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
    baches = []
    for i, bache in enumerate(coordenadas_baches):
        bache = Bache(ruta_imagen + "_" + str(i), bache)
        baches.append(bache)
    
    #Calcular el contorno y el radio maximo de cada bache
    for bache in baches:
        bache.calcular_contorno()
        bache.calcular_radio_maximo()

    

    
    #imprimir el radio maximo de cada bache
    for bache in baches:
        print(f"El radio máximo del bache {bache.id_bache} es {bache.radio_maximo}")
    

    






modelo = CargarModelo()
modelo_entrenado = modelo.cargar_modelo("RutaModelo/model_state_dict.pth")

# Procesar una imagen
procesar_imagen("Imagen/RGBcolor_image.png")

