---
title: std::adjacent_difference
summary: "隣り合う要素の差を求める。"
order: 29
tags:
  - アルゴリズム
---

# std::adjacent_difference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <numeric>`
</div>

時間ごとの累計から、各時間の増分を求めたい。スコアの推移から、1 回ごとの得点を求めたい。隣り合う要素の差を並べるのが `std::adjacent_difference` です。`partial_sum` の逆の働きで、先頭の要素はそのまま、2 番目以降は「自分 - 1 つ前」になります。

!!! tip "ポイント"
    - 出力の先頭は入力の先頭のまま。2 番目以降は、前の要素との差
    - 出力の長さは入力と同じ
    - 入力と出力が同じ範囲でもよい（その場で変換できる）
    - 差を別の演算（割り算など）にも変えられる

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::adjacent_difference {#adjacent_difference}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class InputIt, class OutputIt>
OutputIt adjacent_difference(InputIt first, InputIt last, OutputIt d_first);

template <class InputIt, class OutputIt, class BinaryOp>
OutputIt adjacent_difference(InputIt first, InputIt last, OutputIt d_first, BinaryOp op);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | 入力イテレータ | 入力の範囲 |
| `d_first` | 出力イテレータ | 出力の先頭 |
| `op` | 二項関数 | 差の代わりの演算。省略すると `-` |

`out[0] = in[0]`、`out[i] = op(in[i], in[i-1])` です。戻り値は、出力の最後の次の位置です。

入力と出力が同じ範囲でも、先頭から順に処理されるので、結果が壊れません。

並列版（`std::execution` つき）は、演算が結合法則を満たす必要はありませんが、実行の順序は規定されないので、`op` に副作用を持たせてはいけません。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  const std::vector<int> total = {1, 4, 9, 16};  // 累計
  std::vector<int> each(total.size());
  std::adjacent_difference(total.begin(), total.end(), each.begin());
  std::println("{}", each);  // 各回の増分

  // 差の代わりに、積にする
  std::vector<int> prod(total.size());
  std::adjacent_difference(total.begin(), total.end(), prod.begin(), std::multiplies<>());
  std::println("{}", prod);

  // その場で変換する
  std::vector<int> v = {1, 3, 6, 10};
  std::adjacent_difference(v.begin(), v.end(), v.begin());
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 3, 5, 7]
[1, 4, 36, 144]
[1, 2, 3, 4]
```

## ゲームでの使いどころ

フレームごとの累計時間から、各フレームの経過時間を求めるときに使います。

## よくあるミス

??? failure "先頭が差になると思う"
    先頭は入力のままです。

??? failure "出力の領域が足りない"
    出力は入力と同じ長さが要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`partial_sum`](partial_sum.md) | 逆。累計を求める |
| [`inclusive_scan`](inclusive_scan.md) | 累計の新しい形 |
| [`transform`](transform.md) | 要素ごとの変換 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::adjacent_difference](https://cpprefjp.github.io/reference/numeric/adjacent_difference.html)
- [cppreference: std::adjacent_difference](https://en.cppreference.com/w/cpp/algorithm/adjacent_difference)
