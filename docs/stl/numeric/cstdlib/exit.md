---
title: std::exit
summary: "プログラムを終了する（後片付けをしてから）。"
order: 5
group: <cstdlib> の関数
tags:
  - 数値
---

# std::exit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::exit(コード)` は、**プログラムを終了する**関数です。`atexit` で登録した関数や、グローバル変数のデストラクターを呼んでから終わります。ローカル変数のデストラクターは呼ばれない点に注意します。異常終了で後片付けしないのは `abort` です。

!!! tip "ポイント"
    - `std::atexit` で終了時の処理を登録できる。
    - **ローカル変数のデストラクターは呼ばれない**。普通は `main` から `return` する。
    - 戻り値 0 が正常終了。

## 関数の詳しい説明

### std::exit {#exit}

```cpp
[[noreturn]] void exit(int status);
int atexit(void (*func)());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `status` | `int` | 終了コード（0 が正常） |

- 戻り値: 戻らない
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::atexit([] { std::println("終了処理"); });
  std::exit(0);
}
```

```text title="実行結果"
終了処理
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 致命的なエラーでの強制終了 | `std::exit(1)` |

## よくあるミス

??? failure "ローカル変数の後片付けを期待する"
    呼ばれません。`RAII` の後片付けが飛びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abort`](abort.md) | 後片付けなしで異常終了 |
| [`std::terminate`](../../support/exceptions/terminate.md) | 例外絡みの終了 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プログラムを終了する
    - [x] ローカルのデストラクターは呼ばれない
    - [x] atexit で後処理

## 関連ページ

- [cpprefjp: std::exit](https://cpprefjp.github.io/reference/cstdlib/exit.html)
- [cppreference: std::exit](https://en.cppreference.com/w/cpp/utility/program/exit)
