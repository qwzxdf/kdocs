---
title: std::bit_cast
summary: "値のビット列を保ったまま、別の型として読み替える。"
order: 6
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_cast

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::bit_cast` は、**値のビット列をそのままに、別の型として読み替える**関数です。`float` のビットを `uint32_t` で見る、といった型の読み替えを、**安全に**行えます。ポインターのキャスト（`*(uint32_t*)&f`）は未定義動作ですが、これは問題ありません。`constexpr` でも使えます。

!!! tip "ポイント"
    - 型のサイズが同じで、両方トリビアルにコピーできる型でなければならない。
    - `reinterpret_cast` による読み替えは未定義動作。`bit_cast` を使う。
    - ビット演算で float を操作する技法に使う。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::bit_cast {#bit_cast}

```cpp
template <class To, class From>
constexpr To bit_cast(const From& from) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `To` | 読み替える先の型（`From` と同じ大きさで、コピーできる型） |

- メモリの中身（ビット）はそのままで、別の型として読みます。ハッシュ値の計算や、ネットワーク・ファイル用に float を整数として扱うときに使います

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint32_t bits = std::bit_cast<std::uint32_t>(1.0f);  // float のビット列を整数として見る
  std::println("{:#x}", bits);
}
```

```text title="実行結果"
0x3f800000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| float のビット列を取り出す（ハッシュ、デバッグ表示） | `std::bit_cast<std::uint32_t>(f)` |
| ネットワークで float を送る | バイト列に読み替える |

## よくあるミス

??? failure "ポインターのキャストで読み替える"
    未定義動作です。`bit_cast` を使います。

??? failure "サイズが違う"
    コンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| `memcpy` | 昔の安全な読み替え方法 |
| [`byteswap`](byteswap.md) | バイト順の入れ替え |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビット列を保って別の型に読み替える
    - [x] `reinterpret_cast` の代わり
    - [x] 同じサイズの型どうし

## 関連ページ

- [cpprefjp: std::bit_cast](https://cpprefjp.github.io/reference/bit/bit_cast.html)
- [cppreference: std::bit_cast](https://en.cppreference.com/w/cpp/numeric/bit_cast)
