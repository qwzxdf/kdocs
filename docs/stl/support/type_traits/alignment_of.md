---
title: std::alignment_of
summary: "型のアライメント（配置できる境界のバイト数）を調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::alignment_of

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

CPU はアドレスが決まった倍数でないと遅くなる（または動かない）ことがあります。型ごとに必要な倍数が「アライメント」で、`alignment_of_v<T>` で取れます。`alignof(T)` と同じ値です。

!!! tip "ポイント"
    - `alignof(T)` と同じ値。
    - `double` は 8、`char` は 1 が多い。
    - テンプレートの中で型から取りたいときに使う。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::alignment_of {#alignment_of}

```cpp
template <class T>
struct alignment_of : integral_constant<size_t, alignof(T)> {};
template <class T>
inline constexpr size_t alignment_of_v = alignment_of<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: アライメント（バイト）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::alignment_of_v<double>);
  std::println("{}", std::alignment_of_v<char>);
}
```

```text title="実行結果"
8
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自前のメモリプールで、型に合う境界に配置する |

## よくあるミス

??? failure "`sizeof` と取り違える"
    `sizeof` は大きさ、`alignment_of` は置ける境界です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::align`](../../memory/align.md) | ポインタを境界に合わせる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型のアライメント（配置できる境界のバイト数）を調べる
    - [x] `alignof(T)` と同じ値
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::alignment_of](https://cpprefjp.github.io/reference/type_traits/alignment_of.html)
- [cppreference: std::alignment_of](https://en.cppreference.com/w/cpp/types/alignment_of)
