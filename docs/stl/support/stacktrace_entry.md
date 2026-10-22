---
title: std::stacktrace_entry
summary: "スタックトレースの 1 行（関数 1 つぶん）を表す型。"
order: 900
tags:
  - 型・言語サポート
---

# std::stacktrace_entry

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stacktrace>`
</div>

クラッシュ時のログに「どの関数から呼ばれたか」を残したいとき、`std::stacktrace` の 1 行ぶんが `stacktrace_entry` です。関数の説明（`description()`）、ソースのファイル名（`source_file()`）、行番号（`source_line()`）を取り出せます。

!!! tip "ポイント"
    - `std::stacktrace` の要素の型。
    - `description()` / `source_file()` / `source_line()` で中身を取る。
    - デバッグ情報がないと、空の文字列や 0 が返る。

!!! info "このページを読む前に"
    [`std::stacktrace`](stacktrace.md) を先に読んでください。

## 関数の詳しい説明

### std::stacktrace_entry {#stacktrace_entry}

```cpp
class stacktrace_entry {
 public:
  std::string description() const;
  std::string source_file() const;
  uint_least32_t source_line() const;
  explicit operator bool() const noexcept;
};
```

- 戻り値: 関数の説明・ファイル名・行番号
- 計算量: 情報の取得は重め（シンボルの解決が入る）


## 実際に動かしてみる

```cpp
#include <print>
#include <stacktrace>

int main() {
  auto trace = std::stacktrace::current();
  for (const auto& entry : trace) {
    std::println("{}", entry.description());
  }
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| クラッシュログに呼び出し元を書く | `for (const auto& e : std::stacktrace::current()) log << e.description();` |

## よくあるミス

??? failure "リリースビルドで情報を期待する"
    デバッグ情報（`-g` など）がないと、関数名やファイル名が取れません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stacktrace`](stacktrace.md) | スタックトレース全体 |

## コンパイラ対応

C++23 の機能です。GCC では `-lstdc++exp`（または `-lstdc++_libbacktrace`）が必要です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スタックトレースの 1 行
    - [x] description / source_file / source_line
    - [x] デバッグ情報が必要

## 関連ページ

- [cpprefjp: std::stacktrace_entry](https://cpprefjp.github.io/reference/stacktrace/stacktrace_entry.html)
- [cppreference: std::stacktrace_entry](https://en.cppreference.com/w/cpp/utility/stacktrace_entry)
