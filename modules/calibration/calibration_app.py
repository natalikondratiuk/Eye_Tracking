import logging
import time
from datetime import datetime

import tkinter as tk
import cv2
import matplotlib.pyplot as plt
import numpy as np
import mediapipe as mp

class CalibrationApp(tk.Tk) :
    """
    Механізм калібрування
    системи Eye Tracking
    """

    homography = []

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("Calibrate Eye Tracking" )

        self._logger : logging.Logger = logging.getLogger(type(self).__name__)

        self.screen_width, self.screen_height = self.winfo_screenwidth()-15, self.winfo_screenheight()-65
        self.wm_geometry('%dx%d+0+0' % (self.screen_width, self.screen_height))
        self.canvas = tk.Canvas(self, width=self.screen_width, height=self.screen_height)
        self.canvas.pack()
        self.bind('<Escape>', lambda e: self.destroy())

        self._logger.warning("Calibration started")
        self._calibrate()

    def _calibrate(self) :
        '''Часові налаштування калібрування на основі 9 точок'''
        num_slot = 1
        duration_slot = 4
        record_time = 2

        '''9 точок - позиція зайчика (матриця 3х3)'''
        m9 = [
            (64, 40),
            (948, 40),
            (1812, 40),
            (1812, 518),
            (1812, 968),
            (948, 968),
            (64, 968),
            (64, 518),
            (948, 518)
        ]

        circle_radius = 20  # розмір зайчика

        '''
        root = tk.Tk()
        screenW, screenH = root.winfo_screenwidth(), root.winfo_screenheight()
        root.wm_geometry("%dx%d" % (screenW, screenH))

        canvas = tk.Canvas(root, width=screenW, height=screenH)
        canvas.pack()'''
        mark = self.canvas.create_oval(m9[0][0] - circle_radius, m9[0][1] - circle_radius, m9[0][0] + circle_radius, m9[0][1] + circle_radius,
                                  fill='white')
        countdown = self.canvas.create_text(m9[0][0], m9[0][1], text='', font=('Helvetica 15 bold'))
        self.update()
        # time.sleep(3)
        for i in range(3, -1, -1):
            self.canvas.itemconfig(countdown, text=str(i))
            self.update()
            time.sleep(1)
        self.canvas.delete(countdown)

        start_time = datetime.now()

        mark_points = []  # для гомографії

        cX, cY = .5, .5  # початкова позиція очей

        mX = []
        mY = []

        face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True)  # виявлення 3-ох координат в просторі 468 точок
        cam = cv2.VideoCapture(0)

        while True and len(m9) >= num_slot:
            _, frame = cam.read()  # ігнорування першого аргументу
            frame = cv2.flip(frame, 1)  # вертикальний поворот
            ''''
            winCv = "Calibration Frame"
            cv2.namedWindow(winCv)
            cv2.moveWindow(winCv, 100, 510)
            cv2.imshow(winCv, frame)
            '''
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detection = face_mesh.process(rgb_frame)  # виявлення обличчя
            landmarks = detection.multi_face_landmarks  # виявлення орієнтирів обличчя
            now_time = datetime.now()
            slot_time = (now_time - start_time).total_seconds()

            if landmarks:
                single_face = detection.multi_face_landmarks[0].landmark

                cX = single_face[476].x + (single_face[474].x - single_face[476].x) / 2
                cY = single_face[475].y + (single_face[477].y - single_face[475].y) / 2

            if slot_time / duration_slot < num_slot:
                self.canvas.coords(mark,
                              m9[num_slot - 1][0] - circle_radius,
                              m9[num_slot - 1][1] - circle_radius,
                              m9[num_slot - 1][0] + circle_radius,
                              m9[num_slot - 1][1] + circle_radius)
                self.canvas.itemconfig(mark, fill='yellow')
                self.update()
                if slot_time > num_slot * duration_slot - record_time:
                    self.canvas.itemconfig(mark, fill='red')
                    self.update()

                    mX.append(cX)
                    mY.append(cY)
            else:
                mark_points.append((np.median(mX), np.median(mY)))
                mX = []
                mY = []
                num_slot += 1

        cam.release()
        cv2.destroyAllWindows()
        self._logger.warning("Calibration has been finished")

        CalibrationApp.homography = np.array(mark_points, dtype=float)

        '''Кластеризація середніх точок погляду'''
        plt.figure("Результати калібрування системи Eye Tracking")
        plt.title("Кластеризація середніх точок погляду очей")

        colors = ['red', 'green', 'blue', 'magenta', 'olive', 'cyan', 'salmon', 'purple', 'maroon']
        for i, p in enumerate(CalibrationApp.homography):
            plt.scatter(p[0], p[1], color=colors[i])

        plt.gca().invert_yaxis()
        plt.show()

    @staticmethod
    def get_homography() :
        '''Формування corresponding points для обчислення матриці гомографії'''
        screen_points = np.array([[0, 0],
                                 [960, 0],
                                 [1920, 0],
                                 [1920, 540],
                                 [1920, 1080],
                                 [960, 1080],
                                 [0, 1080],
                                 [0, 540],
                                 [960, 540]], dtype=float)


        '''Обчислення матриці гомографії'''
        homo_matrix, _ = cv2.findHomography(CalibrationApp.homography, screen_points)
        return homo_matrix
    def __call__(self) : tk.mainloop()
