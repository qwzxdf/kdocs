---
title: std::mbrtoc16
summary: "mb → c16：ロケールのマルチバイト文字列 1 文字を UTF-16 のコード単位（`char16_t`）に変換します。"
order: 900
tags:
  - 数値
---

# std::mbrtoc16

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cuchar>`
</div>

ロケールのマルチバイト文字列 1 文字を UTF-16 のコード単位（`char16_t`）に変換します。サロゲートペアのときは 2 回に分けて返します。状態（`mbstate_t`）を引数で受け取るので、1 つの文字が複数回に分かれる場合も扱えます。

!!! tip "ポイント"
    - 途中状態 `mbstate_t` を呼び出しの間で保つ。
    - ロケールの設定で動作が変わる。
    - 新しいコードでは UTF-8 に統一し、変換は最小限にする。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方と、[ロケール](../../io/locale.md) を先に読んでください。

## 関数の詳しい説明

### std::mbrtoc16 {#mbrtoc16}

```cpp
std::size_t mbrtoc16(char16_t* pc, const char* s, std::size_t n, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pc` | char16_t* | 変換結果の書き込み先 |
| `s` | const char* | 変換元のバイト列 |
| `n` | size_t | 調べる最大のバイト数 |
| `ps` | mbstate_t* | 変換の途中状態 |

- 戻り値: 書き込んだ・読んだバイト数など（エラー時は `(size_t)-1`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cuchar>

int main() {
  // 例（ロケールを UTF-8 に設定して使う）
  // std::setlocale(LC_ALL, "C.UTF-8");
  // std::mbstate_t st{};
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 古い API とのやり取りで文字コードを変換する |

## よくあるミス

??? failure "`mbstate_t` を初期化しない"
    最初の呼び出しの前に、`std::mbstate_t st{};` で 0 に初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../../encoding/index.md) | 変換の考え方 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] mb → c16：ロケールのマルチバイト文字列 1 文字を UTF-16 のコード単位（`char16_t`）に変換します
    - [x] 途中状態 `mbstate_t` を呼び出しの間で保つ
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::mbrtoc16](https://cpprefjp.github.io/reference/cuchar/mbrtoc16.html)
- [cppreference: std::mbrtoc16](https://en.cppreference.com/w/cpp/string/multibyte/mbrtoc16)
