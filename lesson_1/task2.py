"""
2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
"""
def print_list_words_length_type(words: list) -> None:

    for word in words:
        print("Слово:", word, "Длина:", len(word), "Тип:", type(word))

list_words_type_byte = [
        b"class",
        b"function",
        b"method",
        ]

print_list_words_length_type(list_words_type_byte)


