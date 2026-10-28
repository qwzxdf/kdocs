---
title: std::rcu_retire
summary: "オブジェクトの破棄を、読み取りが終わってからの予約にする。"
order: 900
tags:
  - 並行処理
---

# std::rcu_retire

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

`rcu_obj_base` を継承できない型でも、`rcu_retire(ptr)` で、読み取り中のスレッドがいなくなってから破棄させられます。

!!! tip "ポイント"
    - 継承せずに破棄を予約できる。
    - 第 2 引数で破棄の方法を指定できる。
    - C++26。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_retire {#rcu_retire}

```cpp
template <class T, class D = default_delete<T>>
void rcu_retire(T* p, D d = D(), rcu_domain& dom = rcu_default_domain());
```

- 戻り値: なし
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: 古いデータを安全に破棄する
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | 古いデータを安全に破棄する |

## よくあるミス

??? failure "すぐに破棄されると思う"
    読み取りが終わったあと、あるタイミングで破棄されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_obj_base`](rcu_obj_base.md) | 継承して使う版 |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] オブジェクトの破棄を読み取りが終わってからの予約にする
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::rcu_retire](https://cpprefjp.github.io/reference/rcu/rcu_retire.html)
- [cppreference: std::rcu_retire](https://en.cppreference.com/w/cpp/thread/rcu_retire)
