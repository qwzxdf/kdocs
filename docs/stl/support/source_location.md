---
title: std::source_location
summary: "今の場所（ファイル・行・関数）を取得する。"
order: 1
tags:
  - 型・言語サポート
---

# std::source_location

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <source_location>`
</div>

`std::source_location` は、**コードのこの場所のファイル名・行番号・関数名を取得する**クラスです。ログに「どこから出たか」を自動で付けるときに使います。引数の既定値として `std::source_location::current()` を書くと、**呼び出した側の場所**が入ります。

!!! tip "ポイント"
    - 関数の引数の既定値に `current()` を書くと、呼び出し側の位置が取れる。
    - `file_name()`、`line()`、`function_name()`、`column()` が使える。
    - `__FILE__` / `__LINE__` マクロの置き換え。

## 関数の詳しい説明

### std::source_location::current {#current}

```cpp
static consteval source_location current() noexcept;
```

- これを書いた場所の情報を返します。**関数のデフォルト引数に書くと、呼び出した側の場所**になります（ここが一番のポイント）

### file_name {#file_name}

```cpp
constexpr const char* file_name() const noexcept;
```

- ファイル名（パス付きのことがある）

### line {#line}

```cpp
constexpr std::uint_least32_t line() const noexcept;
```

- 行番号

### function_name {#function_name}

```cpp
constexpr const char* function_name() const noexcept;
```

- 関数名。どこまで詳しく出るかはコンパイラ次第です

### column {#column}

```cpp
constexpr std::uint_least32_t column() const noexcept;
```

- 列番号（その行の何文字目か）。実装によっては 0

## 実際に動かしてみる

```cpp
#include <print>
#include <source_location>
#include <string_view>

int main() {
  auto loc = std::source_location::current();
  std::println("{} {}", loc.line() > 0, std::string_view(loc.function_name()).contains("main"));
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログやアサートに、呼び出し位置を自動で付ける | `void Log(std::string_view msg, std::source_location loc = std::source_location::current());` |

## よくあるミス

??? failure "関数の中で current() を呼ぶ"
    呼び出し側ではなく、その関数の中の位置になります。引数の既定値に書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stacktrace`](stacktrace.md) | 呼び出し履歴全体 |
| `__FILE__` / `__LINE__` | 古い方法 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイル・行・関数を取得する
    - [x] 引数の既定値に `current()`
    - [x] 呼び出し側の位置が取れる

## 関連ページ

- [cpprefjp: std::source_location](https://cpprefjp.github.io/reference/source_location/source_location.html)
- [cppreference: std::source_location](https://en.cppreference.com/w/cpp/utility/source_location)
