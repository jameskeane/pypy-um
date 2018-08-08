inst_map = [
 'cmovnz', 'loada', 'seta', 'add', 'mul',
 'div', 'nand', 'hlt', 'alloc', 'free',
 'putc', 'getc', 'call', 'load'
]


def disasm(bc):
  inst = (bc >> 28) & 0xf 
  rA   = (bc >> 6)  & 0x7
  rB   = (bc >> 3)  & 0x7
  rC   = (bc >> 0)  & 0x7
  sA   = (bc >> 25) & 0x7
  sv   = (bc & 0x1ffffff)

  # print '{:04b} {:03b} {:03b} {:03b}'.format(inst, rA, rB, rC)
  if inst == 13:
    return [inst, sA, 0, 0, sv]
  else:
    return [inst, rA, rB, rC, 0]

def mnemonize(bc):
  [inst, A, B, C, imm] = disasm(bc)
  mne = inst_map[inst]
  if inst == 13:
    return "mov r%s, %sh" % (A, hex(imm)[2:])
  elif inst == 1:
    return "mov r%s, [r%s * r%s]" % (A, B, C)
  elif inst == 2:
    return "mov [r%s * r%s], r%s" % (A, B, C)
  elif inst == 12:
    return "call [r%s * r%s]" % (B, C)
  else:
    return "%s r%s, r%s, r%s" % (mne, A, B, C)

if __name__ == "__main__":
  import sys
  import struct

  with open(sys.argv[1]) as f:
    bs = f.read(4)
    while (bs != ''):
      i = struct.unpack(">I", bs)[0]
      print mnemonize(i)
      bs = f.read(4)
