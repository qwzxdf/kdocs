---
title: std::stoll
summary: "文字列を long long に変換する（失敗すると例外）。"
order: 64
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stoll

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

ミリ秒単位の時刻や、大きな ID を文字列から読み込みたい。`int` は 32 ビットで、約 21 億までしか表せません。`std::stoll` は、文字列を `long long`（64 ビット整数）に変換する関数です。[`stoi`](stoi.md) の 64 ビット版で、使い方は同じです。符号なしの 64 ビットが必要なら、`stoull` を使います。

!!! tip "ポイント"
    - 失敗は例外。
    - 符号なしの 64 ビットは `stoull`。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stoll {#stoll}

```cpp
long long stoll(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

- `stoi` の long long 版です。int に入らない大きな数（所持金、タイムスタンプ）に使います。`stol`、`stoul`、`stoull` もあります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  long long v = std::stoll("9000000000");   // int に収まらない大きさ
  std::println("{}", v);
}
```

```text title="実行結果"
9000000000
```

## ゲームでの使いどころ

セーブデータにプレイ時間のミリ秒や、64 ビットの ID を保存しているときに使います。`int` に収まらない値を読むと `out_of_range` になるので、最初から `stoll` を選びます。

ハッシュ値の読み込みにも向いています。64 ビットのハッシュを文字列で保存したなら、`stoull` で読み戻します。

例外を使いたくない場面では、`std::from_chars` を使います。速く、ロケールにも影響されません。

## よくあるミス

??? failure "int で受けて桁あふれ"
    大きな値は `long long` で受けます。

??? failure "`int` に代入して桁あふれ"
    `int x = std::stoll(s);` と書くと、64 ビットの値が 32 ビットに切り詰められます。受ける変数も `long long` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stoi`](stoi.md) | 32 ビット |
| [`std::from_chars`](../io/from_chars.md) | 例外なし |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → long long
    - [x] 失敗は例外
    - [x] 64 ビット整数

## 関連ページ

- [cpprefjp: std::stoll](https://cpprefjp.github.io/reference/string/stoll.html)
- [cppreference: std::stoll](https://en.cppreference.com/w/cpp/string/basic_string/stoll)
