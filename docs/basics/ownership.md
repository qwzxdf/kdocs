---
title: 所有権（誰が消すのか）
tags:
  - 基礎
  - メモリ
---

# 所有権（誰が消すのか）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
</div>

**所有権**とは、<strong>「そのオブジェクトを最後に消す責任は誰にあるか」</strong>という考え方です。C++ にはガベージコレクション（自動でメモリを片付ける仕組み）が無いので、作ったものは誰かが必ず消す必要があります。消す人がいなければメモリリーク、2 人が消せば二重解放で落ちます。今の C++ では、**持ち主（所有者）を型で表す**ことで、この問題を起こりにくくしています。

!!! tip "ポイント"
    - **持ち主は 1 人**が基本。値で持つか、[`std::unique_ptr`](../stl/utilities/unique_ptr.md) で持つ。
    - 持ち主ではなく「使わせてもらうだけ」なら、参照 `T&` か生ポインタ `T*`。
    - 本当に持ち主が複数いるときだけ [`std::shared_ptr`](../stl/utilities/shared_ptr.md)。
    - `new` / `delete` を直接書かない。
    - 相手が先に消えるかもしれないなら、ポインタではなく ID / ハンドル / `weak_ptr` で覚える。

## 基本

### 型と意味の対応

| 書き方 | 持ち主？ | 意味 |
| --- | --- | --- |
| `Enemy enemy;`（値） | ○ | 自分の中に直接持つ。自分が消えると一緒に消える。**一番の基本** |
| `std::vector<Enemy> enemies;` | ○ | vector が全員の持ち主 |
| `std::unique_ptr<Enemy> enemy;` | ○（1 人） | ヒープに置いて持つ。ポリモーフィズムに使う |
| `std::shared_ptr<Texture> tex;` | ○（複数） | 最後の 1 人が消すときに消える |
| `Enemy& enemy` | × | 必ずある相手を使わせてもらう |
| `Enemy* enemy` | × | 無いかもしれない相手を指す（`nullptr` あり） |
| `std::weak_ptr<Enemy> enemy` | × | shared_ptr の相手を、消えたか確かめながら指す |
| `EnemyId id` | × | 番号で間接的に指す（相手が消えても安全に確かめられる） |

```cpp
#include <memory>
#include <print>
#include <string>
#include <vector>

struct Weapon {
  std::string name;
};

class Player {
 public:
  explicit Player(std::string name) : name_(std::move(name)) {}

  void Equip(std::unique_ptr<Weapon> w) { weapon_ = std::move(w); }  // 持ち主になる
  const Weapon* weapon() const { return weapon_.get(); }             // 見せるだけ

 private:
  std::string name_;                 // 値で持つ（持ち主）
  std::unique_ptr<Weapon> weapon_;   // unique_ptr で持つ（持ち主）
};

void ShowWeapon(const Player& p) {   // 使わせてもらうだけ（持ち主ではない）
  if (const Weapon* w = p.weapon()) {
    std::println("装備: {}", w->name);
  }
}

int main() {
  Player hero("Alice");
  hero.Equip(std::make_unique<Weapon>("聖剣"));
  ShowWeapon(hero);
}  // hero が消えると、name_ も weapon_ も自動で消える
```

```text title="実行結果"
装備: 聖剣
```

## 詳しく

### スコープと寿命（RAII）

C++ のオブジェクトは、**作られたスコープ（`{}` の中）を抜けると自動で消えます**（デストラクタが呼ばれる）。この仕組みを使って、「作ったら必ず片付ける」をコンパイラに保証させるのが RAII（Resource Acquisition Is Initialization）という考え方です。

```cpp
#include <print>

struct Scope {
  explicit Scope(const char* n) : name(n) { std::println("{} 開始", name); }
  ~Scope() { std::println("{} 終了", name); }
  const char* name;
};

int main() {
  Scope a("A");
  {
    Scope b("B");
  }  // ここで B が消える
  std::println("ブロックの外");
}  // ここで A が消える
```

```text title="実行結果"
A 開始
B 開始
B 終了
ブロックの外
A 終了
```

メモリだけでなく、ファイル、ロック、GPU のリソースも、デストラクタで解放するクラスにしておけば片付け忘れが起きません。

### 引数で「所有権」を表す

| 引数の型 | 呼ぶ側から見た意味 |
| --- | --- |
| `void F(const T& x)` | 読ませるだけ。持ち主は変わらない |
| `void F(T& x)` | 書き換えさせる。持ち主は変わらない |
| `void F(T* x)` | 使わせる（無いかもしれない）。持ち主は変わらない |
| `void F(std::unique_ptr<T> x)` | **持ち主を渡す**（呼ぶ側は `std::move` が必要） |
| `void F(std::shared_ptr<T> x)` | 持ち主の 1 人になる |

### 相手が消えるかもしれないとき

ゲームでは「敵 A が敵 B を狙っていたら、B が先に倒された」がよく起きます。生ポインタで覚えていると、消えたものを指してしまいます。

| 方法 | 特徴 |
| --- | --- |
| ID / ハンドルで覚えて、使うときに探す | 一番安全で、セーブもしやすい。ECS の基本 |
| `std::weak_ptr` | shared_ptr で管理しているなら使える |
| 消えるときに参照している側へ通知する | 実装が面倒で漏れやすい |

```cpp
#include <print>
#include <unordered_map>

struct Enemy {
  int hp;
};

int main() {
  std::unordered_map<int, Enemy> enemies = {{1, {30}}, {2, {50}}};
  int target_id = 2;  // ポインタではなく ID で覚える

  enemies.erase(2);  // 対象が倒された

  if (auto it = enemies.find(target_id); it != enemies.end()) {
    it->second.hp -= 10;
  } else {
    std::println("対象はもういない");
  }
}
```

```text title="実行結果"
対象はもういない
```

## ゲームでの例

| 持ち主 | 持たれるもの |
| --- | --- |
| ゲーム（アプリ全体） | 現在のシーン（`unique_ptr<Scene>`） |
| シーン | エンティティ・オブジェクトの一覧（`vector` / `unique_ptr`） |
| リソースマネージャ | テクスチャ・サウンド（他は ID か参照で借りる） |
| オブジェクト | 自分のコンポーネント（値で持つ） |

## よくあるミス

??? failure "誰が消すのか決まっていない"
    `Enemy* e = new Enemy();` を色々な場所に渡していくと、どこで `delete` するのか分からなくなります。最初に「持ち主」を決めて、その型（unique_ptr など）で持ちます。

??? failure "何でも shared_ptr にする"
    持ち主がはっきりしなくなり、消えるタイミングが読めなくなります。循環参照で永遠に消えないこともあります。

??? failure "消えたものを指し続ける"
    生ポインタや参照で覚えた相手が先に消えると、未定義動作になります。

## 理解度チェック

!!! question "Q1. 「UI がプレイヤーの HP を表示する」とき、UI はプレイヤーをどう持つべき？"
    <div class="spoiler" markdown>

    **答え:** 持ち主にはならないので、`const Player&` か `const Player*`、または ID で参照します。UI が `unique_ptr<Player>` を持つと、UI が消えたときにプレイヤーも消えてしまいます。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主は 1 人。値か unique_ptr で持つ
    - [x] 借りるだけなら `T&` / `T*`
    - [x] 先に消えるかもしれない相手は ID で覚える
    - [x] 片付けはデストラクタに任せる（RAII）

## 関連ページ

- [std::unique_ptr](../stl/utilities/unique_ptr.md)
- [std::shared_ptr](../stl/utilities/shared_ptr.md)
- [ポインタ](pointer.md)
