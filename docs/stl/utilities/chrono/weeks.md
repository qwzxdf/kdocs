---
title: std::chrono::weeks
summary: "週を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::weeks

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

週ごとのイベントや、「毎週月曜日にリセット」の設計では、期間を週で持ちたくなります。`std::chrono::weeks` は、7 日を 1 つぶんとする `duration` の別名で、C++20 から使えます。1 週間は 604800 秒です。

!!! tip "ポイント"
    - `duration<整数, ratio<604800>>` の別名。7 日 = 604800 秒
    - `days` へは暗黙に変換でき、`days` から `weeks` へは `duration_cast`
    - 曜日の単位の `weekday` とは別。`weeks` は期間の長さ
    - 日付に足して、「n 週間後」が求まる

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`days`](days.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::weeks {#weeks}

<span class="ver ver-20">C++20</span>

```cpp
using weeks = duration<int-at-least-22-bits, std::ratio<604800>>;
```

`weeks{2}` は 14 日です。`days d = weeks{2};` と暗黙に変換できます。逆向きは、端数が出るので `duration_cast<weeks>(days{10})` と書き、1 週間に切り捨てられます。

週の始まりが何曜日かは、`weeks` では決まりません。「月曜から始まる週」といった暦の扱いは、`weekday` と組み合わせて自分で計算します。

`sys_days` に `weeks{n}` を足すと、n 週間後の同じ曜日の日付が求まります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  std::println("2 週間は {} 日", days{weeks{2}}.count());
  std::println("10 日は {} 週間 (切り捨て)", duration_cast<weeks>(days{10}).count());

  // 2026-01-01 から 3 週間後
  const sys_days start = year{2026} / January / 1;
  const year_month_day ymd{start + weeks{3}};
  std::println("3 週間後は {} 月 {} 日",
               static_cast<unsigned>(ymd.month()),
               static_cast<unsigned>(ymd.day()));
}
```

```text title="実行結果"
2 週間は 14 日
10 日は 1 週間 (切り捨て)
3 週間後は 1 月 22 日
```

## ゲームでの使いどころ

週替わりのイベントの周期を `weeks{1}` で持ちます。何曜日にリセットするかは、`weekday` で別に管理します。

## よくあるミス

??? failure "weeks を曜日と取り違える"
    `weeks` は 7 日ぶんの長さで、曜日の名前や番号は持ちません。曜日は `weekday` です。

??? failure "C++17 以前で weeks を使う"
    C++20 からです。以前は `duration<int, std::ratio<604800>>` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`days`](days.md) | 日の単位 |
| [`weekday`](weekday.md) | 曜日を表す型 |
| [`months`](months.md) | 月の単位。平均の長さ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: weeks](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::weeks](https://en.cppreference.com/w/cpp/chrono/duration)
