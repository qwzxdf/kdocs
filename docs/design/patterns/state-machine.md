---
title: ステートマシン
tags:
  - ゲームエンジン
---

# ステートマシン

プレイヤーの「ジャンプ中」を表すのに、最初は `bool is_jumping;` を 1 つ置くと思います。そこへ攻撃が入って `is_attacking` が増え、やられ判定で `is_damaged` が増え、気づくと `if (is_jumping && !is_attacking && !is_damaged)` のような条件がコードじゅうに散らばります。しかも、フラグが 3 つあれば組み合わせは 8 通りあって、「ジャンプ中なのに攻撃中でやられ中」のような、ゲーム上ありえない状態もコードの上では作れてしまいます。

そこで、「今どの状態か」を変数 1 つで持ち、「どの条件でどの状態へ移るか」を最初に決めておきます。これが**ステートマシン**（状態機械）です。変数が 1 つなので、ありえない組み合わせは最初から作れません。プレイヤーなら立ち・歩き・ジャンプ・攻撃、敵の AI なら待機・巡回・追跡・攻撃、というように、ゲームには状態ごとに動きが変わるものがたくさんあるので、よく使います。

作り方は、状態の数と中身の重さで 3 つに分かれます。状態が少ないうちは `enum class` と `switch` で十分で、迷ったらこれです。状態ごとに持ちたいデータが違ってきたら [`std::variant`](../../stl/utilities/variant.md)、状態ごとの処理が大きくなったら、状態をクラスにします（State パターン）。

!!! info "このページを読む前に"
    後半の State パターンは [継承と仮想関数](../../basics/virtual.md)、variant の方式は [`std::variant`](../../stl/utilities/variant.md) を使います。分からなければ、先にそちらを読んでください。

## 基本

### enum class + switch

まずは、立ち・走り・ジャンプの 3 状態を `switch` で書きます。

```cpp
#include <print>

enum class PlayerState { kIdle, kRunning, kJumping };

struct Input {
  bool move;
  bool jump;
};

class Player {
 public:
  void Update(const Input& input) {
    switch (state_) {
      case PlayerState::kIdle:
        if (input.jump) {
          ChangeState(PlayerState::kJumping);
        } else if (input.move) {
          ChangeState(PlayerState::kRunning);
        }
        break;
      case PlayerState::kRunning:
        if (input.jump) {
          ChangeState(PlayerState::kJumping);
        } else if (!input.move) {
          ChangeState(PlayerState::kIdle);
        }
        break;
      case PlayerState::kJumping:
        if (--air_frames_ <= 0) {  // 着地した
          ChangeState(PlayerState::kIdle);
        }
        break;
    }
  }

 private:
  void ChangeState(PlayerState next) {
    state_ = next;
    if (next == PlayerState::kJumping) {
      air_frames_ = 2;  // 入るときの処理（Enter）
    }
    std::println("→ {}", Name(next));
  }

  static const char* Name(PlayerState s) {
    switch (s) {
      case PlayerState::kIdle:
        return "立ち";
      case PlayerState::kRunning:
        return "走り";
      case PlayerState::kJumping:
        return "ジャンプ";
    }
    return "";
  }

  PlayerState state_ = PlayerState::kIdle;
  int air_frames_ = 0;
};

int main() {
  Player player;
  for (Input in : {Input{true, false}, Input{true, true}, Input{false, false},
                   Input{false, false}, Input{false, false}}) {
    player.Update(in);
  }
}
```

```text title="実行結果"
→ 走り
→ ジャンプ
→ 立ち
```

`ChangeState` を 1 か所に集めているのがコツです。状態が変わる瞬間に必ずここを通るので、入るときの処理（Enter）をここに書けます。ジャンプの残りフレームを決めているのがその例で、アニメーションやエフェクトの開始もここに置きます。

### 遷移の表

コードを書く前に、「今の状態」「条件」「次の状態」を表にしておくと楽です。上のコードなら、次の 4 行です。

| 今の状態 | 条件 | 次の状態 |
| --- | --- | --- |
| 立ち | 移動入力 | 走り |
| 立ち / 走り | ジャンプ入力 | ジャンプ |
| 走り | 移動入力なし | 立ち |
| ジャンプ | 着地 | 立ち |

表にすると、「走りながら攻撃したら？」「ジャンプ中にやられたら？」のような抜けが、コードを書く前に見つかります。図にするのも同じ効果があります。

<svg class="fig flow" viewBox="0 0 418 256" role="img" aria-label="ステートマシン：今の状態と、遷移"><defs><marker id="fl79738" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ステートマシン：今の状態と、遷移</text><line x1="107.0" y1="124.0" x2="165.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl79738)"/><text x="136.0" y="118.0" text-anchor="middle" style="font-size:12px">移動入力</text><line x1="247.0" y1="124.0" x2="305.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl79738)"/><text x="276.0" y="118.0" text-anchor="middle" style="font-size:12px">ジャンプ</text><path d="M349.0,102.0 Q207.5,50.0 66.0,102.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl79738)"/><text x="207.5" y="64.0" text-anchor="middle" style="font-size:12px">着地</text><line x1="104.3" y1="147.0" x2="167.7" y2="185.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl79738)"/><text x="136.0" y="160.0" text-anchor="middle" style="font-size:12px">攻撃</text><line x1="167.7" y1="185.0" x2="104.3" y2="147.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl79738)"/><rect x="28.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">待機</text><rect x="168.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">走る</text><rect x="308.0" y="104.0" width="82" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="349.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ジャンプ</text><rect x="168.0" y="188.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">攻撃</text></svg>

## 詳しく

### 状態をクラスにする（State パターン）

敵 AI のように、状態ごとの処理が長くなってくると、`switch` の中が肥大化します。そうなったら、状態を 1 つずつクラスにして、処理をそれぞれの中に閉じ込めます。`Update` が「次の状態」を返す作りにしてあります（そのままなら `nullptr`）。

```cpp
#include <memory>
#include <print>
#include <utility>

class Enemy;

class EnemyState {
 public:
  virtual ~EnemyState() = default;
  virtual void Enter(Enemy&) {}
  virtual std::unique_ptr<EnemyState> Update(Enemy& enemy) = 0;  // 次の状態を返す（そのままなら nullptr）
};

class Enemy {
 public:
  explicit Enemy(std::unique_ptr<EnemyState> initial) : state_(std::move(initial)) {
    state_->Enter(*this);
  }
  void Update() {
    if (auto next = state_->Update(*this)) {
      state_ = std::move(next);
      state_->Enter(*this);
    }
  }
  float distance_to_player = 10.0f;

 private:
  std::unique_ptr<EnemyState> state_;
};

class Chase : public EnemyState {
 public:
  void Enter(Enemy&) override { std::println("追いかける"); }
  std::unique_ptr<EnemyState> Update(Enemy& e) override {
    e.distance_to_player -= 4.0f;
    return nullptr;
  }
};

class Patrol : public EnemyState {
 public:
  void Enter(Enemy&) override { std::println("巡回する"); }
  std::unique_ptr<EnemyState> Update(Enemy& e) override {
    if (e.distance_to_player < 5.0f) {
      return std::make_unique<Chase>();
    }
    e.distance_to_player -= 3.0f;  // プレイヤーが近づいてくるとする
    return nullptr;
  }
};

int main() {
  Enemy enemy(std::make_unique<Patrol>());
  for (int i = 0; i < 3; ++i) {
    enemy.Update();
  }
  std::println("距離 {}", enemy.distance_to_player);
}
```

```text title="実行結果"
巡回する
追いかける
距離 4
```

### variant で持つ

ジャンプなら残り時間、攻撃ならコンボ数、というように、状態ごとに持ちたいデータが違うことがあります。`enum` だと全状態ぶんのメンバを 1 つの構造体に並べることになり、使わない値が残ってしまいます。`std::variant` なら、今の状態に必要なデータだけを持てて、ヒープも使いません。

```cpp
#include <print>
#include <variant>

struct Idle {};
struct Jumping {
  int frames_left;
};
struct Attacking {
  int combo;
};

using State = std::variant<Idle, Jumping, Attacking>;

template <class... Fs>
struct Overloaded : Fs... {
  using Fs::operator()...;
};

State Update(const State& state, bool attack) {
  return std::visit(
      Overloaded{
          [&](const Idle&) -> State {
            return attack ? State{Attacking{1}} : State{Jumping{2}};
          },
          [](const Jumping& j) -> State {
            return j.frames_left > 1 ? State{Jumping{j.frames_left - 1}} : State{Idle{}};
          },
          [&](const Attacking& a) -> State {
            return attack ? State{Attacking{a.combo + 1}} : State{Idle{}};
          },
      },
      state);
}

int main() {
  State s = Idle{};
  for (bool attack : {true, true, true, false}) {
    s = Update(s, attack);
    if (auto* a = std::get_if<Attacking>(&s)) {
      std::println("{} コンボ", a->combo);
    }
  }
  std::println("最後は Idle？ {}", std::holds_alternative<Idle>(s));
}
```

```text title="実行結果"
1 コンボ
2 コンボ
3 コンボ
最後は Idle？ true
```

### どれを選ぶか

迷ったら `enum class` + `switch` から始めます。状態が 5 個くらいまでなら、これが一番読みやすいです。`std::variant` + `visit` は、状態ごとにデータが違うときに向いていて、状態を足し忘れるとコンパイラが教えてくれます。State パターンは、状態ごとの処理が大きいときや、状態をあとから足したいときに選びます。

状態が増えすぎたときの手もあります。「地上（立ち・歩き・走り）」「空中（ジャンプ・落下）」のように、状態をグループにまとめるのが階層型ステートマシンです。それでも遷移が増えすぎる複雑な AI は、ステートマシンをやめて、ビヘイビアツリーにします。

## ゲームでの例

プレイヤーの立ち・歩き・ジャンプ・攻撃・被ダメージ・死亡や、敵 AI の待機・巡回・追跡・攻撃・逃走は、すぐ思いつくと思います。ほかにも、ゲーム全体のタイトル・プレイ中・ポーズ・ゲームオーバー（[シーン管理](../../engine/scene.md)）、メニューの閉じている・開く途中・開いている・閉じる途中、ドアの開閉など、「途中」を含む動きは、たいていステートマシンで書けます。「開く途中」を状態にしておくと、開き終わる前にもう一度押されたときの動きも決められます。

<!-- fig:state-transition-walk:begin -->

<svg class="fig illust motion" data-fig="state-transition-walk" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-state-transition-walk" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ステートマシン: 入力があったときだけ、決められた先へ移る</text>
<line x1="252.0" y1="159.0" x2="504.0" y2="159.0" stroke="#cbd5e1" stroke-width="2.5" marker-end="url(#arr-state-transition-walk)" opacity="1"/>
<line x1="551.0" y1="202.0" x2="551.0" y2="244.0" stroke="#cbd5e1" stroke-width="2.5" marker-end="url(#arr-state-transition-walk)" opacity="1"/>
<line x1="515.4615384615385" y1="271.6923076923077" x2="255.15384615384613" y2="163.23076923076923" stroke="#cbd5e1" stroke-width="2.5" marker-end="url(#arr-state-transition-walk)" opacity="1"/>
<line x1="191.0" y1="202.0" x2="191.0" y2="244.0" stroke="#cbd5e1" stroke-width="2.5" marker-end="url(#arr-state-transition-walk)" opacity="1"/>
<line x1="209.0" y1="248.0" x2="209.0" y2="206.0" stroke="#cbd5e1" stroke-width="2.5" marker-end="url(#arr-state-transition-walk)" opacity="1"/>
<line x1="508.0" y1="141.0" x2="256.0" y2="141.0" stroke="#cbd5e1" stroke-width="2.5" marker-end="url(#arr-state-transition-walk)" opacity="1"/>
<circle cx="200" cy="150" r="46" fill="#ffffff" stroke="#94a3b8" stroke-width="3"/>
<text x="200" y="155" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">待機</text>
<circle cx="560" cy="150" r="46" fill="#ffffff" stroke="#94a3b8" stroke-width="3"/>
<text x="560" y="155" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">走る</text>
<circle cx="560" cy="300" r="46" fill="#ffffff" stroke="#94a3b8" stroke-width="3"/>
<text x="560" y="305" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">ジャンプ</text>
<circle cx="200" cy="300" r="46" fill="#ffffff" stroke="#94a3b8" stroke-width="3"/>
<text x="200" y="305" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">攻撃</text>
<line x1="252.0" y1="159.0" x2="504.0" y2="159.0" stroke="#e5484d" stroke-width="4" marker-end="url(#arr-state-transition-walk)" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;0.2160;0.2162;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="560" cy="150" r="46" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0971;0.0973;0.2592;0.2595;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="551.0" y1="202.0" x2="551.0" y2="244.0" stroke="#e5484d" stroke-width="4" marker-end="url(#arr-state-transition-walk)" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2160;0.2162;0.3782;0.3784;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="560" cy="300" r="46" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2592;0.2595;0.4214;0.4216;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="515.4615384615385" y1="271.6923076923077" x2="255.15384615384613" y2="163.23076923076923" stroke="#e5484d" stroke-width="4" marker-end="url(#arr-state-transition-walk)" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3782;0.3784;0.5403;0.5405;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="200" cy="150" r="46" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4214;0.4216;0.5836;0.5838;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="191.0" y1="202.0" x2="191.0" y2="244.0" stroke="#e5484d" stroke-width="4" marker-end="url(#arr-state-transition-walk)" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5403;0.5405;0.7025;0.7027;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="200" cy="300" r="46" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5836;0.5838;0.7457;0.7459;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="209.0" y1="248.0" x2="209.0" y2="206.0" stroke="#e5484d" stroke-width="4" marker-end="url(#arr-state-transition-walk)" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7025;0.7027;0.8646;0.8649;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="200" cy="150" r="46" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7457;0.7459;1.0000" values="0;0;1;1"/></circle>
<circle cx="200" cy="150" r="46" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0003;0.0005;0.0971;0.0973;1.0000" values="0;0;1;1;0;0"/></circle>
<text x="200" y="155" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">待機</text>
<text x="560" y="155" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">走る</text>
<text x="560" y="305" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">ジャンプ</text>
<text x="200" y="305" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">攻撃</text>
<text x="390" y="405" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">最初は「待機」<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;1.0000" values="1;1;0;0"/></text>
<text x="390" y="405" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力「右キー」: 待機 → 走る<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;0.2160;0.2162;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="405" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力「ジャンプ」: 走る → ジャンプ<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2160;0.2162;0.3782;0.3784;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="405" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力「着地」: ジャンプ → 待機<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3782;0.3784;0.5403;0.5405;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="405" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力「攻撃」: 待機 → 攻撃<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5403;0.5405;0.7025;0.7027;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="405" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力「終了」: 攻撃 → 待機<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7025;0.7027;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:state-transition-walk:end -->

## よくあるミス

??? failure "bool のフラグを増やしていく"
    `is_jumping`、`is_attacking`、`is_damaged` を別々に持つと、組み合わせが 8 通りになり、ありえない状態が生まれます。1 つの状態変数にまとめます。

??? failure "switch の default で新しい状態を見落とす"
    `enum class` の switch に `default:` を書くと、状態を追加したときに警告が出なくなります。全部の case を書けば、足りないときにコンパイラが警告してくれます（`-Wswitch` / MSVC の C4062）。

??? failure "状態を変えた同じフレームで、古い状態の処理が続く"
    状態を変えたあとは `return` するか、遷移をフレームの最後にまとめて行います。

## 関連ページ

- [シーン管理](../../engine/scene.md)
- [std::variant](../../stl/utilities/variant.md)
- [Game Programming Patterns: State](https://gameprogrammingpatterns.com/state.html)
