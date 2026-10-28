---
title: std::text_encoding
summary: "文字エンコーディング（UTF-8 など）の名前を表す型。"
order: 900
tags:
  - 型・言語サポート
---

# std::text_encoding

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <text_encoding>`
</div>

ファイルや端末がどの文字コードかを文字列ではなく型で扱いたいことがあります。`std::text_encoding` は、IANA 登録の文字エンコーディング（UTF-8、Shift_JIS など）を表す型で、`literal()` でソース上の文字列リテラルのエンコーディング、`environment()` で環境の既定を取れます。

!!! tip "ポイント"
    - `text_encoding::literal()` で文字列リテラルの文字コードを取る。
    - `name()` で名前、`mib()` で IANA の番号を取る。
    - C++26 の機能。

!!! info "このページを読む前に"
    [文字コード](../../encoding/index.md) の基本を先に読んでください。

## 関数の詳しい説明

### std::text_encoding {#text_encoding}

```cpp
class text_encoding {
 public:
  static text_encoding literal() noexcept;
  static text_encoding environment();
  const char* name() const noexcept;
  id mib() const noexcept;
};
```

- 戻り値: エンコーディングの名前など
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <text_encoding>

int main() {
  std::println("{}", std::text_encoding::literal().name());
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 実行環境の文字コードに合わせて変換する | `std::text_encoding::environment()` |

## よくあるミス

??? failure "名前の綴りで比べる"
    同じ文字コードでも別名があります。`==` で比べると、別名も同じものと判定されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../encoding/index.md) | 文字コードの考え方 |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字エンコーディングを表す型
    - [x] literal() / environment()
    - [x] C++26

## 関連ページ

- [cpprefjp: std::text_encoding](https://cpprefjp.github.io/reference/text_encoding/text_encoding.html)
- [cppreference: std::text_encoding](https://en.cppreference.com/w/cpp/locale/text_encoding)
