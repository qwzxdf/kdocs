---
title: std::format_error
summary: "`std::format` の書式が不正なときの例外。"
order: 16
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::format_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

書式文字列に間違いがあると、`std::format` は、コンパイル時に検出できる場合はコンパイルエラーにします。ですが、実行時に決まる書式文字列（`std::vformat`）では、実行時にしか分かりません。`std::format_error` は、<strong>書式文字列が不正なときに投げられる例外</strong>です。

!!! tip "ポイント"
    - 不正な書式文字列を渡すと `vformat` が投げる
    - `std::format` にリテラルを渡すなら、コンパイル時に検出される
    - 書式をユーザー入力から読むときに備える
    - `std::runtime_error` の派生

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::format_error {#format_error}

<span class="ver ver-20">C++20</span>

```cpp
class format_error : public runtime_error {
 public:
  explicit format_error(const std::string& what_arg);
  explicit format_error(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | `what()` で返すメッセージ |

`std::vformat` など、実行時に書式文字列を受け取る関数で、`{}` の対応が合わない、型に合わない指定（文字列に `:d` など）がある、といった場合に投げられます。

`std::format` の書式文字列は、リテラルならコンパイル時に検査されるので、この例外は出ません。ユーザー入力や設定ファイルから書式を読む場合だけ、注意が必要です。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  const std::string text = "abc";
  try {
    // 文字列に整数用の :d を指定した、不正な書式
    std::string s = std::vformat("{:d}", std::make_format_args(text));
  } catch (const std::format_error&) {
    std::println("format_error を捕まえた");
  }
}
```

```text title="実行結果"
format_error を捕まえた
```

## ゲームでの使いどころ

設定ファイルのメッセージ書式のように、実行時に決まる書式を使うときに備えます。

```cpp
try {
  return std::vformat(user_format, std::make_format_args(name));
} catch (const std::format_error&) {
  return "(書式が不正)";
}
```

## よくあるミス

??? failure "リテラルの書式に、備えを入れて冗長になる"
    リテラルはコンパイル時に検査されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format`](../../utilities/format.md) | 書式つき文字列を作る |
| [`runtime_error`](runtime_error.md) | 基底クラス |

## コンパイラ対応

C++20 から使えます。`<format>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `format_error` は不正な書式文字列を表す例外
    - [x] リテラルならコンパイル時に検出される
    - [x] 実行時に決まる書式で備える

## 関連ページ

- [cpprefjp: std::format_error](https://cpprefjp.github.io/reference/format/format_error.html)
- [cppreference: std::format_error](https://en.cppreference.com/w/cpp/utility/format/format_error)
