from PIL import Image, ImageTk
from dataclasses import dataclass
from typing import List

@dataclass
class ShopDownloader :
    """
    Клас-завантажувач логотипів
    доступних магазинів
    """

    def __init__(self) :
        self._logo_silpo = 'Shops\\silpo_logo200.png'
        self._shop_silpo = ImageTk.PhotoImage(Image.open(self._logo_silpo))

        self._logo_fora= 'Shops\\fora_logo200.png'
        self._shop_fora = ImageTk.PhotoImage(Image.open(self._logo_fora))

        self._logo_atb = 'Shops\\atb_logo200.png'
        self._shop_atb = ImageTk.PhotoImage(Image.open(self._logo_atb))

        self._logo_metro = 'Shops\\metro_logo200.png'
        self._shop_metro = ImageTk.PhotoImage(Image.open(self._logo_metro))

        self._shop_logo : List = []

    def set_image(self):
        self._shop_logo.append(self._shop_silpo)
        self._shop_logo.append(self._shop_fora)
        self._shop_logo.append(self._shop_atb)
        self._shop_logo.append(self._shop_metro)

    @property
    def get_image(self):
        self.set_image()
        return self._shop_logo