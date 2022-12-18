"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv(). 
"""

from chardet import detect
import re
import csv

search_prod = re.compile("Изготовитель системы:\W+([a-zA-Z]+)")
search_name = re.compile("Название ОС:\W+([\w\d\ ]+)")
search_code = re.compile("Код продукта:\W+([\w\d\-\ ]+)")
search_type = re.compile("Тип \w+:\W+([\w\d\-\ ]+)")

headers = ["Изготовитель системы", 
           "Название ОС", 
           "Код продукта", 
           "Тип системы"
           ]

CSV_FILE = "main_data.csv"



list_of_filenames = [
        "info_1.txt",
        "info_2.txt",
        "info_3.txt",
        ]

def search_el_in_text(template, text):
    el = template.findall(text)
    return el

def decode_content_data(content_data):
    detected = detect(content_data)
    encoding = detected["encoding"]
    return content_data.decode(encoding)
    

def get_data(list_of_filenames: list) -> list:
    os_prod_list = [] 
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []
    
    for filename in list_of_filenames:
        with open(filename, "rb") as f_o:
            content_data = f_o.read()

        content_text = decode_content_data(content_data) 

        os_prod_list.append(search_el_in_text(search_prod, content_text)[0])
        os_name_list.append(search_el_in_text(search_name, content_text)[0])
        os_code_list.append(search_el_in_text(search_code, content_text)[0])
        os_type_list.append(search_el_in_text(search_type, content_text)[0])

    main_data.append(headers)

    for val in range(len(headers)-1):
        append_list = []
        append_list.append(os_prod_list[val])
        append_list.append(os_name_list[val])
        append_list.append(os_code_list[val])
        append_list.append(os_type_list[val])
        main_data.append(append_list)

    return main_data

def write_to_csv(csv_filename: str):
    csv_data = get_data(list_of_filenames)    
    with open(csv_filename, "w") as f_o:
        f_o_writer = csv.writer(f_o)
        for row in csv_data:
            f_o_writer.writerow(row)

def read_from_csv(csv_filename: str):
    with open(csv_filename) as f_o:
        print(f_o.read())

write_to_csv(CSV_FILE)
read_from_csv(CSV_FILE)



