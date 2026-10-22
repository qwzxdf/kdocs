---
title: std::rcu_default_domain
summary: "標準の RCU ドメインを返す関数。"
order: 900
tags:
  - 並行処理
---

# std::rcu_default_domain

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

ふつうは自分でドメインを作らず、標準のドメインを使います。`std::rcu_default_domain()` が、そのドメインへの参照を返します。

!!! tip "ポイント"
    - 標準のドメインを返す。
    - `scoped_lock lk(std::rcu_default_domain());` で読み取り区間を作る。
    - プログラム全体で 1 つ。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_default_domain {#rcu_default_domain}

```cpp
rcu_domain& rcu_default_domain() noexcept;
```

- 戻り値: 標準の `rcu_domain` への参照
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: 標準のドメインで読み取り区間を作る
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | 標準のドメインで読み取り区間を作る |

## よくあるミス

??? failure "ドメインを自作する"
    特別な理由がなければ、標準のドメインを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_domain`](rcu_domain.md) | ドメインの型 |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準の RCU ドメインを返す関数
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::rcu_default_domain](https://cpprefjp.github.io/reference/rcu/rcu_default_domain.html)
- [cppreference: std::rcu_default_domain](https://en.cppreference.com/w/cpp/thread/rcu_default_domain)
