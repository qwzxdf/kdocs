---
title: std::is_null_pointer
summary: "型が `std::nullptr_t` かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_null_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <type_traits>`
</div>

`nullptr` の型は `std::nullptr_t` という専用の型です。テンプレートに `nullptr` が渡されたかを、型から判定できます。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_null_pointer {#is_null_pointer}

```cpp
template <class T>
struct is_null_pointer;
template <class T>
inline constexpr bool is_null_pointer_v = is_null_pointer<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_null_pointer_v<decltype(nullptr)>);
  std::println("{}", std::is_null_pointer_v<int*>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "値と型を取り違える"
    `is_null_pointer` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型が `std::nullptr_t` かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_null_pointer](https://cpprefjp.github.io/reference/type_traits/is_null_pointer.html)
- [cppreference: std::is_null_pointer](https://en.cppreference.com/w/cpp/types/is_null_pointer)
