---
title: std::chrono::milliseconds
summary: "ミリ秒（1000 分の 1 秒）を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::milliseconds

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <chrono>`
</div>

待ち時間を `16`、タイムアウトを `5000` と数値で書くと、何の単位か分かりません。`duration<long long, std::ratio<1, 1000>>` と書くのは、長すぎます。標準は、よく使う単位に名前をつけています。`std::chrono::milliseconds` は、ミリ秒（1000 分の 1 秒）を数える `duration` の別名です。ゲームでは、フレーム時間や待ち時間の単位として、いちばんよく使います。

!!! tip "ポイント"
    - 1 つぶんの長さは 1/1000 秒。
    - `count()` で数を取り出し、`duration_cast` で別の単位に変える。
    - リテラルでも書ける（[リテラル](literals.md) を参照）。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::milliseconds {#milliseconds}

```cpp
using milliseconds = duration</* 整数（45 ビット以上） */, std::milli>;
```

- 戻り値: `milliseconds{n}` は ミリ秒（1000 分の 1 秒）を n 個ぶん持つ duration
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::seconds{2}).count());
}
```

```text title="実行結果"
2000
```

## ゲームでの使いどころ

フレーム時間の表示に使います。処理時間を `duration_cast<milliseconds>(end - start).count()` でミリ秒の整数にして、画面に出します。

待ち時間の指定にも使います。`std::this_thread::sleep_for(milliseconds(16))` と書けば、約 60 フレームに相当する待ちです。リテラルで `16ms` と書くほうが短く済みます。

設定の値（クールダウンやタイムアウト）を `milliseconds` で持つと、単位の取り違えが減ります。60 フレーム換算の 16.6 ミリ秒のような小数は、整数のミリ秒では表せないので、`duration<float, std::milli>` を使います。

## よくあるミス

??? failure "整数に切り捨てられる"
    整数の `duration` に `duration_cast` で大きい単位へ直すと、小数点以下は切り捨てられます。小数で受けたいなら `duration<double>` を使います。

??? failure "小数のミリ秒を表そうとする"
    `milliseconds` は整数です。`16.6` ミリ秒は表せず、切り捨てられます。小数が要るなら `duration<float, std::milli>` を使います。

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
    - [x] ミリ秒（1000 分の 1 秒）を数える duration の別名
    - [x] `count()` で数を取り出す
    - [x] 単位の変換は duration_cast

## 関連ページ

- [cpprefjp: std::chrono::milliseconds](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::milliseconds](https://en.cppreference.com/w/cpp/chrono/duration)
