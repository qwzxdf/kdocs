---
title: va_copy
summary: "va_list を複製して、同じ引数をもう一度読めるようにする。"
order: 900
tags:
  - 入出力・文字列
---

# va_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdarg>`
</div>

`printf` 風の関数で、書式に合う文字列の長さを先に測ってから、ちょうどの大きさの領域を用意して書き込みたい。ところが `vsnprintf` は、読んだ分だけ `va_list` を進めてしまうので、長さを測ったあとの `va_list` では、もう一度同じ引数を読めません。そこで、読む前の位置を `va_copy` で複製しておき、1 回目は元の、2 回目は複製の `va_list` を使います。

!!! tip "ポイント"
    - `va_list` を単純に代入（`ap2 = ap;`）してはいけない。環境によっては壊れる
    - 複製にも、元にも、それぞれ `va_end` が要る
    - 別の関数に `va_list` を渡すと、そのあと元の値は不定になる。使い回すなら先に複製する
    - C++11 から標準（C99 の機能を取り込んだもの）

!!! info "このページを読む前に"
    [`<cstdarg>`](cstdarg.md) の概要と [`va_start`](va_start.md)・[`va_end`](va_end.md) を先に読んでください。

## 関数の詳しい説明

### va_copy {#va_copy}

<span class="ver ver-11">C++11</span>

```cpp
void va_copy(va_list dest, va_list src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `va_list` | 複製の入る変数。宣言だけで、初期化していないもの |
| `src` | `va_list` | 複製元。`va_start` で初期化したもの |

`src` の今の位置を覚えた `va_list` を、`dest` に作ります。そのあと `dest` を読み進めても、`src` は動きません。逆も同じです。

`va_list` の中身は、環境によって、ただの整数のポインタだったり、構造体の配列だったりします。そのため `ap2 = ap;` は、前者では動き、後者では同じ領域を共有して壊れます。代入に頼らず、必ず `va_copy` を使います。

`dest` には、すでに `va_start` や `va_copy` を呼んだ `va_list` を渡してはいけません。2 回初期化することになります。また、複製した `dest` も、使い終えたら `va_end` が要ります。

戻り値はありません（マクロです）。計算量は定数です。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>
#include <print>
#include <string>

// printf 風に書式を展開して、std::string を返す
std::string Format(const char* fmt, ...) {
  va_list ap;
  va_start(ap, fmt);

  va_list ap2;
  va_copy(ap2, ap);  // 長さを測る分の複製

  // nullptr, 0 を渡すと、書き込まずに必要な長さだけが返る
  const int length = std::vsnprintf(nullptr, 0, fmt, ap);
  va_end(ap);

  std::string result(static_cast<size_t>(length), '\0');
  // 終端の '\0' の分、1 バイト多く渡す
  std::vsnprintf(result.data(), result.size() + 1, fmt, ap2);
  va_end(ap2);
  return result;
}

int main() {
  std::println("{}", Format("HP=%d name=%s", 30, "Taro"));
}
```

```text title="実行結果"
HP=30 name=Taro
```

1 回目の `vsnprintf` に `ap` を渡すと、`ap` は使えなくなります。そこで先に `ap2` へ複製しておき、2 回目は `ap2` で書き込んでいます。`va_end` は、`ap` と `ap2` の両方に呼んでいます。

## ゲームでの使いどころ

可変長のログを、固定長のバッファ（256 バイトなど）に収まらないときのために、長さを測ってから確保する関数に使います。ログが短いと分かっていれば、固定長のバッファと 1 回の `vsnprintf` で済むので、`va_copy` は要りません。

C++ だけのコードなら、`std::format` に任せれば、長さを測る処理を自分で書く必要はありません。

## よくあるミス

??? failure "va_list を代入で複製する"
    `va_list ap2 = ap;` と書くと、x64 の Linux のように、`va_list` が配列の型の環境で、同じ領域を共有してしまい、一方を読むと他方も進みます。Windows の MSVC では動くことが多いので、移植したときに初めて壊れます。

??? failure "複製に va_end を呼ばない"
    元の `va_list` にだけ `va_end` を呼んで、複製を放置するのは、規格では未定義動作です。`va_copy` を呼んだ数だけ、`va_end` を呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`va_start`](va_start.md) | 関数の引数から、新しく始める |
| [`va_end`](va_end.md) | 後始末。複製にも要る |
| [`vsnprintf`](cstdio/vsnprintf.md) | `va_list` を受け取って書式を展開する |

## コンパイラ対応

C++11 から標準です。MSVC、GCC、Clang とも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `va_copy(dest, src)` で、`va_list` の今の位置を複製する
    - [x] 代入では複製できない。複製にも `va_end` を呼ぶ
    - [x] `vsnprintf` に渡すと元の `va_list` は不定になるので、2 回使うなら先に複製する

## 関連ページ

- [cpprefjp: va_copy](https://cpprefjp.github.io/reference/cstdarg/va_copy.html)
- [cppreference: va_copy](https://en.cppreference.com/w/cpp/utility/variadic/va_copy)
