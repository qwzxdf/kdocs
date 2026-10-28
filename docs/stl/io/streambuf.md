---
title: std::streambuf
summary: "ストリームの裏側にある、バッファと入出力先を扱う土台のクラス。"
order: 92
tags:
  - 入出力・文字列
---

# std::streambuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <streambuf>`
</div>

`std::streambuf` は、**ストリームの内部にある、バッファと実際の入出力先（ファイル、メモリ、コンソール）を扱う土台のクラス**です。`cout` の出力先を別の場所へ切り替えたい（ログをファイルへ流す）、自作のストリーム（ネットワーク、圧縮）を作る、といった上級の場面で使います。`rdbuf()` で取り出せます。

!!! tip "ポイント"
    - `cout.rdbuf(別のbuf)` で、出力先を切り替えられる（戻すのを忘れない）。
    - ストリームの中身を丸ごと別のストリームへ流すには `out << in.rdbuf()`。
    - 自作の入出力先は、`streambuf` を継承して作る。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::streambuf {#streambuf}

```cpp
class streambuf { /* 実装向けの仮想関数 overflow / underflow など */ };
```

- 戻り値: （基底クラス）
- 計算量: 実装による

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::ostringstream captured;
  auto* original = std::cout.rdbuf(captured.rdbuf());   // cout の出力先を文字列に切り替える
  std::cout << "hello";
  std::cout.rdbuf(original);                             // 元に戻す

  std::println("取り込んだ内容: {}", captured.str());
}
```

```text title="実行結果"
取り込んだ内容: hello
```

### std::streambuf::sgetc {#sgetc}

```cpp
int_type sgetc();
```

- 戻り値: 次の 1 文字を読み進めずに返す
- 計算量: 定数

入力バッファから、次の文字をのぞきます。消費はしません。

### std::streambuf::sputc {#sputc}

```cpp
int_type sputc(char_type ch);
```

- 戻り値: 1 文字を書き込む
- 計算量: 定数

出力バッファに 1 文字を書きます。失敗すると `EOF` を返します。

### std::streambuf::in_avail {#in_avail}

```cpp
streamsize in_avail();
```

- 戻り値: 待たずに読める文字の数
- 計算量: 定数

入力バッファに**すでに**入っている文字の数を返します。ブロックせずに読める量を知りたいときに使います。

### std::streambuf::pubsync {#pubsync}

```cpp
int pubsync();
```

- 戻り値: 成功なら 0、失敗なら -1
- 計算量: 定数

バッファの内容をソースや出力先と同期します。`flush()` の中でも呼ばれます。

### std::streambuf::pubseekoff {#pubseekoff}

```cpp
pos_type pubseekoff(off_type off, ios_base::seekdir way, ios_base::openmode which = ios_base::in | ios_base::out);
```

- 戻り値: 新しい位置（失敗したら `-1`）
- 計算量: 定数

位置を相対的に移動します。`seekg`・`seekp` は、これを呼んでいます。

### std::streambuf::pubsetbuf {#pubsetbuf}

```cpp
streambuf* pubsetbuf(char_type* s, streamsize n);
```

- 戻り値: バッファを設定できたら自身（できなければ `nullptr`）
- 計算量: 定数

ストリームバッファが使う、メモリ領域を指定します。実装によっては無視されます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テストで cout の出力を取り込んで確認する | `cout.rdbuf(captured.rdbuf())` |

## よくあるミス

??? failure "元に戻し忘れる"
    破棄されたバッファに出力しようとして、クラッシュします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ostream`](ostream.md) | streambuf を使う側 |
| [`std::ifstream`](ifstream.md) | `rdbuf()` で中身を流し込める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの裏側のバッファ
    - [x] 出力先の切り替えに
    - [x] 元に戻す

## 関連ページ

- [cpprefjp: std::streambuf](https://cpprefjp.github.io/reference/streambuf/basic_streambuf.html)
- [cppreference: std::streambuf](https://en.cppreference.com/w/cpp/io/basic_streambuf)
