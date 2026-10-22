---
title: std::atomic_is_lock_free
summary: "atomic の操作が、ロックなしで行えるかを調べる。"
order: 900
tags:
  - 並行処理
---

# std::atomic_is_lock_free

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic<T>` は、型によっては内部でロックを使います。`is_lock_free()` の自由関数版で、ロックなしで動くなら `true` です。ゲームでは、`int` や `bool` のほとんどが `true` です。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_is_lock_free {#atomic_is_lock_free}

```cpp
template <class T>
bool atomic_is_lock_free(const std::atomic<T>* obj) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | const atomic<T>* | 調べる対象 |

- 戻り値: ロックなしなら `true`
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a;
  std::println("{}", std::atomic_is_lock_free(&a));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | リアルタイム処理で、ロックが入らないことを確かめる |

## よくあるミス

??? failure "大きな構造体に使う"
    大きな型の `atomic` は、内部でロックを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic`](atomic.md) | `is_lock_free()` メンバ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] atomic の操作が、ロックなしで行えるかを調べる
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_is_lock_free](https://cpprefjp.github.io/reference/atomic/atomic_is_lock_free.html)
- [cppreference: std::atomic_is_lock_free](https://en.cppreference.com/w/cpp/atomic/atomic_is_lock_free)
