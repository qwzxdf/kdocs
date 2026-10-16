---
title: ムーブ（コピーとムーブ）
tags:
  - 基礎
---

# ムーブ（コピーとムーブ）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
</div>

**コピー**は中身を丸ごと複製すること、**ムーブ**は中身の「持ち主」を移すことです。`std::string` や `std::vector` は、文字や要素の本体をヒープ（別のメモリ）に置いていて、自分はそこへのポインタを持っているだけです。コピーするとヒープの中身まで全部複製しますが、ムーブならポインタを付け替えるだけで済むので、ずっと速くなります。ムーブされた側は空っぽになります。

!!! tip "結論"
    - **もう使わない大きな値（string、vector、unique_ptr）を渡すときは `std::move` を付けてムーブする。**
    - 関数から値を返すとき（`return v;`）は自動でムーブ（か、それ以上の最適化）になる。`std::move` は付けない。
    - ムーブされた変数は、代入し直すまで使わない。
    - 自作クラスは、メンバが標準の型ならコピー・ムーブは自動で正しく作られる（何も書かなくていい）。

!!! info "このページを読む前に"
    [参照](reference.md) と [ポインタ](pointer.md) を先に読むと分かりやすいです。

## 基本

<div class="mem">
<div class="mem-step"><span class="mem-label">a（string）</span><span class="mem-cells"><span class="move">→</span></span><span class="mem-note">ヒープの "とても長い文字列..." を指している</span></div>
<div class="mem-step"><span class="mem-label">b = a（コピー）</span><span class="mem-cells"><span class="new">→</span></span><span class="mem-note">ヒープに同じ文字列をもう 1 つ作って指す。遅い</span></div>
<div class="mem-step"><span class="mem-label">c = std::move(a)</span><span class="mem-cells"><span class="move">→</span></span><span class="mem-note">a が指していたヒープをそのまま受け取る。a は空になる。速い</span></div>
</div>

```cpp
#include <print>
#include <string>
#include <utility>

int main() {
  std::string a = "とても長いセーブデータ……";
  std::string b = a;             // コピー: a はそのまま
  std::string c = std::move(a);  // ムーブ: a の中身が c に移る

  std::println("b: {} / c: {} / a は空？ {}", b.size(), c.size(), a.empty());
}
```

```text title="実行結果"
b: 39 / c: 39 / a は空？ true
```

（ムーブ後の `a` の中身は規格上「未規定」ですが、標準ライブラリの string は実際には空になります。）

## 詳しく

### 左辺値と右辺値

| 種類 | 意味 | 例 |
| --- | --- | --- |
| 左辺値 | 名前があって、あとでまた使えるもの | 変数 `name`、`v[0]` |
| 右辺値 | 一時的なもの、もう使わないもの | `"abc"s`、`a + b` の結果、関数の戻り値、`std::move(x)` |

C++ は、**右辺値ならムーブ、左辺値ならコピー**を選びます。`std::move(x)` は、左辺値 `x` を「右辺値として扱って」と伝えるキャストです。

```cpp
#include <print>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<std::string> names;
  std::string hero = "勇者";

  names.push_back(hero);               // 左辺値 → コピー
  names.push_back(std::string("魔王"));  // 右辺値（一時オブジェクト） → ムーブ
  names.push_back(std::move(hero));    // std::move → ムーブ

  std::println("{} / hero は空？ {}", names, hero.empty());
}
```

```text title="実行結果"
["勇者", "魔王", "勇者"] / hero は空？ true
```

### 右辺値参照 T&&

`T&&` は右辺値だけを受け取る参照です。ムーブコンストラクタなどで使われます。

```cpp
void Take(std::string&& s);  // 右辺値（std::move したものなど）だけ受け取る
```

普段のコードで自分で書くことはあまりありません。

### 自作クラスのコピー・ムーブ

メンバが標準の型（string、vector、unique_ptr など）なら、コンパイラが**メンバごとにコピー・ムーブする**関数を自動で作ってくれます。何も書かないのが一番です（Rule of Zero）。

```cpp
#include <print>
#include <string>
#include <utility>
#include <vector>

struct Level {
  std::string name;
  std::vector<int> tiles;
  // コピー・ムーブは自動で作られる
};

int main() {
  Level a{"草原", std::vector<int>(1000, 1)};
  Level b = std::move(a);  // name も tiles もムーブされる
  std::println("{} {} / a.tiles {}", b.name, b.tiles.size(), a.tiles.size());
}
```

```text title="実行結果"
草原 1000 / a.tiles 0
```

自分でリソース（生ポインタ、ファイルハンドルなど）を管理するクラスを書くときだけ、コピー・ムーブを自分で書く（か禁止する）必要があります。

```cpp
class Texture {
 public:
  Texture(const Texture&) = delete;             // コピー禁止
  Texture& operator=(const Texture&) = delete;
  Texture(Texture&& other) noexcept;            // ムーブは許可（noexcept を付ける）
  Texture& operator=(Texture&& other) noexcept;
};
```

### noexcept を付ける理由

vector が再確保で要素を引っ越すとき、ムーブコンストラクタが `noexcept` でないと、安全のために**コピー**が使われます。自分で書くムーブには必ず `noexcept` を付けます（`= default` なら自動で付きます）。

### 戻り値は自動でムーブ

```cpp
std::vector<int> MakeTiles() {
  std::vector<int> tiles(10000);
  return tiles;  // コピーされない（コピー省略か、自動ムーブ）
}
```

`return std::move(tiles);` と書くと、コピー省略が効かなくなって**かえって遅くなる**ことがあります。

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| 読み込んだデータを渡す | `level.SetTiles(std::move(loaded))` |
| unique_ptr を vector に入れる | `objects.push_back(std::move(obj))` |
| コンストラクタでメンバへ | `explicit Enemy(std::string name) : name_(std::move(name)) {}` |
| ダブルバッファ | `std::swap(front, back)`（中はムーブ） |

## よくあるミス

??? failure "ムーブした変数を使う"
    ```cpp
    names.push_back(std::move(hero));
    std::println("{}", hero);  // 中身は未規定
    ```

??? failure "const な変数を std::move する"
    `const std::string s = ...; Take(std::move(s));` は、const は書き換えられないのでムーブできず、黙ってコピーになります。

??? failure "int や小さい構造体を move する"
    中にヒープを持たない型は、ムーブしてもコピーと同じです。付けても速くなりません。

## 理解度チェック

!!! question "Q1. ムーブで速くなる型はどれ？"
    `int`、`std::string`、`std::vector<float>`、`struct Vec2 { float x, y; }`、`std::unique_ptr<Enemy>`

    <div class="spoiler" markdown>

    **答え:** `std::string`、`std::vector<float>`、`std::unique_ptr<Enemy>`（中にヒープへのポインタを持っている型）。`int` と `Vec2` はコピーと同じです。unique_ptr はそもそもムーブしかできません。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] コピーは複製、ムーブは持ち主の付け替え
    - [x] もう使わない大きな値は `std::move` して渡す
    - [x] `return x;` に move は付けない
    - [x] 自分で書くムーブには `noexcept`

## 関連ページ

- [std::move / std::forward](../stl/utilities/move.md)
- [所有権](ownership.md)
- [cpprefjp: 右辺値参照・ムーブセマンティクス](https://cpprefjp.github.io/lang/cpp11/rvalue_ref_and_move_semantics.html)
