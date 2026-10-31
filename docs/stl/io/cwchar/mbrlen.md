---
title: std::mbrlen
summary: "マルチバイト文字 1 文字のバイト数を返す（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbrlen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

UTF-8 の文字列を 1 文字ずつ進めたいとき、次の文字が何バイトなのかを先に知る必要があります。ASCII は 1 バイト、日本語は 3 バイト、といった具合です。`mbrlen` は、バイト列の先頭にある 1 文字のバイト数を返します。中身を変換せずに長さだけを知りたいときに使い、`mbrtowc` の「文字を取り出さない版」にあたります。

!!! tip "ポイント"
    - 先頭の 1 文字のバイト数を返す。終端文字なら 0
    - 不正なバイト列なら `(size_t)-1`、文字の途中で切れていたら `(size_t)-2`
    - 状態は `mbstate_t` に覚えさせる。最初は `{}` で初期化する
    - 結果はロケールで変わる。UTF-8 の扱いは環境の設定による

!!! info "このページを読む前に"
    [`std::mbstate_t`](mbstate_t.md) を先に読んでください。

## 関数の詳しい説明

### std::mbrlen {#mbrlen}

```cpp
std::size_t mbrlen(const char* s, std::size_t n, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const char*` | 調べるバイト列の先頭 |
| `n` | `std::size_t` | 調べてよい最大のバイト数 |
| `ps` | `std::mbstate_t*` | 変換の途中状態 |

先頭の 1 文字が完成するまでに必要なバイト数を返します。`n` バイトの範囲に収まる場合の戻り値は、次のとおりです。

| 戻り値 | 意味 |
| --- | --- |
| 1 以上 | 先頭の文字のバイト数 |
| 0 | 終端文字（`'\0'`）だった |
| `(size_t)-1` | 不正なバイト列。`errno` が `EILSEQ` になる |
| `(size_t)-2` | `n` バイトでは文字が完成しない。続きのバイトが必要 |

`(size_t)-2` が返るのは、ネットワークやファイルから少しずつ受け取っているデータの、読みかけの部分です。そのとき状態が `ps` に残るので、続きを受け取ってから、同じ `ps` でもう一度呼びます。

`ps` には、`nullptr` も渡せますが、内部の状態を使うので、スレッドから使うと安全ではありません。自分の `mbstate_t` を渡します。

UTF-8 を正しく扱えるかは、`setlocale` の設定と、実行環境（C ランタイム）の対応しだいです。MSVC では、`setlocale(LC_ALL, ".UTF-8")` で UTF-8 のロケールにできます。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::mbstate_t state{};
  std::println("'A' の長さ: {}", std::mbrlen("A", 4, &state));
  std::println("終端の長さ: {}", std::mbrlen("", 1, &state));
}
```

```text title="実行結果"
'A' の長さ: 1
終端の長さ: 0
```

ASCII の例を使っています。日本語のバイト列で試すときは、実行環境のロケールを UTF-8 に設定してから呼びます。

## ゲームでの使いどころ

UTF-8 の文字列を 1 文字ずつ進める処理の、自作のライブラリで使われることがあります。自分で書く場合は、先頭バイトのビットパターンで長さが決まる UTF-8 の規則を直接使うほうが、ロケールに依存せず、速くて確実です。

## よくあるミス

??? failure "ロケールを設定せずに UTF-8 を渡す"
    既定の "C" ロケールでは、128 以上のバイトの扱いが環境で違います。UTF-8 を扱うなら、ロケールを設定します。

??? failure "(size_t)-2 を不正と誤解する"
    データが足りないだけで、不正ではありません。続きを受け取ってから、同じ状態でもう一度呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbrtowc`](mbrtowc.md) | 長さだけでなく、ワイド文字に変換して返す |
| [`mbsrtowcs`](mbsrtowcs.md) | 文字列全体を変換する |
| [`mbstate_t`](mbstate_t.md) | 途中の状態 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mbrlen` は、先頭の 1 文字のバイト数を返す
    - [x] `-1` は不正、`-2` は途中で切れている
    - [x] 結果はロケールで変わる

## 関連ページ

- [cpprefjp: mbrlen](https://cpprefjp.github.io/reference/cwchar/mbrlen.html)
- [cppreference: mbrlen](https://en.cppreference.com/w/cpp/string/multibyte/mbrlen)
