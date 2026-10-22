---
title: std::c32rtomb
summary: "c32 → mb：UTF-32（コードポイント、`char32_t`）を、ロケールのマルチバイト文字列に変換します。"
order: 900
tags:
  - 数値
---

# std::c32rtomb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cuchar>`
</div>

UTF-32（コードポイント、`char32_t`）を、ロケールのマルチバイト文字列に変換します。状態（`mbstate_t`）を引数で受け取るので、1 つの文字が複数回に分かれる場合も扱えます。

!!! tip "ポイント"
    - 途中状態 `mbstate_t` を呼び出しの間で保つ。
    - ロケールの設定で動作が変わる。
    - 新しいコードでは UTF-8 に統一し、変換は最小限にする。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方と、[ロケール](../../io/locale.md) を先に読んでください。

## 関数の詳しい説明

### std::c32rtomb {#c32rtomb}

```cpp
std::size_t c32rtomb(char* s, char32_t c, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | char* | 変換結果の書き込み先（`MB_LEN_MAX` バイト以上） |
| `c` | char32_t | 変換する文字 |
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
    - [x] c32 → mb：UTF-32（コードポイント、`char32_t`）を、ロケールのマルチバイト文字列に変換します
    - [x] 途中状態 `mbstate_t` を呼び出しの間で保つ
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::c32rtomb](https://cpprefjp.github.io/reference/cuchar/c32rtomb.html)
- [cppreference: std::c32rtomb](https://en.cppreference.com/w/cpp/string/multibyte/c32rtomb)
