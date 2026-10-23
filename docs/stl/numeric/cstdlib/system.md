---
title: std::system
summary: "OS のコマンドを実行する。"
order: 900
tags:
  - 数値
---

# std::system

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

ゲームのツールから、別のコマンドを実行したい。ビルド、画像の変換、ファイルのコピー。`std::system` は、シェルのコマンドを 1 行で実行します。手軽ですが、危険が多い関数です。

!!! tip "ポイント"
    - `std::system("echo hello")` でコマンドを実行する
    - 戻り値は、コマンドの終了コード（環境による）
    - 文字列にユーザーの入力を混ぜない（コマンド注入の危険）
    - 本番のゲームでは使わない。ツールや開発用に限る

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::system {#system}

```cpp
int system(const char* command);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `command` | `const char*` | 実行するコマンド。`nullptr` を渡すと、シェルが使えるかを調べる |

`command` をシェル（Windows では `cmd.exe`、Linux では `sh`）に渡して実行し、終わるまで待ちます。戻り値は、コマンドの終了コードですが、値の意味は環境依存です。Windows では終了コードそのもの、Linux では待機状態にエンコードされた値になることがあります。

最も重要な注意は、安全性です。`command` に、ユーザーが入力した文字列やファイル名を混ぜると、`;` や `&` で別のコマンドを差し込まれる危険があります（コマンド注入）。外部の入力を含む場合は、使わないでください。

コンソールのウィンドウが一瞬現れることがあり、ゲームの本番では見栄えが悪いので、使いません。ゲーム内で別のプログラムを起動するなら、`CreateProcess`（Windows）のような API を使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  const int result = std::system("echo hello");
  std::println("戻り値 {}", result);
}
```

```text title="実行結果"
hello
戻り値 0
```

## ゲームでの使いどころ

開発用のツールで、外部コマンドを呼ぶときに使います。

```cpp
// アセットの変換ツールを呼ぶ（引数は固定の文字列だけ）
std::system("texconv.exe -f BC7_UNORM texture.png");
```

ユーザーの入力を連結してはいけません。

## よくあるミス

??? failure "ユーザーの入力を連結して、コマンド注入される"
    入力を含むコマンドには使いません。

??? failure "ゲームの本番で呼び、コンソールがちらつく"
    本番では OS の専用 API を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`getenv`](getenv.md) | 環境変数を取る |
| [`exit`](exit.md) | プログラムを終了する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `system(command)` はシェルのコマンドを実行して待つ
    - [x] 入力を連結するとコマンド注入の危険
    - [x] 開発ツール用。本番のゲームでは使わない

## 関連ページ

- [cpprefjp: std::system](https://cpprefjp.github.io/reference/cstdlib/system.html)
- [cppreference: std::system](https://en.cppreference.com/w/cpp/c/system)
