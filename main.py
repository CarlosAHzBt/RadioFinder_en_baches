from ModeloSegmentacion import ModeloSegmentacion
from CargarModelo import CargarModelo
from AdministradorDeArchivos import AdministradorArchivos
from Bache import Bache
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

def procesar(ruta):
    segmentador = ModeloSegmentacion(modelo_entrenado)
    administradorArchivos = AdministradorArchivos()

    #Obtener lista de archivos bags
    archivos_bags = administradorArchivos.generar_lista_de_archivosBags()

    # Recorrer la lista de archivos bags
    for ruta_carpeta_bag in archivos_bags:
        # Obtener la lista de imágenes directamente de la carpeta "Imagen" de la carpeta bag
        imagenes = administradorArchivos.generar_lista_de_imagenes(ruta_carpeta_bag)
        for ruta_imagen in imagenes:
            #Obtener las coordenadas de los baches
        
            coordenadas_baches = segmentador.obtener_coordenadas_baches(ruta_imagen)
            #Recorrer el array de coornedadas_baches y crear una instancia de la clase Bache por cada coordenada donde id_bache sera el nombre de la imagen mas un indice_0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
            baches = []
            for i, bache in enumerate(coordenadas_baches):
                bache = Bache(ruta_carpeta_bag,ruta_imagen, bache) #ruta_bag es la ruta de la carpeta bag
                baches.append(bache)
            #Calcular el contorno y el radio maximo de cada bache
            for bache in baches:
                bache.calcular_contorno()
                bache.calcular_radio_maximo()
                # imprimir el radio maximo de cada bache
                print(f"El diametro del bache {bache.id_bache} es {bache.get_diametro_bache()} mm")


        








modelo = CargarModelo()
modelo_entrenado = modelo.cargar_modelo("RutaModelo/model_state_dict.pth")

# Procesar 
procesar("ArchivosDeLaExtraccion")

