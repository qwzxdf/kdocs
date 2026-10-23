---
title: std::enable_shared_from_this
summary: "自分自身を指す shared_ptr を、メンバ関数の中で安全に作る。"
order: 53
tags:
  - ユーティリティ
---

# std::enable_shared_from_this

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::enable_shared_from_this<T>` は、**クラスのメンバ関数の中で、「自分を指す `shared_ptr`」を作れるようにする**基底クラスです。`this` から直接 `shared_ptr` を作ると、同じオブジェクトを 2 つの参照カウントで管理してしまい、二重解放になります。それを防ぎます。

!!! tip "ポイント"
    - クラスが `public std::enable_shared_from_this<自分>` を継承する。
    - `shared_from_this()` は `shared_ptr` を、`weak_from_this()`（C++17）は `weak_ptr` を返す。
    - **すでに `shared_ptr` で管理されているときだけ**使える（コンストラクタの中では使えない）。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::enable_shared_from_this {#shared_from_this}

```cpp
template <class T>
class enable_shared_from_this {
 public:
  std::shared_ptr<T> shared_from_this();
  std::weak_ptr<T> weak_from_this() noexcept;
};
```

- クラスがこれを継承すると、メンバ関数の中で「自分を指す shared_ptr」を作れます（`this` から shared_ptr を作ると二重管理になるため）
- **shared_ptr で管理されているときだけ**使えます

```cpp
#include <memory>
#include <print>
#include <vector>

class Unit : public std::enable_shared_from_this<Unit> {
 public:
  void Register(std::vector<std::weak_ptr<Unit>>& list) {
    list.push_back(weak_from_this());
  }
};

int main() {
  std::vector<std::weak_ptr<Unit>> registry;
  auto unit = std::make_shared<Unit>();
  unit->Register(registry);
  std::println("登録 {} / 生きている？ {}", registry.size(), !registry[0].expired());
}
```

```text title="実行結果"
登録 1 / 生きている？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自分を、非同期処理やイベントの購読者に登録する | `events.Subscribe(weak_from_this())` |
| ツリーの子が、親への `weak_ptr` を持つ | `child->parent = weak_from_this();` |

## よくあるミス

??? failure "shared_ptr になる前に呼ぶ"
    コンストラクタの中や、`shared_ptr` で包む前に `shared_from_this()` を呼ぶと、`std::bad_weak_ptr` の例外になります。

??? failure "this から shared_ptr を作る"
    `std::shared_ptr<T>(this)` は、別の管理者を作ってしまい二重解放になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shared_ptr`](shared_ptr.md) | 本体 |
| [`std::weak_ptr`](weak_ptr.md) | `weak_from_this()` が返す |

## コンパイラ対応

C++11 から使えます。`weak_from_this` は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自分を指す `shared_ptr` を安全に作る
    - [x] 継承して使う
    - [x] `shared_ptr` で管理されているときだけ

## 関連ページ

- [cpprefjp: std::enable_shared_from_this](https://cpprefjp.github.io/reference/memory/enable_shared_from_this.html)
- [cppreference: std::enable_shared_from_this](https://en.cppreference.com/w/cpp/memory/enable_shared_from_this)
