---
title: std::mbstate_t
summary: "マルチバイト文字の変換の途中状態を入れる型。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbstate_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

UTF-8 のように、1 文字が複数バイトの文字コードを、1 バイトずつ受け取って変換すると、文字の途中で区切れることがあります。たとえば 3 バイトの文字の、最初の 2 バイトを受け取った時点では、まだワイド文字に変換できません。そのときの「ここまで読んだ」という途中の状態を覚えておく入れ物が `std::mbstate_t` です。`mbrtowc`、`wcrtomb`、`mbsrtowcs` などが、これを受け取って更新します。

!!! tip "ポイント"
    - 変換の途中状態を持つ。中身は処理系ごとに違うので、直接触らない
    - `std::mbstate_t state{};` で、0 で初期化してから使い始める
    - 1 つの文字列の変換の間は、同じ `mbstate_t` を使い回す。別の文字列に移るときは初期化し直す
    - 複数のスレッドで 1 つの `mbstate_t` を共有しない

!!! info "このページを読む前に"
    [`mbrtowc`](mbrtowc.md) を先に読むと、なぜ状態が要るのかが分かります。

## 関数の詳しい説明

### std::mbstate_t {#mbstate_t}

```cpp
using mbstate_t = /* 実装定義 */;
```

初期状態は、全ビットが 0 の値です。`std::mbstate_t state{};` と書けば、初期状態になります。この状態を「初期シフト状態」と呼びます。

変換関数は、状態のポインタを受け取ります。文字がちょうど完成したとき、状態は初期状態に戻ります。文字の途中で止まったときは、途中経過が状態に残ります。次の呼び出しで続きのバイトを渡すと、前の続きから変換できます。

多くの環境（MSVC の UTF-8 や、Linux の UTF-8）では、状態は、読みかけのバイトを覚えておく程度の小さな構造体です。ISO-2022-JP のような、途中で文字セットを切り替えるエンコーディングでは、切り替え状態もここに入ります。

引数に `nullptr` を渡せる関数もあります。そのときは、関数ごとの内部の状態を使うので、スレッドから使うと安全ではありません。自分の `mbstate_t` を渡すのが安全です。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::mbstate_t state{};  // 初期状態
  wchar_t wc = 0;

  // 'A' は 1 バイトで完結する。状態は初期のまま
  const std::size_t n = std::mbrtowc(&wc, "A", 1, &state);
  std::println("使ったバイト数: {}", n);
  std::println("変換結果: {}", wc == L'A');
  std::println("初期状態か: {}", std::mbsinit(&state) != 0);
}
```

```text title="実行結果"
使ったバイト数: 1
変換結果: true
初期状態か: true
```

`mbsinit` は、状態が初期状態かを調べる関数です。文字が完成して、続きの状態を持っていないので、真になります。

## ゲームでの使いどころ

自分で書くことはあまりありません。UTF-8 から UTF-16 への変換は、Windows の `MultiByteToWideChar` や、C++ の変換の関数を使うほうが確実です。

## よくあるミス

??? failure "状態を初期化しない"
    `std::mbstate_t state;` のままだと、ゴミの値が状態になります。`{}` で初期化します。

??? failure "別の文字列を、前の状態のまま変換する"
    前の文字列の途中で止まっていると、次の文字列の最初の数バイトが、前の続きとして解釈されます。文字列ごとに初期化し直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbrtowc`](mbrtowc.md) | 状態を使って 1 文字変換する |
| [`wcrtomb`](wcrtomb.md) | 逆方向の変換 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mbstate_t` は、マルチバイト変換の途中状態を入れる型
    - [x] `{}` で初期化してから使う
    - [x] 文字列ごとに初期化し直す

## 関連ページ

- [cpprefjp: mbstate_t](https://cpprefjp.github.io/reference/cwchar/mbstate_t.html)
- [cppreference: mbstate_t](https://en.cppreference.com/w/cpp/string/multibyte/mbstate_t)
