---
title: std::chrono::seconds
summary: "秒を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::seconds

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <chrono>`
</div>

長い待ち時間やタイムアウトを `5000` と書くと、ミリ秒なのか秒なのかが分かりません。`std::chrono::seconds` は、秒を数える `duration` の別名です。単位が型に入っているので、`seconds(5)` と書けば、5 秒だと一目で分かります。リテラルで `5s` とも書けます。

!!! tip "ポイント"
    - 1 つぶんの長さは 1 秒。
    - `count()` で数を取り出し、`duration_cast` で別の単位に変える。
    - リテラルでも書ける（[リテラル](literals.md) を参照）。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::seconds {#seconds}

```cpp
using seconds = duration</* 整数（35 ビット以上） */, ratio<1>>;
```

- 戻り値: `seconds{n}` は 秒を n 個ぶん持つ duration
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::duration_cast<std::chrono::seconds>(std::chrono::milliseconds{2500}).count());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

ゲームの設定値で、秒単位の長い時間を持つのに使います。バフの継続時間、ステージの制限時間、オートセーブの間隔などです。`constexpr seconds kAutoSave{60};` と書けます。

小数の秒が欲しいときは、`seconds` ではなく `duration<float>` を使います。`seconds` は整数なので、`1.5` 秒を表せません。デルタタイムは、`duration<float>` で受けるのが定番です。

ミリ秒との変換は、細かい単位への変換（秒からミリ秒）は暗黙にできますが、粗い単位への変換には `duration_cast` が要ります。

## よくあるミス

??? failure "整数に切り捨てられる"
    整数の `duration` に `duration_cast` で大きい単位へ直すと、小数点以下は切り捨てられます。小数で受けたいなら `duration<double>` を使います。

??? failure "小数の秒を `seconds` で表そうとする"
    `seconds` は整数です。`1.5` を渡すと切り捨てられるか、コンパイルエラーになります。`duration<float>` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 時間の長さの型 |
| [`duration_cast`](duration_cast.md) | 単位を変換する |
| [`literals`](literals.md) | `ms` / `s` などの書き方 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 秒を数える duration の別名
    - [x] `count()` で数を取り出す
    - [x] 単位の変換は duration_cast

## 関連ページ

- [cpprefjp: std::chrono::seconds](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::seconds](https://en.cppreference.com/w/cpp/chrono/duration)
