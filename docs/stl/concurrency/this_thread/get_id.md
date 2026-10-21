---
title: std::this_thread::get_id
summary: "今のスレッドの ID を取得する。"
order: 78
group: this_thread
tags:
  - 並行処理
---

# std::this_thread::get_id

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <thread>`
</div>

`std::this_thread::get_id` は、**今実行しているスレッドの ID**（`std::thread::id`）を返します。ログにスレッドを区別して出す、「描画スレッドから呼ばれているか」を確かめる、といったデバッグに使います。ID の値は環境しだいで、数値として意味はありません。

!!! tip "ポイント"
    - 比較できる（`==`）。出力もできる（`std::println("{}", id)`、C++23）。
    - 「このコードはメインスレッドからだけ呼ぶ」の確認に、`assert(this_thread::get_id() == main_id)`。
    - 環境によって数値が違う。

!!! info "このページを読む前に"
    [並行処理の基本](../../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::get_id {#get_id}

```cpp
std::thread::id get_id() noexcept;
```

- 今のスレッドの ID。「メインスレッドから呼ばれているか」のチェックに使えます

## 実際に動かしてみる

```cpp
#include <print>
#include <thread>

int main() {
  auto id = std::this_thread::get_id();
  std::println("{}", id == std::this_thread::get_id());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 描画スレッドからだけ呼ぶ関数で、呼び出し元を確かめる | `assert(std::this_thread::get_id() == render_thread_id);` |
| ログにスレッド ID を付ける | `std::println("[{}] ...", std::this_thread::get_id());` |

## よくあるミス

??? failure "ID を整数として扱う"
    値は実装しだいです。比較と出力だけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::thread::id`](../thread.md) | スレッド ID の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 今のスレッドの ID
    - [x] 比較と出力ができる
    - [x] 値に意味はない

## 関連ページ

- [cpprefjp: std::this_thread::get_id](https://cpprefjp.github.io/reference/thread/this_thread/get_id.html)
- [cppreference: std::this_thread::get_id](https://en.cppreference.com/w/cpp/get_id)
