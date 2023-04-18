# -*- coding: utf-8 -*-
#Source: https://gist.github.com/baskiton/6d361f4155f41e91c4be1dce897f7431
from typing import List
from math import log2, ceil
from random import randrange
from crc64iso.crc64iso import crc64


def __hamming_common(src: List[List[int]], s_num: int, encode=True) -> int:
    s_range = range(s_num)
    errors = 0

    for i in src:
        sindrome = 0
        for s in s_range:
            sind = 0
            for p in range(2 ** s, len(i) + 1, 2 ** (s + 1)):
                for j in range(2 ** s):
                    if (p + j) > len(i):
                        break
                    sind ^= i[p + j - 1]

            if encode:
                i[2 ** s - 1] = sind
            else:
                sindrome += (2 ** s * sind)

        if (not encode) and sindrome:
            try:
                i[sindrome - 1] = int(not i[sindrome - 1])
            except IndexError:
                errors += 1

    return errors


def hamming_encode(msg: str, mode: int = 8) -> str:
    """
    Encoding the message with Hamming code.
    :param msg: Message string to encode
    :param mode: number of significant bits
    :return:
    """

    result = ""
    msg_b = msg.encode("utf8")
    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # number of control bits
    bit_seq = []
    for byte in msg_b:  # get bytes to binary values; every bits store to sublist
        bit_seq += list(map(int, f"{byte:08b}"))

    res_len = ceil((len(msg_b) * 8) / mode)  # length of result (bytes)
    bit_seq += [0] * (res_len * mode - len(bit_seq))  # filling zeros

    to_hamming = []

    for i in range(res_len):  # insert control bits into specified positions
        code = bit_seq[i * mode:i * mode + mode]
        for j in range(s_num):
            code.insert(2 ** j - 1, 0)
        to_hamming.append(code)

    errors = __hamming_common(to_hamming, s_num, True)  # process

    for i in to_hamming:
        result += "".join(map(str, i))

    return result


def hamming_decode(msg: str, mode: int = 8):
    """
    Decoding the message with Hamming code.
    :param msg: Message string to decode
    :param mode: number of significant bits
    :return:
    """

    result = ""

    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # number of control bits
    res_len = len(msg) // (mode + s_num)  # length of result (bytes)
    code_len = mode + s_num  # length of one code sequence

    to_hamming = []

    for i in range(res_len):  # convert binary-like string to int-list
        code = list(map(int, msg[i * code_len:i * code_len + code_len]))
        to_hamming.append(code)

    errors = __hamming_common(to_hamming, s_num, False)  # process

    for i in to_hamming:  # delete control bits
        for j in range(s_num):
            i.pop(2 ** j - 1 - j)
        result += "".join(map(str, i))

    msg_l = []

    for i in range(len(result) // 8):  # convert from binary-sring value to integer
        val = "".join(result[i * 8:i * 8 + 8])
        msg_l.append(int(val, 2))

    try:
        result = bytes(msg_l).decode("utf8")
    except UnicodeDecodeError:
        pass

    return result, errors


def noizer(msg: str, mode: int) -> str:
    """
    Generates an error in each element of a Hamming encoded message
    """
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # количество служебных битов
    code_len = mode + s_num  # длина кодового слова
    cnt = len(msg) // code_len
    result = ""

    for i in range(cnt):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize = randrange(code_len)
        to_noize[noize] = int(not to_noize[noize])
        result += "".join(map(str, to_noize))

    return result


def noizer3(msg: str, mode: int) -> str:
    """
    Generates up to 2 errors in each element of a Hamming encoded message
    """
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    cnt = len(msg) // code_len
    result = ""

    for i in range(cnt):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize1 = randrange(code_len)
        noize2 = randrange(code_len)


        to_noize[noize1] = int(not to_noize[noize1])
        to_noize[noize2] = int(not to_noize[noize2])

        result += "".join(map(str, to_noize))

    return result


if __name__ == '__main__':
    MODE = 120  # Всего 127. Исключаем 1,2,4,8,16,32,64. Остается 120
    msg = 'Допустим, у нас есть сообщение «habr», которое необходимо передать без ошибок. ' \
          'Для этого сначала нужно наше сообщение закодировать при помощи Кода Хэмминга. ' \
          'Нам необходимо представить его в бинарном виде. На этом этапе стоит определиться с, так называемой, ' \
          'длиной информационного слова, то есть длиной строки из нулей и единиц, которые мы будем кодировать. ' \
          'Допустим, у нас длина слова будет равна 16. Таким образом, нам необходимо разделить наше  ' \
          'исходное сообщение («habr») на блоки по 16 бит, которые мы будем потом кодировать отдельно друг  ' \
          'от друга. Так как один символ занимает в памяти 8 бит, то в одно кодируемое слово помещается ровно два ASCII символа. ' \
          'Итак, мы получили две бинарные строки по 16 бит: После этого процесс кодирования распараллеливается, ' \
          'и две части сообщения («ha» и «br») кодируются независимо друг от друга. Рассмотрим, как это делается на примере первой части. ' \
          'Прежде всего, необходимо вставить контрольные биты. Они вставляются в строго определённых местах — это позиции с номерами,  ' \
          'равными степеням двойки. В нашем случае (при длине информационного слова в 16 бит) это будут позиции 1, 2, 4, 8, 16. ' \
          'Соответственно, у нас получилось 5 контрольных бит (выделены красным цветом): Таким образом, ' \
          'длина всего сообщения увеличилась на 5 бит. До вычисления самих контрольных бит, мы присвоили им значение «0». ' \
          'Теперь необходимо вычислить значение каждого контрольного бита. Значение каждого контрольного бита зависит ' \
          'от значений информационных бит (как неожиданно), но не от всех, а только от тех, которые этот контрольных бит контролирует. ' \
          'Для того, чтобы понять, за какие биты отвечает каждых контрольный бит необходимо понять очень простую закономерность: ' \
          'контрольный бит с номером N контролирует все последующие N бит через каждые N бит, начиная с позиции N. ' \
          'Не очень понятно, но по картинке, думаю, станет яснее: Здесь знаком «X» обозначены те биты, которые контролирует контрольный бит, ' \
          'номер которого справа. То есть, к примеру, бит номер 12 контролируется битами с номерами 4 и 8.  ' \
          'Ясно, что чтобы узнать какими битами контролируется бит с номером N надо просто разложить N по степеням двойки. ' \
          'Но как же вычислить значение каждого контрольного бита? Делается это очень просто: берём каждый контрольный бит и смотрим' \
          'сколько среди контролируемых им битов единиц, получаем некоторое целое число и, если оно чётное, то ставим ноль, в противном случае ставим единицу.'
    print(f'Начальное сообщение:\n{msg}')
    checksum = crc64(msg)
    print(f'Контрольная сумма: {checksum}')
    print()
    print('Отправка без ошибок')
    enc_msg = hamming_encode(msg, MODE)
    print(f'Кодированное сообщение:\n{enc_msg}')
    dec_msg, err = hamming_decode(enc_msg, MODE)
    dec_msg = dec_msg[:-1:]
    print(f'Декодированное сообщение:\n{dec_msg}')
    print(f'Контрольная сумма: {crc64(dec_msg)} ')
    print(f'Значения сумм совпадают:{crc64(dec_msg) == checksum}')
    print(f'Совпадение текстов: {msg == dec_msg}')
    print()
    print('Отправка не более 1 ошибки на слово')
    noize_msg = noizer(enc_msg, MODE)
    print(f'Кодированное сообщение с ошибками:\n{noize_msg}')
    dec_msg, err = hamming_decode(noize_msg, MODE)
    dec_msg = dec_msg[:-1:]
    print(f'Декодированное сообщение:\n{dec_msg}')
    print(f'Контрольная сумма: {crc64(dec_msg)} ')
    print(f'Значения сумм совпадают:{crc64(dec_msg) == checksum}')
    print(f'Совпадение текстов: {msg == dec_msg}')
    print()
    print('Отправка до 2 ошибок на каждое слово')
    noize_msg = noizer3(enc_msg, MODE)
    print(f'Кодированное сообщение с ошибками:\n{noize_msg}')
    dec_msg, err = hamming_decode(noize_msg, MODE)
    dec_msg = dec_msg[:-1:]
    print(f'Декодированное сообщение:\n{dec_msg}')
    print(f'Контрольная сумма: {crc64(dec_msg)} ')
    print(f'Значения сумм совпадают:{crc64(dec_msg) == checksum}')
    print(f'Количество обнаруженных ошибок: {err}')
