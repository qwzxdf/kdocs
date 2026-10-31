---
title: std::chrono::treat_as_floating_point
summary: "duration の中身（rep）を、小数として扱うかの特性。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::treat_as_floating_point

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`duration<int>` を別の単位に変換すると、端数が切り捨てられるので、`duration_cast` を書かないと暗黙には変換できません。一方、`duration<double>` なら、端数を持てるので、暗黙に変換できます。この違いを決めているのが `std::chrono::treat_as_floating_point` という特性で、`Rep` が「小数のように端数を持てる型」かどうかを表します。

!!! tip "ポイント"
    - `treat_as_floating_point_v<Rep>` が `true` なら、端数を持てる型として扱われる
    - `float`、`double`、`long double` は `true`。整数は `false`
    - `true` の `duration` どうしは、単位が粗い方向にも暗黙に変換できる
    - 自作の型を小数として扱わせたいときに、特殊化する

!!! info "このページを読む前に"
    [`duration`](duration.md) と [`duration_cast`](duration_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::treat_as_floating_point {#treat_as_floating_point}

```cpp
template <class Rep>
struct treat_as_floating_point : std::is_floating_point<Rep> {};

template <class Rep>
inline constexpr bool treat_as_floating_point_v = treat_as_floating_point<Rep>::value;
```

既定では `std::is_floating_point<Rep>` と同じです。つまり、`float`、`double`、`long double` が `true` で、整数は `false` です。

この値は、`duration` の暗黙の変換の可否を決めます。`duration<Rep1, P1>` から `duration<Rep2, P2>` への暗黙の変換は、次のどちらかのとき許されます。

- 変換先が `treat_as_floating_point` で `true` の型である
- 変換元の `Period` が、変換先の `Period` で割り切れる（細かい単位へ向かう）

小数の型が変換先なら、端数が失われないので、粗い単位への変換も暗黙にできます。`duration<double> d = 1500ms;` は、1.5 秒になります。

固定小数点数のような自作の型は、小数部を持てても、`is_floating_point` が `false` なので、整数と同じ扱いになります。端数を持てる型として扱わせたいなら、`treat_as_floating_point<MyFixed>` を特殊化して `true` にします。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  std::println("double: {}", treat_as_floating_point_v<double>);
  std::println("int:    {}", treat_as_floating_point_v<int>);

  // 変換先が double の duration なら、粗い単位へも暗黙に変換できる
  const duration<double> sec = 1500ms;
  std::println("{} 秒", sec.count());

  // 整数の seconds には暗黙に変換できない。cast が必要
  // seconds s = 1500ms;  // コンパイル エラー
  std::println("{} 秒", duration_cast<seconds>(1500ms).count());
}
```

```text title="実行結果"
double: true
int:    false
1.5 秒
1 秒
```

## ゲームでの使いどころ

表示や計算のために、`duration<double>`（秒）や `duration<float, std::milli>` を使うと、`duration_cast` を書かずに、端数つきで単位を変換できます。デルタタイムを `float` の秒で持つ、よくある書き方は、これによります。

## よくあるミス

??? failure "float の duration で比較して誤差が出る"
    小数の `duration` は、誤差を含みます。ちょうど等しいかの比較は、避けます。

??? failure "自作の固定小数点型が、暗黙に変換できずに困る"
    `treat_as_floating_point` を特殊化して `true` にすると、端数を持てる型として扱われます。ただし、変換で実際に精度が失われないことを、自分で保証します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration_values`](duration_values.md) | もう 1 つの、`Rep` ごとの特性 |
| [`duration_cast`](duration_cast.md) | 明示的に単位を変換する |
| `std::is_floating_point` | 既定の判定の元 |

## コンパイラ対応

C++11 から使えます。`treat_as_floating_point_v` は C++17 から。

## 関連ページ

- [cpprefjp: treat_as_floating_point](https://cpprefjp.github.io/reference/chrono/treat_as_floating_point.html)
- [cppreference: std::chrono::treat_as_floating_point](https://en.cppreference.com/w/cpp/chrono/treat_as_floating_point)
