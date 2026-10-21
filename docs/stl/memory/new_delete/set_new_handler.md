---
title: std::set_new_handler
summary: "`new` が失敗したときに呼ばれる関数を登録する。"
order: 12
group: new / delete まわり
tags:
  - メモリ
---

# std::set_new_handler

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

`std::set_new_handler` は、**`new` がメモリを確保できなかったときに、例外を投げる前に呼ばれる関数を登録する**関数です。ハンドラーの中で、キャッシュを捨ててメモリを空ける、ログを出して終了する、といった対応ができます。

!!! tip "ポイント"
    - ハンドラーがメモリを空ければ、`new` は再試行する。
    - 何もせずに戻ると、無限に再試行する。必ず「空ける」「例外を投げる」「終了する」のどれかをする。
    - 戻り値は、前のハンドラー。

## 関数の詳しい説明

### std::set_new_handler {#set_new_handler}

```cpp
new_handler set_new_handler(new_handler handler) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `handler` | `void(*)()` | メモリ不足のときに呼ぶ関数。`nullptr` で解除 |

- 戻り値: 前のハンドラー
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <new>
#include <print>

int main() {
  std::set_new_handler([] {
    std::println("メモリ不足");
    std::abort();
  });
  auto old = std::set_new_handler(nullptr);  // 解除。前のハンドラーが返る
  std::println("{}", old != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メモリ不足で終わる前に、ログを残す | `std::set_new_handler([] { LogOutOfMemory(); std::abort(); })` |

## よくあるミス

??? failure "ハンドラーが何もしない"
    `new` が無限に再試行します。必ず何かをします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nothrow`](nothrow.md) | 例外を投げない new |
| [`bad_alloc`](../../support/exceptions/bad_alloc.md) | 投げられる例外 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] new 失敗時に呼ぶ関数
    - [x] 何もしないと無限ループ
    - [x] 前のハンドラーが返る

## 関連ページ

- [cpprefjp: std::set_new_handler](https://cpprefjp.github.io/reference/new/set_new_handler.html)
- [cppreference: std::set_new_handler](https://en.cppreference.com/w/cpp/memory/new/set_new_handler)
