---
title: std::terminate
summary: "処理されなかった例外などで呼ばれる、プログラムの強制終了。"
order: 17
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::terminate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <exception>`
</div>

捕まえられなかった例外があるとき、あるいはデストラクターから例外が出たとき、プログラムはもう安全に続行できません。`std::terminate()` は、<strong>プログラムを異常終了させる</strong>関数で、これらの場面で自動的に呼ばれます。

!!! tip "ポイント"
    - プログラムを異常終了させる
    - 捕まらなかった例外などで自動的に呼ばれる
    - 呼ばれる直前に `set_terminate` で登録した関数が実行される
    - 既定では `std::abort` を呼ぶ

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::terminate {#terminate}

<span class="ver ver-98">C++98</span>

```cpp
[[noreturn]] void terminate() noexcept;
```

`std::terminate` は、登録された終了ハンドラー（`set_terminate`）を呼びます。既定のハンドラーは `std::abort` を呼びます。

自動で呼ばれる場面は、次のとおりです。例外が捕まらずに `main` を抜けようとしたとき、`noexcept` の関数から例外が出たとき、デストラクターが巻き戻し中に例外を投げたとき、ムーブ操作などで解決できないとき、`std::thread` が `join` / `detach` されずに破棄されたとき。

自分から呼ぶ場面は、まれです。続行できない状況を検出したら、`std::abort()` か `std::terminate()` で終了します。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>

int main(int argc, char**) {
  if (argc > 1) {
    std::terminate();                // 引数があれば異常終了（今回は実行されない）
  }
  std::println("terminate せずに終了");
}
```

```text title="実行結果"
terminate せずに終了
```

## ゲームでの使いどころ

回復できない状態を検出したときの、最後の手段です。

```cpp
if (!InvariantHolds()) {
  Log("内部の状態が壊れている");
  std::terminate();
}
```

## よくあるミス

??? failure "`noexcept` の関数から例外を出して、意図せず `terminate` になる"
    `noexcept` の関数の中で例外を捕まえます。

??? failure "`std::thread` を `join` せずに破棄する"
    必ず `join` か `detach` を呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`set_terminate`](set_terminate.md) | 終了直前の関数を登録 |
| [`abort`](../../numeric/cstdlib/abort.md) | 後始末なしの異常終了 |

## コンパイラ対応

C++98 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `terminate()` はプログラムを異常終了させる
    - [x] 捕まらない例外、`noexcept` からの例外などで自動的に呼ばれる
    - [x] `set_terminate` で終了直前の処理を登録できる

## 関連ページ

- [cpprefjp: std::terminate](https://cpprefjp.github.io/reference/exception/terminate.html)
- [cppreference: std::terminate](https://en.cppreference.com/w/cpp/error/terminate)
