---
title: std::wcerr
summary: "`wchar_t` の標準エラー出力。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcerr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wcerr` は、`cerr` の `wchar_t` 版です。標準エラー出力に出る点、書くたびに送り出される点は、`cerr` と同じです。Windows の API が返す `wchar_t` のエラー メッセージを、そのまま標準エラー出力に出したいときに使います。

!!! tip "ポイント"
    - 標準エラー出力に出る `wchar_t` のストリーム
    - 最初から `unitbuf` がオンで、`wcout` と結び付いている
    - `cerr` と混ぜて使うと混乱する。どちらかに統一する
    - ゲームでは、UTF-8 の `char` と `std::println(stderr, ...)` のほうが扱いやすい

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wcerr {#wcerr}

```cpp
extern std::wostream wcerr;
```

`<iostream>` を読み込むと使える、グローバルなストリームです。出力先は C の `stderr` で、`cerr` と同じです。`cerr` と同じく、次の設定になっています。

- `unitbuf` がオンで、`<<` のたびに送り出される（[`unitbuf`](unitbuf.md)）。
- `tie()` が `&wcout` を返す。`wcerr` に書く前に、`wcout` の溜まった出力が送り出される。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::println("wcerr: unitbuf={} tie==&wcout:{}",
               (std::wcerr.flags() & std::ios::unitbuf) != 0, std::wcerr.tie() == &std::wcout);

  // 出力先を差し替えて、書いた内容を取り出す
  std::wostringstream sink;
  auto* old = std::wcerr.rdbuf(sink.rdbuf());
  std::wcerr << L"fail " << 3 << L'\n';
  std::wcerr.rdbuf(old);
  std::println("wcerr に書いた文字数: {}", sink.str().size());
}
```

```text title="実行結果"
wcerr: unitbuf=true tie==&wcout:true
wcerr に書いた文字数: 7
```

`wcerr` は、`unitbuf` がオンで、`wcout` と結び付いています。`cerr` が `cout` と結び付いているのと同じ関係です。2 行目は、出力先を差し替えて、`fail 3` と改行の 7 文字が書かれたことを確かめています。

## ゲームでの使いどころ

Windows の API の失敗を知らせるメッセージ（`FormatMessageW` が返す文字列など）が `wchar_t` で、それを標準エラー出力に出したいときです。

その場合も、メッセージを UTF-8 に変換して、`cerr` か `std::println(stderr, ...)` に出すほうが、他のログと形式をそろえられます。

## よくあるミス

??? failure "`cerr` と `wcerr` を混ぜたら、出力が欠けた"
    同じ標準エラー出力に、`char` と `wchar_t` の向きが違う出力を混ぜると、処理系によって、片方が捨てられます。どちらか一方に統一します。

??? failure "日本語のメッセージが、文字化けする"
    ストリームのロケールとコンソールの設定が合っていません。環境で変わるので、UTF-8 の `char` で出すほうが安定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cerr`](cerr.md) | `char` 版 |
| [`wclog`](wclog.md) | 同じ出力先で、バッファあり |
| [`wcout`](wcout.md) | `wchar_t` の標準出力 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcerr` は、`cerr` の `wchar_t` 版。標準エラー出力に、書くたびに送り出す
    - [x] `unitbuf` がオンで、`wcout` と結び付いている
    - [x] `cerr` と混ぜない。新しいコードは UTF-8 の `char` が扱いやすい

## 関連ページ

- [cpprefjp: std::wcerr](https://cpprefjp.github.io/reference/iostream/wcerr.html)
- [cppreference: std::wcerr](https://en.cppreference.com/w/cpp/io/wcerr)
