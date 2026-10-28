---
title: std::type_info
summary: "型の情報（名前・同じ型かの比較）を持つクラス。"
order: 11
group: 実行時の型情報（<typeinfo>）
tags:
  - 型・言語サポート
---

# std::type_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <typeinfo>`
</div>

実行時に、オブジェクトの本当の型を調べたい。`typeid(式)` が返す `std::type_info` は、<strong>型の情報を表すオブジェクト</strong>で、型どうしが同じかを比べられます。

!!! tip "ポイント"
    - `typeid(式)` や `typeid(型)` が返す
    - `==` / `!=` で、2 つの型が同じか比べられる
    - `name()` で型の名前を取れる（形式は実装依存）
    - 仮想関数を持つクラスなら、動的な型が分かる

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::type_info {#type_info}

<span class="ver ver-98">C++98</span>

```cpp
class type_info {
 public:
  bool operator==(const type_info& rhs) const noexcept;
  const char* name() const noexcept;
  std::size_t hash_code() const noexcept;
};
```

`typeid` は、静的な型か、多態的な型（仮想関数を持つクラス）の動的な型を返します。ポインターの `typeid(*p)` は、`p` が指す実際のオブジェクトの型を返します。

`name()` の文字列は、実装によって違います（GCC は "i"、MSVC は "int" のように）。表示以外に使ってはいけません。型の比較は `==` で行います。

`type_info` のコピーはできません。コンテナのキーに使うなら、`std::type_index` で包みます。

## 実際に動かしてみる

```cpp
#include <print>
#include <typeinfo>

struct Base {
  virtual ~Base() = default;
};
struct Derived : Base {};

int main() {
  Base* p = new Derived;
  std::println("typeid(int) == typeid(int)   : {}", typeid(int) == typeid(int));
  std::println("typeid(int) == typeid(float) : {}", typeid(int) == typeid(float));
  std::println("実際の型は Derived          : {}", typeid(*p) == typeid(Derived));
  delete p;
}
```

```text title="実行結果"
typeid(int) == typeid(int)   : true
typeid(int) == typeid(float) : false
実際の型は Derived          : true
```

## ゲームでの使いどころ

デバッグで型の名前を出力します。

```cpp
std::println("{}", typeid(*component).name());   // 名前は実装依存
```

型ごとの処理を分けるなら、仮想関数のほうが適しています。

## よくあるミス

??? failure "`name()` の形式が環境で同じだと思う"
    表示だけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`type_index`](type_index.md) | コンテナのキーにできる |
| [`typeid`](typeid.md) | 演算子 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `type_info` は型の情報を表す
    - [x] `==` で比較できる
    - [x] `name()` は実装依存

## 関連ページ

- [cpprefjp: std::type_info](https://cpprefjp.github.io/reference/typeinfo/type_info.html)
- [cppreference: std::type_info](https://en.cppreference.com/w/cpp/types/type_info)
