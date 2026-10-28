---
title: std::unwrap_ref_decay
summary: "decay してから、reference_wrapper を参照に戻す型変換。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::unwrap_ref_decay

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

`std::make_pair` や `make_tuple` は、引数を保存するときに「配列は先頭ポインタへ const は外す、`reference_wrapper` は参照へ」という型の変換をします。この変換を自分のテンプレートで使うための部品が `unwrap_ref_decay` です。

!!! tip "ポイント"
    - `decay_t<T>` を作り、それが `reference_wrapper<U>` なら `U&` にする。
    - `make_pair` / `make_tuple` の内部と同じ規則。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::unwrap_ref_decay {#unwrap_ref_decay}

```cpp
template <class T> struct unwrap_ref_decay;
template <class T> using unwrap_ref_decay_t = typename unwrap_ref_decay<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換したい型 |

- 戻り値: `decay_t<T>` が `reference_wrapper<U>` なら `U&`、それ以外は `decay_t<T>`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::unwrap_ref_decay_t<const int&>, int>);
  std::println("{}", std::is_same_v<std::unwrap_ref_decay_t<std::reference_wrapper<int>>, int&>);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 関数の引数を値で保存するコンテナを作る | `std::unwrap_ref_decay_t<T>` を保存する型にする |

## よくあるミス

??? failure "decay だけを期待する"
    `reference_wrapper` が入っていると参照になります。単なる decay は [`decay`](../type_traits/decay.md) です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unwrap_reference`](unwrap_reference.md) | decay はしない |
| [`decay`](../type_traits/decay.md) | decay だけ |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] decay + reference_wrapper の解除
    - [x] make_pair と同じ規則
    - [x] `_t` 版で使う

## 関連ページ

- [cpprefjp: std::unwrap_ref_decay](https://cpprefjp.github.io/reference/functional/unwrap_ref_decay.html)
- [cppreference: std::unwrap_ref_decay](https://en.cppreference.com/w/cpp/utility/functional/unwrap_ref_decay)
