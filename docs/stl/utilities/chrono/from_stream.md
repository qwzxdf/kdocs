---
title: std::chrono::from_stream
summary: "ストリームから書式に従って chrono の型を読み込む。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::from_stream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`parse` マニピュレータの中身にあたる関数です。ストリームと書式と変数を渡して、読み込みます。

!!! tip "ポイント"
    - `from_stream(in, "%F", ymd)` の形で使う。
    - 戻り値はストリーム（成功したかは `if (in)` で見る）。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::from_stream {#from_stream}

```cpp
template <class CharT, class Traits>
basic_istream<CharT, Traits>& from_stream(basic_istream<CharT, Traits>& is, const CharT* fmt, year_month_day& ymd);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `is` | istream | 読み込み元 |
| `fmt` | 書式 | `%Y-%m-%d` など |
| `ymd` | chrono の型 | 結果を入れる変数 |

- 戻り値: `is` への参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("2024-03-05");
  std::chrono::year_month_day ymd;
  std::chrono::from_stream(in, "%F", ymd);
  std::println("{}", unsigned(ymd.day()));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 入力欄の日付文字列を読む | `from_stream(in, "%F", ymd)` |

## よくあるミス

??? failure "書式と文字列を合わせない"
    `%F` は `%Y-%m-%d` です。文字列が `2024/03/05` なら書式も `%Y/%m/%d` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`parse`](parse.md) | マニピュレータ版 |
| [`to_stream`](to_stream.md) | 書式で出力する |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームから読み込む
    - [x] 書式は strftime 風
    - [x] 失敗はストリームの状態で見る

## 関連ページ

- [cpprefjp: std::chrono::from_stream](https://cpprefjp.github.io/reference/chrono/from_stream.html)
- [cppreference: std::chrono::from_stream](https://en.cppreference.com/w/cpp/chrono/from_stream)
