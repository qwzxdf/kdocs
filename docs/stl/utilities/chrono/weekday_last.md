---
title: std::chrono::weekday_last
summary: "「最後の曜日」を表す型（最終金曜日など）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::weekday_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

第 5 の曜日は、ある月とない月があります。「毎月の最後の金曜日」を指定したいときは、第何回かの数字ではなく、「最後」と書くほうが確実です。`std::chrono::weekday_last` は、`weekday` に「最後」を付けた型で、`Friday[last]` と書きます。

!!! tip "ポイント"
    - `weekday[last]` で作る。`last` は `std::chrono::last`
    - 第 4 か第 5 か、月によって違うので、数字を使わずに書ける
    - `month / weekday_last` で `month_weekday_last`、`year_month / weekday_last` で `year_month_weekday_last`
    - `ok()` は、曜日が有効かだけを調べる

!!! info "このページを読む前に"
    [`weekday_indexed`](weekday_indexed.md) と [`last_spec`](last_spec.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::weekday_last {#weekday_last}

<span class="ver ver-20">C++20</span>

```cpp
class weekday_last {
 public:
  explicit constexpr weekday_last(const chrono::weekday& wd) noexcept;
  constexpr chrono::weekday weekday() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`Friday[last]` で作ります。`weekday()` で曜日を取り出せます。

これ自体は日付ではなく、月や年と組み合わせて、初めて日付が決まります。`2026y / November / Thursday[last]` は、2026 年 11 月の最後の木曜日です。11 月 30 日が月曜日なので、その前の木曜日、26 日が答えです。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const weekday_last last_friday = Friday[last];
  std::println("金曜日: {}", last_friday.weekday() == Friday);

  // 2026 年 11 月の最後の木曜日
  const sys_days d = 2026y / November / Thursday[last];
  std::println("{:%F}", d);

  // 2026 年 12 月の最後の木曜日
  const sys_days e = 2026y / December / Thursday[last];
  std::println("{:%F}", e);
}
```

```text title="実行結果"
金曜日: true
2026-11-26
2026-12-31
```

12 月 31 日が木曜日なので、12 月の最後の木曜日は 31 日です。

## ゲームでの使いどころ

「毎月最後の金曜日に締め」のような設定を、第 4 か第 5 かを気にせずに書けます。

## よくあるミス

??? failure "last を変数名にして衝突する"
    `using namespace std::chrono;` の下で、`last` という変数を作ると、`std::chrono::last` と紛らわしくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weekday_indexed`](weekday_indexed.md) | 第 n の曜日 |
| [`month_weekday_last`](month_weekday_last.md) | 月と組み合わせたもの |
| [`year_month_weekday_last`](year_month_weekday_last.md) | 年月と組み合わせたもの。日付になる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: weekday_last](https://cpprefjp.github.io/reference/chrono/weekday_last.html)
- [cppreference: std::chrono::weekday_last](https://en.cppreference.com/w/cpp/chrono/weekday_last)
