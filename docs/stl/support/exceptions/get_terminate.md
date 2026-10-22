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

`set_terminate` で設定したハンドラを、あとで読み出します。ハンドラを一時的に差し替えて、あとで元に戻したいときなどに使います。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::get_terminate {#get_terminate}

```cpp
std::terminate_handler get_terminate() noexcept;
```

- 戻り値: 現在のハンドラ（既定ではライブラリが決めた関数）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>

int main() {
  std::terminate_handler h = std::get_terminate();
  std::println("{}", h != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ハンドラを一時的に差し替えて元に戻す |

## よくあるミス

??? failure "ヌルだと思う"
    既定でも、ライブラリが用意した関数が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`set_terminate`](set_terminate.md) | ハンドラを設定する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在設定されている terminate ハンドラを取得する
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::get_terminate](https://cpprefjp.github.io/reference/exception/get_terminate.html)
- [cppreference: std::get_terminate](https://en.cppreference.com/w/cpp/error/get_terminate)
