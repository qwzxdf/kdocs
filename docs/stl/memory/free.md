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

`malloc`、`calloc`、`realloc` で確保した領域は、`std::free(p)` で返します。`nullptr` を渡しても安全です。`new` で確保したものに `free` を、`malloc` で確保したものに `delete` を使うと、壊れます。

!!! tip "ポイント"
    - `malloc` / `calloc` / `realloc` で確保した領域だけに使う
    - `nullptr` に使っても何もしない
    - 二重に `free` すると未定義動作。解放後は `nullptr` にしておく
    - C++ のオブジェクトには、デストラクターを呼ばないので使わない

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::free {#free}

```cpp
void free(void* ptr);
```

解放した領域を読み書きするのは、未定義動作です（ぶら下がったポインター）。解放したら、そのポインターは使わない、`nullptr` を代入する、という習慣が有効です。

`free` はデストラクターを呼びません。`malloc` で確保した領域に配置 new でオブジェクトを作った場合は、`free` の前に、デストラクターを呼びます。

C++ では、`std::unique_ptr<T, 解放関数>` のデリーターに `free` を指定すれば、C の関数が確保した領域を、自動で解放できます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <memory>
#include <print>

struct FreeDeleter {
  void operator()(void* p) const { std::free(p); }
};

int main() {
  // nullptr に free しても安全
  std::free(nullptr);

  // unique_ptr に任せる
  std::unique_ptr<int, FreeDeleter> p(static_cast<int*>(std::malloc(sizeof(int))));
  *p = 42;
  std::println("{}", *p);
  // 破棄のときに free が呼ばれる
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

C のライブラリが `malloc` で確保して返した領域を、`unique_ptr` と `free` のデリーターで包み、確実に解放します。

## よくあるミス

??? failure "new したものに free"
    壊れます。対応する解放関数を使います。

??? failure "二重に free"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](malloc.md) | 確保 |
| [`calloc`](calloc.md) | ゼロクリアして確保 |
| [`default_delete`](default_delete.md) | `delete` を呼ぶデリーター |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: free](https://cpprefjp.github.io/reference/cstdlib/free.html)
- [cppreference: free](https://en.cppreference.com/w/cpp/memory/c/free)
