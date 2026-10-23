---
title: std::dynamic_pointer_cast
summary: "shared_ptr を、派生クラスの shared_ptr に変換する（static / const / reinterpret 版もある）。"
order: 54
tags:
  - ユーティリティ
---

# std::dynamic_pointer_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::dynamic_pointer_cast` は、**`shared_ptr` を、別の型の `shared_ptr` に変換する**関数で、`dynamic_cast` の `shared_ptr` 版です。基底クラスの `shared_ptr` から、本当の型（派生クラス）の `shared_ptr` を取り出すときに使います。キャストできなければ、空の `shared_ptr` が返ります。

!!! tip "ポイント"
    - `shared_ptr` 同士のキャストは、普通の `dynamic_cast<T*>(p.get())` ではなく、これを使う（参照カウントが共有される）。
    - 同じ仲間に `static_pointer_cast`、`const_pointer_cast`、`reinterpret_pointer_cast` がある。
    - `dynamic_pointer_cast` は、基底クラスに仮想関数が必要。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::dynamic_pointer_cast {#pointer_cast}

```cpp
template <class T, class U>
std::shared_ptr<T> dynamic_pointer_cast(const std::shared_ptr<U>& r) noexcept;
```

- `dynamic_cast` の shared_ptr 版。キャストできなければ空の shared_ptr を返します。`static_pointer_cast` もあります

```cpp
#include <memory>
#include <print>

struct Base {
  virtual ~Base() = default;
};
struct Boss : Base {
  int phase = 2;
};

int main() {
  std::shared_ptr<Base> obj = std::make_shared<Boss>();
  if (auto boss = std::dynamic_pointer_cast<Boss>(obj)) {
    std::println("ボス フェーズ {}", boss->phase);
  }
}
```

```text title="実行結果"
ボス フェーズ 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `shared_ptr<Entity>` の中から、ボスだけを取り出す | `std::dynamic_pointer_cast<Boss>(entity)` |

## よくあるミス

??? failure "生ポインタにキャストして shared_ptr を作る"
    `std::shared_ptr<Boss>(dynamic_cast<Boss*>(p.get()))` は別々の管理者になり二重解放です。必ず `dynamic_pointer_cast` を使います。

??? failure "キャストの失敗を調べない"
    失敗すると空の `shared_ptr` です。`if (auto boss = ...)` で確認してから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shared_ptr`](shared_ptr.md) | 本体 |
| `dynamic_cast` | 生ポインタ・参照のキャスト |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `shared_ptr` のキャストは専用の関数で
    - [x] 失敗すると空の `shared_ptr`
    - [x] `static` / `const` / `reinterpret` 版もある

## 関連ページ

- [cpprefjp: std::dynamic_pointer_cast](https://cpprefjp.github.io/reference/memory/pointer_cast.html)
- [cppreference: std::dynamic_pointer_cast](https://en.cppreference.com/w/cpp/memory/shared_ptr/pointer_cast)
