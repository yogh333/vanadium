#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

typedef uint32_t cx_err_t;

typedef enum cx_curve_e {
    CX_CURVE_SECP256K1 = 0x21,
} cx_curve_t;

#define CX_CURVE_256K1 CX_CURVE_SECP256K1

#define CX_OK 0x00000000
#define CX_CARRY 0xFFFFFF21
#define CX_LOCKED 0xFFFFFF81
#define CX_UNLOCKED 0xFFFFFF82
#define CX_NOT_LOCKED 0xFFFFFF83
#define CX_NOT_UNLOCKED 0xFFFFFF84
#define CX_INTERNAL_ERROR 0xFFFFFF85
#define CX_INVALID_PARAMETER_SIZE 0xFFFFFF86
#define CX_INVALID_PARAMETER_VALUE 0xFFFFFF87
#define CX_INVALID_PARAMETER 0xFFFFFF88
#define CX_NOT_INVERTIBLE 0xFFFFFF89
#define CX_OVERFLOW 0xFFFFFF8A
#define CX_MEMORY_FULL 0xFFFFFF8B
#define CX_NO_RESIDUE 0xFFFFFF8C
#define CX_EC_INFINITE_POINT 0xFFFFFF41
#define CX_EC_INVALID_POINT 0xFFFFFFA2
#define CX_EC_INVALID_CURVE 0xFFFFFFA3

typedef struct cx_ecfp_256_public_key_s {
  cx_curve_t curve;
  size_t W_len;
  uint8_t W[65];
} cx_ecfp_public_key_t;

typedef struct cx_ecfp_256_private_key_s {
  cx_curve_t curve;
  size_t d_len;
  uint8_t d[32];
} cx_ecfp_private_key_t;

void ecfp_init_private_key(cx_curve_t curve, const uint8_t *raw_key, size_t key_len, cx_ecfp_private_key_t *key);
cx_err_t derive_node_bip32(cx_curve_t curve, const unsigned int *path, size_t path_count, uint8_t *private_key, uint8_t *chain);
cx_err_t ecfp_generate_pair(cx_curve_t curve, cx_ecfp_public_key_t *pubkey, cx_ecfp_private_key_t *privkey);
void sha3_256(const uint8_t *buffer, size_t size, uint8_t *digest);
