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

日付を `2026/03/09` の形で時刻を `14:30:00` の形で、出力したい。`std::chrono::to_stream` は書式の文字列（`%Y/%m/%d` など）に従って `year_month_day`、`sys_seconds`、`hh_mm_ss` などの chrono の型を出力ストリームに書き込みます。書式は `strftime` と同じ系統です。

C++20 では `std::format` や `std::println` の書式（`{:%F}`）からも同じ書式が使えるので、新しいコードではそちらのほうが書きやすくなります。`to_stream` はその書式処理の下にある関数です。

!!! tip "ポイント"
    - 第 2 引数が書式。`%Y`、`%m`、`%d`、`%H`、`%M`、`%S` など
    - 対応していない型と書式の組み合わせでは、`failbit` が立つ（例: `year_month_day` に `%H`）
    - `std::format("{:%F}", x)` が同じ書式を使う
    - 逆向きは `from_stream` と `parse`

!!! info "このページを読む前に"
    [`std::strftime`](../../io/ctime/strftime.md) の書式を先に読んでください。

## 関数の詳しい説明

### std::chrono::to_stream {#to_stream}

<span class="ver ver-20">C++20</span>

```cpp
template <class CharT, class Traits, class Duration>
std::basic_ostream<CharT, Traits>&
to_stream(std::basic_ostream<CharT, Traits>& os, const CharT* fmt,
          const sys_time<Duration>& tp);
// year_month_day、hh_mm_ss、duration、zoned_time など、型ごとのオーバーロード
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | `std::basic_ostream&` | 書き込み先 |
| `fmt` | `const CharT*` | 書式 |
| 第 3 引数 | chrono の型 | 書き出す値 |

使える書式の指定は型によって決まります。`year_month_day` なら年月日の指定（`%Y`、`%m`、`%d`、`%F`）、`sys_seconds` なら日時の全部、`hh_mm_ss` なら時刻の指定（`%H`、`%M`、`%S`、`%T`）です。型が持たない情報の指定（日付の型に `%H`）は、書き込みに失敗して `failbit` が立ちます。

戻り値は `os` への参照です。

## 実際に動かしてみる

`to_stream` の呼び出しは次の形です。

```cpp
std::ostringstream oss;
std::chrono::to_stream(oss, "%Y/%m/%d", 2026y / March / 9);   // 2026/03/09
std::chrono::to_stream(oss, "%F %T", sys_days{2026y / March / 9} + 14h + 30min);
```

手元の MSVC（Visual Studio 2026）では、`to_stream` は公開されておらずこのままではコンパイルできません。同じ書式は `std::format` の `{:%…}` に書けるので、動作の確認にはそちらを使います。

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  std::println("{:%Y/%m/%d}", 2026y / March / 9);

  // 日時の型には、時刻の指定も使える
  const sys_seconds s = sys_days{2026y / March / 9} + 14h + 30min;
  std::println("{:%F %T}", s);

  // 日付の型に、時刻の指定を書くと誤り。実行時の書式（vformat）だと例外になる
  const year_month_day d = 2026y / March / 9;
  try {
    (void)std::vformat("{:%H}", std::make_format_args(d));
  } catch (const std::format_error&) {
    std::println("型が持たない情報の指定は例外");
  }
}
```

```text title="実行結果"
2026/03/09
2026-03-09 14:30:00
型が持たない情報の指定は例外
```

`std::format` では型が持たない書式の指定は書式が定数ならコンパイル エラーになります。実行時に決まる書式（`vformat`）では `std::format_error` になります。`to_stream` では同じ誤りが `failbit` になります。

## ゲームでの使いどころ

ログやセーブデータの日時の表示で使います。新しいコードは `std::format("{:%F %T}", s)` で同じ書式を直接書けます。

## よくあるミス

??? failure "型が持たない書式を指定する"
    日付の型に `%H` を指定すると、`failbit` が立ち何も出ません。型に合った書式を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`from_stream`](from_stream.md) | 逆向き。ストリームから読む |
| [`parse`](parse.md) | `>>` で読むための操作子 |
| `std::format` | `{:%F}` の書式で同じことができる |
| [`std::strftime`](../../io/ctime/strftime.md) | C の書式化関数 |

## コンパイラ対応

C++20 の機能です。手元の MSVC では `to_stream` を使えず `std::format` の `{:%…}` が代わりになります。GCC と Clang の新しい版では使えます。

## 関連ページ

- [cpprefjp: to_stream](https://cpprefjp.github.io/reference/chrono/to_stream.html)
- [cppreference: std::chrono::to_stream](https://en.cppreference.com/w/cpp/chrono/to_stream)
