#include "huffman.h"
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <ctype.h>

HuffNode nodes[MAX_NODES];
int node_count = 0;
HuffNode* heap[MAX_NODES];
int heap_size = 0;

MergeStep steps[MAX_NODES];
int step_count = 0;

HuffCode codes[256];
int code_count = 0;

uint64_t frequencies[256] = {0};
uint64_t original_size = 0;
uint64_t encoded_bits = 0;

int compare_nodes(const HuffNode* a, const HuffNode* b) {
    if (a->freq != b->freq) return a->freq < b->freq ? -1 : 1;
    return (a->id > b->id) - (a->id < b->id);
}

int qsort_cmp(const void* a, const void* b) {
    HuffNode* na = *(HuffNode**)a;
    HuffNode* nb = *(HuffNode**)b;
    return compare_nodes(na, nb);
}

void push_heap(HuffNode* node) {
    heap[heap_size++] = node;
    int i = heap_size - 1;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (compare_nodes(heap[i], heap[p]) < 0) {
            HuffNode* tmp = heap[i];
            heap[i] = heap[p];
            heap[p] = tmp;
            i = p;
        } else break;
    }
}

HuffNode* pop_heap() {
    if (heap_size == 0) return NULL;
    HuffNode* min_node = heap[0];
    heap[0] = heap[--heap_size];
    int i = 0;
    while (2 * i + 1 < heap_size) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int smallest = left;
        if (right < heap_size && compare_nodes(heap[right], heap[left]) < 0) {
            smallest = right;
        }
        if (compare_nodes(heap[smallest], heap[i]) < 0) {
            HuffNode* tmp = heap[i];
            heap[i] = heap[smallest];
            heap[smallest] = tmp;
            i = smallest;
        } else break;
    }
    return min_node;
}

void generate_codes(int node_id, char* current_code, int depth) {
    if (node_id == -1) return;
    HuffNode* n = NULL;
    for (int i = 0; i < node_count; ++i) {
        if (nodes[i].id == node_id) { n = &nodes[i]; break; }
    }
    if (!n) return;

    if (n->left == -1 && n->right == -1) {
        codes[code_count].symbol = n->symbol;
        if (depth == 0) {
            strcpy(codes[code_count].bits, "0");
            encoded_bits += n->freq * 1;
        } else {
            current_code[depth] = '\0';
            strcpy(codes[code_count].bits, current_code);
            encoded_bits += n->freq * depth;
        }
        code_count++;
        return;
    }
    current_code[depth] = '0';
    generate_codes(n->left, current_code, depth + 1);
    current_code[depth] = '1';
    generate_codes(n->right, current_code, depth + 1);
}

int cmp_code(const void* a, const void* b) {
    return ((HuffCode*)a)->symbol - ((HuffCode*)b)->symbol;
}
int cmp_node_id(const void* a, const void* b) {
    return ((HuffNode*)a)->id - ((HuffNode*)b)->id;
}

void build_tree_and_print() {
    for (int i = 0; i < 256; ++i) {
        if (frequencies[i] > 0) {
            nodes[node_count] = (HuffNode){i, i, frequencies[i], -1, -1};
            push_heap(&nodes[node_count]);
            node_count++;
            original_size += frequencies[i];
        }
    }

    int next_internal_id = 256;
    while (heap_size > 1) {
        HuffNode* left = pop_heap();
        HuffNode* right = pop_heap();

        HuffNode new_node = {next_internal_id++, -1, left->freq + right->freq, left->id, right->id};
        nodes[node_count] = new_node;
        push_heap(&nodes[node_count]);
        node_count++;

        MergeStep step = {++step_count, left->id, right->id, new_node.id, {0}, heap_size};
        HuffNode* temp_heap[MAX_NODES];
        memcpy(temp_heap, heap, heap_size * sizeof(HuffNode*));
        qsort(temp_heap, heap_size, sizeof(HuffNode*), qsort_cmp);
        for (int i = 0; i < heap_size; ++i) step.queue_after[i] = temp_heap[i]->id;
        steps[step_count - 1] = step;
    }

    int root_id = -1;
    if (heap_size == 1) {
        root_id = heap[0]->id;
        char buffer[256];
        generate_codes(root_id, buffer, 0);
    }

    qsort(nodes, node_count, sizeof(HuffNode), cmp_node_id);
    qsort(codes, code_count, sizeof(HuffCode), cmp_code);

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"original_size\": %" PRIu64 ",\n", original_size);
    printf("  \"encoded_bits\": %" PRIu64 ",\n", encoded_bits);
    
    printf("  \"frequencies\": [");
    for (int i = 0; i < 256; ++i) printf("%" PRIu64 "%s", frequencies[i], i == 255 ? "" : ",");
    printf("],\n");

    if (root_id == -1) printf("  \"root\": null,\n");
    else printf("  \"root\": %d,\n", root_id);

    printf("  \"nodes\": [\n");
    for(int i = 0; i < node_count; ++i) {
        printf("    {\"id\":%d,\"symbol\":", nodes[i].id);
        if(nodes[i].symbol == -1) printf("null"); else printf("%d", nodes[i].symbol);
        printf(",\"freq\":%" PRIu64 ",\"left\":", nodes[i].freq);
        if(nodes[i].left == -1) printf("null"); else printf("%d", nodes[i].left);
        printf(",\"right\":");
        if(nodes[i].right == -1) printf("null"); else printf("%d", nodes[i].right);
        printf("}%s\n", i == node_count - 1 ? "" : ",");
    }
    printf("  ],\n");

    printf("  \"codes\": [\n");
    for (int i = 0; i < code_count; ++i) {
        printf("    {\"symbol\":%d,\"bits\":\"%s\"}%s\n", codes[i].symbol, codes[i].bits, i == code_count - 1 ? "" : ",");
    }
    printf("  ],\n");

    printf("  \"steps\": [\n");
    for (int i = 0; i < step_count; ++i) {
        printf("    {\"step\":%d,\"left\":%d,\"right\":%d,\"parent\":%d,\"queue_after\":[",
            steps[i].step, steps[i].left_id, steps[i].right_id, steps[i].parent_id);
        for (int j = 0; j < steps[i].q_size; ++j) {
            printf("%d%s", steps[i].queue_after[j], j == steps[i].q_size - 1 ? "" : ",");
        }
        printf("]}%s\n", i == step_count - 1 ? "" : ",");
    }
    printf("  ]\n}\n");
}

int process_analyze(const char* filepath) {
    FILE* f = fopen(filepath, "rb");
    if (!f) { fprintf(stderr, "Cannot open input file: %s\n", filepath); return 1; }
    
    unsigned char buf[4096];
    size_t bytes;
    uint64_t total = 0;
    while ((bytes = fread(buf, 1, sizeof(buf), f)) > 0) {
        total += bytes;
        if (total > MAX_FILE_SIZE) {
            fprintf(stderr, "File exceeds 16MiB limit\n");
            fclose(f); return 1;
        }
        for (size_t i = 0; i < bytes; ++i) frequencies[buf[i]]++;
    }
    int failed = ferror(f);
    if (fclose(f) != 0) failed = 1;
    if (failed) { fprintf(stderr, "Input read error\n"); return 1; }
    build_tree_and_print();
    return ferror(stdout) ? 1 : 0;
}

int process_tree(const char* filepath) {
    FILE* f = fopen(filepath, "rb");
    if (!f) { fprintf(stderr, "Cannot open freq file: %s\n", filepath); return 1; }
    uint64_t total = 0;
    int c = fgetc(f);
    for (int i = 0; i < 256; ++i) {
        while (c != EOF && isspace((unsigned char)c)) c = fgetc(f);
        if (c < '0' || c > '9') goto invalid;
        uint64_t value = 0;
        do {
            unsigned digit = (unsigned)(c - '0');
            if (value > (UINT64_MAX - digit) / 10) goto invalid;
            value = value * 10 + digit;
            c = fgetc(f);
        } while (c >= '0' && c <= '9');
        if (c != EOF && !isspace((unsigned char)c)) goto invalid;
        if (value > MAX_FILE_SIZE - total) goto invalid;
        frequencies[i] = value;
        total += value;
    }
    while (c != EOF && isspace((unsigned char)c)) c = fgetc(f);
    if (c != EOF || ferror(f)) goto invalid;
    if (fclose(f) != 0) { fprintf(stderr, "Input read error\n"); return 1; }
    build_tree_and_print();
    return ferror(stdout) ? 1 : 0;
invalid:
    fclose(f);
    fprintf(stderr, "Invalid frequency table: expected exactly 256 unsigned decimals, total <= 16 MiB\n");
    return 1;
}
