---
title: std::rcu_barrier
summary: "予約された破棄が、すべて終わるまで待つ。"
order: 900
tags:
  - 並行処理
---

# std::rcu_barrier

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

`rcu_retire` で予約した破棄が全部完了するのを待ちます。プログラム終了前に後始末を確実に終わらせたいときに使います。

!!! tip "ポイント"
    - `rcu_retire` の予約が全部終わるまで待つ。
    - 終了処理の前に呼ぶ。
    - C++26。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_barrier {#rcu_barrier}

```cpp
void rcu_barrier(rcu_domain& dom = rcu_default_domain()) noexcept;
```

- 戻り値: なし（予約済みの破棄が終わるまで待つ）
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: 終了前に保留中の破棄を完了させる
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | 終了前に保留中の破棄を完了させる |

## よくあるミス

??? failure "読み取り区間の中で呼ぶ"
    デッドロックします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_retire`](rcu_retire.md) | 破棄を予約する |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 予約された破棄がすべて終わるまで待つ
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::rcu_barrier](https://cpprefjp.github.io/reference/rcu/rcu_barrier.html)
- [cppreference: std::rcu_barrier](https://en.cppreference.com/w/cpp/thread/rcu_barrier)
