---
title: 継承と仮想関数
tags:
  - 基礎
---

# 継承と仮想関数

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
</div>

**継承**は、**あるクラス（基底クラス）の性質を受け継いだ新しいクラス（派生クラス）を作る仕組み**です。**仮想関数**（`virtual`）を使うと、基底クラスのポインタや参照から呼んだときに、**実際のオブジェクトの種類に合った関数**が呼ばれます（ポリモーフィズム）。「敵もプレイヤーもアイテムも `GameObject` として同じ vector に入れて、`Update()` を呼ぶとそれぞれの処理が動く」という書き方ができるのは、この仕組みのおかげです。

!!! tip "ポイント"
    - 基底クラスに `virtual void Update();`、派生クラスで `void Update() override;`。
    - **基底クラスのデストラクタは `virtual`** にする（付けないと派生クラスの片付けが呼ばれない）。
    - 派生クラスを入れるときは `std::vector<std::unique_ptr<Base>>`（値で入れると切り落とされる）。
    - 継承を深くしすぎない。ゲームでは「継承よりコンポーネント（組み合わせ）」が主流（[コンポーネント指向](../engine/component.md)）。

!!! info "このページを読む前に"
    [ポインタ](pointer.md) と [`std::unique_ptr`](../stl/utilities/unique_ptr.md) を先に読むと分かりやすいです。

## 基本

<div class="anim" data-type="graph" data-label="仮想関数：オブジェクトの持つ vptr から、vtable を引いて、実際の関数を呼ぶ">
n p Enemy*_e 0 1 hit
---
n p Enemy*_e 0 1
n o Goblin_オブジェクト_（vptr_を持つ） 1 1 hit
l p o hit 指す
---
n p Enemy*_e 0 1
n o Goblin_オブジェクト_（vptr_を持つ） 1 1
n vt Goblin_の_vtable_（関数の表） 2 1 hit
l p o - 指す
l o vt hit vptr
---
n p Enemy*_e 0 1
n o Goblin_オブジェクト_（vptr_を持つ） 1 1
n vt Goblin_の_vtable_（関数の表） 2 1
n f Goblin::Attack() 3 1 hit
l p o - 指す
l o vt - vptr
l vt f hit 表を引く
</div>

```cpp
#include <memory>
#include <print>
#include <vector>

class GameObject {
 public:
  virtual ~GameObject() = default;  // 基底クラスのデストラクタは virtual
  virtual void Update() = 0;        // = 0 は「派生クラスで必ず書く」（純粋仮想関数）
  virtual void Draw() const { std::println("  （共通の描画）"); }
};

class Player : public GameObject {
 public:
  void Update() override { std::println("プレイヤー: 入力を見て動く"); }
};

class Enemy : public GameObject {
 public:
  void Update() override { std::println("敵: プレイヤーを追う"); }
  void Draw() const override { std::println("  敵の描画"); }
};

int main() {
  std::vector<std::unique_ptr<GameObject>> objects;
  objects.push_back(std::make_unique<Player>());
  objects.push_back(std::make_unique<Enemy>());

  for (const auto& obj : objects) {
    obj->Update();  // 実際の種類に合った Update が呼ばれる
    obj->Draw();
  }
}
```

```text title="実行結果"
プレイヤー: 入力を見て動く
  （共通の描画）
敵: プレイヤーを追う
  敵の描画
```

## 詳しく

### キーワードのまとめ

| 書き方 | 意味 |
| --- | --- |
| `class Derived : public Base` | Base を継承する（ほぼ必ず `public`） |
| `virtual void F();` | 派生クラスで上書きできる関数 |
| `virtual void F() = 0;` | 純粋仮想関数。派生クラスで必ず書く。これがあるクラスは直接作れない（抽象クラス） |
| `void F() override;` | 基底クラスの仮想関数を上書きする（書き間違いをコンパイラが見つけてくれる） |
| `void F() final;` / `class X final` | これ以上上書き・継承させない |
| `virtual ~Base() = default;` | 仮想デストラクタ |
| `protected:` | 自分と派生クラスからだけ使える |

### override を必ず付ける理由

```cpp
class Base {
 public:
  virtual ~Base() = default;
  virtual void Update(float dt) {}
};

class Bad : public Base {
 public:
  void Update(double dt) {}  // 引数の型が違うので、上書きではなく別の関数になってしまう
};

class Good : public Base {
 public:
  // void Update(double dt) override {}  // コンパイルエラーで間違いに気づける
  void Update(float dt) override {}
};
```

### 仮想デストラクタが必要な理由

```cpp
#include <memory>
#include <print>

class Base {
 public:
  virtual ~Base() { std::println("Base の片付け"); }
};

class Boss : public Base {
 public:
  ~Boss() override { std::println("Boss の片付け（エフェクトの解放など）"); }
};

int main() {
  std::unique_ptr<Base> p = std::make_unique<Boss>();
}  // virtual なので Boss → Base の順に両方呼ばれる
```

```text title="実行結果"
Boss の片付け（エフェクトの解放など）
Base の片付け
```

`virtual` が無いと `Base` のデストラクタしか呼ばれず、未定義動作になります。

### スライシング（切り落とし）

```cpp
std::vector<GameObject> objects;  // 値で持つと…
objects.push_back(Enemy{});       // Enemy の部分が切り落とされて GameObject だけが残る
```

派生クラスを基底クラスの「値」に入れると、派生クラスの部分が失われます。必ずポインタ（`unique_ptr`）か参照で扱います。

### 派生クラスかどうか調べる（dynamic_cast）

```cpp
#include <memory>
#include <print>

struct GameObject {
  virtual ~GameObject() = default;
};
struct Enemy : GameObject {
  int hp = 50;
};

int main() {
  std::unique_ptr<GameObject> obj = std::make_unique<Enemy>();
  if (auto* enemy = dynamic_cast<Enemy*>(obj.get())) {  // Enemy なら非 nullptr
    std::println("敵だった。HP {}", enemy->hp);
  }
}
```

```text title="実行結果"
敵だった。HP 50
```

`dynamic_cast` を多用しているなら、設計を見直すサインです（仮想関数で解決できないか考える）。

### 仮想関数のコスト

- 仮想関数の呼び出しは、オブジェクトが持つ「仮想関数テーブル」を経由する**間接呼び出し**になります。普通の関数より少し遅く、インライン化もされにくいです。
- 何十万回も呼ぶ処理（パーティクル 1 個ずつなど）では、仮想関数よりも「種類ごとに vector を分けて普通の関数で回す」ほうが速くなります。

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| シーン | `class Scene { virtual void Update(); virtual void Draw(); }` を継承した `TitleScene`、`GameScene` |
| コンポーネントの基底 | `class Component { virtual void Update(float dt); }` |
| ステート | `class State { virtual void Enter(); virtual void Update(); }` |
| AI の行動 | `class Action { virtual bool Execute(); }` |

## よくあるミス

??? failure "基底クラスのデストラクタに virtual を付け忘れる"
    `unique_ptr<Base>` で派生クラスを持つなら必須です。

??? failure "override を付けずに、上書きしたつもりになる"
    引数の型や `const` が少し違うだけで別の関数になります。必ず `override` を付けます。

??? failure "継承を深くしすぎる"
    `GameObject → Character → Enemy → FlyingEnemy → FlyingFireEnemy` のように深くすると、「飛ぶけど火を吹かない敵」を作るのが難しくなります。機能を部品（コンポーネント）にして組み合わせる設計が主流です。

??? failure "コンストラクタの中で仮想関数を呼ぶ"
    基底クラスのコンストラクタの中では、派生クラスはまだできていないので、派生クラスの関数は呼ばれません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 上書きできる関数は `virtual`、上書きする側は `override`
    - [x] 基底クラスのデストラクタは `virtual`
    - [x] 派生クラスは unique_ptr で持つ（値で持つと切り落とされる）
    - [x] 継承は浅く。組み合わせはコンポーネントで

## 関連ページ

- [コンポーネント指向](../engine/component.md)
- [cppreference: virtual function specifier](https://en.cppreference.com/w/cpp/language/virtual)
