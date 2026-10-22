---
title: std::atomic_fetch_sub
summary: "アトミックに減算し、減算前の値を返す。"
order: 900
tags:
  - 並行処理
---

# std::atomic_fetch_sub

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`a.fetch_sub(n)` の自由関数版です。参照カウントを減らして、0 になったかを調べるときなどに使います。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_fetch_sub {#atomic_fetch_sub}

```cpp
template <class T>
T atomic_fetch_sub(std::atomic<T>* obj, T arg) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic<T>* | 対象 |
| `arg` | T | 引く値 |

- 戻り値: 減算前の値
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{3};
  int old = std::atomic_fetch_sub(&a, 2);
  std::println("{} {}", old, a.load());
}
```

```text title="実行結果"
3 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 参照カウントを減らす |

## よくあるミス

??? failure "戻り値を減算後と思う"
    戻り値は減算**前**の値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_fetch_add`](atomic_fetch_add.md) | 加算 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アトミックに減算し、減算前の値を返す
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_fetch_sub](https://cpprefjp.github.io/reference/atomic/atomic_fetch_sub.html)
- [cppreference: std::atomic_fetch_sub](https://en.cppreference.com/w/cpp/atomic/atomic_fetch_sub)
