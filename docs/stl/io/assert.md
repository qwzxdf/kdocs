---
title: assert
summary: "デバッグ中だけ「ここは必ず真」と確かめる。偽ならプログラムを止める。"
order: 96
tags:
  - 入出力・文字列
---

# assert

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <cassert>`
</div>

「この関数が呼ばれるとき、ポインターは必ず非ヌルのはず」という前提を、コードで書き残したい。前提が崩れたときに、すぐ気づければ、バグの原因を探す時間が減ります。`assert(条件)` は、条件が必ず真のはずと確かめるマクロです。偽だと、ファイル名、行番号、式を出して `abort` します。リリースビルド（`NDEBUG` 定義時）では、何も実行されません。

!!! tip "ポイント"
    - リリースでは消える。**条件の中に副作用のある式を書かない**（`assert(Init())` はリリースで初期化が消える）。
    - `static_assert` はコンパイル時の確認。
    - ユーザー入力の検証は、`assert` ではなくエラー処理で。

!!! info "このページを読む前に"
    プログラムのバグと、実行時のエラー（ファイルが無いなど）の違いが分かると読みやすいです。`assert` は、バグを検出するためのものです。

## 関数の詳しい説明

### assert {#assert}

```cpp
#define assert(condition) /* 実装定義 */
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `condition` | 式 | 真であるはずの条件 |

- 戻り値: （なし）。偽なら異常終了
- 計算量: O(1)

```cpp
#include <cassert>
#include <print>

int main() {
  int hp = 10;
  assert(hp >= 0 && "HP は 0 以上のはず");   // 文字列を足すとメッセージになる
  std::println("OK");
}
```

```text title="実行結果"
OK
```

### NDEBUG {#NDEBUG}

```cpp
#define NDEBUG
```

- 戻り値: `assert` を無効にするマクロ
- 計算量: なし

`#include <cassert>` の前に `NDEBUG` が定義されていると、`assert(...)` は何もしなくなります。リリースビルドでは、通常これが定義されます（`-DNDEBUG`）。`assert` の中に副作用のある式を書くと、リリースで消えるので、注意します。

### static_assert {#static_assert}

```cpp
static_assert(constant-expression, message);
```

- 戻り値: コンパイル時に条件を検査するキーワード
- 計算量: コンパイル時

実行時ではなく、**コンパイル時**に条件を検査します。条件が偽なら、コンパイルエラーになり、`message` が表示されます。型のサイズやテンプレートの前提の確認に使います。C++17 からは、`message` を省略できます。

## ゲームでの使いどころ

配列の添え字の範囲、ポインターの非ヌル、状態の整合性など、プログラマーの前提を確かめるのに使います。デバッグビルドで落ちるので、開発中にバグが見つかります。

条件の中に副作用のある式を書いてはいけません。`assert(Init())` と書くと、リリースビルドで `Init()` ごと消え、初期化が行われません。

ユーザーの入力やファイルの内容の検証には使いません。それらはエラー処理で扱います。コンパイル時に確かめられるものは、`static_assert` を使います。

## よくあるミス

??? failure "assert の中に副作用を書く"
    `assert(Load())` は、リリースビルドで `Load()` ごと消えます。

??? failure "条件に副作用を書く"
    `assert(ptr = Create())` のように、代入や初期化を条件に入れると、リリースビルドで消えて、動きが変わります。副作用のある処理は、`assert` の外に書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| `static_assert` | コンパイル時の確認 |
| [`std::abort`](../numeric/cstdlib/abort.md) | 失敗時に呼ばれる |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前提条件の確認
    - [x] リリースでは消える
    - [x] 副作用を書かない

## 関連ページ

- [cpprefjp: assert](https://cpprefjp.github.io/reference/cassert/assert.html)
- [cppreference: assert](https://en.cppreference.com/w/cpp/error/assert)
