---
title: std::tie
summary: "変数の参照をまとめた tuple を作る。複数の条件での比較に使う。"
order: 51
tags:
  - ユーティリティ
---

# std::tie

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

構造体の比較関数で、「レベルが同じなら名前で比べる」という複数の条件を書くとき、`if` を入れ子にして書くと、長くなります。`std::tie` は、複数の変数の「参照」をまとめた `tuple` を作る関数です。`tuple` の比較は、先頭の要素から順に行うので、`std::tie(a.level, a.name) < std::tie(b.level, b.name)` の 1 行で、辞書順の比較になります。

もう 1 つの使い方が、複数の戻り値を、既存の変数にまとめて受けることです。

!!! tip "ポイント"
    - 比較関数: `std::tie(a.level, a.name) < std::tie(b.level, b.name)` で、辞書順の比較になる
    - 受け取り: `std::tie(x, y) = f();` で、戻り値を既存の変数に代入する
    - 使わない要素は [`std::ignore`](ignore.md)
    - 新しい変数に受けるなら、構造化束縛 `auto [x, y] = f();` が簡潔

!!! info "このページを読む前に"
    [`std::make_tuple`](make_tuple.md) を先に読んでください。

## 関数の詳しい説明

### std::tie {#tie}

<span class="ver ver-11">C++11</span>

```cpp
template <class... Types>
constexpr std::tuple<Types&...> tie(Types&... args) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 左辺値（可変個） | 参照にまとめる変数 |

戻り値は、引数の参照を持つ `tuple` です。値のコピーはしません。右辺値は渡せません（一時オブジェクトを参照にできないため）。

### 比較に使う {#compare}

`tuple` の `<`、`==` は、先頭の要素から順に比べるので、メンバーを並べて `tie` するだけで、辞書順の比較が書けます。

```cpp
bool operator<(const Player& a, const Player& b) {
  return std::tie(a.level, a.name) < std::tie(b.level, b.name);
}
```

C++20 以降は、`operator<=>` を `= default` にすれば、同じことが自動で得られます。`tie` は、メンバーの順番や一部だけを使いたいときに役立ちます。

### 受け取りに使う {#assign}

関数が `tuple` や `pair` を返すとき、既存の変数に代入できます。

```cpp
int level;
std::string name;
std::tie(level, name) = GetPlayer();
```

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <tuple>

struct Player {
  int level;
  std::string name;
};

bool Less(const Player& a, const Player& b) {
  return std::tie(a.level, a.name) < std::tie(b.level, b.name);
}

std::tuple<int, std::string> GetPlayer() { return {7, "Hero"}; }

int main() {
  const Player a{5, "Zed"};
  const Player b{5, "Amy"};
  const Player c{9, "Amy"};
  std::println("a < b: {}", Less(a, b));  // レベルが同じで、名前は Zed > Amy
  std::println("b < a: {}", Less(b, a));
  std::println("a < c: {}", Less(a, c));  // レベルが低い

  int level = 0;
  std::string name;
  std::tie(level, name) = GetPlayer();
  std::println("{} {}", level, name);
}
```

```text title="実行結果"
a < b: false
b < a: true
a < c: true
7 Hero
```

## ゲームでの使いどころ

`std::sort` の比較関数や、`std::map` のキーの `operator<` を、メンバーを並べた 1 行で書けます。

## よくあるミス

??? failure "右辺値を tie に渡す"
    `std::tie(a, 5)` はコンパイルできません。一時的な値を参照にできないからです。

??? failure "tie の結果を、あとで使う"
    変数の参照を持っているので、元の変数が消えると、ぶら下がります。その場で使い切ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_tuple`](make_tuple.md) | 値をコピーした `tuple` を作る |
| [`std::ignore`](ignore.md) | 受け取らない要素の印 |
| `operator<=>` | C++20 の比較。自動生成できる |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::tie](https://cpprefjp.github.io/reference/tuple/tie.html)
- [cppreference: std::tie](https://en.cppreference.com/w/cpp/utility/tuple/tie)
