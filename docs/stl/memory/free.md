---
title: free
summary: "malloc で確保したメモリを解放する。"
order: 21
group: C の確保関数（<cstdlib>）
tags:
  - メモリ
---

# free

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstdlib>`
</div>

`free` は、**`malloc`・`calloc`・`realloc` で確保したメモリを解放する**関数です。`nullptr` を渡しても安全です。解放後のポインターは使ってはいけません。

!!! tip "ポイント"
    - `new` で確保したものに `free` を使わない。
    - 解放したら、ポインターを `nullptr` にしておくと安全。
    - C++ では、`unique_ptr` に任せるのが普通。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### free {#free}

```cpp
void free(void* ptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `void*` | `malloc` / `calloc` / `realloc` / `aligned_alloc` が返したポインタ。`nullptr` なら何もしない |

- 戻り値: なし
- **必ず `malloc` 系で確保したポインタ**を渡します。`new` したものや、配列の途中のポインタ、スタックのアドレスを渡すのは未定義動作です
- **2 回 `free` するのは未定義動作**（二重解放）。`free` したあとは `ptr = nullptr;` にしておくと安全です（`free(nullptr)` は何もしないので）
- デストラクタは呼ばれません。`std::string` などのクラスを `malloc` で作っていたなら、先に自分でデストラクタを呼ぶ必要があります（普通はそんなことをしません）

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  int* p = static_cast<int*>(std::malloc(sizeof(int)));
  std::free(p);
  p = nullptr;  // 解放後は nullptr にしておく
  std::println("{}", p == nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のAPI が返したメモリの解放 | `free(p);` |

## よくあるミス

??? failure "二重に解放する"
    同じポインターを 2 回 `free` すると未定義動作です。

??? failure "解放後に使う"
    ぶら下がりポインター（dangling）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](malloc.md) | 確保する |
| `delete` | `new` で確保したもの |

## コンパイラ対応

C 由来の関数です。`aligned_alloc` は C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] malloc したものを解放する
    - [x] 二重解放しない
    - [x] new には delete

## 関連ページ

- [cpprefjp: free](https://cpprefjp.github.io/reference/cstdlib/free.html)
- [cppreference: free](https://en.cppreference.com/w/cpp/memory/c/free)
