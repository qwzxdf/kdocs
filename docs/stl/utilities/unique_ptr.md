---
title: std::unique_ptr
summary: "持ち主が 1 つだけの、スマートポインタ。スコープを出ると自動で解放される。"
order: 45
tags:
  - ユーティリティ
  - メモリ
---

# std::unique_ptr

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`new` で作ったオブジェクトは、どこかで `delete` しないとメモリリークになります。逆に二重に `delete` すると、プログラムが壊れます。持ち主が複雑になるほど、このミスは増えます。`std::unique_ptr` は、`new` で作ったオブジェクトを持ち、自分が消えるときに自動で `delete` してくれるポインターです。持ち主は常に 1 人で、コピーはできません。移すときは `std::move` でムーブします。

!!! tip "ポイント"
    - <strong>`new` / `delete` を自分で書かず、`std::make_unique<T>(...)` で作る。</strong>
    - 普通のポインタと同じく `->` と `*` で使える。速さも生ポインタとほぼ同じ。
    - コピーできない。渡すときは `std::move` で持ち主を移す。
    - 関数に「使わせるだけ」なら、`unique_ptr` ではなく **`T&` か `T*` で渡す**。
    - ポリモーフィズム（基底クラスのポインタで派生クラスを持つ）の基本形。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) と [所有権](../../basics/ownership.md) を先に読むと分かりやすいです。

## 宣言

```cpp
template <class T, class Deleter = std::default_delete<T>>
class unique_ptr;

template <class T, class Deleter>
class unique_ptr<T[], Deleter>;  // 配列版
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 持つオブジェクトの型 | 必ず |
| `Deleter` | 消すときの処理 | **C のライブラリの解放関数を呼びたいときだけ**（[フラグ・オプション](#フラグオプション)） |

### 作り方

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `auto p = std::make_unique<Enemy>(引数...);` | <span class="rank rank-must">必須</span> | 作って持つ |
| `std::unique_ptr<Base> p = std::make_unique<Derived>();` | <span class="rank rank-must">必須</span> | 派生クラスを基底クラスのポインタで持つ |
| `std::unique_ptr<Enemy> p;` | <span class="rank rank-often">よく使う</span> | 空（`nullptr`） |
| `auto a = std::make_unique<int[]>(n);` | <span class="rank rank-rare">知ってるだけ</span> | 配列（普通は vector を使う） |
| `std::unique_ptr<Enemy> p(new Enemy());` | <span class="rank rank-rare">知ってるだけ</span> | 古い書き方。使わない |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator->`](#arrow) | <span class="rank rank-must">必須</span> | メンバにアクセス | O(1) |
| [`operator*`](#deref) | <span class="rank rank-must">必須</span> | 中身の参照 | O(1) |
| [`operator bool`](#bool) | <span class="rank rank-must">必須</span> | 空でないか | O(1) |
| [`get`](#get) | <span class="rank rank-often">よく使う</span> | 生ポインタを取り出す（持ち主は変わらない） | O(1) |
| [`reset`](#reset) | <span class="rank rank-often">よく使う</span> | 今のものを消して、空にする（または別のものを持つ） | O(1) |
| [ムーブ代入 / ムーブコンストラクタ](#move) | <span class="rank rank-often">よく使う</span> | 持ち主を移す | O(1) |
| [`release`](#release) | <span class="rank rank-rare">知ってるだけ</span> | 消さずに手放して生ポインタを返す | O(1) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |
| [`get_deleter`](#get_deleter) | <span class="rank rank-rare">知ってるだけ</span> | 削除処理を取得 | O(1) |
| [`operator[]`](#index) | <span class="rank rank-rare">知ってるだけ</span> | 配列版の要素アクセス | O(1) |

## よくある使い方

### 1. 作って使う（自動で消える）

```cpp
#include <memory>
#include <print>
#include <string>

struct Enemy {
  explicit Enemy(std::string n) : name(std::move(n)) { std::println("{} 出現", name); }
  ~Enemy() { std::println("{} 消滅", name); }
  std::string name;
  int hp = 100;
};

int main() {
  {
    auto boss = std::make_unique<Enemy>("ドラゴン");
    boss->hp -= 30;
    std::println("HP {}", boss->hp);
  }  // ここで boss が消えるので、自動で delete される
  std::println("ブロックの外");
}
```

```text title="実行結果"
ドラゴン 出現
HP 70
ドラゴン 消滅
ブロックの外
```

### 2. ポリモーフィズム：いろいろな敵を 1 つの vector に入れる

```cpp
#include <memory>
#include <print>
#include <vector>

class GameObject {
 public:
  virtual ~GameObject() = default;  // 基底クラスのデストラクタは virtual にする
  virtual void Update() = 0;
};

class Player : public GameObject {
 public:
  void Update() override { std::println("プレイヤー更新"); }
};

class Enemy : public GameObject {
 public:
  void Update() override { std::println("敵更新"); }
};

int main() {
  std::vector<std::unique_ptr<GameObject>> objects;
  objects.push_back(std::make_unique<Player>());
  objects.push_back(std::make_unique<Enemy>());

  for (auto& obj : objects) {
    obj->Update();
  }
}
```

```text title="実行結果"
プレイヤー更新
敵更新
```

### 3. 持ち主を移す・使わせるだけで渡す

```cpp
#include <memory>
#include <print>
#include <utility>

struct Weapon {
  int power = 10;
};

class Player {
 public:
  // 持ち主になる（受け取って自分のものにする）
  void Equip(std::unique_ptr<Weapon> weapon) { weapon_ = std::move(weapon); }

  const Weapon* weapon() const { return weapon_.get(); }

 private:
  std::unique_ptr<Weapon> weapon_;
};

// 使わせるだけ（持ち主は変わらない）
void PrintPower(const Weapon& weapon) { std::println("攻撃力 {}", weapon.power); }

int main() {
  auto sword = std::make_unique<Weapon>();
  PrintPower(*sword);

  Player player;
  player.Equip(std::move(sword));  // 持ち主が player に移る
  std::println("sword は空？ {}", sword == nullptr);

  if (const Weapon* w = player.weapon()) {
    PrintPower(*w);
  }
}
```

```text title="実行結果"
攻撃力 10
sword は空？ true
攻撃力 10
```

## 関数の詳しい説明

### operator-> {#arrow}

```cpp
pointer operator->() const noexcept;
```

- 持っているオブジェクトのメンバにアクセスします。**空のとき未定義動作**

### operator* {#deref}

```cpp
std::add_lvalue_reference_t<T> operator*() const;
```

- 持っているオブジェクトの参照を返します。**空のとき未定義動作**

```cpp
#include <memory>
#include <print>

int main() {
  auto score = std::make_unique<int>(100);
  *score += 50;
  std::println("{}", *score);
}
```

```text title="実行結果"
150
```

### operator bool {#bool}

```cpp
explicit operator bool() const noexcept;
```

- 何かを持っていれば `true`、空なら `false`

```cpp
#include <memory>
#include <print>

struct Target {
  int id;
};

int main() {
  std::unique_ptr<Target> target;
  if (!target) {
    std::println("ターゲットなし");
  }
  target = std::make_unique<Target>(3);
  if (target) {
    std::println("ターゲット {}", target->id);
  }
}
```

```text title="実行結果"
ターゲットなし
ターゲット 3
```

### get {#get}

```cpp
pointer get() const noexcept;
```

- 戻り値: 持っているオブジェクトの生ポインタ（空なら `nullptr`）。**持ち主は変わらない**

```cpp
#include <memory>
#include <print>

struct Texture {
  int width = 256;
};

// C の API や、所有しない関数は生ポインタで受け取る
void Draw(const Texture* texture) {
  if (texture != nullptr) {
    std::println("幅 {} を描画", texture->width);
  }
}

int main() {
  auto tex = std::make_unique<Texture>();
  Draw(tex.get());
}
```

```text title="実行結果"
幅 256 を描画
```

!!! warning
    `get()` で取ったポインタを `delete` してはいけません（二重解放になる）。また、unique_ptr が消えたあとは使えません。

### reset {#reset}

```cpp
void reset(pointer p = pointer()) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | 生ポインタ | 新しく持つもの。省略すると空になる |

- 今持っているものを `delete` してから、`p` を持ちます

<div class="anim" data-label="p.reset()">
A # p が所有している
xA # 所有しているものを delete する
_ # p は空
</div>

```cpp
#include <memory>
#include <print>

struct Effect {
  ~Effect() { std::println("エフェクト終了"); }
};

int main() {
  auto effect = std::make_unique<Effect>();
  effect.reset();  // 今すぐ消す
  std::println("空？ {}", effect == nullptr);
}
```

```text title="実行結果"
エフェクト終了
空？ true
```

!!! note "実際は"
    「今すぐ消したい」は `reset()`、「別のものに入れ替えたい」は `p = std::make_unique<T>()` と書きます（代入でも古いものは消えます）。

### ムーブ代入 / ムーブコンストラクタ {#move}

```cpp
unique_ptr(unique_ptr&& other) noexcept;
unique_ptr& operator=(unique_ptr&& other) noexcept;
```

- `other` が持っていたものを受け取ります。`other` は空になります
- コピー（`unique_ptr(const unique_ptr&)`）は**削除されている**のでコンパイルエラーになります

<div class="anim" data-label="b = std::move(a)">
A | _ # a が所有している
_ | >A # 所有権が b に移る。a は空になる
</div>

```cpp
#include <memory>
#include <print>
#include <utility>

int main() {
  auto a = std::make_unique<int>(7);
  // auto b = a;          // コンパイルエラー: コピーできない
  auto b = std::move(a);  // OK: 持ち主を移す
  std::println("a は空？ {} / b = {}", a == nullptr, *b);
}
```

```text title="実行結果"
a は空？ true / b = 7
```

### release {#release}

```cpp
pointer release() noexcept;
```

- 持っているものを**消さずに手放し**、生ポインタを返します。unique_ptr は空になります
- 返されたポインタは、自分で `delete` する責任があります

!!! note "実際は"
    古い API に「持ち主ごと渡す」ときくらいしか使いません。`release()` の戻り値を捨てるとメモリリークになります（`reset()` と間違えやすい）。

<div class="anim" data-label="Enemy* raw = p.release()">
A | _ # p が所有している
_ | *A # 所有をやめて生ポインタを返す。delete はされない
</div>

### swap {#swap}

```cpp
void swap(unique_ptr& other) noexcept;
```

- 2 つの unique_ptr の中身を交換します

<div class="anim" data-label="a.swap(b)">
A | B # a と b
>B | >A # 所有しているものを入れ替える
</div>

### get_deleter {#get_deleter}

```cpp
Deleter& get_deleter() noexcept;
```

- 削除処理（Deleter）を取得します。自作の Deleter を使うとき以外は使いません

### operator[] {#index}

```cpp
T& operator[](std::size_t i) const;  // unique_ptr<T[]> のみ
```

- 配列版の i 番目の要素。配列が欲しいなら普通は `std::vector` を使います

## フラグ・オプション

`Deleter`（2 つ目のテンプレート引数）で「消すときの処理」を変えられます。

| 指定 | 重要度 | 意味 | 使う場面 |
| --- | --- | --- | --- |
| `std::default_delete<T>`（省略時） | <span class="rank rank-must">必須</span> | `delete` する | 普通はこれ |
| 関数ポインタ / ラムダ | <span class="rank rank-sometimes">たまに</span> | 好きな関数で解放する | C のライブラリ（SDL、FILE など）の解放関数を呼ぶ |

```cpp
#include <cstdio>
#include <memory>
#include <print>

struct FileCloser {
  void operator()(std::FILE* f) const {
    std::fclose(f);
    std::println("閉じた");
  }
};

int main() {
  std::unique_ptr<std::FILE, FileCloser> file(std::tmpfile());
  std::fputs("save data", file.get());
}  // ここで自動で fclose される
```

```text title="実行結果"
閉じた
```

!!! note "実際は"
    SDL の `SDL_Texture*` を `SDL_DestroyTexture` で消す、のようなときに使います。C のライブラリを使うときの定番です。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    Enemy* boss = new Enemy("ドラゴン");
    // ...
    delete boss;  // 忘れるとリーク。途中で return しても忘れる

    std::vector<GameObject*> objects;  // 消すのを忘れやすい
    ```

=== "今の書き方"

    ```cpp
    auto boss = std::make_unique<Enemy>("ドラゴン");
    // delete 不要

    std::vector<std::unique_ptr<GameObject>> objects;
    ```

### operator= {#op_assign}

```cpp
unique_ptr& operator=(unique_ptr&& r) noexcept;
unique_ptr& operator=(std::nullptr_t) noexcept;
```

- 計算量: 定数 + 解放

所有権をムーブで受け取ります（コピーはできません）。それまで持っていたものは解放されます。`nullptr` を代入すると、解放して空になります。

## ゲームでの使いどころ

ゲームオブジェクトの持ち主として使います。`std::vector<std::unique_ptr<GameObject>>` に、`Player`、`Enemy` などの派生クラスを入れて管理します。リストから外せば、オブジェクトも自動で消えます。

シーンの切り替えにも向いています。`std::unique_ptr<Scene> current_scene_;` を新しいシーンに置き換えると、前のシーンが自動で破棄されます。大きなリソース（テクスチャやサウンド）の持ち主を、1 か所に決めておく使い方も一般的です。

ヘッダーに実装を見せたくないときの Pimpl というイディオムでは、`std::unique_ptr<Impl> impl_;` を使います。C のライブラリのハンドルは、デリーターを付けた `unique_ptr` にすると、スコープを抜けるときに自動で解放されます。

## パフォーマンス

- Deleter を指定しなければ、**中身は生ポインタ 1 個だけ**で、`->` も生ポインタと同じ速さです。
- 作るときはヒープ確保（`new`）が起きます。小さいものを大量に作るなら、vector に直接入れる（ポインタにしない）ほうが速いです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の unique_ptr を `->` / `*` で使う | 未定義動作 |
| `get()` で取ったポインタを `delete` する | 二重解放（未定義動作） |
| 同じ生ポインタから unique_ptr を 2 つ作る | 二重解放（未定義動作） |
| 基底クラスのデストラクタが virtual でない | 派生クラスのデストラクタが呼ばれない（未定義動作） |

## よくあるミス

??? failure "コピーしようとしてコンパイルエラー"
    ```cpp
    std::vector<std::unique_ptr<Enemy>> enemies;
    auto e = std::make_unique<Enemy>();
    enemies.push_back(e);             // エラー: コピーできない
    enemies.push_back(std::move(e));  // OK
    ```

    範囲 for も `for (auto e : enemies)` はコピーになるのでエラーです。`for (auto& e : enemies)` にします。

??? failure "関数の引数を全部 unique_ptr にする"
    ```cpp
    void Draw(std::unique_ptr<Sprite> sprite);   // 呼ぶと持ち主が移ってしまう
    void Draw(const std::unique_ptr<Sprite>& s);  // 動くが、unique_ptr 以外から呼べない

    void Draw(const Sprite& sprite);  // OK: 使わせるだけ
    ```

??? failure "ムーブしたあとの変数を使う"
    `std::move(p)` で渡したあとの `p` は空です。`p->` は未定義動作です。

??? failure "基底クラスのデストラクタに virtual を付け忘れる"
    `std::unique_ptr<Base>` で派生クラスを持つなら、`virtual ~Base() = default;` が必要です。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::shared_ptr`](shared_ptr.md) | 持ち主が複数。参照カウントのぶん重い | 本当に複数が持ち主のとき（まれ） |
| 生ポインタ `T*` | 持ち主ではない（消さない） | 使わせるだけ、参照するだけ |
| 参照 `T&` | null にならない生ポインタ | 必ずある相手を使わせるとき |
| [`std::optional<T>`](optional.md) | ヒープを使わず、値を直接持つ | 「あるかないか」だけで、ポリモーフィズムが要らない |

## コンパイラ対応

C++11 からある機能です。`std::make_unique` は C++14 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `new` の代わりに `std::make_unique<T>(...)`。delete は書かない
    - [x] コピー不可。移すときは `std::move`
    - [x] 使わせるだけなら `T&` / `T*` で渡す
    - [x] 基底クラスのデストラクタは virtual

## 関連ページ

- [cpprefjp: std::unique_ptr](https://cpprefjp.github.io/reference/memory/unique_ptr.html)
- [cppreference: std::unique_ptr](https://en.cppreference.com/w/cpp/memory/unique_ptr)
