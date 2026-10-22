---
title: std::views::enumerate
summary: "各要素に 0 から始まる番号を付けた組 (番号, 要素) として見る。"
order: 30
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::enumerate

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::enumerate` は、**各要素に 0 から始まる番号を付けて、`(番号, 要素)` の組として見る**ビューです。ランキングの「1 位」「2 位」の表示や、UI のリストの何番目かを使う処理に便利です。Python の `enumerate` と同じです。

!!! tip "ポイント"
    - `for (auto [i, x] : v | std::views::enumerate)` と、構造化束縛で受ける。
    - 番号は 0 始まり。表示で 1 位から始めるなら `i + 1`。
    - 要素は参照なので、`auto& [i, x]` と受ければ書き換えられる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::enumerate {#enumerate}

```cpp
r | std::views::enumerate
std::views::enumerate(r)
```

- 戻り値: (番号, 要素の参照) のビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> ranking = {"Alice", "Bob", "Carol"};

  for (auto [i, name] : ranking | std::views::enumerate) {
    std::println("{}位 {}", i + 1, name);
  }
}
```

```text title="実行結果"
1位 Alice
2位 Bob
3位 Carol
```

### std::ranges::enumerate_view <span class="ver ver-23">C++23</span> {#enumerate_view data-toc-label="std::ranges::enumerate_view"}

```cpp
template <view V>
class enumerate_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

要素に 0 から始まる番号をつけて見せる view。`views::enumerate` が作ります。

ふつうは `views::enumerate` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::enumerate_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ランキングの順位を表示する | `ranking | enumerate` |
| UI のメニューで、何番目の項目かを使う | `items | enumerate` |

## よくあるミス

??? failure "古い環境で使えない"
    C++23 の機能で、GCC 13 / MSVC 19.37 以降です。使えないときは `for (std::size_t i = 0; ...)` か、[`zip`](zip.md) と [`iota`](iota.md) を組み合わせます。

??? failure "番号の型が int だと思う"
    番号は `ptrdiff_t` などの符号つきの型です。`size_t` と比べるときは符号に注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::zip`](zip.md) | 複数の範囲を同時に回す |
| [`std::views::iota`](iota.md) | 連番を作る |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.37（VS 2022 17.7）以降で使えます。Clang (libc++) はまだ未対応のバージョンがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `(番号, 要素)` の組で回す
    - [x] 番号は 0 始まり
    - [x] Python の `enumerate`

## 関連ページ

- [cpprefjp: std::ranges::enumerate_view](https://cpprefjp.github.io/reference/ranges/enumerate_view.html)
- [cppreference: std::ranges::enumerate_view](https://en.cppreference.com/w/cpp/ranges/enumerate_view)
