---
title: std::integral_constant
summary: "コンパイル時の定数を、型として表す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::integral_constant

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

値を型として持ち運びたい。たとえば、整数の `3` をテンプレートの引数に渡す型として表したい。`std::integral_constant` は、<strong>コンパイル時の定数を型として包む</strong>ための基本の部品です。`std::true_type` と `std::false_type` は、これを使って作られています。

!!! tip "ポイント"
    - `std::integral_constant<int, 3>::value` は 3
    - 型そのものが値を持つ。オブジェクトにすると `3` に変換できる
    - `true_type` と `false_type` の土台
    - 型の性質を調べる `is_xxx` は、これを継承している

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::integral_constant {#integral_constant}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, T v>
struct integral_constant {
  static constexpr T value = v;
  using value_type = T;
  using type = integral_constant;
  constexpr operator value_type() const noexcept { return value; }
  constexpr value_type operator()() const noexcept { return value; }
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 値の型 |
| `v` | `T` の定数 | 包みたい値 |

`integral_constant<T, v>` は、`value` という静的なメンバー定数で `v` を持ち、オブジェクトにすると `v` に暗黙に変換できます。`is_integral<T>` のような型の性質は、この型を継承していて、`::value` で結果が取れるのはそのためです。

値を型にすると、オーバーロードの選択（タグ ディスパッチ）に使えます。実行時の値ではオーバーロードを選べませんが、型なら選べます。`integral_constant<int, 1>` と `integral_constant<int, 2>` は、別々の型です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  using Three = std::integral_constant<int, 3>;
  std::println("value     = {}", Three::value);
  std::println("変換して  = {}", Three{} + 1);   // int に暗黙に変換される
  std::println("true_type = {}", std::is_same_v<std::true_type, std::integral_constant<bool, true>>);
}
```

```text title="実行結果"
value     = 3
変換して  = 4
true_type = true
```

## ゲームでの使いどころ

型で分岐するオーバーロード（タグ ディスパッチ）に使います。

```cpp
void Update(std::true_type);    // 高速な経路
void Update(std::false_type);   // 汎用の経路

Update(std::is_trivially_copyable<T>{});   // 型の性質で経路が選ばれる
```

## よくあるミス

??? failure "値を実行時の変数と混同する"
    `v` はコンパイル時の定数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`true_type`](true_type.md) | `integral_constant<bool, true>` |
| [`bool_constant`](bool_constant.md) | `bool` 版の短縮 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `integral_constant<T, v>` はコンパイル時の定数を型として包む
    - [x] `::value` で値、オブジェクトにすると値に変換できる
    - [x] タグ ディスパッチと、型の性質の土台

## 関連ページ

- [cpprefjp: std::integral_constant](https://cpprefjp.github.io/reference/type_traits/integral_constant.html)
- [cppreference: std::integral_constant](https://en.cppreference.com/w/cpp/types/integral_constant)
