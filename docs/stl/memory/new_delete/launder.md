---
title: std::launder
summary: "オブジェクトの置き換えを、コンパイラに知らせてポインターを取り直す。"
order: 10
group: new / delete まわり
tags:
  - メモリ
---

# std::launder

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <new>`
</div>

オブジェクトを破棄して、同じ場所に、新しいオブジェクトを配置 new で作ったとき、古いポインタが新しいオブジェクトを指すとは限りません。コンパイラが、`const` メンバーなどの最適化のために、古い値を使い続けることがあるからです。`std::launder(p)` は、「`p` の指す場所に、新しいオブジェクトがある」とコンパイラに伝える関数です。

!!! tip "ポイント"
    - 同じ場所に作り直したオブジェクトを、古いポインタ経由で使うときに、新しいポインタを得る
    - `const` メンバーや参照メンバーを持つクラスで、特に必要
    - 実行時の動作は何もしない。コンパイラへの指示
    - 使う場面は少ない。`std::optional` など、標準ライブラリの内部が主

!!! info "このページを読む前に"
    [配置 new](placement_new.md) と [`destroy_at`](destroy_at.md) を先に読んでください。

## 関数の詳しい説明

### std::launder {#launder}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
[[nodiscard]] constexpr T* launder(T* p) noexcept;
```

`const` メンバーを持つクラスのオブジェクトは、その値が変わらないものとして最適化されます。同じ場所に別の値で作り直すと（配置 new）、古いポインタを通したアクセスは、古い値のまま読まれる可能性があります。

配置 new の戻り値のポインタは、新しいオブジェクトを指すので、それを使えば問題ありません。`launder` が必要なのは、古いポインタや、`unsigned char` の領域からの `reinterpret_cast` の結果など、新しいオブジェクトを直接指していないポインタを使うときです。

`p` の指す場所に、`T` 型のオブジェクトが実際に生存していなければ、未定義動作です。

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

struct Config {
  const int level;  // const メンバー
};

int main() {
  Config* c = new Config{1};
  std::println("{}", c->level);

  // 同じ場所に作り直す
  c->~Config();
  new (c) Config{2};

  // 古いポインタ c を通して読むなら launder を通す
  std::println("{}", std::launder(c)->level);

  c->~Config();
  ::operator delete(c);
}
```

```text title="実行結果"
1
2
```

## ゲームでの使いどころ

自作の `optional` や `variant` のような、型消去のバッファの上にオブジェクトを作る実装で使います。

## よくあるミス

??? failure "生存していないオブジェクトに使う"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [配置 new](placement_new.md) | 再配置する |
| [`construct_at`](construct_at.md) | 作る |
| `std::start_lifetime_as` | C++23。バイト列を型として扱う |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::launder](https://cpprefjp.github.io/reference/new/launder.html)
- [cppreference: std::launder](https://en.cppreference.com/w/cpp/memory/new/launder)
