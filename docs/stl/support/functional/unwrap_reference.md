---
title: std::unwrap_reference
summary: "reference_wrapper を、ふつうの参照の型に戻す型変換。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::unwrap_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

`std::ref(x)` が返す `reference_wrapper<T>` は、テンプレートの中で「中身は `T&`」と扱いたいことがあります。`unwrap_reference<T>` は、`reference_wrapper<U>` なら `U&`、それ以外なら `T` をそのまま返す型変換です。

!!! tip "ポイント"
    - `reference_wrapper<U>` を `U&` に直す。
    - それ以外の型は変えない。
    - `::type` で結果の型を取る。`_t` 版もある。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::unwrap_reference {#unwrap_reference}

```cpp
template <class T> struct unwrap_reference;
template <class T> using unwrap_reference_t = typename unwrap_reference<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 解きたい型 |

- 戻り値: `reference_wrapper<U>` なら `U&`、それ以外は `T`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::unwrap_reference_t<std::reference_wrapper<int>>, int&>);
  std::println("{}", std::is_same_v<std::unwrap_reference_t<int>, int>);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ライブラリの内部で `ref` を解いて保存する | `std::unwrap_reference_t<std::reference_wrapper<int>>` は `int&` |

## よくあるミス

??? failure "値の `ref` を忘れる"
    `std::ref` を渡し忘れると、コピーが保存されて参照になりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unwrap_ref_decay`](unwrap_ref_decay.md) | decay もしてから解く |
| [`ref`](ref.md) | 参照のラッパーを作る |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] reference_wrapper を参照に戻す型変換
    - [x] それ以外は変えない
    - [x] `unwrap_reference_t` で使う

## 関連ページ

- [cpprefjp: std::unwrap_reference](https://cpprefjp.github.io/reference/functional/unwrap_reference.html)
- [cppreference: std::unwrap_reference](https://en.cppreference.com/w/cpp/utility/functional/unwrap_reference)
