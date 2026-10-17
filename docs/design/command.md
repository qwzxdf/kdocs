---
title: コマンドパターン
tags:
  - 設計
---

# コマンドパターン

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**コマンドパターン**は、<strong>「何をするか」という命令そのものをオブジェクト（データ）にする</strong>設計です。「ジャンプする」「アイテムを使う」「ユニットを (3, 5) へ動かす」を関数としてすぐ実行するのではなく、`JumpCommand` のようなオブジェクトにしておくと、**後で実行する・取り消す（アンドゥ）・記録して再生する・キーの割り当てを変える**といったことが簡単にできるようになります。

!!! tip "ポイント"
    - 入力の割り当て変更（キーコンフィグ）、アンドゥ・リドゥ、リプレイ、AI とプレイヤーで同じ操作を使う、に効く。
    - 形は「`Execute()`（と `Undo()`）を持つクラス」か、単に `std::function<void()>`。
    - アンドゥは「実行前の状態」をコマンドの中に覚えておく。
    - 種類が決まっているなら [`std::variant`](../stl/utilities/variant.md) でコマンドを表すと、ヒープも使わず保存もしやすい。

## 悪い例：入力と処理が直結している

```cpp
void HandleInput(Player& player) {
  if (IsKeyDown(KEY_SPACE)) player.Jump();
  if (IsKeyDown(KEY_Z)) player.Attack();
}
```

- キーの割り当てを変えるには、コードを書き換える必要がある
- 敵の AI に同じ「ジャンプ」をさせたいとき、入力の処理を通せない
- 操作を記録して再生（リプレイ）できない

## 良い例：命令をオブジェクトにする

```cpp
#include <memory>
#include <print>
#include <unordered_map>

struct Actor {
  int x = 0;
  int y = 0;
};

class Command {
 public:
  virtual ~Command() = default;
  virtual void Execute(Actor& actor) = 0;
};

class JumpCommand : public Command {
 public:
  void Execute(Actor& actor) override {
    actor.y += 2;
    std::println("ジャンプ → y = {}", actor.y);
  }
};

class MoveRightCommand : public Command {
 public:
  void Execute(Actor& actor) override {
    ++actor.x;
    std::println("右へ → x = {}", actor.x);
  }
};

int main() {
  // キー → コマンド の表（キーコンフィグで入れ替えられる）
  std::unordered_map<char, std::unique_ptr<Command>> bindings;
  bindings['z'] = std::make_unique<JumpCommand>();
  bindings['d'] = std::make_unique<MoveRightCommand>();

  Actor player;
  for (char key : {'d', 'z', 'd'}) {  // 押されたキー
    if (auto it = bindings.find(key); it != bindings.end()) {
      it->second->Execute(player);
    }
  }

  // AI も同じコマンドで敵を動かせる
  Actor enemy;
  JumpCommand().Execute(enemy);
}
```

```text title="実行結果"
右へ → x = 1
ジャンプ → y = 2
右へ → x = 2
ジャンプ → y = 2
```

## 詳しく

### アンドゥ・リドゥ

コマンドに「元に戻す」処理を持たせ、実行したコマンドをスタックに積んでおきます。

```cpp
#include <memory>
#include <print>
#include <vector>

struct Board {
  int pieces[3] = {0, 0, 0};
};

class MoveCommand {
 public:
  MoveCommand(int from, int to) : from_(from), to_(to) {}
  void Execute(Board& b) {
    b.pieces[to_] += 1;
    b.pieces[from_] -= 1;
  }
  void Undo(Board& b) {  // Execute のちょうど逆
    b.pieces[from_] += 1;
    b.pieces[to_] -= 1;
  }

 private:
  int from_;
  int to_;
};

class History {
 public:
  void Do(MoveCommand cmd, Board& b) {
    cmd.Execute(b);
    done_.push_back(cmd);
    undone_.clear();  // 新しく操作したらリドゥはできなくなる
  }
  void Undo(Board& b) {
    if (done_.empty()) return;
    done_.back().Undo(b);
    undone_.push_back(done_.back());
    done_.pop_back();
  }
  void Redo(Board& b) {
    if (undone_.empty()) return;
    undone_.back().Execute(b);
    done_.push_back(undone_.back());
    undone_.pop_back();
  }

 private:
  std::vector<MoveCommand> done_;
  std::vector<MoveCommand> undone_;
};

int main() {
  Board board;
  board.pieces[0] = 2;
  History history;
  history.Do(MoveCommand(0, 1), board);
  history.Do(MoveCommand(1, 2), board);
  std::println("{} {} {}", board.pieces[0], board.pieces[1], board.pieces[2]);
  history.Undo(board);
  std::println("{} {} {}", board.pieces[0], board.pieces[1], board.pieces[2]);
  history.Redo(board);
  std::println("{} {} {}", board.pieces[0], board.pieces[1], board.pieces[2]);
}
```

```text title="実行結果"
1 0 1
1 1 0
1 0 1
```

### variant で表す

コマンドの種類が決まっているなら、継承の代わりに `std::variant` が使えます。値なのでコピー・保存（リプレイのファイル書き出し）が簡単です。

```cpp
#include <print>
#include <variant>
#include <vector>

struct Move {
  int dx;
  int dy;
};
struct Attack {
  int target;
};
using Command = std::variant<Move, Attack>;

template <class... Fs>
struct Overloaded : Fs... {
  using Fs::operator()...;
};

int main() {
  std::vector<Command> replay = {Move{1, 0}, Attack{7}, Move{0, -1}};  // 記録した操作
  int x = 0;
  int y = 0;
  for (const auto& cmd : replay) {
    std::visit(Overloaded{
                   [&](const Move& m) { x += m.dx; y += m.dy; },
                   [](const Attack& a) { std::println("攻撃 {}", a.target); },
               },
               cmd);
  }
  std::println("({}, {})", x, y);
}
```

```text title="実行結果"
攻撃 7
(1, -1)
```

### 実装の選び方

| 方法 | 向いているとき |
| --- | --- |
| 継承（`Command` 基底クラス） | コマンドの種類をあとから増やしやすくしたい |
| `std::variant` | 種類が決まっている。保存・ネットワーク送信したい |
| `std::function<void()>` | アンドゥ不要で、とにかく「あとで実行」したい |

## ゲームでの例

| 用途 | 例 |
| --- | --- |
| キーコンフィグ | キー → コマンドの表を書き換える |
| アンドゥ | パズルの一手戻し、エディタの操作の取り消し |
| リプレイ | フレームごとのコマンドを記録して再生 |
| ターン制 RTS | 「ユニット A を (3, 5) へ」を予約しておき、ターンの最後にまとめて実行 |
| ネットワーク | 入力ではなくコマンドを送り合う |

## よくある失敗

??? failure "Undo が Execute の逆になっていない"
    「HP を半分にする」のように元に戻せない処理は、実行前の値をコマンドの中に覚えておき、Undo でその値に戻します。

??? failure "コマンドの中で、消えたオブジェクトを指している"
    アンドゥ用に長く保存するコマンドがポインタで相手を覚えていると、相手が消えたあとに壊れます。ID（[ハンドル](../engine/handle.md)）で覚えます。

## 理解度チェック

!!! question "Q1. 「HP を 30 回復する」コマンドの Undo を「HP を 30 減らす」にすると、どんなときに困る？"
    <div class="spoiler" markdown>

    **答え:** 最大 HP の上限で回復量が切られた場合（HP 90 / 最大 100 で 10 しか回復しない）、Undo で 30 減らすと元の 90 ではなく 70 になってしまいます。実行前の HP を覚えておいて、Undo でその値に戻します。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 命令をオブジェクトにすると、後で実行・取り消し・記録ができる
    - [x] キーコンフィグ、アンドゥ、リプレイに効く
    - [x] Undo は実行前の状態を覚えておく

## 関連ページ

- [イベントシステム](../engine/event.md)
- [std::variant](../stl/utilities/variant.md)
- [Game Programming Patterns: Command](https://gameprogrammingpatterns.com/command.html)
