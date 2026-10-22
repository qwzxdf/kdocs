---
title: views::concat
summary: "複数の範囲を、1 本につなげて見せる view。"
order: 900
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# views::concat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <ranges>`
</div>

2 つの `vector` の中身を順に処理したいとき、結合した `vector` を作ると、コピーが必要になります。`views::concat(a, b, ...)` は、コピーせずに、複数の範囲を 1 本の範囲のように見せます。`join` と違い、範囲の範囲ではなく、複数の範囲を直接渡します。

!!! tip "ポイント"
    - 要素の型はそろっている必要がある（共通の参照型が必要）。
    - コピーはしない（元の範囲を借りるだけ）。
    - `join` は範囲の範囲用、`concat` は範囲を直接並べる用。

!!! info "このページを読む前に"
    [`views`](../views.md) を先に読んでください。

## 関数の詳しい説明

### views::concat {#concat}

```cpp
template <input_range... Rs>
constexpr auto views::concat(Rs&&... rs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `rs...` | 範囲 | つなぐ範囲（2 つ以上） |

- 戻り値: `concat_view`
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

### std::ranges::concat_view {#concat_view}

```cpp
template <input_range... Views>
class concat_view;
```

- 戻り値: `views::concat` が作る view の型

ふつうは `views::concat` で書くので、型の名前を自分で書くことは少なく、`auto` で受けます。


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> a = {1, 2};
  std::vector<int> b = {3, 4};
  int sum = 0;
  for (int x : std::views::concat(a, b)) {
    sum += x;
  }
  std::println("{}", sum);
}
```

```text title="実行結果"
10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの配列を 1 つのループで処理 | `for (int x : std::views::concat(a, b)) { ... }` |

## よくあるミス

??? failure "元の範囲が先に消える"
    view は借りるだけなので、元の範囲が先に消えると壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::join`](join.md) | 範囲の範囲をつなぐ |
| [`views::zip`](zip.md) | 並べて歩く |

## コンパイラ対応

C++26 の機能です。新しい標準ライブラリで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の範囲を 1 本に見せる
    - [x] コピーしない
    - [x] C++26

## 関連ページ

- [cpprefjp: views::concat](https://cpprefjp.github.io/reference/ranges/concat_view.html)
- [cppreference: views::concat](https://en.cppreference.com/w/cpp/ranges/concat_view)
