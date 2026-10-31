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

`from_stream` は関数呼び出しの形ですが、ストリームの `>>` でつなげて書きたいこともあります。`std::chrono::parse(fmt, x)` は、`from_stream` を `>>` から呼べるようにする操作子で、`is >> parse("%F", ymd);` のように書けます。

!!! tip "ポイント"
    - `is >> parse(書式, 変数)` で読む。`from_stream` と同じ動作
    - 失敗すると、ストリームに `failbit` が立つ
    - 複数の値を `>>` でつなげて読める
    - 読んだあとに `ok()` で有効性を確かめる

!!! info "このページを読む前に"
    [`from_stream`](from_stream.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::parse {#parse}

<span class="ver ver-20">C++20</span>

```cpp
template <class CharT, class Parsable>
/* 実装定義 */ parse(const CharT* fmt, Parsable& tp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | `const CharT*` | 書式 |
| `tp` | chrono の型の参照 | 読んだ値を入れる変数 |

戻り値は、`>>` に渡せる、実装定義の型のオブジェクトです。`is >> parse(fmt, tp)` と書くと、内部で `from_stream(is, fmt, tp)` が呼ばれます。

`>>` でつなげられるので、複数の値を続けて読めます。

```cpp
in >> parse("%F", date) >> parse("%T", time);
```

`std::get_time` と同じ位置づけの操作子です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <sstream>

int main() {
  using namespace std::chrono;

  std::istringstream in("2026-03-09 14:30:15");
  year_month_day date;
  hh_mm_ss<seconds> time{seconds{0}};

  // 空白をはさんで、日付と時刻を続けて読む
  seconds sec{};
  in >> parse("%F", date) >> parse(" %T", sec);

  std::println("{} 月 {} 日", static_cast<unsigned>(date.month()),
               static_cast<unsigned>(date.day()));
  std::println("{} 秒", sec.count());
  std::println("失敗: {}", in.fail());
}
```

```text title="実行結果"
3 月 9 日
52215 秒
失敗: false
```

`" %T"` の先頭の空白は、入力の空白を読み飛ばす指定です。14 時 30 分 15 秒は、52215 秒です。

## ゲームでの使いどころ

テキストのログやセーブデータから、日時を読み戻すときに使います。

## よくあるミス

??? failure "書式の区切りが入力と食い違う"
    `"2026-03-09 14:30"` を `"%F%T"` で読むと、空白を読み飛ばせず、失敗します。書式にも空白を書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`from_stream`](from_stream.md) | 関数の形 |
| [`to_stream`](to_stream.md) | 逆向き。ストリームに書く |
| [`std::get_time`](../../io/get_time.md) | `tm` を読む、C 時代の操作子 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: parse](https://cpprefjp.github.io/reference/chrono/parse.html)
- [cppreference: std::chrono::parse](https://en.cppreference.com/w/cpp/chrono/parse)
