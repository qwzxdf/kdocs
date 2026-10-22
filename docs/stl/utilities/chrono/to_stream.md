---
title: std::chrono::to_stream
summary: "書式に従って chrono の型をストリームに書き出す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::to_stream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

日付を `2024/01/01` のような決まった形で書き出したいとき、`to_stream(os, 書式, 値)` が使えます。`std::format` の chrono 用の書式と同じ指定が使えます。

!!! tip "ポイント"
    - `to_stream(os, "%Y/%m/%d", ymd)` の形で使う。
    - `std::format("{:%Y/%m/%d}", ymd)` でも同じ。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::to_stream {#to_stream}

```cpp
template <class CharT, class Traits>
basic_ostream<CharT, Traits>& to_stream(basic_ostream<CharT, Traits>& os, const CharT* fmt, const year_month_day& ymd);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | ostream | 書き出し先 |
| `fmt` | 書式 | `%Y/%m/%d` など |
| `ymd` | chrono の型 | 書き出す値 |

- 戻り値: `os` への参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <sstream>

int main() {
  using namespace std::chrono;
  std::ostringstream oss;
  to_stream(oss, "%Y/%m/%d", 2024y / January / 1);
  std::println("{}", oss.str());
}
```

```text title="実行結果"
2024/01/01
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログに日付を決まった書式で書く | `to_stream(os, "%F", ymd)` |

## よくあるミス

??? failure "`std::format` で足りるのに使う"
    新しいコードでは `std::format` / `std::println` の `{:%F}` が簡単です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`parse`](parse.md) | 読み込み |
| [`format`](../format.md) | 文字列の書式化 |

## コンパイラ対応

C++20 の機能です。GCC 13 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] chrono の型を書式つきで書き出す
    - [x] format の書式と同じ
    - [x] 新しいコードは std::format

## 関連ページ

- [cpprefjp: std::chrono::to_stream](https://cpprefjp.github.io/reference/chrono/to_stream.html)
- [cppreference: std::chrono::to_stream](https://en.cppreference.com/w/cpp/chrono/to_stream)
