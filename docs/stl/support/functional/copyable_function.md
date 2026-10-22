---
title: std::copyable_function
summary: "コピーできる、const や noexcept も指定できる関数のラッパー。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::copyable_function

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <functional>`
</div>

`std::function` は const の扱いが曖昧で、`noexcept` や右辺値呼び出しを型で表せません。`std::copyable_function` は、`const` / `noexcept` / 参照修飾を関数シグネチャに書ける、新しいコピー可能な関数ラッパーです。

!!! tip "ポイント"
    - シグネチャに `const` や `noexcept` を書ける（`R(Args...) const noexcept`）。
    - ムーブ専用でよければ [`move_only_function`](../../utilities/move_only_function.md)。
    - `std::function` の置き換え候補。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::copyable_function {#copyable_function}

```cpp
template <class... Sigs> class copyable_function;  // Sigs の例: R(Args...) const noexcept
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R(Args...) 修飾` | シグネチャ | 戻り値・引数と、`const` / `noexcept` / `&` / `&&` の修飾 |

- 戻り値: 呼び出し演算子で呼ぶ
- 計算量: 呼び出しは間接呼び出し 1 回


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::copyable_function<int(int) const> f = [](int x) { return x * 2; };
  auto g = f;  // コピーできる
  std::println("{} {}", f(3), g(4));
}
```

```text title="実行結果"
6 8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コールバックを const で呼べるようにしてコピーも許す | `std::copyable_function<void(int) const> cb = ...;` |

## よくあるミス

??? failure "`std::function` と同じ感覚で const を無視する"
    `const` つきのシグネチャで宣言すると、呼び出しも const に限られます。呼ぶ関数がそれに合うか確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::function`](../../utilities/function.md) | 従来の版 |
| [`move_only_function`](../../utilities/move_only_function.md) | ムーブ専用 |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] std::function の改良版
    - [x] const / noexcept をシグネチャで表せる
    - [x] コピー可能

## 関連ページ

- [cpprefjp: std::copyable_function](https://cpprefjp.github.io/reference/functional/copyable_function.html)
- [cppreference: std::copyable_function](https://en.cppreference.com/w/cpp/utility/functional/copyable_function)
