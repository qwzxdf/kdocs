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

`rcu_retire` は、予約の記録のために、メモリを確保します。確保の失敗が許されない場面では、予約の記録をオブジェクト自身に持たせる `std::rcu_obj_base<T>` を継承します。`retire()` を呼ぶと、確保せずに予約できます。

!!! tip "ポイント"
    - 解放を予約する対象のクラスが、`rcu_obj_base<Self>` を継承する（CRTP）
    - `obj->retire()` で予約する。メモリの確保が要らない
    - 読み手がいなくなったあとに、デリーターで解放される
    - C++26

!!! info "このページを読む前に"
    [`rcu_retire`](rcu_retire.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_obj_base {#rcu_obj_base}

<span class="ver ver-26">C++26</span>

```cpp
template <class T, class D = std::default_delete<T>>
class rcu_obj_base {
 public:
  void retire(D d = D(), std::rcu_domain& dom = std::rcu_default_domain()) noexcept;
};
```

`noexcept` であることが、`rcu_retire` との違いです。予約の記録を基底クラスのメンバーに持つので、確保が要りません。

継承するクラスのオブジェクトは、`retire` を呼んだあと、解放されるまで生きている必要があります。基底クラスのデストラクターは `protected` で、直接 `delete` できません。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
struct Config : std::rcu_obj_base<Config> {
  int level = 1;
};

void Update(std::atomic<Config*>& slot, Config* fresh) {
  Config* old = slot.exchange(fresh);
  old->retire();                 // 確保なしで、解放を予約する
}
```

## ゲームでの使いどころ

解放の予約が失敗してはいけない、ゲームの中心的な構造で使います。

## よくあるミス

??? failure "retire 後に、直接 delete する"
    二重解放になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_retire`](rcu_retire.md) | 関数版 |
| [`hazard_pointer_obj_base`](hazard_pointer_obj_base.md) | hazard pointer 版 |
| [`rcu_domain`](rcu_domain.md) | ドメイン |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::rcu_obj_base](https://cpprefjp.github.io/reference/rcu/rcu_obj_base.html)
- [cppreference: std::rcu_obj_base](https://en.cppreference.com/w/cpp/thread/rcu_obj_base)
