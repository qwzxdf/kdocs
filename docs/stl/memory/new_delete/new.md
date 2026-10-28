---
title: new 式
summary: "オブジェクトをヒープに作る式。メモリ確保とコンストラクターの呼び出しを一度に行う。"
order: 1
group: new / delete まわり
tags:
  - メモリ
---

# new 式

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

ゲームのオブジェクトを関数を抜けたあとも生かしたいとき、ヒープ（自由に使えるメモリ領域）に置く必要があります。`new` は、ヒープにメモリを確保して、そこにオブジェクトを作る式です。確保（`operator new`）とコンストラクターの呼び出しを一度に行います。作ったものは、`delete` で解放する責任が生じます。現代の C++ では、直接 `new` を書かず、`std::make_unique` などに任せます。

!!! tip "ポイント"
    - **生の `new` は書かない。** `std::make_unique<T>(...)` を使う。
    - `new` で作ったものは、必ず `delete` で解放する。
    - 失敗すると `std::bad_alloc` を投げる（`nothrow` を付けると `nullptr`）。

!!! info "このページを読む前に"
    [ヒープとスタックの違い](../../../basics/heap.md)を先に読んでください。`new` はヒープに置く式です。

## 関数の詳しい説明

### new 式 {#new data-toc-label="new 式"}

```cpp
T* p = new T(args...);       // () の初期化
T* p = new T{args...};       // {} の初期化
T* p = new T;                // 基本型は未初期化、クラスはデフォルトコンストラクタ
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | `Args&&...` | `T` のコンストラクタに渡す引数 |

- 戻り値: 作ったオブジェクトへのポインタ
- 例外: メモリが確保できないと `std::bad_alloc`。コンストラクタが例外を投げたら、確保したメモリは自動で返される
- `new int;` だと**中身が不定**です。`new int();` か `new int{}` とすると 0 で初期化されます
- 確保の中身（どこから取るか）は [`operator new`](operator_new.md) が決めます

!!! warning "`new` の結果は、すぐ unique_ptr に入れる"
    `new` で得たポインタを生のまま持ち回らないでください。例外が出たときにリークします。`std::make_unique<T>(...)` なら、確保と所有を同時に行えます。

## しくみ

`new T(args)` は、2 段階に分かれています。1 段階目は `operator new(sizeof(T))` を呼んでメモリを確保すること、2 段階目はそのメモリに `T` のコンストラクターを呼ぶことです。コンストラクターが例外を投げたときは、確保したメモリが自動で返されます。

確保に失敗すると `std::bad_alloc` を投げます。`new (std::nothrow) T` と書くと、例外を投げず `nullptr` を返します。ゲームでは例外を使わない設定にすることが多いので、`nothrow` を使う場面もあります。

配列は `new T[n]` と書き、解放は `delete[]` で行います。`delete` と `delete[]` を取り違えると、未定義動作になります。確保した場所を自分で決めたいときは、配置 `new`（`new (ptr) T`）を使います。

## 実際に動かしてみる

```cpp
#include <print>

int main() {
  int* p = new int(5);
  std::println("{}", *p);
  delete p;
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

通常のゲームのコードで、`new` を直接書く場面は、ほとんどありません。オブジェクトの持ち主は `std::make_unique`、配列は `std::vector` で表します。

直接使うのは、オブジェクトプールを自作するときです。あらかじめ確保した大きな領域の中に配置 `new` でオブジェクトを作ります。確保済みの領域を使い回すので、毎フレームのメモリ確保の遅さを避けられます。

古いコードを読むときには、`new` が頻繁に出てきます。誰が `delete` するのかを追いかけながら、`unique_ptr` に置き換えられるかを考えます。

## よくあるミス

??? failure "`new` で作ったのに `delete` を忘れる"
    関数を抜ける前に `return` や例外が起きると、`delete` に届かずリークします。`unique_ptr` に任せれば、どの経路でも解放されます。

??? failure "`new[]` を `delete` で解放する"
    `new int[10]` は `delete[]` で解放します。`delete` だと未定義動作です。配列の確保は `std::vector` を使えば、この間違いがなくなります。

??? failure "`new` の結果を確かめずに使う"
    通常の `new` は、失敗すると例外を投げるので、戻り値を `nullptr` と比べる必要はありません。比べるのは `nothrow` 版のときです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_unique`](../../utilities/make_unique.md) | `new` の代わり。持ち主を `unique_ptr` で表す |
| [`delete`](delete.md) | `new` で作ったものを解放する |
| [配置 new](placement_new.md) | 確保済みの場所にオブジェクトを作る |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 生の `new` は書かない。`make_unique` か `vector` を使う。
    - [x] `new` は「確保」と「コンストラクターの呼び出し」の 2 段階。
    - [x] 失敗は `bad_alloc`。`nothrow` なら `nullptr`。

## 関連ページ

- [cpprefjp: new 式](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: new 式](https://en.cppreference.com/w/cpp/memory/new/new)
