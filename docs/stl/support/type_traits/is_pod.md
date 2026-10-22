---
title: std::is_pod
summary: "型が POD（トリビアルかつ標準レイアウト）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_pod

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

C の構造体と同じように扱える、単純な型です。C++20 で非推奨になったので、`is_trivial` と `is_standard_layout` を組み合わせて使います。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_pod {#is_pod}

```cpp
template <class T>
struct is_pod;
template <class T>
inline constexpr bool is_pod_v = is_pod<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct A {
  int x;
  int y;
};

int main() {
  std::println("{}", std::is_pod_v<A>);
  std::println("{}", std::is_pod_v<std::string>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "新しいコードで使う"
    C++20 以降は非推奨です。コンパイル時に警告が出ることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_trivial`](is_trivial.md) | トリビアルか |
| [`is_standard_layout`](is_standard_layout.md) | 標準レイアウトか |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型が POD（トリビアルかつ標準レイアウト）かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_pod](https://cpprefjp.github.io/reference/type_traits/is_pod.html)
- [cppreference: std::is_pod](https://en.cppreference.com/w/cpp/types/is_pod)
