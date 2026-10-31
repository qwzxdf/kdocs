---
title: std::to_address
summary: "ポインターやイテレータ（スマートポインターなど）から、生のポインターを取る。"
order: 22
tags:
  - メモリ
---

# std::to_address

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

イテレータやスマート ポインターから、生のポインター（アドレス）を取り出したい。`&*it` と書くと、`it` が `end()` のときに、参照できない位置の参照を作ってしまい、未定義動作です。C++20 の `std::to_address(p)` は、間接参照せずに、生のポインターを取り出します。

!!! tip "ポイント"
    - ポインター風の型から、生のポインター `T*` を取る
    - 間接参照しないので、`end()` のイテレータにも使える
    - 生のポインターを渡すと、そのまま返す
    - `std::vector` や `std::string` のイテレータ、スマート ポインターに使える

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::to_address {#to_address}

<span class="ver ver-20">C++20</span>

```cpp
template <class T> constexpr T* to_address(T* p) noexcept;
template <class Ptr> constexpr auto to_address(const Ptr& p) noexcept;
```

`Ptr` が `std::pointer_traits<Ptr>::to_address` を持てばそれを呼び、なければ `p.operator->()` を使います。

連続した領域のイテレータ（`vector::iterator` など、C++20 の `contiguous_iterator`）なら、`to_address(it)` は、その要素のアドレスです。`it == v.end()` でも、そのアドレス（最後の要素の次）を返します。`&*it` は、これができません。

関数に生のポインターを渡すときに、イテレータの種類を気にせず書けます。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};

  auto it = v.begin() + 1;
  std::println("2 番目のアドレス: {}", std::to_address(it) == v.data() + 1);

  // end() でも安全
  std::println("end の位置: {}", std::to_address(v.end()) == v.data() + v.size());

  // スマート ポインターからも取れる
  auto sp = std::make_shared<int>(7);
  std::println("shared_ptr: {}", std::to_address(sp) == sp.get());
}
```

```text title="実行結果"
2 番目のアドレス: true
end の位置: true
shared_ptr: true
```

## ゲームでの使いどころ

C の API に、`vector` の途中の位置から続く領域を、生のポインターで渡すときに使います。

## よくあるミス

??? failure "&*it で end() を参照する"
    未定義動作です。`std::to_address(it)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`pointer_traits`](pointer_traits.md) | 元になる特性 |
| [`addressof`](../utilities/addressof.md) | オブジェクトのアドレス |
| `std::vector::data()` | 先頭のアドレス |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::to_address](https://cpprefjp.github.io/reference/memory/to_address.html)
- [cppreference: std::to_address](https://en.cppreference.com/w/cpp/memory/to_address)
