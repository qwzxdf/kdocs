---
title: ステートマシン
tags:
  - ゲームエンジン
---

# ステートマシン

**ステートマシン**（状態機械）は、**オブジェクトの「今の状態」と「どの条件でどの状態に移るか」をはっきり決めて管理する仕組み**です。プレイヤーなら「立ち・歩き・ジャンプ・攻撃」、敵の AI なら「待機・巡回・追跡・攻撃」のように、状態ごとにできることや動きが変わります。`bool is_jumping; bool is_attacking;` のようにフラグを増やしていくと、「ジャンプ中なのに攻撃中」のようなありえない組み合わせが生まれますが、状態を 1 つの変数で持てば必ず 1 つの状態にしかなりません。

!!! tip "ポイント"
    - <strong>状態が少ないうちは `enum class` + `switch` で十分。</strong>
    - 状態ごとのデータや処理が増えたら、状態をクラスにする（State パターン）か、[`std::variant`](../../stl/utilities/variant.md) で持つ。
    - 状態に入るとき・出るときの処理（Enter / Exit）を用意すると、アニメーションやエフェクトの開始・終了を書きやすい。
    - 状態の移り方（遷移）を図に描いてから作ると、抜け漏れが減る。

!!! info "このページを読む前に"
    [継承と仮想関数](../../basics/virtual.md) と [`std::variant`](../../stl/utilities/variant.md) を使います。

## 基本

### enum class + switch

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

### 遷移の表

| 今の状態 | 条件 | 次の状態 |
| --- | --- | --- |
| 立ち | 移動入力 | 走り |
| 立ち / 走り | ジャンプ入力 | ジャンプ |
| 走り | 移動入力なし | 立ち |
| ジャンプ | 着地 | 立ち |

作る前にこういう表や図を書いておくと、「走りながら攻撃したら？」のような抜けに気づけます。

<svg class="fig flow" viewBox="0 0 418 196" role="img" aria-label="ステートマシン：今の状態と、遷移"><defs><marker id="fl37273" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ステートマシン：今の状態と、遷移</text><line x1="107.0" y1="64.0" x2="165.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37273)"/><text x="136.0" y="58.0" text-anchor="middle" style="font-size:12px">移動入力</text><line x1="247.0" y1="64.0" x2="305.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37273)"/><text x="276.0" y="58.0" text-anchor="middle" style="font-size:12px">ジャンプ</text><line x1="305.0" y1="64.0" x2="107.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37273)"/><text x="206.0" y="58.0" text-anchor="middle" style="font-size:12px">着地</text><line x1="104.3" y1="87.0" x2="167.7" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37273)"/><text x="136.0" y="100.0" text-anchor="middle" style="font-size:12px">攻撃</text><line x1="167.7" y1="125.0" x2="104.3" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl37273)"/><rect x="28.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">待機</text><rect x="168.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">走る</text><rect x="308.0" y="44.0" width="82" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="349.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ジャンプ</text><rect x="168.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">攻撃</text></svg>

## 詳しく

### 状態をクラスにする（State パターン）

状態ごとの処理やデータが増えたら、状態を 1 つずつクラスにします。

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

状態ごとに違うデータ（ジャンプなら残り時間、攻撃ならコンボ数）を持たせたいときは、`std::variant` が便利です。ヒープも使いません。

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

### 方式の比較

| 方式 | 向いているとき |
| --- | --- |
| `enum class` + `switch` | 状態が少ない（〜5 個程度）。一番読みやすい |
| `std::variant` + `visit` | 状態ごとにデータが違う。対応漏れをコンパイラが見つけてくれる |
| State パターン（クラス） | 状態ごとの処理が大きい。状態をあとから追加しやすくしたい |
| 階層型ステートマシン | 「地上（立ち・歩き・走り）」「空中（ジャンプ・落下）」のように状態をグループ化したい |
| ビヘイビアツリー | 複雑な AI。状態マシンだと遷移が増えすぎるとき |

## ゲームでの例

| 対象 | 状態 |
| --- | --- |
| プレイヤー | 立ち、歩き、ジャンプ、攻撃、被ダメージ、死亡 |
| 敵 AI | 待機、巡回、追跡、攻撃、逃走 |
| ゲーム全体 | タイトル、プレイ中、ポーズ、ゲームオーバー（[シーン管理](../../engine/scene.md)） |
| UI | 閉じている、開く途中、開いている、閉じる途中 |
| ドア | 閉、開く途中、開、閉まる途中 |

## よくあるミス

??? failure "bool のフラグを増やしていく"
    `is_jumping`、`is_attacking`、`is_damaged` を別々に持つと、組み合わせが 8 通りになり、ありえない状態が生まれます。1 つの状態変数にまとめます。

??? failure "switch の default で新しい状態を見落とす"
    `enum class` の switch に `default:` を書くと、状態を追加したときに警告が出なくなります。全部の case を書けば、足りないときにコンパイラが警告してくれます（`-Wswitch` / MSVC の C4062）。

??? failure "状態を変えた同じフレームで、古い状態の処理が続く"
    状態を変えたあとは `return` するか、遷移をフレームの最後にまとめて行います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 状態は 1 つの変数で持つ（フラグを増やさない）
    - [x] 少なければ enum + switch、データが違えば variant、大きければクラス
    - [x] 遷移は表や図に書いてから作る

## 関連ページ

- [シーン管理](../../engine/scene.md)
- [std::variant](../../stl/utilities/variant.md)
- [Game Programming Patterns: State](https://gameprogrammingpatterns.com/state.html)
