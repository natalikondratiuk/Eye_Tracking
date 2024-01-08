import logging

import tkinter as tk
from tkinter import messagebox

import numpy as np
import cv2
import mediapipe as mp
import pyautogui

from modules.data.queue_setup import FilterCenter
from modules.calibration import CalibrationApp
from modules.controller import ControlFrame

class Controller(tk.Tk) :
    """
    Користувацькі налаштування
    для гри "Catch Sunny Bunny"
    """

    bg_color: str = ""
    queue_len: int = 0

    def __init__( self, *args, **kwargs ) :
        tk.Tk.__init__( self, *args, **kwargs )
        tk.Tk.wm_title( self, "Controller App" )
        self._logger: logging.Logger = logging.getLogger(type(self).__name__)

        self.screen_width, self.screen_height = self.winfo_screenwidth()-15, self.winfo_screenheight()-65
        self.wm_geometry('%dx%d+0+0' % (self.screen_width, self.screen_height))
        self.cX, self.cY = int(self.screen_width/2), int(self.screen_height/2)
        self.bind('<Escape>', lambda e: self.destroy())

        self.colors = ('lightblue', 'lightgreen', 'antiquewhite2')
        self.history_len = (5, 15, 21)
        self._flag = False

        self.homo_matrix = CalibrationApp.get_homography()

        '''Mouse Controll Settings'''
        self.history_length = 21  # довжина черги (історія попередніх координат від веб-камери)
        self.ctr = FilterCenter(self.history_length)

        self.canvas = tk.Canvas(self, width=self.screen_width, height=self.screen_height, bg='azure1')
        self.canvas.pack()

        self.bg_title = self.canvas.create_text(500, 30, text='Background Color', fill='red', font=('Helvetica 25 bold'))

        self.banners_color = [
            ControlFrame(self.canvas, 300, 71, f'bg color - {self.colors[0]}'),
            ControlFrame(self.canvas, 300, 275, f'bg color - {self.colors[1]}'),
            ControlFrame(self.canvas, 300, 529, f'bg color - {self.colors[2]}')
        ]

        self.history_title = self.canvas.create_text(1229, 30, text='History Length', fill='red', font=('Helvetica 25 bold'))
        self.banners_queue = [
            ControlFrame(self.canvas, 1029, 71, f'history length - {self.history_len[0]}'),
            ControlFrame(self.canvas, 1029, 275, f'history length - {self.history_len[1]}'),
            ControlFrame(self.canvas, 1029, 529, f'history length - {self.history_len[2]}')
        ]

        self.button_start = tk.Button(self, text="START Game", width=20, height=3, font=('Consolas', 25), command=self._start_game)
        self.button_start.place(relx=0.36, rely=0.72)

        self._color_change()

    @staticmethod
    def get_config() : return Controller.bg_color, Controller.queue_len

    def _start_game(self) :
        if Controller.bg_color == "" or Controller.queue_len == 0 :
            messagebox.showerror("Error",
                                 "You must choose bg color and queue length "
                                 "to start Sunny Bunny Game\n"
                                 "RETRY AGAIN!!!")
            self._logger.warning('You must choose bg color and queue length '
                                 'to start Sunny Bunny Game')
        else:
            start = messagebox.askyesno("Start Sunny Bunny Game",
                               f"You choose:\nbg color - {Controller.bg_color}\nqueue length - {Controller.queue_len}\n"
                               f"START Sunny Bunny Game?", icon='info')
            self._logger.warning(f'You have chose bg color - {Controller.bg_color} & queue length - {Controller.queue_len}')

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
                posNorm = self.homo_matrix.dot(eye_pos_homo)  # tx, ty, tz - гомогенні координати
                '''
                Для переведення з однорідних координат в світові
                дві перших координати діляться на w != 0
                '''

                '''Sunny Bunny Centroid'''
                xCentroid, yCentroid = self.ctr.out_filter(int(posNorm[0] / posNorm[2]), int(posNorm[1] / posNorm[2]))

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
                            ban.make_active(self.colors[i])
                            Controller.bg_color = self.colors[i]
                        else : ban.make_disabled()

                    for i, ban in enumerate(self.banners_queue):
                        if ban.check_pos(xCentroid, yCentroid):
                            ban.make_active()
                            Controller.queue_len = self.history_len[i]
                        else: ban.make_disabled()
                    pyautogui.click()

                    self.config(cursor='hand2')
                    self.update()

                self.config(cursor='arrow')
                self.update()

        cam.release()
        cv2.destroyAllWindows()

    def __call__(self): tk.mainloop()
