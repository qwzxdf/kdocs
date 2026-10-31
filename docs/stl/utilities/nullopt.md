---
title: std::nullopt
summary: "optional を「空」にするための印。"
order: 71
tags:
  - ユーティリティ
---

# std::nullopt

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

`std::optional<T>` は、「値があるかもしれないし、ないかもしれない」を表す型です。値がない状態を作るとき、`optional<int> o = 0;` のように 0 や -1 を使うと、本当の 0 と区別できません。`std::nullopt` は、「値なし」を表す専用の定数で、`optional` を空にするとき、空と比べるときに使います。

!!! tip "ポイント"
    - `std::optional<int> o = std::nullopt;` で、値なしの `optional` ができる
    - `o = std::nullopt;` で、中身を捨てて空にする
    - 関数から「見つからなかった」を返すとき、`return std::nullopt;` と書く
    - 比較では、`nullopt` はどの値よりも小さい

!!! info "このページを読む前に"
    [`std::optional`](optional.md) を先に読んでください。

## 関数の詳しい説明

### std::nullopt {#nullopt}

<span class="ver ver-17">C++17</span>

```cpp
struct nullopt_t { explicit constexpr nullopt_t(/* 未規定 */); };
inline constexpr nullopt_t nullopt{/* 未規定 */};
```

`nullopt_t` は、`optional` のコンストラクターや代入で、空にすることを選ぶための印の型です。`nullopt` は、その値です。空の `optional` を作る方法は他に `std::optional<int> o;`（既定の構築）もありますが、`return std::nullopt;` と書くと、意図が読み取りやすくなります。

`nullopt` との比較は、`o == std::nullopt`（空か）、`o != std::nullopt`（値があるか）が書けます。`o` を `bool` に変換する（`if (o)`）と同じ意味です。

大小の比較では、`nullopt` は、どの値よりも小さいものとして扱われます。`std::optional<int>{} < std::optional<int>{0}` は真です。

`nullopt_t` は、既定のコンストラクターを持たないので、`std::nullopt_t x;` とは書けません。`nullopt` を使います。

## 実際に動かしてみる

```cpp
#include <optional>
#include <print>
#include <string>

// 見つかれば名前、見つからなければ nullopt
std::optional<std::string> FindName(int id) {
  if (id == 1) return "Hero";
  return std::nullopt;
}

int main() {
  const auto a = FindName(1);
  const auto b = FindName(2);
  std::println("a: {}", a.has_value());
  std::println("b: {}", b.has_value());
  std::println("b == nullopt: {}", b == std::nullopt);

  std::optional<int> o = 5;
  o = std::nullopt;  // 空にする
  std::println("空にした: {}", !o.has_value());

  // nullopt は、どの値よりも小さい
  std::println("空 < 0: {}", std::optional<int>{} < std::optional<int>{0});
}
```

```text title="実行結果"
a: true
b: false
b == nullopt: true
空にした: true
空 < 0: true
```

## ゲームでの使いどころ

「アイテムが見つからない」「該当するキャラクターがいない」を、戻り値で表します。ポインタの `nullptr` と違い、値そのものを返せます。

## よくあるミス

??? failure "nullopt_t を変数に作ろうとする"
    作れません。`nullopt` をそのまま使います。

??? failure "0 を空の意味に使う"
    本当の 0 と区別できなくなります。`nullopt` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::optional`](optional.md) | 値があるかもしれない型 |
| [`std::make_optional`](make_optional.md) | 値のある `optional` を作る |
| `nullptr` | ポインタの空 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::nullopt](https://cpprefjp.github.io/reference/optional/nullopt.html)
- [cppreference: std::nullopt](https://en.cppreference.com/w/cpp/utility/optional/nullopt)
