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

終端のイテレータを別に用意しなくても、「数え終わった」ことを `default_sentinel` と比べて知らせる仕組みです。`counted_iterator` が終わりかを調べるときに使います。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::default_sentinel {#default_sentinel}

```cpp
struct default_sentinel_t {};
inline constexpr default_sentinel_t default_sentinel{};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  int sum = 0;
  for (std::counted_iterator it(v.begin(), 2); it != std::default_sentinel; ++it) {
    sum += *it;
  }
  std::println("{}", sum);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 個数で止まるループ |

## よくあるミス

??? failure "普通のイテレータと比べる"
    `default_sentinel` と比べられるのは、対応するイテレータ（`counted_iterator` など）だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`counted_iterator`](counted_iterator.md) | これと使う |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] counted_iterator などの終端を表す目印の定数
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::default_sentinel](https://cpprefjp.github.io/reference/iterator/default_sentinel.html)
- [cppreference: std::default_sentinel](https://en.cppreference.com/w/cpp/iterator/default_sentinel)
