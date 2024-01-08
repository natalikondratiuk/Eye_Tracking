import logging

import webbrowser
import tkinter as tk

import cv2
import numpy as np
import mediapipe as mp

import pyautogui
pyautogui.FAILSAFE = False

from modules.data.queue_setup import FilterCenter
from modules.calibration import CalibrationApp
from modules.eye_track_controller_app import EyeTrackController
from modules.controller_app import Controller

from objects.activity_downloader import ActivityDownloader
from objects.shop_downloader import ShopDownloader

class EyeTracker(tk.Tk) :
    """
    GUI, що відображає практичне застосування
    технології Eye Tracking на прикладі
    керування Інтернет-ресурсами однієї
    з чотирьох категорій
    """

    def __init__(self, *args, **kwargs) :
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Eye Tracker")
        self._logger: logging.Logger = logging.getLogger(type(self).__name__)

        self._screen_width, self._screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        tk.Tk.wm_state( self, 'zoomed' )
        self.bind('<Escape>', lambda e: self.destroy())

        self._activity_images = ActivityDownloader().get_image
        self._logos = ShopDownloader().get_image
        self.active, self.non_active = 'green', '#F08080'

        self.homoMatrix = CalibrationApp.get_homography()

        '''Mouse Controll Settings'''
        self.history_len = Controller.get_config()[1]  # довжина черги (історія попередніх координат від веб-камери)
        self.algorithm = EyeTrackController.get_config()
        if self.algorithm == "Центроїд":
            self._logger.warning('You choose Centroid filter algorithm')
        if self.algorithm == "МНК":
            self._logger.warning('You choose MNK filter algorithm')

        self.ctr = FilterCenter(self.history_len)

        self._shop_frame = tk.Frame(self, width=int(self._screen_width / 2), height=int(self._screen_height / 2),
                              bg='yellow', relief=tk.RIDGE, borderwidth=2)

        self._eat_frame = tk.Frame(self._shop_frame, width=400, height=400, bg=self.non_active, relief=tk.RIDGE, borderwidth=15)
        self._eat_landmark = tk.Label(self._eat_frame, bg=self.non_active, image=self._activity_images[0])
        self._eat_landmark.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self._eat_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self._education_frame = tk.Frame(self, width=int(self._screen_width / 2), height=int(self._screen_height / 2),
                                   bg='orange', relief=tk.RIDGE, borderwidth=2)
        self._edu_frame = tk.Frame(self._education_frame, width=400, height=400,
                                   bg=self.non_active, relief=tk.RIDGE, borderwidth=15)
        self._edu_img = [edu_logo for edu_logo in self._activity_images[1]['edu'].keys()]
        self._edu_landmark = tk.Label(self._edu_frame, bg=self.non_active, image=self._edu_img[0])
        self._edu_landmark.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self._edu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self._house_frame = tk.Frame(self, width=int(self._screen_width / 2), height=int(self._screen_height / 2),
                               bg='lightgreen', relief=tk.RIDGE, borderwidth=2)
        self._electro_frame = tk.Frame(self._house_frame, width=400, height=400,
                                       bg=self.non_active, relief=tk.RIDGE, borderwidth=15)
        self._house_img = [house_logo for house_logo in self._activity_images[2]['house'].keys()]
        self._electro_landmark = tk.Label(self._electro_frame, bg=self.non_active, image=self._house_img[0])
        self._electro_landmark.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self._electro_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self._rest_frame = tk.Frame(self, width=int(self._screen_width / 2), height=int(self._screen_height / 2),
                              bg='lightblue', relief=tk.RIDGE, borderwidth=2)
        self._concert_frame = tk.Frame(self._rest_frame, width=400, height=400,
                                       bg=self.non_active, relief=tk.RIDGE, borderwidth=15)
        self._rest_img = [rest_logo for rest_logo in self._activity_images[3]['rest'].keys()]
        self._rest_landmark = tk.Label(self._concert_frame, bg=self.non_active, image=self._rest_img[0])
        self._rest_landmark.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self._concert_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        '''
        Точка перетину всіх Frame -
        орієнтир переходу до нової операції
        '''
        self.landmarkMain = tk.Label(self, bg='red', width=1, height=1)
        self.landmarkMain.place(relx=0.5, rely=0.52, anchor=tk.CENTER)
        tk.Tk.update(self)
        self.center = (self.landmarkMain.winfo_rootx(), self.landmarkMain.winfo_rooty())

        self.eyeLabel = tk.Label(self._shop_frame, text='Eye Pos: ')
        self.eyeLabel.place(relx=0, rely=0)

        self._shop_frame.grid(row=0, column=0, sticky=tk.NW)
        self._education_frame.grid(row=0, column=1, sticky=tk.NE)
        self._house_frame.grid(row=1, column=0, sticky=tk.SW)
        self._rest_frame.grid(row=1, column=1, sticky=tk.SE)

        self._logger.warning('Eye Track Program starts')
        self._main()


    def _open_url(self, url):
        self._logger.warning(f'You opened {url}')
        webbrowser.open(url)

    def _flipper(self, landmark, frame_flipped, logos, name:str=None, img_key=None):
        landmark.place_forget()

        if isinstance(logos, list) :
            self._logger.warning('You choose Eat Category')

            shop_silpo = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)
            silpo_btn = tk.Button(shop_silpo, bg='#FFA07A', image=logos[0], command=lambda: self._open_url(
                'https://shop.silpo.ua/?gclid=CjwKCAiAxreqBhAxEiwAfGfndGv0w0T1m4C1Ke0ZeLMkRZ8YTCFii2nckcPH9kj0P0HlKIyuKEA6GxoCkrIQAvD_BwE'))
            silpo_btn.pack(anchor=tk.CENTER)

            shop_fora = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)

            fora_btn = tk.Button(shop_fora, bg='#90EE90', image=logos[1],
                                 command=lambda: self._open_url(
                                     'https://shop.fora.ua/?utm_source=google&utm_medium=cpc&utm_campaign=Ukr-Srch-Brand-Fora&utm_content=gid_141971809650_g_c_21114&utm_term=%D1%84%D0%BE%D1%80%D0%B0_p__kwd-43569792099&gclid=CjwKCAiAxreqBhAxEiwAfGfndCh6UDToTmBnMeRTRvq6Px8TcBZ_Ptd9eFtC1CSTyKyLwd4PXTW5VBoCW1oQAvD_BwE'))
            fora_btn.pack(anchor=tk.CENTER)

            shop_atb = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)
            atb_btn = tk.Button(shop_atb, bg='#AFEEEE', image=logos[2],
                                command=lambda: self._open_url('https://www.atbmarket.com/'))
            atb_btn.pack(anchor=tk.CENTER)

            shop_metro = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)
            metro_btn = tk.Button(shop_metro, bg='#0000FF', image=logos[3],
                                  command=lambda: self._open_url('https://metro.zakaz.ua/uk/'))
            metro_btn.pack(anchor=tk.CENTER)

            shop_silpo.grid(row=0, column=0, sticky=tk.NW)
            shop_fora.grid(row=0, column=1, sticky=tk.NE)
            shop_atb.grid(row=1, column=0, sticky=tk.SW)
            shop_metro.grid(row=1, column=1, sticky=tk.SE)
        elif isinstance(logos, dict) :
            if name == 'edu' :
                self._logger.warning('You choose Education Category')

                edu_frame = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)
                edu_btn = tk.Button(edu_frame, image=logos[name].get(img_key),
                                     command=lambda : self._open_url('https://osvita.ua/'))

                edu_btn.pack(anchor=tk.CENTER)
                edu_frame.grid(row=0, column=0, sticky=tk.NSEW)
            elif name == 'house' :
                self._logger.warning('You choose House Category')

                rozetka_frame = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)

                rozetka_btn = tk.Button(rozetka_frame, image=logos[name][img_key].get('rozetka'),
                                     command=lambda : self._open_url('https://rozetka.com.ua/ua/'))

                rozetka_btn.pack(anchor=tk.CENTER)
                rozetka_frame.grid(row=0, column=0, sticky=tk.W)

                comfy_frame = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)

                comfy_btn = tk.Button(comfy_frame, image=logos[name][img_key].get('comfy'),
                                     command=lambda : self._open_url('https://comfy.ua/ua/korostyshiv/'))

                comfy_btn.pack(anchor=tk.CENTER)
                comfy_frame.grid(row=0, column=1, sticky=tk.E)
            elif name == 'rest' :
                self._logger.warning('You choose Rest Category')

                rest_frame = tk.Frame(frame_flipped, width=400, height=400, relief=tk.RIDGE, borderwidth=2)
                rest_btn = tk.Button(rest_frame, image=logos[name].get(img_key),
                                     command=lambda : self._open_url('https://kontramarka.ua/uk'))

                rest_btn.pack(anchor=tk.CENTER)
                rest_frame.grid(row=0, column=0, sticky=tk.NSEW)

    def _main(self) :
        face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)  # виявлення 3-ох координат в просторі 468 точок
        cam = cv2.VideoCapture(0)

        while True:
            _, frame = cam.read()  # ігнорування першого аргументу
            frame = cv2.flip(frame, 1)  # вертикальний поворот
            rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_detector = face_mesh.process(rgbFrame)  # розпізнавання обличчя людини
            landmarks = face_detector.multi_face_landmarks  # виявлення орієнтирів обличчя

            if landmarks:
                single_face = face_detector.multi_face_landmarks[0].landmark

                cX = single_face[476].x + (single_face[474].x - single_face[476].x) / 2
                cY = single_face[475].y + (single_face[477].y - single_face[475].y) / 2
                self.update()

                '''Calculate eye position'''
                eye_pos = (cX, cY)
                eye_pos_homo = np.append(eye_pos, 1)
                pos_norm = self.homoMatrix.dot(eye_pos_homo)  # tx, ty, tz - гомогенні координати

                xCentroid, yCentroid = None, None
                if self.algorithm == "Центроїд" :
                    xCentroid, yCentroid = self.ctr.out_filter(int(pos_norm[0] / pos_norm[2]), int(pos_norm[1] / pos_norm[2]))
                if self.algorithm == "МНК" :
                    xCentroid, yCentroid = self.ctr.out_filterMNK(int(pos_norm[0] / pos_norm[2]), int(pos_norm[1] / pos_norm[2]))

                if xCentroid < 0: xCentroid = 0
                if xCentroid > self._screen_width: xCentroid = self._screen_width

                if yCentroid < 0: yCentroid = 0
                if yCentroid > self._screen_height: yCentroid = self._screen_height

                pyautogui.moveTo(xCentroid, yCentroid)
                self.eyeLabel.configure(text=f'Eye Pos: ({int(xCentroid)}, {int(yCentroid)})')

                '''Кліпання лівого ока - вибір нової операції'''
                left_eye = [single_face[145], single_face[159]]
                blink = left_eye[0].y - left_eye[1].y  # різниця між краями лівого ока - признак кліпання ока
                blink_threshold = 0.01  # все, що менше порогу - ознака кліпання ока
                if blink < blink_threshold:
                    pyautogui.click()
                    self.config(cursor='hand2')
                    self.update()

                    if xCentroid < self.center[0] and yCentroid < self.center[1]:
                        self._eat_frame.configure(bg=self.active)
                        self._eat_landmark.configure(bg=self.active)
                        self.update()
                        self.after(2000, self._flipper(self._eat_landmark, self._eat_frame, self._logos))

                        self._edu_frame.configure(bg=self.non_active)
                        self._edu_landmark.configure(bg=self.non_active)
                        self._electro_frame.configure(bg=self.non_active)
                        self._electro_landmark.configure(bg=self.non_active)
                        self._concert_frame.configure(bg=self.non_active)
                        self._rest_landmark.configure(bg=self.non_active)
                    elif xCentroid > self.center[0] and yCentroid < self.center[1]:
                        self._edu_frame.configure(bg=self.active)
                        self._edu_landmark.configure(bg=self.active)
                        self.update()
                        self.after(2000, self._flipper(self._edu_landmark, self._edu_frame, self._activity_images[1], name='edu', img_key=self._edu_img[0]))

                        self._eat_frame.configure(bg=self.non_active)
                        self._eat_landmark.configure(bg=self.non_active)
                        self._electro_frame.configure(bg=self.non_active)
                        self._electro_landmark.configure(bg=self.non_active)
                        self._concert_frame.configure(bg=self.non_active)
                        self._rest_landmark.configure(bg=self.non_active)
                    elif xCentroid < self.center[0] and yCentroid > self.center[1]:
                        self._electro_frame.configure(bg=self.active)
                        self._electro_landmark.configure(bg=self.active)
                        self.update()
                        self.after(2000, self._flipper(self._electro_landmark, self._electro_frame, self._activity_images[2], name='house', img_key=self._house_img[0]))

                        self._edu_frame.configure(bg=self.non_active)
                        self._edu_landmark.configure(bg=self.non_active)
                        self._eat_frame.configure(bg=self.non_active)
                        self._eat_landmark.configure(bg=self.non_active)
                        self._concert_frame.configure(bg=self.non_active)
                        self._rest_landmark.configure(bg=self.non_active)
                    elif xCentroid > self.center[0] and yCentroid > self.center[1]:
                        self._concert_frame.configure(bg=self.active)
                        self._rest_landmark.configure(bg=self.active)
                        self.update()
                        self.after(2000, self._flipper(self._rest_landmark, self._concert_frame, self._activity_images[3], name='rest', img_key=self._rest_img[0]))

                        self._edu_frame.configure(bg=self.non_active)
                        self._edu_landmark.configure(bg=self.non_active)
                        self._eat_frame.configure(bg=self.non_active)
                        self._eat_landmark.configure(bg=self.non_active)
                        self._electro_frame.configure(bg=self.non_active)
                        self._electro_landmark.configure(bg=self.non_active)


                self.config(cursor='arrow')
                self.update()

            if cv2.waitKey(20) == 27: break

        cam.release()
        cv2.destroyAllWindows()
        self._logger.warning('Eye Track Program finishes')

    def __call__(self) : tk.mainloop()
