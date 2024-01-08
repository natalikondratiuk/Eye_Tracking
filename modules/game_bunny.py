import logging

import tkinter as tk
from PIL import Image, ImageTk

import numpy as np
import math as mt

import cv2
import mediapipe as mp

from modules.controller_app import Controller
from modules.calibration import CalibrationApp
from modules.data import FilterCenter, Data
from modules.visual import CameraFrame, MatplotlibFrame

from objects.sunny_bunny import SunnyBunny
from objects.bunny_catch import BunnyCatch

class GameSB( tk.Tk ) :
    """
    Тренувальна гра
    "Catch Sunny Bunny"
    для визначення найкращого алгоритму
    керування курсором
    """

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Catch Sunny Bunny" )
        self._logger: logging.Logger = logging.getLogger(type(self).__name__)

        self.screen_width, self.screen_height = self.winfo_screenwidth()-15, self.winfo_screenheight()-65
        self.wm_geometry('%dx%d+0+0' % (self.screen_width, self.screen_height))
        self.cX, self.cY = int(self.screen_width/2), int(self.screen_height/2)

        self.color, self.history_len = Controller.get_config()

        self.homo_matrix = CalibrationApp.get_homography()

        self.canvas = tk.Canvas( self, width=self.screen_width, height=self.screen_height, bg=self.color )
        self.canvas.pack()

        self.ctr = FilterCenter(self.history_len)
        self.bunniesQ = self.plot_bunnies = 20
        self.dataset = Data( self.bunniesQ * 35 ) # розмір датасету для аналізу (~35fps)

        self.sb = SunnyBunny(self.canvas, 50,'yellow')
        self.bunny_label = tk.Label( self, text=f"Sunny Bunnies: {self.bunniesQ}", font= ('Consolas 24 bold'), bg=self.color, fg='red' )
        self.bunny_label.place(relx=0.02, rely=0.02)

        '''Налаштування камери для роботи'''
        self.camera_frame = CameraFrame(self)
        self.cam = cv2.VideoCapture(0)
        self.width, self.height = 800, 600

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

        self.sbBase = BunnyCatch(self.canvas, 15, 'gray')
        self.sbCentroid = BunnyCatch(self.canvas, 25, 'green')
        self.sbMNK = BunnyCatch(self.canvas, 25, 'blue')

        self._logger.warning("Game Sunny Bunny started")
        self.set_pos_rand()
        self.get_eye_pos()

    def set_pos_rand(self):
        """
        Генерування сонячного зайчика у випадковому місці
        :return:
        """

        pos = self.sb.get_coords()
        border = 100 # сонячний зайчик не "прилипає" до країв робочого вікна
        x, y = np.random.randint(border, self.screen_width-border), np.random.randint(border, self.screen_height-border)

        dx = x - pos[0]
        dy = y - pos[1]

        self.sb.pos(dx, dy)
        self.bunniesQ -= 1
        self.bunny_label.configure(text=f"Sunny Bunnies: {self.bunniesQ}")

        self.after(5000, self.set_pos_rand) # швидкість сонячного зайчика

    def set_pos_cam(self, sb, x, y):
        """
        Керування очима сонячним зайчиком
        :param sb: сонячний зайчик, що використовує один з алгоритмів
        :param x: Ох точки робочої області екрана
        :param y: Ох точки робочої області екрана
        :return:
        """

        pos = sb.get_coords()

        dx = x - pos[0]
        dy = y - pos[1]

        sb.pos(dx, dy)

    def get_eye_pos(self):
        """
        Основний цикл програми
        :return:
        """

        '''Крок № 1 - налаштування камери'''
        _, frame = self.cam.read()  # ігнорування першого аргументу
        if isinstance(frame, np.ndarray) :
            frame = cv2.flip(frame, 1)  # вертикальний поворот
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            '''Вікно OpenCV у вікні Tkinter'''
            captured_image = Image.fromarray(rgb_frame)
            photo_image = ImageTk.PhotoImage(image=captured_image)

            self.camera_frame.camLabel.photo_image = photo_image
            self.camera_frame.camLabel.configure(image=photo_image)
            self.camera_frame.camLabel.after(10, self.get_eye_pos)

            '''Основний алгоритм роботи програми'''
            face_detector = self.face_mesh.process(rgb_frame)  # розпізнавання обличчя людини
            landmarks = face_detector.multi_face_landmarks

            if landmarks:
                single_face = face_detector.multi_face_landmarks[0].landmark

                cX = single_face[476].x + (single_face[474].x - single_face[476].x) / 2
                cY = single_face[475].y + (single_face[477].y - single_face[475].y) / 2

                '''Calculate eye position'''
                eye_pos = (cX, cY)
                eye_pos_homo = np.append(eye_pos, 1)
                pos_norm = self.homo_matrix.dot(eye_pos_homo)  # tx, ty, tz - гомогенні координати
                '''
                Для переведення з однорідних координат в світові
                дві перших координати діляться на w != 0
                '''

                '''Sunny Bunny Base'''
                xScreen, yScreen = int(pos_norm[0] / pos_norm[2]), int(pos_norm[1] / pos_norm[2])

                '''
                Погляд поза межами екрана -
                значення курсору миші - нижня/верхня межа
                висоти та ширини екрана
                '''

                if xScreen < 0: xScreen = 0
                if xScreen > self.screen_width: xScreen = self.screen_width

                if yScreen < 0: yScreen = 0
                if yScreen > self.screen_height: yScreen = self.screen_height

                self.set_pos_cam( self.sbBase, xScreen, yScreen )

                '''Sunny Bunny Centroid'''
                xCentroid, yCentroid = self.ctr.out_filter(int(pos_norm[0] / pos_norm[2]), int(pos_norm[1] / pos_norm[2]))

                if xCentroid < 0: xCentroid = 0
                if xCentroid > self.screen_width: xCentroid = self.screen_width

                if yCentroid < 0: yCentroid = 0
                if yCentroid > self.screen_height: yCentroid = self.screen_height

                self.set_pos_cam( self.sbCentroid, xCentroid, yCentroid )

                '''Sunny Bunny MNK'''
                xMNK, yMNK = self.ctr.out_filterMNK(int(pos_norm[0] / pos_norm[2]), int(pos_norm[1] / pos_norm[2]))

                if xMNK < 0: xMNK = 0
                if xMNK > self.screen_width: xMNK = self.screen_width

                if yMNK < 0: yMNK = 0
                if yMNK > self.screen_height: yMNK = self.screen_height

                self.set_pos_cam( self.sbMNK, xMNK, yMNK)
                self.dataset.add_data((self.sb.get_coords()[0], self.sb.get_coords()[1]),
                                     (self.sbCentroid.get_coords()[0], self.sbCentroid.get_coords()[1]),
                                     (self.sbMNK.get_coords()[0], self.sbMNK.get_coords()[1]),
                                     (self.sbBase.get_coords()[0], self.sbBase.get_coords()[1]))

        if self.bunniesQ == 0 :
            self.cam.release()
            self.canvas.destroy()
            self.bunny_label.destroy()
            self._logger.warning("Game Sunny Bunny finished")
            self.plot_data() # графічний аналіз даних

            '''
            Аналітичний аналіз даних:
            отримання статичних характеристик
            всіх алгоритмів задля точнішого висновку
            '''
            print('#########################')
            print( 'Визначення найкращого алгоритму калібрування' )
            self.print_stat( self.dataset.get_dist_eye(), 'роботи нефільтрованого значення' )
            self.print_stat(self.dataset.get_dist_centroid(), 'роботи центроїда')
            self.print_stat(self.dataset.get_distMNK(), 'роботи МНК')

    def plot_data(self):
        """
        Графічний аналіз розроблених алгоритмів
        керування курсором миші
        :return:
        """

        min_var, min_algorithm = self.show_min()
        log_message = ''
        if min_algorithm == "Нефільтроване значення": log_message = 'Non-filtered'
        if min_algorithm == "Центроїд" : log_message = 'Centroid'
        if min_algorithm == "МНК": log_message = 'MNK'

        self.plotter = MatplotlibFrame(self, f'Результати роботи алгоритмів калібрування\n'
                                          f'для {self.plot_bunnies} сонячних зайчиків. '
                                          f'Довжина черги - {self.history_len}. '
                                          f'Найкращий алгоритм калібрування - {min_algorithm} (СКВ = {min_var:.3f})', ('Consolas 18'))
        self.plotter.pack()
        self._logger.warning(f'The best filter is {log_message}')

        plt_hist = self.plotter.f.subplots(1, 1)
        plt_hist.hist(self.dataset.get_dist_eye(), bins=100, alpha=0.5, label='Нефільтроване значення')
        plt_hist.hist( self.dataset.get_dist_centroid(), bins=100, alpha=0.5, label='Центроїд' )
        plt_hist.hist(self.dataset.get_distMNK(), bins=100, alpha=0.5, label='МНК')
        self.plotter.f.legend(loc=2)

    def get_statistcs(self, dataset):
        """
        Отримання статистичних даних кожного датасету
        :param dataset: датасет кожного алгоритму
        :return: статистичні характеристики одного з алгоритмів
        """

        statistics = []

        median = np.median( dataset ) # медіана датасету
        statistics.append( median )

        variance = np.var( dataset ) # дисперсія датасету
        statistics.append( variance )

        std = mt.sqrt( variance ) # середньоквадратичне відхилення датасету
        statistics.append( std )

        return statistics

    def print_stat(self, dataset, name):
        """
        Аналітичний аналіз даних
        шляхом порівняння статистичних характеристик
        :param dataset: датасет кожного алгоритму
        :param name: назва кожного датасету
        :return:
        """

        dataStat = self.get_statistcs( dataset ) # статистичні дані кожного датасету

        print('*************************')
        print( f'Статистичні хар-ки {name}' )
        print('*************************')
        print( f'Математичне сподівання = {dataStat[0]}' )
        print( f'Дисперсія = {dataStat[1]}' )
        print( f'Сігма (СКВ) = {dataStat[2]}' )
        print('---------------------------')

    def show_min(self) :
        algorithm_set = ['Нефільтроване значення', 'Центроїд', 'МНК']
        stat_non_filter = self.get_statistcs(self.dataset.get_dist_eye())
        stat_centroid = self.get_statistcs(self.dataset.get_dist_centroid())
        stat_MNK = self.get_statistcs(self.dataset.get_distMNK())

        compare_var = [stat_non_filter[2], stat_centroid[2], stat_MNK[2]]
        comparator = np.array(compare_var)
        min_algorithm = np.argmin(comparator)
        min_var = np.min(comparator)

        return min_var, algorithm_set[min_algorithm]

    def __call__(self): tk.mainloop()
