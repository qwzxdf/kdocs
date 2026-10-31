---
title: std::time_t
summary: "時刻（エポックからの秒数）を表す型。"
order: 900
tags:
  - 入出力・文字列
---

# std::time_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`std::time` が返す「1970 年からの秒数」を入れる変数には、何型を使えばよいのでしょうか。`int` では足りなくなる日が来るので、規格は専用の型 `std::time_t` を用意しています。中身が整数なのか、浮動小数点数なのかは、規格では決まっていません。ほとんどの環境では、秒を数える符号つきの整数です。

!!! tip "ポイント"
    - `time` が返し、`localtime` や `gmtime` が受け取る型
    - 現在の主な環境では、64 ビットの符号つき整数（秒）
    - 32 ビットだと 2038 年 1 月 19 日にあふれる（2038 年問題）。`int` には入れない
    - 引き算は `difftime` で行うと、環境の違いに安全

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::time_t {#time_t}

```cpp
using time_t = /* 実装定義の算術型 */;
```

規格が決めているのは、「時刻を表せる算術型」ということだけです。基準の日（エポック）も、規格では指定されていません。ただし POSIX では、エポックが 1970 年 1 月 1 日 0 時（UTC）と決まっていて、Windows、Linux、macOS のどれもそうなっています。

大きさは環境で違います。64 ビットの MSVC では、64 ビットの `__int64` です。古い 32 ビット環境では、32 ビットの `long` で、2038 年 1 月 19 日 3 時 14 分 7 秒（UTC）に表せなくなります。新しく書くコードでは、`time_t` のまま持ち、`int` や `long` に代入しないようにします。

32 ビットの値が 2038 年にあふれる問題は、64 ビット化で解決されています。ただしファイルやネットワークで、32 ビットの時刻を決め打ちしている古い形式には、いまも残っています。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>
#include <type_traits>

int main() {
  static_assert(std::is_arithmetic_v<std::time_t>);  // 算術型であることは確実
  std::println("ビット数: {}", sizeof(std::time_t) * 8);

  const std::time_t t = 86400;  // 1970 年 1 月 2 日 0 時（UTC）
  const std::tm* utc = std::gmtime(&t);
  std::println("{}/{}", utc->tm_mon + 1, utc->tm_mday);
}
```

```text title="実行結果"
ビット数: 64
1/2
```

ビット数は、64 ビットの環境での結果です。86400 は 1 日の秒数なので、エポックの次の日、1 月 2 日になります。

## ゲームでの使いどころ

セーブデータに時刻を保存するときに、`time_t` をそのまま書き込むと、環境によって大きさが変わります。保存形式では `std::int64_t` に直して書き、読むときに `time_t` に戻します。

## よくあるミス

??? failure "int や long に入れる"
    Windows の `long` は 32 ビットなので、2038 年にあふれます。`time_t` か `std::int64_t` を使います。

??? failure "time_t どうしを引き算して、秒だと決めつける"
    ほとんどの環境では秒ですが、規格は保証していません。`difftime` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tm`](tm.md) | 年月日時分秒に分解した形 |
| [`std::chrono::system_clock::time_point`](../../utilities/chrono/system_clock.md) | C++ の時刻の型。単位を型で持つ |
| [`std::timespec`](timespec.md) | 秒とナノ秒の組 |

## コンパイラ対応

C 由来の型です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `time_t` は、エポックからの秒数を入れる型
    - [x] 64 ビットが普通。`int` に入れない
    - [x] 保存するときは `std::int64_t` に直す

## 関連ページ

- [cpprefjp: std::time_t](https://cpprefjp.github.io/reference/ctime/time_t.html)
- [cppreference: std::time_t](https://en.cppreference.com/w/cpp/chrono/c/time_t)
