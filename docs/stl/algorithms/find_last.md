---
title: std::ranges::find_last
summary: "条件に合う（または等しい）最後の要素を探す。"
order: 16
tags:
  - アルゴリズム
---

# std::ranges::find_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`std::ranges::find_last` は、**値と等しい最後の要素**を探します。[`find`](find.md) が先頭から探すのに対し、こちらは「最後に出てきた所」を返します。条件で探す `find_last_if` もあります。

!!! tip "ポイント"
    - 戻り値は**位置ではなく、その位置から終わりまでの範囲**（`subrange`）。`.begin()` で位置が取れる。
    - 見つからなければ、空の範囲（`.empty()` が `true`）。
    - 逆順にして `find` するより、`find_last` のほうが読みやすい。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::find_last <span class="ver ver-23">C++23</span> {#find_last data-toc-label="std::ranges::find_last"}

```cpp
template <forward_range R, class T, class Proj = identity>
constexpr borrowed_subrange_t<R> find_last(R&& r, const T& value, Proj proj = {});
```

- 戻り値: **最後に**見つかった要素から終わりまでの範囲（`subrange`）。`.begin()` がその位置。見つからなければ空の範囲

<div class="anim" data-label="std::ranges::find_last(v, 2)">
2 1 2 3 # 値が 2 の最後の要素
2 1 *2 3 # 後ろ側のものが見つかる
</div>

### std::ranges::find_last_if <span class="ver ver-23">C++23</span> {#find_last_if data-toc-label="std::ranges::find_last_if"}

```cpp
template <forward_range R, class Proj = identity, class Pred>
constexpr borrowed_subrange_t<R> find_last_if(R&& r, Pred pred, Proj proj = {});
```

- 条件に合う**最後の**要素を探します

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> checkpoints = {0, 1, 0, 1, 0};
  auto last = std::ranges::find_last(checkpoints, 1);
  std::println("最後の 1 は {} 番目", last.begin() - checkpoints.begin());
}
```

```text title="実行結果"
最後の 1 は 3 番目
```

!!! note "実際は"
    戻り値がイテレータではなく範囲なので少し扱いにくいです。`.begin()` を取れば位置になります。


## フラグ・オプション

| 関数 | 重要度 | 意味 |
| --- | --- | --- |
| `find_last` | <span class="rank rank-rare">知ってるだけ</span> | 値と等しい最後の要素 |
| `find_last_if` | <span class="rank rank-rare">知ってるだけ</span> | 条件に合う最後の要素 |
| `find_last_if_not` | <span class="rank rank-rare">知ってるだけ</span> | 条件に合わない最後の要素 |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 直前に通ったチェックポイント | `find_last(checkpoints, 1)` |
| 最後に被弾した時刻のログ | `find_last_if(log, 被弾)` |

## よくあるミス

??? failure "戻り値を要素のイテレータだと思う"
    `find_last` は `subrange` を返します。先頭の位置は `.begin()`、見つかったかは `!r.empty()` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](find.md) | 先頭から探して、最初のものを返す |
| [`std::views::reverse`](views/reverse.md) | 逆順にして `find` する代わりの方法 |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 19 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最後に出てきた所を探す
    - [x] 戻り値は部分範囲
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::find_last](https://cpprefjp.github.io/reference/algorithm/ranges_find_last.html)
- [cppreference: std::ranges::find_last](https://en.cppreference.com/w/cpp/algorithm/ranges/find_last)
