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

`std::exit` は、静的変数のデストラクターや `atexit` の関数を実行して終了します。後始末が多いと時間がかかり、他のスレッドが動いている最中だと、危険です。`std::quick_exit` は、<strong>後始末を最小限にして素早く終了</strong>します。

!!! tip "ポイント"
    - `std::quick_exit(status)` で素早く終了する
    - `at_quick_exit` で登録した関数だけを呼ぶ
    - `atexit` の関数と、静的変数のデストラクターは呼ばない
    - 標準入出力はフラッシュされないことがある

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::quick_exit {#quick_exit}

<span class="ver ver-11">C++11</span>

```cpp
[[noreturn]] void quick_exit(int status) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `status` | `int` | 終了コード。`EXIT_SUCCESS` か `EXIT_FAILURE` |

`at_quick_exit` で登録された関数を、登録の逆順に呼んで、プロセスを終了させます。`atexit` で登録した関数や、静的記憶域期間のオブジェクトのデストラクターは実行しません。

通常の `exit` では、他のスレッドがまだ動いている状態で静的変数が破棄され、そのスレッドが破棄済みのオブジェクトを触って不具合になることがあります。`quick_exit` はこの危険を避けられます。

標準入出力のバッファは、フラッシュされない場合があります。ログをファイルに残すなら、`quick_exit` の前に明示的にフラッシュします。

`abort` との違いは、異常終了のシグナルを出さず、登録した処理を実行できる点です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

void Handler() { std::println("quick_exit のハンドラ"); }

int main(int argc, char**) {
  std::at_quick_exit(Handler);          // quick_exit 用の関数を登録する
  if (argc > 1) {
    std::quick_exit(EXIT_SUCCESS);      // 引数があれば素早く終了（今回は実行されない）
  }
  std::println("quick_exit せずに終了");
}
```

```text title="実行結果"
quick_exit せずに終了
```

## ゲームでの使いどころ

他のスレッドが動いている最中に、安全にプロセスを終わらせたいときに使います。

```cpp
std::fflush(stdout);                    // ログは自分でフラッシュする
std::quick_exit(EXIT_FAILURE);
```

## よくあるミス

??? failure "`atexit` の後始末が実行されると期待する"
    `at_quick_exit` で登録した関数だけが呼ばれます。

??? failure "出力が切れる"
    標準出力を明示的にフラッシュします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exit`](exit.md) | 通常の後始末をして終了 |
| [`abort`](abort.md) | 異常終了 |
| [`at_quick_exit`](at_quick_exit.md) | `quick_exit` 用の関数を登録 |

## コンパイラ対応

C++11 から使えます。`<cstdlib>` で宣言されます。Visual Studio 2015 以降、GCC、Clang で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `quick_exit` は最小限の後始末で素早く終了する
    - [x] `at_quick_exit` の関数だけを呼ぶ
    - [x] 出力はフラッシュされない場合がある

## 関連ページ

- [cpprefjp: std::quick_exit](https://cpprefjp.github.io/reference/cstdlib/quick_exit.html)
- [cppreference: std::quick_exit](https://en.cppreference.com/w/cpp/c/quick_exit)
