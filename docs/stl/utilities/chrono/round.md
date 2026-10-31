---
title: std::chrono::round
summary: "duration / time_point を、指定した単位に四捨五入する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::round

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <chrono>`
</div>

1499 ミリ秒を 1 秒、1501 ミリ秒を 2 秒と表示したい。四捨五入の動きをするのが `std::chrono::round<ToDuration>` です。ちょうど半分（1500 ミリ秒）のときは、偶数のほうに丸めます。2.5 秒が 2 秒、3.5 秒が 4 秒になる、いわゆる「銀行丸め」です。

!!! tip "ポイント"
    - 近い側に丸める。ちょうど真ん中なら、偶数のほうへ
    - `round<seconds>(1500ms)` は 2、`round<seconds>(2500ms)` も 2
    - 整数の `ToDuration` だけで使える。小数の型では、丸める必要がなく、使えない
    - 常識的な「五入」とは、ちょうど半分で結果が違う

!!! info "このページを読む前に"
    [`floor`](floor.md) と [`ceil`](ceil.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::round {#round}

<span class="ver ver-17">C++17</span>

```cpp
template <class ToDuration, class Rep, class Period>
constexpr ToDuration round(const duration<Rep, Period>& d);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換先の `duration` の型。整数の型 |
| `d` | `duration` | 変換する値 |

`d` に最も近い `ToDuration` の値を返します。ちょうど中間のとき（1500 ミリ秒を秒にするとき）は、結果が偶数になるほうを選びます。

| 入力 | `round<seconds>` |
| --- | --- |
| 1499ms | 1 |
| 1500ms | 2（偶数） |
| 2500ms | 2（偶数） |
| 3500ms | 4（偶数） |

この規則は、大量の値を丸めるときに、上と下への偏りが出ないようにするためのものです。学校で習う四捨五入（0.5 は切り上げ）とは違うので、表示を期待するとおりにしたいときは注意します。

`ToDuration` が小数型の `duration` のときは、丸めの必要がありません。そのため、`round` は整数の `ToDuration` に限られます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  std::println("round 1499ms → {}", round<seconds>(1499ms).count());
  std::println("round 1500ms → {}", round<seconds>(1500ms).count());
  std::println("round 2500ms → {}", round<seconds>(2500ms).count());
  std::println("round 3500ms → {}", round<seconds>(3500ms).count());
}
```

```text title="実行結果"
round 1499ms → 1
round 1500ms → 2
round 2500ms → 2
round 3500ms → 4
```

1500 は 2（偶数）、2500 も 2（偶数）、3500 は 4（偶数）に丸められています。

## ゲームでの使いどころ

プレイ時間の表示のように、四捨五入して見せたいときに使います。ちょうど半分の扱いが問題になるなら、`ceil` か `floor` を、仕様として決めて使います。

## よくあるミス

??? failure "2.5 が 3 になると思う"
    ちょうど半分は偶数に丸められます。2500ms は 2 秒です。0.5 を必ず切り上げたいなら、`floor(x + 0.5 単位)` のように自分で書きます。

??? failure "小数の duration を ToDuration にする"
    `round<duration<double>>(...)` はコンパイルできません。整数の型を指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 切り捨てる |
| [`ceil`](ceil.md) | 切り上げる |
| [`duration_cast`](duration_cast.md) | 0 に向かって丸める |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: round](https://cpprefjp.github.io/reference/chrono/round.html)
- [cppreference: std::chrono::round](https://en.cppreference.com/w/cpp/chrono/round)
