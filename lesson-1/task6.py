"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""

def write_str_to_file(file_name: str, list_of_data: list) -> None:
    file = open(file_name, "w")
    for words in list_of_data:
        file.write(words + "\n")
    file.close()
    print(f"Кодировка файла {file_name} по умолчанию:", str(file).split("encoding=")[1].split(">")[0])

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
read_file_in_unicode(file_name)


