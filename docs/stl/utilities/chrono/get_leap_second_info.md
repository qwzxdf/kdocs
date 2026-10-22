---
title: std::chrono::get_leap_second_info
summary: "ある UTC の時点が、うるう秒の中か、それまでに何秒入ったかを調べる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::get_leap_second_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

UTC の時刻が、うるう秒の 1 秒（23:59:60）そのものなのか、そしてその時点までに累計で何秒挿入されたかを知りたいことがあります。`get_leap_second_info(utc_time)` が教えてくれます。

!!! tip "ポイント"
    - `is_leap_second` が `true` なら、うるう秒の最中。
    - `elapsed` は、その時点までに入ったうるう秒の累計。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::get_leap_second_info {#get_leap_second_info}

```cpp
template <class D>
leap_second_info get_leap_second_info(const utc_time<D>& ut);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ut` | utc_time | 調べる時点 |

- 戻り値: `is_leap_second` と `elapsed`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto ut = utc_clock::from_sys(sys_days{2024y / January / 1});
  auto info = get_leap_second_info(ut);
  std::println("{} {}", info.is_leap_second, info.elapsed.count());
}
```

```text title="実行結果"
false 27
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 経過秒の厳密な計算 | `info.elapsed` |

## よくあるミス

??? failure "sys_time に使う"
    引数は `utc_time` です。`system_clock` の時点は、先に `utc_clock::from_sys` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`leap_second`](leap_second.md) | うるう秒の記録 |
| [`utc_clock`](utc_clock.md) | UTC の時計 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] うるう秒の状態を調べる
    - [x] is_leap_second と elapsed
    - [x] utc_time を渡す

## 関連ページ

- [cpprefjp: std::chrono::get_leap_second_info](https://cpprefjp.github.io/reference/chrono/get_leap_second_info.html)
- [cppreference: std::chrono::get_leap_second_info](https://en.cppreference.com/w/cpp/chrono/get_leap_second_info)
