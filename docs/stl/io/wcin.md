---
title: std::wcin
summary: "`wchar_t` の標準入力。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wcin` は、標準入力から `wchar_t` で読む入力ストリームです。`std::cin` の `wchar_t` 版で、`std::wstring` や `wchar_t` を読み込めます。Windows の API が UTF-16（`wchar_t`）で文字列を扱うので、その文字列をそのまま受け取りたいときに出てきます。

!!! tip "ポイント"
    - `cin` の `wchar_t` 版。`>>` で `std::wstring` や数を読める
    - 標準入力は同じなので、`cin` と混ぜて使うと混乱する。どちらかに統一する
    - `wcout` と結び付いていて、読む前に `wcout` の出力が送り出される
    - ゲームの文字列は UTF-8 の `char` で持つことが多く、`wcin` を使う場面は少ない

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wcin {#wcin}

```cpp
extern std::wistream wcin;
```

`<iostream>` を読み込むと使える、グローバルな入力ストリームです。標準入力（C の `stdin`）から、文字を `wchar_t` に変換しながら読み込みます。変換は、ストリームのロケールに従います。

使い方は `cin` と同じです。違いは、文字の型だけです。

| 読み込む型 | `cin` | `wcin` |
| --- | --- | --- |
| 文字 | `char` | `wchar_t` |
| 文字列 | `std::string` | `std::wstring` |
| 1 行 | `std::getline(std::cin, s)` | `std::getline(std::wcin, ws)` |

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <string>

int main() {
  // 入力元を差し替えて、決まった入力を読ませる
  std::wistringstream src(L"hp 120");
  auto* old = std::wcin.rdbuf(src.rdbuf());

  std::wstring key;
  int value = 0;
  std::wcin >> key >> value;

  std::wcin.rdbuf(old);
  std::println("key の長さ={} value={}", key.size(), value);
}
```

```text title="実行結果"
key の長さ=2 value=120
```

標準入力から読むプログラムの動作を、毎回手で入力せずに確かめたいときは、この例のように、`rdbuf` で入力元を `wistringstream` に差し替えます。差し替えたら、`old` に戻すことを忘れないでください。

## ゲームでの使いどころ

ゲーム本体で `wcin` を使う場面は、ほとんどありません。標準入力から読むのは、開発用のコンソール ツールや、デバッグ用のコマンド入力くらいで、その場合も `char` と UTF-8 を使うほうが、他の処理と合わせやすいです。

Windows の API が返す `wchar_t` の文字列（ファイル名、環境変数）を扱うプログラムで、ユーザーの入力も同じ型で受けたいときに、`wcin` の出番があります。

## よくあるミス

??? failure "`cin` と `wcin` を混ぜて読んだら、入力が欠けた"
    どちらも同じ標準入力を読みますが、先読みの仕組みが別です。1 つのプログラムの中では、どちらか一方に統一します。

??? failure "日本語の入力が、文字化けする"
    コンソールのコード ページと、ストリームのロケールが合っていません。ロケールの設定は環境で変わるので、UTF-8 の `char` で扱うほうが、安定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cin`](cin.md) | `char` 版 |
| [`wcout`](wcout.md) | `wchar_t` の標準出力 |
| [`istringstream`](istringstream.md) | 文字列から読むストリーム（`wchar_t` 版は `wistringstream`）。差し替えで使う |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcin` は、`cin` の `wchar_t` 版。`wstring` を読み込める
    - [x] `cin` と混ぜない。ゲームの文字列は UTF-8 の `char` で持つほうが扱いやすい
    - [x] テストでは `rdbuf` で入力元を差し替えると、入力を固定できる

## 関連ページ

- [cpprefjp: std::wcin](https://cpprefjp.github.io/reference/iostream/wcin.html)
- [cppreference: std::wcin](https://en.cppreference.com/w/cpp/io/wcin)
