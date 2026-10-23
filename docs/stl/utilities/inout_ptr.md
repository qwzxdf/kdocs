---
title: std::inout_ptr
summary: "C のAPI に、既存のポインターを渡して、置き換えてもらう。"
order: 77
tags:
  - ユーティリティ
---

# std::inout_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <memory>`
</div>

`std::inout_ptr(smart_ptr)` は、**C のAPI が `T**` の引数を通して、既存のオブジェクトを受け取り、別のものに置き換えて返す**ような場合に使います。`realloc` のように「今の値を渡して、新しい値を受け取る」関数向けです。[`out_ptr`](out_ptr.md) は「出力だけ」、こちらは「入力と出力」です。

!!! tip "ポイント"
    - `Replace(std::inout_ptr(p));` の形。
    - `unique_ptr` が持っていた値を、API 側に引き渡す（所有権が一旦 API に渡る）。
    - API が失敗したときの挙動に注意する。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::inout_ptr {#inout_ptr}

```cpp
template <class Smart, class... Args>
auto inout_ptr(Smart& s, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | スマートポインター | 入力と出力に使うもの |

- 戻り値: `T**` として使える包み
- 計算量: O(1)

```cpp
#include <memory>
#include <print>

// C 風の API: 渡されたものを捨てて、新しいものに置き換える
void Replace(int** p) {
  delete *p;
  *p = new int(9);
}

int main() {
  std::unique_ptr<int> p(new int(1));
  Replace(std::inout_ptr(p));
  std::println("{}", *p);
}
```

```text title="実行結果"
9
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| realloc 風の C のAPI を、スマートポインターで使う | `Resize(std::inout_ptr(p), new_size)` |

## よくあるミス

??? failure "API が解放しないのに使う"
    所有権が API に移る前提です。API の仕様を確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`out_ptr`](out_ptr.md) | 出力だけ |

## コンパイラ対応

C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力と出力に使う
    - [x] 所有権が API に渡る
    - [x] C++23

## 関連ページ

- [cpprefjp: std::inout_ptr](https://cpprefjp.github.io/reference/memory/inout_ptr.html)
- [cppreference: std::inout_ptr](https://en.cppreference.com/w/cpp/memory/inout_ptr_t)
