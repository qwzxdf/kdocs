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

RCU（Read-Copy-Update）は、読み手がロックを取らず、書き手が古いデータを置き換えるときに、読み手が全員いなくなるまで古いデータの解放を待つ、という方式です。`std::rcu_domain` は、読み手の区間（読み取りの臨界区間）を管理する単位です。既定では、プログラムに 1 つの既定のドメイン（`rcu_default_domain()`）を使います。

!!! tip "ポイント"
    - `lock()` / `unlock()` で、読み取りの区間を囲む
    - `std::scoped_lock` などで囲める（BasicLockable）
    - 読み手は、他の読み手や書き手を待たない
    - C++26

!!! info "このページを読む前に"
    [`atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_domain {#rcu_domain}

<span class="ver ver-26">C++26</span>

```cpp
class rcu_domain {
 public:
  rcu_domain(const rcu_domain&) = delete;
  void lock() noexcept;
  bool try_lock() noexcept;
  void unlock() noexcept;
};
rcu_domain& rcu_default_domain() noexcept;
```

読み手は、`rcu_default_domain()` を `std::scoped_lock` で囲んで、その間に共有データを読みます。ロックと呼びますが、他のスレッドを待たせる排他ロックではありません。「ここから、このドメインの読み手である」と宣言するだけです。

書き手は、データを置き換えたあと、古いデータを `rcu_retire` か `rcu_obj_base::retire` で予約します。その古いデータは、予約より前に始まった読み手が全員区間を出てから、解放されます。

読み手の区間の中で、ブロックする操作を長くやると、書き手の解放が遅れます。区間は短く保ちます。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
std::atomic<Config*> g_config;

int ReadLevel() {
  std::scoped_lock guard(std::rcu_default_domain());   // 読み取り区間
  Config* c = g_config.load();
  return c->level;
}
```

## ゲームでの使いどころ

ほとんど読み取りで、まれに更新される設定やテーブルを、読み手が待たずに読めるようにします。

## よくあるミス

??? failure "区間の外にポインターを持ち出す"
    区間を出ると、解放されるかもしれません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_default_domain`](rcu_default_domain.md) | 既定のドメイン |
| [`rcu_retire`](rcu_retire.md) | 古いデータの解放を予約する |
| [`rcu_synchronize`](rcu_synchronize.md) | 読み手の終了を待つ |
| [`hazard_pointer`](hazard_pointer.md) | 別の方式 |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::rcu_domain](https://cpprefjp.github.io/reference/rcu/rcu_domain.html)
- [cppreference: std::rcu_domain](https://en.cppreference.com/w/cpp/thread/rcu_domain)
