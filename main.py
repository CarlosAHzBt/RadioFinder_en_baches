from ProcesadorBags import ProcesadorBags
from AdministradorDeArchivos import AdministradorArchivos
from ModeloSegmentacion import ModeloSegmentacion
from CargarModelo import CargarModelo
from Bache import Bache
import concurrent.futures
import os


def cargar_modelo():
    modelo = CargarModelo()
    modelo_entrenado = modelo.cargar_modelo("RutaModelo/model_state_dict.pth")
    return modelo_entrenado
def procesar_imagenes(carpeta_base):

    segmentador = ModeloSegmentacion(modelo_entrenado)
    administrador_archivos = AdministradorArchivos(carpeta_base)

    archivos_bags = administrador_archivos.generar_lista_de_archivosBags()
    for ruta_carpeta_bag in archivos_bags:
        imagenes = administrador_archivos.generar_lista_de_imagenes(ruta_carpeta_bag)
        for ruta_imagen in imagenes:
            coordenadas_baches = segmentador.obtener_coordenadas_baches(ruta_imagen)
            for i, coord in enumerate(coordenadas_baches):
                # Generar un ID único para cada bache
                id_bache = f"{os.path.splitext(os.path.basename(ruta_imagen))[0]}_{i}"
                bache = Bache(ruta_carpeta_bag, ruta_imagen, id_bache, coord)
                # Procesar el bache (calcular contorno, radio máximo, etc.)
                bache.calcular_contorno()
                bache.calcular_radio_maximo()
                print(f"El radio máximo del bache {bache.id_bache} es {bache.diametro_bache} mm procedente del bag {bache.bag_de_origen}.")
                # Asumiendo que existe una lista para almacenar baches detectados
                lista_baches.append(bache)
    return lista_baches

def filtrar_baches_por_radio(baches, diametro_minimo, diamtro_maximo):
    baches_filtrados = [bache for bache in baches if diametro_minimo <= bache.diametro_bache <= diamtro_maximo]
    return baches_filtrados

#Con la lista de baches filtrados por radio se puede hacer el procesamiento de nubes de puntos
#Se puede hacer el procesamiento de nubes de puntos en paralelo
def procesar_nubes_de_puntos(baches_filtrados):
    for bache in baches_filtrados:
        bache.procesar_nube_puntos()
        print(f"Se procesó la nube de puntos del bache {bache.id_bache} procedente del bag {bache.bag_de_origen}.")

if __name__ == "__main__":
    ruta_carpeta_bags = "bag"
    carpeta_destino = "ArchivosDeLaExtraccion"
    lista_baches = []
    modelo_entrenado = cargar_modelo()

    procesador_bag = ProcesadorBags(ruta_carpeta_bags)
    lista_bag = procesador_bag.get_bag_files()
    # Paso 1: Extraer datos de archivos .bag
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for bag in lista_bag:
            executor.submit(procesador_bag.process_bag_file, bag)

    # Paso 2: Procesar imágenes y detección de baches
            #Se podria agregar paralelismo en este paso pero se tiene que cambiar la ruta que se manda ya que se esta mandando la ruta de todos los bags 
            #Y la ruta de todos los bags se utiliza para darle identificador a los baches y facilitar el acceso a las nubes de puntos e imagenes
            # por lo que se ocupa hacer varios cambios para poder hacer paralelismo en este paso
    lista_baches = procesar_imagenes(carpeta_destino)
    # Paso 3: Filtrar baches por radio
    diametro_minimo = 150
    diametro_maximo = 5000
    baches_filtrados = filtrar_baches_por_radio(lista_baches, diametro_minimo, diametro_maximo)

    print(f"Se encontraron {len(baches_filtrados)} baches con un diámetro entre {diametro_minimo} y {diametro_maximo} unidades.")

    # Paso 4: Procesar nubes de puntos
    procesar_nubes_de_puntos(baches_filtrados)
    
    