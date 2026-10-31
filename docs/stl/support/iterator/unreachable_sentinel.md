---
title: std::unreachable_sentinel
summary: "「終わりには絶対に届かない」と約束する終端。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::unreachable_sentinel

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

「必ず見つかる」と分かっている探索では、終端の検査が無駄です。`std::unreachable_sentinel` は、<strong>どのイテレータと比べても決して等しくならない</strong>番兵で、終端の検査をコンパイラが取り除けます。範囲の大きさが無限の `iota_view` の終端にも使われます。

!!! tip "ポイント"
    - どのイテレータとも等しくならない番兵
    - 終端の検査が不要な探索に使うと速くなる
    - 本当に見つかる保証がないと、範囲の外へ読み続ける
    - 無限の範囲（`iota(0)`）の終端にもなる

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::unreachable_sentinel {#unreachable_sentinel}

<span class="ver ver-20">C++20</span>

```cpp
struct unreachable_sentinel_t {
  template <std::weakly_incrementable I>
  friend constexpr bool operator==(unreachable_sentinel_t, const I&) noexcept { return false; }
};
inline constexpr std::unreachable_sentinel_t unreachable_sentinel{};
```

比較が常に偽を返すだけなので、ループの終了判定が消えます。

```cpp
std::ranges::find(v.begin(), std::unreachable_sentinel, 3);   // 3 が必ずあるなら、終端の検査なし
```

探している値が範囲になかった場合は、範囲の外を読み続けるので未定義動作です。必ず見つかる保証がある場面（番兵の値を末尾に置いてある）にだけ使います。

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
  std::vector<int> v = {5, 8, 3, 9};

  // 3 が必ずあるので、終端の検査を省ける
  auto it = std::ranges::find(v.begin(), std::unreachable_sentinel, 3);
  std::println("位置: {}", it - v.begin());

  // 無限の範囲の終端
  auto nums = std::views::iota(1);  // 1, 2, 3, ... (終わりなし)
  static_assert(std::is_same_v<std::ranges::sentinel_t<decltype(nums)>, std::unreachable_sentinel_t>);
  std::println("先頭: {}", *nums.begin());
}
```

```text title="実行結果"
位置: 2
先頭: 1
```

## ゲームでの使いどころ

番兵を末尾に置いた配列で、終端の検査なしに探索するときに使います。

## よくあるミス

??? failure "見つからない可能性がある探索に使う"
    範囲の外を読み続けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_sentinel`](default_sentinel.md) | 終わりの条件をイテレータに任せる |
| [`sentinel_for`](../concepts/sentinel_for.md) | 番兵のコンセプト |
| [`iota`](../../algorithms/views/iota.md) | 無限の範囲を作る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::unreachable_sentinel](https://cpprefjp.github.io/reference/iterator/unreachable_sentinel.html)
- [cppreference: std::unreachable_sentinel](https://en.cppreference.com/w/cpp/iterator/unreachable_sentinel)
