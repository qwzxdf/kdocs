---
title: std::set_terminate
summary: "プログラムが異常終了する直前に呼ばれる関数を設定する。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::set_terminate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <exception>`
</div>

捕まえられなかった例外があると、プログラムは `std::terminate` で終了します。そのとき、何も表示されずに落ちるのでは、原因が分かりません。`std::set_terminate(handler)` は、<strong>終了の直前に呼ばれる関数を登録</strong>します。ログを出したり、クラッシュ ダンプを残したりできます。

!!! tip "ポイント"
    - `std::set_terminate(f)` で、終了直前に呼ばれる関数を登録する
    - 関数の中で必ず終了させる（戻らない）
    - 戻り値は、直前に登録されていた関数
    - ログの出力やクラッシュ ダンプに使う

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::set_terminate {#set_terminate}

<span class="ver ver-11">C++11</span>

```cpp
std::terminate_handler set_terminate(std::terminate_handler f) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 関数ポインター | 終了直前に呼ぶ関数。戻らないこと |

登録した関数は、`std::terminate` が呼ばれたときに実行されます。関数の中では、プログラムを終了させる処理（`std::abort()` など）を必ず行います。戻ると未定義動作になります。

戻り値は、それまで登録されていた関数です。変更を元に戻したいときのために保存します。登録していなければ、既定の関数（`abort` を呼ぶ）が返ります。

Windows のゲームでは、`SetUnhandledExceptionFilter` で SEH の例外も拾う設計とあわせて、ログを書き出してから終了する仕組みを作ります。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <exception>
#include <print>

[[noreturn]] void OnTerminate() {
  std::println(stderr, "未処理の例外で終了します");
  std::abort();
}

int main() {
  const std::terminate_handler previous = std::set_terminate(OnTerminate);
  std::println("登録した: {}", std::get_terminate() == OnTerminate);
  std::set_terminate(previous);       // 元に戻す
}
```

```text title="実行結果"
登録した: true
```

## ゲームでの使いどころ

未処理の例外で落ちたとき、原因をログに残します。

```cpp
std::set_terminate([] {
  if (auto e = std::current_exception()) {
    try { std::rethrow_exception(e); }
    catch (const std::exception& ex) { Log(ex.what()); }
  }
  std::abort();
});
```

## よくあるミス

??? failure "登録した関数が戻って、未定義動作になる"
    必ず `std::abort()` などで終了します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_terminate`](get_terminate.md) | 登録中の関数を取る |
| [`terminate`](terminate.md) | 異常終了する |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `set_terminate(f)` は終了直前の関数を登録する
    - [x] 関数は終了させる（戻らない）
    - [x] ログやダンプに使う

## 関連ページ

- [cpprefjp: std::set_terminate](https://cpprefjp.github.io/reference/exception/set_terminate.html)
- [cppreference: std::set_terminate](https://en.cppreference.com/w/cpp/error/set_terminate)
