---
title: std::cerr
summary: "標準エラー出力。エラーやログを出す（バッファなしで即座に出る）。"
order: 72
tags:
  - 入出力・文字列
---

# std::cerr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <iostream>`
</div>

エラーメッセージを `cout` に出すと、通常の出力と混ざります。ログをファイルにリダイレクトして保存したいときに、エラーだけを別に見たくても、分けられません。`std::cerr` は、標準エラー出力（stderr）に出るストリームで、通常の出力（stdout）と別の流れになります。さらに、1 回出力するたびにバッファを送り出すので、プログラムが落ちる直前のメッセージも残ります。

!!! tip "ポイント"
    - 標準エラー出力に出る。`program > out.txt` としても、画面に出る（`2> err.txt` で別に保存できる）
    - 最初から `unitbuf` がオンで、`<<` のたびにバッファを送り出す
    - `cout` と結び付いている（`tie`）。`cerr` に書く前に、`cout` の溜まった出力が先に送り出される
    - 大量のログを出すと遅い。通常のログには `clog` やファイルを使う

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::cerr {#cerr}

```cpp
extern std::ostream cerr;
```

`<iostream>` を読み込むと使える、標準ライブラリのグローバルなストリームです。プログラムの開始時に、C の `stderr` と結び付いた状態で用意されます。

`cerr` が `cout` と違うのは、設定の次の 2 点です。

- `unitbuf` がオンです（[`unitbuf`](unitbuf.md)）。`<<` の 1 回ごとに送り出されます。
- `tie()` が `&cout` を返します。`cerr` に出力しようとすると、その前に `cout.flush()` が呼ばれます。画面に出るメッセージの順番が、書いた順番とずれないための仕組みです。

`cout` と `clog` は、どちらも `unitbuf` がオフで、`tie` もありません。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  // cerr は最初から unitbuf がオンで、cout と結び付いている
  std::println("cerr: unitbuf={} tie==&cout:{}",
               (std::cerr.flags() & std::ios::unitbuf) != 0, std::cerr.tie() == &std::cout);
  std::println("cout: unitbuf={} tie={}",
               (std::cout.flags() & std::ios::unitbuf) != 0, std::cout.tie() != nullptr);
  std::println("clog: unitbuf={} tie={}",
               (std::clog.flags() & std::ios::unitbuf) != 0, std::clog.tie() != nullptr);

  // 出力先を差し替えて、書いた内容を取り出す（テストのときの定番）
  std::ostringstream captured;
  auto* old = std::cerr.rdbuf(captured.rdbuf());
  std::cerr << "error: 設定ファイルが見つからない\n";
  std::cerr.rdbuf(old);
  std::print("取り出した: {}", captured.str());
}
```

```text title="実行結果"
cerr: unitbuf=true tie==&cout:true
cout: unitbuf=false tie=false
clog: unitbuf=false tie=false
取り出した: error: 設定ファイルが見つからない
```

最初の 3 行は、3 つのストリームの設定の違いです。`cerr` だけが `unitbuf` がオンで、`cout` と結び付いています。

最後の 3 行は、`rdbuf` で出力先のバッファを差し替える方法です。`cerr` に書いたつもりの内容が、`ostringstream` に溜まります。エラーの出力を確かめるテストで使えます。差し替えたら、必ず元の `old` に戻してください。戻さないまま `captured` が破棄されると、`cerr` は存在しないバッファに書こうとして、プログラムが壊れます。

## ゲームでの使いどころ

起動時の致命的なエラー（DLL が見つからない、GPU が足りない）や、アサートの失敗メッセージを出すときです。落ちる直前に出したメッセージが、バッファの中に残って消えることがないので、原因の調査に使えます。

毎フレーム出すようなログには向きません。`cerr` は、書くたびに送り出すので、遅くなります。通常のログは、ファイルに溜めて書き、重大なエラーだけを `cerr` に書く、という使い分けが、速度を落とさずに済みます。新しいコードでは、`std::println(stderr, "...")` でも、同じ出力先に書けます。

## よくあるミス

??? failure "ログを `cerr` に出し続けて、動作が遅くなった"
    `cerr` は、書くたびにバッファを送り出します。大量のログには、バッファのある `clog` か、ファイル ストリームを使います。

??? failure "リダイレクトしたのに、エラーがファイルに入らない"
    `> out.txt` は、標準出力（`cout`）だけをファイルにします。`cerr` は別の流れなので、`2> err.txt` か、`> out.txt 2>&1`（両方を同じファイルに）と書きます。

??? failure "`rdbuf` で差し替えたあと、元に戻さずに落ちた"
    差し替えたバッファ（`ostringstream` の中身など）が、`cerr` より先に破棄されました。差し替える前の `rdbuf()` を保存しておき、使い終わったら必ず戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cout`](cout.md) | 通常の出力。`unitbuf` も `tie` もない |
| [`clog`](clog.md) | 同じ標準エラー出力に出るが、バッファあり（`unitbuf` がオフ） |
| [`wcerr`](wcerr.md) | `wchar_t` 版 |
| [`println`](../utilities/print.md) | `std::println(stderr, ...)` でも同じ出力先に出せる |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cerr` は、標準エラー出力に出るストリーム。通常の出力とは別の流れ
    - [x] `unitbuf` がオンで、`cout` と結び付いている。落ちる直前のメッセージも残る
    - [x] 毎回送り出すので、大量のログには向かない

## 関連ページ

- [cpprefjp: std::cerr](https://cpprefjp.github.io/reference/iostream/cerr.html)
- [cppreference: std::cerr](https://en.cppreference.com/w/cpp/io/cerr)
