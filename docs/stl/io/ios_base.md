---
title: std::ios_base
summary: "ストリームの状態と、開き方・書式のフラグをまとめた土台のクラス。"
order: 68
tags:
  - 入出力・文字列
---

# std::ios_base

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

`std::ios_base` は、**すべての入出力ストリームの土台**となるクラスです。ファイルの開き方（`openmode`）、位置の基準（`seekdir`）、書式のフラグ（`fmtflags`）、状態（`iostate`）の定数を持っています。`std::ios::in` や `std::ios::binary` と書くのは、この中の定数です。

!!! tip "ポイント"
    - ファイルを開くときのフラグ: `std::ios::in` `out` `binary` `app` `trunc` `ate`。
    - 状態の確認: `good()` `eof()` `fail()` `bad()`。`if (stream)` は `!fail()` と同じ。
    - 位置の基準: `std::ios::beg` `cur` `end`。

## 開き方（openmode）

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::ios::in` | <span class="rank rank-must">必須</span> | 読み込み（ifstream のデフォルト） |
| `std::ios::out` | <span class="rank rank-must">必須</span> | 書き込み（ofstream のデフォルト。中身は消える） |
| `std::ios::binary` | <span class="rank rank-must">必須</span> | バイナリ。改行コードを変換しない |
| `std::ios::app` | <span class="rank rank-often">よく使う</span> | 必ず末尾に追記する |
| `std::ios::trunc` | <span class="rank rank-sometimes">たまに</span> | 開くときに中身を消す |
| `std::ios::ate` | <span class="rank rank-rare">知ってるだけ</span> | 開いた直後に末尾へ移動（その後は好きな場所に書ける） |
| `std::ios::noreplace` | <span class="rank rank-rare">知ってるだけ</span> | すでにファイルがあれば開くのに失敗する <span class="ver ver-23">C++23</span> |

## 位置の基準（seekdir）

| 値 | 意味 |
| --- | --- |
| `std::ios::beg` | 先頭から |
| `std::ios::cur` | 今の位置から |
| `std::ios::end` | 末尾から |

## 状態（iostate）

| 値 | 意味 | 調べる関数 |
| --- | --- | --- |
| `goodbit` | 問題なし | `good()` |
| `eofbit` | 終わりまで読んだ | `eof()` |
| `failbit` | 読み取り・変換に失敗した（数字の所に文字があった、など） | `fail()` |
| `badbit` | 読み書きそのものができない深刻なエラー | `bad()` |

## 関数の詳しい説明

### 状態の確認と復帰 {#state}

```cpp
bool good() const;   // 問題なし
bool eof() const;    // 終わりまで読んだ
bool fail() const;   // 失敗した（failbit か badbit）
bool bad() const;    // 深刻なエラー
void clear();        // エラー状態を消す
```

```cpp
#include <print>
#include <sstream>

int main() {
  std::istringstream in("12 abc");
  int a = 0;
  int b = 0;

  in >> a;                         // 12 を読む
  std::println("a={} fail={}", a, in.fail());

  in >> b;                         // "abc" は数字でない
  std::println("fail={}", in.fail());

  in.clear();                      // エラー状態を消す（読み取れなかった文字は残っている）
  std::println("fail={}", in.fail());
}
```

```text title="実行結果"
a=12 fail=false
fail=true
fail=false
```

### std::ios_base::fmtflags {#fmtflags}

```cpp
using fmtflags = /* ビットマスク型 */;
```

- 戻り値: 書式フラグ（`showbase`・`hex`・`fixed` など）を表すビットマスク型
- 計算量: 定数

`flags()` で取れる、書式の状態をまとめた型です。`ios::showpos | ios::uppercase` のように `|` でつなぎます。個別に設定するなら、マニピュレータ（`std::showpos` など）が読みやすいです。

### std::streamsize {#streamsize}

```cpp
using streamsize = /* 実装定義 */;
```

- 戻り値: ストリームで読み書きする文字数を表す符号つき整数型
- 計算量: 定数

ストリームで読み書きする文字数を表す符号つき整数型です。`read(buf, n)` の `n` や、`gcount()` の戻り値などに出てきます。

### std::streamoff {#streamoff}

```cpp
using streamoff = /* 実装定義 */;
```

- 戻り値: ストリーム上の位置の差（オフセット）を表す符号つき整数型
- 計算量: 定数

ストリーム上の位置の差（オフセット）を表す符号つき整数型です。`read(buf, n)` の `n` や、`gcount()` の戻り値などに出てきます。

### std::streampos {#streampos}

```cpp
using streampos = /* 実装定義 */;
```

- 戻り値: ストリーム上の位置を表す型（`fpos<mbstate_t>` の別名）
- 計算量: 定数

ストリーム上の位置を表す型（`fpos<mbstate_t>` の別名）です。`read(buf, n)` の `n` や、`gcount()` の戻り値などに出てきます。

### std::fpos {#fpos}

```cpp
template <class StateT>
class fpos;
```

- 戻り値: ストリームの位置を表すクラス（状態つき）
- 計算量: 定数

マルチバイト文字のように、位置に状態が必要なストリームのための位置の型です。`tellg()` の戻り値（`streampos`）が、これにあたります。整数のように足し引きできますが、`tellg()` で得た値以外の演算は、移植性がありません。

### std::ios_base::badbit {#badbit}

```cpp
static constexpr iostate badbit = /* 実装定義 */;
```

- 戻り値: 状態フラグ：ストリームが壊れた（回復できないエラー）
- 計算量: 定数

`rdstate()` で調べる状態フラグのひとつで、ストリームが壊れた（回復できないエラー）ことを表します。`good()`・`eof()`・`fail()`・`bad()` で調べるほうが読みやすいです。

### std::ios_base::eofbit {#eofbit}

```cpp
static constexpr iostate eofbit = /* 実装定義 */;
```

- 戻り値: 状態フラグ：入力が終端に達した
- 計算量: 定数

`rdstate()` で調べる状態フラグのひとつで、入力が終端に達したことを表します。`good()`・`eof()`・`fail()`・`bad()` で調べるほうが読みやすいです。

### std::ios_base::failbit {#failbit}

```cpp
static constexpr iostate failbit = /* 実装定義 */;
```

- 戻り値: 状態フラグ：操作に失敗した（形式が合わないなど。回復できる）
- 計算量: 定数

`rdstate()` で調べる状態フラグのひとつで、操作に失敗した（形式が合わないなど。回復できる）ことを表します。`good()`・`eof()`・`fail()`・`bad()` で調べるほうが読みやすいです。

### std::ios_base::goodbit {#goodbit}

```cpp
static constexpr iostate goodbit = /* 実装定義 */;
```

- 戻り値: 状態フラグ：エラーがない状態（値は 0）
- 計算量: 定数

`rdstate()` で調べる状態フラグのひとつで、エラーがない状態（値は 0）ことを表します。`good()`・`eof()`・`fail()`・`bad()` で調べるほうが読みやすいです。

### std::ios_base::iword {#iword}

```cpp
long& iword(int idx);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `idx` | int | `xalloc()` で取った添字 |

- 戻り値: 格納場所への参照
- 計算量: 定数

ストリームに、任意の整数を 1 つ持たせる（`xalloc` で取った添字で）。自作のマニピュレータが、ストリームごとの設定を覚えておくために使います。

### std::ios_base::pword {#pword}

```cpp
void*& pword(int idx);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `idx` | int | `xalloc()` で取った添字 |

- 戻り値: 格納場所への参照
- 計算量: 定数

ストリームに、任意のポインタを 1 つ持たせる（`xalloc` で取った添字で）。自作のマニピュレータが、ストリームごとの設定を覚えておくために使います。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バイナリで書き出す | `std::ofstream out(path, std::ios::binary);` |
| 読み込みの失敗を調べる | `if (in.fail()) ...` |

## よくあるミス

??? failure "eof で終わりを判断する"
    `eof()` は「読もうとして終わりだった」ときに初めて真になります。読む前に `while (!in.eof())` と書くと、最後に余分に回ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ifstream`](ifstream.md) / [`std::ofstream`](ofstream.md) | フラグを渡して使う |
| [`std::cout`](cout.md) | 書式フラグを使う |

## コンパイラ対応

C++98 から使えます。`std::ios::noreplace` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの定数と状態の土台
    - [x] 開き方は `in` `out` `binary` `app`
    - [x] 状態は `good` `eof` `fail` `bad`

## 関連ページ

- [cpprefjp: std::ios_base](https://cpprefjp.github.io/reference/ios/ios_base.html)
- [cppreference: std::ios_base](https://en.cppreference.com/w/cpp/io/ios_base)
