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

`std::quick_exit` で終了するときに実行したい後始末を登録するのが、`std::at_quick_exit` です。`atexit` の `quick_exit` 版で、登録した関数は `quick_exit` のときだけ呼ばれます。

!!! tip "ポイント"
    - `std::at_quick_exit(func)` で `quick_exit` 時の関数を登録する
    - 登録の逆順に呼ばれる
    - `exit` や `main` からの戻りでは呼ばれない
    - 成功すれば 0 を返す

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::at_quick_exit {#at_quick_exit}

<span class="ver ver-11">C++11</span>

```cpp
int at_quick_exit(void (*func)()) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `func` | 関数ポインタ | `quick_exit` のときに呼ぶ関数 |

`func` を `quick_exit` 時の処理として登録します。登録できれば 0、できなければ 0 以外を返します。少なくとも 32 個まで登録できます。

`atexit` で登録した関数とは別の一覧です。通常の終了と、素早い終了で、実行する後始末を分けられます。

登録した関数の中で例外を投げ、外に出すと `std::terminate` が呼ばれます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

void Handler() { std::println("後始末"); }

int main() {
  const int result = std::at_quick_exit(Handler);
  std::println("登録の戻り値 = {}", result);
}
```

```text title="実行結果"
登録の戻り値 = 0
```

## ゲームでの使いどころ

`quick_exit` で終了する設計のプログラムが、必要最小限の保存処理を登録するときに使います。ほとんどのゲームでは `exit` か `main` の戻りで足りるため、使う機会はまれです。

## よくあるミス

??? failure "`exit` のときにも呼ばれると思う"
    `quick_exit` のときだけ呼ばれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atexit`](atexit.md) | `exit` 用の登録 |
| [`quick_exit`](quick_exit.md) | 素早く終了する |

## コンパイラ対応

C++11 から使えます。`<cstdlib>` で宣言されます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `at_quick_exit(func)` は `quick_exit` 用の関数を登録する
    - [x] 逆順に呼ばれる
    - [x] `exit` では呼ばれない

## 関連ページ

- [cpprefjp: std::at_quick_exit](https://cpprefjp.github.io/reference/cstdlib/at_quick_exit.html)
- [cppreference: std::at_quick_exit](https://en.cppreference.com/w/cpp/c/at_quick_exit)
