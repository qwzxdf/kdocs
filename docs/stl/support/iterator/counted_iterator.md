---
title: std::counted_iterator
summary: "残りの個数を数えながら進むイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::counted_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

「先頭から n 個だけ」を処理したいとき、`take` のような view を使わなくても、`counted_iterator` で個数つきのイテレータにできます。残りが 0 になると、`default_sentinel` と等しくなります。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::counted_iterator {#counted_iterator}

```cpp
template <input_or_output_iterator It>
class counted_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `It` | 型 | 元のイテレータ |

- 戻り値: `count()` で残りの個数
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
  std::vector<int> out;
  std::ranges::copy(std::counted_iterator(v.begin(), 2), std::default_sentinel, std::back_inserter(out));
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 先頭から n 個だけ処理する |

## よくあるミス

??? failure "n を要素数より大きくする"
    要素数を超えると範囲外を読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_sentinel`](default_sentinel.md) | 終端 |
| [`views::counted`](../../algorithms/views/counted.md) | view 版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 残りの個数を数えながら進むイテレータ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::counted_iterator](https://cpprefjp.github.io/reference/iterator/counted_iterator.html)
- [cppreference: std::counted_iterator](https://en.cppreference.com/w/cpp/iterator/counted_iterator)
