---
title: std::void_t
summary: "どんな型を渡しても `void` になる別名（検出イディオム用）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::void_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

「この型に `size()` というメンバがあるか」をコンパイル時に調べたいとき、`void_t<decltype(declval<T>().size())>` と書きます。式が正しければ `void` になり、間違っていれば SFINAE で候補から外れます。これで、メンバの有無を調べる型特性が書けます（検出イディオム）。C++20 では `requires` が簡単です。

!!! tip "ポイント"
    - どんな型も `void` に変える。
    - 式の正しさを、SFINAE で調べるのに使う。
    - C++20 では `requires` 式のほうが読みやすい。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::void_t {#void_t}

```cpp
template <class... Ts>
using void_t = void;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Ts...` | 型 | SFINAE で調べたい型（式の `decltype` など） |

- 戻り値: 常に `void`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <vector>

template <class T, class = void>
struct HasSize : std::false_type {};
template <class T>
struct HasSize<T, std::void_t<decltype(std::declval<T>().size())>> : std::true_type {};

int main() {
  std::println("{} {}", HasSize<std::vector<int>>::value, HasSize<int>::value);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | メンバや式が使えるかをコンパイル時に調べる |

## よくあるミス

??? failure "`void` を返すと思って使う"
    `void_t` は「式が正しいか」を調べる道具です。戻り値の型として使うものではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`enable_if`](enable_if.md) | 条件で型を存在させる |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] どんな型を渡しても `void` になる別名（検出イディオム用）
    - [x] どんな型も `void` に変える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::void_t](https://cpprefjp.github.io/reference/type_traits/void_t.html)
- [cppreference: std::void_t](https://en.cppreference.com/w/cpp/types/void_t)
