#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

def pyc_read(file_path):
    with open(file_path, 'rb') as f:
        # 读取前4个字节作为magic number
        magic = f.read(4)
        magic = struct.unpack('I', magic)[0]
        r = ~(ord('\r') << 16)
        n = ~(ord('\n') << 24)
        print(type(r), type(n))
        print('magic number:', magic)
        magic = magic & r
        magic = magic & n
        print('magic number:', magic)

        # 读取后4个字节作为时间戳
        timestamp = f.read(4)
        timestamp = struct.unpack('I', timestamp)[0]
        print('timestamp:', timestamp)

        # 读取后4个字节作为文件大小
        size = f.read(4)
        size = struct.unpack('I', size)[0]
        print('size:', size)

        # 读取文件
        code = f.read()
        print('code:', code)

if __name__ == '__main__':
    pyc_read('./__pycache__/add.cpython-312.pyc')
