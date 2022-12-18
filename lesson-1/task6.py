"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""

from chardet import detect

def write_str_to_file(file_name: str, list_of_data: list) -> None:
    file = open(file_name, "w")
    for words in list_of_data:
        file.write(words + "\n")
    file.close()

def set_encoding_utf8(file_name: str) -> None:
    with open(file_name, "rb") as f_o:
        file_data = f_o.read()
    detected = detect(file_data)
    file_encoding = detected["encoding"]
    file_data_decode = file_data.decode(file_encoding)
    with open(file_name, "w", encoding="utf-8") as f_o:
        f_o.write(file_data_decode)
    

def read_file_in_unicode(file_name: str):
    with open(file_name, encoding='utf-8') as file:
        print(f"\nЧтение содержимого файла {file_name}:")
        for line in file:
            print(line, end="")

file_name = "test_file.txt"

list_of_words = [
        "сетевое программирование",
        "сокет",
        "декоратор",
        ]

write_str_to_file(file_name ,list_of_words)
set_encoding_utf8(file_name)
read_file_in_unicode(file_name)


