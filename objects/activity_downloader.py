from PIL import Image, ImageTk
from dataclasses import dataclass
from typing import List

@dataclass
class ActivityDownloader :
    """
    Клас-завантажувач логотипів
    доступних операцій та
    відповідних Інтернет-ресурсів
    """

    def __init__(self) :
        self._eatPath = 'Activities\\EatTrans.png'
        self._eating = ImageTk.PhotoImage(Image.open(self._eatPath))

        self._readPath = 'Activities\\Read360.png'
        self._reading = ImageTk.PhotoImage(Image.open(self._readPath))
        self._osvitaPath = 'Activities\\osvita360.jpg'
        self._osvita = ImageTk.PhotoImage(Image.open(self._osvitaPath))
        self._edu_dict = {'edu' : {self._reading: self._osvita}}

        self._housePath = 'Activities\\house_techno360.png'
        self._house = ImageTk.PhotoImage(Image.open(self._housePath))
        self._rozetkaPath = 'Activities\\rozetka200.png'
        self._rozetka = ImageTk.PhotoImage(Image.open(self._rozetkaPath))
        self._comfyPath = 'Activities\\comfy200.png'
        self._comfy = ImageTk.PhotoImage(Image.open(self._comfyPath))
        self._house_dict = {'house' : {self._house :
                                           {'rozetka' : self._rozetka,
                                            'comfy' : self._comfy}
                                       }}

        self._restPath = 'Activities\\RestTrans.png'
        self._rest = ImageTk.PhotoImage(Image.open(self._restPath))
        self._kontramarkaPath = 'Activities\\kontramarka360.jpg'
        self._kontramarka = ImageTk.PhotoImage(Image.open(self._kontramarkaPath))
        self._rest_dict = {'rest' : {self._rest : self._kontramarka}}

        self._activity_images : List = []

    def set_image(self):
        self._activity_images.append(self._eating)
        self._activity_images.append(self._edu_dict)
        self._activity_images.append(self._house_dict)
        self._activity_images.append(self._rest_dict)

    @property
    def get_image(self):
        self.set_image()
        return self._activity_images