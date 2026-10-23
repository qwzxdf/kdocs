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

`std::errc` は、**環境に依存しないエラーの種類の名前**をまとめた列挙型です。`no_such_file_or_directory`（ファイルが無い）、`permission_denied`（権限がない）、`invalid_argument`（引数が不正）、`not_enough_memory`（メモリ不足）などがあります。`error_code` と比べて、エラーの原因で分岐します。

!!! tip "ポイント"
    - `ec == std::errc::no_such_file_or_directory` のように比べる。
    - `std::make_error_code(std::errc::xxx)` でエラーコードを作れる。
    - POSIX のエラー番号（ENOENT など）に対応している。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::errc {#errc}

```cpp
enum class errc {
  no_such_file_or_directory, permission_denied, invalid_argument, not_enough_memory, /* ... */
};
```

- 戻り値: （列挙型）
- 計算量: O(1)

```cpp
#include <print>
#include <system_error>

int main() {
  std::error_code ec = std::make_error_code(std::errc::invalid_argument);
  std::println("{}", ec == std::errc::invalid_argument);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルが無いときだけデフォルト値にする | `if (ec == std::errc::no_such_file_or_directory)` |

## よくあるミス

??? failure "OS のエラー番号と直接比べる"
    Windows では番号が違います。`errc` と比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_code`](error_code.md) | 値と分類 |
| [`error_condition`](error_condition.md) | 種類を表す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エラーの種類の名前
    - [x] 環境に依存しない
    - [x] `error_code` と比べる

## 関連ページ

- [cpprefjp: std::errc](https://cpprefjp.github.io/reference/system_error/errc.html)
- [cppreference: std::errc](https://en.cppreference.com/w/cpp/error/errc)
