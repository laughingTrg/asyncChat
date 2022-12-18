"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на кириллице.
"""
import subprocess

def print_ping_host(args: list) -> None:
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        print(line.decode('utf-8'))




list_args = [
        ["ping", "-c", "5", "-n", "yandex.ru"],
        ["ping", "-c", "5", "-n", "youtube.com"],
        ]

for args in list_args:
    print_ping_host(args)
