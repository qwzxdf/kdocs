---
title: co_yield
summary: "コルーチンから値を 1 つ返して一時停止し、次に呼ばれたら続きから再開する。"
order: 5
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# co_yield

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

`co_yield` は、**コルーチンから値を 1 つ返して、いったん一時停止する**キーワードです。次に値を要求されると、そこから再開します。`std::generator` の中で、値を 1 つずつ作って返すときに使います。

!!! tip "ポイント"
    - `co_yield 値;` で値を返して止まる。
    - 無限の列も、必要な分だけ作れる（遅延評価）。
    - `std::generator`（C++23）の中で使うのが普通。

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページにコルーチンの簡単な例があります。

## 関数の詳しい説明

### co_yield {#co_yield}

```cpp
co_yield 式;
```

- 値を 1 つ呼び出し側に渡して、関数を一時停止します。ローカル変数はそのまま保たれ、次に再開すると続きから動きます

## 実際に動かしてみる

```cpp
#include <generator>
#include <print>

std::generator<int> Count(int n) {
  for (int i = 0; i < n; ++i) {
    co_yield i;   // 値を返して一時停止する
  }
}

int main() {
  for (int v : Count(3)) {
    std::println("{}", v);
  }
}
```

```text title="実行結果"
0
1
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フレームごとに次の位置を返す動きのパターン | `co_yield position;` |

## よくあるミス

??? failure "generator なしで使う"
    戻り値の型が `co_yield` に対応していないとコンパイルエラーです。`std::generator` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::generator`](../generator.md) | co_yield を使う標準の型 |
| [`co_return`](co_return.md) | コルーチンを終えて値を返す |

## コンパイラ対応

C++20 の機能です（`std::generator` は C++23）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値を返して一時停止する
    - [x] `generator` と使う
    - [x] 無限の列も作れる

## 関連ページ

- [cpprefjp: コルーチン](https://cpprefjp.github.io/reference/coroutine.html)
- [cppreference: Coroutines](https://en.cppreference.com/w/cpp/language/coroutines)
