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

ハザードポインタは、ロックなしのデータ構造で、「いま読んでいるオブジェクトを他のスレッドに破棄されない」ように守る仕組みです。`hazard_pointer` に読みたいオブジェクトを登録（保護）してから読みます。

!!! tip "ポイント"
    - `protect(src)` で読みたいポインタを保護する。
    - `reset_protection()` で保護を解く。
    - C++26。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::hazard_pointer {#hazard_pointer}

```cpp
class hazard_pointer {
 public:
  template <class T> T* protect(const std::atomic<T*>& src) noexcept;
  void reset_protection() noexcept;
};
```

- 戻り値: 保護しているポインタを返す
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: ロックなしのキューで、読み取り中のノードを守る
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | ロックなしのキューで、読み取り中のノードを守る |

## よくあるミス

??? failure "保護せずに読む"
    別のスレッドが破棄すると壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hazard_pointer_obj_base`](hazard_pointer_obj_base.md) | 守られる側の基底クラス |
| [`make_hazard_pointer`](make_hazard_pointer.md) | 作る関数 |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 別のスレッドが使用中のオブジェクトを「使っている」と宣言する印
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::hazard_pointer](https://cpprefjp.github.io/reference/hazard_pointer/hazard_pointer.html)
- [cppreference: std::hazard_pointer](https://en.cppreference.com/w/cpp/thread/hazard_pointer)
