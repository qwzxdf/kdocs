---
title: std::views::repeat
summary: "同じ値を、繰り返し並べて見る。"
order: 16
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::repeat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::repeat` は、**同じ値を繰り返し並べて見る**ビューです。回数を指定すれば有限、省略すれば無限になります。区切り線（`====`）の作成や、同じ値で初期化した配列を作るときに使えます。

!!! tip "ポイント"
    - `repeat(値, 回数)` は有限、`repeat(値)` は無限。
    - 要素は 1 つだけ保存し、コピーを作らない。
    - C++23 の機能。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::repeat {#repeat}

```cpp
std::views::repeat(value)          // 無限に繰り返す
std::views::repeat(value, count)   // count 回
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | T | 繰り返す値 |
| `count` | 整数 | 繰り返す回数。省略すると無限 |

- 戻り値: 同じ値が並ぶビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  auto a = std::views::repeat(7, 3) | std::ranges::to<std::vector>();
  std::println("{}", a);

  // 区切り線を作る
  auto line = std::views::repeat('=') | std::views::take(5) | std::ranges::to<std::string>();
  std::println("{}", line);
}
```

```text title="実行結果"
[7, 7, 7]
=====
```

### std::ranges::repeat_view <span class="ver ver-23">C++23</span> {#repeat_view data-toc-label="std::ranges::repeat_view"}

```cpp
template <move_constructible W, semiregular Bound = unreachable_sentinel_t>
class repeat_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

同じ値を繰り返す view。`views::repeat(x, n)` が作ります。

ふつうは `views::repeat` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::repeat_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メニューの区切り線を作る | `repeat('-') | take(20)` |
| 同じ値の配列を作る | `repeat(0, n) | to<vector>` |

## よくあるミス

??? failure "無限の repeat をそのまま回す"
    個数を決めずに範囲 for で回すと、止まりません。`take` で区切るか、回数を指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::iota`](iota.md) | 連番を並べる |
| [`std::views::single`](single.md) | 1 つの値だけを範囲にする |
| `std::vector<T>(n, value)` | 同じ値で初期化した `vector` |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ値を繰り返す
    - [x] 回数なしなら無限
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::repeat_view](https://cpprefjp.github.io/reference/ranges/repeat_view.html)
- [cppreference: std::ranges::repeat_view](https://en.cppreference.com/w/cpp/ranges/repeat_view)
