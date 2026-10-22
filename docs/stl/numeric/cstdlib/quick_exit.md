---
title: std::quick_exit
summary: "後始末を最小限にして、プログラムを終了する。"
order: 900
tags:
  - 数値
---

# std::quick_exit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdlib>`
</div>

`exit` は、静的オブジェクトの破棄や `atexit` の関数をすべて実行するので、時間がかかり、デッドロックの危険もあります。`quick_exit` は、`at_quick_exit` で登録した関数だけを呼んで終了します。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::quick_exit {#quick_exit}

```cpp
[[noreturn]] void quick_exit(int exit_code);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `exit_code` | int | 終了コード |

- 戻り値: 戻らない
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
| 使いどころ | 異常時にすばやく終了する |

## よくあるミス

??? failure "通常の後始末を期待する"
    デストラクタは実行されません。ファイルバッファなども書き出されない場合があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exit`](exit.md) | 通常の終了 |
| [`abort`](abort.md) | 異常終了 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 後始末を最小限にして、プログラムを終了する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::quick_exit](https://cpprefjp.github.io/reference/cstdlib/quick_exit.html)
- [cppreference: std::quick_exit](https://en.cppreference.com/w/cpp/c/quick_exit)
