from shapely.geometry import Point, Polygon
import numpy as np
import open3d as o3d

class PointCloudFilter:
    def __init__(self):
        pass

    def get_bounding_box(self, contour_coords_meters):
        """
        Calcula el bounding box a partir de las coordenadas del contorno.
        """
        # Convierte la lista de coordenadas a un array de NumPy para facilitar los cálculos
        coords = np.array(contour_coords_meters)
        x_min, y_min = np.min(coords, axis=0)
        x_max, y_max = np.max(coords, axis=0)
        return x_min, y_min, x_max, y_max
    
    def filter_points_with_bounding_box(self, pcd, contour_coords_meters):
        """
        Filtra puntos dentro del bounding box calculado a partir de las coordenadas del contorno.
        """
        if pcd is None or contour_coords_meters is None:
            raise ValueError("Nube de puntos o coordenadas del contorno no definidos")
        
        # Calcula el bounding box
        x_min, y_min, x_max, y_max = self.get_bounding_box(contour_coords_meters)
        
        # Filtra los puntos dentro del bounding box
        points = np.asarray(pcd.points)
        filtered_points = points[
            (points[:, 0] >= x_min) & (points[:, 0] <= x_max) &
            (points[:, 1] >= y_min) & (points[:, 1] <= y_max)
        ]
        
        # Crea una nueva nube de puntos con los puntos filtrados
        filtered_pcd = o3d.geometry.PointCloud()
        filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)

        # Opcional: Visualizar la nube de puntos filtrada
        #self.visualize_point_cloud(filtered_pcd)

        return filtered_pcd

    @staticmethod
    def visualize_point_cloud(pcd):
        """
        Visualiza la nube de puntos.
        """
        o3d.visualization.draw_geometries([pcd])

    @staticmethod
    def save_point_cloud(output_path, pcd):
        """
        Guarda la nube de puntos en el archivo especificado.
        """
        o3d.io.write_point_cloud(output_path, pcd)


    #Funcion para visualizar imagen rgb en una malla de puntos 3D para comparar con la nube de puntos y el contorno de las coordenadas convertidas a metros
    def visuzlizar_imgen_rgb(self,imagen_path, coordenadass_a_metros):
    #    #Crear una malla de puntos 3D a partir de la imagen
    #    imagen = o3d.io.read_image(imagen_path)
#
    #    imagen_malla = o3d.geometry.Image(imagen)
    #    #imagen_malla = o3d.geometry.create_point_cloud_from_rgbd_image(imagen_malla)
    #    #Crear una malla de puntos 3D a partir de las coordenadas convertidas a metros
    #    coordenadas_malla = o3d.geometry.PointCloud()
    #    coordenadass_a_metros = np.array(coordenadass_a_metros)
    #    coordenadass_a_metros = np.concatenate([coordenadass_a_metros, np.zeros((coordenadass_a_metros.shape[0], 1))], axis=1)
#
    #    coordenadas_malla.points = o3d.utility.Vector3dVector(coordenadass_a_metros)
    #    #Visualizar ambas mallas de puntos
    #    o3d.visualization.draw_geometries([imagen_malla, coordenadas_malla])
        pass