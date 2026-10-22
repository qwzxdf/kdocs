---
title: std::rcu_synchronize
summary: "読み取り中のスレッドがいなくなるまで待つ。"
order: 900
tags:
  - 並行処理
---

# std::rcu_synchronize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

古いデータを差し替えたあと、そのデータを読んでいるかもしれないスレッドが、全員終わるまで待つ関数です。待ったあとは、古いデータを破棄しても安全です。

!!! tip "ポイント"
    - 差し替えのあと、古いデータの破棄の前に呼ぶ。
    - 待つので、遅い。
    - 遅れてよいなら `rcu_retire`。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_synchronize {#rcu_synchronize}

```cpp
void rcu_synchronize(rcu_domain& dom = rcu_default_domain()) noexcept;
```

- 戻り値: なし（読み取りが終わるまで待つ）
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: データ差し替えの後始末を同期的に行う
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | データ差し替えの後始末を同期的に行う |

## よくあるミス

??? failure "読み取り区間の中で呼ぶ"
    自分自身を待ってしまい、デッドロックします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_retire`](rcu_retire.md) | 待たずに予約する |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読み取り中のスレッドがいなくなるまで待つ
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::rcu_synchronize](https://cpprefjp.github.io/reference/rcu/rcu_synchronize.html)
- [cppreference: std::rcu_synchronize](https://en.cppreference.com/w/cpp/thread/rcu_synchronize)
