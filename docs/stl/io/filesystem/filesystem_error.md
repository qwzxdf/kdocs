---
title: std::filesystem::filesystem_error
summary: "filesystem の関数が投げる例外。"
order: 27
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::filesystem_error

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::filesystem_error` は、**filesystem の関数が失敗したときに投げる例外**です。失敗した原因（`code()`）と、対象のパス（`path1()`、`path2()`）を持っています。

!!! tip "ポイント"
    - `catch (const fs::filesystem_error& e)` で受け、`e.what()` を表示する。
    - ゲームで例外を使わない方針なら、`error_code` を渡す版を使う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### filesystem_error {#filesystem_error}

```cpp
class filesystem_error : public std::system_error;
```

- 例外を投げる版の関数が失敗したときに投げられます。`path1()` / `path2()` で関係したパス、`what()` で説明が取れます

```cpp
#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  try {
    std::println("{}", fs::file_size("no_such_file.dat"));
  } catch (const fs::filesystem_error& e) {
    std::println("失敗: {}", e.path1().string());
  }

  std::error_code ec;  // 例外を使わない版
  auto size = fs::file_size("no_such_file.dat", ec);
  std::println("エラーあり？ {} / size は -1 相当？ {}", static_cast<bool>(ec),
               size == static_cast<std::uintmax_t>(-1));
}
```

```text title="実行結果"
失敗: no_such_file.dat
エラーあり？ true / size は -1 相当？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルが開けなかった原因をログに出す | `e.code().message()` |

## よくあるミス

??? failure "どの関数でも例外が出ると思う"
    `error_code` を渡す版は、例外を投げません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::runtime_error`](../../support/exceptions.md) | 親の例外クラス |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] filesystem の例外
    - [x] `code()` と `path1()` を持つ
    - [x] error_code 版なら例外なし

## 関連ページ

- [cpprefjp: std::filesystem::filesystem_error](https://cpprefjp.github.io/reference/filesystem/filesystem_error.html)
- [cppreference: std::filesystem::filesystem_error](https://en.cppreference.com/w/cpp/filesystem/filesystem_error)
