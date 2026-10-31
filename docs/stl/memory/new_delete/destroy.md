---
title: std::destroy
summary: "範囲のオブジェクトのデストラクタを呼ぶ（メモリは返さない）。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::destroy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

生のメモリに作った複数のオブジェクトを、まとめて壊したい。`std::destroy(first, last)` は、`[first, last)` の各要素に、`destroy_at` を呼びます。

!!! tip "ポイント"
    - 範囲 `[first, last)` の全要素のデストラクターを呼ぶ
    - メモリは解放しない
    - 壊す順序は規定されていない
    - 自明なデストラクターの型なら、何もしない

!!! info "このページを読む前に"
    [`destroy_at`](destroy_at.md) を先に読んでください。

## 関数の詳しい説明

### std::destroy {#destroy}

<span class="ver ver-17">C++17</span>

```cpp
template <class ForwardIt>
constexpr void destroy(ForwardIt first, ForwardIt last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | 前方イテレータ | 壊す範囲 |

壊す順序は、先頭から末尾へとは限りません。順序に依存するデストラクターは、書かないようにします。

`uninitialized_*` 系のアルゴリズムで作った範囲を壊すときの、対になる関数です。

範囲のうち一部が作られていない状態では使えません。作られていない領域のデストラクターを呼ぶと、未定義動作です。

## 実際に動かしてみる

```cpp
#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  Tracer(const Tracer&) { ++alive; }
  Tracer(Tracer&&) noexcept { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 3];
  auto* first = reinterpret_cast<Tracer*>(buf);
  for (int i = 0; i < 3; ++i) std::construct_at(first + i);
  std::println("作った: {}", Tracer::alive);

  std::destroy(first, first + 3);
  std::println("壊した: {}", Tracer::alive);
}
```

```text title="実行結果"
作った: 3
壊した: 0
```

## ゲームでの使いどころ

自作のコンテナで、`clear()` や破棄のときに、範囲をまとめて壊します。

## よくあるミス

??? failure "作っていない部分を含める"
    未定義動作です。作った範囲だけを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`destroy_at`](destroy_at.md) | 1 つだけ壊す |
| [`destroy_n`](destroy_n.md) | 個数を指定する |
| [`uninitialized_fill`](uninitialized_fill.md) | 範囲に作る |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::destroy](https://cpprefjp.github.io/reference/memory/destroy.html)
- [cppreference: std::destroy](https://en.cppreference.com/w/cpp/memory/destroy)
