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

範囲の終端が別の型（sentinel）のとき、`move_iterator` とそろえた終端として `move_sentinel` を使います。ふつうは `ranges::copy` などの C++20 のアルゴリズムに、`move_iterator` と一緒に渡します。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::move_sentinel {#move_sentinel}

```cpp
template <semiregular S>
class move_sentinel;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `S` | 型 | 元の終端の型 |

- 戻り値: ムーブ用の終端として比較に使う
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> src = {"aaaaaaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbbbbbb"};
  std::vector<std::string> dst;
  std::ranges::copy(std::move_iterator(src.begin()), std::move_sentinel(src.end()), std::back_inserter(dst));
  std::println("{}", dst.size());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 範囲の中身を別の場所へムーブする |

## よくあるミス

??? failure "コピーだと思う"
    `move_iterator` 経由では要素はムーブされ、元は空になるかもしれません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`move_iterator`](move_iterator.md) | ムーブ用イテレータ |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] move_iterator と組み合わせる、ムーブ用の終端
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::move_sentinel](https://cpprefjp.github.io/reference/iterator/move_sentinel.html)
- [cppreference: std::move_sentinel](https://en.cppreference.com/w/cpp/iterator/move_sentinel)
