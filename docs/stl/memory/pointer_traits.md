---
title: std::pointer_traits
summary: "ポインタ（生ポインタやスマートポインタ）の性質を、同じ書き方で調べる。"
order: 900
tags:
  - メモリ
---

# std::pointer_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

アロケータやコンテナを書くとき、「ポインタの指す型」や「ポインタを作る方法」を生ポインタでも自作のスマートポインタでも同じ書き方で扱いたくなります。`pointer_traits<P>` は、そのための統一された入り口です。

!!! tip "ポイント"
    - `element_type` が指す先の型、`pointer_to(r)` が参照からポインタを作る。
    - 生ポインタ `T*` にも特殊化がある。
    - 自作のアロケータ `pointer` 型を扱うときに使う。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::pointer_traits {#pointer_traits}

```cpp
template <class Ptr> struct pointer_traits {
  using pointer = Ptr;
  using element_type = /* Ptr が指す型 */;
  using difference_type = /* 差の型 */;
  static pointer pointer_to(element_type& r);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Ptr` | 型 | 調べるポインタ型 |

- 戻り値: `element_type` などの型メンバと `pointer_to`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

int main() {
  int x = 5;
  int* p = std::pointer_traits<int*>::pointer_to(x);
  std::println("{}", *p);
  std::println("{}", std::is_same_v<std::pointer_traits<int*>::element_type, int>);
}
```

```text title="実行結果"
5
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ポインタ型に依存しない書き方 | `std::pointer_traits<Ptr>::element_type` |

## よくあるミス

??? failure "生ポインタ以外に `&x` を使う"
    自作のポインタ型では `&x` ではなく `pointer_to(x)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_address`](to_address.md) | ポインタから生ポインタを取り出す |
| [`allocator_traits`](allocator_traits.md) | アロケータの性質 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポインタの性質をそろえて扱う入り口
    - [x] `element_type` と `pointer_to`
    - [x] アロケータ作りで登場

## 関連ページ

- [cpprefjp: std::pointer_traits](https://cpprefjp.github.io/reference/memory/pointer_traits.html)
- [cppreference: std::pointer_traits](https://en.cppreference.com/w/cpp/memory/pointer_traits)
