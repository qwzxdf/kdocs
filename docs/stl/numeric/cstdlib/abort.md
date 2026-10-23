---
title: std::abort
summary: "プログラムを異常終了する（後片付けなし）。"
order: 6
group: <cstdlib> の関数
tags:
  - 数値
---

# std::abort

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

続行しても意味がないほど、プログラムの状態が壊れている。そんなときの最後の手段が `std::abort` です。後始末をせず、異常終了させます。`assert` が失敗したときも、内部でこれが呼ばれます。

!!! tip "ポイント"
    - `std::abort()` で、後始末なしにプロセスを異常終了する
    - デストラクターも `atexit` の関数も呼ばれない
    - デバッガーで止まる、クラッシュダンプが残る
    - `assert` が失敗したときの動作

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::abort {#abort}

```cpp
[[noreturn]] void abort() noexcept;
```

プログラムを異常終了させます。`SIGABRT` というシグナルを発生させ、既定の動作では、デストラクターや `atexit` の関数を呼ばずにプロセスを終わらせます。戻ってくることはありません。

異常終了なので、デバッガーを接続していれば、その場で止まります。クラッシュレポートの仕組み（Windows のエラー報告、ミニダンプ）が有効なら、状態が記録されます。原因の調査には向いています。

Windows の MSVC のデバッグ ビルドでは、`abort` が「プログラムが異常終了しました」のダイアログを出すことがあります。

`exit` との違いは、正常な後始末を行わないことです。データの破損を広げたくないとき、つまり「今のメモリの状態を信用できない」ときに使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main(int argc, char**) {
  if (argc > 1) {
    std::abort();                    // 引数があれば異常終了（今回は実行されない）
  }
  std::println("abort せずに終了");
}
```

```text title="実行結果"
abort せずに終了
```

## ゲームでの使いどころ

決して起きないはずの状態を検出したときに使います。

```cpp
switch (state) {
  case State::kIdle: /* ... */ break;
  case State::kRun:  /* ... */ break;
  default:
    std::abort();   // 列挙子に無い値。メモリが壊れている
}
```

`assert` を使うほうが一般的です。リリース版で `assert` が無効になる場合でも、`abort` は常に有効です。

## よくあるミス

??? failure "エラー処理の通常の手段として使い、ユーザーのデータが失われる"
    回復できるエラーは、戻り値や例外で扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exit`](exit.md) | 後始末をして終了 |
| [`quick_exit`](quick_exit.md) | 最小限の後始末で終了 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `abort()` は後始末をせずに異常終了する
    - [x] デバッガーで止まり、ダンプが残る
    - [x] メモリの状態が信用できないときの最後の手段

## 関連ページ

- [cpprefjp: std::abort](https://cpprefjp.github.io/reference/cstdlib/abort.html)
- [cppreference: std::abort](https://en.cppreference.com/w/cpp/utility/program/abort)
