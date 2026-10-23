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

`std::type_info` は、**型の情報を持つクラス**で、`typeid` が返します。`==` で同じ型かを比べたり、`name()` で名前を取ったり、`hash_code()` でハッシュ値を取ったりできます。コピーできないので、`std::type_index` で包んでコンテナのキーにします。

!!! tip "ポイント"
    - `name()` の文字列は実装依存（GCC は壊れた形、MSVC は読める形）。
    - `hash_code()` は同じ型で同じ値になる（実行ごとには変わりうる）。
    - コンテナのキーにしたいなら [`type_index`](type_index.md)。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::type_info {#type_info}

```cpp
class type_info {
 public:
  const char* name() const noexcept;
  size_t hash_code() const noexcept;
  bool operator==(const type_info&) const noexcept;
};
```

- 戻り値: 型の名前・ハッシュ値・比較
- 計算量: O(1)

```cpp
#include <print>
#include <typeinfo>

int main() {
  std::println("{} {}", typeid(int) == typeid(int), typeid(int).hash_code() == typeid(long).hash_code());
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| エディタで、コンポーネントの型を見分ける | `typeid(*component) == typeid(Mesh)` |

## よくあるミス

??? failure "name() の文字列を比べる"
    実装によって違う文字列です。比較は `==` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`typeid`](typeid.md) | 型情報を得る演算子 |
| [`type_index`](type_index.md) | キーにできる包み |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型の情報を持つ
    - [x] name は実装依存
    - [x] キーにするなら type_index

## 関連ページ

- [cpprefjp: std::type_info](https://cpprefjp.github.io/reference/typeinfo/type_info.html)
- [cppreference: std::type_info](https://en.cppreference.com/w/cpp/types/type_info)
