---
title: std::atexit
summary: "プログラム終了時に呼ぶ関数を登録する。"
order: 900
tags:
  - 数値
---

# std::atexit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

プログラムの終了時に、必ず実行したい後始末がある。ログファイルを閉じる、一時ファイルを消す。`std::atexit` は、<strong>終了時に呼ぶ関数を登録</strong>しておく仕組みです。

!!! tip "ポイント"
    - `std::atexit(func)` で終了時の関数を登録する
    - 登録の逆順に呼ばれる（後入れ先出し）
    - `main` から `return` したときと、`exit` のときに呼ばれる
    - `abort` のときは呼ばれない

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atexit {#atexit}

```cpp
int atexit(void (*func)());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `func` | 関数ポインタ | 終了時に呼ぶ関数。引数も戻り値もない |

`func` を終了時の処理として登録します。登録できれば 0、できなければ 0 以外を返します。少なくとも 32 個まで登録できます。

実行の順序は、登録の逆です。後で登録した関数が先に呼ばれます。これは、依存関係のある後始末に都合がよい決まりです。

`main` から戻るとき、または `std::exit` が呼ばれたときに実行されます。`std::abort` や `std::quick_exit` では実行されません。

関数の中で例外を投げ、外に出すと `std::terminate` になります。また、引数を渡せないので、後始末に必要な情報はグローバル変数や静的変数に持たせます。C++ では、後始末は RAII のデストラクターで書くほうが安全です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

void First() { std::println("1 番目に登録"); }
void Second() { std::println("2 番目に登録"); }

int main() {
  std::atexit(First);
  std::atexit(Second);
  std::println("main の終わり");
}
```

```text title="実行結果"
main の終わり
2 番目に登録
1 番目に登録
```

## ゲームでの使いどころ

グローバルな資源（ログ ファイルなど）の後始末を、終了時に行うために使います。

```cpp
std::atexit([] { FlushLogFile(); });   // キャプチャなしのラムダは関数ポインタにできる
```

C++ では、静的なオブジェクトのデストラクターで後始末をするほうが一般的です。

## よくあるミス

??? failure "呼ばれる順序を登録順と思う"
    逆順（後入れ先出し）です。

??? failure "関数の中から例外を外に出す"
    `std::terminate` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`at_quick_exit`](at_quick_exit.md) | `quick_exit` 用の登録 |
| [`exit`](exit.md) | プログラムを終了する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `atexit(func)` は終了時に呼ぶ関数を登録する
    - [x] 登録の逆順に呼ばれる
    - [x] `abort` のときは呼ばれない

## 関連ページ

- [cpprefjp: std::atexit](https://cpprefjp.github.io/reference/cstdlib/atexit.html)
- [cppreference: std::atexit](https://en.cppreference.com/w/cpp/c/atexit)
