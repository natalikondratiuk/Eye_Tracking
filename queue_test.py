"""
Тестування алгоритмів фільтрації
кільцевої черги з використанням
синтетичних даних
до магістерського проекту
Кондратюк Наталії ПІ-22-1м
"""

import numpy as np
import matplotlib.pyplot as plt

from modules.data.queue_setup import FilterCenter

def test_queue() :
    """
    Тестування алгоритмів фільтрації
    на основі кільцевої черги
    :return:
    """

    mediapipe_points = np.array([
        [0.25891244, 0.2751783],
        [0.34671304, 0.25906067],
        [0.45463192, 0.2539763],
        [0.46548238, 0.3039763],
        [0.48297535, 0.36034049],
        [0.38702606, 0.37580551],
        [0.26290893, 0.39845074],
        [0.27030575, 0.32130253],
        [0.36526209, 0.31428277]
    ]) # нормалізовані координати точок спостереження

    '''Налаштування генератора випадкових точок'''
    qty = 30 # кількість спостережень
    mu = 0.01 # значення СКВ як розкид точок навколо центра

    ctr_len = 21
    ctr = FilterCenter(ctr_len, init_x=.5, init_y=.5) # черга заповнена значенням 0.5 (в координатах Mediapipe)

    '''Синтетичні дані, що моделюють роботу веб камери, генеруються за розподілом Гаусса'''
    plt.title('Mediapipe Points')
    for x, y in mediapipe_points :
        plt.scatter(x, y, s=5, marker='^')
        random_x = np.random.normal(loc=x, scale=mu, size=(1, qty))
        random_y = np.random.normal(loc=y, scale=mu, size=(1, qty))
        plt.scatter(random_x, random_y, s=5, marker='*')
        for tmp_x, tmp_y in zip(random_x[0], random_y[0]):
            ctr.add_point(tmp_x, tmp_y) # занесення випадкових точок до кільцевої черги

        plt.scatter(ctr.out_filter()[0], ctr.out_filter()[1], s=5, marker='s') # робота центроїда з штучними даними
        plt.scatter(ctr.out_filterMNK()[0], ctr.out_filterMNK()[1], s=5, marker='o') # робота МНК з штучними даними

    plt.legend(['Original Data', 'Random Data', 'Centroid Data', 'MNK Data'], loc=2)
    plt.gca().invert_yaxis()
    plt.show()

if __name__ == '__main__' :
    test_queue()