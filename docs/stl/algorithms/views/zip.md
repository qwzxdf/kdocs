---
title: std::views::zip
summary: "複数の範囲を、同じ位置どうしの組にして同時に回す。"
order: 31
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::zip

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::zip` は、**複数の範囲を同じ位置どうしでペアにして、同時に回す**ビューです。「名前の配列と値段の配列を一緒に回す」「位置と速度の配列を同時に更新する」といった処理を、添字を使わずに書けます。

!!! tip "ポイント"
    - 最も短い範囲の長さまで回る。
    - 各要素は参照の組。`auto& [pos, vel]` で受ければ、書き換えもできる。
    - 3 つ以上の範囲も渡せる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::zip {#zip}

```cpp
std::views::zip(r1, r2, ...)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r1, r2, ...` | 範囲 | 同時に回す範囲（1 つ以上） |

- 戻り値: 要素の参照を組にして並べたビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> names = {"ポーション", "エーテル"};
  std::vector<int> prices = {50, 120};

  for (auto [name, price] : std::views::zip(names, prices)) {
    std::println("{}: {} G", name, price);
  }
}
```

```text title="実行結果"
ポーション: 50 G
エーテル: 120 G
```

### std::ranges::zip_view <span class="ver ver-23">C++23</span> {#zip_view data-toc-label="std::ranges::zip_view"}

```cpp
template <input_range... Vs>
class zip_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

複数の範囲をいっしょに歩き、タプルにして見せる view。`views::zip` が作ります。

ふつうは `views::zip` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::zip_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 位置と速度の配列を同時に更新する | `for (auto [p, v] : zip(positions, velocities)) p += v * dt;` |
| 名前の配列と値段の配列を一緒に表示する | `zip(names, prices)` |

## よくあるミス

??? failure "長さが違うと思う"
    長さが違うときは短いほうに合わせて止まります。余った要素は、黙って無視されます。

??? failure "値渡しで受けて、書き換えが反映されない"
    `for (auto [p, v] : ...)` はコピーです。書き換えたいなら `auto&` を付けます（`for (auto& [p, v] : ...)`）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::enumerate`](enumerate.md) | 番号と要素の組 |
| [`std::views::zip_transform`](zip_transform.md) | 組を作らず、関数を適用した結果を並べる |
| [`std::views::cartesian_product`](cartesian_product.md) | 全部の組み合わせ |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 17 / MSVC 19.37（VS 2022 17.7）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の範囲を同時に回す
    - [x] 短いほうに合わせて止まる
    - [x] 書き換えるなら `auto&`

## 関連ページ

- [cpprefjp: std::ranges::zip_view](https://cpprefjp.github.io/reference/ranges/zip_view.html)
- [cppreference: std::ranges::zip_view](https://en.cppreference.com/w/cpp/ranges/zip_view)
