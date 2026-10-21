---
title: std::regex_search
summary: "文字列のどこかに、パターンに合う部分があるか探す。"
order: 86
tags:
  - 入出力・文字列
---

# std::regex_search

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex_search` は、**文字列のどこかに、正規表現に合う部分があるか**を探します。見つかった部分は `smatch` に入ります。全体が一致するかを調べるのは [`regex_match`](regex_match.md) です。

!!! tip "ポイント"
    - どこかに含まれていればよい → `regex_search`。全体が一致 → `regex_match`。
    - 見つかった部分は [`std::smatch`](smatch.md) で取り出す。
    - `regex` は一度だけ作って使い回す。

!!! info "このページを読む前に"
    [`std::regex`](regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_search {#regex_search}

```cpp
bool regex_search(const std::string& s, const std::regex& re);
bool regex_search(const std::string& s, std::smatch& m, const std::regex& re);
```

- 文字列の中に一致する部分があれば `true`。`m` を渡すと最初に一致した部分が入ります

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string text = "HP 120";
  std::smatch m;
  if (std::regex_search(text, m, std::regex(R"(\d+)"))) {
    std::println("{}", m[0].str());   // 見つかった数字
  }
}
```

```text title="実行結果"
120
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログから数字の部分を取り出す | `std::regex_search(line, m, std::regex(R"(\d+)"))` |

## よくあるミス

??? failure "regex を毎回作る"
    作るのが重いので、`static const std::regex` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::regex_match`](regex_match.md) | 全体の一致 |
| [`std::regex_replace`](regex_replace.md) | 置き換える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] どこかに合う部分を探す
    - [x] 結果は `smatch`
    - [x] regex は使い回す

## 関連ページ

- [cpprefjp: std::regex_search](https://cpprefjp.github.io/reference/regex/regex_search.html)
- [cppreference: std::regex_search](https://en.cppreference.com/w/cpp/regex/regex_search)
