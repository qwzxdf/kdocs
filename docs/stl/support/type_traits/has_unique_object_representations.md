---
title: std::has_unique_object_representations
summary: "同じ値なら必ず同じビット列になる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::has_unique_object_representations

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

2 つの値が等しいかをバイト列の比較（`memcmp`）で判定してよいかを知りたい。ハッシュ値をバイト列から作ってよいかも同じ問題です。`std::has_unique_object_representations` は、<strong>等しい値が必ず等しいビット列になるか</strong>を調べます。

!!! tip "ポイント"
    - `std::has_unique_object_representations_v<T>` は、`T` の値がビット表現と 1 対 1 に対応するか
    - パディングがあると `false`
    - `std::has_unique_object_representations<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `float` や `double` を含むと `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::has_unique_object_representations_v {#has_unique_object_representations}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
inline constexpr bool has_unique_object_representations_v = has_unique_object_representations<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

値が同じなら、メモリ上のビット列も必ず同じになる型が `true` です。`int` は `true` です。`float` は `+0.0` と `-0.0` が等しいのにビット列が違うので `false` です。メンバーの間にパディング（詰め物）が入る構造体も、詰め物の中身が決まっていないので `false` になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Pair {
  int a;
  int b;
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                                -> {}", std::has_unique_object_representations_v<int>);
  std::println("float                              -> {}", std::has_unique_object_representations_v<float>);
  std::println("Pair                               -> {}", std::has_unique_object_representations_v<Pair>);
  std::println("Player                             -> {}", std::has_unique_object_representations_v<Player>);
}
```

```text title="実行結果"
int                                -> true
float                              -> false
Pair                               -> true
Player                             -> false
```

## ゲームでの使いどころ

構造体を、バイト列のまま比べたり、ハッシュにしたりしてよいかを、コンパイル時に確かめます。

```cpp
template <class T>
std::size_t HashBytes(const T& value) {
  static_assert(std::has_unique_object_representations_v<T>,
                "詰め物や浮動小数点数を含む型は、バイト列では比べられません");
  return std::hash<std::string_view>{}(
      std::string_view(reinterpret_cast<const char*>(&value), sizeof(T)));
}
```

## よくあるミス

??? failure "パディングを含む構造体"
    `struct { char c; int i; }` は、`c` と `i` の間に隙間があり、`false` です。メンバーの並びを大きい順に変えるか、隙間を明示的なメンバーにします。

??? failure "浮動小数点数を含む型"
    `+0.0` と `-0.0`、NaN の種類があるので、`false` です。ビット列でハッシュすると、等しい値が違うハッシュになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_standard_layout`](is_standard_layout.md) | C と同じメモリ配置か |
| [`is_trivially_copyable`](is_trivially_copyable.md) | ビットを写してよいか |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::has_unique_object_representations_v<T>` は、`T` の値がビット表現と 1 対 1 に対応するか
    - [x] 値とビット列が 1 対 1 の型が `true`
    - [x] バイト列でハッシュや比較をしてよいかの条件

## 関連ページ

- [cpprefjp: std::has_unique_object_representations](https://cpprefjp.github.io/reference/type_traits/has_unique_object_representations.html)
- [cppreference: std::has_unique_object_representations](https://en.cppreference.com/w/cpp/types/has_unique_object_representations)
