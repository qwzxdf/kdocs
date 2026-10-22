---
title: std::collate
summary: "文字列の照合（辞書順の比較）を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::collate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

文字列の並び順は、言語によって違います。その比較規則を持っているのが `collate` ファセットです。`compare` で 2 つの文字列を比べます。`std::locale` の `operator()` は、これを使って文字列を並べ替えます。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::collate {#collate}

```cpp
template <class CharT>
class collate {
 public:
  int compare(const CharT* lo1, const CharT* hi1, const CharT* lo2, const CharT* hi2) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lo1, hi1` | ポインタ | 1 つ目の文字列の範囲 |
| `lo2, hi2` | ポインタ | 2 つ目の文字列の範囲 |

- 戻り値: `-1`（小さい）・0（等しい）・1（大きい）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  const char a[] = "a";
  const char b[] = "b";
  const auto& co = std::use_facet<std::collate<char>>(std::locale::classic());
  std::println("{}", co.compare(a, a + 1, b, b + 1));
}
```

```text title="実行結果"
-1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 名前を言語に合った順で並べ替える |

## よくあるミス

??? failure "文字コード順と同じだと思う"
    ロケールによっては、大文字小文字の扱いや、アクセント付き文字の順序が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcoll`](../../memory/cstring/strcoll.md) | C の関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列の照合（辞書順の比較）を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::collate](https://cpprefjp.github.io/reference/locale/collate.html)
- [cppreference: std::collate](https://en.cppreference.com/w/cpp/locale/collate)
