---
title: std::in_place
summary: "optional / variant / any の中に、オブジェクトをその場で構築するための印。"
order: 70
tags:
  - ユーティリティ
---

# std::in_place

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`std::in_place` は、**`optional`、`variant`、`any` などの中にオブジェクトを「コピーせず、その場で」構築するための印**です。`std::optional<std::string> o(std::in_place, 3, 'a');` のように、最初の引数に渡すと、残りの引数がコンストラクターに渡されます。`in_place_type<T>` / `in_place_index<N>` は、`variant` で型や番号を指定するときに使います。

!!! tip "ポイント"
    - コンストラクターの引数をそのまま渡せる（一時オブジェクトを作らない）。
    - `std::variant<int, float> v(std::in_place_type<float>, 1.5f);` のように、型を指定できる。
    - `optional::emplace` と同じ目的。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::in_place {#in_place}

```cpp
inline constexpr std::in_place_t in_place{};
```

- 戻り値: （タグ）
- 計算量: O(1)

```cpp
#include <optional>
#include <print>
#include <string>

int main() {
  // string(3, 'a') を optional の中でその場で構築する
  std::optional<std::string> name(std::in_place, 3, 'a');
  std::println("{}", *name);
}
```

```text title="実行結果"
aaa
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コピーしにくい（重い）オブジェクトを optional に入れる | `std::optional<Big> o(std::in_place, args...);` |

## よくあるミス

??? failure "引数の順番を間違える"
    `in_place` が**先頭**です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::optional`](optional.md) | in_place で構築できる |
| [`std::variant`](variant.md) | `in_place_type` で型を指定 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] その場で構築するための印
    - [x] 一時オブジェクトを作らない
    - [x] `in_place_type` / `in_place_index`

## 関連ページ

- [cpprefjp: std::in_place](https://cpprefjp.github.io/reference/utility/in_place.html)
- [cppreference: std::in_place](https://en.cppreference.com/w/cpp/utility/in_place)
