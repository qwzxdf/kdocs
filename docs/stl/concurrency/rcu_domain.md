---
title: std::rcu_domain
summary: "RCU の管理単位（ドメイン）を表す型。"
order: 900
tags:
  - 並行処理
---

# std::rcu_domain

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

RCU（Read-Copy-Update）は、読み取りをロックなしで行い、書き換えはコピーを作って差し替える同期方式です。`rcu_domain` は、読み取り中のスレッドを数える管理の単位で、ふつうは標準のドメイン（`rcu_default_domain()`）を使います。

!!! tip "ポイント"
    - `lock()` / `unlock()` が読み取り区間の開始・終了。
    - `scoped_lock` で読み取り区間を作る。
    - ふつうは標準のドメインを使う。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_domain {#rcu_domain}

```cpp
class rcu_domain {
 public:
  void lock() noexcept;    // 読み取り区間の開始
  void unlock() noexcept;  // 読み取り区間の終了
};
```

- 戻り値: 読み取り区間を管理する
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: 読み取りが多い設定データを、ロックなしで読めるようにする
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | 読み取りが多い設定データを、ロックなしで読めるようにする |

## よくあるミス

??? failure "読み取り区間で長く待つ"
    区間が長いと、書き換えの後始末が遅れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_default_domain`](rcu_default_domain.md) | 標準のドメイン |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RCU の管理単位（ドメイン）を表す型
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::rcu_domain](https://cpprefjp.github.io/reference/rcu/rcu_domain.html)
- [cppreference: std::rcu_domain](https://en.cppreference.com/w/cpp/thread/rcu_domain)
