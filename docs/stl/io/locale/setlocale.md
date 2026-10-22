---
title: std::setlocale
summary: "C のロケールを設定・取得する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setlocale

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <clocale>`
</div>

`printf` や `strftime` など、C 由来の関数のロケールを設定します。`setlocale(LC_ALL, "")` で、環境のロケールを設定します。C++ のストリームのロケール（`std::locale`）とは別のものです。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::setlocale {#setlocale}

```cpp
char* setlocale(int category, const char* locale);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `category` | int | 対象の分類（`LC_ALL`・`LC_NUMERIC` など） |
| `locale` | const char* | ロケール名（`nullptr` で取得のみ） |

- 戻り値: 設定後のロケール名。失敗したら `nullptr`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <clocale>
#include <print>

int main() {
  std::println("{}", std::setlocale(LC_ALL, "C"));
}
```

```text title="実行結果"
C
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | コンソールの文字化けを防ぐ（環境のロケールを設定） |

## よくあるミス

??? failure "C++ のストリームにも効くと思う"
    `std::locale::global` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localeconv`](localeconv.md) | 現在の書式を調べる |
| [`std::locale`](../locale.md) | C++ のロケール |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C のロケールを設定・取得する
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::setlocale](https://cpprefjp.github.io/reference/locale/setlocale.html)
- [cppreference: std::setlocale](https://en.cppreference.com/w/cpp/locale/setlocale)
