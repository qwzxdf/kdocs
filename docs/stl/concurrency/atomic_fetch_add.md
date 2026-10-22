---
title: std::atomic_fetch_add
summary: "アトミックに加算し、加算前の値を返す。"
order: 900
tags:
  - 並行処理
---

# std::atomic_fetch_add

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`a.fetch_add(n)` の自由関数版です。複数のスレッドから同時に加算しても、更新が失われません。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_fetch_add {#atomic_fetch_add}

```cpp
template <class T>
T atomic_fetch_add(std::atomic<T>* obj, T arg) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic<T>* | 対象 |
| `arg` | T | 足す値 |

- 戻り値: 加算前の値
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{1};
  int old = std::atomic_fetch_add(&a, 2);
  std::println("{} {}", old, a.load());
}
```

```text title="実行結果"
1 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | スレッド間で共有するカウンタを増やす |

## よくあるミス

??? failure "`a += 2` との違いを気にしない"
    `a += 2` も同じ意味ですが、戻り値（加算前）が欲しいときだけ `fetch_add` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_fetch_sub`](atomic_fetch_sub.md) | 減算 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アトミックに加算し、加算前の値を返す
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_fetch_add](https://cpprefjp.github.io/reference/atomic/atomic_fetch_add.html)
- [cppreference: std::atomic_fetch_add](https://en.cppreference.com/w/cpp/atomic/atomic_fetch_add)
