	.file	"1-21.c"
	.intel_syntax noprefix
# GNU C23 (GCC) version 15.2.0 (x86_64-unknown-linux-gnu)
#	compiled by GNU C version 15.2.0, GMP version 6.3.0, MPFR version 4.2.2, MPC version 1.3.1, isl version isl-0.27-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -masm=intel -mtune=generic -march=x86-64 -O2
	.text
	.section	.text.startup,"ax",@progbits
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB11:
	.cfi_startproc
	push	r12	#
	.cfi_def_cfa_offset 16
	.cfi_offset 12, -16
# 1-21.c:12:   int col = 0, spaces = 0, c;
	xor	r12d, r12d	# col
# 1-21.c:10: int main(void) {
	push	rbp	#
	.cfi_def_cfa_offset 24
	.cfi_offset 6, -24
	push	rbx	#
	.cfi_def_cfa_offset 32
	.cfi_offset 3, -32
# 1-21.c:12:   int col = 0, spaces = 0, c;
	xor	ebx, ebx	# spaces
	.p2align 4
	.p2align 3
.L2:
# /usr/include/x86_64-linux-gnu/bits/stdio.h:49:   return getc (stdin);
	mov	rdi, QWORD PTR stdin[rip]	#, stdin
	call	getc@PLT	#
	mov	ebp, eax	# _21,
# 1-21.c:14:   while ((c = getchar()) != EOF) {
	cmp	eax, -1	# _21,
	je	.L15	#,
# 1-21.c:15:     if (c == ' ') {
	cmp	ebp, 32	# _21,
	jne	.L16	#,
# 1-21.c:17:       col++;
	add	r12d, 1	# col,
# 1-21.c:16:       spaces++;
	add	ebx, 1	# spaces,
# 1-21.c:18:       if (col % TAB == 0) {
	test	r12b, 7	# col,
	jne	.L2	#,
# /usr/include/x86_64-linux-gnu/bits/stdio.h:84:   return putc (__c, stdout);
	mov	rsi, QWORD PTR stdout[rip]	#, stdout
	mov	edi, 9	#,
# 1-21.c:20:         spaces = 0;
	xor	ebx, ebx	# spaces
# /usr/include/x86_64-linux-gnu/bits/stdio.h:84:   return putc (__c, stdout);
	call	putc@PLT	#
	jmp	.L2	#
	.p2align 4,,10
	.p2align 3
.L16:
# 1-21.c:23:       while (spaces > 0) {
	test	ebx, ebx	# spaces
	je	.L5	#,
	.p2align 4
	.p2align 3
.L4:
# /usr/include/x86_64-linux-gnu/bits/stdio.h:84:   return putc (__c, stdout);
	mov	rsi, QWORD PTR stdout[rip]	#, stdout
	mov	edi, 32	#,
	call	putc@PLT	#
# 1-21.c:23:       while (spaces > 0) {
	sub	ebx, 1	# spaces,
	jne	.L4	#,
.L5:
# /usr/include/x86_64-linux-gnu/bits/stdio.h:84:   return putc (__c, stdout);
	mov	rsi, QWORD PTR stdout[rip]	#, stdout
	mov	edi, ebp	#, _21
	call	putc@PLT	#
# 1-21.c:28:       if (c == '\n')
	cmp	ebp, 10	# _21,
	je	.L10	#,
# 1-21.c:30:       else if (c == '\t')
	cmp	ebp, 9	# _21,
	je	.L17	#,
# 1-21.c:33:         col++;
	add	r12d, 1	# col,
	xor	ebx, ebx	# spaces
	jmp	.L2	#
	.p2align 4,,10
	.p2align 3
.L10:
	xor	ebx, ebx	# spaces
# 1-21.c:29:         col = 0;
	xor	r12d, r12d	# col
	jmp	.L2	#
	.p2align 4,,10
	.p2align 3
.L15:
# 1-21.c:37: }
	pop	rbx	#
	.cfi_remember_state
	.cfi_def_cfa_offset 24
	xor	eax, eax	#
	pop	rbp	#
	.cfi_def_cfa_offset 16
	pop	r12	#
	.cfi_def_cfa_offset 8
	ret	
	.p2align 4,,10
	.p2align 3
.L17:
	.cfi_restore_state
# 1-21.c:31:         col += (TAB - col % TAB);
	mov	eax, r12d	# tmp113, col
	xor	ebx, ebx	# spaces
	sar	eax, 31	# tmp113,
	shr	eax, 29	# tmp114,
	lea	edx, [r12+rax]	# tmp115,
	and	edx, 7	# tmp116,
# 1-21.c:31:         col += (TAB - col % TAB);
	sub	eax, edx	# tmp118, tmp116
# 1-21.c:31:         col += (TAB - col % TAB);
	lea	r12d, 8[r12+rax]	# col,
	jmp	.L2	#
	.cfi_endproc
.LFE11:
	.size	main, .-main
	.ident	"GCC: (GNU) 15.2.0"
	.section	.note.GNU-stack,"",@progbits
