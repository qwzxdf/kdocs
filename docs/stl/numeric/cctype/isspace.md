---
title: std::isspace
summary: "空白文字（スペース・タブ・改行）かを調べる。"
order: 3
group: <cctype> の文字判定
tags:
  - 数値
---

# std::isspace

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

`std::isspace` は、**文字が空白類（スペース、タブ、改行など）か**を調べる関数です。文字列の前後の空白を取り除く、単語に区切る、といった処理に使います。

!!! tip "ポイント"
    - スペース、`\t`、`\n`、`\r`、`\v`、`\f` が対象。
    - 全角スペースは判定できない。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::isspace {#isspace}

```cpp
int isspace(int c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `int` | 判定・変換する文字（`unsigned char` の範囲か EOF） |

- 戻り値: 結果
- 計算量: O(1)

```cpp
#include <cctype>
#include <print>

int main() {
  std::println("{} {}", std::isspace(' ') != 0, std::isspace('a') != 0);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの行頭・行末の空白を取る | `while (std::isspace(s.back())) s.pop_back();` |

## よくあるミス

??? failure "char のまま渡す"
    負の `char` は未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isalpha`](isalpha.md) | 英字 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空白類かを調べる
    - [x] 全角スペースは対象外
    - [x] unsigned char にして渡す

## 関連ページ

- [cpprefjp: std::isspace](https://cpprefjp.github.io/reference/cctype/isspace.html)
- [cppreference: std::isspace](https://en.cppreference.com/w/cpp/string/byte/isspace)
