#include "huffman.h"
#include <string.h>

int main(int argc, char** argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <analyze|tree> <filepath>\n", argv[0]);
        return 2;
    }
    if (strcmp(argv[1], "analyze") == 0) {
        return process_analyze(argv[2]);
    } else if (strcmp(argv[1], "tree") == 0) {
        return process_tree(argv[2]);
    } else {
        fprintf(stderr, "Invalid command. Use 'analyze' or 'tree'.\n");
        return 2;
    }
}
