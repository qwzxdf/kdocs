---
title: std::is_standard_layout
summary: "型が標準レイアウト（C 言語と互換のメモリ配置）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_standard_layout

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

C 言語の構造体と同じメモリ配置が保証される型かを調べたい。`std::is_standard_layout` は、<strong>型が標準レイアウトか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_standard_layout_v<T>` は、`T` が標準レイアウト型か
    - 仮想関数があると `false`
    - `std::is_standard_layout<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - アクセス指定の混在も `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_standard_layout_v {#is_standard_layout}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_standard_layout_v = is_standard_layout<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

仮想関数を持たず、すべての非静的メンバー変数のアクセス指定が同じで、継承の形が単純な型が `true` です。C 言語のコードや GPU のバッファと、構造体のメモリ配置を共有するときの条件になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
struct Animal {
  virtual ~Animal() = default;
  virtual void Speak() {}
};

int main() {
  std::println("Player                     -> {}", std::is_standard_layout_v<Player>);
  std::println("Animal                     -> {}", std::is_standard_layout_v<Animal>);
  std::println("int                        -> {}", std::is_standard_layout_v<int>);
}
```

```text title="実行結果"
Player                     -> true
Animal                     -> false
int                        -> true
```

## ゲームでの使いどころ

GPU の定数バッファやファイルの先頭に置く構造体が、予想どおりの並びかを確かめます。

```cpp
struct ConstantBuffer {
  float world[16];
  float color[4];
};

static_assert(std::is_standard_layout_v<ConstantBuffer>, "メモリ配置が C と同じ形である必要があります");
static_assert(sizeof(ConstantBuffer) == 80);   // 大きさも確かめる
```

## よくあるミス

??? failure "standard layout ならパディングがないと思う"
    並びが C と同じ規則になるだけで、パディングは入ります。大きさは `sizeof` で確かめます。

??? failure "public と private のメンバーを混ぜる"
    アクセス指定が混ざると `false` です。メンバーの並びが、環境ごとに変わりうるためです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_trivial`](is_trivial.md) | 構築・コピー・破棄が自明か |
| [`is_pod`](is_pod.md) | 両方を満たす（C++20 で非推奨） |
| [`is_aggregate`](is_aggregate.md) | 波括弧で初期化できるか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_standard_layout_v<T>` は、`T` が標準レイアウト型か
    - [x] C と同じメモリ配置の型が `true`
    - [x] パディングの有無とは別の話

## 関連ページ

- [cpprefjp: std::is_standard_layout](https://cpprefjp.github.io/reference/type_traits/is_standard_layout.html)
- [cppreference: std::is_standard_layout](https://en.cppreference.com/w/cpp/types/is_standard_layout)
