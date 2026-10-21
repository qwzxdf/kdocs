---
title: std::is_trivially_copyable
summary: "`memcpy` で安全にコピーできる型かを調べる。"
order: 5
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_copyable

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::is_trivially_copyable_v<T>` は、**型 T が `memcpy` でバイト単位にコピーしても安全か**を調べます。ファイルやネットワークへバイナリのまま書き出せる型かの確認に使います。`std::string` や `vector` は `false` です。

!!! tip "ポイント"
    - ポインターを含む型も、`true` になりうる（意味は壊れる）。
    - `static_assert` で、書き出す型を守る。
    - `std::bit_cast` や `memcpy` を使う前の確認に。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_trivially_copyable_v {#is_trivially_copyable}

```cpp
template <class T>
inline constexpr bool is_trivially_copyable_v;
```

- `memcpy` でビットをそのままコピーしてよい型。int、float、それらだけの構造体は true。string、vector、仮想関数を持つクラスは false

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Pod {
  int a;
  float b;
};

int main() {
  std::println("{} {}", std::is_trivially_copyable_v<Pod>, std::is_trivially_copyable_v<std::string>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの構造体を、そのままファイルに書いてよいか | `static_assert(std::is_trivially_copyable_v<SaveData>)` |

## よくあるミス

??? failure "ポインターを含むのに true"
    コピーできても、ポインターの指す先は別の環境で無効です。ポインターは書き出しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_aggregate`](is_aggregate.md) | 集成体か |
| [`std::bit_cast`](../../numeric/bit/bit_cast.md) | この条件が必要 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] memcpy で安全か
    - [x] バイナリ保存の前に static_assert
    - [x] ポインターの中身は別問題

## 関連ページ

- [cpprefjp: std::is_trivially_copyable](https://cpprefjp.github.io/reference/type_traits/is_trivially_copyable.html)
- [cppreference: std::is_trivially_copyable](https://en.cppreference.com/w/cpp/types/is_trivially_copyable)
