---
title: std::wclog
summary: "`wchar_t` の標準ログ出力（バッファあり）。"
order: 900
tags:
  - 入出力・文字列
---

# std::wclog

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wclog` は、`clog` の `wchar_t` 版です。`wcerr` と同じ標準エラー出力に出ますが、バッファに溜めてから送り出します。`wchar_t` の診断ログを大量に出すときに使うストリームですが、ゲームで使う場面は多くありません。

!!! tip "ポイント"
    - 標準エラー出力に出る `wchar_t` のストリーム。バッファあり（`unitbuf` がオフ）
    - `wcerr` と違い、`wcout` と結び付いていない
    - 落ちる直前の出力は、残らないことがある
    - `clog` と混ぜて使わない。ゲームでは UTF-8 の `char` で統一するほうが扱いやすい

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wclog {#wclog}

```cpp
extern std::wostream wclog;
```

`<iostream>` を読み込むと使える、グローバルなストリームです。`clog` の `wchar_t` 版で、出力先は C の `stderr` です。

| | `wcout` | `wcerr` | `wclog` |
| --- | --- | --- | --- |
| 出力先 | 標準出力 | 標準エラー出力 | 標準エラー出力 |
| `unitbuf` | オフ | **オン** | オフ |
| `tie` | なし | `wcout` | なし |

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::println("wclog: unitbuf={} tie={}",
               (std::wclog.flags() & std::ios::unitbuf) != 0, std::wclog.tie() != nullptr);

  // 出力先を差し替えて、書いた内容を取り出す
  std::wostringstream sink;
  auto* old = std::wclog.rdbuf(sink.rdbuf());
  std::wclog << L"loaded " << 128 << L" assets\n";
  std::wclog.rdbuf(old);
  std::println("wclog に書いた文字数: {}", sink.str().size());
}
```

```text title="実行結果"
wclog: unitbuf=false tie=false
wclog に書いた文字数: 18
```

`unitbuf` も `tie` もなく、`wcout` と同じ設定です。出力先が標準エラー出力であることだけが、違いです。

## ゲームでの使いどころ

`wchar_t` の診断ログを標準エラー出力に出したい、小さな開発用のツールで使います。ゲーム本体では、ログは UTF-8 の `char` の文字列にそろえて、ファイルに書くのが普通です。

## よくあるミス

??? failure "落ちる直前のログが出ていない"
    `wclog` はバッファに溜めるので、落ちる前に送り出されませんでした。確実に残したい行は、`wcerr` に出すか、`std::flush` を流します。

??? failure "`clog` と混ぜて使ったら、出力が欠けた"
    同じ標準エラー出力に、向きの違う出力を混ぜると、処理系によっては片方が捨てられます。どちらか一方に統一します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clog`](clog.md) | `char` 版 |
| [`wcerr`](wcerr.md) | 同じ出力先で、書くたびに送り出す |
| [`wcout`](wcout.md) | `wchar_t` の標準出力 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wclog` は、`clog` の `wchar_t` 版。標準エラー出力に、バッファありで出す
    - [x] `unitbuf` も `tie` もない。確実に残したいものは `wcerr` か `flush`
    - [x] `clog` と混ぜない。ゲームでは UTF-8 の `char` が扱いやすい

## 関連ページ

- [cpprefjp: std::wclog](https://cpprefjp.github.io/reference/iostream/wclog.html)
- [cppreference: std::wclog](https://en.cppreference.com/w/cpp/io/wclog)
