"""Модуль содержит функции для преобразования изображения в вектор и функции
работы с векторами."""

import pickle
from pygame import surfarray, image

SIZE = 300  # ширина и высота преобразованного изображения
NORM = 255  # нормировочный коэффициент для элементов массива


def get_pix_pos(pos, k):
    """Функция получает номера пикселей исходного изображения, которые
    соответствуют пикселю изображения с новыми размерами.
    :param pos: номер пикселя по оси в новом изображении;
    :param k: отношение размера исходного изображения к размеру нового.
    :return: пиксели исходного изображения, соответствующие заданному пикселю
    нового."""

    if k >= 1:
        if int(pos) < pos:
            pos0 = int(pos) + 1
        else:
            pos0 = int(pos)
        if int(pos + k) < pos + k:
            pos_end = int(pos + k) + 1
        else:
            pos_end = int(pos + k)
        return range(pos0, pos_end)
    else:
        return [int(pos / k)]


def process_image(file):
    """Функция обрабатывает изображение и преобразует его в массив.
    :param file: файл-изображение.
    :return: сериализованный массив."""

    # Получаем данные о пикселях изображения
    img = image.load(file)
    rgb = surfarray.pixels3d(img)
    # Ширина и высот исходного изображения
    WIDTH = img.get_width()
    HEIGHT = img.get_height()
    # Отношение исходных размеров к новым
    kx = WIDTH / SIZE
    ky = HEIGHT / SIZE
    # Вычисляем массив для изображения
    array = []
    for x in range(SIZE):
        # Пиксели по горизонтали из старого изображения, которые нужно учесть
        # в пикселе нового изображения
        xs = get_pix_pos(x * kx, kx)
        for y in range(SIZE):
            r = g = b = 0  # RGB цвета в пикселе нового изображения
            # Пиксели по вертикали из старого изображения, которые нужно учесть
            # в пикселе нового изображения
            ys = get_pix_pos(y * ky, ky)
            n = 0
            for x_old in xs:
                if x_old >= WIDTH:
                    break
                for y_old in ys:
                    if y_old >= HEIGHT:
                        break
                    r += rgb[x_old][y_old][0]
                    g += rgb[x_old][y_old][1]
                    b += rgb[x_old][y_old][2]
                    n += 1
            r = round(r / n) / NORM
            g = round(g / n) / NORM
            b = round(b / n) / NORM
            array.append([r, g, b])
    # Сериализуем массив
    return pickle.dumps(array)


def get_euclid(a1, a2):
    """Функция вычисляет евклидово расстояние между двумя векторами.
    :param array1, array2: два сериализованных вектора.
    :return: евклидово расстояние между векторами."""

    array1 = pickle.loads(a1)
    array2 = pickle.loads(a2)
    distance = 0
    for i in range(len(array1)):
        for color in range(3):
            distance += pow(array1[i][color] - array2[i][color], 2)
    return distance
