---
title: std::owner_hash
summary: "shared_ptr / weak_ptr を、持ち主（制御ブロック）で数えたハッシュ値を作る。"
order: 900
tags:
  - メモリ
---

# std::owner_hash

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <memory>`
</div>

`std::unordered_map` のキーに `weak_ptr` や `shared_ptr` を使いたい。`owner_less` の順序版に対し、ハッシュの版が C++26 の `std::owner_hash` で、制御ブロックのアドレスからハッシュ値を作ります。同じ所有権を共有していれば、`shared_ptr` と `weak_ptr` で同じ値になります。

!!! tip "ポイント"
    - 制御ブロックのアドレスを元にしたハッシュ値
    - `unordered_map` の `Hash` に指定する
    - `owner_equal` と組で使う
    - C++26

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::owner_hash {#owner_hash}

<span class="ver ver-26">C++26</span>

```cpp
struct owner_hash {
  template <class T> std::size_t operator()(const std::shared_ptr<T>& s) const noexcept;
  template <class T> std::size_t operator()(const std::weak_ptr<T>& w) const noexcept;
  using is_transparent = /* 未規定 */;
};
```

`std::hash<std::shared_ptr<T>>` は、`get()` が返すポインターのハッシュです。所有権が同じでも、別のアドレスを指していると、値が違います。`owner_hash` は所有権で決まるので、`weak_ptr` と `shared_ptr` の両方で、同じ値になります。

`std::unordered_map<std::weak_ptr<T>, V, std::owner_hash, std::owner_equal>` のように指定します。

## 実際に動かしてみる

手元の MSVC は `std::owner_hash` に未対応なので、既存の `std::hash` との違いを確かめます。C++26 の環境では、`std::owner_hash()(a)` が、所有権で決まる値を返します。

```cpp
#include <functional>
#include <memory>
#include <print>

int main() {
  auto a = std::make_shared<int>(1);
  int other = 0;
  std::shared_ptr<int> alias(a, &other);  // 所有権は同じで、別のアドレスを指す

  std::hash<std::shared_ptr<int>> h;
  std::println("std::hash は、指す先で決まる: {}", h(a) != h(alias));

  // weak_ptr には std::hash がない。owner_hash があれば、キーにできる
  std::weak_ptr<int> w = a;
  std::println("weak_ptr がまだ有効: {}", !w.expired());
}
```

```text title="実行結果"
std::hash は、指す先で決まる: true
weak_ptr がまだ有効: true
```

## ゲームでの使いどころ

`weak_ptr` をキーにした `unordered_map` で使います。C++26 が使えない環境では、`owner_less` と `std::map` を使います。

## よくあるミス

??? failure "std::hash を使う"
    所有権ではなくポインターで決まります。

??? failure "owner_equal を忘れる"
    等値の判定が合わず、検索できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`owner_less`](owner_less.md) | 順序版 |
| [`owner_equal`](owner_equal.md) | 等値版 |
| `std::hash` | ポインターで決まる |

## コンパイラ対応

C++26 から使えます。手元の MSVC では未対応のことがあります。

## 関連ページ

- [cpprefjp: std::owner_hash](https://cpprefjp.github.io/reference/memory/owner_hash.html)
- [cppreference: std::owner_hash](https://en.cppreference.com/w/cpp/memory/owner_hash)
