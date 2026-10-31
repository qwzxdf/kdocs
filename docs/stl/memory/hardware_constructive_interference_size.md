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

2 つの変数を、同じキャッシュ ラインに置くと、1 回の読み込みで両方がキャッシュに載り、速くなります。`std::hardware_constructive_interference_size` は、<strong>「この大きさ以内に置けば、同じキャッシュ ラインに載せやすい」という上限</strong>の定数です。

!!! tip "ポイント"
    - 一緒に使うデータを、この大きさ以内にまとめると、キャッシュに有利
    - `<new>` の定数。C++17
    - 典型は 64 バイト
    - 逆に、スレッド間の偽共有を避けるなら `hardware_destructive_interference_size`

!!! info "このページを読む前に"
    [`hardware_destructive_interference_size`](hardware_destructive_interference_size.md) とセットで読んでください。

## 関数の詳しい説明

### std::hardware_constructive_interference_size {#hardware_constructive_interference_size}

<span class="ver ver-17">C++17</span>

```cpp
inline constexpr std::size_t hardware_constructive_interference_size = /* 実装定義 */;
```

「構築的な干渉」、つまり、同じキャッシュ ラインに載ることで、むしろ得をする大きさの上限です。

構造体を、この大きさ以下にまとめ、`alignas` でこの境界に合わせれば、構造体全体が 1 つのキャッシュ ラインに載ります。頻繁に一緒に読む、座標と速度などの組み合わせが対象です。

値は、コンパイル時の目標の CPU から決まる推定値です。実際に動かす CPU が違うと、ずれます。ライブラリの ABI に影響するので、公開するヘッダーの中で使うのは避けます。

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

struct alignas(std::hardware_constructive_interference_size) Particle {
  float x, y, vx, vy;  // 一緒に使うデータ
};

int main() {
  std::println("構造体の大きさ {} <= {}", sizeof(Particle),
               std::hardware_constructive_interference_size);
  std::println("大きさ以内に収まる: {}",
               sizeof(Particle) <= std::hardware_constructive_interference_size);
}
```

```text title="実行結果"
構造体の大きさ 64 <= 64
大きさ以内に収まる: true
```

## ゲームでの使いどころ

パーティクルのような、大量に並べて走査するデータを、キャッシュ ラインに合わせて設計します。

## よくあるミス

??? failure "公開ヘッダーで使う"
    値がコンパイラや CPU の設定で変わり、ABI がずれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hardware_destructive_interference_size`](hardware_destructive_interference_size.md) | 偽共有を避けるための間隔 |
| [`align`](align.md) | 境界に合わせる |
| `alignas` | 型にアライメントを指定する |

## コンパイラ対応

C++17 から使えます。手元の MSVC では 64 でした。

## 関連ページ

- [cpprefjp: std::hardware_constructive_interference_size](https://cpprefjp.github.io/reference/new/hardware_constructive_interference_size.html)
- [cppreference: std::hardware_constructive_interference_size](https://en.cppreference.com/w/cpp/error/hardware_constructive_interference_size)
