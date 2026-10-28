---
title: std::type_index
summary: "`type_info` を、コンテナのキーにできるようにした包み。"
order: 12
group: 実行時の型情報（<typeinfo>）
tags:
  - 型・言語サポート
---

# std::type_index

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <typeindex>`
</div>

型ごとにデータを管理したい。たとえば「型 → 処理」の表を作りたい。`std::type_info` はコピーできず、`std::map` のキーにできません。`std::type_index` は、<strong>`type_info` を包んで、コンテナのキーにできるようにした型</strong>です。

!!! tip "ポイント"
    - `std::type_index(typeid(T))` で作る
    - `==` と `<` で比べられる。`std::hash` にも対応する
    - `std::map` や `std::unordered_map` のキーに使える
    - 型ごとの処理やリソースの管理に使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::type_index {#type_index}

<span class="ver ver-11">C++11</span>

```cpp
class type_index {
 public:
  type_index(const std::type_info& info) noexcept;
  bool operator==(const type_index& rhs) const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `info` | `type_info` | 包む型情報 |

`type_info` への参照を保持し、比較・ハッシュ・コピーができるようにした型です。`std::unordered_map<std::type_index, ...>` にすると、型から値を引く表を作れます。

ECS のコンポーネントを、型で探すテーブルなどで使われます。ただし、実行時の型情報（RTTI）を有効にする必要があります。ゲームでは RTTI を切る方針の場合も多く、その場合は、自前の型 ID（テンプレートで連番を振る）を使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <typeindex>
#include <unordered_map>

int main() {
  std::unordered_map<std::type_index, int> counts;
  counts[std::type_index(typeid(int))] += 1;
  counts[std::type_index(typeid(float))] += 1;
  counts[std::type_index(typeid(int))] += 1;
  std::println("int の数   = {}", counts[std::type_index(typeid(int))]);
  std::println("種類の数   = {}", counts.size());
}
```

```text title="実行結果"
int の数   = 2
種類の数   = 2
```

## ゲームでの使いどころ

型をキーにして、データを引きます。

```cpp
std::unordered_map<std::type_index, std::unique_ptr<System>> systems;
systems[std::type_index(typeid(PhysicsSystem))] = std::make_unique<PhysicsSystem>();
```

## よくあるミス

??? failure "RTTI を切った環境で使えない"
    自前の型 ID を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`type_info`](type_info.md) | 型の情報 |
| [`typeid`](typeid.md) | 演算子 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `type_index` は `type_info` をコンテナのキーにできる形にしたもの
    - [x] `map` / `unordered_map` のキーに使える
    - [x] RTTI が必要

## 関連ページ

- [cpprefjp: std::type_index](https://cpprefjp.github.io/reference/typeindex/type_index.html)
- [cppreference: std::type_index](https://en.cppreference.com/w/cpp/types/type_index)
