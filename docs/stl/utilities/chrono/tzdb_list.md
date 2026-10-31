---
title: std::chrono::tzdb_list
summary: "tzdb の更新履歴（世代ごとの一覧）を管理する型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tzdb_list

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

長く動くプログラムでは、実行中にタイムゾーンデータベースを更新したくなることがあります。更新すると、新しい `tzdb` ができますが、古い版を指していた参照やポインタを無効にしてはいけません。`std::chrono::tzdb_list` は、`tzdb` の各世代を、新しい順に並べて保持する一覧です。古い版は消されず、一覧の末尾に残ります。

!!! tip "ポイント"
    - `get_tzdb_list()` で、唯一のインスタンスを取得する
    - `front()` が最新の版。`begin()` / `end()` で古い版まで辿れる
    - `reload_tzdb()` は、一覧の先頭に新しい版を足す
    - 古い版の参照は有効なまま。削除はされない

!!! info "このページを読む前に"
    [`tzdb`](tzdb.md) と [`reload_tzdb`](reload_tzdb.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tzdb_list {#tzdb_list}

<span class="ver ver-20">C++20</span>

```cpp
class tzdb_list {
 public:
  const tzdb& front() const noexcept;
  const_iterator begin() const noexcept;
  const_iterator end() const noexcept;
  const_iterator cbegin() const noexcept;
  const_iterator cend() const noexcept;
};

tzdb_list& get_tzdb_list();
```

`tzdb_list` は自分で作れません。`get_tzdb_list()` で、プログラムに 1 つだけ存在するものを取得します。

`front()` は、最新の版で、`get_tzdb()` が返すものと同じです。`begin()` から `end()` は、新しい順に古い版へと辿ります。

`reload_tzdb()` を呼ぶたびに、新しい版が先頭に足されます。ただし、データベースが更新されていなければ、足されません。古い版は、メモリに残り続けるので、頻繁に更新するプログラムでは、メモリが増えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const tzdb_list& list = get_tzdb_list();

  int count = 0;
  for (const tzdb& db : list) {
    ++count;
  }
  std::println("版が 1 つ以上ある: {}", count >= 1);
  std::println("先頭は get_tzdb と同じ: {}", &list.front() == &get_tzdb());
}
```

```text title="実行結果"
版が 1 つ以上ある: true
先頭は get_tzdb と同じ: true
```

## ゲームでの使いどころ

ほとんどの場合は使いません。何日も動かし続けるサーバーで、データベースの更新を取り込みたいときに、`reload_tzdb` とあわせて出てきます。

## よくあるミス

??? failure "tzdb_list を自分で作ろうとする"
    作れません。`get_tzdb_list()` で取得します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tzdb`](tzdb.md) | 一覧の要素 |
| [`get_tzdb`](get_tzdb.md) | 最新の版を取る |
| [`reload_tzdb`](reload_tzdb.md) | 更新して一覧に足す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: tzdb_list](https://cpprefjp.github.io/reference/chrono/tzdb_list.html)
- [cppreference: std::chrono::tzdb_list](https://en.cppreference.com/w/cpp/chrono/tzdb_list)
