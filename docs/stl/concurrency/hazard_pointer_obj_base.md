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

ハザードポインタで守るオブジェクトは、誰も保護していないことを確かめてから破棄する必要があります。`hazard_pointer_obj_base<T>` を継承すると、`retire()` で「保護が外れたら破棄して」と頼めます。

!!! tip "ポイント"
    - `class Node : public std::hazard_pointer_obj_base<Node>` と継承する。
    - `retire()` が、保護が外れたら破棄する。
    - C++26。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::hazard_pointer_obj_base {#hazard_pointer_obj_base}

```cpp
template <class T, class D = default_delete<T>>
class hazard_pointer_obj_base {
 public:
  void retire(D d = D()) noexcept;
};
```

- 戻り値: `retire()` で破棄を予約する
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: ロックなしのキューのノードを、安全に破棄する
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | ロックなしのキューのノードを、安全に破棄する |

## よくあるミス

??? failure "`delete` を直接呼ぶ"
    他のスレッドが保護していると壊れます。`retire()` に任せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hazard_pointer`](hazard_pointer.md) | 保護する側 |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ハザードポインタで守るオブジェクトが継承する基底クラス
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::hazard_pointer_obj_base](https://cpprefjp.github.io/reference/hazard_pointer/hazard_pointer_obj_base.html)
- [cppreference: std::hazard_pointer_obj_base](https://en.cppreference.com/w/cpp/thread/hazard_pointer_obj_base)
