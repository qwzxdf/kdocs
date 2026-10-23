---
title: std::integral
summary: "整数型であることを要求するコンセプト。"
order: 2
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::integral

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`Half(int)` と書いた関数に `float` を渡すと、小数部が切り捨てられて、気づかないうちに結果が変わります。テンプレートにして `template <class T> T Half(T v)` と書くと、今度は `std::string` を渡してもコンパイルが通りかけて、中で長いエラーを出します。`std::integral<T>` は、T が整数型（`int`、`char`、`bool` など）であることを要求するコンセプトです。`template <std::integral T>` と書けば、整数以外は、呼び出しの時点で分かりやすいエラーになります。

!!! tip "ポイント"
    - `template <std::integral T> T Half(T v)` のように書く。
    - 符号つきだけは `std::signed_integral`、符号なしだけは `std::unsigned_integral`。
    - `bool` も整数型。

!!! info "このページを読む前に"
    テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。

## 関数の詳しい説明

### std::integral {#integral}

```cpp
template <class T>
concept integral = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

template <std::integral T>
T Half(T v) {
  return v / 2;
}

int main() {
  std::println("{}", Half(7));       // 整数だけ受け取る
  // Half(7.0);                      // コンパイルエラー: 小数は渡せない
}
```

```text title="実行結果"
3
```

## しくみ

`std::integral<T>` は、`std::is_integral_v<T>` が `true` の型だけを通すコンセプトです。コンセプトはテンプレートの引数に直接書けるので、`std::enable_if` を使うより、ずっと読みやすくなります。

`template <std::integral T>` の代わりに、`void F(std::integral auto v)` と書く省略形もあります。型の名前を後で使わないなら、こちらが短く済みます。

符号付きだけを許すなら `std::signed_integral`、符号なしだけなら `std::unsigned_integral` です。浮動小数点を許すなら `std::floating_point`、数値全般なら `integral` と `floating_point` を `||` でつなぎます。

## ゲームでの使いどころ

整数のIDやフラグだけを受け取るテンプレート関数に使います。ビット演算のヘルパー（`SetBit`、`HasBit`）は、整数以外を渡されると意味がないので、`std::integral` で制約します。

数学ヘルパーでは、整数と小数で実装を分ける場面があります。`template <std::integral T> T Half(T v) { return v / 2; }` と `template <std::floating_point T> T Half(T v) { return v * 0.5; }` のように、コンセプトでオーバーロードを分けられます。

ゲームエンジンのシリアライズ関数で、整数型をバイナリに書き出す版と、小数を書き出す版を分けるときにも使います。

## よくあるミス

??? failure "`bool` や `char` も通ってしまう"
    `bool` と `char` も整数型です。`Half(true)` が通ってしまいます。「数としての整数」だけにしたいなら、`requires (!std::same_as<T, bool>)` を足します。

??? failure "`enum` を通そうとして失敗する"
    `enum` と `enum class` は整数型ではないので、`std::integral` を満たしません。列挙型を受けたいなら、`std::is_enum_v` で別のコンセプトを作ります。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。C++17 では、`std::enable_if_t<std::is_integral_v<T>, int> = 0` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::is_integral`](../type_traits/is_integral.md) | 型特性版。`bool` の値として使え、`if constexpr` に向く |
| `std::floating_point` | 小数型を要求するコンセプト |
| [`std::same_as`](same_as.md) | 特定の型と同じであることを要求する |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数だけを受け取るテンプレートは `template <std::integral T>`。
    - [x] `bool` と `char` も整数型。
    - [x] C++20 の機能。C++17 は `enable_if` で書く。

## 関連ページ

- [cpprefjp: std::integral](https://cpprefjp.github.io/reference/concepts/integral.html)
- [cppreference: std::integral](https://en.cppreference.com/w/cpp/concepts/integral)
