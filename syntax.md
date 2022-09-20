
# ISA Syntax

The ISA is based on code from the [PWLP](https://github.com/pixelspark/pwlp) repo, which was authored by [Tommy van der Vorst](https://github.com/pixelspark):

|      | opcode  | funct            | args  | documentation                          |
|      | [0:4]   | [5:8]            | [9:]  |                                        |
|______|_________|__________________|_______|________________________________________|
| 0x0* | POP     | *                |       | removes *th item from stack            |
| 0x10 | PUSHZ   |                  |       | push 0 onto stack                      |
| 0x11 | PUSHB   |                  | byte  | push byte onto stack                   |
| 0x2* | PEEK    | *                |       | copies *th item to top of stack        |
| 0x31 | PUSHW   |                  | word  | push word onto stack                   |
| 0x40 | JMP     |                  | short | jump to address                        |
| 0x50 | JZ      |                  | short | jump if equal to zero                  |
| 0x60 | JNZ     |                  | short | jump if not equal to zero              |
| 0x70 | UNARY   | INC              |       | add 1 to top of stack (TOS)            |
| 0x71 | UNARY   | DEC              |       | sub 1 from TOS                         |
| 0x72 | UNARY   | NOT              |       | bitwise invert TOS                     |
| 0x73 | UNARY   | NEG              |       | logical invert TOS                     |
| 0x74 | UNARY   | SHL8             |       | shift TOS left by eight bits           |
| 0x75 | UNARY   | SHR8             |       | shift TOS right by eight bits          |
| 0x80 | BINARY  | ADD              |       | add TOS and second from top            |
| 0x81 | BINARY  | SUB              |       | sub TOS from second from top           |
| 0x82 | BINARY  | DIV              |       | integer divide                         |
| 0x83 | BINARY  | MUL              |       |                                        |
| 0x84 | BINARY  | MOD              |       | remainder from integer division        |
| 0x85 | BINARY  | AND              |       |                                        |
| 0x86 | BINARY  | OR               |       |                                        |
| 0x87 | BINARY  | XOR              |       |                                        |
| 0x88 | BINARY  | GT               |       |                                        |
| 0x89 | BINARY  | GTE              |       |                                        |
| 0x8a | BINARY  | LT               |       |                                        |
| 0x8b | BINARY  | LTE              |       |                                        |
| 0x8c | BINARY  | EQ               |       |                                        |
| 0x8d | BINARY  | NEQ              |       |                                        |
| 0x8e | BINARY  | SHL              |       | shift left                             |
| 0x8f | BINARY  | SHR              |       | shift right                            |
| 0x90 | FLOAT   | FLOOR            |       | round TOS down to the nearest int      |
| 0x91 | FLOAT   | CEIL             |       | round TOS up to nearest int            |
| 0x92 | FLOAT   | SIN              |       | take the sin of TOS                    |
| 0x93 | FLOAT   | COS              |       | take the cos of TOS                    |
| 0x9f | FLOAT   | FDIV             |       | divide using floating-point division   |
| 0xe0 | USER    | get_length       |       | put number of leds on stack as int     |
| 0xe1 | USER    | get_wall_time    |       | put time in sec on stack as 64-bit int |
| 0xe2 | USER    | get_precise_time |       | put time in ms on stack as 64-bit int  |
| 0xe3 | USER    | set_pixel        |       |                                        |
| 0xe4 | USER    | show             |       | display updated led values             |
| 0xe5 | USER    | random_int       |       | push uniform random integer            |
| 0xe6 | USER    | get_pixel        |       |                                        |
| 0xe7 | USER    | set_all_pixels   |       |                                        |
| 0xf9 | SPECIAL | sleep            |       | sleep program in number of ms          |
| 0xfa | SPECIAL | exit             |       |                                        |
| 0xfb | SPECIAL | error            |       |                                        |
| 0xfc | SPECIAL | swap             |       |                                        |
| 0xfd | SPECIAL | dump             |       | dump stack to stdout (for debugging)   |
| 0xfe | SPECIAL | yield            |       |                                        |
| 0xff | SPECIAL | two_byte         |       |                                        |
