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

`std::type_index` は、**`std::type_info` をコンテナのキーにできるようにした包みの型**です。`std::type_info` はコピーできませんが、`type_index` はコピーでき、`std::map` や `std::unordered_map` のキーに使えます。「型ごとの設定」を引く表を作るときに便利です。

!!! tip "ポイント"
    - `std::unordered_map<std::type_index, T>` が使える（ハッシュも用意されている）。
    - `typeid(型)` から暗黙に作れる。
    - 型ごとのシステム・サービスの登録表（サービスロケーター）に使える。

## 関数の詳しい説明

### std::type_index {#type_index}

```cpp
class type_index {
 public:
  type_index(const std::type_info&) noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ti` | `type_info` | 包みたい型情報 |

- 戻り値: （キーにできる型）
- 計算量: O(1)

```cpp
#include <print>
#include <string>
#include <typeindex>
#include <unordered_map>

int main() {
  std::unordered_map<std::type_index, std::string> names;
  names[typeid(int)] = "整数";
  names[typeid(float)] = "小数";
  std::println("{}", names[typeid(int)]);
}
```

```text title="実行結果"
整数
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 型ごとに登録するサービス（ECS のコンポーネント種類） | `std::unordered_map<std::type_index, Pool*>` |

## よくあるミス

??? failure "RTTI を切った環境で使う"
    RTTI が必要です。無効にする場合は、自前の型 ID の仕組みを作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::type_info`](type_info.md) | 包む前の型 |
| [`typeid`](typeid.md) | 型情報を得る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] type_info をキーにできる
    - [x] unordered_map のキーに使える
    - [x] RTTI が必要

## 関連ページ

- [cpprefjp: std::type_index](https://cpprefjp.github.io/reference/typeindex/type_index.html)
- [cppreference: std::type_index](https://en.cppreference.com/w/cpp/types/type_index)
