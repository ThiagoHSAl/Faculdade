#ifndef ITEM_HPP
#define ITEM_HPP

#include <string>

#define KEYSZ 3
#define VETSZ 20
#define PLSZ 3

typedef struct item {
    long long int key;
    char payload[PLSZ];
} item_t;

inline bool operator<(const item_t& a, const item_t& b) {
    return a.key < b.key;
}

inline bool operator>(const item_t& a, const item_t& b) {
    return a.key > b.key;
}

inline bool operator==(const item_t& a, const item_t& b) {
    return a.key == b.key;
}

inline bool operator<=(const item_t& a, const item_t& b) {
    return a.key <= b.key;
}

inline bool operator>=(const item_t& a, const item_t& b) {
    return a.key >= b.key;
}

inline bool operator!=(const item_t& a, const item_t& b) {
    return a.key != b.key;
}

#endif
