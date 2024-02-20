import numpy as np
import open3d as o3d

class RANSAC:
    """
    Clase RANSAC que realiza la detección y nivelación del plano del terreno en una nube de puntos preprocesada.
    Attributes:
        distancia_thresh (float): Umbral de distancia para el algoritmo RANSAC.
    """

    def __init__(self, distancia_thresh=0.05):
        """
        Inicializa la clase RANSAC con el umbral de distancia para el algoritmo RANSAC.
        Parameters:
            distancia_thresh (float): Umbral de distancia para el algoritmo RANSAC.
        """
        self.distancia_thresh = distancia_thresh

    def filtrar_puntos(self, pcd, z_min, z_max):
        """
        Filtra la nube de puntos en el eje Z entre z_min y z_max.
        """
        puntos = np.asarray(pcd.points)
        filtrados = puntos[(puntos[:, 1] > z_min) & (puntos[:, 1] < z_max)]
        pcd_filtrado = o3d.geometry.PointCloud()
        pcd_filtrado.points = o3d.utility.Vector3dVector(filtrados)
        return pcd_filtrado

    def segmentar_terreno(self, pcd):
        """
        Segmenta el terreno utilizando el algoritmo RANSAC.
        """
        plano, inliers = pcd.segment_plane(distance_threshold=self.distancia_thresh, ransac_n=4, num_iterations=10000)

        inlier_cloud = pcd.select_by_index(inliers)

        return inlier_cloud, plano

    def nivelar_puntos(self, plano):
        """
        Nivela la nube de puntos basándose en el plano del terreno detectado.
        """
        A, B, C, D = plano
        norm = np.linalg.norm([A, B, C])
        vector_plano = np.array([A, B, C]) / norm
        up_vector = np.array([0, 0, 1])
        rot = self.matriz_rotacion(vector_plano, up_vector)
        transform = np.eye(4)
        transform[:3, :3] = rot
    
        return transform  # Retorna la nube de puntos transformada ya que la transformación se aplica in situ

    @staticmethod
    def matriz_rotacion(v1, v2):
        """
        Calcula la matriz de rotación para alinear v1 con v2.
        """
        v = np.cross(v1, v2)
        s = np.linalg.norm(v)
        c = np.dot(v1, v2)
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        R = np.eye(3) + vx + np.dot(vx, vx) * ((1 - c) / (s ** 2))
        return R

    def procesar_nube_completa(self, pcd, z_min=-2, z_max=2):
        """
        Procesa la nube de puntos completa: filtra, segmenta y nivela el terreno.
        """
        # Filtrar puntos en el eje Z
        pcd_filtrado = self.filtrar_puntos(pcd, z_min, z_max)


        # Segmentar terreno
        pcd_terreno, plano = self.segmentar_terreno(pcd_filtrado)

        # Nivelar puntos
        transformacion = self.nivelar_puntos(plano)
        pcd_nivelada = pcd.transform(transformacion) # La nube de puntos ya está nivelada después de esta llamada
        #o3d.visualization.draw_geometries([pcd_nivelada])

        return pcd_nivelada, plano
