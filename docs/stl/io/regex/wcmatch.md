---
title: std::wcmatch
summary: "wchar_t の C 文字列用の match_results。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcmatch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`match_results<const wchar_t*>` の別名です。`const wchar_t*` を `wregex` で検索した結果を入れます。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::wcmatch {#wcmatch}

```cpp
using wcmatch = match_results<const wchar_t*>;
```

- 戻り値: `m[n]` で n 番目のグループ（`wcsub_match`）
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  const wchar_t* s = L"x=5";
  std::wcmatch m;
  std::regex_search(s, m, std::wregex(L"(\\d)"));
  std::println("{}", m.size());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Windows API が返した `wchar_t*` を検索する |

## よくあるミス

??? failure "`cmatch` を使う"
    `wchar_t` には `wcmatch` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cmatch`](cmatch.md) | char の C 文字列用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] wchar_t の C 文字列用の match_results
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcmatch](https://cpprefjp.github.io/reference/regex/wcmatch.html)
- [cppreference: std::wcmatch](https://en.cppreference.com/w/cpp/regex/wcmatch)
