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

`std::cerr` は、**標準エラー出力**に出すストリームです。通常の出力（`cout`）とは別のストリームで、**バッファなしですぐに出ます**。エラーメッセージやログを出すときに使います。`std::clog` は同じ出力先ですが、バッファありです。

!!! tip "ポイント"
    - エラーは `cerr`、通常の出力は `cout` と分けると、リダイレクトで別々に保存できる。
    - 新しいコードでは `std::println(stderr, "...")` も使える。
    - `cerr` は `cout` と結び付いていて、`cerr` に出す前に `cout` が `flush` される。

## 関数の詳しい説明

### std::cerr {#cerr}

```cpp
extern std::ostream cerr;
```

- エラー用の出力。バッファにためずに**すぐ**出るので、落ちる直前のメッセージも残ります

### std::clog {#clog}

```cpp
extern std::ostream clog;
```

- ログ用の出力。cerr と同じ出力先ですが、バッファにためます

### std::wcerr {#wcerr}

```cpp
extern std::wostream wcerr;
```

- 戻り値: `wostream`（`wchar_t` の標準エラー出力）
- 計算量: 操作による

`wcerr` は、`cerr` の `wchar_t` 版です。`wchar_t` の文字列（`L"..."`）を扱うときに使います。1 つのプログラムで `cerr` と `wcerr` を混ぜて使うと、文字化けや動作不良の原因になることがあります。

### std::wclog {#wclog}

```cpp
extern std::wostream wclog;
```

- 戻り値: `wostream`（`wchar_t` のログ出力（バッファあり））
- 計算量: 操作による

`wclog` は、`clog` の `wchar_t` 版です。`wchar_t` の文字列（`L"..."`）を扱うときに使います。1 つのプログラムで `clog` と `wclog` を混ぜて使うと、文字化けや動作不良の原因になることがあります。

## 実際に動かしてみる

（標準エラー出力に出ます。コンソールでは通常の出力と同じように見えます）

```cpp
#include <iostream>

int main() {
  std::cerr << "error: 設定ファイルが見つからない\n";   // 標準エラー出力に出る
}
```

```text title="実行結果"
error: 設定ファイルが見つからない
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 起動時の致命的なエラーを出す | `std::cerr << "初期化に失敗\n";` |

## よくあるミス

??? failure "ログを cerr に出し続けて遅くなる"
    `cerr` はバッファなしで、1 回ごとに出力します。大量のログには `clog` や、ファイル出力を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cout`](cout.md) | 通常の出力 |
| [`std::println`](../utilities/print.md) | `println(stderr, ...)` でも出せる |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準エラー出力
    - [x] バッファなしですぐ出る
    - [x] エラーはこちらへ

## 関連ページ

- [cpprefjp: std::cerr](https://cpprefjp.github.io/reference/iostream/cerr.html)
- [cppreference: std::cerr](https://en.cppreference.com/w/cpp/io/cerr)
