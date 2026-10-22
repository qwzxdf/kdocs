---
title: std::facet
summary: "ロケールを構成する、部品（ファセット）の基底クラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::facet

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

ロケールは、数字の書式、日付の書式、文字の分類など、複数の「部品」で構成されます。その部品の共通の基底クラスが `std::locale::facet` です。自分で部品を作るときは、これを継承し、`static std::locale::id id;` を持たせます。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::facet {#facet}

```cpp
class locale::facet {
 protected:
  explicit facet(std::size_t refs = 0);
  virtual ~facet();
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `refs` | size_t | 参照カウントの管理（0 ならロケールが管理する） |

- 戻り値: ロケールに追加できる部品
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

struct MyFacet : std::locale::facet {
  static std::locale::id id;
};
std::locale::id MyFacet::id;

int main() {
  std::locale loc(std::locale::classic(), new MyFacet);
  std::println("{}", std::has_facet<MyFacet>(loc));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 独自の書式を、ロケールの仕組みに乗せる |

## よくあるミス

??? failure "`delete` を自分で呼ぶ"
    ロケールが参照を数えて破棄します。`new` で渡して、自分では消しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`use_facet`](use_facet.md) | ファセットを取り出す |
| [`has_facet`](has_facet.md) | ファセットがあるか |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロケールを構成する、部品（ファセット）の基底クラス
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::facet](https://cpprefjp.github.io/reference/locale/facet.html)
- [cppreference: std::facet](https://en.cppreference.com/w/cpp/locale/facet)
