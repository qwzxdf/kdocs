---
title: クラス設計
tags:
  - 設計
---

# クラス設計

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

クラスは「データ」と「そのデータを正しく扱う関数」をひとまとめにしたものです。良いクラスは、**外から間違った使い方ができない**ように作られています。たとえば HP が最大値を超えたりマイナスになったりしないように、HP を直接書き換えさせず、`Damage()` や `Heal()` を通して変えさせます。このページでは、ゲームのクラスを作るときに押さえておきたいポイントをまとめます。

!!! tip "ポイント"
    - **メンバ変数は private** にして、意味のある操作（`Damage`、`Heal`）だけを public にする。
    - **コンストラクタが終わった時点で、使える状態**にする（`Init()` を後で呼ばせない）。
    - 書き換えないメンバ関数には **`const`**、引数 1 つのコンストラクタには **`explicit`**。
    - コピー・ムーブ・デストラクタは**書かない**のが基本（Rule of Zero）。リソースを直接持つときだけ考える。
    - ただのデータの入れ物なら `struct` にしてメンバを公開していい。

!!! info "このページを読む前に"
    [参照](../basics/reference.md)、[ムーブ](../basics/move.md)、[所有権](../basics/ownership.md) が分かると読みやすいです。

## 1. カプセル化：壊れた状態を作らせない

### 悪い例

```cpp
struct Player {
  int hp;
  int max_hp;
};

player.hp -= 999;   // マイナスになる
player.hp = 50000;  // 最大値を超える
```

### 良い例

```cpp
#include <algorithm>
#include <print>

class Player {
 public:
  explicit Player(int max_hp) : max_hp_(max_hp), hp_(max_hp) {}

  void Damage(int amount) { hp_ = std::max(hp_ - amount, 0); }
  void Heal(int amount) { hp_ = std::min(hp_ + amount, max_hp_); }

  int hp() const { return hp_; }
  bool IsDead() const { return hp_ == 0; }

 private:
  int max_hp_;
  int hp_;  // 0 <= hp_ <= max_hp_ が常に成り立つ（不変条件）
};

int main() {
  Player p(100);
  p.Damage(999);
  std::println("{} {}", p.hp(), p.IsDead());
  p.Heal(50000);
  std::println("{}", p.hp());
}
```

```text title="実行結果"
0 true
100
```

「HP は 0 以上、最大値以下」という**不変条件**を、クラスの中だけで守れるようになります。どこから使われても HP が壊れません。

### class と struct の使い分け

| 使い方 | 書き方 |
| --- | --- |
| 守るべきルール（不変条件）がある | `class`（メンバは private） |
| ただのデータの入れ物（どんな値でも OK） | `struct`（メンバは public） |

```cpp
struct Vec2 {  // どんな x, y でも正しい → struct で公開
  float x = 0.0f;
  float y = 0.0f;
};
```

ゲッター・セッターを全部のメンバに付けるだけなら、カプセル化の意味はありません（`set_hp` で何でも入れられるなら、public と同じ）。

## 2. コンストラクタで完成させる

### 悪い例

```cpp
Enemy enemy;
enemy.Init(texture, 100);  // 呼び忘れると壊れた敵が動く
```

### 良い例

```cpp
class Enemy {
 public:
  Enemy(const Texture& texture, int hp) : texture_(&texture), hp_(hp) {}
  // コンストラクタが終わった時点で、必ず使える状態
 private:
  const Texture* texture_;
  int hp_;
};
```

### メンバ初期化のルール

```cpp
class Timer {
 public:
  explicit Timer(float duration) : duration_(duration) {}  // 初期化リストで初期化

 private:
  float duration_;
  float elapsed_ = 0.0f;  // デフォルト値はここに書ける
  bool running_ = false;
};
```

- メンバは**宣言した順番**で初期化されます（初期化リストの順番ではない）
- 初期値の無いメンバ（`int x;`）は中身がゴミになるので、必ず初期値を書きます

## 3. const と explicit

### const メンバ関数

```cpp
int hp() const { return hp_; }   // 読むだけ → const
void Damage(int amount);          // 書き換える → const なし
```

- `const Player&` で受け取った関数からは、const メンバ関数しか呼べません
- 「この関数は状態を変えない」ことが一目で分かります

### explicit

```cpp
#include <print>

class Meter {
 public:
  explicit Meter(float value) : value_(value) {}
  float value() const { return value_; }

 private:
  float value_;
};

void Print(Meter m) { std::println("{} m", m.value()); }

int main() {
  Print(Meter(3.0f));  // OK
  // Print(3.0f);      // explicit なのでエラー（うっかり変換を防ぐ）
}
```

```text title="実行結果"
3 m
```

引数 1 つのコンストラクタに `explicit` を付けないと、`float` が勝手に `Meter` に変換されて、単位の間違いなどに気づけなくなります。

## 4. Rule of Zero / Rule of Five

| ルール | 中身 |
| --- | --- |
| **Rule of Zero** | メンバが標準の型（string、vector、unique_ptr）なら、コピー・ムーブ・デストラクタを**何も書かない**。コンパイラが正しく作ってくれる |
| **Rule of Five** | どれか 1 つ（デストラクタなど）を自分で書いたら、残り 4 つ（コピーコンストラクタ、コピー代入、ムーブコンストラクタ、ムーブ代入）も考える |

```cpp
// Rule of Zero：何も書かなくていい
class Level {
  std::string name_;
  std::vector<int> tiles_;
  std::unique_ptr<Texture> background_;
};
```

```cpp
// リソースを直接持つクラス（C のライブラリのハンドルなど）
class GpuBuffer {
 public:
  explicit GpuBuffer(std::size_t size);
  ~GpuBuffer();                                     // 解放する

  GpuBuffer(const GpuBuffer&) = delete;             // コピー禁止
  GpuBuffer& operator=(const GpuBuffer&) = delete;

  GpuBuffer(GpuBuffer&& other) noexcept;            // ムーブは許す
  GpuBuffer& operator=(GpuBuffer&& other) noexcept;

 private:
  unsigned int handle_ = 0;
};
```

!!! note "実際は"
    生のハンドルを持つクラスを書くより、[Deleter 付きの unique_ptr](../stl/utilities/unique_ptr.md#フラグオプション) に包むほうが簡単で安全です。そうすれば Rule of Zero に戻れます。

## 5. その他のポイント

| ポイント | 理由 |
| --- | --- |
| public → protected → private の順に書く | 使う人が知りたいもの（public）が先に見える（Google Style） |
| メンバ変数の名前の最後に `_` を付ける | ローカル変数・引数と区別できる（Google Style） |
| 仮想関数を持つ基底クラスのデストラクタは `virtual` | [継承と仮想関数](../basics/virtual.md) |
| 継承させないクラスには `final` | 意図がはっきりし、最適化もされやすい |
| 1 つのクラスが大きくなったら分ける | [単一責任](principles.md#1-単一責任single-responsibility) |
| 比較が必要なら `operator==` / `<=>` を `= default` | メンバごとの比較を自動で作れる |

```cpp
#include <compare>
#include <print>

struct Version {
  int major = 0;
  int minor = 0;
  auto operator<=>(const Version&) const = default;  // ==, <, > などが全部使える
};

int main() {
  std::println("{} {}", Version{1, 2} < Version{1, 10}, Version{2, 0} == Version{2, 0});
}
```

```text title="実行結果"
true true
```

## ゲームでの例

| クラス | 守るルール（不変条件） |
| --- | --- |
| `Health` | 0 ≦ HP ≦ 最大 HP |
| `Inventory` | アイテム数は容量以下、同じ枠に重ならない |
| `Timer` | 経過時間は 0 以上 |
| `Camera` | マップの外を映さない |

## よくある失敗

??? failure "全部のメンバにゲッター・セッターを付ける"
    `set_hp(int)` で何でも入れられるなら、private にした意味がありません。「何をしたいか」（`Damage`、`Heal`、`Revive`）を関数にします。

??? failure "Init() を別に呼ばせる"
    呼び忘れ、二重呼び出しのバグの元です。コンストラクタで完成させ、失敗しうるなら [ファクトリ関数](factory.md) で `std::expected` や `std::optional` を返します。

??? failure "初期化リストの順番を宣言と違う順にする"
    宣言順に初期化されるので、`hp_(max_hp_)` のように後で宣言されたメンバを使うとゴミが入ります（警告 `-Wreorder` が出ます）。

## 理解度チェック

!!! question "Q1. このクラスの問題は？"
    ```cpp
    class Timer {
     public:
      Timer(float d) : duration(d) {}
      float duration;
      float elapsed;
    };
    ```

    <div class="spoiler" markdown>

    **答え:** ① `explicit` が無いので `float` から勝手に変換される。② `elapsed` が初期化されていない。③ メンバが public で、`elapsed` をマイナスにされても防げない。④ メンバ名に `_` が無く、Google Style に合っていない。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] メンバは private、意味のある操作だけ public
    - [x] コンストラクタで完成させる
    - [x] 読むだけの関数は const、引数 1 つのコンストラクタは explicit
    - [x] コピー・ムーブ・デストラクタは書かない（Rule of Zero）

## 関連ページ

- [設計の基本原則](principles.md)
- [ムーブ](../basics/move.md)
- [Google C++ Style Guide: Classes](https://google.github.io/styleguide/cppguide.html#Classes)
