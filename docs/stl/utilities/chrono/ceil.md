---
title: std::chrono::ceil
summary: "duration / time_point を、指定した単位に切り上げる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::ceil

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <chrono>`
</div>

`duration_cast` は 0 方向へ切り捨てます。`ceil` は、大きいほうへ切り上げます。必要な数のフレームを求める、残り時間を秒に切り上げて表示する、といった場面で使います。

!!! tip "ポイント"
    - `floor`・`ceil`・`round`・`duration_cast` で、丸め方を選ぶ。
    - `duration` にも `time_point` にも使える。
    - 戻り値の単位は、`ToDuration` で指定する。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::ceil {#ceil}

```cpp
template <class ToDuration, class Rep, class Period>
constexpr ToDuration ceil(const duration<Rep, Period>& d);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換後の `duration` |
| `d` | duration | 変換する時間 |

- 戻り値: 丸めた `ToDuration`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono_literals;
  auto d = 2500ms;
  std::println("{}", std::chrono::ceil<std::chrono::seconds>(d).count());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 残り時間を秒単位で表示する | `std::chrono::ceil<std::chrono::seconds>(remaining)` |

## よくあるミス

??? failure "`duration_cast` と同じだと思う"
    `duration_cast` は 0 方向への切り捨てです。負の値では、`floor` と結果が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 切り捨て |
| [`duration_cast`](duration_cast.md) | 0 方向への切り捨て |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] duration / time_point を、指定した単位に切り上げる
    - [x] duration にも time_point にも使える
    - [x] 丸め方で使い分ける

## 関連ページ

- [cpprefjp: std::chrono::ceil](https://cpprefjp.github.io/reference/chrono/ceil.html)
- [cppreference: std::chrono::ceil](https://en.cppreference.com/w/cpp/chrono/duration/ceil)
