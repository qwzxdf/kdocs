---
title: 設計の基本原則
tags:
  - 設計
---

# 設計の基本原則

プログラムが小さいうちは、どう書いても動きます。でもゲームは、敵の種類が増え、仕様が変わり、チームの人数が増えていくものです。そのときに「1 か所直したら別の所が壊れた」「どこを直せばいいか分からない」とならないようにするための考え方が**設計の原則**です。ここでは、ゲーム制作で特に効く 5 つを、悪い例と良い例で説明します。

!!! tip "ポイント"
    1. **1 つのクラス・関数は 1 つの役割だけ**（単一責任）
    2. **お互いに知っていることを減らす**（疎結合）
    3. **継承より組み合わせ**（合成）
    4. **同じことを 2 か所に書かない**（DRY）
    5. **今必要なものだけ作る**（YAGNI / KISS）

    原則はルールではなく「迷ったときの目安」。守るために複雑になるなら、守らなくていい。

## この考え方の全体像

| 原則 | ひとことで | 守らないと起きること |
| --- | --- | --- |
| 単一責任 | 変わる理由が 1 つだけになるように分ける | 1 つの修正があちこちに影響する |
| 疎結合 | 相手の中身を知らなくても使えるようにする | 1 つ変えると芋づる式に直す羽目になる |
| 継承より合成 | 機能を部品にして組み合わせる | 継承の木が複雑になり、組み合わせが作れない |
| DRY | 知識（ルール・数値）を 1 か所にまとめる | 直し忘れで不具合が出る |
| YAGNI / KISS | 今いらない仕組みを作らない。単純に書く | 使われない複雑な仕組みが残る |

## 1. 単一責任（Single Responsibility）

### 悪い例

```cpp
class Player {
 public:
  void Update() {
    // 入力を読む
    // 移動する
    // 当たり判定をする
    // HP を減らす
    // HP バーを描く
    // 効果音を鳴らす
    // セーブデータに書く
  }
};
```

### 何が困るか

- 「HP バーの見た目を変えたい」だけなのに、入力や移動と同じクラスを触ることになる
- Player が 2000 行になり、誰も全体を把握できない
- 敵にも HP バーを付けたいとき、使い回せない

### 良い例

```cpp
class PlayerInput { /* 入力 → 移動の意図 */ };
class Mover { /* 位置と速度 */ };
class Health { /* HP とダメージ */ };
class HealthBarView { /* HP の表示 */ };
```

役割ごとに分けると、「HP バーを変えるなら HealthBarView だけ」と、直す場所がはっきりします。[コンポーネント指向](../../engine/component.md)は、この考え方をゲームオブジェクトに当てはめたものです。

### 目安

- クラスの説明を「〜と〜をする」と「と」でつなぐ必要があるなら、分けられるかもしれない
- 関数が画面に収まらない（50 行を超える）なら、分けられるかもしれない

## 2. 疎結合（依存を減らす）

### 悪い例

```cpp
class Enemy {
 public:
  void Die() {
    game_->score_manager_->Add(100);         // スコアの中身を知っている
    game_->ui_->kill_counter_->Increment();  // UI の中身を知っている
    game_->audio_->Play("explode.wav");      // サウンドの中身を知っている
  }
};
```

### 何が困るか

- UI の作りを変えると、Enemy まで直す必要がある
- Enemy だけをテストできない（ゲーム全体が必要）
- 「倒したときに実績を解除したい」と思うたびに Enemy を触る

### 良い例

```cpp
class Enemy {
 public:
  explicit Enemy(EventBus& events) : events_(events) {}
  void Die() { events_.Publish(EnemyKilled{id_, score_}); }  // 起きたことを知らせるだけ

 private:
  EventBus& events_;
  int id_ = 0;
  int score_ = 100;
};
```

Enemy は「倒された」と知らせるだけで、誰が反応するかは知りません（[イベントシステム](../patterns/event.md)）。

### 依存を減らす方法

| 方法 | 例 |
| --- | --- |
| 必要なものだけ引数で渡す | `Update(const Input& input)`（ゲーム全体ではなく入力だけ） |
| イベントで知らせる | [イベントシステム](../patterns/event.md) |
| インターフェース（抽象クラス）越しに使う | [依存性の注入](../patterns/dependency-injection.md) |
| 相手を ID で指す | [ハンドル](../../engine/handle.md) |

## 3. 継承より合成（Composition over Inheritance）

### 悪い例

<div class="anim" data-type="graph" data-label="継承で機能を足すと、同じ処理が複数の場所に増える">
n e Enemy 0 1
n w WalkingEnemy 1 0
n f FlyingEnemy 1 2
n ws WalkingShootingEnemy 2 0
n fs FlyingShootingEnemy 2 2
l e w
l e f
l w ws
l f fs
---
n e Enemy 0 1
n w WalkingEnemy 1 0
n f FlyingEnemy 1 2
n ws WalkingShootingEnemy 2 0 hit
n fs FlyingShootingEnemy 2 2 hit
l e w
l e f
l w ws
l f fs
</div>

### 良い例

```cpp
struct Enemy {
  std::unique_ptr<MoveBehavior> move;     // 歩く / 飛ぶ
  std::unique_ptr<AttackBehavior> attack;  // 撃つ / 噛む / 何もしない
};
```

移動と攻撃を別々の部品にすると、「飛んで噛む敵」も新しいクラスを作らずに組み合わせで作れます（[ストラテジー](../patterns/strategy.md)、[コンポーネント指向](../../engine/component.md)）。

### 継承を使っていいとき

- 「〜は〜の一種」が本当に成り立ち、深さが 1〜2 段で済む（`Scene` → `TitleScene`）
- 同じ呼び方（インターフェース）で、違う中身を差し替えたい

## 4. DRY（Don't Repeat Yourself）

### 悪い例

```cpp
// player.cpp
if (hp > 100) hp = 100;
// ui.cpp
float ratio = hp / 100.0f;
// save.cpp
if (loaded_hp > 100) { /* 壊れたデータ */ }
```

最大 HP を 150 に変えたとき、3 か所全部を直す必要があり、1 つ忘れると不具合になります。

### 良い例

```cpp
constexpr int kMaxHp = 100;  // ルールは 1 か所に
```

さらに、こういった数値は [データ駆動](../patterns/factory.md) で外部ファイルに出すと、プログラマー以外も調整できます。

!!! note "DRY のやりすぎに注意"
    見た目が似ているだけのコード（たまたま同じ形の計算）を無理にまとめると、片方だけ変えたいときに困ります。まとめるのは「**同じ知識・同じルール**」だけにします。

## 5. YAGNI / KISS

- **YAGNI**（You Aren't Gonna Need It）: 「いつか必要になるかも」で仕組みを作らない
- **KISS**（Keep It Simple, Stupid）: 一番単純な書き方を選ぶ

### 悪い例

```cpp
// 敵は 3 種類しかいないのに、プラグインで敵を追加できる汎用システムを作る
template <class T, class Allocator, class Policy, class... Mixins>
class GenericEntityFactoryRegistry { /* 500 行 */ };
```

### 良い例

```cpp
enum class EnemyType { kSlime, kGoblin, kDragon };
std::unique_ptr<Enemy> CreateEnemy(EnemyType type);  // 必要になったら広げる
```

学生のゲーム制作は期間が短いので、**まず動くものを単純に作り、困ったところだけ設計し直す**のが一番速いです。

## ゲームでの例

| よくある状況 | 当てはまる原則 |
| --- | --- |
| Player クラスが巨大 | 単一責任 → コンポーネントに分ける |
| 敵のコードが UI を直接触っている | 疎結合 → イベントで知らせる |
| 敵の種類ごとにクラスが増え続ける | 合成 → 振る舞いを部品にする |
| 同じ数値があちこちに書いてある | DRY → 定数・データファイルにまとめる |
| 使われない汎用システムがある | YAGNI → 消す |

## よくある失敗

??? failure "原則を守るために細かく分けすぎる"
    3 行のクラスが 50 個あると、かえって全体が追えなくなります。分けるのは「変わる理由が違うもの」です。

??? failure "最初から完璧な設計を目指す"
    仕様が決まっていないうちに作り込むと、仕様変更で全部無駄になります。動かしながら、困ったところを直します（リファクタリング）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 つのクラスは 1 つの役割
    - [x] 相手の中身を知らずに済むようにする
    - [x] 継承より組み合わせ
    - [x] 同じルールは 1 か所に
    - [x] 今いらないものは作らない

## 関連ページ

- [クラス設計](class-design.md)
- [コンポーネント指向](../../engine/component.md)
- [Game Programming Patterns](https://gameprogrammingpatterns.com/)
