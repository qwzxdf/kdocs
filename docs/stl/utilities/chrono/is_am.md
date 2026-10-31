---
title: std::chrono::is_am
summary: "24 時間制の時刻が午前かを調べる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::is_am

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

24 時間制の時刻（0〜23）が、午前か午後かを調べたい。`std::chrono::is_am` は、時（`hours`）を受け取って、0〜11 時なら真、12〜23 時なら偽を返す関数です。12 時間制の表示で、AM と PM を付けるときに使います。

!!! tip "ポイント"
    - 0〜11 時が午前、12〜23 時が午後
    - 引数は `hours`。分や秒は関係ない
    - 12 時間制の時（1〜12）に直すには `make12`
    - 午後を調べる `is_pm` と対になる

!!! info "このページを読む前に"
    [`hours`](hours.md) と [`make12`](make12.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::is_am {#is_am}

<span class="ver ver-20">C++20</span>

```cpp
constexpr bool is_am(const hours& h) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | `hours` | 24 時間制の時（0〜23） |

`0h <= h && h <= 11h` なら真を返します。0 時は午前（深夜 12 時）です。12 時（正午）は午後に含まれます。

範囲外の値（24 時以上や負の値）を渡しても、エラーにはなりません。11 より大きいので、偽になります。値が正しい範囲かを確かめるのは、呼ぶ側の仕事です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  for (const int h : {0, 9, 11, 12, 18, 23}) {
    std::println("{:2} 時: 午前={} 午後={}", h, is_am(hours{h}), is_pm(hours{h}));
  }
}
```

```text title="実行結果"
 0 時: 午前=true 午後=false
 9 時: 午前=true 午後=false
11 時: 午前=true 午後=false
12 時: 午前=false 午後=true
18 時: 午前=false 午後=true
23 時: 午前=false 午後=true
```

0 時は午前、12 時は午後です。

## ゲームでの使いどころ

時刻の表示で、「AM 9:30」「PM 6:00」と出すときに使います。12 時間制の数字は、`make12` で求めます。

## よくあるミス

??? failure "12 時を午前だと思う"
    12 時（正午）は午後です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_pm`](is_pm.md) | 午後かを調べる |
| [`make12`](make12.md) | 12 時間制の時（1〜12）に直す |
| [`make24`](make24.md) | 24 時間制に直す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: is_am](https://cpprefjp.github.io/reference/chrono/is_am.html)
- [cppreference: std::chrono::is_am](https://en.cppreference.com/w/cpp/chrono/is_am)
