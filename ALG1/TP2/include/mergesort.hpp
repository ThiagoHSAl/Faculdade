#ifndef MERGESORT_HPP
#define MERGESORT_HPP

#include <vector>

// --- 3. Etapa "Combine" (Mesclar) ---
// Esta função mescla duas sub-listas já ordenadas em uma única lista ordenada.
template <typename T, typename Comparator>
void merge(std::vector<T>& arr, int left, int mid, int right, Comparator comp) {
    // 1. Calcular os tamanhos das duas metades
    int leftSize = mid - left + 1;
    int rightSize = right - mid;

    // 2. Criar vetores temporários para as metades
    std::vector<T> L(leftSize);
    std::vector<T> R(rightSize);

    // 3. Copiar os dados para os vetores temporários
    for (int i = 0; i < leftSize; i++) {
        L[i] = arr[left + i];
    }
    for (int j = 0; j < rightSize; j++) {
        R[j] = arr[mid + 1 + j];
    }

    // 4. Mesclar (intercalar) os vetores temporários de volta no vetor original
    int i = 0; // Índice inicial da primeira metade (L)
    int j = 0; // Índice inicial da segunda metade (R)
    int k = left; // Índice inicial da lista mesclada (no 'arr' original)

    while (i < leftSize && j < rightSize) {
        // Usa a função de comparação para decidir quem é menor
        // Se comp(L[i], R[j]) for verdadeiro, L[i] vem antes
        if (comp(L[i], R[j])) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    // 5. Copiar quaisquer elementos restantes (se uma das listas acabar primeiro)
    while (i < leftSize) {
        arr[k] = L[i];
        i++;
        k++;
    }
    while (j < rightSize) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

// --- 1. Etapa "Divide" e 2. "Conquer" (Recursão) ---
// Esta é a função recursiva principal do MergeSort.
template <typename T, typename Comparator>
void mergeSortRecursive(std::vector<T>& arr, int left, int right, Comparator comp) {
    // Caso Base: se a lista tem 0 ou 1 elemento, ela já está ordenada
    if (left >= right) {
        return;
    }

    // 1. Dividir: Encontrar o ponto do meio
    int mid = left + (right - left) / 2;

    // 2. Conquistar: Ordenar recursivamente cada metade
    mergeSortRecursive(arr, left, mid, comp);
    mergeSortRecursive(arr, mid + 1, right, comp);

    // 3. Combinar: Mesclar as duas metades agora ordenadas
    merge(arr, left, mid, right, comp);
}

// --- Função "Wrapper" (Ponto de Entrada) ---
// Ela esconde a complexidade de ter que passar 'left' e 'right'
template <typename T, typename Comparator>
void mergeSort(std::vector<T>& arr, Comparator comp) {
    if (arr.size() > 1) {
        mergeSortRecursive(arr, 0, static_cast<int>(arr.size()) - 1, comp);
    }
}

// --- Funções de Comparação ---
bool comparaPorX(const Arvore& a, const Arvore& b) {
    // Critério de desempate: se X for igual, desempata por Y
    if (a.posicao.x != b.posicao.x) {
        return a.posicao.x < b.posicao.x;
    }
    return a.posicao.y < b.posicao.y;
}

bool comparaPorY(const Arvore& a, const Arvore& b) {
    // Critério de desempate: se Y for igual, desempata por X
    if (a.posicao.y != b.posicao.y) {
        return a.posicao.y < b.posicao.y;
    }
    return a.posicao.x < b.posicao.x;
}

#endif // MERGESORT_HPP