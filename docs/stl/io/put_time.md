---
title: std::put_time
summary: "日時（`tm`）を、書式を指定して出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::put_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <iomanip>`
</div>

スクリーンショットのファイル名を `shot_20261029_140509.png` のように、撮った日時で付けたい。ログの行頭に時刻を付けたい。日時を、決まった書式の文字にするのが `std::put_time` です。`tm` 構造体と、`%Y-%m-%d` のような書式の文字列を渡すと、ストリームに書き出してくれます。

!!! tip "ポイント"
    - `std::put_time(&tm, "%Y-%m-%d %H:%M:%S")` のように、`tm` へのポインターと書式を渡す
    - 書式は `strftime` と同じ（`%Y` 年、`%m` 月、`%d` 日、`%H` 時、`%M` 分、`%S` 秒）
    - `tm` の各フィールドは、自分で正しく入れる。現在時刻なら `localtime_s` などで作る
    - 曜日や月の名前は、ストリームのロケールで決まる

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::put_time {#put_time}

```cpp
template <class CharT>
/* 未規定 */ put_time(const std::tm* tmb, const CharT* fmt);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tmb` | `const std::tm*` | 書き出す日時 |
| `fmt` | `const CharT*` | 書式。`%` で始まる変換指定と、それ以外の文字 |

ストリームのロケールの `time_put` ファセットに、`tmb` と `fmt` を渡して書き出させます。使える変換指定は `strftime` と同じで、主なものは次のとおりです。

| 指定 | 意味 | 例 |
| --- | --- | --- |
| `%Y` | 西暦 4 桁 | `2026` |
| `%m`・`%d` | 月・日（2 桁、ゼロ埋め） | `10`・`29` |
| `%H`・`%M`・`%S` | 時（24 時間）・分・秒 | `14`・`05`・`09` |
| `%a`・`%b` | 曜日・月の短い名前 | `Thu`・`Oct` |
| `%F`・`%T` | `%Y-%m-%d`・`%H:%M:%S` の短縮形 | `2026-10-29`・`14:05:09` |

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>
#include <ctime>

int main() {
  std::tm t{};
  t.tm_year = 2026 - 1900;
  t.tm_mon = 10 - 1;
  t.tm_mday = 29;
  t.tm_hour = 14;
  t.tm_min = 5;
  t.tm_sec = 9;
  t.tm_wday = 4;   // 木曜日

  std::cout << std::put_time(&t, "%Y-%m-%d %H:%M:%S") << '\n';
  std::cout << std::put_time(&t, "%Y%m%d_%H%M%S") << '\n';
  std::cout << std::put_time(&t, "%a %b %d") << '\n';
}
```

```text title="実行結果"
2026-10-29 14:05:09
20261029_140509
Thu Oct 29
```

`tm` の年は 1900 からの年数、月は 0 から始まります（10 月は 9）。`%a` の曜日は、`tm_wday`（日曜が 0）を見るので、手で作った `tm` では、自分で正しい値を入れる必要があります。ここでは、2026 年 10 月 29 日の木曜日なので 4 です。

現在時刻を出すときは、次のように `tm` を作ります。

```cpp
#include <ctime>
#include <iomanip>
#include <iostream>

void PrintNow() {
  std::time_t now = std::time(nullptr);
  std::tm local{};
  localtime_s(&local, &now);                       // MSVC。POSIX では localtime_r(&now, &local)
  std::cout << std::put_time(&local, "%F %T") << '\n';
}
```

## ゲームでの使いどころ

セーブ データやスクリーンショットのファイル名に、日時を入れるときです。`%Y%m%d_%H%M%S` の形にすると、ファイル名を並べ替えたときに、撮影順になります。ログの行頭の時刻にも使います。

`localtime` 自体は、内部の静的な領域を使うので、複数のスレッドから呼ぶと危険です。上のように、`localtime_s`（MSVC）か `localtime_r`（POSIX）に自分の `tm` を渡します。C++20 以降なら、`std::format("{:%F %T}", std::chrono::system_clock::now())` のように、`<chrono>` の時刻をそのまま書式化できて、`tm` を経由する必要がありません。新しく書くコードなら、そちらを先に考えてください。

## よくあるミス

??? failure "曜日が、実際と違う"
    手で作った `tm` の `tm_wday` が 0（日曜）のままです。`std::mktime(&t)` を呼ぶと、`tm_wday` と `tm_yday` が計算し直されます。

??? failure "月が 1 つずれる、年が 1900 になる"
    `tm_mon` は 0 から、`tm_year` は 1900 からの年数です。10 月なら 9、2026 年なら 126 を入れます。

??? failure "現在時刻が 9 時間ずれる"
    `gmtime`（UTC）で作った `tm` です。ローカル時間なら `localtime_s` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_time`](get_time.md) | 逆に、文字から日時を読み込む |
| [`strftime`](ctime/strftime.md) | 同じ書式で、文字配列に書き出す C の関数 |
| [`std::format` の日時書式と `chrono`](../utilities/chrono.md) | `<chrono>` の時刻を、`tm` を使わずに書式化する（C++20） |

## コンパイラ対応

C++11 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `put_time` は、`tm` を `strftime` の書式で書き出す
    - [x] `tm_year` は 1900 からの年数、`tm_mon` は 0 から。手で作った `tm` は `tm_wday` も入れる
    - [x] 現在時刻は `localtime_s` で作る。C++20 なら `std::format` で `<chrono>` を直接書式化できる

## 関連ページ

- [cpprefjp: std::put_time](https://cpprefjp.github.io/reference/ios/put_time.html)
- [cppreference: std::put_time](https://en.cppreference.com/w/cpp/io/manip/put_time)
