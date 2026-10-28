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

ファイルを開くときの `std::ios::binary` や `std::ios::app`、ストリームの状態を調べる `eof()` や `fail()`。これらの定数は、どこで定義されているのでしょうか。`std::ios_base` は、すべての入出力ストリームの土台になるクラスです。ファイルの開き方（`openmode`）、位置の基準（`seekdir`）、書式のフラグ（`fmtflags`）、状態（`iostate`）の定数を持っています。`std::ios` は、このクラスの派生です。

!!! tip "ポイント"
    - ファイルを開くときのフラグ: `std::ios::in` `out` `binary` `app` `trunc` `ate`。
    - 状態の確認: `good()` `eof()` `fail()` `bad()`。`if (stream)` は `!fail()` と同じ。
    - 位置の基準: `std::ios::beg` `cur` `end`。

!!! info "このページを読む前に"
    [`std::ifstream`](ifstream.md) や [`std::cout`](cout.md) など、ストリームの基本を先に読んでください。

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

ストリームに任意の整数を 1 つ持たせる（`xalloc` で取った添字で）。自作のマニピュレータがストリームごとの設定を覚えておくために使います。

### std::ios_base::pword {#pword}

```cpp
void*& pword(int idx);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `idx` | int | `xalloc()` で取った添字 |

- 戻り値: 格納場所への参照
- 計算量: 定数

ストリームに任意のポインタを 1 つ持たせる（`xalloc` で取った添字で）。自作のマニピュレータがストリームごとの設定を覚えておくために使います。

### flags {#flags}

```cpp
fmtflags flags() const;
fmtflags flags(fmtflags fl);
```

- 計算量: 定数

いまの書式フラグを返します。引数つきの版は、フラグを**全部置き換え**て、それまでのフラグを返します。

### setf {#setf}

```cpp
fmtflags setf(fmtflags fl);
fmtflags setf(fmtflags fl, fmtflags mask);
```

- 計算量: 定数

書式フラグを**追加**します。2 引数の版は、`mask` の範囲（`basefield` など）を先にクリアしてから設定するので、`hex` の切り替えに使えます。

### unsetf {#unsetf}

```cpp
void unsetf(fmtflags mask);
```

- 計算量: 定数

指定した書式フラグを解除します。

### precision {#precision}

```cpp
streamsize precision() const;
streamsize precision(streamsize new_precision);
```

- 計算量: 定数

小数の出力の桁数（既定は 6）を返す、または設定します。`setprecision` マニピュレータと同じ働きです。

### width {#width}

```cpp
streamsize width() const;
streamsize width(streamsize new_width);
```

- 計算量: 定数

次の 1 回の出力の最小の幅を返す、または設定します。出力のたびにリセットされます。`setw` と同じ働きです。

### xalloc {#xalloc}

```cpp
static int xalloc();
```

- 計算量: 定数

`iword`・`pword` で使う、新しい添字を確保して返します。自作のマニピュレータがストリームごとの設定を覚えるのに使います。

### register_callback {#register_callback}

```cpp
void register_callback(event_callback fn, int index);
```

- 計算量: 定数

`imbue`・`copyfmt`・ストリームの破棄のときに呼ばれる関数を登録します。`iword`/`pword` の後始末に使います。

### sync_with_stdio {#sync_with_stdio}

```cpp
static bool sync_with_stdio(bool sync = true);
```

- 計算量: 定数

C++ のストリームと C の入出力（`printf` など）を同期するかを設定します。`false` にすると、入出力が速くなります（競技プログラミングの定番）が `printf` と混ぜられなくなります。

### imbue {#imbue}

```cpp
std::locale imbue(const std::locale& loc);
```

- 計算量: 定数

ストリームのロケールを設定します。数値の区切りや、日付の書式が変わります。

### getloc {#getloc}

```cpp
std::locale getloc() const;
```

- 計算量: 定数

ストリームのロケールを返します。

## ゲームでの使いどころ

ファイルを開くときのフラグとして、最もよく目にします。`std::ifstream in(path, std::ios::binary);` のように指定します。複数は `|` で組み合わせます。

読み込みの失敗の調べ方は、`if (stream)` が `!fail()` と同じで、`eof()` は終わりに達したことを `bad()` は重大な失敗を示します。

書式のフラグ（`setf`、`unsetf`）は、`setw` などのマニピュレーターの下の仕組みです。新しいコードでは、`std::format` で書式を指定するので、直接触ることは少なくなります。

## よくあるミス

??? failure "eof で終わりを判断する"
    `eof()` は「読もうとして終わりだった」ときに初めて真になります。読む前に `while (!in.eof())` と書くと、最後に余分に回ります。

??? failure "`binary` を付けずにバイナリを読み、改行が変換される"
    Windows のテキストモードは、`\r\n` を `\n` に変換します。バイナリを読むときに `std::ios::binary` を付けないと、データが壊れます。

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
