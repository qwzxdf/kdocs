---
title: const と引数の渡し方
tags:
  - 設計
---

# const と引数の渡し方

関数の引数を「値渡し」にするか「参照渡し」にするか、`const` を付けるか、は、C++ を書くたびに迷うところです。ここには**だいたいの正解**があり、それを守ると、**無駄なコピーが減り、バグも減り、読む人にも意図が伝わります**。`const` は「ここは変わらない」という**約束**で、コンパイラがその約束を守らせてくれます。この考え方を <strong>const 正しさ（const correctness）</strong> と呼びます。

!!! tip "ポイント"
    - **読むだけの引数は `const T&`**（大きい型）。**`int` や `float` などの小さい型は値渡し**。
    - **書き換えて返したい引数は `T&`**。ただし、戻り値で返せるなら戻り値にする。
    - **所有権を渡す（ムーブする）ときは `T`（値渡し）+ `std::move`**。
    - **メンバ関数は、変更しないなら `const` を付ける**（`int hp() const`）。
    - **変数も、変えないなら `const`**。最初から `const` にして、必要なときだけ外す。
    - 文字列を読むだけなら **`std::string_view`**、配列を読むだけなら **`std::span`**。

## 引数の渡し方の早見表

| 状況 | 書き方 | 例 |
| --- | --- | --- |
| 小さい型（`int`、`float`、`bool`、ポインタ、enum）を読む | **値渡し** `T` | `void SetHp(int hp)` |
| 大きい型（`std::string`、`std::vector`、自作の構造体）を**読むだけ** | **`const T&`** | `void Print(const Player& p)` |
| 文字列を**読むだけ** | **`std::string_view`**（値渡し） | `void Log(std::string_view msg)` |
| 配列を**読むだけ** | **`std::span<const T>`**（値渡し） | `float Sum(std::span<const float> v)` |
| 引数を**書き換える**（呼び出し側の変数を変える） | **`T&`** | `void Heal(Player& p)` |
| 引数を**受け取って、自分のものにする** | **`T`（値渡し）+ `std::move`** | `void SetName(std::string name)` |
| 引数がなくてもよい（省略可能） | `const T*`、`std::optional<T>` | `void Draw(const Texture* tex)` |
| 戻り値が大きいとき | **値で返す**（ムーブ・RVO が効く） | `std::vector<int> MakeList()` |

### 値渡しと const 参照の分かれ目

目安は、**ポインタ 2 つぶん（16 バイト）以下なら値渡し、それより大きければ `const&`**、です。

| 型 | 大きさ | 渡し方 |
| --- | --- | --- |
| `int`、`float`、`bool`、enum | 1〜8 バイト | 値渡し |
| `Vec2`（`float` 2 つ）、`Vec3` | 8〜12 バイト | 値渡しでよい |
| `Vec4`、`Mat4`、`std::string`、`std::vector` | 16 バイト以上 | `const&` |
| `std::string_view`、`std::span` | 16 バイト（ポインタ + 長さ） | **値渡し**（それ自体が参照の役目） |

## 悪い例：コピーが多く、意図が伝わらない

```cpp
// 値渡しで、読むだけの大きなデータをコピーしている
float Average(std::vector<float> values);           // 呼ぶたびに vector 全体がコピーされる
void Log(std::string message);                       // 文字列がコピーされる

// 逆に、小さな型を参照で渡している（意味のない間接参照）
void SetHp(const int& hp);

// 書き換えるのか、読むだけなのか、分からない
void Process(Player& player);                        // 中で player を変えている？ 見ただけでは不明
```

## 良い例：型が意図を語る

```cpp
float Average(std::span<const float> values);       // 読むだけ。vector でも array でも渡せる
void Log(std::string_view message);                  // 読むだけ。リテラルも string も渡せる
void SetHp(int hp);                                  // 小さい型は値渡し
void Heal(Player& player);                           // 書き換える、と分かる
void Inspect(const Player& player);                  // 読むだけ、と分かる
```

## const を付ける場所

### 変数に const

```cpp
const int kMaxEnemies = 100;          // 定数
const auto& config = LoadConfig();    // 参照を const にして、変更を防ぐ
for (const auto& enemy : enemies) {   // 読むだけなら const auto&
  Draw(enemy);
}
```

- **最初から `const` にして、変えたくなったときだけ外す**のが、バグを減らす習慣です
- 定数は `constexpr`（コンパイル時に決まるもの）にします

### メンバ関数に const

```cpp
class Player {
 public:
  int hp() const { return hp_; }       // 中身を変えない → const
  void TakeDamage(int d) { hp_ -= d; } // 中身を変える → const にしない

 private:
  int hp_ = 100;
};

void Show(const Player& p) {
  p.hp();           // OK：const 関数は呼べる
  // p.TakeDamage(5);  // エラー：const の Player に、変更する関数は呼べない
}
```

- **変更しない関数に `const` を付けないと、`const Player&` から呼べなくなります**。あとから付けるのは大変なので、最初から付けます

### ポインタと const の読み方

| 書き方 | 意味 |
| --- | --- |
| `const int* p` | 指す先の値を**変えられない**（ポインタは付け替えられる） |
| `int* const p` | ポインタを**付け替えられない**（指す先は変えられる） |
| `const int* const p` | どちらも変えられない |

`const` は「左のもの」にかかります（左がなければ右）。**`*` の左に `const` があれば、指す先が const** と覚えます。

## ムーブで受け取る（シンク引数）

引数を**受け取って、自分のメンバにする**ときは、**値渡し + `std::move`** が一番簡単で、速いです。

```cpp
class Enemy {
 public:
  explicit Enemy(std::string name) : name_(std::move(name)) {}  // 値で受け取って、ムーブ

 private:
  std::string name_;
};

Enemy a("slime");              // リテラルから作る → 1 回の確保
std::string n = "bat";
Enemy b(n);                    // コピーして渡す → 1 回のコピー
Enemy c(std::move(n));         // ムーブして渡す → コピーなし
```

`const std::string&` で受けると、**コピーが必ず 1 回**起きます。`std::string&&` と両方書くより、**値渡し + `std::move`** のほうが短く、ほぼ同じ速さです（[ムーブ](../../basics/move.md)）。

## 戻り値

| 書き方 | 使いどころ |
| --- | --- |
| `T`（値で返す） | **基本はこれ**。ムーブや RVO で、コピーは起きない |
| `const T&` | メンバ変数など、**持ち主が生きている間だけ**、読み取りで渡す（ゲッター） |
| `T&` | 書き換えさせたいとき（`operator[]` など） |
| `T*` | なくてもよいとき（`Find` が見つからなければ `nullptr`）。`std::optional<T>` のほうが分かりやすいことも |
| `const T`（値で返す const） | **付けない**（ムーブを妨げる） |

```cpp
class Inventory {
 public:
  const std::vector<Item>& items() const { return items_; }  // 読み取り専用で見せる
  std::vector<Item> TakeAll() { return std::move(items_); }   // 中身を渡して、空にする

 private:
  std::vector<Item> items_;
};
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎フレーム呼ぶ更新関数 | `void Update(float dt)`（小さい型は値渡し） |
| 描画に、モデルや行列を渡す | `void Draw(const Model& model, const Mat4& world)` |
| ログ、メッセージ | `void Log(std::string_view message)` |
| 配列を処理する関数 | `void Process(std::span<Enemy> enemies)` |
| 設定を読むだけ | `void Apply(const Config& config)` |
| コンテナにオブジェクトを追加する | `void Add(Enemy enemy)`（値渡し + `std::move`） |

## よくあるミス

??? failure "const なしで宣言して、const オブジェクトから呼べない"
    `int hp()`（`const` なし）のゲッターは、`const Player&` からは呼べません。**変更しない関数には、最初から `const` を付けます**。

??? failure "一時オブジェクトを `T&`（const なし）で受けようとする"
    `void F(std::string& s)` に `F("abc")` や `F(MakeName())` は渡せません（一時オブジェクトは、const でない参照に束縛できません）。読むだけなら `const std::string&` か `std::string_view` にします。

??? failure "`const` を付けた戻り値で、ムーブできなくなる"
    `const std::string GetName()` のように、**値の戻り値に const** を付けると、ムーブが効かず、コピーになります。付けません。

??? failure "参照のメンバ変数を持つ"
    `class A { const B& b_; };` は、代入できず、`b_` の寿命にも注意が必要です。<strong>所有しない相手は、ポインタ（または、引数で都度渡す）</strong>ほうが扱いやすいです。

??? failure "`const_cast` で const を外す"
    「約束を破る」操作です。外さないと動かない設計は、間違っています。関数の引数を `const` にするか、`mutable` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読むだけ：小さい型は値、大きい型は `const&`、文字列は `string_view`、配列は `span`
    - [x] 書き換える：`T&`。受け取って持つ：値渡し + `std::move`
    - [x] 変更しないメンバ関数・変数には、最初から `const`
    - [x] 戻り値は値で返す（`const` を付けない）
    - [x] 型を見れば「読むだけ・書き換える・受け取る」が分かるようにする

## 関連ページ

- [設計の基本原則](principles.md)
- [所有権とライフタイム設計](ownership-lifetime.md)
- [参照（基礎）](../../basics/reference.md)
- [ムーブ（基礎）](../../basics/move.md)
- [std::string_view](../../stl/utilities/string_view.md) / [std::span](../../stl/containers/span.md)
