---
title: std::chrono::duration_cast
summary: "時間の単位を変換する（切り捨て）。"
order: 6
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::duration_cast

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`std::chrono::duration_cast` は、**`duration` を別の単位に変換する**関数です。細かい単位から粗い単位へ（ミリ秒 → 秒）は情報が失われるので、`=` では代入できず、これを使います。**端数は切り捨て**られます。切り上げや四捨五入にしたいときは [`floor` / `ceil` / `round`](floor.md) を使います。

!!! tip "ポイント"
    - ミリ秒 → 秒のように、**粗くする変換は明示が必要**。
    - 粗い → 細かい（秒 → ミリ秒）は暗黙に変換できる。
    - 端数は切り捨て（0 に向かって）。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chrono::duration_cast {#duration_cast}

```cpp
template <class ToDuration, class Rep, class Period>
constexpr ToDuration duration_cast(const duration<Rep, Period>& d);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換先の `duration` 型 |
| `d` | `duration` | 変換元 |

- 戻り値: 変換した `ToDuration`（端数は切り捨て）
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  std::println("{}", duration_cast<seconds>(1999ms));       // 1.999 秒 → 1 秒（切り捨て）
  std::println("{}", duration_cast<milliseconds>(1.5s));    // 1.5 秒 → 1500 ミリ秒
}
```

```text title="実行結果"
1s
1500ms
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 経過時間をミリ秒の整数で表示する | `duration_cast<milliseconds>(end - start).count()` |
| 秒単位に丸めたタイマー表示 | `duration_cast<seconds>(remaining)` |

## よくあるミス

??? failure "小数の秒が欲しいのに duration_cast を使う"
    `duration_cast<seconds>` は整数秒に切り捨てます。小数の秒は `duration<float>`（や `duration<double>`）に代入します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor / ceil / round`](floor.md) | 丸め方を選べる |
| [`duration`](duration.md) | 本体 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 単位の変換（粗くする方向は明示）
    - [x] 端数は切り捨て
    - [x] 小数の秒は `duration<float>`

## 関連ページ

- [cpprefjp: std::chrono::duration_cast](https://cpprefjp.github.io/reference/chrono/duration_cast.html)
- [cppreference: std::chrono::duration_cast](https://en.cppreference.com/w/cpp/chrono/duration/duration_cast)
