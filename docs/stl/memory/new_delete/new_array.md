---
title: new[]
summary: "配列をヒープに作り、解放する式。"
order: 3
group: new / delete まわり
tags:
  - メモリ
---

# new[]

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

同じ型のオブジェクトを、まとめて確保したい。`new T[n]` は、`n` 個分の領域を確保して、各要素のコンストラクターを呼びます。解放には、必ず `delete[]` を使います。生の `new[]` は、`std::vector` や `std::unique_ptr<T[]>` に置き換えるのが普通です。

!!! tip "ポイント"
    - `new T[n]` は、`n` 個を確保して、全部にコンストラクターを呼ぶ
    - 解放は `delete[]`。`delete` だと未定義動作
    - `new T[n]()` は値初期化（0 で初期化）、`new T[n]` は既定の初期化
    - 新しいコードは `std::vector` か `std::make_unique<T[]>(n)`

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) と [`delete[]`](delete_array.md) を先に読んでください。

## 関数の詳しい説明

### new[] 式 {#new_array}

```cpp
T* p = new T[n];
T* q = new T[n]{};            // 値初期化
T* r = new T[3]{1, 2, 3};     // 初期化子つき
```

`new[]` 式は、内部で `operator new[](size)` を呼んでメモリを確保し、各要素にコンストラクターを順に呼びます。途中のコンストラクターが例外を投げると、作り終えた要素のデストラクターを逆順に呼び、メモリを解放してから、例外を伝えます。

`int` のような基本型を `new int[n]` で作ると、値は初期化されません。0 で初期化したいなら、`new int[n]()` か `new int[n]{}` と書きます。

要素の個数は、実装がどこかに覚えていて、`delete[]` がそれを使ってデストラクターを呼びます。そのため、`delete[]` と `delete` の取り違えは、未定義動作になります。

## 実際に動かしてみる

```cpp
#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  Tracer(const Tracer&) { ++alive; }
  Tracer(Tracer&&) noexcept { ++alive; }
  ~Tracer() { --alive; }
};

struct Item {
  Item() { ++Tracer::alive; }
  ~Item() { --Tracer::alive; }
};

int main() {
  Item* items = new Item[3];
  std::println("生きている数: {}", Tracer::alive);
  delete[] items;
  std::println("解放後: {}", Tracer::alive);

  // 基本型は初期化されない。() で 0 にする
  int* zeros = new int[3]();
  std::println("{} {} {}", zeros[0], zeros[1], zeros[2]);
  delete[] zeros;
}
```

```text title="実行結果"
生きている数: 3
解放後: 0
0 0 0
```

## ゲームでの使いどころ

古いコードの読解用です。新しく書くなら、`std::vector<T>` か `std::make_unique<T[]>(n)` を使います。

## よくあるミス

??? failure "delete で解放する"
    未定義動作です。`new[]` には `delete[]`。

??? failure "基本型が 0 で初期化されると思う"
    `()` や `{}` を付けないと、ゴミの値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`delete[]`](delete_array.md) | 対になる解放 |
| `std::vector` | 普段はこちら |
| `std::unique_ptr<T[]>` | 所有権を持つ配列 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: new[] と delete[]](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: new[] と delete[]](https://en.cppreference.com/w/cpp/memory/new/new)
