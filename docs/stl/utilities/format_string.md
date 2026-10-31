---
title: std::format_string
summary: "書式文字列を、コンパイル時に検査する型（char 版の別名）。"
order: 900
tags:
  - ユーティリティ
---

# std::format_string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format("{}", x)` の書式文字列は、コンパイル時に検査されます。`"{:d}"` を文字列に使うなどの誤りは、実行前に、コンパイル エラーになります。この検査を受ける、書式文字列の引数の型が `std::format_string<Args...>` です。`std::format` や `std::println` の第 1 引数の型であり、自分で `format` を包む関数を書くときにも使います。

!!! tip "ポイント"
    - `std::format` の第 1 引数の型。書式の誤りをコンパイル時に検出する
    - 自作のログ関数などで包むときは、引数に `std::format_string<Args...>` を書く
    - 実行時に決まる書式なら、`std::vformat` と `make_format_args` を使う
    - 文字列リテラルから暗黙に作られる。変数の `std::string` は渡せない

!!! info "このページを読む前に"
    [`std::format`](format.md) と [`std::vformat`](vformat.md) を先に読んでください。

## 関数の詳しい説明

### std::format_string {#format_string}

<span class="ver ver-20">C++20</span>

```cpp
template <class... Args>
using format_string = std::basic_format_string<char, std::type_identity_t<Args>...>;
```

`format_string` のコンストラクターは `consteval` で、渡された書式文字列を、コンパイル時に解析します。引数の個数や型に合わない指定（`{}` が足りない、整数に `{:s}` など）は、コンパイル エラーです。

`std::type_identity_t<Args>` は、`Args` を、引数から推論させないための工夫です。`Args` は、後ろの値の引数から決まります。

`get()` で、元の書式文字列を `std::string_view` として取り出せます。

### 自作の関数で包む {#wrapper}

ログ関数のように、`format` を包む関数を作るときは、第 1 引数を `format_string<Args...>` にします。

```cpp
template <class... Args>
void Log(std::format_string<Args...> fmt, Args&&... args) {
  std::println(fmt, std::forward<Args>(args)...);
}
```

こう書くと、`Log("HP {}", hp)` の書式が、コンパイル時に検査されます。`const char*` や `std::string` を第 1 引数にすると、検査が働きません。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <utility>

// 書式をコンパイル時に検査する、ログ関数
template <class... Args>
void Log(std::format_string<Args...> fmt, Args&&... args) {
  std::println("[LOG] {}", std::format(fmt, std::forward<Args>(args)...));
}

int main() {
  Log("HP {} / MP {}", 30, 12);
  Log("name = {:>6}", "Hero");

  // 元の書式文字列を取り出す
  constexpr std::format_string<int> f{"{:>5}"};
  std::println("{}", f.get());

  // Log("HP {}", 30, 12);   // 引数が多すぎて、コンパイル エラー
}
```

```text title="実行結果"
[LOG] HP 30 / MP 12
[LOG] name =   Hero
{:>5}
```

## ゲームでの使いどころ

ゲーム独自のログ関数を作るとき、第 1 引数を `std::format_string<Args...>` にして、書式のミスをビルド時に見つけます。

## よくあるミス

??? failure "std::string を書式にして、コンパイルできない"
    `Log(fmt_string, x)` は、定数式でないのでエラーです。実行時の書式には `vformat` を使います。

??? failure "ログ関数の第 1 引数を const char* にする"
    書式のコンパイル時の検査が、効かなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wformat_string`](wformat_string.md) | `wchar_t` 版 |
| [`basic_format_string`](basic_format_string.md) | 元のテンプレート |
| [`std::vformat`](vformat.md) | 実行時に決まる書式を使う |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::format_string](https://cpprefjp.github.io/reference/format/format_string.html)
- [cppreference: std::format_string](https://en.cppreference.com/w/cpp/utility/format/format_string)
