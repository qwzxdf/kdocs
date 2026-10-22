---
title: std::raise
summary: "自分自身にシグナルを送る。"
order: 900
tags:
  - 入出力・文字列
---

# std::raise

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csignal>`
</div>

シグナル処理をテストしたいとき、本当に `Ctrl+C` を押さなくても、`raise(SIGINT)` で自分自身にシグナルを送れます。`signal` で登録したハンドラが呼ばれます。

!!! tip "ポイント"
    - `signal` で登録したハンドラが呼ばれる。
    - ハンドラの中では、限られた操作しかできない。
    - `sig_atomic_t` の変数を書き換えるのが定番。

!!! info "このページを読む前に"
    [`<csignal>`](csignal.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::raise {#raise}

```cpp
int raise(int sig);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `sig` | int | 送るシグナル（`SIGINT` など） |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <csignal>
#include <print>

volatile std::sig_atomic_t got = 0;
void Handler(int) { got = 1; }

int main() {
  std::signal(SIGINT, Handler);
  std::raise(SIGINT);
  std::println("{}", got);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Ctrl+C のハンドラのテスト |

## よくあるミス

??? failure "ハンドラで色々な処理をする"
    ハンドラの中でできる操作は限られます。フラグを立てて、メインループで処理します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`signal`](csignal.md) | ハンドラを登録する |
| [`sig_atomic_t`](sig_atomic_t.md) | ハンドラで使える整数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自分自身にシグナルを送る
    - [x] `signal` で登録したハンドラが呼ばれる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::raise](https://cpprefjp.github.io/reference/csignal/raise.html)
- [cppreference: std::raise](https://en.cppreference.com/w/cpp/utility/program/raise)
