from disasm import disasm, mnemonize
import os, sys

# So that you can still run this module under standard CPython
try:
    from rpython.rlib.jit import JitDriver, hint
except ImportError:
    class JitDriver(object):
        def __init__(self,**kw): pass
        def jit_merge_point(self,**kw): pass
        def can_enter_jit(self,**kw): pass


def get_location(pc, mem):
    return mnemonize(mem[0][pc])


jitdriver = JitDriver(greens=['pc', 'mem'], reds=['r'],
        get_printable_location=get_location)


def interp(prog):
  r = [0, 0, 0, 0, 0, 0, 0, 0]
  mem = [prog]
  pc = 0

  while True:
    jitdriver.jit_merge_point(pc=pc, r=r, mem=mem)

    [inst, A, B, C, imm] = disasm(mem[0][pc])

    if inst == 0:                     # cmovnz
      if r[C] != 0: r[A] = r[B]
    elif inst == 1:                   # mov rA, [rB * rC]
      r[A] = mem[r[B]][r[C]]
    elif inst == 2:                   # mov [rA * rB], rC
      mem[r[A]][r[B]] = r[C]
    elif inst == 3:                   # add rA <- rB + rC
      r[A] = (r[B] + r[C]) % (2 ** 32)
    elif inst == 4:                   # mul rA <- rB * rC
      r[A] = (r[B] * r[C]) % (2 ** 32)
    elif inst == 5:                   # div rA <- rB / rC
      r[A] = r[B] / r[C]
    elif inst == 6:                   # nand rA <- ~(rB & rC)
      r[A] = (~(r[B] & r[C])) & 0xffffffff
    elif inst == 7:                   # hlt
      break
    elif inst == 8:                   # alloc rB = *arr[rC]
      i = len(mem)
      mem.append([0] * r[C])
      r[B] = i
    elif inst == 9:                   # free rC
      mem[r[C]] = None
    elif inst == 10:                  # putc
      os.write(1, chr(r[C]))
    elif inst == 11:                  # getc
      r[C] = ord(os.read(0, 1)[0])
    elif inst == 12:                  # load [rB * rC]
      if r[B] != 0:
        mem[0] = mem[r[B]][:]
      else:
        # A simple jump, if backwards we can enter jit
        pass # jitdriver.can_enter_jit(...)
      pc = r[C]
      continue
    elif inst == 13:                  # mov rA, imm
      r[A] = imm
    else:
      print 'bad opcode %s' % inst

    # Can use this for debugging, i.e. `interp.py ... 2> trace`
    # sys.stderr.write(mnemonize(mem[0][pc]))
    # sys.stderr.write('\n')
    pc += 1


def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    # read the bytecode from the file
    fd = os.open(filename, os.O_RDONLY, 0777)
    bc = []
    while True:
        bs = os.read(fd, 4)
        if len(bs) == 0: break

        uint = (ord(bs[0]) << 24) | (ord(bs[1]) << 16) | (ord(bs[2]) << 8) | ord(bs[3])
        bc.append(uint)
    os.close(fd)

    interp(bc)
    return 0


def target(*args):
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
