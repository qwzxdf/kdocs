---
title: std::cref
summary: "const 参照を、値のように渡せる reference_wrapper にする。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::cref

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

読み取り専用の参照を、`std::thread` や `std::bind` に渡したい。`std::cref(x)` は、<strong>`x` への `const` 参照を包んだ `reference_wrapper`</strong> を返します。`std::ref` の `const` 版です。

!!! tip "ポイント"
    - `std::cref(x)` は `const` 参照を包んだ `reference_wrapper`
    - 大きなオブジェクトを、コピーせずに渡す
    - 書き換えられないので、データ競合を避けやすい
    - 参照先の寿命に注意する

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cref {#cref}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
std::reference_wrapper<const T> cref(const T& t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 値 | `const` 参照で持たせたいオブジェクト |

`std::ref` と同じですが、参照が `const` になります。設定データなど、読み取り専用で共有するオブジェクトを渡すときに使います。

コピーを避けられるので、重い構造体を渡すときに効率が良いです。ただし、スレッドで共有するとき、元のオブジェクトが書き換えられると、データ競合になります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <string>

void Show(const std::string& s) { std::println("{}", s); }

int main() {
  const std::string config = "easy";
  auto f = std::bind(Show, std::cref(config));   // コピーせずに参照を保持
  f();
}
```

```text title="実行結果"
easy
```

## ゲームでの使いどころ

大きな設定を、コピーせずにスレッドへ渡します。

```cpp
std::thread t(Run, std::cref(big_config));
```

## よくあるミス

??? failure "参照先が先に破棄される"
    寿命を呼び出し側で保証します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ref`](ref.md) | 書き換え可能な参照 |
| [`reference_wrapper`](reference_wrapper.md) | ラッパーの型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::cref(x)` は `const` 参照を持ち運べるラッパー
    - [x] コピーを避けられる
    - [x] 寿命に注意

## 関連ページ

- [cpprefjp: std::cref](https://cpprefjp.github.io/reference/functional/cref.html)
- [cppreference: std::cref](https://en.cppreference.com/w/cpp/utility/functional/ref)
