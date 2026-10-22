---
title: std::sig_atomic_t
summary: "シグナルハンドラの中で、安全に読み書きできる整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::sig_atomic_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csignal>`
</div>

シグナルハンドラは、プログラムの途中に割り込んで呼ばれます。そのため、ふつうの変数の書き換えは、読み書きの途中で割り込まれて壊れるかもしれません。`sig_atomic_t` は、1 回の操作で読み書きが済むと保証された整数型で、ハンドラとメインの間のフラグに使います。

!!! tip "ポイント"
    - `volatile std::sig_atomic_t` として宣言する。
    - ハンドラの中で書き換えてよい数少ない型。
    - スレッド間の同期には使えない（`atomic` を使う）。

!!! info "このページを読む前に"
    [`<csignal>`](csignal.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sig_atomic_t {#sig_atomic_t}

```cpp
using sig_atomic_t = /* 整数型 */;
```

- 戻り値: なし（型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <csignal>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_integral_v<std::sig_atomic_t>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Ctrl+C で終了フラグを立てる |

## よくあるミス

??? failure "スレッド間の通信に使う"
    スレッド間には `std::atomic` を使います。`sig_atomic_t` は割り込み専用です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`raise`](raise.md) | シグナルを送る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シグナルハンドラの中で、安全に読み書きできる整数型
    - [x] `volatile std::sig_atomic_t` として宣言する
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sig_atomic_t](https://cpprefjp.github.io/reference/csignal/sig_atomic_t.html)
- [cppreference: std::sig_atomic_t](https://en.cppreference.com/w/cpp/utility/program/sig_atomic_t)
