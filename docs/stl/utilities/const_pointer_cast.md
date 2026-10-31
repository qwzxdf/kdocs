---
title: std::const_pointer_cast
summary: "shared_ptr の指す先から const を外す（持ち主は共有）。"
order: 900
tags:
  - ユーティリティ
---

# std::const_pointer_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

`std::shared_ptr<const Player>` を持っているけれど、古い API が `Player*`（非 const）を要求する。`const` を外すための変換が `std::const_pointer_cast<Player>(sp)` です。`const_cast` の `shared_ptr` 版で、所有権を共有したまま、`const` を外した `shared_ptr` を返します。

!!! tip "ポイント"
    - `const` や `volatile` だけを外す（付ける）変換
    - 所有権を共有する。参照カウントが増える
    - 元のオブジェクトが本当に `const` で作られていたら、書き換えは未定義動作
    - 外す必要が出る設計を、見直すほうが先

!!! info "このページを読む前に"
    [`std::static_pointer_cast`](static_pointer_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::const_pointer_cast {#const_pointer_cast}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class U>
std::shared_ptr<T> const_pointer_cast(const std::shared_ptr<U>& r) noexcept;
```

`const_cast<T*>(r.get())` の結果を、`r` と所有権を共有する `shared_ptr` として返します。`T` は、`U` から `const` / `volatile` の違いだけがある型です。

もとのオブジェクトが、初めから `const` として作られている場合（`const Player p;` の `p` を指していたなど）、`const` を外して書き換えると、未定義動作です。`std::make_shared<const Player>(...)` で作られたものを、`const_pointer_cast` で外すのも同じです。

`std::shared_ptr<Player>` から `std::shared_ptr<const Player>` への変換は、暗黙にできます。`const` を付ける方向は、安全なので、キャストが要りません。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

struct Player { int hp = 10; };

int main() {
  // 非 const で作ったオブジェクトを、const として共有する
  std::shared_ptr<Player> p = std::make_shared<Player>();
  std::shared_ptr<const Player> cp = p;  // const を付けるのは暗黙にできる

  // const を外す
  std::shared_ptr<Player> back = std::const_pointer_cast<Player>(cp);
  back->hp = 99;
  std::println("hp = {}", p->hp);
  std::println("use_count = {}", p.use_count());
}
```

```text title="実行結果"
hp = 99
use_count = 3
```

## ゲームでの使いどころ

`const` に対応していない古いライブラリの API に、`shared_ptr<const T>` を渡すときに使います。できれば、ライブラリ側に `const` を付ける修正をします。

## よくあるミス

??? failure "const で作ったオブジェクトを書き換える"
    未定義動作です。もともと非 const で作られたものにだけ使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`static_pointer_cast`](static_pointer_cast.md) | 型の変換 |
| `const_cast` | 生ポインタ版 |
| `std::as_const` | 値を const 参照にする |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::const_pointer_cast](https://cpprefjp.github.io/reference/memory/const_pointer_cast.html)
- [cppreference: std::const_pointer_cast](https://en.cppreference.com/w/cpp/memory/const_pointer_cast)
