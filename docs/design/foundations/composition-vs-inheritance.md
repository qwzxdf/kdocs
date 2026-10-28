---
title: 継承と合成（コンポジション）
tags:
  - 設計
---

# 継承と合成（コンポジション）

オブジェクト指向を習うと、まず**継承**（`class Player : public Character`）を覚えます。でも、ゲームのコードで継承を使いすぎると、「`FlyingEnemy` と `ShootingEnemy` の両方の性質を持つ敵はどうする？」という問題で行き詰まります。そこで、「継承（is-a：〜は〜である）」より「合成（has-a：〜は〜を持っている）」を優先する、という原則があります。部品（機能）を持たせて組み合わせるほうが、変更に強く、組み合わせも自由だからです。

!!! tip "ポイント"
    - <strong>「A は B の一種」と言い切れるときだけ継承</strong>。「A は B の機能を使いたい」なら合成（メンバとして持つ）。
    - 継承は**関係が固い**。親が変わると子すべてが影響を受ける。合成は差し替えやすい。
    - 継承の深さは 2〜3 段まで。それ以上は、設計を見直すサイン。
    - 継承するのは、仮想関数でインターフェースを共有するとき（[インターフェース設計](interface-design.md)）が中心。
    - ゲームの「いろいろな機能を持つオブジェクト」は、コンポーネント（部品の合成）で作る（[コンポーネント指向](../../engine/component.md)、[ECS](../patterns/ecs.md)）。

!!! info "このページを読む前に"
    - [design/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](principles.md)（設計の基本原則）

## 悪い例：機能ごとに継承を重ねる

```cpp
class Enemy { /* 体力、位置 */ };
class FlyingEnemy : public Enemy { /* 飛ぶ */ };
class ShootingEnemy : public Enemy { /* 撃つ */ };
class FlyingShootingEnemy : public ??? { /* 飛んで、撃つ → どっちを継承する？ */ };
```

### 何が困るか

<div class="anim" data-type="graph" data-label="継承だけでは、両方の性質を持つ敵が作れない">
n e Enemy 1 0
n f FlyingEnemy 0 1
n s ShootingEnemy 2 1
l e f
l e s
---
n e Enemy 1 0
n f FlyingEnemy 0 1
n s ShootingEnemy 2 1
n fs FlyingShootingEnemy 1 2 gone
l e f
l e s
l f fs
l s fs - 多重継承は複雑
</div>

| 問題 | 説明 |
| --- | --- |
| **組み合わせが爆発する** | 飛ぶ・撃つ・毒・透明…が増えるたびに、組み合わせのクラスが増える |
| 親の変更が全員に影響する（壊れやすい基底クラス） | `Enemy` を直すと、すべての子が壊れる可能性がある |
| 途中で性質を変えられない | 「撃てなくなった」を表現するには、別のクラスに作り直すしかない |
| 使わない機能まで引き継ぐ | 親が持つ機能を子が全部持つ |

## 良い例：機能を部品にして、持たせる（合成）

```cpp
// 機能を小さな部品にする
class Flight {
 public:
  void Update(Transform& transform, float dt);  // 飛ぶ動き
};

class Shooter {
 public:
  void Update(Transform& transform, float dt);  // 撃つ動き
};

class Enemy {
 public:
  void Update(float dt) {
    if (flight_) {
      flight_->Update(transform_, dt);
    }
    if (shooter_) {
      shooter_->Update(transform_, dt);
    }
  }

  // 必要な部品だけを持たせる
  void AddFlight() { flight_ = std::make_unique<Flight>(); }
  void AddShooter() { shooter_ = std::make_unique<Shooter>(); }

 private:
  Transform transform_;
  std::unique_ptr<Flight> flight_;    // 持っているときだけ飛ぶ
  std::unique_ptr<Shooter> shooter_;  // 持っているときだけ撃つ
};
```

```cpp
Enemy flying_shooter;
flying_shooter.AddFlight();
flying_shooter.AddShooter();  // 飛んで撃つ敵。新しいクラスはいらない
```

<div class="anim" data-type="graph" data-label="継承と合成：機能の足し方">
n a 敵 0 0
n b 飛ぶ敵 1 0
n c 撃つ敵 1 1
n d 飛んで撃つ敵 2 0 gone
l a b
l a c
l b d gone 組み合わせの継承は作れない
# 継承：組み合わせごとにクラスが必要になる
---
n e 敵 0 0
n f 飛ぶ 1 0 new
n g 撃つ 1 1 new
n h 毒 1 2 new
l e f new
l e g new
l e h new
# 合成：敵に部品を足すだけ。新しいクラスは増えない
</div>

## 継承と合成の使い分け

| 状況 | 選ぶもの | 理由 |
| --- | --- | --- |
| 「Player は Character **である**」（本当にそう言える） | 継承（ただし浅く） | 仮想関数で、共通の呼び出し方ができる |
| 「Enemy は Health を持っている」 | 合成 | 体力は、部品として別のクラスにできる |
| 機能を再利用したいだけ | 合成 | 継承は再利用の道具ではない |
| 実行中に機能を変えたい（飛べなくなる） | 合成（部品を外す） | 継承は途中で変えられない |
| 同じ呼び出し方で、違う動きをさせたい | インターフェース（抽象クラス）+ 継承、または [ストラテジー](../patterns/strategy.md) | 多態（ポリモーフィズム） |
| 型ごとに速さが重要（毎フレーム何万回） | 継承の仮想関数を避け、[CRTP](../patterns/crtp-policy.md) や、型ごとの配列 | 仮想呼び出しのコスト |

## 継承の判断：リスコフの置換原則

「**親の代わりに子を渡しても、正しく動く**」ときだけ、継承してよい、という考え方です。

```cpp
class Bird {
 public:
  virtual void Fly() = 0;
};

class Penguin : public Bird {
 public:
  void Fly() override { /* 飛べない… 何を書く？ */ }
};
```

`Penguin` は `Bird` の一種ですが、`Fly()` できないので、`Bird` の代わりに使うと壊れます。このようなときは、継承の関係が間違っています。「飛べる」は `Flyable` という別のインターフェースか、部品（`Flight`）にします。

## 継承が向いているところ

| 向いている | 例 |
| --- | --- |
| **インターフェースを決める**（中身は持たない） | `IRenderer`、`IAudio`（[インターフェース設計](interface-design.md)） |
| 実行時に型を切り替える（多態） | `Scene` の種類（`TitleScene`、`GameScene`）。[シーン管理](../../engine/scene.md) |
| 多態で、まとめて扱う | `std::vector<std::unique_ptr<Shape>>` |

その場合も、基底クラスは「インターフェースだけ」（データを持たない）にすると、壊れにくくなります。

## ゲームでの使いどころ

| 場面 | 設計 |
| --- | --- |
| いろいろな敵 | 敵の基底クラスを増やさず、<strong>データ（JSON）と部品（コンポーネント）</strong> で作る |
| シーンの種類 | `Scene` インターフェース + 各シーンの継承（浅い） |
| 入力（キーボード、パッド） | `IInput` インターフェースで差し替える |
| 当たり判定の形 | `Shape` インターフェース（`Circle`、`Box`）。または `std::variant` |

## よくあるミス

??? failure "コードを再利用したくて継承する"
    `Player` が `Timer` の機能を使いたくて `Timer` を継承すると、「Player は Timer である」という意味になってしまいます。`Timer timer_;` をメンバに持ちます。

??? failure "継承が深くなる（5 段、6 段…）"
    親のどこで何をしているかが分からなくなります。<strong>浅く（2〜3 段）</strong>、できればインターフェースだけにします。

??? failure "子クラスで、親の関数を「何もしない」で上書きする"
    `Penguin::Fly()` のように、使わない機能を空にするのは、継承が間違っているサインです。機能を分けます。

??? failure "基底クラスのデストラクタが `virtual` でない"
    基底のポインタで `delete` すると、子のデストラクタが呼ばれず、リークします。多態で使う基底クラスは、デストラクタを `virtual` にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「A は B の一種」と言い切れるときだけ継承。機能の再利用は合成
    - [x] 継承は浅く（2〜3 段）、基底クラスは**インターフェースだけ**にする
    - [x] 機能は小さな部品にして、持たせて組み合わせる
    - [x] 実行中に機能を変えたいなら、合成（部品を足す・外す）
    - [x] ゲームのオブジェクトは、コンポーネントで作る

## 関連ページ

- [設計の基本原則](principles.md)
- [インターフェース設計](interface-design.md)
- [コンポーネント指向](../../engine/component.md)
- [ECS](../patterns/ecs.md)
- [ストラテジー](../patterns/strategy.md)
- [継承と仮想関数（基礎）](../../basics/virtual.md)
