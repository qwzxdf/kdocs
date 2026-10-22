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

位置の配列と速度の配列を、同時に更新したい。名前の配列と値段の配列を、並べて表示したい。複数の配列を同じ位置どうしで扱うとき、`for (size_t i = 0; ...)` で添え字をそろえる書き方が、すぐ思い浮かびます。添え字の書き間違いや、配列の長さが違うときのバグが起きがちです。`std::views::zip` は、複数の範囲を同じ位置でペアにして、同時に回すビューです。C++23 の機能です。

!!! tip "ポイント"
    - 最も短い範囲の長さまで回る。
    - 各要素は参照の組。`auto& [pos, vel]` で受ければ、書き換えもできる。
    - 3 つ以上の範囲も渡せる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)と、[ラムダ式](../../../basics/lambda.md)が分かると読みやすいです。

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

Structure of Arrays（要素ごとに配列を分ける設計）のデータを更新するときに使います。位置の `vector` と速度の `vector` を、`for (auto&& [pos, vel] : std::views::zip(positions, velocities))` と書けば、同じ位置どうしを組にして回せます。`pos += vel * dt;` と、添え字なしで書けます。

名前と値段のように、別々の配列を並べて表示する場面にも使います。3 つ以上の範囲も渡せます。

範囲の長さが違うときは、いちばん短いものに合わせて終わります。長さが違うことを異常として扱いたいなら、事前に長さを確かめます。

## よくあるミス

??? failure "長さが違う配列を渡して、末尾を取りこぼす"
    最も短い範囲の長さまでしか回りません。長いほうの余りは、黙って無視されます。長さが同じはずの配列は、`assert` で確かめておくと安全です。

??? failure "`auto [a, b]` で受けて、書き換えが元に反映されない"
    `auto [a, b]` で受けると、要素のコピーになります。元の配列を書き換えたいなら、`auto&& [a, b]` で受けます。

??? failure "C++23 未対応のコンパイラで使う"
    `views::zip` は C++23 の機能です。GCC 13 以降、MSVC 19.37 以降が必要です。

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
