---
title: std::at_quick_exit
summary: "quick_exit() で終了するときに呼ぶ関数を登録する。"
order: 900
tags:
  - 数値
---

# std::at_quick_exit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdlib>`
</div>

`quick_exit` が呼ぶ後始末の関数を登録します。`atexit` の `quick_exit` 版です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::at_quick_exit {#at_quick_exit}

```cpp
int at_quick_exit(void (*func)());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `func` | 関数ポインタ | 終了時に呼ぶ関数 |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  // 例: std::at_quick_exit(Cleanup);  std::quick_exit(0);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | すばやい終了時の後始末 |

## よくあるミス

??? failure "`atexit` のつもりで登録する"
    `atexit` の関数は `quick_exit` では呼ばれません。別に登録します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`quick_exit`](quick_exit.md) | 終了する |
| [`atexit`](atexit.md) | 通常の終了時 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] quick_exit() で終了するときに呼ぶ関数を登録する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::at_quick_exit](https://cpprefjp.github.io/reference/cstdlib/at_quick_exit.html)
- [cppreference: std::at_quick_exit](https://en.cppreference.com/w/cpp/c/at_quick_exit)
