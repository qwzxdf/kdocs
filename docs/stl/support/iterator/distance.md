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

2 つのイテレーターの間に、要素がいくつあるか知りたい。`last - first` は、ランダムアクセスのイテレーターにしか使えません。`std::distance(first, last)` は、<strong>どんなイテレーターでも間の要素数を返します</strong>。

!!! tip "ポイント"
    - `std::distance(first, last)` は `first` から `last` までの要素数
    - ランダムアクセスは O(1)、それ以外は O(n)
    - `last` に `first` から到達できること
    - 要素の位置（添字）を求めるのにも使える

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::distance {#distance}

<span class="ver ver-98">C++98</span>

```cpp
template <class It>
constexpr typename std::iterator_traits<It>::difference_type
distance(It first, It last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレーター | 始まり |
| `last` | イテレーター | 終わり（`first` から到達できること） |

`first` を `last` に到達するまで進めた回数を返します。`first` より `last` が前にある場合は、ランダムアクセスのイテレーターでは負の値になり、それ以外では未定義動作です。

`std::find` が返したイテレーターから、要素の添字を求めるときによく使います。`std::list` の要素数を `distance(begin, end)` で求めると O(n) ですが、`l.size()` は O(1) です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30, 40};
  auto it = std::find(v.begin(), v.end(), 30);
  std::println("30 の添字: {}", std::distance(v.begin(), it));
  std::println("全体の要素数: {}", std::distance(v.begin(), v.end()));
}
```

```text title="実行結果"
30 の添字: 2
全体の要素数: 4
```

## ゲームでの使いどころ

検索で見つけた要素の位置（添字）を求めます。

```cpp
auto it = std::ranges::find(items, target);
const auto index = std::distance(items.begin(), it);
```

## よくあるミス

??? failure "`first` と `last` を逆にする"
    `first` が前でなければなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`next`](next.md) | 進める |
| [`advance`](advance.md) | 元を進める |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::distance(first, last)` は間の要素数
    - [x] 位置（添字）を求めるのに使う
    - [x] 双方向以下のイテレーターは O(n)

## 関連ページ

- [cpprefjp: std::distance](https://cpprefjp.github.io/reference/iterator/distance.html)
- [cppreference: std::distance](https://en.cppreference.com/w/cpp/iterator/distance)
