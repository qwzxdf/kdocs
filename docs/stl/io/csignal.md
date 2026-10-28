---
title: std::signal
summary: "Ctrl+C やクラッシュ（シグナル）を受け取る関数を登録する。"
order: 98
tags:
  - 入出力・文字列
---

# std::signal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <csignal>`
</div>

`std::signal` は、**シグナル（Ctrl+C の `SIGINT`、終了要求の `SIGTERM`、異常の `SIGSEGV` など）を受け取ったときに呼ばれる関数を登録する**関数です。Ctrl+C で後片付けしてから終了する、といった処理に使います。**ハンドラーの中でできることは限られる**（フラグを立てるだけにする）点に注意します。

!!! tip "ポイント"
    - ハンドラーでは、`volatile std::sig_atomic_t` のフラグを立てるだけにする。
    - `std::raise(SIGINT)` で、自分でシグナルを発生させられる。
    - ハンドラーの中で `println` や `new` を呼ぶのは危険。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::signal {#csignal}

```cpp
using signal_handler = void (*)(int);
signal_handler signal(int sig, signal_handler handler);
int raise(int sig);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `sig` | `int` | シグナルの番号（`SIGINT` など） |
| `handler` | 関数 | 受け取ったときに呼ぶ関数 |

- 戻り値: 前のハンドラー
- 計算量: O(1)

```cpp
#include <csignal>
#include <print>

volatile std::sig_atomic_t g_received = 0;

void OnSignal(int) {
  g_received = 1;   // フラグを立てるだけにする
}

int main() {
  std::signal(SIGINT, OnSignal);
  std::raise(SIGINT);                  // 自分でシグナルを発生させる
  std::println("受信 {}", static_cast<int>(g_received));   // volatile のままでは format できない
}
```

```text title="実行結果"
受信 1
```

### SIGINT {#SIGINT}

```cpp
#define SIGINT /* 実装定義の整数 */
```

- 戻り値: 割り込み（`Ctrl+C`）を表すシグナル番号のマクロ
- 計算量: なし

`SIGINT` は、割り込み（`Ctrl+C`）を表すシグナルの番号です。`std::signal(SIGINT, handler)` で、ハンドラを登録します。

### SIGTERM {#SIGTERM}

```cpp
#define SIGTERM /* 実装定義の整数 */
```

- 戻り値: 終了要求を表すシグナル番号のマクロ
- 計算量: なし

`SIGTERM` は、終了要求を表すシグナルの番号です。`std::signal(SIGTERM, handler)` で、ハンドラを登録します。

### SIGSEGV {#SIGSEGV}

```cpp
#define SIGSEGV /* 実装定義の整数 */
```

- 戻り値: 不正なメモリアクセス（セグメンテーション違反）を表すシグナル番号のマクロ
- 計算量: なし

`SIGSEGV` は、不正なメモリアクセス（セグメンテーション違反）を表すシグナルの番号です。`std::signal(SIGSEGV, handler)` で、ハンドラを登録します。ハンドラから戻った後の動作は未定義なので、通常は終了処理だけを行います。

### SIGABRT {#SIGABRT}

```cpp
#define SIGABRT /* 実装定義の整数 */
```

- 戻り値: 異常終了（`abort()`）を表すシグナル番号のマクロ
- 計算量: なし

`SIGABRT` は、異常終了（`abort()`）を表すシグナルの番号です。`std::signal(SIGABRT, handler)` で、ハンドラを登録します。

### SIGFPE {#SIGFPE}

```cpp
#define SIGFPE /* 実装定義の整数 */
```

- 戻り値: 算術エラー（0 での整数除算など）を表すシグナル番号のマクロ
- 計算量: なし

`SIGFPE` は、算術エラー（0 での整数除算など）を表すシグナルの番号です。`std::signal(SIGFPE, handler)` で、ハンドラを登録します。ハンドラから戻った後の動作は未定義なので、通常は終了処理だけを行います。

### SIGILL {#SIGILL}

```cpp
#define SIGILL /* 実装定義の整数 */
```

- 戻り値: 不正な命令を表すシグナル番号のマクロ
- 計算量: なし

`SIGILL` は、不正な命令を表すシグナルの番号です。`std::signal(SIGILL, handler)` で、ハンドラを登録します。ハンドラから戻った後の動作は未定義なので、通常は終了処理だけを行います。

### SIG_DFL {#SIG_DFL}

```cpp
#define SIG_DFL /* 実装定義 */
```

- 戻り値: 既定の動作に戻すための特別なハンドラの値
- 計算量: なし

`SIG_DFL` は、既定の動作に戻すための値です。

### SIG_IGN {#SIG_IGN}

```cpp
#define SIG_IGN /* 実装定義 */
```

- 戻り値: シグナルを無視するための特別なハンドラの値
- 計算量: なし

`SIG_IGN` は、シグナルを無視するための値です。

### SIG_ERR {#SIG_ERR}

```cpp
#define SIG_ERR /* 実装定義 */
```

- 戻り値: `signal` が失敗したときの戻り値ための特別なハンドラの値
- 計算量: なし

`SIG_ERR` は、`signal` が失敗したときの戻り値ための値です。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Ctrl+C でセーブしてから終了する | フラグを見て、メインループで後片付け |

## よくあるミス

??? failure "ハンドラーで重い処理をする"
    ヒープの確保やファイル出力は、シグナルの途中では危険です。フラグを立てるだけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::atomic`](../concurrency/atomic.md) | スレッド間のフラグ |
| [`std::terminate`](../support/exceptions/terminate.md) | 例外絡みの終了 |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シグナルを受け取る関数を登録
    - [x] ハンドラーはフラグを立てるだけ
    - [x] `sig_atomic_t` を使う

## 関連ページ

- [cpprefjp: std::signal](https://cpprefjp.github.io/reference/csignal/signal.html)
- [cppreference: std::signal](https://en.cppreference.com/w/cpp/utility/program/signal)
