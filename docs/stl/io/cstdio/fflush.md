---
title: std::fflush
summary: "出力バッファの内容を、いまファイルに書き出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::fflush

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

出力はバッファに貯められて、まとめて書き出されます。`fflush` を呼ぶと、貯まっているぶんをいまこの時点で書き出します。クラッシュ前にログを確実に残したいときに使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fflush {#fflush}

```cpp
int fflush(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 書き出すファイル。`nullptr` なら開いている出力ファイル全部 |

- 戻り値: 成功なら 0、失敗なら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::fputs("hello\n", stdout);
  std::println("{}", std::fflush(stdout));
}
```

```text title="実行結果"
hello
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | クラッシュしても残したいログを書き出す |

## よくあるミス

??? failure "入力ストリームに使う"
    入力ストリームへの `fflush` は未定義動作です（入力を捨てる用途には使えません）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::flush`](../flush.md) | C++ のフラッシュ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力バッファの内容をいまファイルに書き出す
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fflush](https://cpprefjp.github.io/reference/cstdio/fflush.html)
- [cppreference: std::fflush](https://en.cppreference.com/w/cpp/io/c/fflush)
