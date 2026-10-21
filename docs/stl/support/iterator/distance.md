---
title: std::distance
summary: "2 つのイテレータの間の要素数を返す。"
order: 4
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::distance

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <iterator>`
</div>

`std::distance(first, last)` は、**2 つのイテレータの間にある要素の数**を返す関数です。「見つかった位置は何番目か」を `distance(v.begin(), it)` で求めます。ランダムアクセスできる範囲では O(1)、`list` では O(n) です。

!!! tip "ポイント"
    - `it - v.begin()` と同じ（vector）。
    - `list` など、引き算できない範囲で使う。
    - `first` から `last` に到達できなければ未定義動作。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::distance {#distance}

```cpp
template <class InputIt>
std::iter_difference_t<InputIt> distance(InputIt first, InputIt last);
```

- `first` から `last` まで何個あるか。vector なら O(1)、list なら O(n)。見つかった位置の添字を出すのにも使えます

<div class="anim" data-label="std::distance(first, last)">
*a b c *d # first は a、last は d
*a *b *c d # 間の個数（3）を数える
</div>

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto it = std::find(v.begin(), v.end(), 3);
  std::println("{}", std::distance(v.begin(), it));
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 見つけた要素の添字を求める | `std::distance(v.begin(), it)` |

## よくあるミス

??? failure "順番を逆にする"
    `distance(last, first)` は負の数（または未定義）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::distance`](distance.md) | ranges 版 |
| [`advance`](advance.md) | 進める |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの間の要素数
    - [x] vector は O(1)
    - [x] list は O(n)

## 関連ページ

- [cpprefjp: std::distance](https://cpprefjp.github.io/reference/iterator/distance.html)
- [cppreference: std::distance](https://en.cppreference.com/w/cpp/iterator/distance)
