---
title: std::iter_move
summary: "イテレータが指す要素を、右辺値として取り出す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iter_move

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータの先の要素を、右辺値として取り出したい。通常は `std::move(*it)` と書きますが、プロキシ参照を返すイテレータでは、これが正しく動かないことがあります。`std::ranges::iter_move(it)` は、イテレータの種類に応じて、正しく右辺値を取り出します。

!!! tip "ポイント"
    - イテレータの先の要素を、右辺値の参照として返す
    - 通常のイテレータでは `std::move(*it)` と同じ
    - プロキシ参照のイテレータでは、カスタマイゼーション ポイントで正しい動作ができる
    - `std::ranges::move` などのアルゴリズムが使う

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::iter_move {#iter_move}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ iter_move = /* 未規定 */;
// 戻り値の型: std::iter_rvalue_reference_t<I>
```

`*it` が左辺値を返すイテレータでは `std::move(*it)` と同じで、`T&&` を返します。`*it` が値（プロキシ）を返すイテレータでは、その値をそのまま返します。

自作のイテレータが特別なムーブの動作を持つなら、`iter_move(it)` という自由関数を、ADL で見つかるように用意します。`std::ranges::move` や `std::ranges::uninitialized_move` は内部で `iter_move` を呼ぶので、プロキシ参照のイテレータの範囲も、正しくムーブできます。

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
  std::vector<std::string> v = {"hero", "mage"};

  // 先頭の要素を右辺値として取り出して、ムーブ構築する
  std::string taken = std::ranges::iter_move(v.begin());
  std::println("取り出した: {}", taken);
  std::println("元は空: {}", v[0].empty());

  static_assert(std::is_same_v<std::iter_rvalue_reference_t<std::vector<std::string>::iterator>, std::string&&>);
}
```

```text title="実行結果"
取り出した: hero
元は空: true
```

## ゲームでの使いどころ

自作のアルゴリズムで、イテレータの先から要素をムーブするときに、`std::move(*it)` の代わりに使います。

## よくあるミス

??? failure "ムーブ後の要素を使う"
    元の要素は、ムーブされた状態です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_reference_t`](iter_reference_t.md) | 参照の型 |
| [`indirectly_movable`](../concepts/indirectly_movable.md) | ムーブできる条件 |
| [`move_sentinel`](move_sentinel.md) | ムーブするイテレータの番兵 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::iter_move](https://cpprefjp.github.io/reference/iterator/iter_move.html)
- [cppreference: std::iter_move](https://en.cppreference.com/w/cpp/iterator/iter_move)
