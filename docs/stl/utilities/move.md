---
title: std::move / std::forward
tags:
  - ユーティリティ
---

# std::move / std::forward

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

`std::move` は、<strong>「この変数の中身はもう使わないので、持っていっていい」と伝えるための関数</strong>です。それ自体は何もコピーも移動もしませんが、これを付けた値を代入や関数に渡すと、コピーの代わりに**ムーブ**（中身の付け替え）が選ばれるようになります。`std::forward` は、テンプレートで受け取った引数を「受け取ったときの形のまま」次の関数へ渡すためのものです。

!!! tip "ポイント"
    - <strong>もう使わない大きな値（string、vector、unique_ptr）を渡すときに `std::move` を付ける。</strong>
    - `std::move` したあとの変数は「空っぽ（中身は未規定）」として扱い、代入し直すまで使わない。
    - `return local;` には付けない（付けると逆に遅くなることがある）。
    - `std::forward` はテンプレートで「転送」するときだけ。普段のコードでは使わない。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) の考え方を先に読むと分かりやすいです。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::move`](#move) | <span class="rank rank-often">よく使う</span> | ムーブしていい値（右辺値）として扱わせる |
| [`std::forward`](#forward) | <span class="rank rank-sometimes">たまに</span> | 受け取った形（左辺値 / 右辺値）のまま転送する |
| [`std::exchange`](#exchange) | <span class="rank rank-sometimes">たまに</span> | 新しい値を入れて、古い値を返す |
| [`std::swap`](#swap) | <span class="rank rank-sometimes">たまに</span> | 2 つの値を交換する |
| [`std::move_if_noexcept`](#move_if_noexcept) | <span class="rank rank-rare">知ってるだけ</span> | ムーブが例外を投げないときだけムーブする |

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

### std::forward {#forward}

```cpp
template <class T>
constexpr T&& forward(std::remove_reference_t<T>& t) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `T` | 受け取ったときのテンプレート引数（`Args` など）をそのまま書く |

- 「左辺値で渡されたら左辺値のまま、右辺値で渡されたら右辺値のまま」次へ渡します（完全転送）
- `template <class... Args> void F(Args&&... args)` の中で使います

```cpp
#include <memory>
#include <print>
#include <string>
#include <utility>
#include <vector>

struct Enemy {
  Enemy(std::string n, int h) : name(std::move(n)), hp(h) {}
  std::string name;
  int hp;
};

class EnemyPool {
 public:
  // 引数をそのまま Enemy のコンストラクタへ転送する
  template <class... Args>
  Enemy& Spawn(Args&&... args) {
    return enemies_.emplace_back(std::forward<Args>(args)...);
  }

 private:
  std::vector<Enemy> enemies_;
};

int main() {
  EnemyPool pool;
  std::string name = "スライム";
  pool.Spawn(name, 10);          // name は左辺値 → コピーされる（name は残る）
  pool.Spawn(std::string("ゴブリン"), 30);  // 右辺値 → ムーブされる
  std::println("{}", name);
}
```

```text title="実行結果"
スライム
```

!!! note "実際は"
    自分でラッパー関数（`emplace` のようなもの）を作るとき以外は使いません。

### std::exchange <span class="ver ver-14">C++14</span> {#exchange data-toc-label="std::exchange"}

```cpp
template <class T, class U = T>
constexpr T exchange(T& obj, U&& new_value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | `T&` | 書き換える変数 |
| `new_value` | 値 | 新しく入れる値 |

- 戻り値: `obj` の**古い値**

<div class="anim" data-label="std::exchange(a, 9)">
5 # a = 5
*5 # 古い値（5）を返す
+9 # a に新しい値 9 を入れる
</div>

```cpp
#include <print>
#include <utility>

int main() {
  int pending_damage = 25;
  int applied = std::exchange(pending_damage, 0);  // 取り出して 0 にリセット
  std::println("{} {}", applied, pending_damage);
}
```

```text title="実行結果"
25 0
```

!!! note "実際は"
    「溜まっていたものを取り出してリセット」「前の状態を覚えつつ新しい状態にする」を 1 行で書けます。ムーブコンストラクタの実装でもよく使います。

### std::swap {#swap}

```cpp
template <class T>
constexpr void swap(T& a, T& b) noexcept(/* 条件 */);
```

- `a` と `b` の中身を交換します。vector や string ならポインタの付け替えだけなので速いです

<div class="anim" data-label="std::swap(a, b)">
A | B # a と b
>B | >A # 中身を入れ替える
</div>

```cpp
#include <print>
#include <utility>

int main() {
  int front = 1;
  int back = 2;
  std::swap(front, back);
  std::println("{} {}", front, back);
}
```

```text title="実行結果"
2 1
```

### std::move_if_noexcept {#move_if_noexcept}

```cpp
template <class T>
constexpr auto move_if_noexcept(T& x) noexcept;
```

- ムーブコンストラクタが `noexcept` ならムーブ、そうでなければコピーとして扱わせます。vector の再確保の中で使われている仕組みで、自分で書くことはまずありません

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 読み込んだデータを持ち主に渡す | ファイルから読んだ vector をレベルに渡す |
| unique_ptr の受け渡し | `objects.push_back(std::move(obj))` |
| コンストラクタで引数をメンバへ | `: name_(std::move(name))` |
| ダブルバッファ | `std::swap(current, next)` |

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

## 理解度チェック

!!! question "Q1. `std::move(x)` を書いただけの行は何をする？"
    ```cpp
    std::string x = "abc";
    std::move(x);
    ```

    <div class="spoiler" markdown>

    **答え:** 何もしません。`std::move` はキャストするだけで、受け取る側がいないので移動は起きず、`x` は `"abc"` のままです。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| コピー | 中身を複製する。元はそのまま |
| [`std::unique_ptr`](unique_ptr.md) | ムーブでしか渡せない型の代表 |

## コンパイラ対応

C++11 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] もう使わない大きな値は `std::move` して渡す
    - [x] ムーブ後の変数は使わない
    - [x] `return x;` に move は付けない
    - [x] `std::forward` はテンプレートの転送専用

## 関連ページ

- [cpprefjp: std::move](https://cpprefjp.github.io/reference/utility/move.html)
- [cppreference: std::forward](https://en.cppreference.com/w/cpp/utility/forward)
