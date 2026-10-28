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

ランキングの「1 位、2 位、3 位」を表示したい、リストの何番目かを使いたい。要素と番号の両方が必要な `for` を書くとき、`for (size_t i = 0; i < v.size(); ++i)` と添え字で回すか、別に番号の変数を作って `++` することになります。`std::views::enumerate` は、各要素に 0 から始まる番号を付けて、`(番号, 要素)` の組として見せてくれます。Python の `enumerate` と同じです。C++23 の機能です。

!!! tip "ポイント"
    - `for (auto [i, x] : v | std::views::enumerate)` と、構造化束縛で受ける。
    - 番号は 0 始まり。表示で 1 位から始めるなら `i + 1`。
    - 要素は参照なので、`auto& [i, x]` と受ければ書き換えられる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)と、[ラムダ式](../../../basics/lambda.md)が分かると読みやすいです。

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

ランキングの表示が代表的な使い方です。`for (auto [i, score] : scores | std::views::enumerate)` と書けば、`i` が 0 始まりの番号、`score` が値です。表示のときは `i + 1` で 1 位から始めます。

UI のメニュー項目の描画にも使います。選択中の項目の番号と、各項目の番号を比べて、選択中のものだけ色を変える、という処理が自然に書けます。

要素を書き換えたいときは、`auto&& [i, x]` と受けます。`vector` の添え字ループが範囲の外れ（`i < size()`）や型の不一致（`int` と `size_t`）で警告を出していた書き方を置き換えられます。

## よくあるミス

??? failure "番号を 1 始まりのつもりで使う"
    番号は 0 から始まります。画面の「1 位」を表示するなら `i + 1` です。そのまま表示すると、1 位が 0 位になります。

??? failure "C++23 未対応のコンパイラで使う"
    `views::enumerate` は C++23 の機能です。GCC 13 以降、MSVC 19.37 以降が必要です。古いコンパイラでは、`views::zip(views::iota(0), v)` で代用できます。

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
