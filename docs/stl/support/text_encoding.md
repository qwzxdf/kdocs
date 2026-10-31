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

ファイルや端末の文字コードを、文字列で `"UTF-8"` や `"Shift_JIS"` と持ち回ると、綴りが違う別名（`"utf8"` や `"MS_Kanji"`）で、比較がうまくいかなくなります。`std::text_encoding` は、IANA に登録された文字エンコーディングを、型として表します。別名も同じものとして扱われるので、`==` で正しく比べられます。

!!! tip "ポイント"
    - IANA に登録された文字コードを表す型
    - `literal()` でソースの文字列リテラルの文字コード、`environment()` で実行環境の文字コードを取る
    - `name()` で標準の名前、`mib()` で IANA の番号、`aliases()` で別名を取る
    - 別名どうしでも `==` が真になる

!!! info "このページを読む前に"
    [文字コード](../../encoding/index.md) の基本を先に読んでください。

## 関数の詳しい説明

### std::text_encoding {#text_encoding}

<span class="ver ver-26">C++26</span>

```cpp
class text_encoding {
 public:
  enum class id : int_least32_t { /* UTF8, ShiftJIS, ... unknown, other */ };

  constexpr text_encoding() noexcept;
  constexpr explicit text_encoding(std::string_view name) noexcept;
  constexpr text_encoding(id i) noexcept;

  constexpr id mib() const noexcept;
  constexpr const char* name() const noexcept;
  constexpr aliases_view aliases() const noexcept;

  static text_encoding literal() noexcept;
  static text_encoding environment();
  template <id I> static bool environment_is();
};
```

#### 作り方

文字列から作るときは、`text_encoding("Shift_JIS")` のように名前を渡します。IANA の登録名と別名のどれでも構いません。登録にない名前だと、`mib()` は `id::other` になります。

列挙型の `id` から作ることもできます。`text_encoding(text_encoding::id::UTF8)` のようにです。

#### mib

`mib()` は、IANA の番号（MIBenum）を `id` で返します。UTF-8 は 106、Shift_JIS は 17 です。文字列の綴りに頼らず、番号で比べられます。

#### name と aliases

`name()` は、そのエンコーディングの代表的な名前を返します。`aliases()` は、同じエンコーディングの別名を、順に取れる範囲で返します。

#### literal

`literal()` は、コンパイル時に決まる、文字列リテラルのエンコーディングです。MSVC に `/utf-8` を付けると UTF-8 になります。付けないと、実行環境の既定のコード ページです。

#### environment

`environment()` は、実行している環境の既定の文字コード（ロケールなど）を返します。Windows のコンソールでは、コード ページに対応するエンコーディングです。`environment_is<id::UTF8>()` のように、特定のエンコーディングかどうかだけを調べるテンプレートもあります。

#### 比較

`==` は、`mib()` が等しいかで判定します。別名でも同じです。登録にない名前（`id::other`）は、名前の文字列が同じなら等しいとされます。

## 使い方の形

```cpp
#include <print>
#include <text_encoding>

int main() {
  std::text_encoding lit = std::text_encoding::literal();
  std::println("リテラルの文字コード: {}", lit.name());
  std::println("UTF-8 か: {}", lit.mib() == std::text_encoding::id::UTF8);

  // 別名でも同じものと判定される
  std::text_encoding a("Shift_JIS");
  std::text_encoding b("MS_Kanji");
  std::println("Shift_JIS と MS_Kanji は同じ: {}", a == b);
  std::println("Shift_JIS の mib: {}", static_cast<int>(a.mib()));
}
```


## ゲームでの使いどころ

ファイルの読み書きや、ネットワークの入出力で、相手の文字コードを文字列の綴りではなく、型で扱って変換するときに使います。

## よくあるミス

??? failure "名前の文字列を == で比べる"
    別名があるので、綴りの違いで比較に失敗します。`text_encoding` どうしで比べます。

??? failure "literal() をコンソールの文字コードと思う"
    `literal()` は、ソースの文字列リテラルの文字コードです。実行環境の文字コードは `environment()` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../encoding/index.md) | 文字コードの全体像 |
| [`locale`](../io/locale.md) | ロケール |
| [`string_view`](../utilities/string_view.md) | 名前の受け渡し |

## コンパイラ対応

C++26 です。手元の MSVC（Visual Studio 2026）では、まだ `<text_encoding>` が無く、コンパイルできませんでした。そのため、このページのサンプルは動かして確かめていません。使えるようになったら、実行結果を確かめて書き足します。

## 関連ページ

- [cpprefjp: std::text_encoding](https://cpprefjp.github.io/reference/text_encoding/text_encoding.html)
- [cppreference: std::text_encoding](https://en.cppreference.com/w/cpp/locale/text_encoding)
