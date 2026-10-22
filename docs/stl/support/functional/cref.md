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

`std::thread` や `std::bind` に引数を渡すと、値としてコピーされます。読むだけの大きなオブジェクトをコピーしたくないとき、`std::cref(x)` で包むと、const 参照として渡せます。`std::ref` の const 版です。

!!! tip "ポイント"
    - `std::reference_wrapper<const T>` を返す。
    - `.get()` で参照を取り出せる。
    - 書き換えたいなら [`ref`](ref.md)。

!!! info "このページを読む前に"
    [`std::ref`](ref.md) を先に読んでください。

## 関数の詳しい説明

### std::cref {#cref}

```cpp
template <class T>
std::reference_wrapper<const T> cref(const T& t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | const T& | 参照で渡したいオブジェクト |

- 戻り値: `reference_wrapper<const T>`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  int x = 1;
  auto r = std::cref(x);
  x = 2;
  std::println("{}", r.get());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スレッドに大きな設定データを読み取り専用で渡す | `std::thread t(Worker, std::cref(config));` |

## よくあるミス

??? failure "元のオブジェクトが先に消える"
    参照を渡しているだけです。スレッドが終わるまで、元のオブジェクトは生きている必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ref`](ref.md) | 書き換え可能な参照 |
| [`bind_front`](bind_front.md) | 引数を固定する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] const 参照を値のように渡す
    - [x] ref の const 版
    - [x] 元が先に消えないように

## 関連ページ

- [cpprefjp: std::cref](https://cpprefjp.github.io/reference/functional/cref.html)
- [cppreference: std::cref](https://en.cppreference.com/w/cpp/utility/functional/ref)
