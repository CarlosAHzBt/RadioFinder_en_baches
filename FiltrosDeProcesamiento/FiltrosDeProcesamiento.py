from shapely.geometry import Point, Polygon
import numpy as np
import open3d as o3d

class PointCloudFilter:
    def __init__(self):
        pass
    
    def filter_points_with_contour(self, pcd, contour_coords_meters):
        """
        Filtra puntos dentro de la región de interés definida por el polígono.
        """
        if pcd is None or contour_coords_meters is None:
            raise ValueError("Nube de puntos o polígono de ROI no definidos")

        # Crear un objeto Polygon usando contour_coords_meters
        roi_polygon = Polygon(contour_coords_meters)
        # Extrae los puntos como un array de numpy
        points = np.asarray(pcd.points)
        # Filtra los puntos usando el polígono de ROI
        filtered_points = [point for point in points if roi_polygon.contains(Point(point[:2]))]

        # Crea una nueva nube de puntos con los puntos filtrados
        filtered_pcd = o3d.geometry.PointCloud()
        filtered_pcd.points = o3d.utility.Vector3dVector(np.array(filtered_points))

        #Ver nube de puntos
        self.visualize_point_cloud(filtered_pcd)

        return filtered_pcd

    @staticmethod
    def visualize_point_cloud(pcd):
        o3d.visualization.draw_geometries([pcd])

    @staticmethod
    def save_point_cloud(output_path, pcd):
        o3d.io.write_point_cloud(output_path, pcd)
