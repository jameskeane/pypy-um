import os
try:
    from rpython.rlib.rtermios import *
    def wrap_tcsetattr(fd, when, mode):
        tcsetattr(fd, when, mode)

except ImportError:
    from termios import * 
    def wrap_tcsetattr(fd, when, mode):
        tcsetattr(fd, when, list(mode))

# Indexes for termios list.
IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6

def _setraw(fd, when=TCSAFLUSH):
    """Put terminal into a raw mode."""
    mode = tcgetattr(fd)

    # rpython wants a tuple, when python wants a list...
    mode[CC][VMIN] = chr(1)
    mode[CC][VTIME] = chr(0)
    raw = (
        mode[IFLAG] & ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON),
        mode[OFLAG] & ~(OPOST),
        (mode[CFLAG] & ~(CSIZE | PARENB)) | CS8,
        mode[LFLAG] & ~(ECHO | ICANON | IEXTEN | ISIG),
        mode[ISPEED],
        mode[OSPEED],
        mode[CC]
    )
    wrap_tcsetattr(fd, when, raw)


def readchar(fd):
    old_mode = tcgetattr(fd)
    try:
        _setraw(fd)
        ch = os.read(fd, 1)[0]
    finally:
        tcsetattr(fd, TCSAFLUSH, old_mode)
    return ch
