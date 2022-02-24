#pragma once

/*
 * This file is shared between the RISC-V apps and the RISC-V VM.
 */

#define ECALL_XSEND            2
#define ECALL_XRECV            3
#define ECALL_SHA256SUM        4
#define ECALL_EXIT             5
#define ECALL_UX_RECTANGLE     6
#define ECALL_SCREEN_UPDATE    7
#define ECALL_BAGL_DRAW_BITMAP 8
#define ECALL_WAIT_BUTTON      9
#define ECALL_BAGL_DRAW        10

#define ECALL_DERIVE_NODE_BIP32     100
#define ECALL_CX_ECFP_GENERATE_PAIR 101
#define ECALL_CX_SHA3_256           102
