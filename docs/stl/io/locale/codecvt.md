---
title: std::codecvt
summary: "文字コードの変換を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::codecvt

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

ファイルの文字コードと、メモリ上の文字コードが違うとき、変換を担当するのが `codecvt` ファセットです。ストリームの `imbue` で、変換規則を設定します。`always_noconv()` が `true` なら、変換は不要です。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::codecvt {#codecvt}

```cpp
template <class InternT, class ExternT, class StateT>
class codecvt {
 public:
  bool always_noconv() const noexcept;
  result in(StateT& state, const ExternT* from, const ExternT* from_end, const ExternT*& from_next, InternT* to, InternT* to_end, InternT*& to_next) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `InternT` | 型 | メモリ上の文字の型 |
| `ExternT` | 型 | ファイル側の文字の型 |
| `StateT` | 型 | 変換の途中状態（`mbstate_t`） |

- 戻り値: 変換結果（`ok`・`partial`・`error`・`noconv`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  const auto& cv = std::use_facet<std::codecvt<char, char, std::mbstate_t>>(std::locale::classic());
  std::println("{}", cv.always_noconv());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | UTF-8 のファイルを読んで UTF-16 に変換する |

## よくあるミス

??? failure "`codecvt_utf8` を新しいコードで使う"
    標準の変換ファセットの多くは C++17 で非推奨です。変換は変換用ライブラリ（ICU など）か、OS の API を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`codecvt_utf8`](codecvt_utf8.md) | UTF-8 の変換 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字コードの変換を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::codecvt](https://cpprefjp.github.io/reference/locale/codecvt.html)
- [cppreference: std::codecvt](https://en.cppreference.com/w/cpp/locale/codecvt)
