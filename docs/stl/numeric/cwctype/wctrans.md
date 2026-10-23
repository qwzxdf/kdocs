---
title: std::wctrans
summary: "変換の名前から、wctrans_t を取得する。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::wctrans

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

文字を変換する関数にも、`towlower`、`towupper` と種類があります。変換の種類を名前（"tolower"、"toupper"）で選びたいとき、`std::wctrans` がその変換を表す値を返し、`std::towctrans` で実際に変換します。

!!! tip "ポイント"
    - `std::wctrans("toupper")` は大文字化の変換を表す `wctrans_t` の値
    - 標準で使える名前は `tolower` と `toupper`
    - 分からない名前は 0 を返す
    - `towctrans` に渡して変換する

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::wctrans {#wctrans}

```cpp
std::wctrans_t wctrans(const char* property);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `property` | `const char*` | 変換の名前。`"tolower"` か `"toupper"` |

戻り値は、`property` の名前に対応する変換を表す値（`wctrans_t`）です。名前が正しくなければ 0 を返します。

この値だけでは何も変換されません。`std::towctrans(wc, 変換)` に渡して使います。`wctype` と同じ形の組み合わせです。

変換の種類を実行時に切り替えたいときにしか使いません。固定なら `towlower` と `towupper` で足ります。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  const std::wctrans_t to_upper = std::wctrans("toupper");
  std::println("toupper は有効: {}", to_upper != 0);
  std::println("未知の名前は 0: {}", std::wctrans("unknown") == 0);
}
```

```text title="実行結果"
toupper は有効: true
未知の名前は 0: true
```

## ゲームでの使いどころ

文字の変換方法を設定で選ぶ処理に使います。ゲームでは出番がほとんどなく、標準ライブラリの全体像を知るための項目です。

## よくあるミス

??? failure "未知の名前の戻り値を確かめない"
    0 かを確かめてから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`towctrans`](towctrans.md) | 変換を実行する |
| [`wctype`](wctype.md) | 分類を名前で指定する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wctrans(name)` は名前から変換を表す値を返す
    - [x] 標準の名前は `tolower` と `toupper`
    - [x] `towctrans` に渡して変換する

## 関連ページ

- [cpprefjp: std::wctrans](https://cpprefjp.github.io/reference/cwctype/wctrans.html)
- [cppreference: std::wctrans](https://en.cppreference.com/w/cpp/string/wide/wctrans)
