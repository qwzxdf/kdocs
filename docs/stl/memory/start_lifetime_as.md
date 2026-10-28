---
title: std::start_lifetime_as
summary: "バイト列を、そのままの値で指定した型のオブジェクトとして使い始める。"
order: 900
tags:
  - メモリ
---

# std::start_lifetime_as

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <memory>`
</div>

ネットワークやファイルから読んだバイト列を `reinterpret_cast` で構造体として読むのは、厳密にはオブジェクトが存在しないので未定義動作です。`start_lifetime_as<T>(p)` は、「ここから `T` として使い始める」と宣言して、バイトの値を壊さずにオブジェクトの寿命を始めます。

!!! tip "ポイント"
    - `T` は暗黙的に寿命を始められる型（トリビアルな型）に限る。
    - バイト列の中身は変わらない（初期化し直さない）。
    - `memcpy` でコピーする方法の代わりになる。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::start_lifetime_as {#start_lifetime_as}

```cpp
template <class T> T* start_lifetime_as(void* p) noexcept;
template <class T> const T* start_lifetime_as(const void* p) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | void* | `T` として使い始める場所（大きさと境界が合っていること） |

- 戻り値: 寿命を始めた `T` へのポインタ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  alignas(int) unsigned char buf[sizeof(int)] = {7, 0, 0, 0};
  int* p = std::start_lifetime_as<int>(buf);
  std::println("{}", sizeof(*p));
}
```

```text title="実行結果"
4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 受信バッファを構造体として読む | `auto* h = std::start_lifetime_as<Header>(buf);` |

## よくあるミス

??? failure "非トリビアルな型を指定する"
    コンストラクタが必要な型には使えません。`construct_at` や placement new を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`launder`](new_delete/launder.md) | 同じ場所に作り直したオブジェクトを指す |
| [`bit_cast`](../numeric/bit/bit_cast.md) | 値をコピーして型を変える |

## コンパイラ対応

C++23 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト列をそのまま T として使い始める
    - [x] トリビアルな型だけ
    - [x] reinterpret_cast より安全

## 関連ページ

- [cpprefjp: std::start_lifetime_as](https://cpprefjp.github.io/reference/memory/start_lifetime_as.html)
- [cppreference: std::start_lifetime_as](https://en.cppreference.com/w/cpp/memory/start_lifetime_as)
