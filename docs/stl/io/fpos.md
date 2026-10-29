---
title: std::fpos
summary: "ストリームの位置を状態つきで表すクラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::fpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`std::fpos` は、ストリーム上の位置を表すクラス テンプレートです。`std::streampos` は、これの別名で、ふつうは `fpos` という名前を直接書くことはありません。位置の数値と、文字コード変換の途中状態をまとめて持つこと、足し算や引き算、比較ができることを知っておくと、`streampos` の挙動が読みやすくなります。

!!! tip "ポイント"
    - `streampos`・`wstreampos`・`u8streampos` などの、位置の型の元になっているテンプレート
    - 位置の数値（`streamoff`）と、変換の状態（`mbstate_t`）を持つ
    - `streamoff` との足し算・引き算、`fpos` どうしの引き算と比較ができる
    - 数値だけを取り出したいときは、`streamoff` に変換する

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::fpos {#fpos}

```cpp
template <class State>
class fpos;
```

`<ios>` で定義されます。`State` は、文字コードの変換の途中状態を表す型で、標準では `std::mbstate_t` です。次のように別名が決まっています。

| 別名 | 元の型 |
| --- | --- |
| `streampos` | `fpos<mbstate_t>` |
| `wstreampos` | `fpos<mbstate_t>` |
| `u8streampos`・`u16streampos`・`u32streampos` | `fpos<mbstate_t>` |

主な操作は、次のとおりです。

| 操作 | 意味 |
| --- | --- |
| `fpos(streamoff)` | 数値から作る |
| `operator streamoff()` | 位置の数値を取り出す |
| `p + off`・`p - off` | ずらした位置を返す |
| `p2 - p1` | 2 つの位置の差（`streamoff`）を返す |
| `==`・`!=` | 位置が等しいかを比べる |

比較は等しいかどうかだけで、大小の比較（`<` など）は、位置の数値を取り出してから行います。

## 実際に動かしてみる

```cpp
#include <ios>
#include <print>

int main() {
  std::streampos a = 10;
  std::streampos b = a + std::streamoff(5);
  std::streamoff d = b - a;

  std::println("{} {} {}", static_cast<long long>(std::streamoff(a)),
               static_cast<long long>(std::streamoff(b)), static_cast<long long>(d));
  std::println("{}", a == std::streampos(10));
  std::println("{}", std::streamoff(a) < std::streamoff(b));
}
```

```text title="実行結果"
10 15 5
true
true
```

`a` は 10、`b` は `a` を 5 だけ進めた 15、2 つの差は `streamoff` の 5 です。足す値は `std::streamoff(5)` のように型を明示します。`int` のまま渡すと、`fpos` を作る変換と `streamoff` に直す変換が両方成り立ち、どちらの `+` か決まらずに、コンパイル エラー（`C2666`）になります。比較は、等しいかどうかを直接比べられ、大小は `streamoff` に変換してから比べています。

## ゲームでの使いどころ

直接 `fpos` を書くことは、ほとんどありません。`tellg()` が返した値を、そのまま `seekg()` に渡す、という使い方で十分です。

位置から位置までの長さ（読んだバイト数）を測りたいときに、引き算で `streamoff` が出てくる、という覚え方で足ります。

## よくあるミス

??? failure "`streampos` を数値で作って、`seekg` に渡したら、戻れなかった"
    ファイルの文字コードの変換が絡むストリームでは、数値だけでは状態が足りないことがあります。`tellg()` が返した値を、そのまま使います。

??? failure "`<` で比べようとしたら、コンパイル エラーになった"
    `fpos` は、等しいかどうか（`==`、`!=`）しか比べられません。大小は、`std::streamoff(p)` に変換してから比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`streampos`](streampos.md) | `fpos<mbstate_t>` の別名。ふつうはこちらを使う |
| [`streamoff`](streamoff.md) | 位置のずれを表す整数型 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fpos` は、位置の数値と変換の状態をまとめて持つクラス テンプレート
    - [x] `streampos` は、その別名。`tellg()` が返す
    - [x] 引き算で `streamoff` が出る。大小の比較は、`streamoff` に変換してから

## 関連ページ

- [cpprefjp: std::fpos](https://cpprefjp.github.io/reference/ios/fpos.html)
- [cppreference: std::fpos](https://en.cppreference.com/w/cpp/io/fpos)
