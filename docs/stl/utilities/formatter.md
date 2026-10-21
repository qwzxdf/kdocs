---
title: std::formatter
summary: "自作の型を、{} で出せるようにする。"
order: 50
tags:
  - ユーティリティ
---

# std::formatter

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::formatter<T>` は、**型 `T` を `{}` で出すときの書き方を決める**クラスです。自作の型（`Vec3` など）にこれを書いておくと、`std::println("{}", v)` で出せるようになります。

!!! tip "ポイント"
    - `std::formatter<自作の型>` を**特殊化**して、`parse`（書式指定の読み取り）と `format`（書き出し）を書く。
    - 凝った書式が要らないなら、`parse` は `ctx.begin()` を返すだけでよい。
    - 既存の型（`std::string` など）に委譲すると、書式指定も使える。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) などは不要です。書式の指定は [std::format](format.md) のページにまとめてあります。

## 関数の詳しい説明

### std::formatter（自作の型を出す） {#formatter}

```cpp
template <class T, class CharT = char>
struct formatter;
```

- `std::formatter<自作の型>` を特殊化すると、自作の型も `{}` で出せるようになります
- 一番簡単なのは、既にある formatter（`std::string_view` など）を継承して `format` だけ書く方法です

```cpp
#include <format>
#include <print>

struct Vec2 {
  float x;
  float y;
};

template <>
struct std::formatter<Vec2> : std::formatter<std::string_view> {
  auto format(const Vec2& v, std::format_context& ctx) const {
    return std::format_to(ctx.out(), "({:.1f}, {:.1f})", v.x, v.y);
  }
};

int main() {
  Vec2 pos = {1.25f, -3.0f};
  std::println("位置 {}", pos);
}
```

```text title="実行結果"
位置 (1.2, -3.0)
```

!!! note "実際は"
    `Vec2`、`Color`、`Rect` などの自作型に formatter を書いておくと、デバッグ表示がとても楽になります。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `Vec3` をデバッグ出力する | `std::println("pos = {}", pos);` |
| 列挙型を名前で出す | `std::formatter<Color>` で名前の文字列を返す |

## よくあるミス

??? failure "parse を書き忘れる"
    `parse` が無いと、コンパイルエラーになります。書式を無視するだけなら、`return ctx.begin();` と書きます。

??? failure "const を付け忘れる"
    `format` は `const` メンバ関数でなければなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](format.md) | 書式を使って文字列を作る |
| `operator<<` | ストリーム用の出力。`format` には効かない |

## コンパイラ対応

C++20 の機能です。GCC 13 / Clang 17 / MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自作の型に `std::formatter` を特殊化する
    - [x] `parse` と `format` の 2 つを書く
    - [x] 既存の型に委譲すると楽

## 関連ページ

- [cpprefjp: std::formatter](https://cpprefjp.github.io/reference/format/formatter.html)
- [cppreference: std::formatter](https://en.cppreference.com/w/cpp/utility/format/formatter)
