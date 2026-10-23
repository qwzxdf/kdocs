---
title: std::piecewise_construct
summary: "pair の 2 つの要素を、それぞれ別のコンストラクタ引数で作るための印。"
order: 60
tags:
  - ユーティリティ
---

# std::piecewise_construct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

`std::piecewise_construct` は、**pair の 1 つ目と 2 つ目を、それぞれ別々のコンストラクタ引数（tuple）で作る**ための印です。`map::emplace` で、キーと値の両方に複数の引数を渡したいときに使います。

!!! tip "ポイント"
    - `m.emplace(std::piecewise_construct, std::forward_as_tuple(キーの引数...), std::forward_as_tuple(値の引数...));` という形で使う。
    - 普通は `try_emplace` のほうが読みやすい。
    - 知っておくだけでよい。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::piecewise_construct {#piecewise_construct}

```cpp
inline constexpr std::piecewise_construct_t piecewise_construct{};
```

- 戻り値: （タグ。pair のコンストラクタの先頭に渡す）
- 計算量: O(1)

```cpp
#include <map>
#include <print>
#include <string>
#include <tuple>

struct Vec {
  Vec(int x, int y) : x(x), y(y) {}
  int x;
  int y;
};

int main() {
  std::map<std::string, Vec> positions;

  // キーは "a"、値は Vec(1, 2) を、それぞれ別の引数で作る
  positions.emplace(std::piecewise_construct,
                    std::forward_as_tuple("a"),
                    std::forward_as_tuple(1, 2));
  std::println("{} {}", positions.at("a").x, positions.at("a").y);
}
```

```text title="実行結果"
1 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| map に、コピーを作らず、値を直接構築して入れる | `try_emplace(key, args...)`（こちらが簡単） |

## よくあるミス

??? failure "try_emplace で足りるのに使う"
    `std::map::try_emplace(key, 値の引数...)` で同じことができ、短く書けます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::map::try_emplace` | キーと値の引数を分けて渡せる。簡単 |
| [`std::forward_as_tuple`](forward_as_tuple.md) | 引数を tuple にまとめる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] pair の要素を別々の引数で作る印
    - [x] `map::emplace` と使う
    - [x] 普通は `try_emplace` が簡単

## 関連ページ

- [cpprefjp: std::piecewise_construct](https://cpprefjp.github.io/reference/utility/piecewise_construct.html)
- [cppreference: std::piecewise_construct](https://en.cppreference.com/w/cpp/utility/piecewise_construct)
