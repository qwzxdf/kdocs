---
title: std::move
summary: "コピーせず中身を「移す」ための道具（`move`・`forward`）。"
order: 51
tags:
  - ユーティリティ
---

# std::move

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

大きな `vector` を関数に渡したり、別の変数に代入したりするとき、普通はコピーが起きて、中身が全部複製されます。もう使わない値なら、コピーする必要はなく、中身を付け替えるだけで足ります。`std::move` は、「この変数の中身はもう使わないので、持っていっていい」と伝える関数です。それ自体は何もコピーも移動もしませんが、これを付けた値は、コピーの代わりにムーブ（中身の付け替え）が選ばれます。

!!! tip "ポイント"
    - <strong>もう使わない大きな値（string、vector、unique_ptr）を渡すときに `std::move` を付ける。</strong>
    - `std::move` したあとの変数は「空っぽ（中身は未規定）」として扱い、代入し直すまで使わない。
    - `return local;` には付けない（付けると逆に遅くなることがある）。
    - 「転送」するときは [`std::forward`](forward.md)。普段のコードでは使わない。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) の考え方を先に読むと分かりやすいです。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::move`](#move) | <span class="rank rank-often">よく使う</span> | ムーブしていい値（右辺値）として扱わせる |

## よくある使い方

### 1. 大きなものを受け渡す

```cpp
#include <print>
#include <string>
#include <utility>
#include <vector>

class Level {
 public:
  // 受け取った vector を自分のメンバにムーブする
  explicit Level(std::vector<int> tiles) : tiles_(std::move(tiles)) {}
  std::size_t size() const { return tiles_.size(); }

 private:
  std::vector<int> tiles_;
};

int main() {
  std::vector<int> loaded(10000, 1);  // ファイルから読み込んだとする
  Level level(std::move(loaded));     // コピーせずに渡す
  std::println("level {} / loaded {}", level.size(), loaded.size());
}
```

```text title="実行結果"
level 10000 / loaded 0
```

`loaded` の中身は level に移ったので、`loaded` は（この実装では）空になっています。ムーブ後の中身は規格上は「未規定」です。

### 2. vector に入れる

```cpp
#include <memory>
#include <print>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<std::string> names;
  std::string name = "とても長い名前のプレイヤー";
  names.push_back(std::move(name));  // コピーではなくムーブ

  std::vector<std::unique_ptr<int>> ptrs;
  auto p = std::make_unique<int>(5);
  ptrs.push_back(std::move(p));  // unique_ptr はムーブしか入れられない
  std::println("{} {}", names.size(), *ptrs[0]);
}
```

```text title="実行結果"
1 5
```

## 関数の詳しい説明

### std::move {#move}

```cpp
template <class T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 何でも | ムーブしてよいと伝えたい値 |

- 戻り値: `t` を右辺値参照にキャストしたもの。**これ自体は何も移動しない**
- 移動が起きるのは、戻り値を受け取ったムーブコンストラクタ・ムーブ代入の中

<div class="mem">
<div class="mem-step"><span class="mem-label">コピー</span><span class="mem-note">a の中身（ヒープの文字列）を丸ごと複製して b に作る → 遅い</span></div>
<div class="mem-step"><span class="mem-label">ムーブ</span><span class="mem-note">a が持っていたヒープへのポインタを b に付け替え、a は空にする → 速い</span></div>
</div>

<div class="anim" data-label="b = std::move(a)">
A | _ # a が持っている
_ | >A # 中身が b に移る。a は空（有効だが中身は不定）
</div>

```cpp
#include <print>
#include <string>
#include <utility>

int main() {
  std::string a = "data";
  std::string b = std::move(a);  // a の中身が b に移る
  a = "new";                     // 代入し直せばまた普通に使える
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
new data
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

`vector` に大きなオブジェクトを入れるとき、`vec.push_back(std::move(obj))` と書くと、コピーを避けられます。`unique_ptr` は、コピーできないので、`std::move` で移すしかありません。

関数の引数で、「受け取った値を自分で持つ」場合は、値渡しで受けて、`std::move` でメンバーに入れます。`Enemy(std::string name) : name_(std::move(name)) {}` の形です。呼ぶ側が右辺値を渡せばムーブ、左辺値ならコピーになります。

ローカル変数を `return` するときは、`std::move` を付けません。コンパイラーが自動で最適化（戻り値最適化）するので、付けると逆に遅くなることがあります。

## パフォーマンス

- `int` や `float`、小さな構造体はムーブしてもコピーと同じです（速くならない）。効果があるのは、中でヒープを持っている型（string、vector、unique_ptr など）です。
- 自作のクラスのムーブコンストラクタには `noexcept` を付けます（付けないと vector の再確保でコピーされる）。`= default` なら自動で付きます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| ムーブした後の変数の中身を使う | 標準ライブラリの型なら「有効だが未規定」な状態。値に頼ると壊れる |
| ムーブした後の unique_ptr を `->` で使う | 空なので未定義動作 |

## よくあるミス

??? failure "return に std::move を付ける"
    ```cpp
    std::vector<int> Make() {
      std::vector<int> v(100);
      return std::move(v);  // NG: 戻り値の最適化（コピー省略）が効かなくなる
      return v;             // OK: 自動でムーブ（か、それより速い最適化）される
    }
    ```

??? failure "const の値を move する"
    `const std::string s = ...; Take(std::move(s));` はムーブにならず、コピーされます（const は書き換えられないため）。

??? failure "ムーブした変数をそのまま使う"
    ```cpp
    names.push_back(std::move(name));
    std::println("{}", name);  // 中身は分からない
    ```

## 類似

| 名前 | 違い |
| --- | --- |
| コピー | 中身を複製する。元はそのまま |
| [`std::unique_ptr`](unique_ptr.md) | ムーブでしか渡せない型の代表 |

## コンパイラ対応

C++11 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] もう使わない値に付けて、コピーの代わりにムーブさせる。
    - [x] ムーブしたあとの変数は、代入し直すまで使わない。
    - [x] `return local;` には付けない。

## 関連ページ

- [cpprefjp: std::move](https://cpprefjp.github.io/reference/utility/move.html)
- [cppreference: std::forward](https://en.cppreference.com/w/cpp/utility/forward)
