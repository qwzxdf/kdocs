---
title: std::views::common
summary: "先頭と終わりの型が違う範囲を、同じ型の範囲に整える。"
order: 20
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::common

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::common` は、**先頭（begin）と終わり（end）の型が違う範囲を、同じ型にそろえる**ビューです。`take_while` などのビューは、終わりが特別な型（番兵）になることがあり、古い（イテレータのペアしか受け取らない）関数に渡せません。`common` で型をそろえると渡せるようになります。

!!! tip "ポイント"
    - C++20 より前のアルゴリズムや、`std::vector(first, last)` のコンストラクタは、begin と end が同じ型でないと受け取れない。
    - `common` を挟めば、新旧のコードをつなげられる。
    - すでに同じ型なら、何もしない（コピーも作らない）。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::common {#common}

```cpp
r | std::views::common
std::views::common(r)
```

- 戻り値: begin と end が同じ型のビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 10};

  // take_while の終わりは特別な型。common で begin/end を同じ型にそろえる
  auto small = v | std::views::take_while([](int x) { return x < 5; }) | std::views::common;
  std::vector<int> out(small.begin(), small.end());  // イテレータ 2 つを取るコンストラクタ
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いライブラリの関数に、ビューを渡す | `view | common` の `begin()` と `end()` を渡す |

## よくあるミス

??? failure "common を付けなくてもコンパイルが通る場合がある"
    ほとんどの現代的な関数は、型の違う begin / end も受け取れます。コンパイルエラーが出たときにだけ足します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::to`](../ranges_to.md) | ビューからコンテナを作る。たいていはこちらで足りる |
| [`std::views::all`](all.md) | 範囲をビューにする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] begin と end の型をそろえる
    - [x] 古い関数に渡すときに使う
    - [x] 普通は `ranges::to` で足りる

## 関連ページ

- [cpprefjp: std::ranges::common_view](https://cpprefjp.github.io/reference/ranges/common_view.html)
- [cppreference: std::ranges::common_view](https://en.cppreference.com/w/cpp/ranges/common_view)
