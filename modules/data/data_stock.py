import numpy as np
import math as mt

class Data:
    """
    Створення датасету для визначення
    найкращого алгоритму керування курсором миші
    """

    def __init__(self, history_len):
        self.i = 0

        self.data_len = history_len

        '''Масиви для кожного зайчика'''
        self.rand_coordsX = np.zeros(self.data_len, dtype=np.int32)
        self.rand_coordsY = np.zeros(self.data_len, dtype=np.int32)

        self.centroid_coordsX = np.zeros(self.data_len, dtype=np.int32)
        self.centroid_coordsY = np.zeros(self.data_len, dtype=np.int32)

        self.MNK_coordsX = np.zeros(self.data_len, dtype=np.int32)
        self.MNK_coordsY = np.zeros(self.data_len, dtype=np.int32)

        self.eye_coordsX = np.zeros(self.data_len, dtype=np.int32)
        self.eye_coordsY = np.zeros(self.data_len, dtype=np.int32)

    def dist(self, x, y, x1, y1):
        """"
        Евклідова відстань
        як фактор порівняння алгоритмів
        """

        return mt.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)

    def add_data(self, randCoords, centroidCoords, MNKCoords, eyeCoords):

        if self.i >= self.data_len: return

        self.rand_coordsX[self.i] = randCoords[0]
        self.rand_coordsY[self.i] = randCoords[1]

        self.centroid_coordsX[self.i] = centroidCoords[0]
        self.centroid_coordsY[self.i] = centroidCoords[1]

        self.MNK_coordsX[self.i] = MNKCoords[0]
        self.MNK_coordsY[self.i] = MNKCoords[1]

        self.eye_coordsX[self.i] = eyeCoords[0]
        self.eye_coordsY[self.i] = eyeCoords[1]

        self.i += 1

    def getDataX(self, type):
        if type == 0: return self.rand_coordsX
        if type == 1: return self.centroid_coordsX
        if type == 2: return self.MNK_coordsX
        if type == 3: return self.eye_coordsX

    def getDataY(self, type):
        if type == 0: return self.rand_coordsY
        if type == 1: return self.centroid_coordsY
        if type == 2: return self.MNK_coordsY
        if type == 3: return self.eye_coordsY

    '''
    Пошук евклідової відстані
    між сонячним зайчиком,
    чиї координати генеруються випадково
    та зайчиками, що керуються очима
    '''

    def get_dist_centroid(self):
        dst = np.zeros(self.data_len)
        for i in range(self.data_len):
            dst[i] = self.dist(self.rand_coordsX[i],
                               self.rand_coordsY[i],
                               self.centroid_coordsX[i],
                               self.centroid_coordsY[i])
        return dst

    def get_distMNK(self):
        dst = np.zeros(self.data_len)
        for i in range(self.data_len):
            dst[i] = self.dist(self.rand_coordsX[i],
                               self.rand_coordsY[i],
                               self.MNK_coordsX[i],
                               self.MNK_coordsY[i])
        return dst

    def get_dist_eye(self):
        dst = np.zeros(self.data_len)
        for i in range(self.data_len):
            dst[i] = self.dist(self.rand_coordsX[i],
                               self.rand_coordsY[i],
                               self.eye_coordsX[i],
                               self.eye_coordsY[i])
        return dst