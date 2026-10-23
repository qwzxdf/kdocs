---
title: std::div
summary: "整数の割り算で、商と余りを同時に求める。"
order: 1
group: <cstdlib> の関数
tags:
  - 数値
---

# std::div

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

割り算の商と余りが、両方欲しいことがあります。`a / b` と `a % b` を別々に書く代わりに、1 回で両方を返すのが `std::div` です。負の数の割り算で、結果が環境で変わらないことも保証されます。

!!! tip "ポイント"
    - `std::div(7, 2)` は商 3、余り 1
    - 結果は `div_t` 構造体（`quot` と `rem`）
    - 負の数は 0 方向に丸める（C++11 以降の定義）
    - `long` 用は `ldiv`、`long long` 用は `lldiv`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::div {#div}

```cpp
div_t div(int x, int y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `int` | 割られる数 |
| `y` | `int` | 割る数。0 は未定義動作 |

戻り値の `div_t` は、`quot`（商）と `rem`（余り）を持つ構造体で、`x == quot * y + rem` が成り立ちます。商は 0 方向に切り捨てられるので、`div(-7, 2)` は商 −3、余り −1 です。余りの符号は割られる数に従います。

C++11 より前は、負の数の割り算の丸めが処理系に任されていましたが、`div` は昔から 0 方向への丸めを保証していました。今は `/` と `%` も同じ定義です。

`y` が 0 のとき、または `INT_MIN / -1` のように商が表せない場合は、未定義動作です。

`/` と `%` を並べて書けば、コンパイラが 1 つの命令にまとめることが多く、`div` が速いとは限りません。使う理由は、1 回の呼び出しで両方を受け取る書き方が読みやすい場合です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  const std::div_t a = std::div(7, 2);
  std::println("7 / 2   -> 商 {}, 余り {}", a.quot, a.rem);

  const std::div_t b = std::div(-7, 2);
  std::println("-7 / 2  -> 商 {}, 余り {}", b.quot, b.rem);   // 0 方向への切り捨て
}
```

```text title="実行結果"
7 / 2   -> 商 3, 余り 1
-7 / 2  -> 商 -3, 余り -1
```

## ゲームでの使いどころ

秒数を分と秒に分けるような、商と余りが両方要る処理で使えます。

```cpp
const std::div_t t = std::div(total_seconds, 60);
std::println("{} 分 {} 秒", t.quot, t.rem);
```

負の数で「常に 0 以上の余り」が欲しい場合（タイルの座標など）は、`div` では得られません。別途補正が要ります。

## よくあるミス

??? failure "負の数の余りを、常に 0 以上だと思う"
    余りの符号は割られる数に従います。0 以上にしたいなら補正します。

??? failure "0 で割る"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ldiv`](ldiv.md) | `long` 版 |
| [`lldiv`](lldiv.md) | `long long` 版 |
| [`remainder`](../cmath/remainder.md) | 浮動小数点数の余り |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `div(x, y)` は商と余りを `div_t` で返す
    - [x] 0 方向への切り捨てで、余りの符号は `x` に従う
    - [x] `/` と `%` と同じ意味。読みやすさで選ぶ

## 関連ページ

- [cpprefjp: std::div](https://cpprefjp.github.io/reference/cstdlib/div.html)
- [cppreference: std::div](https://en.cppreference.com/w/cpp/numeric/math/div)
