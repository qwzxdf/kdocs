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

`new` は、**ヒープにメモリを確保して、そこにオブジェクトを作る**式です。確保（`operator new`）とコンストラクターの呼び出しを一度に行います。作ったものは、`delete` で解放する責任が生じます。現代の C++ では、直接 `new` を書かず、`std::make_unique` などを使います。

!!! tip "ポイント"
    - **生の `new` は書かない。** `std::make_unique<T>(...)` を使う。
    - `new` で作ったものは、必ず `delete` で解放する。
    - 失敗すると `std::bad_alloc` を投げる（`nothrow` を付けると `nullptr`）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

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
- 確保の中身（どこから取るか）は [`operator new`](#operator_new) が決めます

!!! warning "`new` の結果は、すぐ unique_ptr に入れる"
    `new` で得たポインタを、生のまま持ち回らないでください。例外が出たときにリークします。`std::make_unique<T>(...)` なら、確保と所有を同時に行えます。

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

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `T* p = new T(args);` → `auto p = std::make_unique<T>(args);` |

## よくあるミス

??? failure "delete し忘れる"
    メモリリークになります。`unique_ptr` に任せます。

??? failure "new[] を delete で解放する"
    `new[]` には `delete[]` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_unique`](../../utilities/make_unique.md) | `new` の代わり |
| [`delete`](delete.md) | 解放する |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープにオブジェクトを作る
    - [x] 生の new は書かない
    - [x] delete で解放する責任

## 関連ページ

- [cpprefjp: new 式](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: new 式](https://en.cppreference.com/w/cpp/memory/new/new)
