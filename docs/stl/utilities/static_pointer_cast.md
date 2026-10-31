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

`std::shared_ptr<Base>` を持っていて、実体が `Derived` だと分かっているとき、`Derived` として使いたい。生のポインタなら `static_cast<Derived*>(p)` ですが、`shared_ptr` の中身だけを取り出して変換すると、参照カウントが別になり、二重に解放されます。`std::static_pointer_cast<Derived>(sp)` は、<strong>所有権を共有したまま</strong>、`static_cast` した型の `shared_ptr` を返します。

!!! tip "ポイント"
    - 参照カウントを共有する。元の `shared_ptr` と、同じ管理下
    - 変換は `static_cast` と同じ。実行時の検査はない
    - 実体が違う型だと未定義動作。確かでなければ `dynamic_pointer_cast`
    - 結果の `use_count` は 1 つ増える

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::static_pointer_cast {#static_pointer_cast}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class U>
std::shared_ptr<T> static_pointer_cast(const std::shared_ptr<U>& r) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 変換先の型 |
| `r` | `std::shared_ptr<U>` | 変換元 |

`static_cast<T*>(r.get())` の結果を、`r` と所有権を共有するポインタ（エイリアシング コンストラクター）として返します。`r` が空なら、空の `shared_ptr` です。

`static_cast` なので、継承の上向きと下向き、`void*` との変換ができます。下向き（`Base` → `Derived`）のとき、実体が本当に `Derived` かは、検査されません。違っていれば、未定義動作です。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

struct Base { virtual ~Base() = default; };
struct Derived : Base { int power = 7; };

int main() {
  std::shared_ptr<Base> base = std::make_shared<Derived>();
  std::println("変換前の use_count: {}", base.use_count());

  // 実体が Derived だと分かっているので、static で変換
  std::shared_ptr<Derived> d = std::static_pointer_cast<Derived>(base);
  std::println("変換後の use_count: {}", base.use_count());  // 共有される
  std::println("power = {}", d->power);
}
```

```text title="実行結果"
変換前の use_count: 1
変換後の use_count: 2
power = 7
```

## ゲームでの使いどころ

コンポーネントを `shared_ptr<Component>` で持つ設計で、型が確実に分かっている場面で、派生クラスとして使うときに使います。

## よくあるミス

??? failure "実体が違う型のとき"
    検査がないので、未定義動作です。確実でないなら、`dynamic_pointer_cast` です。

??? failure "get() で生ポインタを取り出して、別の shared_ptr に入れる"
    参照カウントが別になり、二重に解放されます。必ずキャスト関数を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dynamic_pointer_cast`](dynamic_pointer_cast.md) | 実行時に検査する |
| [`const_pointer_cast`](const_pointer_cast.md) | `const` を外す |
| [`reinterpret_pointer_cast`](reinterpret_pointer_cast.md) | ビット列として解釈し直す |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::static_pointer_cast](https://cpprefjp.github.io/reference/memory/static_pointer_cast.html)
- [cppreference: std::static_pointer_cast](https://en.cppreference.com/w/cpp/memory/static_pointer_cast)
