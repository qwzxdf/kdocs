---
title: std::get_time
summary: "日時を、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::get_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <iomanip>`
</div>

ログやセーブ データに `2026-10-29 14:05:09` のような日時の文字が書いてあり、それを `tm` 構造体に読み込んで、比べたり計算したりしたい。`std::get_time` は、`put_time` と逆に、書式を指定して、文字から日時を読み込みます。

!!! tip "ポイント"
    - `in >> std::get_time(&tm, "%Y-%m-%d %H:%M:%S")` のように、`tm` へのポインターと書式を渡す
    - 書式に合わない文字があると、ストリームが失敗状態（`failbit`）になる
    - 読み込むのは、書式に出てくるフィールドだけ。曜日などは設定されないことがある
    - `tm_year` は 1900 からの年数、`tm_mon` は 0 から始まる

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::get_time {#get_time}

```cpp
template <class CharT>
/* 未規定 */ get_time(std::tm* tmb, const CharT* fmt);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tmb` | `std::tm*` | 読み込んだ値を入れる構造体 |
| `fmt` | `const CharT*` | 書式。`put_time` と同じ変換指定 |

ストリームのロケールの `time_get` ファセットが、入力を `fmt` に従って読み、`tmb` の対応するフィールドを書き換えます。`fmt` にないフィールドは、触りません。読み込みが失敗すると、ストリームに `failbit` が立ち、`tmb` の中身は、未規定になります。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>
#include <print>
#include <sstream>
#include <ctime>

int main() {
  std::tm t{};
  std::istringstream in("2026-10-29 14:05:09");
  in >> std::get_time(&t, "%Y-%m-%d %H:%M:%S");
  std::println("ok={} {}/{}/{} {}:{}:{}", static_cast<bool>(in),
               t.tm_year + 1900, t.tm_mon + 1, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec);

  std::tm bad{};
  std::istringstream in2("2026/10/29");
  in2 >> std::get_time(&bad, "%Y-%m-%d");
  std::println("ok={}", static_cast<bool>(in2));
}
```

```text title="実行結果"
ok=true 2026/10/29 14:5:9
ok=false
```

1 つ目は、書式どおりの入力なので読めて、`tm_year` から 1900 を足して西暦に直しています。2 つ目は、入力が `/` 区切りで、書式の `-` と合わないため、`failbit` が立っています。読んだあとは、必ず `static_cast<bool>(in)`（または `if (in)`）で成功を確かめます。

## ゲームでの使いどころ

セーブ データの保存日時を表示するとき、ログ ファイルの時刻から経過時間を計算するとき、リプレイ ファイルの日時を並べ替えるときです。読んだ `tm` は、`std::mktime` で `time_t` に変えると、秒単位の差を計算できます。

ただし、書式が少しでも違うと失敗します。外部から来る文字（ユーザーが編集できるファイルなど）は、失敗した場合の扱いを必ず決めておきます。C++20 以降なら、`std::chrono::parse` で `<chrono>` の時刻型に直接読み込めて、`tm` を経由せずに済みます。

## よくあるミス

??? failure "読み込みの成否を確かめず、`tm` をそのまま使った"
    失敗したときの `tm` の中身は、未規定です。`if (in)` で成功を確かめてから使います。

??? failure "月が 1 つ多い、年が 1900 になる"
    読んだ値が `tm_mon`（0 から）、`tm_year`（1900 からの年数）に入っています。表示や比較の前に、補正してください。

??? failure "`tm_wday` や `tm_yday` を使ったら、0 だった"
    `get_time` は、書式にあるフィールドしか書き換えません。曜日や通算日が必要なら、`std::mktime(&t)` を呼ぶと計算されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`put_time`](put_time.md) | 逆に、日時を書式付きで書き出す |
| `strptime` | 同じ書式で文字配列から読む、POSIX の関数（標準の C++ にはない） |
| [`strftime`](ctime/strftime.md) | 逆に、同じ書式で日時を文字配列に書き出す C の関数 |

## コンパイラ対応

C++11 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `get_time` は、書式に従って文字から日時を `tm` に読み込む
    - [x] 書式に合わないと `failbit` が立つ。読んだら、必ず成否を確かめる
    - [x] `tm_year` は 1900 からの年数、`tm_mon` は 0 から。曜日などは `mktime` で補う

## 関連ページ

- [cpprefjp: std::get_time](https://cpprefjp.github.io/reference/ios/get_time.html)
- [cppreference: std::get_time](https://en.cppreference.com/w/cpp/io/manip/get_time)
