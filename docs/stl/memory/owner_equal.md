---
title: std::owner_equal
summary: "shared_ptr / weak_ptr が、同じ持ち主（制御ブロック）かを比べる。"
order: 900
tags:
  - メモリ
---

# std::owner_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <memory>`
</div>

`std::owner_less` が順序、`std::owner_hash` がハッシュなら、`std::owner_equal` は、所有権が等しいかどうかの判定です。C++26 で追加されました。`shared_ptr` と `weak_ptr` のどの組み合わせでも比べられます。

!!! tip "ポイント"
    - 2 つのスマート ポインターが、同じ所有権（制御ブロック）を共有するかを調べる
    - `shared_ptr` と `weak_ptr` を混ぜて比べられる
    - `owner_hash` と組で `unordered_map` に使う
    - C++26

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::owner_equal {#owner_equal}

<span class="ver ver-26">C++26</span>

```cpp
struct owner_equal {
  template <class T, class U>
  bool operator()(const std::shared_ptr<T>&, const std::shared_ptr<U>&) const noexcept;
  // weak_ptr との組み合わせも同様
  using is_transparent = /* 未規定 */;
};
```

メンバー関数の `owner_before` を使って、`!a.owner_before(b) && !b.owner_before(a)` で判定するのと同じです。

通常の `==` は、指す先のポインターで比べます。エイリアシングで別の部分を指していても、所有権が同じなら、`owner_equal` では等しいと判定されます。

## 実際に動かしてみる

手元の MSVC は `std::owner_equal` に未対応なので、同じ判定をする `owner_before` で確かめます。C++26 の環境では、`std::owner_equal()(a, w)` と書けます。

```cpp
#include <memory>
#include <print>

// owner_equal と同じ判定
template <class A, class B>
bool OwnerEqual(const A& a, const B& b) {
  return !a.owner_before(b) && !b.owner_before(a);
}

int main() {
  auto a = std::make_shared<int>(1);
  auto b = std::make_shared<int>(1);  // 値は同じでも別の所有権
  std::weak_ptr<int> w = a;

  std::println("a と w: {}", OwnerEqual(a, w));
  std::println("a と b: {}", OwnerEqual(a, b));

  // 別のアドレスを指していても、所有権が同じなら等しい
  int other = 0;
  std::shared_ptr<int> alias(a, &other);
  std::println("== は {} だが所有権は {}", a == alias, OwnerEqual(a, alias));
}
```

```text title="実行結果"
a と w: true
a と b: false
== は false だが所有権は true
```

## ゲームでの使いどころ

`weak_ptr` をキーにした `unordered_map` で、キーが同じオブジェクトを指すかの判定に使います。

## よくあるミス

??? failure "== で比べる"
    ポインターの比較です。所有権を比べるには `owner_equal` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`owner_hash`](owner_hash.md) | ハッシュ版 |
| [`owner_less`](owner_less.md) | 順序版 |
| `shared_ptr::owner_before` | 順序のメンバー関数 |

## コンパイラ対応

C++26 から使えます。手元の MSVC では未対応のことがあります。

## 関連ページ

- [cpprefjp: std::owner_equal](https://cpprefjp.github.io/reference/memory/owner_equal.html)
- [cppreference: std::owner_equal](https://en.cppreference.com/w/cpp/memory/owner_equal)
