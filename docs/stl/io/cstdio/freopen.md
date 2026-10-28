---
title: std::freopen
summary: "開いているファイル（stdout など）を、別のファイルに付け替える。"
order: 900
tags:
  - 入出力・文字列
---

# std::freopen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ゲームの `stdout` や `stderr` に出ているメッセージを、画面ではなく、ログ ファイルに保存したい。プログラムのあちこちの `printf` を書き換えずに、出力先だけを差し替える関数が `std::freopen` です。

<strong>すでにある `FILE*` を閉じて、別のファイルに開き直します</strong>。`stdout` のような標準ストリームの向きを変えるときの、定番です。

!!! tip "ポイント"
    - `freopen(パス, モード, ストリーム)`。戻り値は、成功ならそのストリーム、失敗は `nullptr`
    - `stdout`、`stderr`、`stdin` の出力先・入力元を、ファイルに変えられる
    - 元に戻すのは難しい（環境依存）。リダイレクトは起動時に 1 回だけにする
    - GUI アプリ（Windows のサブシステム `WINDOWS`）では、`stdout` が元々つながっていない

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::freopen {#freopen}

```cpp
std::FILE* freopen(const char* filename, const char* mode, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | 新しく開くファイルのパス。`nullptr` なら、同じファイルでモードだけ変える（環境による） |
| `mode` | `const char*` | 開き方。`fopen` と同じ |
| `stream` | `FILE*` | 開き直す対象。`stdout` などでもよい |

まず、`stream` で開いているファイルを閉じ、そのあと `filename` を `mode` で開いて、同じ `FILE*` に結び付けます。失敗すると、元のストリームは閉じられたままになるので、使い続けられません。戻り値の `nullptr` を確かめます。

`freopen("log.txt", "w", stdout)` を実行すると、その後の `printf` や `std::print`（`stdout` への出力）が、すべて `log.txt` に書かれます。個々の呼び出しを直さなくて済むのが利点です。

Windows の GUI アプリ（`WinMain` で始まるもの）では、コンソールが無いため、`stdout` が使えません。`AllocConsole` でコンソールを作り、`freopen("CONOUT$", "w", stdout)` でつなぎ直す、というデバッグ用の定番があります。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  // 標準エラー出力をファイルに向け直す
  std::FILE* r = std::freopen("err.log", "w", stderr);
  if (!r) return 1;

  std::fprintf(stderr, "警告: テクスチャがありません\n");   // 画面ではなくファイルに入る
  std::fflush(stderr);

  // ファイルに入ったか確かめる
  std::FILE* in = std::fopen("err.log", "r");
  char buf[64];
  std::fgets(buf, sizeof(buf), in);
  std::fclose(in);
  std::print("ログの中身: {}", buf);
}
```

```text title="実行結果"
ログの中身: 警告: テクスチャがありません
```

## ゲームでの使いどころ

ゲームの起動時に、`stdout` と `stderr` をログ ファイルに向けます。サードパーティのライブラリが `printf` で出すメッセージも、まとめてログに残せます。

Windows の GUI アプリでは、デバッグ用に、コンソールを開いて `freopen("CONOUT$", "w", stdout)` でつなぎます。製品版では外します。

## よくあるミス

??? failure "失敗しても続けて、閉じられた `stdout` に書いて落ちる"
    `nullptr` が返ったら、元のストリームは使えません。エラーを `stderr` 以外に伝える手段を用意します。

??? failure "途中で何度も向き先を変えようとして、混乱する"
    起動時に 1 回だけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fopen`](fopen.md) | 新しいファイルを開く |
| [`fclose`](fclose.md) | 閉じる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 既存のストリームを別のファイルに開き直す
    - [x] `stdout` の向き先を変えられる
    - [x] 失敗するとストリームは使えない

## 関連ページ

- [cpprefjp: std::freopen](https://cpprefjp.github.io/reference/cstdio/freopen.html)
- [cppreference: std::freopen](https://en.cppreference.com/w/cpp/io/c/freopen)
