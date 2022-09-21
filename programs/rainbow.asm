start:
  get_precise_time
  PEEK 0
  PUSHW 1000
  FDIV
  SIN
  PUSHB 0x1
  ADD
  PUSHB 0x7f
  MUL
  FLOOR
  PEEK 1
  PUSHW 0x82e
  ADD
  PUSHW 1000
  FDIV
  SIN
  PUSHB 0x1
  ADD
  PUSHB 0x7f
  MUL
  FLOOR
  PEEK 2
  PUSHW 0x105d
  ADD
  PUSHW 1000
  FDIV
  SIN
  PUSHB 0x01
  ADD
  PUSHB 0x7f
  MUL
  FLOOR
  SHL8
  ADD
  SHL8
  ADD
  set_all_pixels
  POP 1
  PUSHB 0xa
  sleep
  JMP start
