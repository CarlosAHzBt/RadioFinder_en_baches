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
        self.visualize_point_cloud(filtered_pcd)

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
