---
title: std::atomic_init
summary: "atomic を初期化する（まだ他のスレッドが触っていないとき）。"
order: 900
tags:
  - 並行処理
---

# std::atomic_init

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

古い C++ では、`atomic<T>` の既定構築が初期化しないことがあり、`atomic_init` で初期化する必要がありました。C++20 以降は、既定構築で値初期化されるので、不要になり、非推奨です。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_init {#atomic_init}

```cpp
template <class T>
void atomic_init(std::atomic<T>* obj, T desired) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic<T>* | 対象 |
| `desired` | T | 初期値 |

- 戻り値: なし
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a;
  std::atomic_init(&a, 7);
  std::println("{}", a.load());
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 古いコードの保守 |

## よくあるミス

??? failure "新しいコードで使う"
    C++20 以降は非推奨です。コンストラクタで初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic`](atomic.md) | コンストラクタで初期化する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] atomic を初期化する（まだ他のスレッドが触っていないとき）
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_init](https://cpprefjp.github.io/reference/atomic/atomic_init.html)
- [cppreference: std::atomic_init](https://en.cppreference.com/w/cpp/atomic/atomic_init)
