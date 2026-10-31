---
title: std::ctime
summary: "time_t を、ローカル時刻の決まった形の文字列にする。"
order: 900
tags:
  - 入出力・文字列
---

# std::ctime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`std::ctime(&now)` は、現在時刻を `Sat Oct 31 18:00:05 2026` のような、英語の決まった形の文字列にします。内部では `localtime` と `asctime` を続けて呼ぶ処理と同じです。1 行でログの時刻を出せるので、昔の C のコードでよく使われました。

書式を選べない点や、結果が静的な領域に置かれる点は、`asctime` と同じです。今は、`strftime` か `std::format` を使います。

!!! tip "ポイント"
    - `ctime(&t)` は `asctime(localtime(&t))` と同じ。結果はローカル時刻
    - 全体で 25 文字、末尾に改行が付く
    - 結果は静的な領域を指す。次の呼び出しで上書きされる
    - 失敗すると `nullptr`

!!! info "このページを読む前に"
    [`std::asctime`](asctime.md) と [`std::localtime`](localtime.md) を先に読んでください。

## 関数の詳しい説明

### std::ctime {#ctime}

```cpp
char* ctime(const std::time_t* timer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `timer` | `const std::time_t*` | 文字列にする時刻。ポインタで渡す |

戻り値は、静的な領域にある文字列へのポインタです。形は `asctime` と同じで、`曜日 月 日 時:分:秒 年` と、末尾に改行が付きます。時刻はローカル時刻で、タイムゾーンの設定によって結果が変わります。

変換できない `time_t` を渡すと `nullptr` を返すので、外から来る値のときは、検査してから使います。

内部で `localtime` を使うので、`localtime`、`gmtime`、`asctime` と、静的な領域を共有している環境があります。たとえば、`ctime` を呼んだあとで `localtime` を呼ぶと、先に取った文字列が壊れることがあります。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <ctime>
#include <print>

int main() {
  const std::time_t now = std::time(nullptr);
  const char* text = std::ctime(&now);

  // 結果は時刻によって変わるので、形だけ確かめる
  std::println("文字数: {}", std::strlen(text));
  std::println("末尾は改行: {}", text[std::strlen(text) - 1] == '\n');
}
```

```text title="実行結果"
文字数: 25
末尾は改行: true
```

中身の日時は実行のたびに変わりますが、形は固定で 25 文字です。

## ゲームでの使いどころ

使う場面はほとんどありません。古いコードで、ログの先頭に時刻を出している箇所を読むときに出会います。置き換える先は、`strftime` です。

```cpp
char text[32];
const std::tm local = *std::localtime(&now);
std::strftime(text, sizeof(text), "%Y-%m-%d %H:%M:%S", &local);
```

## よくあるミス

??? failure "末尾の改行を知らずに使う"
    戻り値の末尾に `\n` があります。`println("{}", ctime(&t))` では、空行が入ります。

??? failure "戻り値のポインタを保存する"
    次の `ctime` や `localtime` の呼び出しで、中身が上書きされます。必要なら `std::string` にコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`asctime`](asctime.md) | `tm` を同じ形の文字列にする |
| [`strftime`](strftime.md) | 書式を選べる。普段はこちら |
| [`localtime`](localtime.md) | ローカル時刻の `tm` に分解する |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。MSVC は、`ctime` を使うと警告（C4996）を出すことがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ctime(&t)` は、ローカル時刻を固定の形（25 文字、末尾に改行）の文字列にする
    - [x] 静的な領域を使うので、コピーして持つ
    - [x] 新しいコードは `strftime`

## 関連ページ

- [cpprefjp: std::ctime](https://cpprefjp.github.io/reference/ctime/ctime.html)
- [cppreference: std::ctime](https://en.cppreference.com/w/cpp/chrono/c/ctime)
