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

`shared_ptr<Base>` の実体が `Derived` かどうか、実行してみないと分からないことがあります。`std::dynamic_pointer_cast<Derived>(sp)` は、実行時に型を検査して、`Derived` なら所有権を共有した `shared_ptr<Derived>` を返し、違えば空の `shared_ptr` を返します。`dynamic_cast` の、`shared_ptr` 版です。

!!! tip "ポイント"
    - 型が合えば、所有権を共有した `shared_ptr<T>` を返す
    - 合わなければ、空の `shared_ptr`（`nullptr` と比べられる）
    - `Base` が仮想関数を持つ（多態的な）型である必要がある
    - 型が確実なら、速い `static_pointer_cast`

!!! info "このページを読む前に"
    [`std::static_pointer_cast`](static_pointer_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::dynamic_pointer_cast {#dynamic_pointer_cast}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class U>
std::shared_ptr<T> dynamic_pointer_cast(const std::shared_ptr<U>& r) noexcept;
```

`dynamic_cast<T*>(r.get())` が成功すれば、その結果を `r` と所有権を共有する `shared_ptr` にして返します。失敗すれば、空の `shared_ptr` です。

`dynamic_cast` を使うので、RTTI（実行時型情報）が有効でなければなりません。ゲームのビルドで RTTI を切っている場合、この関数は使えません。

実行時の検査があるぶん、`static_pointer_cast` より遅くなります。毎フレーム大量に呼ぶ場所では、避けるか、型を判別する別の仕組み（型 ID を持たせる）を使います。

`T` が参照型や、多態的でない型に変換するときの制約は、`dynamic_cast` と同じです。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

struct Enemy { virtual ~Enemy() = default; };
struct Slime : Enemy { int hp = 5; };
struct Dragon : Enemy { int hp = 500; };

int main() {
  std::shared_ptr<Enemy> e = std::make_shared<Slime>();

  // Slime として扱えるか
  if (auto s = std::dynamic_pointer_cast<Slime>(e)) {
    std::println("Slime: hp={}", s->hp);
  }

  // Dragon ではない: 空が返る
  auto d = std::dynamic_pointer_cast<Dragon>(e);
  std::println("Dragon に変換できた: {}", d != nullptr);
  std::println("use_count: {}", e.use_count());  // 失敗した変換は数えない
}
```

```text title="実行結果"
Slime: hp=5
Dragon に変換できた: false
use_count: 1
```

`s` は `if` の中でだけ生きるので、`if` を出ると `use_count` は 1 に戻ります。

## ゲームでの使いどころ

敵の種類ごとの処理を分けるとき、`shared_ptr<Enemy>` から、`Slime` かどうかを調べて処理する、といった場面で使います。種類が多いなら、仮想関数か `std::visit` に置き換えるほうが整理されます。

## よくあるミス

??? failure "RTTI を無効にしたビルドで使う"
    コンパイルできるか、実行時に失敗します。RTTI の設定を確かめます。

??? failure "空を確かめずに使う"
    失敗すると空です。`if (auto p = ...)` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`static_pointer_cast`](static_pointer_cast.md) | 検査しない。速い |
| `dynamic_cast` | 生ポインタ版 |
| [`std::visit`](visit.md) | `variant` で型を分ける |

## コンパイラ対応

C++11 から使えます。RTTI が必要です。

## 関連ページ

- [cpprefjp: std::dynamic_pointer_cast](https://cpprefjp.github.io/reference/memory/pointer_cast.html)
- [cppreference: std::dynamic_pointer_cast](https://en.cppreference.com/w/cpp/memory/shared_ptr/pointer_cast)
