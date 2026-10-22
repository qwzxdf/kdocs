---
title: std::in_place_index
summary: "variant に、番号を指定してその場で作らせる目印。"
order: 900
tags:
  - ユーティリティ
---

# std::in_place_index

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`variant<int, int>` のように同じ型が複数あると、型では選べません。`std::in_place_index<N>` は、「N 番目の選択肢で、その場で作る」と番号で指定します。

!!! tip "ポイント"
    - 番号は 0 から。
    - 型が重複しているときの選び方として使う。
    - 型で選ぶなら [`in_place_type`](in_place_type.md)。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::in_place_index {#in_place_index}

```cpp
template <size_t I> struct in_place_index_t { explicit in_place_index_t() = default; };
template <size_t I> inline constexpr in_place_index_t<I> in_place_index{};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | テンプレート引数 | 選択肢の番号（0 から） |

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <print>
#include <utility>
#include <variant>

int main() {
  std::variant<int, int> v(std::in_place_index<1>, 5);
  std::println("{} {}", v.index(), std::get<1>(v));
}
```

```text title="実行結果"
1 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同じ型が並ぶ variant の 2 番目に入れる | `std::variant<int, int> v(std::in_place_index<1>, 5);` |

## よくあるミス

??? failure "番号が範囲外"
    選択肢の数以上の番号を指定すると、コンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`in_place_type`](in_place_type.md) | 型で指定 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 番号を指定してその場で作る目印
    - [x] 0 から数える
    - [x] 型が重複するときに使う

## 関連ページ

- [cpprefjp: std::in_place_index](https://cpprefjp.github.io/reference/utility/in_place_index_t.html)
- [cppreference: std::in_place_index](https://en.cppreference.com/w/cpp/utility/in_place)
