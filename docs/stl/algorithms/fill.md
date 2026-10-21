---
title: std::ranges::fill
summary: "範囲の全要素を、同じ値で埋める。"
order: 45
tags:
  - アルゴリズム
---

# std::ranges::fill

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::fill` は、**範囲の全要素を同じ値で埋める**アルゴリズムです。配列を 0 で初期化する、画面を 1 色で塗りつぶす、といったときに使います。先頭から n 個だけ埋める `fill_n` もあります。

!!! tip "ポイント"
    - 新しい `vector` を作るときは、コンストラクタ `std::vector<int>(n, 0)` のほうが短い。
    - 既にある配列を**初期化し直す**ときに使う。
    - 1 バイトずつ埋めたいなら `std::memset`（[cstring](../memory/cstring.md)）のほうが速いこともあるが、型安全ではない。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fill {#fill}

```cpp
template <class T, output_range<const T&> R>
constexpr borrowed_iterator_t<R> fill(R&& r, const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 埋める範囲 |
| `value` | `const T&` | 入れる値 |

<div class="anim" data-label="std::ranges::fill(v, 0)">
1 2 3 4 # v
+0 +0 +0 +0 # 全要素を同じ値で埋める
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> visited(6, 1);
  std::ranges::fill(visited, 0);  // 毎回の探索の前にリセット
  std::println("{}", visited);
}
```

```text title="実行結果"
[0, 0, 0, 0, 0, 0]
```

### std::ranges::fill_n {#fill_n}

```cpp
template <class T, output_iterator<const T&> O>
constexpr O fill_n(O first, std::iter_difference_t<O> n, const T& value);
```

- `first` から `n` 個を `value` で埋めます

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {9, 8, 7, 6};
  std::vector<int> dst(4, 0);
  std::ranges::copy_n(src.begin(), 2, dst.begin());
  std::ranges::fill_n(dst.begin() + 2, 2, 5);
  std::println("{}", dst);
}
```

```text title="実行結果"
[9, 8, 5, 5]
```


## フラグ・オプション

| 関数 | 重要度 | 意味 |
| --- | --- | --- |
| `fill` | <span class="rank rank-sometimes">たまに</span> | 全要素を同じ値で埋める |
| `fill_n` | <span class="rank rank-rare">知ってるだけ</span> | 先頭から n 個だけ埋める |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| マップのマスを全部「空」にする | `fill(tiles, Tile::kEmpty)` |
| フレームバッファを 1 色で塗る | `fill(pixels, color)` |
| ステージ開始時にフラグを全部 false に戻す | `fill(flags, false)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `fill_n` で、範囲より大きい個数を指定する | 範囲外への書き込み（未定義動作） |

## よくあるミス

??? failure "空の vector に fill する"
    `std::vector<int> v; std::ranges::fill(v, 0);` は何も起きません。要素の数は変わらないので、個数を決めるなら `v.assign(n, 0)` か `v.resize(n, 0)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::generate`](generate.md) | 関数を呼んで、毎回違う値で埋める |
| [`std::ranges::iota`](iota.md) | 1 ずつ増える連番で埋める |
| `std::vector::assign` | 個数ごと入れ替える |
| `std::memset` | バイト単位で埋める（C 由来） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全要素を同じ値で埋める
    - [x] 個数指定は `fill_n`
    - [x] 要素数は変わらない

## 関連ページ

- [cpprefjp: std::ranges::fill](https://cpprefjp.github.io/reference/algorithm/ranges_fill.html)
- [cppreference: std::ranges::fill](https://en.cppreference.com/w/cpp/algorithm/ranges/fill)
