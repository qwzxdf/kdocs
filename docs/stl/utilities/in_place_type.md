---
title: std::in_place_type
summary: "variant / any / optional に、型を指定してその場で作らせる目印。"
order: 900
tags:
  - ユーティリティ
---

# std::in_place_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`std::variant<int, std::string>` に文字列を入れたいとき、コンストラクタ引数だけでは「どの型で作るか」が曖昧です。`std::in_place_type<T>` を先頭に置くと、「T の型で、その場で作る」ことを指定できます。コピーやムーブが入らないので効率的です。

!!! tip "ポイント"
    - `variant`、`any` のコンストラクタや `emplace` で使う。
    - 型で指定するのが `in_place_type`、番号で指定するのが [`in_place_index`](in_place_index.md)。
    - `optional` / `expected` は型が 1 つなので [`in_place`](in_place.md) を使う。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::in_place_type {#in_place_type}

```cpp
template <class T> struct in_place_type_t { explicit in_place_type_t() = default; };
template <class T> inline constexpr in_place_type_t<T> in_place_type{};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | その場で作る型 |

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <utility>
#include <variant>

int main() {
  std::variant<int, std::string> v(std::in_place_type<std::string>, 3, 'x');
  std::println("{}", std::get<std::string>(v));
}
```

```text title="実行結果"
xxx
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| variant にその場で文字列を作る | `std::variant<int, std::string> v(std::in_place_type<std::string>, 3, 'x');` |

## よくあるミス

??? failure "型が重複する variant で使う"
    同じ型が複数あると型では選べません。`in_place_index` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`in_place`](in_place.md) | 型がひとつの場合 |
| [`in_place_index`](in_place_index.md) | 番号で指定 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型を指定してその場で作る目印
    - [x] variant / any で使う
    - [x] 重複があれば in_place_index

## 関連ページ

- [cpprefjp: std::in_place_type](https://cpprefjp.github.io/reference/utility/in_place_type_t.html)
- [cppreference: std::in_place_type](https://en.cppreference.com/w/cpp/utility/in_place)
