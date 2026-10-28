---
title: co_return
summary: "コルーチンを終了して、値を返す。"
order: 6
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# co_return

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

`co_return` は、**コルーチンを終了して（値があれば）値を返す**キーワードです。普通の関数の `return` に相当します。コルーチンの中では `return` は使えず、必ず `co_return` を使います。

!!! tip "ポイント"
    - 値なしの `co_return;` は、`promise.return_void()` を呼ぶ。
    - 値ありの `co_return x;` は、`promise.return_value(x)` を呼ぶ。
    - 関数の最後まで流れて終わると、`co_return;` と同じ。

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページにコルーチンの簡単な例があります。

## 関数の詳しい説明

### co_return {#co_return}

```cpp
co_return;
```

- generator を終わらせます（範囲 for が終わる）

```cpp
#include <generator>
#include <print>
#include <string>

// 迷路の道順を 1 歩ずつ出す（途中で終わる）
std::generator<std::string> Path() {
  co_yield "右";
  co_yield "右";
  co_yield "上";
  co_return;  // ここで終わり
  co_yield "ここには来ない";
}

int main() {
  for (const std::string& step : Path()) {
    std::print("{} ", step);
  }
  std::println("");
}
```

```text title="実行結果"
右 右 上 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 演出の途中でキャンセルされたら、その場で終了する | `if (cancelled) co_return;` |

## よくあるミス

??? failure "return を使う"
    コルーチンの中の `return` はコンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`co_yield`](co_yield.md) | 値を返して続きがある |
| [`co_await`](co_await.md) | 待つ |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コルーチンを終えて値を返す
    - [x] `return` は使えない
    - [x] 最後まで流れても終了

## 関連ページ

- [cpprefjp: コルーチン](https://cpprefjp.github.io/reference/coroutine.html)
- [cppreference: Coroutines](https://en.cppreference.com/w/cpp/language/coroutines)
