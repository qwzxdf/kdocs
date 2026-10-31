---
title: operator delete
summary: "new 式の「解放の部分」だけを行う関数（デストラクタは呼ばない）。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# operator delete

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <new>`
</div>

`delete p` は、デストラクターを呼んだあとに、`operator delete(p)` を呼んでメモリを返します。この関数を置き換えると、プログラム全体の解放を、独自の方法に変えられます。メモリの使用量の計測や、リークの検出に使います。

!!! tip "ポイント"
    - `operator new` と必ず対で置き換える
    - `delete` 式は、デストラクターを呼んでから、これを呼ぶ
    - `nullptr` が渡されても、安全に何もしないよう作る
    - サイズつき（`operator delete(void*, size_t)`）の版もある

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) を先に読んでください。

## 関数の詳しい説明

### operator delete {#operator_delete}

```cpp
void operator delete(void* ptr) noexcept;
void operator delete(void* ptr, std::size_t size) noexcept;      // C++14
void operator delete(void* ptr, std::align_val_t align) noexcept;  // C++17
```

確保と解放の対応を、取り違えないようにします。`operator new` を置き換えたのに `delete` を置き換えない、またはその逆は、`malloc` で確保したものを別の方法で解放することになり、壊れます。

サイズつきの版は、解放するオブジェクトの大きさを、コンパイラが教えてくれます。メモリ プールのように、大きさごとにリストを持つアロケーターで、サイズを記録する手間が省けます。

配列版（`operator delete[]`）も、同様に置き換えます。デフォルトの実装は、配列版が普通の版を呼ぶので、普通の版だけを置き換えても、ほとんど動きます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <new>
#include <print>

int g_news = 0;
int g_deletes = 0;

// グローバルの new / delete を置き換えて、回数を数える
void* operator new(std::size_t size) {
  ++g_news;
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}

void operator delete(void* p) noexcept {
  if (p != nullptr) ++g_deletes;
  std::free(p);
}

void operator delete(void* p, std::size_t) noexcept { operator delete(p); }

int main() {
  const int n0 = g_news;
  const int d0 = g_deletes;

  int* p = new int(5);
  delete p;

  const int dn = g_news - n0;
  const int dd = g_deletes - d0;
  std::println("new: {} delete: {}", dn, dd);
}
```

```text title="実行結果"
new: 1 delete: 1
```

## ゲームでの使いどころ

デバッグ ビルドで、確保と解放の回数や、確保した場所を記録して、リークを見つけます。

## よくあるミス

??? failure "new だけを置き換える"
    解放が標準のものになり、`malloc` と `delete` の取り合わせで壊れます。

??? failure "置き換えた関数の中で new を使う"
    無限に再帰します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`operator new`](operator_new.md) | 確保側 |
| [`delete`](delete.md) | `delete` 式 |
| [`set_new_handler`](set_new_handler.md) | 失敗時の回復 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: operator delete](https://cpprefjp.github.io/reference/new/operator_delete.html)
- [cppreference: operator delete](https://en.cppreference.com/w/cpp/memory/new/operator_delete)
