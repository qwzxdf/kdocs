---
title: std::hazard_pointer_obj_base
summary: "ハザードポインタで守るオブジェクトが継承する基底クラス。"
order: 900
tags:
  - 並行処理
---

# std::hazard_pointer_obj_base

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <hazard_pointer>`
</div>

`std::hazard_pointer` で保護される側のオブジェクトが継承する基底クラスが `std::hazard_pointer_obj_base<T>` です。`retire()` を呼ぶと、そのオブジェクトを「もう使わないので、誰も保護しなくなったら解放してよい」と登録します。

!!! tip "ポイント"
    - 保護されるクラスが `hazard_pointer_obj_base<Self>` を継承する（CRTP）
    - `obj->retire()` で、解放を予約する
    - 保護している `hazard_pointer` がなくなってから、解放される
    - 解放の方法は、第 2 テンプレート引数のデリーターで変えられる

!!! info "このページを読む前に"
    [`hazard_pointer`](hazard_pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::hazard_pointer_obj_base {#hazard_pointer_obj_base}

<span class="ver ver-26">C++26</span>

```cpp
template <class T, class D = std::default_delete<T>>
class hazard_pointer_obj_base {
 public:
  void retire(D d = D()) noexcept;
 protected:
  hazard_pointer_obj_base() = default;
  ~hazard_pointer_obj_base() = default;
};
```

`retire` を呼んだあと、そのオブジェクトにアクセスしてよいのは、すでに保護している `hazard_pointer` を持つスレッドだけです。新しく `protect` で取得することは、もうできないように、構造から取り外してから `retire` を呼びます。

実際の解放は、すぐではありません。内部のリストに溜められ、定期的に、保護されていないものだけが解放されます。溜まったまま解放が進まない場合、メモリ使用量が増えます。

`D` は、解放の処理（既定は `delete`）です。メモリ プールに返すなど、独自の解放が必要なら指定します。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
struct Node : std::hazard_pointer_obj_base<Node> {
  explicit Node(int v) : value(v) {}
  int value;
};

void Remove(std::atomic<Node*>& slot) {
  Node* old = slot.exchange(nullptr);   // 先に構造から外す
  if (old) old->retire();               // 保護者がいなくなったら解放される
}
```

## ゲームでの使いどころ

自作のロック フリー コンテナのノードに、継承させます。

## よくあるミス

??? failure "構造から外す前に retire する"
    他のスレッドが新しく protect できてしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hazard_pointer`](hazard_pointer.md) | 保護する側 |
| [`rcu_obj_base`](rcu_obj_base.md) | RCU 版 |
| `std::default_delete` | 既定のデリーター |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::hazard_pointer_obj_base](https://cpprefjp.github.io/reference/hazard_pointer/hazard_pointer_obj_base.html)
- [cppreference: std::hazard_pointer_obj_base](https://en.cppreference.com/w/cpp/thread/hazard_pointer_obj_base)
