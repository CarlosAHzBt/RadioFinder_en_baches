import os

class AdministradorArchivos:
    def __init__(self, carpeta_base="ArchivosDeLaExtraccion"):
        self.carpeta_base = carpeta_base

    def generar_lista_de_archivosBags(self):
        # Asumiendo que los archivos bags están directamente bajo carpeta_base
        archivos_bags = [os.path.join(self.carpeta_base, f) for f in os.listdir(self.carpeta_base)
                         if os.path.isdir(os.path.join(self.carpeta_base, f))]
        return archivos_bags

    def generar_lista_de_subcarpetas(self, ruta_carpeta_bag):
        # Genera y devuelve una lista de subcarpetas para una carpeta bag dada
        subcarpetas = [os.path.join(ruta_carpeta_bag, f) for f in os.listdir(ruta_carpeta_bag)
                       if os.path.isdir(os.path.join(ruta_carpeta_bag, f))]
        return subcarpetas

    def generar_lista_de_imagenes(self, ruta_carpeta_bag):
        # Devuelve una lista de rutas de imágenes dentro de la carpeta "Imagen" de la carpeta bag
        ruta_carpeta_imagenes = os.path.join(ruta_carpeta_bag, "Imagen")
        imagenes = [os.path.join(ruta_carpeta_imagenes, f) for f in os.listdir(ruta_carpeta_imagenes)
                    if os.path.isfile(os.path.join(ruta_carpeta_imagenes, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return imagenes
    
    def generar_lista_de_nubes_puntos(self, ruta_subcarpeta):
        # Genera y devuelve una lista de rutas de nubes de puntos dentro de una subcarpeta
        ruta_carpeta_ply = os.path.join(ruta_subcarpeta, "PLY")
        nubes_puntos = [os.path.join(ruta_carpeta_ply, f) for f in os.listdir(ruta_carpeta_ply)
                        if os.path.isfile(os.path.join(ruta_carpeta_ply, f))]
        return nubes_puntos
    


    def crear_carpeta(self, ruta_carpeta):
        # Crea una carpeta si no existe
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

    def consultar_carpeta(self, ruta_carpeta, tipo='imagenes'):
        # Devuelve la lista de archivos dentro de una carpeta específica, filtrando por tipo
        archivos = [os.path.join(ruta_carpeta, f) for f in os.listdir(ruta_carpeta)
                    if os.path.isfile(os.path.join(ruta_carpeta, f)) and f.endswith(self._obtener_extension(tipo))]
        return archivos

    def _obtener_extension(self, tipo):
        # Devuelve la extensión de archivo basada en el tipo especificado
        if tipo == 'imagenes':
            return ('.png', '.jpg', '.jpeg')
        elif tipo == 'nube_puntos':
            return '.ply'
        else:
            return ''
