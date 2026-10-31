---
title: std::default_sentinel
summary: "counted_iterator などの終端を表す目印の定数。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::default_sentinel

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータの終わりを表すのに、同じ型のイテレータを用意するのが従来の方法でした。しかし、終わりが「個数に達したとき」「入力が尽きたとき」のように、イテレータの内部の状態で決まる場合、終端用のイテレータを作るのは無駄です。`std::default_sentinel` は、「このイテレータ自身が持つ終わりの条件を使え」という、汎用の番兵です。

!!! tip "ポイント"
    - 型は `std::default_sentinel_t`。値は `std::default_sentinel`
    - `counted_iterator` などと `==` で比べると、終わりに達したかが分かる
    - 範囲の `end()` に使えて、イテレータとは別の型の終端を作れる
    - C++20

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::default_sentinel {#default_sentinel}

<span class="ver ver-20">C++20</span>

```cpp
struct default_sentinel_t { explicit default_sentinel_t() = default; };
inline constexpr std::default_sentinel_t default_sentinel{};
```

空の構造体です。比較の演算子は、使うイテレータ側が用意します。たとえば `counted_iterator` は、残りの個数が 0 のとき、`default_sentinel` と等しくなります。

自作のイテレータに「終わりの条件」があるなら、`friend bool operator==(const MyIt&, std::default_sentinel_t)` を用意すると、`default_sentinel` を終端として使えます。

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
  std::vector<int> v = {10, 20, 30, 40, 50};

  // 先頭から 3 個だけ数える counted_iterator
  std::counted_iterator it(v.begin(), 3);
  int sum = 0;
  for (; it != std::default_sentinel; ++it) sum += *it;

  std::println("先頭 3 個の合計: {}", sum);
}
```

```text title="実行結果"
先頭 3 個の合計: 60
```

## ゲームでの使いどころ

個数が決まった範囲を、終端用のイテレータなしでループするときに使います。

## よくあるミス

??? failure "比較の演算子がないイテレータと比べる"
    コンパイルできません。イテレータ側の対応が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unreachable_sentinel`](unreachable_sentinel.md) | 決して終わらない番兵 |
| [`counted_iterator`](counted_iterator.md) | 個数を数えるイテレータ |
| [`sentinel_for`](../concepts/sentinel_for.md) | 番兵のコンセプト |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::default_sentinel](https://cpprefjp.github.io/reference/iterator/default_sentinel.html)
- [cppreference: std::default_sentinel](https://en.cppreference.com/w/cpp/iterator/default_sentinel)
