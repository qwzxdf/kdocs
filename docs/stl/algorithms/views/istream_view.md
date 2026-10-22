---
title: std::views::istream_view
summary: "入力ストリームから、値を 1 つずつ読み出す範囲を作る。"
order: 40
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::istream_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::istream<T>` は、**入力ストリーム（`cin`、ファイル、`istringstream`）から、`T` 型の値を 1 つずつ読み出す範囲**を作るビューです。「空白区切りの数字をすべて読む」を、範囲 for で書けます。

!!! tip "ポイント"
    - `views::istream<int>(stream)` と、読みたい型を指定する。
    - 読み込みに失敗した（型が違う・終わり）時点で止まる。
    - 1 回しか読めない範囲（入力範囲）。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::istream_view {#istream_view}

```cpp
std::views::istream<T>(stream)
std::ranges::istream_view<T>(stream)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `basic_istream` | 読み出し元のストリーム |

- 戻り値: 値を 1 つずつ読み出すビュー
- 計算量: 値 1 つにつき、`>>` 1 回

```cpp
#include <print>
#include <ranges>
#include <sstream>

int main() {
  std::istringstream in("10 20 30");

  int sum = 0;
  for (int x : std::views::istream<int>(in)) {
    sum += x;
  }
  std::println("合計 {}", sum);
}
```

```text title="実行結果"
合計 60
```

### std::ranges::basic_istream_view <span class="ver ver-20">C++20</span> {#basic_istream_view data-toc-label="std::ranges::basic_istream_view"}

```cpp
template <movable Val, class CharT, class Traits>
class basic_istream_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

入力ストリームから `>>` で読み取り続ける view。`views::istream<T>(in)` が作ります。

ふつうは `views::istream_view` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::basic_istream_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの数値列を読み込む | `views::istream<float>(file)` |
| 標準入力の数値を全部読む | `views::istream<int>(std::cin)` |

## よくあるミス

??? failure "数値でない文字で、途中で止まる"
    `10 abc 30` のように読めない所があると、そこで終わります。エラーとの区別はできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cin`](../../io/cin.md) | 標準入力（1 つずつ `>>` で読む） |
| [`std::istream_iterator`](../../support/iterator/istream_iterator.md) | 従来のイテレータ版 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの値を範囲として読む
    - [x] 読めなくなったら終わり
    - [x] 1 回しか読めない

## 関連ページ

- [cpprefjp: std::ranges::basic_istream_view](https://cpprefjp.github.io/reference/ranges/basic_istream_view.html)
- [cppreference: std::ranges::basic_istream_view](https://en.cppreference.com/w/cpp/ranges/basic_istream_view)
