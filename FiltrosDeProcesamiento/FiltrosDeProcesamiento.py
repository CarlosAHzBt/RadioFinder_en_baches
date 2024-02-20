from shapely.geometry import Point, Polygon
import numpy as np
import open3d as o3d

class PointCloudFilter:
    def __init__(self):
        pass
    
    def filter_points_with_contour(self, pcd, contour_coords_meters):
        """
        Filtra los puntos dentro de una nube de puntos basándose en un contorno dado en metros.

        :param pcd: Objeto PointCloud de Open3D que se filtrará.
        :param contour_coords_meters: Lista de coordenadas (x, y) en metros que definen el contorno del bache.
        :return: Objeto PointCloud filtrado con solo los puntos dentro del contorno del bache.
        """
        # Crear un polígono a partir del contorno
        polygon = Polygon(contour_coords_meters)
        
        # Lista para almacenar los índices de puntos dentro del contorno
        inside_indices = []
        
        # Verificar cada punto en la nube de puntos
        for i, point in enumerate(pcd.points):
            # Crear un objeto Point con las coordenadas x, y del punto
            point_2d = Point([point[0], point[1]])
            
            # Verificar si el punto está dentro del polígono del contorno
            if polygon.contains(point_2d):
                inside_indices.append(i)
        
        # Filtrar la nube de puntos para quedarse solo con los puntos dentro del contorno
        filtered_pcd = pcd.select_by_index(inside_indices, invert=False)
        
        return filtered_pcd

    @staticmethod
    def visualize_point_cloud(pcd):
        o3d.visualization.draw_geometries([pcd])

    @staticmethod
    def save_point_cloud(output_path, pcd):
        o3d.io.write_point_cloud(output_path, pcd)
