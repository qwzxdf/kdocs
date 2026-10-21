---
title: std::convertible_to
summary: "ある型から別の型へ変換できることを要求するコンセプト。"
order: 4
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::convertible_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::convertible_to<From, To>` は、**`From` の値を `To` に変換できること**を要求するコンセプトです。`std::string_view` が欲しい関数に、`std::string` や `const char*` も渡せる、といった条件を表せます。

!!! tip "ポイント"
    - 暗黙の変換と、`static_cast` による明示の変換の、両方ができることが条件。
    - `template <std::convertible_to<std::string_view> S>` のように使う。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::convertible_to {#convertible_to}

```cpp
template <class T>
concept convertible_to = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  std::println("{} {}", std::convertible_to<int, double>, std::convertible_to<std::string, int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「string_view に変換できるもの」を受け取る関数 | `template <std::convertible_to<std::string_view> S>` |

## よくあるミス

??? failure "explicit な変換を含むと思う"
    `explicit` なコンストラクターによる変換は含まれません。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::is_convertible` | 変数テンプレート版 |
| [`same_as`](same_as.md) | 同じ型 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 変換できることを要求
    - [x] 暗黙変換が条件
    - [x] explicit は含まれない

## 関連ページ

- [cpprefjp: std::convertible_to](https://cpprefjp.github.io/reference/concepts/convertible_to.html)
- [cppreference: std::convertible_to](https://en.cppreference.com/w/cpp/concepts/convertible_to)
