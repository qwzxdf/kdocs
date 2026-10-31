---
title: std::chrono::utc_seconds
summary: "utc_clock の時点（秒単位）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::utc_seconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::utc_seconds` は、`utc_clock` の時点を秒の単位で表す型です。`utc_time<seconds>` の別名で、`clock_cast<utc_clock>(sys_seconds)` の結果を受けるときなどに使います。

!!! tip "ポイント"
    - `utc_time<seconds>` の別名
    - `sys_seconds` との差は、挿入済みのうるう秒の累計
    - 書式は `{:%F %T}`。うるう秒の中は `23:59:60` と出る
    - `clock_cast` で相互に変換する

!!! info "このページを読む前に"
    [`utc_time`](utc_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::utc_seconds {#utc_seconds}

<span class="ver ver-20">C++20</span>

```cpp
using utc_seconds = utc_time<seconds>;
```

`system_clock` の時点を `utc_clock` の時点にするには、`clock_cast<utc_clock>(t)` を使います。秒の単位で受けたいなら、結果を `utc_seconds` に代入します。

2 つの `utc_seconds` の差が、うるう秒を含む本当の秒数です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const sys_seconds s = sys_days{2026y / January / 1};
  const utc_seconds u = clock_cast<utc_clock>(s);

  std::println("sys: {:%F %T}", s);
  std::println("utc: {:%F %T}", u);
  std::println("数値の差: {} 秒", (u.time_since_epoch() - s.time_since_epoch()).count());
}
```

```text title="実行結果"
sys: 2026-01-01 00:00:00
utc: 2026-01-01 00:00:00
数値の差: 27 秒
```

表示は同じですが、内部の秒数は、挿入されたうるう秒の分だけ大きくなっています。

## ゲームでの使いどころ

ほとんどありません。

## よくあるミス

??? failure "数値の差が 0 のはずだと思う"
    表示は同じでも、内部の数値は 27 秒ずれています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`utc_time`](utc_time.md) | 単位を選べる元の別名 |
| [`sys_seconds`](sys_seconds.md) | うるう秒を数えない |
| [`tai_seconds`](tai_seconds.md) | TAI の秒 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: utc_seconds](https://cpprefjp.github.io/reference/chrono/utc_clock.html)
- [cppreference: std::chrono::utc_seconds](https://en.cppreference.com/w/cpp/chrono/utc_clock)
