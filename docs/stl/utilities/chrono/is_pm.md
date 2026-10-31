---
title: std::chrono::is_pm
summary: "24 時間制の時刻が午後かを調べる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::is_pm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::is_pm` は、24 時間制の時（`hours`）が午後かを調べる関数で、`is_am` の逆です。12〜23 時なら真を返します。「12 時間制の PM」の表示に使います。

!!! tip "ポイント"
    - 12〜23 時が午後、0〜11 時が午前
    - 引数は `hours`
    - 12 時（正午）は午後
    - 範囲外の値でもエラーにならない

!!! info "このページを読む前に"
    [`is_am`](is_am.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::is_pm {#is_pm}

<span class="ver ver-20">C++20</span>

```cpp
constexpr bool is_pm(const hours& h) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | `hours` | 24 時間制の時（0〜23） |

`12h <= h && h <= 23h` なら真を返します。範囲外の値は偽になる側に倒れます。24 時以上は偽になり、午前とも午後ともつかない結果になります。

`is_am(h)` と `is_pm(h)` は、0〜23 の範囲では、必ずどちらか一方だけが真です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const hours now{15};
  const char* suffix = is_pm(now) ? "PM" : "AM";
  std::println("{} {}", make12(now).count(), suffix);

  const hours morning{9};
  std::println("{} {}", make12(morning).count(), is_pm(morning) ? "PM" : "AM");
}
```

```text title="実行結果"
3 PM
9 AM
```

`make12` で 12 時間制の数字にし、`is_pm` で AM / PM を付けています。

## ゲームでの使いどころ

英語圏向けの時刻表示で、AM / PM を付けるときに使います。日本語の表示なら「午前」「午後」です。

## よくあるミス

??? failure "24 時以上を渡す"
    翌日の 0 時を `24` と書くと、午後でも午前でもない結果になります。`0` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_am`](is_am.md) | 午前かを調べる |
| [`make12`](make12.md) | 12 時間制の時に直す |
| [`hh_mm_ss`](hh_mm_ss.md) | 時・分・秒に分解する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: is_pm](https://cpprefjp.github.io/reference/chrono/is_pm.html)
- [cppreference: std::chrono::is_pm](https://en.cppreference.com/w/cpp/chrono/is_pm)
