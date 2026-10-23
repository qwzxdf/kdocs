---
title: std::back_inserter
summary: "代入するたびに、コンテナの末尾に push_back するイテレータ。"
order: 10
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::back_inserter

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <iterator>`
</div>

`std::copy` で別の `vector` に写すとき、コピー先の大きさが足りないと、範囲外に書き込んでしまいます。先に `resize` するのも手間です。`std::back_inserter(c)` は、代入するたびにコンテナの末尾へ `push_back` するイテレーターを作ります。これを出力先に渡せば、結果が自動で末尾へ足され、コンテナが必要なだけ大きくなります。

!!! tip "ポイント"
    - `std::ranges::copy(src, std::back_inserter(dst));`
    - `push_back` があるコンテナにだけ使える（`vector`、`deque`、`list`、`string`）。
    - `vector` では、事前に `reserve` すると速い。

!!! info "このページを読む前に"
    [イテレーター](../../../basics/iterator.md)の基本と、`copy` や `transform` の使い方を先に読んでください。

## 関数の詳しい説明

### std::back_inserter {#back_inserter}

```cpp
template <class Container>
std::back_insert_iterator<Container> back_inserter(Container& c);
```

- このイテレータに書き込む（`*it = x`）と、`c.push_back(x)` が呼ばれます。アルゴリズムの出力先に使います

<div class="anim" data-label="std::back_inserter(v)">
1 2 # v
1 2 +3 # 代入するたびに push_back される
1 2 3 +4 # 出力先の大きさを気にしなくてよい
</div>

## しくみ

`back_inserter` が返すのは `back_insert_iterator` というイテレーターで、`*it = value` と代入すると、中でコンテナの `push_back(value)` を呼びます。進める（`++it`）操作は何もしません。

出力先を「書き込み先の位置」ではなく「追加するコンテナ」で指定する、という考え方です。出力先の大きさを気にしなくてよくなる反面、`push_back` の回数だけ、要素が必要に応じて再確保されることがあります。

`push_back` がないコンテナ（`set` や `map`）には使えません。先頭に追加するなら `front_inserter`、任意の位置に追加するなら `inserter` があります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {1, 2, 3};
  std::vector<int> dst;  // 空のまま
  std::ranges::copy(src, std::back_inserter(dst));
  std::println("{}", dst);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

別のコンテナに結果を集める処理に使います。`std::ranges::copy_if(enemies, std::back_inserter(alive), IsAlive)` なら、生きている敵だけが `alive` に集まります。

事前に `alive.reserve(enemies.size())` で容量を確保しておくと、再確保が起きず速くなります。件数が分からないときは、最大の件数で `reserve` するか、`std::ranges::to` で `vector` に変換する方法もあります。

`transform` の出力先にも向いています。変換の結果を別の `vector` に溜めたいときに、`std::back_inserter(out)` を渡します。

## よくあるミス

??? failure "`reserve` せずに大量に追加して、再確保が何度も起きる"
    `push_back` が繰り返されるたびに、容量が足りなくなると再確保されます。件数の目安が分かるなら、事前に `reserve` しておきます。

??? failure "コピー元とコピー先が同じコンテナ"
    `copy(v, back_inserter(v))` は、`push_back` で `v` が再確保され、読み取り中のイテレーターが壊れます。別のコンテナに写します。

??? failure "`set` や `map` に使ってコンパイルエラーになる"
    `push_back` が無いコンテナには使えません。`std::inserter(s, s.end())` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::front_inserter` | 先頭に追加する。`push_front` があるコンテナ向け |
| `std::inserter` | 任意の位置に追加する。`set` や `map` でも使える |
| [`std::ranges::to`](../../algorithms/ranges_to.md) | ビューの結果を新しいコンテナに作り直す。C++23 |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力先に渡すと、代入のたびに `push_back` される。
    - [x] 事前に `reserve` すると速い。
    - [x] `set` や `map` には `inserter` を使う。

## 関連ページ

- [cpprefjp: std::back_inserter](https://cpprefjp.github.io/reference/iterator/back_inserter.html)
- [cppreference: std::back_inserter](https://en.cppreference.com/w/cpp/iterator/back_inserter)
