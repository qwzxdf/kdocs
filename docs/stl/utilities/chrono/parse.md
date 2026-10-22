---
title: std::chrono::parse
summary: "文字列を書式に従って読み込み、chrono の型にするための入力マニピュレータ。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::parse

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

ユーザーが入力した日付文字列を、`year_month_day` のような型に変換したいことがあります。`std::chrono::parse(書式, 変数)` を `>>` に渡すと、書式（`%Y-%m-%d` など）に従って読み込みます。

!!! tip "ポイント"
    - `in >> std::chrono::parse("%F", ymd);` の形で使う。
    - 書式は `strftime` に似た `%Y` `%m` `%d` `%H` `%M` `%S` など。
    - 失敗すると `failbit` が立つ。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::parse {#parse}

```cpp
template <class CharT, class Traits, class Alloc, class Parsable>
/* 実装定義 */ parse(const basic_string<CharT, Traits, Alloc>& fmt, Parsable& tp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | 文字列 | 書式 |
| `tp` | chrono の型 | 結果を入れる変数 |

- 戻り値: ストリームに流せるマニピュレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("2024-03-05");
  std::chrono::year_month_day ymd;
  in >> std::chrono::parse("%F", ymd);
  std::println("{}", unsigned(ymd.day()));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの日付文字列を読む | `in >> std::chrono::parse("%F", ymd)` |

## よくあるミス

??? failure "失敗を確かめない"
    書式に合わない文字列では `failbit` が立ち、変数は変わりません。読み込み後に `if (in)` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`from_stream`](from_stream.md) | 同じ処理を関数で書く |
| [`to_stream`](to_stream.md) | 書式で出力する |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を chrono の型に読み込む
    - [x] 書式は strftime 風
    - [x] 失敗は failbit

## 関連ページ

- [cpprefjp: std::chrono::parse](https://cpprefjp.github.io/reference/chrono/parse.html)
- [cppreference: std::chrono::parse](https://en.cppreference.com/w/cpp/chrono/parse)
