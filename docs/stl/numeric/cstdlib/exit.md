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

致命的なエラーで、プログラムを今すぐ終了したい。深い呼び出しの途中から `return` で戻る手間をかけずに、プロセスを終わらせるのが `std::exit` です。ただし、<strong>ローカル変数のデストラクターが呼ばれない</strong>ので、使うときは注意が要ります。

!!! tip "ポイント"
    - `std::exit(0)` または `std::exit(EXIT_SUCCESS)` で正常終了
    - `std::exit(EXIT_FAILURE)` で異常終了
    - `atexit` で登録した関数と、静的変数のデストラクターは呼ばれる
    - ローカル変数のデストラクターは呼ばれない

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exit {#exit}

```cpp
[[noreturn]] void exit(int status);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `status` | `int` | 終了コード。`EXIT_SUCCESS`（成功）か `EXIT_FAILURE`（失敗）が移植性がある |

プログラムを終了します。`atexit` で登録した関数を、登録の逆順に呼び、静的記憶域期間のオブジェクトのデストラクターを呼び、標準入出力をフラッシュしてから、`status` で終了します。戻ってくることはありません。

呼び出した関数のスタックの上にあるローカル変数のデストラクターは、<strong>呼ばれません</strong>。ファイルのクローズ、ミューテックスの解放、`unique_ptr` の解放など、RAII に頼った後始末が実行されないので、リソースが残ります。そのため、C++ では、`exit` よりも、例外を投げて `main` まで戻る、または `main` から `return` する書き方が好まれます。

`abort` との違いは、後始末が行われる点です。`quick_exit` は、さらに軽く終了します。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

void Cleanup() { std::println("後始末"); }

int main() {
  std::atexit(Cleanup);              // 終了時に呼ぶ関数を登録
  std::println("終了します");
  std::exit(EXIT_SUCCESS);           // Cleanup が呼ばれて終了
}
```

```text title="実行結果"
終了します
後始末
```

## ゲームでの使いどころ

致命的な設定エラーで、起動直後に終了するような単純なツールで使います。

```cpp
if (!LoadConfig()) {
  std::println(stderr, "設定を読めません");
  std::exit(EXIT_FAILURE);
}
```

ゲームの本体では、ウィンドウやデバイスの後始末がデストラクターで行われるため、`exit` ではなく、`main` に戻る形で終了させるのが安全です。

## よくあるミス

??? failure "RAII のオブジェクトの後始末が実行されない"
    `main` まで戻って終了させます。

??? failure "デストラクターの中から呼んで、デッドロックする"
    終了処理の中での `exit` は避けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abort`](abort.md) | 後始末なしで即座に異常終了 |
| [`quick_exit`](quick_exit.md) | 最小限の後始末で終了 |
| [`atexit`](atexit.md) | 終了時の関数を登録 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `exit(status)` は後始末をしてプロセスを終了する
    - [x] ローカル変数のデストラクターは呼ばれない
    - [x] `main` に戻る形のほうが安全

## 関連ページ

- [cpprefjp: std::exit](https://cpprefjp.github.io/reference/cstdlib/exit.html)
- [cppreference: std::exit](https://en.cppreference.com/w/cpp/utility/program/exit)
