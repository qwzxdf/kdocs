---
title: std::basic_ios
summary: "すべてのストリームの土台。状態の確認（good / fail / bad）とロケールの設定を持つ。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_ios

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`cin` も `cout` もファイルも、状態（「いま正常か」「入力が終わったか」）とロケールを持っています。その共通の部分を持つ土台が `basic_ios` で、`std::ios` はその `char` 版の別名です。ストリームの失敗を調べるときに使う `good()`・`fail()`・`bad()`・`rdstate()` は、この土台のメンバです。

!!! tip "ポイント"
    - `good()`・`eof()`・`fail()`・`bad()` で状態を調べる。
    - `setstate()` で状態を設定し、`clear()` で戻す。
    - `std::ios` = `basic_ios<char>`。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_ios {#basic_ios}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_ios : public ios_base;
using ios = basic_ios<char>;
```

- 戻り値: ストリームの共通の土台

### good {#good}

```cpp
bool good() const;
```

- 戻り値: エラーがなければ `true`（`badbit`・`eofbit`・`failbit` が全部立っていない）
- 計算量: 定数

### fail {#fail}

```cpp
bool fail() const;
```

- 戻り値: `failbit` か `badbit` が立っていれば `true`
- 計算量: 定数

読み込みの失敗（`int` に変換できない文字など）で `true` になります。`operator!` と `explicit operator bool` は、これを使っています。

### bad {#bad}

```cpp
bool bad() const;
```

- 戻り値: `badbit` が立っていれば `true`（回復できない深刻なエラー）
- 計算量: 定数

### rdstate {#rdstate}

```cpp
iostate rdstate() const;
```

- 戻り値: 状態フラグ（`badbit`・`eofbit`・`failbit`）のビットマスク
- 計算量: 定数

### setstate {#setstate}

```cpp
void setstate(iostate state);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `state` | iostate | 立てる状態フラグ |

- 戻り値: なし
- 計算量: 定数

既存の状態に、フラグを**足し**ます（上書きはしません）。上書きは `clear(state)` です。

### imbue {#imbue}

```cpp
std::locale imbue(const std::locale& loc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `loc` | locale | 設定するロケール |

- 戻り値: それまでのロケール
- 計算量: 定数

ストリームのロケールを設定します。数値の区切りや日付の書式が変わります。

### getloc {#getloc}

```cpp
std::locale getloc() const;
```

- 戻り値: ストリームのロケール
- 計算量: 定数

### std::ios {#ios}

```cpp
using ios = basic_ios<char>;
```

- 戻り値: `char` 用の `basic_ios` の別名
- 計算量: なし

`basic_ios<char>` の別名で、すべての `char` ストリームの土台です。`std::ios::sync_with_stdio` のような static な関数や、`std::ios::in` のようなフラグも、`ios_base` から受け継いでいるため、`std::ios::` で書けます。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("abc");
  int n = 0;
  in >> n;  // 数字ではないので失敗
  std::println("{} {}", in.good(), in.fail());
}
```

```text title="実行結果"
false true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 入力が失敗したかを調べる | `if (!(std::cin >> n)) { ... }`（`fail()` が呼ばれる） |

## よくあるミス

??? failure "`eof()` だけでループを書く"
    最後の読み込みの後で `eof()` が真になるまでループすると、最後に 1 回余分に読みます。読み込みの成否で判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ios_base`](ios_base.md) | 書式フラグなど |
| [`istream`](istream.md) | 入力ストリーム |
| [`ostream`](ostream.md) | 出力ストリーム |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの土台
    - [x] 状態の確認とロケール
    - [x] ios は char 版の別名

## 関連ページ

- [cpprefjp: std::basic_ios](https://cpprefjp.github.io/reference/ios/basic_ios.html)
- [cppreference: std::basic_ios](https://en.cppreference.com/w/cpp/io/basic_ios)
