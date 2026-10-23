---
title: std::llabs
summary: "long long の絶対値を返す。"
order: 900
tags:
  - 数値
---

# std::llabs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

整数の絶対値を取る `std::abs` には、型ごとに専用の関数もあります。`std::llabs` は、`long long`の絶対値を返します。C++ では `std::abs` が型に応じて自動で選ばれるので、直接使う機会は多くありません。

!!! tip "ポイント"
    - `std::llabs(-5)` は 5
    - 最小値の絶対値は表せない（未定義動作）
    - C++ では `std::abs` を使えば型に応じて選ばれる
    - C 言語のコードとの互換のために残っている

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::llabs {#llabs}

```cpp
long long llabs(long long n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `long long` | 絶対値を取りたい値 |

戻り値は `n` の絶対値で、型は long long です。`n` が負なら符号を反転し、0 以上ならそのまま返します。

型の最小値（`long` の最小値など）は、符号を反転すると範囲を超えるので、結果は未定義動作です。2 の補数表現では、負の側が正より 1 つ多い範囲を持つからです。

C++ の `<cstdlib>` には、`std::abs` の整数型のオーバーロードが用意されているため、`llabs` を直接書くより `std::abs(n)` を使うほうが、型の変更に強くなります。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("llabs(-5000000000LL) = {}", std::llabs(-5000000000LL));
  std::println("llabs(7) = {}", std::llabs(7));
}
```

```text title="実行結果"
llabs(-5000000000LL) = 5000000000
llabs(7) = 7
```

## ゲームでの使いどころ

2 つの整数の差の大きさを求めるときに使います。通常は `std::abs` と書きます。

```cpp
const auto distance = std::abs(a - b);   // 型に応じて選ばれる
```

## よくあるミス

??? failure "最小値に使って未定義動作になる"
    範囲の端の値を渡さないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abs`](../cmath/abs.md) | 型に応じて選ばれる |
| [`fabs`](../cmath/fabs.md) | 浮動小数点数の絶対値 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `llabs` は`long long`の絶対値
    - [x] 最小値は未定義動作
    - [x] C++ では `std::abs` を使う

## 関連ページ

- [cpprefjp: std::llabs](https://cpprefjp.github.io/reference/cstdlib/llabs.html)
- [cppreference: std::llabs](https://en.cppreference.com/w/cpp/c/llabs)
