---
title: std::get_terminate
summary: "現在設定されている terminate ハンドラを取得する。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::get_terminate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

`std::set_terminate` で登録した関数をあとから確認したい。`std::get_terminate()` は、<strong>現在登録されている終了ハンドラーを返します</strong>。

!!! tip "ポイント"
    - 現在登録されている終了ハンドラーを返す
    - 何も登録していなければ既定のハンドラー
    - `set_terminate` の戻り値でも、直前の値を取れる
    - 戻り値は null にならない

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::get_terminate {#get_terminate}

<span class="ver ver-11">C++11</span>

```cpp
std::terminate_handler get_terminate() noexcept;
```

登録されている `std::terminate_handler` を返します。何も登録していなければ、実装が持つ既定のハンドラー（通常は `std::abort` を呼ぶ）を返します。

用途は、一時的に登録を変えたあとに、元に戻すためです。ただし、`set_terminate` の戻り値でも同じことができるので、`get_terminate` を使う場面は限られます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <exception>
#include <print>

[[noreturn]] void Handler() { std::abort(); }

int main() {
  std::println("既定のハンドラーは null でない: {}", std::get_terminate() != nullptr);
  const auto previous = std::set_terminate(Handler);
  std::println("登録したものが返る: {}", std::get_terminate() == Handler);
  std::set_terminate(previous);
}
```

```text title="実行結果"
既定のハンドラーは null でない: true
登録したものが返る: true
```

## ゲームでの使いどころ

登録状態の確認や、デバッグで使います。

## よくあるミス

??? failure "登録がないときに `nullptr` が返ると思う"
    既定のハンドラーが返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`set_terminate`](set_terminate.md) | 登録する |
| [`terminate`](terminate.md) | 異常終了する |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `get_terminate()` は現在の終了ハンドラーを返す
    - [x] 登録がなければ既定のハンドラー
    - [x] 元に戻すには `set_terminate` の戻り値でもよい

## 関連ページ

- [cpprefjp: std::get_terminate](https://cpprefjp.github.io/reference/exception/get_terminate.html)
- [cppreference: std::get_terminate](https://en.cppreference.com/w/cpp/error/get_terminate)
