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

空のハザードポインタを作ります。作ったものに `protect()` で、読みたいオブジェクトを保護させます。

!!! tip "ポイント"
    - 戻り値で `hazard_pointer` を受け取る。
    - 作るのにはコストがかかるので、使い回すとよい。
    - C++26。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::make_hazard_pointer {#make_hazard_pointer}

```cpp
hazard_pointer make_hazard_pointer();
```

- 戻り値: 新しい `hazard_pointer`
- 計算量: 実装依存


## 実際に動かしてみる

```cpp
// 例（概念）: ロックなしのデータ構造の読み取りを始める前に作る
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが圧倒的に多い共有データの管理 | ロックなしのデータ構造の読み取りを始める前に作る |

## よくあるミス

??? failure "読み取りごとに作る"
    作るコストがかかります。スレッドごとに使い回します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hazard_pointer`](hazard_pointer.md) | ハザードポインタ |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ハザードポインタを作る
    - [x] 読み取りをロックなしで行う仕組み
    - [x] C++26

## 関連ページ

- [cpprefjp: std::make_hazard_pointer](https://cpprefjp.github.io/reference/hazard_pointer/make_hazard_pointer.html)
- [cppreference: std::make_hazard_pointer](https://en.cppreference.com/w/cpp/thread/make_hazard_pointer)
