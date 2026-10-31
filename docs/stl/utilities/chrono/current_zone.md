---
title: std::chrono::current_zone
summary: "今の環境のタイムゾーンを取得する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::current_zone

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

プレイヤーの PC に設定されているタイムゾーンを知りたい。`std::chrono::current_zone()` は、OS の設定に従った `time_zone` を返す関数です。ここから `to_local` で、プレイヤーの壁掛け時計の時刻を求められます。

!!! tip "ポイント"
    - OS の設定によるタイムゾーン。環境で結果が変わる
    - 戻り値は `const time_zone*`
    - OS の設定を変更しても、実行中に追従するとは限らない
    - 決まったゾーンで動かしたいなら、`locate_zone` で名前を指定する

!!! info "このページを読む前に"
    [`time_zone`](time_zone.md) と [`locate_zone`](locate_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::current_zone {#current_zone}

<span class="ver ver-20">C++20</span>

```cpp
const time_zone* current_zone();
```

引数はありません。呼び出した時点の、OS のタイムゾーン設定から、`time_zone` を返します。実行する環境のタイムゾーンが分からないとき（コンテナなど）は、`UTC` になるか、例外を投げる環境があります。

テストでは、実行環境によって結果が変わるのは困ります。ローカル時刻の処理を、`current_zone()` に直接頼らず、`const time_zone*` を引数で受け取る関数にしておくと、テストでは `locate_zone("Asia/Tokyo")` を渡せます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const time_zone* zone = current_zone();
  std::println("ゾーンが取れた: {}", zone != nullptr);
  std::println("名前がある: {}", !zone->name().empty());

  // 現在時刻を、そのゾーンの壁掛け時計で
  const auto now = zone->to_local(floor<seconds>(system_clock::now()));
  std::println("2026 年以降: {}", now >= local_days{2026y / January / 1});
}
```

```text title="実行結果"
ゾーンが取れた: true
名前がある: true
2026 年以降: true
```

どの名前が返るかは環境しだいなので、表示していません。

## ゲームでの使いどころ

プレイヤーの地域の「今日の日付」の判定に使います。日替わりの要素を、サーバー側では UTC、クライアントの表示では `current_zone` にします。

## よくあるミス

??? failure "サーバーのタイムゾーンを取得してしまう"
    サーバーで `current_zone()` を呼ぶと、サーバーのゾーンです。プレイヤーのゾーンは、クライアントから送ってもらいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`locate_zone`](locate_zone.md) | 名前を指定して取る |
| [`zoned_time`](zoned_time.md) | ゾーンつきの時点 |
| [`time_zone`](time_zone.md) | 取得するもの |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: current_zone](https://cpprefjp.github.io/reference/chrono/current_zone.html)
- [cppreference: std::chrono::current_zone](https://en.cppreference.com/w/cpp/chrono/current_zone)
