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

ロケールは、1 つの塊に見えますが、中身は小さな部品の集まりです。数値の書式、日付の書式、文字の分類、文字コードの変換。それぞれが独立した部品で、これを「ファセット（facet）」と呼びます。どのファセットも `std::locale::facet` を親に持ちます。自作のファセットをロケールに差し込めば、`std::cout` の数値の出力のしかたなどを、あとから変えられます。

!!! tip "ポイント"
    - ファセットは `std::locale::facet` を継承したクラス。ロケールが部品として持つ
    - 自作するときは `static std::locale::id id;` を持たせる。ロケールが部品を探す鍵になる
    - `new` で作ったものを `std::locale` のコンストラクターに渡す。自分では `delete` しない
    - 取り出すには `std::use_facet<型>(loc)`、あるかの確認は `std::has_facet<型>(loc)`

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::locale::facet {#facet}

```cpp
class locale::facet {
 protected:
  explicit facet(std::size_t refs = 0);
  virtual ~facet();
  facet(const facet&) = delete;
  facet& operator=(const facet&) = delete;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `refs` | `std::size_t` | 参照の管理の指定。0 ならロケールが寿命を管理し、1 なら自分で管理する |

コンストラクターとデストラクターは `protected` なので、直接作ることはできません。継承したクラスの中でだけ使えます。コピーも禁止です。

`refs` が 0（既定）だと、ファセットを持つ最後のロケールが破棄されるときに、ロケールが `delete` します。1 を渡すと、ロケールは破棄しません。静的な領域に置いた場合などに使います。普通は、0 のままにします。

### 自作のファセット {#custom}

ファセットを作る約束は、2 つです。`std::locale::facet` を継承することと、`static std::locale::id id;` を持つことです。`id` は、ロケールが「この型のファセットが入っているか」を調べるための、型ごとに 1 つの目印になります。

```cpp
struct MyFacet : std::locale::facet {
  static std::locale::id id;     // 宣言
};
std::locale::id MyFacet::id;     // 定義（クラスの外に 1 つだけ）
```

既存のファセット（`numpunct` など）の動作を変えるときは、標準のファセットを継承して、仮想関数を上書きします。

```cpp
struct Comma : std::numpunct<char> {
  char do_thousands_sep() const override { return ','; }
  std::string do_grouping() const override { return "\3"; }
};
```

これをストリームに `imbue` すれば、数値が `1,234,567` のように出ます。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>
#include <sstream>

// 桁区切りをカンマにする numpunct
struct Comma : std::numpunct<char> {
  char do_thousands_sep() const override { return ','; }
  std::string do_grouping() const override { return "\3"; }
};

int main() {
  // new で渡す。ロケールが寿命を管理するので delete しない
  const std::locale loc(std::locale::classic(), new Comma);

  std::ostringstream os;
  os.imbue(loc);
  os << 1234567;
  std::println("{}", os.str());
}
```

```text title="実行結果"
1,234,567
```

`std::locale(基になるロケール, 新しいファセット)` の形で、`Comma` を足した新しいロケールを作っています。元のロケール（`classic`）は変わりません。

## ゲームでの使いどころ

スコアの表示で、桁区切りを入れたいときに使えます。ただし、`std::format` の `{:L}` や、数値を自分で整形する方法のほうが分かりやすいことが多く、ファセットを自作する機会は少ないです。

## よくあるミス

??? failure "delete を自分で呼ぶ"
    ロケールが参照を数えて破棄します。`new` で渡したあとは、自分では消しません。二重に解放されます。

??? failure "id の定義を忘れる"
    宣言だけして定義しないと、リンク エラーになります。クラスの外で `std::locale::id MyFacet::id;` を書きます。

??? failure "ファセットをスタックに作る"
    ロケールが `delete` しようとして、クラッシュします。`new` で作るか、`refs` に 1 を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`use_facet`](use_facet.md) | ロケールからファセットを取り出す |
| [`has_facet`](has_facet.md) | ファセットを持っているかを調べる |
| [`std::numpunct`](numpunct.md) | 標準のファセットの例 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `facet` は、ロケールの部品の基底クラス
    - [x] 自作するなら `static std::locale::id id;` を持つ
    - [x] `new` でロケールに渡し、自分では `delete` しない

## 関連ページ

- [cpprefjp: facet](https://cpprefjp.github.io/reference/locale/facet.html)
- [cppreference: std::facet](https://en.cppreference.com/w/cpp/locale/locale/facet)
