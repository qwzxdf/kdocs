---
title: std::wctype
summary: "分類の名前から、wctype_t を取得する。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::wctype

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

文字の種類を調べる関数は `iswalpha`、`iswdigit` など、種類ごとに別の名前です。文字の種類を、文字列の名前（"alpha"、"digit"）で選びたいとき、`std::wctype` が、その名前に対応する分類を表す値を返します。それを `iswctype` に渡して判定します。

!!! tip "ポイント"
    - `std::wctype("alpha")` は「英字」の分類を表す `wctype_t` の値
    - 使える名前は `alnum`、`alpha`、`blank`、`cntrl`、`digit`、`graph`、`lower`、`print`、`punct`、`space`、`upper`、`xdigit`
    - 分からない名前は 0 を返す
    - `iswctype` で実際に判定する

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::wctype {#wctype}

```cpp
std::wctype_t wctype(const char* property);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `property` | `const char*` | 分類の名前 |

戻り値は、`property` の名前に対応する分類を表す値（`wctype_t`）です。名前が正しくなければ 0 を返します。実行時に分類を切り替えたいとき（設定ファイルから種類を読むなど）に便利です。

この値は、そのまま判定に使うのではなく、`std::iswctype(wc, 分類)` に渡します。名前から分類を引く処理は少し時間がかかるので、ループの中で毎回呼ばず、外で 1 回だけ呼んで保持します。

分類の値は、ロケールに依存します。`setlocale` で変えたあとに取り直さないと、前のロケールの分類が使われます。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  const std::wctype_t alpha = std::wctype("alpha");
  std::println("alpha は有効: {}", alpha != 0);
  std::println("未知の名前は 0: {}", std::wctype("unknown") == 0);
}
```

```text title="実行結果"
alpha は有効: true
未知の名前は 0: true
```

## ゲームでの使いどころ

入力の検査ルールを、設定の文字列で切り替えるときに使います。

```cpp
const std::wctype_t category = std::wctype(rule_name.c_str());   // "digit" や "alpha"
for (wchar_t c : text) {
  if (!std::iswctype(c, category)) return false;
}
```

## よくあるミス

??? failure "ループの中で毎回呼ぶ"
    外で 1 回だけ呼びます。

??? failure "ロケールを変えたあとに取り直さない"
    `setlocale` のあとに取得し直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iswctype`](iswctype.md) | 分類で判定する |
| [`wctype_t`](wctype_t.md) | 分類を表す型 |
| [`wctrans`](wctrans.md) | 変換の種類を名前で指定する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wctype(name)` は名前から分類を表す値を返す
    - [x] 未知の名前は 0
    - [x] `iswctype` に渡して判定する

## 関連ページ

- [cpprefjp: std::wctype](https://cpprefjp.github.io/reference/cwctype/wctype.html)
- [cppreference: std::wctype](https://en.cppreference.com/w/cpp/string/wide/wctype)
