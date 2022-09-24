	PUSHW 0x404040     # [ffffff00]
	PUSHB 25           # [25, ffffff00]
	PEEK 1             # [ffffff00, 25, ffffff00]
	set_pixel          # [25, ffffff00]
	POP 1              # [ffffff00]

loop:
	PUSHZ              # [0, ffffff00]
inner_loop:
	PEEK 0             # [0, 0, ffffff00]
	DEC                # [-1, 0, ffffff00]
	get_length         # [len, -1, 0, ffffff00]
	MOD                # [len-1, 0, ffffff00]
	get_pixel          # [a, 0, ffffff00]
	PEEK 1             # [0, a, 0, ffffff00]
	INC                # [1, a, 0, ffffff00]
	get_length         # [len, 1, a, 0, ffffff00]
	MOD                # [1, a, 0, ffffff00]
	get_pixel          # [c, a, 0, ffffff00]
	XOR                # [x, 0, ffffff00]
	JZ if_then

	POP 1              # [0, ffffff00]
	PEEK 1             # [ffffff00, 0, ffffff00]

if_then:
	set_pixel          # [0, ffffff00]
	INC                # [1, ffffff00]
	PEEK 0             # [1, 1, ffffff00]
	get_length         # [len, 1, 1, ffffff00]
	SUB                # [len-1, 1, ffffff00]
	JNZ continue

	POP 2              # [ffffff00]
	JMP loop

continue:
	POP 1              # [1, ffffff00]
	PUSHB 10           # [10, 1, ffffff00]
	sleep
	JMP inner_loop
