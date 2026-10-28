---
title: std::rcu_obj_base
summary: "RCU で保護するオブジェクトが継承する基底クラス。"
order: 900
tags:
  - 並行処理
---

# std::rcu_obj_base

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

RCU で守るオブジェクトは、書き換えで古いものを差し替えたあと、読み取り中のスレッドがいなくなってから破棄する必要があります。`rcu_obj_base<T>` を継承すると、`retire()` で「あとで安全になったら破棄して」と頼めます。

!!! tip "ポイント"
    - `class MyData : public std::rcu_obj_base<MyData>` と継承する。
    - `retire()` が、安全になったら破棄する。
    - C++26。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_obj_base {#rcu_obj_base}

```cpp
template <class T, class D = default_delete<T>>
class rcu_obj_base {
 public:
  void retire(D d = D(), rcu_domain& dom = rcu_default_domain()) noexcept;
};
```

- 戻り値: `retire()` でオブジェクトの破棄を予約する
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: 古い設定データを読み取りが終わってから破棄する
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | 古い設定データを読み取りが終わってから破棄する |

## よくあるミス

??? failure "`delete` を直接呼ぶ"
    読み取り中のスレッドがいると壊れます。`retire()` に任せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_retire`](rcu_retire.md) | 継承せずに破棄を予約する |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RCU で保護するオブジェクトが継承する基底クラス
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::rcu_obj_base](https://cpprefjp.github.io/reference/rcu/rcu_obj_base.html)
- [cppreference: std::rcu_obj_base](https://en.cppreference.com/w/cpp/thread/rcu_obj_base)
