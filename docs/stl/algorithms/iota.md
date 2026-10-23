---
title: std::iota
summary: "範囲を、1 ずつ増える連番で埋める。"
order: 46
tags:
  - アルゴリズム
---

# std::iota

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <numeric>`
</div>

0 から n-1 までの添え字の表を作りたい、ID を 1 ずつ振りたい。連番を配列に入れるには、`for` で `v[i] = i` と書くことになります。`std::iota` は、範囲を「開始値、開始値+1、開始値+2、…」という連番で埋める関数です。名前は、ギリシャ文字のイオタに由来します。ヘッダーは `<algorithm>` ではなく `<numeric>` です。

!!! tip "ポイント"
    - ヘッダーは `<algorithm>` ではなく **`<numeric>`**。
    - C++23 には `std::ranges::iota` もあるが、使える環境はまだ少ない。普通は `std::iota(begin, end, 開始値)`。
    - 0 から並べた添字を作って、それを [`sort`](sort.md) で並べ替える（間接ソート）のが定番の使い方。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::iota {#iota}

```cpp
template <class ForwardIt, class T>
constexpr void iota(ForwardIt first, ForwardIt last, T value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 埋める範囲 |
| `value` | `T` | 最初の値。1 ずつ増える |

- `<numeric>` にあります。C++23 では `std::ranges::iota(r, value)` もあります

<div class="anim" data-label="std::iota(v.begin(), v.end(), 1)">
0 0 0 0 # v
+1 +2 +3 +4 # 1 から順に増やしながら入れる
</div>

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> order(4);
  std::iota(order.begin(), order.end(), 0);  // 0, 1, 2, 3（添字の配列を作る定番）
  std::println("{}", order);
}
```

```text title="実行結果"
[0, 1, 2, 3]
```


## フラグ・オプション

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `std::iota(first, last, 値)` | <span class="rank rank-sometimes">たまに</span> | 従来の書き方（C++11 から） |
| `std::ranges::iota(r, 値)` | <span class="rank rank-rare">知ってるだけ</span> | 範囲版（C++23） |
| [`std::views::iota`](views/iota.md) | <span class="rank rank-often">よく使う</span> | 配列を作らず、連番を「遅延して」並べる |

## ゲームでの使いどころ

間接ソート（添え字のソート）の準備に使います。大きな構造体を直接 `sort` するのではなく、0 から並べた添え字の配列を作り、それを構造体のメンバーで `sort` します。構造体を動かさずに済み、並べ替えの結果を別の配列として使えます。

ID を連番で振るときや、テスト用のデータを作るときにも使います。

配列が不要なら、`views::iota` が使えます。連番をループの範囲として使うだけなら、実体のある配列を作らずに済みます。

## よくあるミス

??? failure "<algorithm> だけを include して、iota が見つからない"
    `std::iota` は `<numeric>` にあります。`#include <numeric>` を足します。

??? failure "`<numeric>` を include し忘れる"
    `iota` は `<algorithm>` ではなく `<numeric>` にあります。include を忘れると、名前が見つかりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::iota`](views/iota.md) | 配列を作らずに連番を並べる |
| [`std::ranges::fill`](fill.md) | 同じ値で埋める |
| [`std::ranges::generate`](generate.md) | 関数を呼んだ結果で埋める |

## コンパイラ対応

`std::iota` は C++11 です。範囲版の `std::ranges::iota` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連番で埋める
    - [x] ヘッダーは `<numeric>`
    - [x] 添字の表を作って間接ソートに使う

## 関連ページ

- [cpprefjp: std::iota](https://cpprefjp.github.io/reference/numeric/iota.html)
- [cppreference: std::iota](https://en.cppreference.com/w/cpp/algorithm/iota)
