---
title: std::variant_size
summary: "variant が持てる型の数をコンパイル時に取り出す。"
order: 900
tags:
  - ユーティリティ
---

# std::variant_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`variant<int, double, std::string>` が、何種類の型を持てるかをテンプレートの中で知りたいことがあります。`variant_size_v<V>` が、その数（この例では 3）を返します。型のリストを `index_sequence` で順に処理するときの終点にも使えます。

!!! tip "ポイント"
    - `variant_size_v<V>` で数が取れる（`size_t`）。
    - `variant_alternative_t<I, V>` と組み合わせると、全部の選択肢を順に調べられる。
    - `std::tuple_size` の variant 版。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::variant_size {#variant_size}

```cpp
template <class T>
struct variant_size;
template <class T>
inline constexpr size_t variant_size_v = variant_size<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | variant 型 | 調べる variant |

- 戻り値: 型の数（`size_t`）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <variant>

int main() {
  using V = std::variant<int, double, char>;
  std::println("{}", std::variant_size_v<V>);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| variant の全ての選択肢に処理をする | `std::make_index_sequence<std::variant_size_v<V>>{}` |

## よくあるミス

??? failure "`index()` と混同する"
    `index()` は今入っている型の番号、`variant_size` は持てる型の数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`variant_alternative`](variant_alternative.md) | N 番目の型 |
| [`std::variant`](variant.md) | variant の本体 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持てる型の数を取り出す
    - [x] variant_size_v
    - [x] コンパイル時の値

## 関連ページ

- [cpprefjp: std::variant_size](https://cpprefjp.github.io/reference/variant/variant_size.html)
- [cppreference: std::variant_size](https://en.cppreference.com/w/cpp/utility/variant/variant_size)
