---
title: std::is_implicit_lifetime
summary: "型が「暗黙的に寿命を始められる」型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_implicit_lifetime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <type_traits>`
</div>

`malloc` や `memcpy` で用意したメモリをそのまま `T` のオブジェクトとして使い始められる型かを判定します。`int` や単純な構造体は満たし、コンストラクタやデストラクタが必要な型は満たしません。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_implicit_lifetime {#is_implicit_lifetime}

```cpp
template <class T>
struct is_implicit_lifetime;
template <class T>
inline constexpr bool is_implicit_lifetime_v = is_implicit_lifetime<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  std::println("{}", std::is_implicit_lifetime_v<int>);
  std::println("{}", std::is_implicit_lifetime_v<std::string>);
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
    `is_implicit_lifetime` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型が「暗黙的に寿命を始められる」型かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_implicit_lifetime](https://cpprefjp.github.io/reference/type_traits/is_implicit_lifetime.html)
- [cppreference: std::is_implicit_lifetime](https://en.cppreference.com/w/cpp/types/is_implicit_lifetime)
