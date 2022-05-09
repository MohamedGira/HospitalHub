


# .data

# msg: .asciiz "Hello World\n"
# .text

# .globl  main
# main:
#     jal proc1
#     li $v0 ,10 
#     syscall



# proc1:
#     li $v0 ,4 
#     la $a0 ,msg
#     syscall

#     add $t0,$zero,$zero
#     addi $t1, $t0 ,10
#     addi $a0, $zero ,'*'
#         li $v0 ,11 

#     loop: 
#         syscall
#         addi $t0,$t0,1
#         bne $t0,$t1, loop

# jr $ra


.data
A:  .word -2, 5, 10, -4, 7
B: .space 20

.text

.globl main

main:
    jal proc2
    li $v0,10
    syscall


proc2:
    add $t0, $zero,$zero
    la $t1, A
    la $t2, B
    add $t4,$zero,$zero,
    loop:
        
        lw $t3, 0($t1)
        nor $t3,$t3,$t3
        addi $t3,$t3,1
        sw $t3,0($t2)
        add $t4,$t4,$t3
        addi $t1,$t1,4
        addi $t2,$t2,4
        addi $t0,$t0,4
        bne $t0, 20, loop

    li $v0, 1
    add $a0,$zero,$t4
    syscall
    jr $ra 
        