"""
4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""
def decode_encode_list_words(words: list) -> None:

    for word in words:
        print(f"----encode {word}----")
        word = word.encode('utf-8')
        print("Encode in utf-8:", word)
        print("----decode----")
        word = word.decode('utf-8')
        print("Decode from utf-8:", word, "\n")


list_words = [
        "разработка",
        "администрирование",
        "protocol",
        "standard",
        ]

decode_encode_list_words(list_words)
