---
title: ストラテジー（振る舞いの差し替え）
tags:
  - 設計
---

# ストラテジー（振る舞いの差し替え）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**ストラテジーパターン**は、<strong>「やり方」（アルゴリズム）を部品として取り替えられるようにする</strong>設計です。敵の移動方法（まっすぐ・追いかける・ジグザグ）、ダメージ計算の式、カメラの追い方などを、`if` や `switch` で分けるのではなく、差し替えられる部品にしておきます。C++ では、仮想関数、`std::function`、テンプレートの 3 通りで書けます。

!!! tip "ポイント"
    - 「同じ役割で、やり方だけが違う」ものが増えてきたら使う。
    - 実行中に切り替えたいなら **`std::function`<strong>（一番手軽）か </strong>仮想関数**。
    - コンパイル時に決まっていて速さが大事なら **テンプレート**。
    - やり方が 2〜3 個しかなく増えないなら、`switch` のままでいい。

## 悪い例：switch が増え続ける

```cpp
void Enemy::Update() {
  switch (move_type_) {
    case MoveType::kStraight: /* ... */ break;
    case MoveType::kChase: /* ... */ break;
    case MoveType::kZigzag: /* ... */ break;
    // 新しい動きを足すたびに、ここと Enemy のメンバが増えていく
  }
}
```

<div class="anim" data-type="graph" data-label="ストラテジー：動き方を差し替える">
n enemy 敵 0 1
n patrol 巡回 2 0 hit
n chase 追跡 2 1 dim
n flee 逃走 2 2 dim
l enemy patrol hit 今の行動
# 最初は「巡回」の行動を持っている
---
n enemy 敵 0 1
n patrol 巡回 2 0 dim
n chase 追跡 2 1 hit
n flee 逃走 2 2 dim
l enemy chase hit 差し替え
# プレイヤーを見つけたので、「追跡」に差し替える（敵のコードは変わらない）
---
n enemy 敵 0 1
n patrol 巡回 2 0 dim
n chase 追跡 2 1 dim
n flee 逃走 2 2 hit
l enemy flee hit 差し替え
# 体力が減ったので、「逃走」に差し替える
</div>

## 良い例 1：std::function で差し替える

```cpp
#include <cmath>
#include <functional>
#include <print>
#include <utility>

struct Vec2 {
  float x;
  float y;
};

using MoveStrategy = std::function<Vec2(Vec2 pos, float time)>;

class Enemy {
 public:
  explicit Enemy(MoveStrategy move) : move_(std::move(move)) {}
  void Update(float time) { pos_ = move_(pos_, time); }
  void set_move(MoveStrategy move) { move_ = std::move(move); }  // 途中で切り替えられる
  Vec2 pos() const { return pos_; }

 private:
  MoveStrategy move_;
  Vec2 pos_{0.0f, 0.0f};
};

MoveStrategy Straight(float speed) {
  return [speed](Vec2 p, float) { return Vec2{p.x + speed, p.y}; };
}

MoveStrategy Zigzag(float speed) {
  return [speed](Vec2 p, float t) { return Vec2{p.x + speed, std::sin(t * 3.14159f)}; };
}

int main() {
  Enemy enemy(Straight(1.0f));
  enemy.Update(0.0f);
  enemy.Update(0.5f);
  enemy.set_move(Zigzag(2.0f));  // 怒ったら動きを変える
  enemy.Update(0.5f);
  std::println("({}, {:.1f})", enemy.pos().x, enemy.pos().y);
}
```

```text title="実行結果"
(4, 1.0)
```

## 良い例 2：仮想関数で差し替える

やり方ごとにデータ（状態）を持たせたいときは、クラスにします。

```cpp
#include <memory>
#include <print>

class DamageFormula {
 public:
  virtual ~DamageFormula() = default;
  virtual int Calculate(int attack, int defense) const = 0;
};

class Subtract : public DamageFormula {
 public:
  int Calculate(int attack, int defense) const override {
    return attack > defense ? attack - defense : 1;
  }
};

class Ratio : public DamageFormula {
 public:
  int Calculate(int attack, int defense) const override {
    return attack * 100 / (100 + defense);
  }
};

int main() {
  std::unique_ptr<DamageFormula> formula = std::make_unique<Subtract>();
  std::println("引き算式: {}", formula->Calculate(50, 30));
  formula = std::make_unique<Ratio>();  // バランス調整で式を変える
  std::println("割合式: {}", formula->Calculate(50, 30));
}
```

```text title="実行結果"
引き算式: 20
割合式: 38
```

## 良い例 3：テンプレートで差し替える

コンパイル時に決まっていてよいなら、テンプレート引数で渡します。仮想関数の呼び出しコストがなく、インライン化もされます。

```cpp
#include <print>

struct Linear {
  static float Apply(float t) { return t; }
};
struct EaseIn {
  static float Apply(float t) { return t * t; }
};

template <class Easing>
float Interpolate(float from, float to, float t) {
  return from + (to - from) * Easing::Apply(t);
}

int main() {
  std::println("{} {}", Interpolate<Linear>(0.0f, 100.0f, 0.5f),
               Interpolate<EaseIn>(0.0f, 100.0f, 0.5f));
}
```

```text title="実行結果"
50 25
```

## 3 つの方法の比較

| 方法 | 実行中に切り替え | 状態を持てる | 速さ | 書きやすさ |
| --- | --- | --- | --- | --- |
| `std::function` + ラムダ | ○ | ○（キャプチャ） | ○ | ◎ |
| 仮想関数（継承） | ○ | ◎（メンバ） | ○ | ○ |
| テンプレート | × | ○ | ◎ | ○ |
| `switch` | ○ | △ | ◎ | ◎（少ないうちは） |

## ゲームでの例

| 差し替えるもの | 例 |
| --- | --- |
| 敵の移動 | まっすぐ、追いかける、ジグザグ、待ち伏せ |
| ダメージ計算 | 引き算式、割合式、属性つき |
| カメラ | 固定、追従、なめらかに追従 |
| イージング（補間） | Linear、EaseIn、EaseOut、Bounce |
| AI の難易度 | 弱い（ランダム）、普通、強い（先読み） |

## よくある失敗

??? failure "2 種類しかないのにストラテジーにする"
    `if (is_boss)` で済むものをクラス階層にすると、読むファイルが増えるだけです。増えてきたら切り替えます。

??? failure "ストラテジーの中から持ち主を勝手に書き換える"
    差し替える部品が持ち主（Enemy）の内部を何でも触ると、部品を替えたときの影響が読めなくなります。必要な値だけを引数で受け取り、結果を返す形にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] やり方を部品にして差し替える
    - [x] 手軽なのは std::function、状態が多いなら仮想関数、速さならテンプレート
    - [x] 少ないうちは switch で十分

## 関連ページ

- [std::function](../../stl/utilities/function.md)
- [継承と仮想関数](../../basics/virtual.md)
- [ファクトリとデータ駆動](factory.md)
