---
title: std::ranges::partition_copy
summary: "条件に合う要素と合わない要素を、元を残したまま 2 つの場所に振り分ける。"
order: 50
tags:
  - アルゴリズム
---

# std::ranges::partition_copy

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

味方と敵を別々のリストに分けたい。元のリストは残したい。`partition` は元の配列を並べ替えてしまいます。`std::ranges::partition_copy` は、条件に合う要素と合わない要素を 2 つの別々の場所へ振り分けてコピーします。元の範囲は変わりません。各グループの中の順序は、元の順序のままです。

!!! tip "ポイント"
    - 書き出し先を 2 つ渡す（条件に合う側、合わない側）。
    - 元の範囲は変わらない。
    - 各側の中の順序は、元の順序のまま。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::partition_copy {#partition_copy}

```cpp
template <input_range R, weakly_incrementable O1, weakly_incrementable O2, class Proj = identity,
          class Pred>
constexpr partition_copy_result<borrowed_iterator_t<R>, O1, O2>
partition_copy(R&& r, O1 out_true, O2 out_false, Pred pred, Proj proj = {});
```

- 条件に合うものを `out_true` に、合わないものを `out_false` に、元を変えずにコピーします

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {80, 45, 92, 30};
  std::vector<int> pass;
  std::vector<int> fail;
  std::ranges::partition_copy(scores, std::back_inserter(pass), std::back_inserter(fail),
                              [](int s) { return s >= 50; });
  std::vector<int> sorted = {9, 7, 5, 2, 1};  // 5 以上が前に分かれている
  auto p = std::ranges::partition_point(sorted, [](int x) { return x >= 5; });
  std::println("{} {} / 分かれ目 {}", pass, fail, *p);
}
```

```text title="実行結果"
[80, 92] [45, 30] / 分かれ目 2
```

## ゲームでの使いどころ

敵と味方、合格と不合格、表示するものとしないもの、といった分け方に使います。`partition_copy(units, back_inserter(allies), back_inserter(enemies), IsAlly)` で、1 回の走査で 2 つに分けられます。

2 回 `copy_if` を呼ぶ方法もありますが、`partition_copy` なら走査が 1 回で済みます。条件の判定が重い場合に差が出ます。

元の範囲を並べ替えてよいなら、`partition` のほうがメモリを使わず、速くなります。

## よくあるミス

??? failure "書き出し先の順番を逆にする"
    1 つ目が「条件に合う」側、2 つ目が「合わない」側です。

??? failure "書き出し先の大きさが足りない"
    出力先に `begin()` を渡すと、足りない場合に範囲外へ書き込みます。`back_inserter` を使うと安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::partition`](partition.md) | 元の範囲の中で分ける |
| [`std::ranges::copy`](copy.md) | `copy_if` は片側だけコピーする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの出力に振り分ける
    - [x] 元は変わらない
    - [x] 順序は保たれる

## 関連ページ

- [cpprefjp: std::ranges::partition_copy](https://cpprefjp.github.io/reference/algorithm/ranges_partition_copy.html)
- [cppreference: std::ranges::partition_copy](https://en.cppreference.com/w/cpp/algorithm/ranges/partition_copy)
