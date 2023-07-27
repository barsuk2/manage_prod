import re

import numpy as np
import pytesseract
from PIL import Image

# Открываем изображение с текстом
image = Image.open('/home/egor/PDF/result/Pagea_asd3.pdf')

# Преобразуем изображение в массив numpy
image_array = np.array(image)

# Распознаем текст на изображении
text = pytesseract.image_to_string(image_array, lang='rus')

# Выводим распознанный текст
match = re.search('(?P<name>[А-ЯЁ][а-яё]+)\s(?P<lastname>[А-ЯЁ][а-яё]+)\s(?P<fatherland>[А-ЯЁ][а-яё]+)\s\((?P<birthdate>\d{2}.\d{2}.\d{4}).+\)', text)


if match:
    name = match.group('name')
    surname = match.group('lastname')
    fatherland = match.group('fatherland')
    birthdate = match.group('birthdate')

    print("Имя:", name)
    print("Фамилия:", surname)
    print("Отчество:", fatherland)
    print("Отчество:", birthdate)
else:
    print("Не удалось найти имя, фамилию и дату рождения")
