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

`std::rcu_default_domain()` は、プログラム全体で共通の、既定の RCU ドメインへの参照を返します。ドメインを指定しない `rcu_retire` や `rcu_synchronize` は、これを使います。通常は、これだけで足ります。

!!! tip "ポイント"
    - `rcu_domain&` を返す
    - プログラムに 1 つ。いつ呼んでも同じオブジェクト
    - 読み手の区間は `std::scoped_lock(std::rcu_default_domain())` で囲む
    - C++26

!!! info "このページを読む前に"
    [`rcu_domain`](rcu_domain.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_default_domain {#rcu_default_domain}

<span class="ver ver-26">C++26</span>

```cpp
std::rcu_domain& rcu_default_domain() noexcept;
```

別のドメインを作ることも仕様上はできますが、標準では、ドメインを自作する方法は限られていて、既定のドメインを使うのが普通です。

読み手が区間に入ってから出るまでの間は、このドメインの書き手（`rcu_synchronize`）が待たされる対象になります。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
void Reader() {
  std::scoped_lock guard(std::rcu_default_domain());
  // 共有データを読む
}
```

## ゲームでの使いどころ

RCU を使うほぼすべての場面で、読み手の区間の指定に使います。

## よくあるミス

??? failure "区間を長く保つ"
    書き手の解放が遅れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_domain`](rcu_domain.md) | ドメインの型 |
| [`rcu_synchronize`](rcu_synchronize.md) | 読み手の終了を待つ |
| [`rcu_retire`](rcu_retire.md) | 解放を予約する |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::rcu_default_domain](https://cpprefjp.github.io/reference/rcu/rcu_default_domain.html)
- [cppreference: std::rcu_default_domain](https://en.cppreference.com/w/cpp/thread/rcu_default_domain)
