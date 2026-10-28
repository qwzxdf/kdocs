---
title: std::ranges::dangling
summary: "「一時オブジェクトのイテレータは危険」と知らせるための印の型。"
order: 4
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::dangling

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::find(GetItems(), 3)` のように、関数が返した一時的な `vector` に対して検索すると、見つかったイテレーターは、式が終わった瞬間に破棄される `vector` を指します。そのまま使うと未定義動作です。`std::ranges::dangling` は、<strong>この危険な戻り値を、型として使えなくする</strong>ための印の型です。

!!! tip "ポイント"
    - 借用できない範囲に対して、アルゴリズムが返す型
    - イテレーターの代わりに `dangling` が返る
    - `dangling` の値は参照できない（使おうとするとコンパイルエラー）
    - 一時オブジェクトのイテレーターを使う事故を、ビルド時に防ぐ

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::dangling {#dangling}

<span class="ver ver-20">C++20</span>

```cpp
struct dangling {
  dangling() = default;
  constexpr dangling(auto&&...) noexcept {}
};
```

`std::ranges::find`、`std::ranges::max_element` など、イテレーターを返すアルゴリズムは、借用できない範囲（一時的な `vector` など）に呼ばれると、イテレーターの代わりに `dangling` を返します。`dangling` は、`*` で参照することも、`++` で進めることもできないので、使おうとするとコンパイルエラーになり、事故に気づけます。

直す方法は、一時オブジェクトをいったん変数に入れて（左辺値にして）から、アルゴリズムに渡すことです。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

std::vector<int> GetItems() { return {1, 2, 3}; }

int main() {
  auto bad = std::ranges::find(GetItems(), 2);        // 一時オブジェクトに対して
  std::println("dangling が返る: {}", std::is_same_v<decltype(bad), std::ranges::dangling>);

  auto items = GetItems();                             // いったん変数に入れる
  auto ok = std::ranges::find(items, 2);
  std::println("要素が見つかる: {}", *ok);
}
```

```text title="実行結果"
dangling が返る: true
要素が見つかる: 2
```

## ゲームでの使いどころ

一時オブジェクトに対する検索の誤りを、コンパイル時に見つけます。

```cpp
auto it = std::ranges::find(LoadItems(), id);   // ここで dangling が返り、*it は書けない
```

## よくあるミス

??? failure "`dangling` を参照しようとして、コンパイルエラーになる"
    一時オブジェクトを変数に入れてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`borrowed_range`](borrowed_range.md) | 借用できる範囲 |
| [`borrowed_iterator_t`](borrowed_iterator_t.md) | 借用できるときだけイテレーター |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ranges::dangling` は一時オブジェクトのイテレーターを使えなくする印の型
    - [x] 参照も進めることもできない
    - [x] 直すには、変数に入れてから渡す

## 関連ページ

- [cpprefjp: std::ranges::dangling](https://cpprefjp.github.io/reference/ranges/dangling.html)
- [cppreference: std::ranges::dangling](https://en.cppreference.com/w/cpp/ranges/dangling)
