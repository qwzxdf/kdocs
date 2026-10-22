---
title: std::hardware_constructive_interference_size
summary: "同じキャッシュラインに載せたいデータの、大きさの上限。"
order: 900
tags:
  - メモリ
---

# std::hardware_constructive_interference_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <new>`
</div>

2 つのデータを同時に読み書きするなら、同じキャッシュラインに乗せたほうが速くなります。逆に、別のスレッドが別々に書き込むデータは、別のラインに離すべきです（偽共有の回避）。`hardware_constructive_interference_size` は、前者の「同じラインに収める」上限の目安です。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`hardware_destructive_interference_size`](hardware_destructive_interference_size.md) を先に読んでください。

## 関数の詳しい説明

### std::hardware_constructive_interference_size {#hardware_constructive_interference_size}

```cpp
inline constexpr std::size_t hardware_constructive_interference_size = /* 実装定義 */;
```

- 戻り値: キャッシュラインの大きさ（多くは 64）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  std::println("{}", std::hardware_constructive_interference_size > 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 一緒に使うデータをキャッシュ 1 ライン内にまとめる |

## よくあるミス

??? failure "コンパイル環境と実行環境が違う"
    値はコンパイル時に決まります。別の CPU で動かすとずれることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hardware_destructive_interference_size`](hardware_destructive_interference_size.md) | 離すべき距離 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じキャッシュラインに載せたいデータの、大きさの上限
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::hardware_constructive_interference_size](https://cpprefjp.github.io/reference/new/hardware_constructive_interference_size.html)
- [cppreference: std::hardware_constructive_interference_size](https://en.cppreference.com/w/cpp/error/hardware_constructive_interference_size)
