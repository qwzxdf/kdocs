---
title: std::move_sentinel
summary: "move_iterator と組み合わせる、ムーブ用の終端。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::move_sentinel

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::move_iterator` は、イテレータの先の要素を右辺値として返します。範囲の終端がイテレータとは別の型の番兵のとき、番兵も `move_iterator` と比較できる形にする必要があります。`std::move_sentinel<S>` は、番兵 `S` を包んで、`move_iterator` と比べられるようにします。

!!! tip "ポイント"
    - `move_iterator` の終端用に、番兵を包むアダプター
    - `move_iterator<I>` と `move_sentinel<S>` を `==` で比べられる
    - イテレータと番兵が同じ型なら不要（`move_iterator` で足りる）
    - C++20

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::move_sentinel {#move_sentinel}

<span class="ver ver-20">C++20</span>

```cpp
template <std::semiregular S>
class move_sentinel {
 public:
  constexpr move_sentinel(S s);
  constexpr S base() const;
};
```

`std::ranges::subrange(std::move_iterator(first), std::move_sentinel(last))` のように、範囲の要素をムーブして取り出すときに使います。

通常の `vector` のイテレータなら、`std::move_iterator(v.begin())` と `std::move_iterator(v.end())` の組で足ります。`move_sentinel` が必要なのは、終端が別の型の番兵のときです。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <ranges>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

int main() {
  std::vector<std::string> src = {"hero", "mage", "thief"};
  std::vector<std::string> dst;

  std::move_iterator it(src.begin());
  std::move_sentinel end(src.end());
  for (; it != end; ++it) dst.push_back(*it);  // 右辺値として取り出される

  std::println("{}", dst);
  std::println("元は空: {}", src[0].empty());
}
```

```text title="実行結果"
["hero", "mage", "thief"]
元は空: true
```

## ゲームでの使いどころ

要素をコピーせずに別のコンテナへ移すループを、範囲ライブラリの流儀で書くときに使います。

## よくあるミス

??? failure "ムーブ後の元の要素を使う"
    ムーブされた状態です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_move`](iter_move.md) | 右辺値として取り出す |
| [`sentinel_for`](../concepts/sentinel_for.md) | 番兵のコンセプト |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::move_sentinel](https://cpprefjp.github.io/reference/iterator/move_sentinel.html)
- [cppreference: std::move_sentinel](https://en.cppreference.com/w/cpp/iterator/move_sentinel)
