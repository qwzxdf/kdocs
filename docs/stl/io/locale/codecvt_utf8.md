---
title: std::codecvt_utf8
summary: "UTF-8 と、UCS-2 / UTF-32 を変換するファセット（非推奨）。"
order: 900
tags:
  - 入出力・文字列
---

# std::codecvt_utf8

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <codecvt>`
</div>

ファイルは UTF-8、メモリの中は `char32_t` で持ちたい。この変換のために、C++11 で用意されたのが `std::codecvt_utf8` です。`std::wstring_convert` と組み合わせて、文字列を丸ごと変換する使い方が、一時期広く使われました。

ところが C++17 で、`codecvt_utf8` も `wstring_convert` も非推奨になりました。理由は、不正な入力の扱いや、例外の仕様に問題があり、代わりになる標準の仕組みが決まっていなかったからです。今も動きますが、新しいコードで使うことは勧められません。

!!! tip "ポイント"
    - C++17 で非推奨。コンパイラが警告を出す
    - `codecvt_utf8<char32_t>` は UTF-8 と UTF-32、`codecvt_utf8<char16_t>` は UTF-8 と UCS-2（サロゲートを扱えない）
    - 不正な入力では、`wstring_convert` が `std::range_error` を投げる
    - 新しいコードは Windows API の `MultiByteToWideChar`、あるいは自前の変換関数

!!! info "このページを読む前に"
    [`std::codecvt`](codecvt.md) を先に読んでください。

## 関数の詳しい説明

### std::codecvt_utf8 {#codecvt_utf8}

<span class="ver ver-11">C++11</span>

```cpp
template <class Elem, unsigned long Maxcode = 0x10ffff,
          std::codecvt_mode Mode = std::codecvt_mode(0)>
class codecvt_utf8 : public std::codecvt<Elem, char, std::mbstate_t>;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Elem` | メモリ上の文字の型。`char32_t`、`char16_t`、`wchar_t` |
| `Maxcode` | 扱える最大のコードポイント。既定は Unicode の上限 `0x10ffff` |
| `Mode` | `consume_header`（BOM を読み飛ばす）、`generate_header`（BOM を書く）など |

`Elem` が `char32_t` なら、UTF-8 と UTF-32 の変換です。`char16_t` や、Windows の `wchar_t` を渡すと、UTF-8 と UCS-2 の変換になります。UCS-2 は、UTF-16 のサロゲート ペアを使わない形式なので、基本多言語面の外の文字（多くの絵文字）は変換できません。

サロゲート ペアを含む UTF-16 との完全な変換には、同じ系統の `codecvt_utf8_utf16` を使います。こちらも非推奨です。

### std::wstring_convert と組み合わせる {#wstring_convert}

```cpp
std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
std::string utf8 = conv.to_bytes(U"あ");     // UTF-32 → UTF-8
std::u32string u32 = conv.from_bytes(utf8);  // UTF-8 → UTF-32
```

`to_bytes` と `from_bytes` が、変換を 1 回で行います。不正な入力があると、`std::range_error` を投げます。

## 実際に動かしてみる

```cpp
#include <codecvt>
#include <locale>
#include <print>
#include <string>

int main() {
  std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;

  // UTF-32 の「あ」(U+3042) → UTF-8
  const std::string s = conv.to_bytes(U'あ');
  std::println("UTF-8 のバイト数: {}", s.size());

  // UTF-8 → UTF-32 に戻す
  const std::u32string back = conv.from_bytes(s);
  std::println("往復: {}", back.size() == 1 && back[0] == U'あ');
}
```

```text title="実行結果"
UTF-8 のバイト数: 3
往復: true
```

このコードは、コンパイラが非推奨の警告を出しますが、動作はします。日本語の「あ」は、UTF-8 では 3 バイトです。

## ゲームでの使いどころ

古いコードで、UTF-8 と UTF-32 の変換に使われているのを見かけます。新しく書くなら、次のような方法があります。

- Windows では `MultiByteToWideChar(CP_UTF8, ...)` と `WideCharToMultiByte(CP_UTF8, ...)`
- UTF-8 と UTF-32 の変換だけなら、UTF-8 の規則（先頭バイトの形で長さが決まる）を使って、数十行で自作する

内部の文字列を、最初から UTF-8 の `std::string` に統一すれば、そもそも変換の回数が減ります。

## よくあるミス

??? failure "非推奨の警告を無視して使い続ける"
    将来の標準から削除される可能性があります。置き換える方法を決めておきます。

??? failure "不正な UTF-8 で例外が飛ぶのを知らない"
    `from_bytes` は、不正なバイト列を読むと `std::range_error` を投げます。外部から来るデータには、try で囲むか、検査済みのデータだけに使います。

??? failure "char16_t でサロゲート ペアが壊れる"
    `codecvt_utf8<char16_t>` は UCS-2 なので、サロゲートを扱えません。絵文字などで失敗します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`codecvt`](codecvt.md) | 基底の仕組み |
| `codecvt_utf8_utf16` | UTF-8 と UTF-16 を変換する。同じく非推奨 |
| `MultiByteToWideChar` | Windows の API。UTF-8 を直接指定できる |

## コンパイラ対応

C++11 から使えます。C++17 で非推奨です。MSVC は、使うと警告（C4996）を出します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `codecvt_utf8` は、UTF-8 と UTF-32（または UCS-2）を変換するが、C++17 で非推奨
    - [x] `wstring_convert` と組み合わせて使うが、不正な入力で例外が飛ぶ
    - [x] 新しいコードは、API の直前での変換か、自前の関数

## 関連ページ

- [cpprefjp: codecvt_utf8](https://cpprefjp.github.io/reference/codecvt/codecvt_utf8.html)
- [cppreference: std::codecvt_utf8](https://en.cppreference.com/w/cpp/locale/codecvt_utf8)
