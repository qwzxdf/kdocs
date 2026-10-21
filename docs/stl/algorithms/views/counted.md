---
title: std::views::counted
summary: "先頭の位置と個数から、範囲を作る。"
order: 19
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::counted

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::counted` は、**先頭の位置（イテレータ）と個数から、その分だけの範囲**を作るビューです。ポインターと個数で渡される古い API（C のバッファなど）を、範囲として扱うのに使います。

!!! tip "ポイント"
    - `counted(先頭, 個数)`。終わりの位置ではなく、**個数**を渡す。
    - 先頭がポインターなら `std::span` に近い使い方ができる。
    - 個数が実際の要素数を超えると未定義動作。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::counted {#counted}

```cpp
std::views::counted(first, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレータ | 範囲の先頭 |
| `n` | 整数 | 個数 |

- 戻り値: 先頭から n 個のビュー（ランダムアクセスできる先頭なら `span` や `subrange`）
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  // 2 番目から 3 個
  auto part = std::views::counted(v.begin() + 1, 3) | std::ranges::to<std::vector>();
  std::println("{}", part);
}
```

```text title="実行結果"
[2, 3, 4]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C 風の API が返す「ポインター + 個数」を範囲として扱う | `counted(ptr, count)` |
| バッファの途中から n 個を処理する | `counted(buf.begin() + offset, n)` |

## よくあるミス

??? failure "個数が足りない"
    `v.begin() + 3` から 5 個のように、範囲を超える個数を渡すと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::span`](../../containers/span.md) | ポインターと個数を 1 つにした型 |
| [`std::views::take`](take.md) | 先頭から n 個を取る |
| [`std::ranges::subrange`](subrange.md) | 2 つのイテレータから範囲を作る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭と個数から範囲を作る
    - [x] 終わりではなく個数
    - [x] 範囲外は未定義動作

## 関連ページ

- [cpprefjp: std::ranges::counted_view](https://cpprefjp.github.io/reference/ranges/counted_view.html)
- [cppreference: std::ranges::counted_view](https://en.cppreference.com/w/cpp/ranges/counted_view)
