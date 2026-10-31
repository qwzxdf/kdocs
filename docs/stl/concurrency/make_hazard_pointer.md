---
title: std::make_hazard_pointer
summary: "ハザードポインタを作る。"
order: 900
tags:
  - 並行処理
---

# std::make_hazard_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <hazard_pointer>`
</div>

`std::hazard_pointer` を作る関数が `std::make_hazard_pointer()` です。保護の宣言を置く場所を、内部の領域から割り当てて、空でない `hazard_pointer` を返します。

!!! tip "ポイント"
    - 空でない `hazard_pointer` を返す
    - 内部の領域を確保するので、例外を投げることがある
    - 既定の構築の `hazard_pointer` は空で、`protect` を呼べない
    - 返した `hazard_pointer` は、ムーブできる

!!! info "このページを読む前に"
    [`hazard_pointer`](hazard_pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::make_hazard_pointer {#make_hazard_pointer}

<span class="ver ver-26">C++26</span>

```cpp
std::hazard_pointer make_hazard_pointer();
```

内部では、スレッドが使える保護の置き場（スロット）を取得します。足りなければ、新しく確保するので、`std::bad_alloc` を投げる可能性があります。

保護の置き場は、`hazard_pointer` のデストラクターで、返されます。長い間持ち続けると、他のスレッドが取れる置き場が減ります。読み取りが終わったら、すぐ破棄します。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
int Read(const std::atomic<Node*>& head) {
  std::hazard_pointer hp = std::make_hazard_pointer();   // 置き場を確保
  Node* p = hp.protect(head);
  return p ? p->value : -1;
}   // hp の破棄で、置き場が返される
```

## ゲームでの使いどころ

読み取りの関数の冒頭で作り、関数の終わりで破棄します。

## よくあるミス

??? failure "長く持ち続ける"
    置き場を占有します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hazard_pointer`](hazard_pointer.md) | 作られる型 |
| [`hazard_pointer_obj_base`](hazard_pointer_obj_base.md) | 保護される側 |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::make_hazard_pointer](https://cpprefjp.github.io/reference/hazard_pointer/make_hazard_pointer.html)
- [cppreference: std::make_hazard_pointer](https://en.cppreference.com/w/cpp/thread/make_hazard_pointer)
