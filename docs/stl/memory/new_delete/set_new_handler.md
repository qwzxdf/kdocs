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

ゲーム機のように、メモリが限られた環境で、`new` が失敗したとき、すぐに `std::bad_alloc` で落とすのではなく、キャッシュを捨てて空きを作ってから、もう一度確保を試みたい。`std::set_new_handler(h)` は、`operator new` が確保に失敗したときに呼ばれる関数 `h` を登録します。

!!! tip "ポイント"
    - `new` が失敗するたびに、登録した関数が呼ばれ、成功するまで繰り返される
    - ハンドラーの中では、メモリを解放する、例外 `bad_alloc` を投げる、`abort` する、のどれかをする
    - 何もせずに戻ると、また `new` が再試行されて、無限ループになる
    - 戻り値は、それまでのハンドラー。`nullptr` を渡すと、既定の動作（例外）に戻る

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) を先に読んでください。

## 関数の詳しい説明

### std::set_new_handler {#set_new_handler}

```cpp
std::new_handler set_new_handler(std::new_handler new_p) noexcept;
using new_handler = void (*)();
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `new_p` | `std::new_handler` | 登録する関数。`nullptr` で解除 |

ハンドラーは、引数も戻り値もない関数です。`operator new` は、確保に失敗するたびに、ハンドラーを呼んでから、確保を再試行します。ハンドラーが何もせずに戻り続けると、永久に繰り返します。

ハンドラーに許される動作は、次のどれかです。

- メモリを解放して、再試行に成功する見込みを作る
- 別のハンドラーを登録する、または解除する（`set_new_handler(nullptr)`）
- `std::bad_alloc`（の派生）を投げる
- `std::abort` か `std::exit` で終了する

登録はプログラム全体で 1 つで、スレッドごとではありません。複数のスレッドから同時に確保するときは、ハンドラーの中でも排他制御が要ります。

## 実際に動かしてみる

```cpp
#include <limits>
#include <new>
#include <print>

int g_calls = 0;

void MyHandler() {
  ++g_calls;
  throw std::bad_alloc();  // 空きを作れないので、例外にする
}

int main() {
  std::new_handler old = std::set_new_handler(MyHandler);
  try {
    // 確保できない大きさを要求する
    char* p = new char[std::numeric_limits<std::size_t>::max() / 2];
    delete[] p;
  } catch (const std::bad_alloc&) {
    std::println("bad_alloc を捕まえた");
  }
  std::println("ハンドラーが呼ばれた回数: {}", g_calls);
  std::set_new_handler(old);
}
```

```text title="実行結果"
bad_alloc を捕まえた
ハンドラーが呼ばれた回数: 1
```

## ゲームでの使いどころ

空きが足りなくなったときに、キャッシュした画像を捨てて空きを作る、といった回復に使います。回復できなければ、原因を記録して終了します。

## よくあるミス

??? failure "何もせずに戻る"
    再試行が続き、止まらなくなります。

??? failure "ハンドラーの中で new を使う"
    再び失敗して、ハンドラーが再帰的に呼ばれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_new_handler`](get_new_handler.md) | 現在のハンドラーを調べる |
| [`nothrow`](nothrow.md) | 失敗したら `nullptr` を返す `new` |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::set_new_handler](https://cpprefjp.github.io/reference/new/set_new_handler.html)
- [cppreference: std::set_new_handler](https://en.cppreference.com/w/cpp/memory/new/set_new_handler)
