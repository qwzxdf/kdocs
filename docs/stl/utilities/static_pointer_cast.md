---
title: std::static_pointer_cast
summary: "shared_ptr の指す先を、static_cast で別の型に変える（持ち主は共有）。"
order: 900
tags:
  - ユーティリティ
---

# std::static_pointer_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

`shared_ptr<Base>` を `shared_ptr<Derived>` に変えたいとき、`shared_ptr(static_cast<Derived*>(p.get()))` と書くと、**別々の持ち主**になって二重解放します。`static_pointer_cast` なら**同じ持ち主を共有したまま**型だけ変えられます。

!!! tip "ポイント"
    - 持ち主（制御ブロック）は共有される。
    - 生ポインタで作り直すと別の持ち主になり、二重解放になる。
    - `dynamic_pointer_cast` は実行時に型を確かめる。

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::static_pointer_cast {#static_pointer_cast}

```cpp
template <class T, class U>
shared_ptr<T> static_pointer_cast(const shared_ptr<U>& r) noexcept;
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

struct Base { virtual ~Base() = default; };
struct Derived : Base { int value = 42; };

int main() {
  std::shared_ptr<Base> b = std::make_shared<Derived>();
  auto d = std::static_pointer_cast<Derived>(b);
  std::println("{} {}", d->value, b.use_count());
}
```

```text title="実行結果"
42 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 基底クラスのポインタから派生クラスに | `std::static_pointer_cast<T>(p);` |

## よくあるミス

??? failure "型が違うオブジェクトに使う"
    `static_cast` と同じで、実際の型が合っていなくても通ります。確実でないなら `dynamic_pointer_cast` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dynamic_pointer_cast`](dynamic_pointer_cast.md) | 実行時に型を確かめる |
| [`shared_ptr`](shared_ptr.md) | 共有所有のスマートポインタ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主を共有したまま型を変える
    - [x] 生ポインタで作り直さない
    - [x] use_count が増える

## 関連ページ

- [cpprefjp: std::static_pointer_cast](https://cpprefjp.github.io/reference/memory/static_pointer_cast.html)
- [cppreference: std::static_pointer_cast](https://en.cppreference.com/w/cpp/memory/static_pointer_cast)
