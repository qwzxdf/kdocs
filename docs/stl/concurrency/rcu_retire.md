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

古いデータの解放を、書き手が待たずに済ませたい。`std::rcu_retire(p, d)` は、`p` を「読み手が全員いなくなったら、`d` で解放してほしい」と予約して、すぐ戻ります。実際の解放は、あとで、別のスレッドが行います。

!!! tip "ポイント"
    - ポインターとデリーターを渡して、解放を予約する
    - 呼び出し側は待たない
    - 実際の解放は、読み手がいなくなったあと
    - 完了を確かめたいなら `rcu_barrier`

!!! info "このページを読む前に"
    [`rcu_synchronize`](rcu_synchronize.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_retire {#rcu_retire}

<span class="ver ver-26">C++26</span>

```cpp
template <class T, class D = std::default_delete<T>>
void rcu_retire(T* p, D d = D(), std::rcu_domain& dom = std::rcu_default_domain());
```

内部でメモリを確保して予約を記録するので、`std::bad_alloc` を投げることがあります。確保の失敗を避けたいなら、`rcu_obj_base` を継承するクラスの `retire` を使います（記録の領域をオブジェクトに持つ）。

`rcu_synchronize` と違い、書き手が止まらないので、更新の頻度が高いときに向きます。そのかわり、解放が遅れるぶん、メモリ使用量が増えます。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
void Update(std::atomic<Config*>& slot, Config* fresh) {
  Config* old = slot.exchange(fresh);
  std::rcu_retire(old);          // 待たずに、解放を予約する
}
```

## ゲームでの使いどころ

更新が頻繁で、書き手を止めたくない場面で使います。

## よくあるミス

??? failure "予約後も old を使う"
    解放される可能性があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_synchronize`](rcu_synchronize.md) | 待ってから解放する |
| [`rcu_obj_base`](rcu_obj_base.md) | オブジェクトに予約の領域を持たせる |
| [`rcu_barrier`](rcu_barrier.md) | 予約の完了を待つ |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::rcu_retire](https://cpprefjp.github.io/reference/rcu/rcu_retire.html)
- [cppreference: std::rcu_retire](https://en.cppreference.com/w/cpp/thread/rcu_retire)
