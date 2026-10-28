---
title: std::in_range
summary: "整数の値が、ある整数型の範囲に収まるかを調べる。"
order: 4
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::in_range

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <utility>`
</div>

`int` の値を `std::uint8_t` に入れたい。範囲に収まるか先に確かめたいのですが、`value >= 0 && value <= 255` と手で書くと、型が変わるたびに書き直しが必要で、符号の混在で誤りやすいです。`std::in_range<R>(x)` は、<strong>値 `x` が型 `R` の範囲に収まるか</strong>を調べます。

!!! tip "ポイント"
    - `std::in_range<std::uint8_t>(200)` は `true`、`(300)` は `false`
    - 負の値は、符号なしの型では `false`
    - 整数型どうしの比較で、符号の混在による誤りがない
    - `<utility>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::in_range {#in_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class R, class T>
constexpr bool in_range(T t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 整数型 | 収まるか調べたい型（テンプレート引数） |
| `t` | 整数型 | 調べる値 |

`t` が `R` で表せる範囲（`numeric_limits<R>::min()` 〜 `max()`）に入っていれば `true` です。符号つきと符号なしの違いも、正しく扱います。たとえば `in_range<unsigned>(-1)` は `false` です。

整数型だけが対象です。`bool` や `char` 系は渡せません。

型の変換（`static_cast`）の前に情報が失われないかを確かめる用途です。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <utility>

int main() {
  std::println("200 は uint8_t に収まる : {}", std::in_range<std::uint8_t>(200));
  std::println("300 は uint8_t に収まる : {}", std::in_range<std::uint8_t>(300));
  std::println("-1 は uint8_t に収まる  : {}", std::in_range<std::uint8_t>(-1));
  std::println("-1 は int8_t に収まる   : {}", std::in_range<std::int8_t>(-1));
}
```

```text title="実行結果"
200 は uint8_t に収まる : true
300 は uint8_t に収まる : false
-1 は uint8_t に収まる  : false
-1 は int8_t に収まる   : true
```

## ゲームでの使いどころ

大きな型の値を小さな型に詰めるときの検査に使います。

```cpp
int health = ComputeHealth();
if (!std::in_range<std::uint8_t>(health)) { /* 0〜255 に収まらない */ }
save.health = static_cast<std::uint8_t>(health);
```

## よくあるミス

??? failure "範囲外の値を `static_cast` して、黙って折り返される"
    変換の前に `in_range` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cmp_less`](cmp_less.md) | 安全な比較 |
| [`saturate_cast`](../numeric/saturate_cast.md) | 範囲外を端で止める変換 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `in_range<R>(x)` は `x` が `R` の範囲に収まるか
    - [x] 符号の違いを正しく扱う
    - [x] `static_cast` の前の検査に使う

## 関連ページ

- [cpprefjp: std::in_range](https://cpprefjp.github.io/reference/utility/in_range.html)
- [cppreference: std::in_range](https://en.cppreference.com/w/cpp/utility/in_range)
