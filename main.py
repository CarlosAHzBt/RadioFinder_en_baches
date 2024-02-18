from ProcesadorBags import ProcesadorBags
from AdministradorDeArchivos import AdministradorArchivos
from ModeloSegmentacion import ModeloSegmentacion
from CargarModelo import CargarModelo
from Bache import Bache

def extraer_datos_de_bags(ruta_carpeta_bags):
    procesador_bags = ProcesadorBags(ruta_carpeta_bags)
    procesador_bags.process_bag_files()
    print("Extracción de datos de archivos .bag completada.")

def procesar_imagenes(carpeta_base):
    modelo = CargarModelo()
    modelo_entrenado = modelo.cargar_modelo("RutaModelo/model_state_dict.pth")
    segmentador = ModeloSegmentacion(modelo_entrenado)
    administrador_archivos = AdministradorArchivos(carpeta_base)

    archivos_bags = administrador_archivos.generar_lista_de_archivosBags()
    for ruta_carpeta_bag in archivos_bags:
        imagenes = administrador_archivos.generar_lista_de_imagenes(ruta_carpeta_bag)
        for ruta_imagen in imagenes:
            coordenadas_baches = segmentador.obtener_coordenadas_baches(ruta_imagen)
            baches = [Bache(ruta_carpeta_bag, ruta_imagen, coord) for coord in coordenadas_baches]

            for bache in baches:
                bache.calcular_contorno()
                bache.calcular_radio_maximo()
                print(f"El radio máximo del bache {bache.id_bache} es {bache.diametro_bache} unidades.")

if __name__ == "__main__":
    ruta_carpeta_bags = "bag"
    carpeta_destino = "ArchivosDeLaExtraccion"
    
    # Paso 1: Extraer datos de archivos .bag
    extraer_datos_de_bags(ruta_carpeta_bags)
    
    # Paso 2: Procesar imágenes y detección de baches
    procesar_imagenes(carpeta_destino)
