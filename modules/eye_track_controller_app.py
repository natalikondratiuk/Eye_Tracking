import logging

import tkinter as tk
from tkinter import messagebox

import numpy as np
import cv2
import mediapipe as mp
import pyautogui

from modules.data.queue_setup import FilterCenter
from modules.calibration import CalibrationApp
from modules.controller_app import Controller
from modules.controller import ControlFrame

class EyeTrackController(tk.Tk) :
    """
    Користувацькі налаштування
    для процесу Eye Tracking
    """

    algorithm: str = ""

    def __init__( self, *args, **kwargs ) :
        tk.Tk.__init__( self, *args, **kwargs )
        tk.Tk.wm_title( self, "Controller App" )
        self._logger: logging.Logger = logging.getLogger(type(self).__name__)

        self.screen_width, self.screen_height = self.winfo_screenwidth()-15, self.winfo_screenheight()-65
        self.wm_geometry('%dx%d+0+0' % (self.screen_width, self.screen_height))
        self.cX, self.cY = int(self.screen_width/2), int(self.screen_height/2)
        self.bind('<Escape>', lambda e: self.destroy())

        self.algorithms = ("Центроїд", "МНК")
        self.bg = Controller.get_config()[0]
        self._flag = False

        self.homo_matrix = CalibrationApp.get_homography()
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

        '''Mouse Controll Settings'''
        self.history_len = 21  # довжина черги (історія попередніх координат від веб-камери)
        self.ctr = FilterCenter(self.history_len)

        self.canvas = tk.Canvas(self, width=self.screen_width, height=self.screen_height, bg=self.bg)
        self.canvas.pack()

        self.bg_title = self.canvas.create_text(900, 100, text='Алгоритм калібрування', fill='red', font=('Helvetica 25 bold'))

        self.banners_color = [
            ControlFrame(self.canvas, 300, 275, f'Алгоритм - {self.algorithms[0]}'),
            ControlFrame(self.canvas, 1029, 275, f'Алгоритм - {self.algorithms[1]}')
        ]

        self.button_start = tk.Button(self, text="START Program", width=20, height=3, font=('Consolas', 25), command=self._start_game)
        self.button_start.place(relx=0.36, rely=0.52)

        self._color_change()

    @staticmethod
    def get_config() : return EyeTrackController.algorithm

    def _start_game(self) :
        if EyeTrackController.algorithm == "" :
            messagebox.showerror("Error",
                                 "You must choose calibration algorithm "
                                 "to start Eye Track Program\n"
                                 "RETRY AGAIN!!!")
            self._logger.warning('You must choose filter algorithm '
                                 'to start Eye Track program')
        else:
            start = messagebox.askyesno("Start Eye Track Program",
                               f"You choose:\ncalibration algorithm - {EyeTrackController.algorithm}\n"
                               f"START Eye Track Program?", icon='info')
            log_message = ''
            if EyeTrackController.algorithm == 'Центроїд' : log_message = 'Centroid'
            if EyeTrackController.algorithm == 'МНК': log_message = 'MNK'
            self._logger.warning(f'You have chose filter algorithm - {log_message}')

            if start == True : self._flag = True

    def _color_change(self):
        face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)  # виявлення 3-ох координат в просторі 468 точок
        cam = cv2.VideoCapture(0)

        while True and not self._flag:
            _, frame = cam.read()  # ігнорування першого аргументу
            frame = cv2.flip(frame, 1)  # вертикальний поворот
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_detector = face_mesh.process(rgb_frame)  # розпізнавання обличчя людини
            landmarks = face_detector.multi_face_landmarks  # виявлення орієнтирів обличчя

            if landmarks:
                single_face = face_detector.multi_face_landmarks[0].landmark

                cX = single_face[476].x + (single_face[474].x - single_face[476].x) / 2
                cY = single_face[475].y + (single_face[477].y - single_face[475].y) / 2
                self.update()

                '''Calculate eye position'''
                eye_pos = (cX, cY)
                eye_pos_homo = np.append(eye_pos, 1)
                pos_norm = self.homo_matrix.dot(eye_pos_homo)  # tx, ty, tz - гомогенні координати
                '''
                Для переведення з однорідних координат в світові
                дві перших координати діляться на w != 0
                '''

                '''Sunny Bunny Centroid'''
                xCentroid, yCentroid = self.ctr.out_filter(int(pos_norm[0] / pos_norm[2]), int(pos_norm[1] / pos_norm[2]))

                if xCentroid < 0: xCentroid = 0
                if xCentroid > self.screen_width: xCentroid = self.screen_width

                if yCentroid < 0: yCentroid = 0
                if yCentroid > self.screen_height: yCentroid = self.screen_height

                pyautogui.moveTo(xCentroid, yCentroid)

                '''Кліпання лівого ока - вибір нової операції'''
                left_eye = [single_face[145], single_face[159]]
                blink = left_eye[0].y - left_eye[1].y  # різниця між краями лівого ока - признак кліпання ока
                blink_threshold = 0.01  # все, що менше порогу - ознака кліпання ока
                if blink < blink_threshold:
                    for i, ban in enumerate (self.banners_color):
                        if ban.check_pos(xCentroid,yCentroid):
                            ban.make_active()
                            EyeTrackController.algorithm = self.algorithms[i]
                        else : ban.make_disabled()

                    pyautogui.click()

                    self.config(cursor='hand2')
                    self.update()

                self.config(cursor='arrow')
                self.update()

        cam.release()
        cv2.destroyAllWindows()

    def __call__(self): tk.mainloop()
