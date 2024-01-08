import numpy as np

class FilterCenter :
    """
    Створення кільцевої черги
    для калібрування системи Eye Tracking
    """

    def __init__(self, k) :
        self.k = k # кільцева черга на основі масиву фіксованої довжини, де k - його довжина

        '''Масиви aX та aY проініціалізовані серединою екрану:'''
        self.aX = np.full((self.k), 960) # 1) ширина екрану / 2
        self.aY = np.full((self.k), 540) # 2) висота екрану / 2
        self.tail = 0 # хвіст черги - інкрементується внаслідок додавання нового елементу до черги

        self.historyX = []
        self.historyY = []

    def add_point(self, x, y):
        """
        Додавання нової точки до черги
        :param x: Ох точки
        :param y: Оу точки
        :return:
        """

        self.x = x
        self.y = y

        '''Нова точка в черзі'''
        self.aX[self.tail] = self.x
        self.aY[self.tail] = self.y
        self.tail = self.tail + 1 if self.tail < self.k-1 else 0 # хвіст черги вказує на наступний елемент черги

    def out_filter(self, x, y):
        """
        Пошук центроїду черги
        :param x: Ох точки
        :param y: Оу точки
        :return: центроїд черги
        """

        self.x = x
        self.y = y

        '''Нова точка в черзі'''
        self.aX[self.tail] = self.x
        self.aY[self.tail] = self.y
        self.tail = self.tail + 1 if self.tail < self.k-1 else 0

        return np.average(self.aX), np.average(self.aY)

    def MNK(self, arr, tail) :
        """
        МНК-згладжування
        як один з алгоритмів зменшення
        аномальних рухів курсора
        :param arr: черга (історія координат очей)
        :param tail: поточний хвіст черги
        :return: прогнозоване значення МНК - останній елемент масиву МНК
        """

        '''
        Підготовка масиву черги до МНК-згладжування:
        елементи в порядку їхнього надходження до черги
        '''
        arrList = arr.tolist()
        arrMNK = []
        arrMNK.extend(arrList[tail:])
        arrMNK.extend(arrList[:tail])

        '''МНК-згладжування'''
        length = len( arrMNK ) # довжина масиву вхідної функції (створеного масиву)
        funcIn = np.zeros( (length, 1) ) # матриця вхідних даних
        pointsF = np.ones( (length, 3) ) # матриця: ф-ція, аргумент ф-ції, квадрат ф-ції (поліном 2-го ступеню)

        for i in range( length ) :
            funcIn[i, 0] = float( arrMNK[i] ) # значення ф-ції

            pointsF[i, 1] = float( i ) # аргумент ф-ції
            pointsF[i, 2] = float( i*i ) # квадрат ф-ції

        '''
        Критерій мінімізації суми квадратів різниць лівої і правої частини рівнянь:
        АТ*АХ = АТ*b => x = (AT*A)^-1*AT*b
        А+*b, А+ - псевдообернена матриця
        '''
        pointsFT = pointsF.T # транспонована матриця (апроксимуючої) ф-ції
        pointsFTP = pointsFT.dot( pointsF ) # AT*A
        pointsFTPInv = np.linalg.pinv( pointsFTP ) # мультиплікативна обернена матриця
        pointsMNK = pointsFTPInv.dot( pointsFT ) # А+*b, А+ - псевдообернена матриця

        c = pointsMNK.dot( funcIn ) # коефцієнти для регресійної моделі
        funcMNK = pointsF.dot( c ) # згладжування ф-ції за коефіцієнтами регресійної моделі

        return funcMNK[-1, 0]

    def out_filterMNK(self, x, y):
        self.x = x
        self.y = y
        self.aX[self.tail] = self.x
        self.aY[self.tail] = self.y
        self.tail = self.tail + 1 if self.tail < self.k-1 else 0

        return self.MNK(self.aX, self.tail), self.MNK(self.aY, self.tail)

    def outNumPoints(self): return self.aX, self.aY

    def printCenter(self):
        for i in range(self.k): print(f'({self.aX[i]}, {self.aY[i]}), ', end='')
        print()