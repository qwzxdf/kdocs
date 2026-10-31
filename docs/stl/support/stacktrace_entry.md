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

クラッシュ時のログで読みたいのは、「どの関数の、どのファイルの、何行目か」です。`std::stacktrace` の 1 段ぶんが `std::stacktrace_entry` で、それらを取り出すための関数 `description()`・`source_file()`・`source_line()` を持っています。

!!! tip "ポイント"
    - `std::stacktrace` の要素の型。1 段ぶんの情報
    - `description()` で関数名、`source_file()` でファイル名、`source_line()` で行番号
    - デバッグ情報がないと、名前や行番号は空や 0 になる
    - 呼び出すたびに調べるので、遅い。ログに書くときだけ呼ぶ

!!! info "このページを読む前に"
    [`std::stacktrace`](stacktrace.md) を先に読んでください。

## 関数の詳しい説明

### description {#description}

<span class="ver ver-23">C++23</span>

```cpp
std::string description() const;
```

その段の関数の説明（関数名など）を返します。形式は実装に依存します。MSVC はデバッグ情報があると関数名を、なければアドレスなどを返します。調べるときに記号の解決をするので、時間がかかります。

### source_file {#source_file}

```cpp
std::string source_file() const;
```

その段のソース ファイルのパスを返します。デバッグ情報がなければ、空の文字列です。

### source_line {#source_line}

```cpp
std::uint_least32_t source_line() const;
```

その段の行番号を返します。デバッグ情報がなければ `0` です。

### native_handle {#native_handle}

```cpp
native_handle_type native_handle() const noexcept;
```

実装ごとの生の値（命令アドレスなど）を返します。標準ではない方法で、別の記号解決ツールに渡したいときに使います。

### operator bool {#operator-bool}

```cpp
explicit operator bool() const noexcept;
```

エントリーが有効かどうかを返します。既定で作ったエントリーは `false` です。

### 比較と書式指定

`==` と `<=>` で比べられます。`std::println("{}", entry)` のように、書式指定にも渡せ、`description`・ファイル名・行番号を並べた文字列になります。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <stacktrace>

int main() {
  std::stacktrace_entry empty;   // 既定で作ると、空のエントリー
  std::stacktrace trace = std::stacktrace::current();
  const std::stacktrace_entry& top = trace[0];

  std::println("空のエントリーは有効か: {}", static_cast<bool>(empty));
  std::println("先頭のエントリーは有効か: {}", static_cast<bool>(top));
  std::println("先頭は自分と等しい: {}", top == trace[0]);
  std::println("説明は空ではない: {}", !top.description().empty());
  std::println("書式指定で文字列にできる: {}", !std::format("{}", top).empty());
}
```

```text title="実行結果"
空のエントリーは有効か: false
先頭のエントリーは有効か: true
先頭は自分と等しい: true
説明は空ではない: true
書式指定で文字列にできる: true
```

## ゲームでの使いどころ

クラッシュ ログに、`関数名 (ファイル:行)` の形で履歴を書き出すときに使います。書式指定にそのまま渡せば、自分で整形する必要は、ほとんどありません。

## よくあるミス

??? failure "デバッグ情報なしでファイル名と行番号を期待する"
    空の文字列と `0` が返ります。

??? failure "description を毎フレーム呼ぶ"
    記号の解決で遅くなります。エラー ログだけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stacktrace`](stacktrace.md) | 履歴全体 |
| [`basic_stacktrace`](basic_stacktrace.md) | アロケーターを変えられる版 |
| [`source_location`](source_location.md) | コンパイル時の位置 |

## コンパイラ対応

C++23 です。MSVC は Visual Studio 2022 17.4 以降、GCC 12 以降が対応しています。

## 関連ページ

- [cpprefjp: std::stacktrace_entry](https://cpprefjp.github.io/reference/stacktrace/stacktrace_entry.html)
- [cppreference: std::stacktrace_entry](https://en.cppreference.com/w/cpp/utility/stacktrace_entry)
