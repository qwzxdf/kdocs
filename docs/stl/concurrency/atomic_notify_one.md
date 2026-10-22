---
title: std::atomic_notify_one
summary: "atomic_wait で待っているスレッドを 1 つ起こす。"
order: 900
tags:
  - 並行処理
---

# std::atomic_notify_one

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <atomic>`
</div>

`atomic_wait` で待っているスレッドが複数いるとき、そのうち 1 つを起こします。値を変えたあとに呼びます。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_notify_one {#atomic_notify_one}

```cpp
template <class T>
void atomic_notify_one(std::atomic<T>* obj) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic<T>* | 対象 |

- 戻り値: なし
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{0};
  a.store(1);
  std::atomic_notify_one(&a);
  std::println("notified");
}
```

```text title="実行結果"
notified
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 待機中のスレッドを 1 つ起こす |

## よくあるミス

??? failure "値を変えずに通知する"
    値を変えてから通知します。変えないと、起きても再び眠ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_wait`](atomic_wait.md) | 待つ |
| [`atomic_notify_all`](atomic_notify_all.md) | 全部起こす |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] atomic_wait で待っているスレッドを 1 つ起こす
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_notify_one](https://cpprefjp.github.io/reference/atomic/atomic_notify_one.html)
- [cppreference: std::atomic_notify_one](https://en.cppreference.com/w/cpp/atomic/atomic_notify_one)
