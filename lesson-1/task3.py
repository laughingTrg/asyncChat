"""
3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
"""
def convert_list_in_bytes(words: list) -> None:

    for word in words:
        try:
            word = bytes(word, 'ascii')
        except UnicodeEncodeError:
            print("Слово", word, "невозможно записать в байтовом типе.")
list_of_words = [
        "attribute",
        "класс",
        "функция",
        "type",
        ]

convert_list_in_bytes(list_of_words)
