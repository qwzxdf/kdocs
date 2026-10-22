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

必ず見つかると分かっている検索では、終端の比較が不要です。`unreachable_sentinel` を終端に渡すと、「この範囲は終わらない」とコンパイラに伝え、終端の比較が省かれます。見つからないと範囲外を読みます。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::unreachable_sentinel {#unreachable_sentinel}

```cpp
struct unreachable_sentinel_t {};
inline constexpr unreachable_sentinel_t unreachable_sentinel{};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  auto it = std::ranges::find(v.begin(), std::unreachable_sentinel, 3);
  std::println("{}", *it);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 必ず見つかる検索を、終端の比較なしで速くする |

## よくあるミス

??? failure "見つからないかもしれない検索に使う"
    見つからないと、範囲外へ読み進めて未定義動作になります。必ず存在する場合だけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::iota`](../../algorithms/views/iota.md) | 終わりのない範囲 |
| [`default_sentinel`](default_sentinel.md) | 個数が決まった終端 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「終わりには絶対に届かない」と約束する終端
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::unreachable_sentinel](https://cpprefjp.github.io/reference/iterator/unreachable_sentinel.html)
- [cppreference: std::unreachable_sentinel](https://en.cppreference.com/w/cpp/iterator/unreachable_sentinel)
