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

`std::signal` は、**シグナル（Ctrl+C の `SIGINT`、終了要求の `SIGTERM`、異常の `SIGSEGV` など）を受け取ったときに呼ばれる関数を登録する**関数です。Ctrl+C で後片付けしてから終了する、といった処理に使います。**ハンドラーの中でできることは非常に限られる**（フラグを立てるだけにする）点に注意します。

!!! tip "ポイント"
    - ハンドラーでは、`volatile std::sig_atomic_t` のフラグを立てるだけにする。
    - `std::raise(SIGINT)` で、自分でシグナルを発生させられる。
    - ハンドラーの中で `println` や `new` を呼ぶのは危険。

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
  std::println("受信 {}", g_received);
}
```

```text title="実行結果"
受信 1
```

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
