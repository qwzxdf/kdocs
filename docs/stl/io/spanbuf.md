---
title: std::spanbuf
summary: "自分で用意したメモリ領域を入出力先にするストリームバッファ。"
order: 900
tags:
  - 入出力・文字列
---

# std::spanbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <spanstream>`
</div>

`std::stringstream` は便利ですが、書き込むたびに内部の `std::string` が大きくなり、ヒープの確保が起きます。毎フレーム呼ぶ関数で、固定の大きさのバッファに整形するだけなら、この確保が無駄です。`spanbuf` は、自分で用意したメモリ領域（`char buf[256]` など）を、そのまま入出力先にします。確保もコピーもしません。

`std::spanstream` の内部にある部品で、直接使うことはほとんどありません。

!!! tip "ポイント"
    - 渡した領域を使い、新しく確保しない。領域が足りなくなったら、書き込みが失敗する
    - 領域は自分で用意し、バッファより長く生かす
    - `span()` で、いま書かれている範囲（書き込み済みの部分）が取れる
    - C++23 の機能。`stringbuf` の確保をなくしたいときの選択肢

!!! info "このページを読む前に"
    [`std::spanstream`](spanstream.md) と [`std::stringbuf`](stringbuf.md) を先に読んでください。

## 関数の詳しい説明

### std::spanbuf {#spanbuf}

<span class="ver ver-23">C++23</span>

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_spanbuf;
using spanbuf = basic_spanbuf<char>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `std::span<CharT>` | 入出力に使うメモリ領域 |
| `mode` | `std::ios_base::openmode` | 読み書きのモード。既定は `in \| out` |

渡した領域の大きさが、バッファの大きさです。それを超えて書こうとすると、`overflow` が失敗して、ストリームの `badbit` が立ちます。`stringbuf` のように大きくはなりません。

### span {#span}

```cpp
std::span<CharT> span() const noexcept;
void span(std::span<CharT> s) noexcept;
```

引数なしの `span()` は、書き込み用のモードでは、<strong>書き込み済みの範囲</strong>（先頭から、いまの書き込み位置まで）を返します。読み込み用のモードだけなら、領域全体です。引数ありの `span(s)` で、使う領域を入れ替えられます。

返るのは領域への参照にすぎないので、元のバッファが消えると、`span` も無効になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <span>
#include <spanstream>
#include <string_view>

int main() {
  char buf[16] = {};
  std::spanbuf sb{std::span<char>(buf)};
  std::ostream os(&sb);
  os << "HP " << 30;  // buf の中に直接書かれる

  const auto written = sb.span();  // 書き込み済みの範囲
  std::println("{} バイト: {}", written.size(),
               std::string_view(written.data(), written.size()));
}
```

```text title="実行結果"
5 バイト: HP 30
```

`buf` は 16 バイトありますが、`span()` が返すのは書き込み済みの 5 バイトだけです。ヒープの確保は一度も起きていません。

## ゲームでの使いどころ

毎フレーム更新する HUD の文字列（スコア、FPS）を、固定のバッファに整形するのに向いています。`std::stringstream` を毎フレーム作ると、確保が起きて遅くなるからです。

ただし、C++23 の `std::format_to_n` や、`std::format_to` と `char` の配列の組み合わせのほうが、さらに簡単で速い場面が多いです。`spanbuf` は、`<<` で書く既存のコードを、確保なしで動かしたいときに使います。

## よくあるミス

??? failure "バッファより先に span や spanbuf を破棄する"
    `span()` が返すのは、元の領域への参照だけです。バッファがスコープを抜けたあとに使うと、ぶら下がった参照になります。バッファのほうを長く生かします。

??? failure "領域が足りなくなったのに気づかない"
    `os << "とても長い文字列..."` が領域を超えると、`badbit` が立って、以降の出力は全部無視されます。`os.fail()` を調べるか、余裕のある大きさにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stringbuf`](stringbuf.md) | `std::string` を内部で確保する。大きさに制限がない |
| [`std::spanstream`](spanstream.md) | `spanbuf` に `<<` と `>>` を付けたもの。普段はこちら |
| [`std::basic_streambuf`](basic_streambuf.md) | 親クラス |

## コンパイラ対応

C++23 の機能です。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `spanbuf` は、自分で用意した領域を入出力先にする。確保しない
    - [x] 領域が足りなくなると、書き込みが失敗する
    - [x] `span()` が返す範囲は、元のバッファが生きている間だけ有効

## 関連ページ

- [cpprefjp: std::spanbuf](https://cpprefjp.github.io/reference/spanstream/basic_spanbuf.html)
- [cppreference: std::spanbuf](https://en.cppreference.com/w/cpp/io/basic_spanbuf)
