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

ユーザーが入力した `"2026-03-09"` を、`year_month_day` に変換したい。`std::chrono::from_stream` は、書式の文字列（`%F` など）に従って、入力ストリームから日付や時刻を読み取り、chrono の型に入れます。読めなかったときは、ストリームに `failbit` が立ちます。

!!! tip "ポイント"
    - 第 2 引数が書式。`to_stream` と同じ指定が使える
    - 読めなかったとき、ストリームに `failbit` が立つ。変数は変わらない
    - 書式に合わない余計な文字があると、失敗する
    - 同じことを `is >> parse(fmt, x)` と書ける

!!! info "このページを読む前に"
    [`to_stream`](to_stream.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::from_stream {#from_stream}

<span class="ver ver-20">C++20</span>

```cpp
template <class CharT, class Traits>
std::basic_istream<CharT, Traits>&
from_stream(std::basic_istream<CharT, Traits>& is, const CharT* fmt,
            year_month_day& ymd);
// sys_time、duration、weekday、month など、型ごとのオーバーロード
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `is` | `std::basic_istream&` | 読み取り元 |
| `fmt` | `const CharT*` | 書式 |
| 第 3 引数 | chrono の型の参照 | 読んだ値を入れる変数 |

書式の変換指定に従って、ストリームの文字を読みます。書式の中の普通の文字（`-` や `/`）は、入力にあるはずの文字として照合されます。入力が書式と合わないと、`failbit` が立ち、第 3 引数は変更されません。

`%F`（`%Y-%m-%d`）で `"2026-03-09"` を読めば、年月日が入ります。存在しない日付（`2026-02-30`）も、書式としては合っているので読めますが、`ymd.ok()` が偽になります。読んだあと、`ok()` で確かめます。

戻り値は、`is` への参照です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <sstream>

int main() {
  using namespace std::chrono;

  // 正常に読める
  std::istringstream in("2026-03-09");
  year_month_day ymd;
  from_stream(in, "%F", ymd);
  std::println("{} 月 {} 日 有効={}", static_cast<unsigned>(ymd.month()),
               static_cast<unsigned>(ymd.day()), ymd.ok());

  // 書式に合わない入力は失敗する
  std::istringstream bad("hello");
  year_month_day ymd2;
  from_stream(bad, "%F", ymd2);
  std::println("失敗: {}", bad.fail());

  // 日付として存在しない値は、読めるが ok() が偽
  std::istringstream feb("2026-02-30");
  year_month_day ymd3;
  from_stream(feb, "%F", ymd3);
  std::println("2026-02-30 の ok(): {}", ymd3.ok());
}
```

```text title="実行結果"
3 月 9 日 有効=true
失敗: true
2026-02-30 の ok(): false
```

## ゲームでの使いどころ

設定ファイルや入力欄の日付を読むときに使います。読んだあとに `ok()` で確かめることが重要です。

## よくあるミス

??? failure "読んだあとに ok() を確かめない"
    `2026-02-30` のように、書式は合っているが実在しない日付が、素通りします。

??? failure "failbit を見ずに、変数を使う"
    失敗したときは変数が変わりません。初期値のまま使ってしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`parse`](parse.md) | `>>` で使う操作子 |
| [`to_stream`](to_stream.md) | 逆向き。ストリームに書く |
| [`year_month_day`](year_month_day.md) | 読み込み先の例 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: from_stream](https://cpprefjp.github.io/reference/chrono/from_stream.html)
- [cppreference: std::chrono::from_stream](https://en.cppreference.com/w/cpp/chrono/from_stream)
