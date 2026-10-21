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

`std::tie` は、**複数の変数の「参照」をまとめた tuple を作る**関数です。メンバを順に比べる比較関数を 1 行で書くのに使います。`std::tie(a, b) = pair;` のように、tuple の中身を既存の変数に代入するのにも使えます。

!!! tip "ポイント"
    - 比較関数: `std::tie(a.level, a.name) < std::tie(b.level, b.name)` で、辞書順の比較になる。
    - 降順にしたい項目は、`a` と `b` を入れ替える（上の例）。
    - 使わない要素は [`std::ignore`](ignore.md)。

## 関数の詳しい説明

### std::tie {#tie}

```cpp
template <class... Types>
constexpr std::tuple<Types&...> tie(Types&... args) noexcept;
```

- 変数の**参照**をまとめた tuple を作ります。複数の条件で比べる比較関数を短く書くのに使います

```cpp
#include <print>
#include <string>
#include <tuple>

struct Player {
  int level;
  std::string name;
};

bool Before(const Player& a, const Player& b) {
  // レベルの大きい順、同じなら名前順
  return std::tie(b.level, a.name) < std::tie(a.level, b.name);
}

int main() {
  Player x = {5, "Bob"};
  Player y = {5, "Alice"};
  std::println("{}", Before(y, x));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| (レベル, 名前) の複数条件のソート | `return std::tie(a.level, a.name) < std::tie(b.level, b.name);` |
| 関数の戻り値（pair / tuple）を既存の変数に受ける | `std::tie(x, y) = GetPos();` |

## よくあるミス

??? failure "一時オブジェクトを tie する"
    `std::tie(Func())` のように一時的な値を渡すと、すぐ消える値を参照します。変数だけを渡します。

??? failure "構造化束縛で足りる場面で使う"
    新しい変数に受けるなら `auto [a, b] = ...;` のほうが読みやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| 構造化束縛 `auto [a, b]` | 新しい変数に取り出す |
| [`std::make_tuple`](make_tuple.md) | 値のコピーを持つ tuple を作る |
| [`std::forward_as_tuple`](forward_as_tuple.md) | 転送用の参照を持つ tuple |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 変数の参照をまとめる
    - [x] 比較関数を 1 行で書ける
    - [x] 使わない要素は `std::ignore`

## 関連ページ

- [cpprefjp: std::tie](https://cpprefjp.github.io/reference/tuple/tie.html)
- [cppreference: std::tie](https://en.cppreference.com/w/cpp/utility/tuple/tie)
