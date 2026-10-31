---
title: std::localeconv
summary: "現在のロケールの数値・通貨の書式情報を取得する。"
order: 900
tags:
  - 入出力・文字列
---

# std::localeconv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <clocale>`
</div>

いまのロケールでは、小数点は `.` か `,` か。桁区切りは何か。通貨記号は何か。C のロケールが持つ、こうした数値と通貨の書式の情報を、構造体にまとめて返すのが `localeconv` です。自分で金額を整形する関数を作るときに、環境に合わせた記号を調べるために使います。

!!! tip "ポイント"
    - 戻り値は `lconv` へのポインタ。中身は読み取り専用
    - 次の `setlocale` や `localeconv` の呼び出しで、内容が変わることがある。使い終わるまでに呼ばない
    - `"C"` ロケールでは、小数点が `.`、桁区切りが空、他の項目は `CHAR_MAX` か空
    - C++ のストリームの書式は、`std::numpunct` で調べる

!!! info "このページを読む前に"
    [`std::setlocale`](setlocale.md) と [`std::lconv`](lconv.md) を先に読んでください。

## 関数の詳しい説明

### std::localeconv {#localeconv}

```cpp
std::lconv* localeconv();
```

引数はありません。現在の C のロケール（`setlocale` で設定したもの）の、`LC_NUMERIC` と `LC_MONETARY` の情報を、`lconv` 構造体にして返します。戻り値は、ライブラリが持つ静的な領域を指します。書き換えてはいけません。

返された構造体は、次に `localeconv` を呼ぶか、`setlocale` で `LC_NUMERIC` や `LC_MONETARY` を変えると、内容が変わります。値を後で使うなら、文字列をコピーしておきます。

複数のスレッドで同時に呼ぶのは安全ではありません。`setlocale` と同じく、設定の変更と取得が混ざると、結果が壊れます。

## 実際に動かしてみる

```cpp
#include <clocale>
#include <print>

int main() {
  const std::lconv* lc = std::localeconv();

  std::println("小数点: {}", lc->decimal_point);
  std::println("桁区切りは空: {}", lc->thousands_sep[0] == '\0');
}
```

```text title="実行結果"
小数点: .
桁区切りは空: true
```

起動直後は `"C"` ロケールなので、小数点は `.`、桁区切りはありません。

## ゲームでの使いどころ

通貨の表示を自作するときくらいです。ゲーム内の通貨は、現実の通貨と違うことが多く、ロケールの情報は使いません。多くの場合、桁区切りと小数点を固定して、自分で整形します。

## よくあるミス

??? failure "戻り値を書き換える"
    読み取り専用です。書き換えると、以降の呼び出しの結果が壊れます。

??? failure "ポインタを持ち続ける"
    `setlocale` を呼ぶと中身が変わります。必要な文字列はコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::lconv`](lconv.md) | 戻り値の構造体 |
| [`std::setlocale`](setlocale.md) | ロケールを設定する |
| [`std::numpunct`](numpunct.md) | C++ のロケールの数値の書式 |
| [`std::moneypunct`](moneypunct.md) | C++ のロケールの通貨の書式 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `localeconv` は、いまのロケールの数値と通貨の書式を、`lconv` で返す
    - [x] 読み取り専用。次の呼び出しで変わる
    - [x] C++ の側は `numpunct` と `moneypunct`

## 関連ページ

- [cpprefjp: localeconv](https://cpprefjp.github.io/reference/clocale/localeconv.html)
- [cppreference: std::localeconv](https://en.cppreference.com/w/cpp/locale/localeconv)
