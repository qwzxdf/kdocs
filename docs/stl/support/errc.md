---
title: std::errc
summary: "環境に依存しない、エラーの種類の名前（列挙型）。"
order: 32
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::errc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

システムのエラーを表す番号（`errno`）は、環境によって値が違います。`std::errc` は、<strong>移植性のあるエラーの種類</strong>を表す列挙型で、`no_such_file_or_directory`（ファイルがない）、`permission_denied`（権限がない）などがあります。

!!! tip "ポイント"
    - `std::errc::no_such_file_or_directory` などの名前でエラーを表す
    - `std::error_condition` と比べて、エラーの種類を判定する
    - `<cerrno>` の `ENOENT` などに対応する
    - 環境によらない名前で書ける

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::errc {#errc}

<span class="ver ver-11">C++11</span>

```cpp
enum class errc {
  no_such_file_or_directory = ENOENT,
  permission_denied = EACCES,
  invalid_argument = EINVAL,
  // …
};
```

`std::errc` の値は、`std::error_code` と比べる、エラーの種類の名前として使います。たとえば、`ec == std::errc::no_such_file_or_directory` で「ファイルがない」エラーかを判定できます。

`std::filesystem` の関数が返す `std::error_code` の判定に、よく使われます。値は `<cerrno>` の定数と同じ番号ですが、列挙型なので、名前で書けて、取り違えが防げます。

## 実際に動かしてみる

```cpp
#include <cerrno>
#include <print>
#include <system_error>

int main() {
  const std::error_code ec = std::make_error_code(std::errc::invalid_argument);
  std::println("invalid_argument と比べて一致: {}", ec == std::errc::invalid_argument);
  std::println("値は EINVAL と同じ        : {}", ec.value() == EINVAL);
}
```

```text title="実行結果"
invalid_argument と比べて一致: true
値は EINVAL と同じ        : true
```

## ゲームでの使いどころ

ファイル操作のエラーの原因で、処理を分けます。

```cpp
std::error_code ec;
std::filesystem::remove(path, ec);
if (ec == std::errc::no_such_file_or_directory) { /* もともとない */ }
```

## よくあるミス

??? failure "`errno` の数値を直接比べる"
    `std::errc` の名前で比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_code`](error_code.md) | エラーを表す値 |
| [`error_condition`](error_condition.md) | エラーの種類 |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::errc` は移植性のあるエラーの種類
    - [x] `error_code` と `==` で比べる
    - [x] `errno` と同じ番号

## 関連ページ

- [cpprefjp: std::errc](https://cpprefjp.github.io/reference/system_error/errc.html)
- [cppreference: std::errc](https://en.cppreference.com/w/cpp/error/errc)
