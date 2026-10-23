---
title: std::intmax_t
summary: "その環境で最も大きい符号付き整数。"
order: 900
tags:
  - 数値
---

# std::intmax_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

環境で扱える最大の整数型を知りたい場面があります。ライブラリが、どんな整数でも受け取れる共通の入れ物を必要とするときです。

`std::intmax_t` は、<strong>その環境で最大の幅を持つ符号つき整数型</strong>です。

!!! tip "ポイント"
    - 最大の符号つき整数型。少なくとも 64 ビット
    - `std::uintmax_t` は符号なし版
    - `<ratio>` の分子・分母や、`<chrono>` の内部で使われる
    - 普通のゲームでは `long long` か `std::int64_t` で足りる

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::intmax_t {#intmax_t}

<span class="ver ver-11">C++11</span>

```cpp
using intmax_t = /* 最大幅の符号つき整数型 */;
```

`std::intmax_t` は、環境にある符号つき整数型の中で、最も大きいものの別名です。ほとんどの環境で 64 ビット（`long long`）です。

将来、128 ビット整数が標準の整数型として扱われると、`intmax_t` が 128 ビットになる可能性があります。そのため、ファイルや通信のデータ形式には使えません。形式には、`std::int64_t` のような固定幅を使います。

使われる場所は、型を問わない共通の窓口です。たとえば `std::ratio` は、分子と分母を `intmax_t` で持ちます。`std::chrono::duration` の内部で、時間の単位の比を扱うときにも登場します。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("少なくとも 64 ビット: {}", sizeof(std::intmax_t) * 8 >= 64);
}
```

```text title="実行結果"
少なくとも 64 ビット: true
```

## ゲームでの使いどころ

ゲームの通常のコードに登場することはまれです。ライブラリを作るときに、符号つきの整数を何でも受け取れる共通の型として使います。

```cpp
// どの整数型でも受け取る関数（intmax_t に広げて処理する）
void LogInteger(std::intmax_t value);
```

## よくあるミス

??? failure "ファイルの形式に使い、環境で大きさが変わる"
    `std::int64_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uintmax_t`](uintmax_t.md) | 符号なし版 |
| [`std::int64_t`](int64_t.md) | ちょうど 64 ビット |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大幅の符号つき整数型。少なくとも 64 ビット
    - [x] 大きさが将来変わりうるので、データ形式には使わない
    - [x] `std::ratio` などの内部で使われる

## 関連ページ

- [cpprefjp: std::intmax_t](https://cpprefjp.github.io/reference/cstdint/intmax_t.html)
- [cppreference: std::intmax_t](https://en.cppreference.com/w/cpp/types/integer)
