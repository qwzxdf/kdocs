---
title: <version>（機能テストマクロ）
summary: "「この標準ライブラリの機能が使えるか」を、`#if` で調べるためのマクロ。"
order: 40
tags:
  - 型・言語サポート
---

# <version>（機能テストマクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <version>`
</div>

コンパイラが、ある機能に対応しているかを調べたい。`__cplusplus` の値は規格の版を示しますが、個々の機能（`<ranges>` や `std::format`）の対応までは分かりません。`<version>` は、<strong>機能ごとのテスト用マクロ（`__cpp_lib_...`）を定義するだけのヘッダー</strong>です。

!!! tip "ポイント"
    - `<version>` を取り込むと、`__cpp_lib_ranges` などのマクロが使える
    - マクロの値は、その機能が導入された年月（例: 202110L）
    - `#ifdef` でマクロの有無を調べて、使える機能を分岐する
    - 標準ヘッダーを取り込むのでも、同じマクロが定義される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### `<version>` {#version}

<span class="ver ver-20">C++20</span>

```cpp
#include <version>
// 例: __cpp_lib_ranges, __cpp_lib_format, __cpp_lib_expected
```

機能ごとにマクロが決まっていて、値は、その機能が標準に入った年月（`YYYYMM`）の整数です。複数の版がある機能は、新しい版ほど値が大きくなります。

たとえば `#if defined(__cpp_lib_format)` で、`std::format` が使えるかを調べます。対応していない環境では、`fmt` ライブラリなどの代替に切り替える、といった書き方ができます。

`<version>` は C++20 で追加されました。それ以前の環境では、個別の標準ヘッダーを取り込んでから、マクロを調べます。

## 実際に動かしてみる

```cpp
#include <print>
#include <version>

int main() {
#ifdef __cpp_lib_ranges
  std::println("ranges が使える");
#else
  std::println("ranges は使えない");
#endif
}
```

```text title="実行結果"
ranges が使える
```

## ゲームでの使いどころ

新しい標準ライブラリの機能に対応しているコンパイラ用と、対応していないコンパイラ用で、コードを切り替えます。

```cpp
#if defined(__cpp_lib_expected)
  std::expected<int, Error> result = Load();
#else
  // 代替の実装
#endif
```

## よくあるミス

??? failure "`__cplusplus` だけで機能の有無を判断する"
    個別の機能は `__cpp_lib_` マクロで確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](type_traits.md) | 型の性質を調べる |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 7 以降、Visual Studio 2019 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<version>` は機能テスト用のマクロを定義する
    - [x] 値は導入された年月
    - [x] `#ifdef` で機能の有無を分岐する

## 関連ページ

- [cpprefjp: <version>（機能テストマクロ）](https://cpprefjp.github.io/reference/version.html)
- [cppreference: <version>（機能テストマクロ）](https://en.cppreference.com/w/cpp/utility/feature_test)
