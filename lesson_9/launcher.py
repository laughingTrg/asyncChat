"""Программа-лаунчер"""

import subprocess

PROCESSES = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   't - запуск 2-х тестовых клиентов и сервера'
                   's - запустить сервер и количество указанных клиентов, '
                   'x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 't':
        PROCESSES.append(subprocess.Popen('python3 data_server_jim.py', shell=True))
        PROCESSES.append(subprocess.Popen('python3 data_client_jim.py -n test1', shell=True))
        PROCESSES.append(subprocess.Popen('python3 data_client_jim.py -n test2', shell=True))
    elif ACTION == 's':
        number_of_clients = int(input("Введите необходимое количество клиентов: "))
        PROCESSES.append(subprocess.Popen('python data_server_jim.py', shell=True))
        for client in range(number_of_clients):

            PROCESSES.append(subprocess.Popen(f'python data_client_jim.py -n Guest{client}', shell=True))

    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
