---
title: std::wcout
summary: "`wchar_t` の標準出力。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcout

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wcout` は、標準出力に `wchar_t` で書き込む出力ストリームです。`std::cout` の `wchar_t` 版で、`std::wstring` や `L"..."` の文字列リテラルをそのまま出せます。Windows の API が返す UTF-16 の文字列を、そのまま画面に出したいときに登場します。

!!! tip "ポイント"
    - `cout` の `wchar_t` 版。`L"..."` や `std::wstring` を出力できる
    - 標準出力は同じなので、`cout` と混ぜて使うと混乱する。どちらかに統一する
    - ASCII 以外の文字（日本語など）は、コンソールの設定とロケールで結果が変わる
    - ゲームでは、UTF-8 の `char` と `std::println` のほうが扱いやすい

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wcout {#wcout}

```cpp
extern std::wostream wcout;
```

`<iostream>` を読み込むと使える、グローバルな出力ストリームです。出力先は、C の `stdout` で、`cout` と同じです。書き込んだ `wchar_t` を、ストリームのロケールに従って、`char` の並びに変換してから出力します。

`cout` と同じ操作子（`hex`、`setw`、`endl` など）が使えます。`wcout` の `endl` は、`L'\n'` を書いて送り出します。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  // 出力先を差し替えて、書いた内容を取り出す
  std::wostringstream sink;
  auto* old = std::wcout.rdbuf(sink.rdbuf());
  std::wcout << L"score=" << 42 << L'\n';
  std::wcout.rdbuf(old);

  std::println("wcout に書いた文字数: {}", sink.str().size());
  std::println("内容が一致: {}", sink.str() == L"score=42\n");
}
```

```text title="実行結果"
wcout に書いた文字数: 9
内容が一致: true
```

`wcout` に書いた `score=42` と改行の 9 文字が、`wostringstream` に溜まっています。画面への出力そのものは、コンソールの設定に左右されるので、動作の確認には、この差し替えが確実です。

## ゲームでの使いどころ

ゲーム本体で `wcout` を使う場面は少ないです。Windows の API が返す `wchar_t` の文字列を、デバッグ用にコンソールへ出す程度です。

日本語を出す場合は、コンソールのコード ページとロケールの設定が必要で、環境ごとに結果が変わります。新しく書くコードでは、UTF-8 の `char` の文字列と `std::println` を使うほうが、短く、安定して書けます。

## よくあるミス

??? failure "`cout` と `wcout` を混ぜたら、出力が欠けたり、壊れたりした"
    どちらも同じ標準出力に書きますが、C の `stdout` の「向き」（文字か、ワイド文字か）が、処理系によって固定されることがあります。1 つのプログラムの中では、どちらか一方に統一します。

??? failure "日本語が `?` になる、または出ない"
    ストリームのロケールが `"C"` のままで、変換できる範囲が ASCII だけです。ロケールを設定するか、`wcout` をやめて UTF-8 の `char` で出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cout`](cout.md) | `char` 版 |
| [`wcerr`](wcerr.md)・[`wclog`](wclog.md) | `wchar_t` の標準エラー出力 |
| [`println`](../utilities/print.md) | 新しい書き方。UTF-8 の文字列を扱える |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcout` は、`cout` の `wchar_t` 版。`L"..."` や `wstring` を出力できる
    - [x] `cout` と混ぜない。ASCII 以外の出力は、環境の設定で結果が変わる
    - [x] テストでは `rdbuf` で出力先を差し替えると、内容を確かめられる

## 関連ページ

- [cpprefjp: std::wcout](https://cpprefjp.github.io/reference/iostream/wcout.html)
- [cppreference: std::wcout](https://en.cppreference.com/w/cpp/io/wcout)
