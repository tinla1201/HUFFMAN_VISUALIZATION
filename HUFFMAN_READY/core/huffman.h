#ifndef HUFFMAN_H
#define HUFFMAN_H

#include <stdint.h>
#include <stdio.h>

#define MAX_FILE_SIZE 16777216ULL // 16 MiB
#define MAX_NODES 511

typedef struct {
    int id;
    int symbol; // -1 (null) cho nút nội bộ
    uint64_t freq;
    int left;
    int right;
} HuffNode;

typedef struct {
    int step;
    int left_id;
    int right_id;
    int parent_id;
    int queue_after[MAX_NODES];
    int q_size;
} MergeStep;

typedef struct {
    int symbol;
    char bits[256]; // Đảm bảo lưu được mã lên đến 255 bit
} HuffCode;

// API
int process_analyze(const char* filepath);
int process_tree(const char* filepath);

#endif
