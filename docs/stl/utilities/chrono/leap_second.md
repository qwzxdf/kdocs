---
title: std::chrono::leap_second
summary: "うるう秒の挿入日と値を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::leap_second

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

うるう秒は、いつ、何秒入ったのか。`std::chrono::leap_second` は、そのうるう秒 1 件の情報（挿入日時と値）を持つ型です。タイムゾーンのデータベース（`tzdb`）が、過去のうるう秒を全部、この型の一覧で持っています。

!!! tip "ポイント"
    - `date()` が挿入日時、`value()` が挿入する秒数（+1 秒か -1 秒）
    - 一覧は `get_tzdb().leap_seconds`
    - 比較演算子は、挿入日時の順で並ぶ
    - ゲームでは使わない。時計の仕組みを調べるとき用

!!! info "このページを読む前に"
    [`utc_clock`](utc_clock.md) と [`get_tzdb`](get_tzdb.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::leap_second {#leap_second}

<span class="ver ver-20">C++20</span>

```cpp
class leap_second {
 public:
  constexpr sys_seconds date() const noexcept;
  constexpr seconds value() const noexcept;
};
```

`date()` は、うるう秒の挿入日時を `sys_seconds` で返します。うるう秒は、6 月 30 日か 12 月 31 日の終わりに入るので、この値は 7 月 1 日 0 時か、1 月 1 日 0 時です。

`value()` は、挿入する秒数です。+1 秒（追加）が普通で、-1 秒（削除）は定義上あり得ますが、これまで一度も実施されていません。

一覧は、時刻のデータベース（`tzdb`）の `leap_seconds` に入っています。1972 年から 2017 年までに 27 回あり、2017 年 1 月 1 日が最後です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const tzdb& db = get_tzdb();
  const auto& list = db.leap_seconds;

  std::println("うるう秒の回数: {}", list.size());
  std::println("最初: {:%F}", list.front().date());
  std::println("最後: {:%F}", list.back().date());
  std::println("最後の値: {} 秒", list.back().value().count());
}
```

```text title="実行結果"
うるう秒の回数: 27
最初: 1972-07-01
最後: 2017-01-01
最後の値: 1 秒
```

27 回は、`utc_clock` と `system_clock` の差が 27 秒であることと一致します。

## ゲームでの使いどころ

使いません。

## よくあるミス

??? failure "date() をうるう秒の最中の時刻だと思う"
    挿入が終わった直後の時刻です。うるう秒の最中は、`date()` の 1 秒前（23:59:60）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_leap_second_info`](get_leap_second_info.md) | ある時点のうるう秒の情報を調べる |
| [`utc_clock`](utc_clock.md) | うるう秒を数える時計 |
| [`tzdb`](tzdb.md) | この一覧を持つ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: leap_second](https://cpprefjp.github.io/reference/chrono/leap_second.html)
- [cppreference: std::chrono::leap_second](https://en.cppreference.com/w/cpp/chrono/leap_second)
