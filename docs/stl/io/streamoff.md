---
title: std::streamoff
summary: "ストリーム上の位置の差（オフセット）を表す符号付き整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::streamoff

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

ファイルの途中へ飛んで読み直したい。末尾から 3 文字前の位置を調べたい。そのとき、「今の位置から、何文字ずらすか」を表すのが `std::streamoff` です。符号付きの整数で、前にも後ろにもずらせます。

!!! tip "ポイント"
    - ストリーム上の位置の差（オフセット）を表す、符号付きの整数型
    - `seekg(off, dir)` の第 1 引数や、2 つの位置の差（`tellg() - here`）が、この型になる
    - 負の値で、後ろに戻れる。基準は `ios::beg`（先頭）、`ios::cur`（今の位置）、`ios::end`（末尾）
    - 大きなファイルでも桁あふれしないように、`int` ではなくこの型で持つ

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::streamoff {#streamoff}

```cpp
using streamoff = /* 実装定義の符号付き整数型 */;
```

`<ios>` で定義されます。64 ビット版の MSVC では 8 バイトで、2 GB を超えるファイルの位置も表せます。

`seekg` の 2 つの形で使われます。

| 書き方 | 意味 |
| --- | --- |
| `in.seekg(pos)` | 絶対位置（`streampos`）へ移動する |
| `in.seekg(off, dir)` | 基準 `dir` から `off` だけずらした位置へ移動する |

`streampos` どうしを引き算すると、`streamoff` になります。

## 実際に動かしてみる

```cpp
#include <ios>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::println("streamoff: {} バイト", sizeof(std::streamoff));

  std::istringstream in("0123456789\nabc\n");

  // 末尾から 3 文字前へ（負のオフセット）
  in.seekg(-3, std::ios::end);
  char c = static_cast<char>(in.get());
  std::println("末尾から 3 文字前: {}", c);

  // 位置の差は streamoff
  in.clear();
  in.seekg(2);
  std::streampos from = in.tellg();
  std::string line;
  std::getline(in, line);
  std::streamoff len = in.tellg() - from;
  std::println("読んだ行: {} / 進んだ量: {}", line, static_cast<long long>(len));
}
```

```text title="実行結果"
streamoff: 8 バイト
末尾から 3 文字前: b
読んだ行: 23456789 / 進んだ量: 9
```

`seekg(-3, std::ios::end)` は、末尾から 3 文字戻った位置で、そこには `b`（`abc\n` の `b`）があります。2 つ目は、位置 2 から 1 行読み、`tellg()` どうしを引き算した値（`streamoff`）が、改行を含めて進んだ 9 文字を示しています。

## ゲームでの使いどころ

セーブ データやアセットのパックのように、先頭に目次を持つバイナリ ファイルです。目次に書いてあるオフセットの位置へ `seekg(offset)` で飛んで、そこから必要な分だけ読みます。末尾にチェックサムなどの固定長の情報があるファイルでは、`seekg(-8, std::ios::end)` のように、末尾から数えて読み込みます。

## よくあるミス

??? failure "`seekg` したのに、思った場所に飛ばない"
    直前の読み込みで `eofbit` が立っていると、`seekg` が効きません。C++11 以降は `seekg` が先にクリアしますが、古いコードでは `in.clear()` を先に呼んでいました。

??? failure "テキスト モードで、オフセットがずれる"
    Windows のテキスト モードでは、改行が 2 文字（`\r\n`）として保存されているので、読んだ文字数とファイル上のバイト数がずれます。正確なオフセットが必要なら、バイナリ モード（`std::ios::binary`）で開きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`streampos`](streampos.md) | 位置そのものを表す型。差を取ると `streamoff` になる |
| [`streamsize`](streamsize.md) | 読み書きする文字数を表す型 |
| [`fpos`](fpos.md) | `streampos` の元になっているクラス テンプレート |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `streamoff` は、ストリーム上の位置のずれを表す符号付きの整数型
    - [x] `seekg(off, dir)` に渡す。負の値で、後ろへ戻れる
    - [x] Windows のテキスト モードでは、オフセットと文字数がずれる。正確さが要るなら `binary`

## 関連ページ

- [cpprefjp: std::streamoff](https://cpprefjp.github.io/reference/ios/streamoff.html)
- [cppreference: std::streamoff](https://en.cppreference.com/w/cpp/io/streamoff)
