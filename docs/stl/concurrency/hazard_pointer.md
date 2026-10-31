---
title: std::hazard_pointer
summary: "別のスレッドが使用中のオブジェクトを「使っている」と宣言する印。"
order: 900
tags:
  - 並行処理
---

# std::hazard_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <hazard_pointer>`
</div>

ロックなしのデータ構造（ロック フリーのリスト）では、あるスレッドがノードを読んでいる最中に、別のスレッドがそのノードを `delete` すると、解放済みのメモリを読んでしまいます。`std::hazard_pointer` は、「いま、このノードを使っているので、解放しないでほしい」と宣言する印です。宣言されたノードは、解放が先送りされます。

!!! tip "ポイント"
    - `protect(atomic<T*>)` で、読んだポインターを保護する
    - 保護されたオブジェクトは、`retire` されても、解放されない
    - 1 つのスレッドが、同時に複数の `hazard_pointer` を持てる
    - C++26。解放の遅延は、ロック フリー構造のための基本的な手法

!!! info "このページを読む前に"
    [`atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::hazard_pointer {#hazard_pointer}

<span class="ver ver-26">C++26</span>

```cpp
class hazard_pointer {
 public:
  hazard_pointer() noexcept;                       // 空
  hazard_pointer(hazard_pointer&&) noexcept;
  template <class T>
  T* protect(const std::atomic<T*>& src) noexcept;
  template <class T>
  bool try_protect(T*& ptr, const std::atomic<T*>& src) noexcept;
  template <class T>
  void reset_protection(const T* ptr) noexcept;
  void reset_protection(std::nullptr_t = nullptr) noexcept;
  bool empty() const noexcept;
};
hazard_pointer make_hazard_pointer();
```

`protect` は、`src` の値を読み、保護の宣言を公開し、公開中に `src` が書き換わっていないことを確かめて返します。書き換わっていたら、読み直します。保護中のポインターが指す先は、他のスレッドが `retire` しても、解放されません。

使い終えたら `reset_protection()` か、`hazard_pointer` のデストラクターで、保護を外します。

オブジェクトの側は、`hazard_pointer_obj_base<T>` を継承します。`retire()` を呼ぶと、誰にも保護されていなくなってから、実際に解放されます。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
struct Node : std::hazard_pointer_obj_base<Node> {
  int value;
  std::atomic<Node*> next{nullptr};
};

std::atomic<Node*> head;

int ReadHead() {
  std::hazard_pointer hp = std::make_hazard_pointer();
  Node* p = hp.protect(head);       // 保護しながら読む
  return p ? p->value : -1;         // 保護中は、他のスレッドが retire しても解放されない
}

void RemoveHead() {
  Node* old = head.exchange(nullptr);
  if (old) old->retire();           // 保護されなくなってから解放される
}
```

## ゲームでの使いどころ

ロック フリーのキューやスタックを自作するときの、ノードの安全な解放に使います。ゲームの通常の開発で、直接使うことはまれです。

## よくあるミス

??? failure "protect せずにポインターを読み続ける"
    別のスレッドが解放すると、解放済みのメモリを読みます。

??? failure "retire せずに delete する"
    保護中のスレッドがいても、解放してしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hazard_pointer_obj_base`](hazard_pointer_obj_base.md) | 保護される側が継承する |
| [`make_hazard_pointer`](make_hazard_pointer.md) | hazard_pointer を作る |
| [`rcu_domain`](rcu_domain.md) | 別の解放の遅延方式 |
| [`atomic`](atomic.md) | 読み書きの基本 |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::hazard_pointer](https://cpprefjp.github.io/reference/hazard_pointer/hazard_pointer.html)
- [cppreference: std::hazard_pointer](https://en.cppreference.com/w/cpp/thread/hazard_pointer)
