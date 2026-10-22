---
title: std::reinterpret_pointer_cast
summary: "shared_ptr の指す先を、reinterpret_cast で別の型に見せる（持ち主は共有）。"
order: 900
tags:
  - ユーティリティ
---

# std::reinterpret_pointer_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

メモリの内容を別の型として見たいとき、`shared_ptr` を `reinterpret_cast` するには持ち主を共有したままにする必要があります。`reinterpret_pointer_cast` は、持ち主を共有したまま `reinterpret_cast` します。

!!! tip "ポイント"
    - 持ち主（制御ブロック）は共有される。
    - 生ポインタで作り直すと別の持ち主になり、二重解放になる。
    - `dynamic_pointer_cast` は実行時に型を確かめる。

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::reinterpret_pointer_cast {#reinterpret_pointer_cast}

```cpp
template <class T, class U>
shared_ptr<T> reinterpret_pointer_cast(const shared_ptr<U>& r) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 変換後の型 |
| `r` | shared_ptr<U> | 変換元 |

- 戻り値: 変換後の `shared_ptr<T>`（持ち主は共有）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  auto u = std::make_shared<unsigned>(1);
  auto b = std::reinterpret_pointer_cast<unsigned char>(u);
  std::println("{}", u.use_count());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| const の外し方を持ち主を保ったまま | `std::reinterpret_pointer_cast<T>(p);` |

## よくあるミス

??? failure "型の別名規則に反する読み書き"
    `reinterpret_cast` と同じ制約があります。安全に読める保証があるときだけ使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dynamic_pointer_cast`](dynamic_pointer_cast.md) | 実行時に型を確かめる |
| [`shared_ptr`](shared_ptr.md) | 共有所有のスマートポインタ |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主を共有したまま型を変える
    - [x] 生ポインタで作り直さない
    - [x] use_count が増える

## 関連ページ

- [cpprefjp: std::reinterpret_pointer_cast](https://cpprefjp.github.io/reference/memory/reinterpret_pointer_cast.html)
- [cppreference: std::reinterpret_pointer_cast](https://en.cppreference.com/w/cpp/memory/reinterpret_pointer_cast)
