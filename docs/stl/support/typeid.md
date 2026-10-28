---
title: typeid
summary: "式や型の「実際の型」を、実行時に調べる演算子。"
order: 10
group: 実行時の型情報（<typeinfo>）
tags:
  - 型・言語サポート
---

# typeid

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <typeinfo>`
</div>

式や型から、型の情報（`std::type_info`）を取り出す演算子が `typeid` です。仮想関数を持つクラスのオブジェクトに使うと、実行時に本当の型が分かります。

!!! tip "ポイント"
    - `typeid(式)` または `typeid(型)` で `std::type_info` を取る
    - 多態的な型への参照・`*ポインター` は、動的な型を返す
    - ヌルのポインターを `*` したものに使うと `bad_typeid` が投げられる
    - `<typeinfo>` が必要

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### typeid {#typeid}

<span class="ver ver-98">C++98</span>

```cpp
const std::type_info& typeid(式 または 型);
```

演算子なので、関数のように見えますが、`<typeinfo>` を取り込まずに使うとコンパイルエラーです。

式に対して使うとき、式の型が仮想関数を持つクラスなら、実行時のオブジェクトの型を返します（動的な型）。そうでなければ、式の静的な型を返します。

コンパイラのオプションで RTTI を切ると、多態的な型の `typeid` は使えなくなります。

## 実際に動かしてみる

```cpp
#include <print>
#include <typeinfo>

struct Animal {
  virtual ~Animal() = default;
};
struct Dog : Animal {};

int main() {
  Dog dog;
  Animal& a = dog;
  std::println("静的な型 Animal では一致しない: {}", typeid(a) == typeid(Animal));
  std::println("動的な型 Dog と一致        : {}", typeid(a) == typeid(Dog));
}
```

```text title="実行結果"
静的な型 Animal では一致しない: false
動的な型 Dog と一致        : true
```

## ゲームでの使いどころ

多態的なオブジェクトの本当の型を調べます。ただし、型ごとの分岐は仮想関数で書くほうが設計として良いです。

## よくあるミス

??? failure "`<typeinfo>` を忘れる"
    取り込みます。

??? failure "ヌルのポインターを `*` して使う"
    `bad_typeid` が投げられます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`type_info`](type_info.md) | 戻り値の型 |
| [`bad_typeid`](exceptions/bad_typeid.md) | ヌルのときの例外 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `typeid` は型の情報を取る演算子
    - [x] 多態的な型は動的な型を返す
    - [x] `<typeinfo>` が必要

## 関連ページ

- [cpprefjp: typeid](https://cpprefjp.github.io/reference/typeinfo/type_info.html)
- [cppreference: typeid](https://en.cppreference.com/w/cpp/language/typeid)
