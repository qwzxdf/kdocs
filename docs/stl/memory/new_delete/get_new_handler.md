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

`set_new_handler` で登録したハンドラーが、いま何かを調べたいことがあります。一時的にハンドラーを差し替えて、あとで元に戻すとき、元の値を覚えておく必要があります。`std::get_new_handler()` は、現在のハンドラーを返します。

!!! tip "ポイント"
    - 登録中のハンドラー（関数ポインタ）を返す
    - 何も登録していなければ `nullptr`
    - `set_new_handler` の戻り値でも、直前の値が分かる
    - C++11 から

!!! info "このページを読む前に"
    [`set_new_handler`](set_new_handler.md) を先に読んでください。

## 関数の詳しい説明

### std::get_new_handler {#get_new_handler}

```cpp
std::new_handler get_new_handler() noexcept;
```

引数はありません。戻り値が `nullptr` なら、既定の動作（失敗したら `std::bad_alloc` を投げる）です。

C++11 より前には、ハンドラーを読むだけの関数がなく、`set_new_handler(nullptr)` で取り出して、すぐ戻すという回りくどい方法でした。この間に別のスレッドが確保すると、既定の動作になってしまう危険がありました。`get_new_handler` で、その問題がなくなりました。

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

void MyHandler() { throw std::bad_alloc(); }

int main() {
  std::println("最初は未登録: {}", std::get_new_handler() == nullptr);

  std::set_new_handler(MyHandler);
  std::println("登録後は同じ: {}", std::get_new_handler() == MyHandler);

  std::set_new_handler(nullptr);
  std::println("解除後は未登録: {}", std::get_new_handler() == nullptr);
}
```

```text title="実行結果"
最初は未登録: true
登録後は同じ: true
解除後は未登録: true
```

## ゲームでの使いどころ

テストで一時的にハンドラーを差し替えて、終わったら元に戻すときに使います。

## よくあるミス

??? failure "C++11 より前の方法を真似る"
    取り出して戻す間に、隙があります。`get_new_handler` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`set_new_handler`](set_new_handler.md) | 登録する |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::get_new_handler](https://cpprefjp.github.io/reference/new/get_new_handler.html)
- [cppreference: std::get_new_handler](https://en.cppreference.com/w/cpp/error/get_new_handler)
