---
title: std::time_get
summary: "日時を、書式に従って文字列から読み込むファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::time_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`"12:30:45"` や `"2024-01-01"` のような文字列から、時・分・秒や年月日を取り出して `tm` に入れる部品が `std::time_get` です。`std::get_time` という操作子の裏で動いています。`time_put` の逆の働きにあたります。

!!! tip "ポイント"
    - 時刻だけ、日付だけ、曜日だけ、のように、読む対象ごとに関数が分かれている
    - 書式を指定して読むなら、`get`（C++11 から）か、`std::get_time` の操作子
    - 読めなかったときは、`err` に `failbit`。範囲の終わりに達すれば `eofbit`
    - 読み込んだ結果は、`tm` の該当するフィールドだけ書き換わる

!!! info "このページを読む前に"
    [`std::time_put`](time_put.md) と [`std::get_time`](../get_time.md) を先に読んでください。

## 関数の詳しい説明

### std::time_get {#time_get}

```cpp
template <class CharT, class InIt = std::istreambuf_iterator<CharT>>
class time_get {
 public:
  InIt get_time(InIt in, InIt end, std::ios_base& str,
                std::ios_base::iostate& err, std::tm* t) const;
  InIt get_date(InIt in, InIt end, std::ios_base& str,
                std::ios_base::iostate& err, std::tm* t) const;
  InIt get_weekday(InIt in, InIt end, std::ios_base& str,
                   std::ios_base::iostate& err, std::tm* t) const;
  InIt get_monthname(InIt in, InIt end, std::ios_base& str,
                     std::ios_base::iostate& err, std::tm* t) const;
  InIt get_year(InIt in, InIt end, std::ios_base& str,
                std::ios_base::iostate& err, std::tm* t) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in`, `end` | `InIt` | 読み込み元の範囲 |
| `str` | `std::ios_base&` | ロケールの取得元のストリーム |
| `err` | `std::ios_base::iostate&` | エラーの状態を受け取る |
| `t` | `std::tm*` | 結果を入れる変数 |

### get_time {#get_time}

`"%H:%M:%S"` の形の時刻を読みます。`tm` の `tm_hour`、`tm_min`、`tm_sec` が書き換わります。

### get_date {#get_date}

ロケールが決めた日付の形（`"C"` ロケールでは `"%m/%d/%y"`）を読みます。書式がロケールで変わるので、決まった形の日付は、書式を指定できる `std::get_time` の操作子で読むほうが確実です。

### get_weekday と get_monthname {#names}

曜日の名前（`Mon`、`Monday`）や、月の名前（`Jan`、`January`）を読みます。名前は、ロケールの言語に従うので、`"C"` ロケールでは英語です。

### get_year {#get_year}

年を読みます。2 桁の年（`24`）は、1969〜2068 の範囲に解釈する環境が多く、4 桁で書かれていれば、そのまま扱います。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("12:30:45");
  std::istreambuf_iterator<char> b(in);
  std::istreambuf_iterator<char> e;
  std::tm t{};
  std::ios_base::iostate err = std::ios_base::goodbit;

  std::use_facet<std::time_get<char>>(std::locale::classic())
      .get_time(b, e, in, err, &t);

  std::println("{} 時 {} 分 {} 秒", t.tm_hour, t.tm_min, t.tm_sec);
  std::println("失敗: {}", (err & std::ios_base::failbit) != 0);
}
```

```text title="実行結果"
12 時 30 分 45 秒
失敗: false
```

`tm` の時・分・秒だけが書き換わります。年月日は、初期化した 0 のままです。

## ゲームでの使いどころ

テキストのログやセーブ データから、時刻を読み戻すときに使えます。ただし、書式を自由に指定できる `std::get_time` の操作子や、`std::chrono::from_stream`（C++20）のほうが、扱いやすいです。

## よくあるミス

??? failure "get_date の書式が環境で変わる"
    `"C"` ロケールでは月/日/年の順で、日本語のロケールでは年/月/日の順になることがあります。決まった形の日付は、書式を指定して読みます。

??? failure "tm を初期化せずに渡す"
    読まなかったフィールドは、ゴミの値のままになります。`std::tm t{};` で初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_put`](time_put.md) | 逆方向。日時を文字にする |
| [`std::get_time`](../get_time.md) | ストリームから読む操作子。普段はこちら |
| `std::chrono::from_stream` | C++20 の日時の読み込み |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `time_get` は、文字列から時刻・日付・曜日・月・年を読む部品
    - [x] 読んだフィールドだけ `tm` に入る。`tm` は 0 で初期化しておく
    - [x] 書式を指定するなら `std::get_time` の操作子

## 関連ページ

- [cpprefjp: time_get](https://cpprefjp.github.io/reference/locale/time_get.html)
- [cppreference: std::time_get](https://en.cppreference.com/w/cpp/locale/time_get)
