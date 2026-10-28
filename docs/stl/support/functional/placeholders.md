---
title: std::placeholders
summary: "bind の引数の位置を表す _1, _2, … の名前空間。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::placeholders

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::bind` で「あとから渡す引数」を位置で指定するための印が `std::placeholders::_1`、`_2`… です。`_1` は呼び出し時の 1 番目の引数、`_2` は 2 番目の引数、という意味です。

!!! tip "ポイント"
    - `std::placeholders::_1` から `_N` まで（N は実装依存で 10 以上）。
    - 名前空間が長いので `using namespace std::placeholders;` を関数の中で使うことが多い。
    - 新しいコードではラムダか [`bind_front`](bind_front.md) が読みやすい。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::placeholders {#placeholders}

```cpp
namespace std::placeholders {
  inline constexpr /* 実装定義 */ _1, _2, _3 /* ... */;
}
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `_1, _2, ...` | プレースホルダー | 呼び出し時の 1 番目、2 番目、... の引数 |

- 戻り値: なし（`bind` に渡す印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int Sub(int a, int b) { return a - b; }

int main() {
  using namespace std::placeholders;
  auto f = std::bind(Sub, _2, _1);  // 引数を入れ替える
  std::println("{}", f(10, 3));      // Sub(3, 10)
}
```

```text title="実行結果"
-7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 引数の順を入れ替えた関数を作る | `auto f = std::bind(g, _2, _1);` |

## よくあるミス

??? failure "`using namespace` を広い範囲に書く"
    ヘッダやグローバルに書くと、`_1` などの名前が衝突します。関数の中で書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind_front`](bind_front.md) | 前の引数を固定するだけならこちら |
| [ラムダ式](../../../basics/lambda.md) | 読みやすさで勝る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] bind の引数位置の印
    - [x] 関数の中で using する
    - [x] 新しいコードはラムダか bind_front

## 関連ページ

- [cpprefjp: std::placeholders](https://cpprefjp.github.io/reference/functional/placeholders.html)
- [cppreference: std::placeholders](https://en.cppreference.com/w/cpp/utility/functional/placeholders)
