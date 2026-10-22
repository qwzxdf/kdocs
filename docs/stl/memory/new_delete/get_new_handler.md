---
title: std::get_new_handler
summary: "現在設定されている new ハンドラを取得する。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::get_new_handler

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <new>`
</div>

`new` でメモリが足りなくなったとき、呼ばれる関数が `new_handler` です。いま設定されているものを `get_new_handler()` で取り出せます。一時的に差し替えて元に戻すときなどに使います。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`set_new_handler`](set_new_handler.md) を先に読んでください。

## 関数の詳しい説明

### std::get_new_handler {#get_new_handler}

```cpp
std::new_handler get_new_handler() noexcept;
```

- 戻り値: 現在のハンドラ（未設定なら `nullptr`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  std::println("{}", std::get_new_handler() == nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | メモリ不足時の動作を一時的に変える |

## よくあるミス

??? failure "ヌルのまま呼ぶ"
    戻り値は未設定のとき `nullptr` です。呼ぶ前に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`set_new_handler`](set_new_handler.md) | ハンドラを設定する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在設定されている new ハンドラを取得する
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::get_new_handler](https://cpprefjp.github.io/reference/new/get_new_handler.html)
- [cppreference: std::get_new_handler](https://en.cppreference.com/w/cpp/error/get_new_handler)
