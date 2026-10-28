---
title: アンチパターン集
tags:
  - 設計
  - 実践
---

# アンチパターン集

**アンチパターン**は、「よくやってしまうが、あとで困る書き方」です。デザインパターンが「うまくいく型」なら、アンチパターンは「はまりやすい落とし穴」です。このページは、実際のコードで、悪い例（Before）と、直した例（After）を並べて、なぜ困るのかと、どう直すかを示します。タブを切り替えて、見比べてください。

!!! tip "ポイント"
    - アンチパターンは、**最初は便利に見える**から、はまる。「あとで困る」を先に知っておく。
    - 多くは、「**1 か所に集めすぎる**」「あちこちから触れすぎる」「先回りしすぎる」のどれか。
    - 全部を避ける必要はない。小さなゲームなら、許せるものもある。大きくなる前に直す。
    - 直すときは、[リファクタリング](refactoring-smells.md)の小さな手順で。
    - 名前より、なぜ困るのかを理解する。

!!! info "このページを読む前に"
    - [design/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](../foundations/principles.md)（設計の基本原則）

## 設計のアンチパターン

### 神クラス（God Class / Manager だらけ）

| 症状 | `GameManager`、`Utils`、`Common` が、何千行もある。何でも入っている |
| --- | --- |
| なぜ起きる | 「とりあえずここに書けば動く」を繰り返す |
| 困ること | 変更が怖い。複数人で同時に触れず、衝突する。テストできない |

=== "Before（悪い例）"

    ```cpp
    class GameManager {
     public:
      void Update(float dt) {
        UpdateInput();
        UpdatePlayer(dt);
        UpdateEnemies(dt);
        UpdateBullets(dt);
        UpdateCollision();
        UpdateUi();
        UpdateSound();
        SaveIfNeeded();
      }

      void LoadStage(int stage);
      void SaveGame();
      void DrawEverything();
      void PlaySe(int id);
      void ShowDialog(const std::string& text);
      // …1 万行

     private:
      std::vector<Enemy> enemies_;
      std::vector<Bullet> bullets_;
      Player player_;
      Ui ui_;
      SoundEngine sound_;
      SaveData save_;
      // …何でも持っている
    };
    ```

=== "After（直した例）"

    ```cpp
    class Game {
     public:
      void Update(float dt) {
        input_.Update();
        player_.Update(dt, input_);
        enemies_.Update(dt);
        bullets_.Update(dt);
        collision_.Resolve(player_, enemies_, bullets_);
        ui_.Update(player_);
      }

     private:
      InputSystem input_;
      Player player_;
      EnemySystem enemies_;
      BulletSystem bullets_;
      CollisionSystem collision_;
      UiSystem ui_;
    };
    ```

    **責任ごとに、クラスを分けます**（入力・敵・弾・当たり判定・UI）。`Game` は、それらを順に呼ぶだけです。

直し方：責任ごとに分ける。名前に `Manager` と付けたくなったら、何をする責任かを考えます。

### 過剰な継承（継承の地獄）

| 症状 | 継承が 5 段以上。組み合わせごとにクラスが増える |
| --- | --- |
| 困ること | 親の変更が全員に影響する。「飛ぶ + 撃つ」のような組み合わせに、新しいクラスがいる |

=== "Before（悪い例）"

    ```cpp
    class Enemy { virtual void Update(float dt); };
    class FlyingEnemy : public Enemy { void Update(float dt) override { Fly(dt); } };
    class ShootingEnemy : public Enemy { void Update(float dt) override { Shoot(dt); } };
    class FlyingShootingEnemy : public FlyingEnemy {
      void Update(float dt) override {
        Fly(dt);
        Shoot(dt);
      }
    };
    class BossFlyingShootingEnemy : public FlyingShootingEnemy { /* … */ };
    ```

=== "After（直した例）"

    ```cpp
    struct Enemy {
      std::vector<std::unique_ptr<Behavior>> behaviors;

      void Update(float dt) {
        for (auto& b : behaviors) b->Update(*this, dt);
      }
    };

    Enemy boss;
    boss.behaviors.push_back(std::make_unique<FlyBehavior>());
    boss.behaviors.push_back(std::make_unique<ShootBehavior>());
    ```

    機能を部品（コンポーネント）にして、組み合わせます。新しい組み合わせでも、クラスは増えません（[継承と合成](../foundations/composition-vs-inheritance.md)）。

### 何でもシングルトン / グローバル変数

| 症状 | `Game::Instance()`、`g_player`、`extern` の変数がどこからでも使われる |
| --- | --- |
| 困ること | 誰がいつ書き換えたか分からない。初期化の順番で壊れる。テストできない |

=== "Before（悪い例）"

    ```cpp
    extern Player g_player;

    void Enemy::Attack() {
      g_player.hp -= damage_;
      Game::Instance().Sound().Play(kHitSe);
      Game::Instance().Score().Add(10);
    }
    ```

=== "After（直した例）"

    ```cpp
    void Enemy::Attack(Player& target, ISound& sound) {
      target.hp -= damage_;
      sound.Play(kHitSe);
    }

    enemy.Attack(player, sound);
    ```

    使う相手を引数で受け取ります。何に依存しているかが、シグネチャで見え、テストでは、偽物を渡せます（[依存性の注入](../patterns/dependency-injection.md)、[シングルトン](../patterns/singleton.md)）。

### 循環依存

| 症状 | A が B を include し、B が A を include している。ヘッダの循環で、ビルドエラー |
| --- | --- |
| 困ること | ビルドが通らない・遅い。お互いを分離できない |

=== "Before（悪い例）"

    ```cpp
    // player.h
    #include "enemy.h"
    class Player {
      Enemy* target_;
    };

    // enemy.h
    #include "player.h"
    class Enemy {
      Player* target_;
    };
    ```

=== "After（直した例）"

    ```cpp
    // player.h
    class Enemy;
    class Player {
      Enemy* target_;
    };

    // enemy.h
    class Player;
    class Enemy {
      Player* target_;
    };
    ```

    ポインタ・参照だけなら、前方宣言で足ります。`.cpp` で include します。それでも循環するなら、共通のインターフェース（`IDamageable`）に依存するか、イベントで通知して、依存を一方向にします（[レイヤー](../foundations/layers.md)、[ヘッダとソース](../foundations/header-source.md)）。

### 早すぎる一般化（YAGNI 違反）

| 症状 | 「将来使うかも」で、設定だらけ・テンプレートだらけ・インターフェースだらけにする |
| --- | --- |
| 困ること | 使わない仕組みの分、複雑。結局、必要になったのは、別の形だった |

=== "Before（悪い例）"

    ```cpp
    template <typename T, typename Policy = DefaultPolicy, typename Allocator = std::allocator<T>>
    class AbstractEnemyFactoryProvider : public IProvider<IFactory<T>> {
      // 使われているのは、Goblin 1 種類だけ
    };
    ```

=== "After（直した例）"

    ```cpp
    std::unique_ptr<Enemy> CreateGoblin(Vector3 position) {
      return std::make_unique<Goblin>(position);
    }
    ```

    今必要なものだけを作ります。2 種類目が出てきたときに、共通部分を抜き出して広げます。

### データと処理が離れている（貧血なドメイン）

| 症状 | `struct` はデータだけ。処理は、`XxxManager` に全部 |
| --- | --- |
| 困ること | データの不整合をどこでも作れる。変更がいろいろなファイルに散らばる |

=== "Before（悪い例）"

    ```cpp
    struct Player {
      int hp;
      int max_hp;
    };

    void PlayerManager::Damage(Player& p, int amount) { p.hp -= amount; }
    void SomewhereElse(Player& p) { p.hp = 9999; }
    ```

=== "After（直した例）"

    ```cpp
    class Player {
     public:
      void TakeDamage(int amount) { hp_ = std::max(0, hp_ - amount); }
      void Heal(int amount) { hp_ = std::min(max_hp_, hp_ + amount); }
      bool IsDead() const { return hp_ == 0; }

     private:
      int hp_ = 100;
      int max_hp_ = 100;
    };
    ```

    「HP は 0〜最大値の範囲」という決まり（不変条件）をクラスの中で守ります。外からは、壊れた状態を作れません（[クラス設計](../foundations/class-design.md)）。

## コードの書き方のアンチパターン

### マジックナンバー

| 症状 | `if (type == 3)`、`damage * 1.5f`、`for (i = 0; i < 64; ...)` |
| --- | --- |
| 困ること | **意味が分からない**。同じ数を何か所も直すことになる |

=== "Before（悪い例）"

    ```cpp
    if (enemy.type == 3) {
      damage = base * 1.5f;
    }
    for (int i = 0; i < 64; ++i) { ... }
    ```

=== "After（直した例）"

    ```cpp
    enum class EnemyType { kSlime, kGoblin, kBoss };
    constexpr float kBossDamageRate = 1.5f;
    constexpr int kMaxEnemies = 64;

    if (enemy.type == EnemyType::kBoss) {
      damage = base * kBossDamageRate;
    }
    for (int i = 0; i < kMaxEnemies; ++i) { ... }
    ```

    名前を付けると、意味が読めます。調整したい数値は、データファイルに出します（[ファクトリとデータ駆動](../patterns/factory.md)）。

### コピー＆ペースト

| 症状 | 同じコードを少しだけ変えて何か所にも貼っている |
| --- | --- |
| 困ること | 直すとき、貼った全部を直す必要がある。直し忘れでバグ |

=== "Before（悪い例）"

    ```cpp
    void DrawHealthBarPlayer(const Player& p) {
      float ratio = static_cast<float>(p.hp) / p.max_hp;
      DrawRect(10, 10, 200 * ratio, 20, kGreen);
    }
    void DrawHealthBarEnemy(const Enemy& e) {
      float ratio = static_cast<float>(e.hp) / e.max_hp;
      DrawRect(e.x, e.y - 20, 50 * ratio, 6, kRed);
    }
    ```

=== "After（直した例）"

    ```cpp
    void DrawHealthBar(Vector2 position, float width, float height, int hp, int max_hp, Color color) {
      float ratio = static_cast<float>(hp) / max_hp;
      DrawRect(position.x, position.y, width * ratio, height, color);
    }

    DrawHealthBar({10, 10}, 200, 20, player.hp, player.max_hp, kGreen);
    DrawHealthBar({enemy.x, enemy.y - 20}, 50, 6, enemy.hp, enemy.max_hp, kRed);
    ```

    共通の部分を関数にして、違う部分を引数にします。

### 長い `if` / `else if` の連鎖・`switch` の増殖

| 症状 | 種類による分岐があちこちに散らばっている |
| --- | --- |
| 困ること | 新しい種類を足すたびに、全部の `switch` を直す。1 か所直し忘れる |

=== "Before（悪い例）"

    ```cpp
    float GetSpeed(const Enemy& e) {
      switch (e.type) {
        case EnemyType::kSlime: return 1.0f;
        case EnemyType::kGoblin: return 2.0f;
        case EnemyType::kBoss: return 1.5f;
      }
    }
    void Attack(Enemy& e) {
      switch (e.type) {
        case EnemyType::kSlime: /* … */ break;
        case EnemyType::kGoblin: /* … */ break;
        case EnemyType::kBoss: /* … */ break;
      }
    }
    ```

=== "After（直した例）"

    ```cpp
    class Enemy {
     public:
      virtual ~Enemy() = default;
      virtual float Speed() const = 0;
      virtual void Attack() = 0;
    };

    class Slime : public Enemy {
      float Speed() const override { return 1.0f; }
      void Attack() override { /* … */ }
    };
    ```

    種類ごとの違いをクラス（または[ストラテジー](../patterns/strategy.md)・[ステートマシン](../patterns/state-machine.md)・データ）にまとめます。種類を足すときは、クラスを 1 つ足すだけです。

### 例外を制御の流れに使う

| 症状 | 「見つからない」「入力が違う」のような、普通に起きることを `throw` で表している |
| --- | --- |
| 困ること | 遅い。流れが追えない |

=== "Before（悪い例）"

    ```cpp
    Item FindItem(int id) {
      auto it = items_.find(id);
      if (it == items_.end()) throw std::runtime_error("not found");
      return it->second;
    }

    try {
      Item item = FindItem(id);
    } catch (const std::exception&) {
      // 見つからないのは、普通に起きる
    }
    ```

=== "After（直した例）"

    ```cpp
    std::optional<Item> FindItem(int id) {
      auto it = items_.find(id);
      if (it == items_.end()) return std::nullopt;
      return it->second;
    }

    if (auto item = FindItem(id)) {
      Use(*item);
    }
    ```

    「ないかもしれない」は `std::optional`、理由付きの失敗は `std::expected`（[エラー処理](../foundations/error-handling.md)）。例外は、本当に例外的な事態だけにします。

### エラーを握りつぶす

| 症状 | `catch (...) {}` と何もしない。戻り値のエラーを無視する |
| --- | --- |
| 困ること | 失敗に気づけず、後でおかしな所で壊れる |

=== "Before（悪い例）"

    ```cpp
    try {
      LoadStage(path);
    } catch (...) {
    }

    SaveGame(data);
    ```

=== "After（直した例）"

    ```cpp
    [[nodiscard]] bool SaveGame(const SaveData& data);

    if (!SaveGame(data)) {
      Log::Error("セーブに失敗しました: {}", path);
      ShowErrorDialog();
    }

    try {
      LoadStage(path);
    } catch (const std::exception& e) {
      Log::Error("ステージの読み込みに失敗: {}", e.what());
      throw;
    }
    ```

    ログに出す・上に伝える。`[[nodiscard]]` を付けて、戻り値の無視に警告が出るようにします。

### 生の `new` / `delete`、`malloc` / `free`

| 症状 | 自分で解放する。`delete` を書き忘れる・2 回書く・早期 `return` で飛ばされる |
| --- | --- |
| 困ること | リーク・二重解放・解放後の使用 |

=== "Before（悪い例）"

    ```cpp
    Enemy* e = new Enemy();
    if (!e->Init()) {
      return;
    }
    Process(e);
    delete e;
    ```

=== "After（直した例）"

    ```cpp
    auto e = std::make_unique<Enemy>();
    if (!e->Init()) {
      return;
    }
    Process(*e);
    ```

    `std::unique_ptr` が、どの出口でも、自動で解放します。`std::vector` などのコンテナも同じです（[RAII](../patterns/raii.md)）。

### `using namespace std;` をヘッダに書く

| 症状 | ヘッダの先頭に `using namespace std;` |
| --- | --- |
| 困ること | そのヘッダを include した全員の名前空間が汚れ、名前が衝突する |

=== "Before（悪い例）"

    ```cpp
    #pragma once
    #include <vector>
    using namespace std;

    class Level {
      vector<int> tiles_;
    };
    ```

=== "After（直した例）"

    ```cpp
    #pragma once
    #include <vector>

    class Level {
      std::vector<int> tiles_;
    };
    ```

    ヘッダでは、`std::` を付けます。`using` は、`.cpp` の関数の中だけにします。

### 値渡しの乱用・参照のぶら下がり

| 症状 | 大きなオブジェクトを値で渡す。ローカル変数の参照を返す |
| --- | --- |
| 困ること | 無駄なコピーで遅い。消えた変数を指して、クラッシュ |

=== "Before（悪い例）"

    ```cpp
    void Draw(std::vector<Vertex> vertices, std::string name);

    const std::string& MakeName() {
      std::string s = "enemy";
      return s;
    }
    ```

=== "After（直した例）"

    ```cpp
    void Draw(const std::vector<Vertex>& vertices, std::string_view name);

    std::string MakeName() {
      return "enemy";
    }
    ```

    読むだけなら `const&`（文字列は `string_view`）。新しく作ったものは、値で返す（ムーブ・省略されるので、コピーされません）（[const と引数の渡し方](../foundations/const-and-passing.md)）。

### 初期化されていない変数

| 症状 | `int hp;` と宣言して、代入前に読む |
| --- | --- |
| 困ること | 値が不定。Debug と Release で、動きが違う |

=== "Before（悪い例）"

    ```cpp
    struct Enemy {
      int hp;
      float speed;
      bool alive;
    };

    Enemy e;
    if (e.alive) { ... }
    ```

=== "After（直した例）"

    ```cpp
    struct Enemy {
      int hp = 100;
      float speed = 1.0f;
      bool alive = true;
    };

    Enemy e;
    ```

    メンバの宣言時に初期値を書きます（`{}` でゼロ初期化でも）。警告 `C4700` を見逃さないようにします。

## ゲームに多いアンチパターン

### 毎フレーム、同じものを作って捨てる

| 症状 | `Update` の中で、`std::vector` や `std::string` を毎回作っている |
| --- | --- |
| 困ること | **メモリ確保が重く**、フレームがカクつく |

=== "Before（悪い例）"

    ```cpp
    void Update(float dt) {
      std::vector<Enemy*> nearby;
      for (Enemy& e : enemies_) {
        if (IsNear(e)) nearby.push_back(&e);
      }
      std::string text = "HP: " + std::to_string(hp_);
      ui_.Draw(text);
    }
    ```

=== "After（直した例）"

    ```cpp
    class Game {
     public:
      Game() { nearby_.reserve(256); }

      void Update(float dt) {
        nearby_.clear();
        for (Enemy& e : enemies_) {
          if (IsNear(e)) nearby_.push_back(&e);
        }

        char text[32];
        std::format_to_n(text, sizeof(text) - 1, "HP: {}", hp_);
        ui_.Draw(text);
      }

     private:
      std::vector<Enemy*> nearby_;
    };
    ```

    メンバに持って、`reserve` + `clear()` で使い回す。文字列は、固定バッファに書きます（[毎フレームのヒープ確保を避ける](../../optimize/frame-allocation.md)）。

### ゲームの更新速度がフレームレートに依存する

| 症状 | `position += 5;`（毎フレーム固定の量） |
| --- | --- |
| 困ること | 60 FPS と 144 FPS で、速さが違う |

=== "Before（悪い例）"

    ```cpp
    void Update() {
      position.x += 5.0f;
    }
    ```

=== "After（直した例）"

    ```cpp
    void Update(float dt) {
      constexpr float kSpeed = 300.0f;
      position.x += kSpeed * dt;
    }
    ```

    「1 秒あたりの量 × 経過時間（`dt`）」にします。物理は、固定タイムステップ（[ゲームループ](../../engine/game-loop.md)、[フレーム時間の設計](../../optimize/frame-budget.md)）。

### オブジェクトへのポインタをずっと持つ

| 症状 | 敵へのポインタを弾が持っている。敵が消えると、壊れる |
| --- | --- |
| 困ること | ぶら下がりポインタ。クラッシュ・原因不明の挙動 |

=== "Before（悪い例）"

    ```cpp
    struct Bullet {
      Enemy* target;

      void Update() {
        direction = Normalize(target->position - position);
      }
    };
    ```

=== "After（直した例）"

    ```cpp
    struct Bullet {
      EnemyHandle target;

      void Update(EnemyPool& enemies) {
        if (Enemy* e = enemies.Get(target)) {
          direction = Normalize(e->position - position);
        }
      }
    };
    ```

    ハンドル（番号 + 世代）で持ち、使うときに、まだ生きているかを確認します（[ハンドル](../../engine/handle.md)）。

### 文字列で、種類や名前を比べる

| 症状 | `if (name == "player")` を毎フレーム何千回もやっている |
| --- | --- |
| 困ること | 遅い。綴りの間違いに、気づけない |

=== "Before（悪い例）"

    ```cpp
    for (Entity& e : entities) {
      if (e.name == "enemy") { ... }
      else if (e.name == "item") { ... }
    }
    ```

=== "After（直した例）"

    ```cpp
    enum class EntityKind : uint8_t { kEnemy, kItem, kPlayer };

    for (Entity& e : entities) {
      switch (e.kind) {
        case EntityKind::kEnemy: ...
        case EntityKind::kItem: ...
      }
    }
    ```

    `enum class`・整数の ID・コンパイル時のハッシュにします（[文字列とハッシュ](../../optimize/strings-hash.md)、[std::hash](../../stl/utilities/hash.md)）。

### デバッグ用のコードをそのまま残す

| 症状 | `std::println` や、デバッグ描画が製品版に残っている |
| --- | --- |
| 困ること | 遅く、ログがあふれる。チート用のコマンドが残る |

=== "Before（悪い例）"

    ```cpp
    void Update() {
      std::println("player pos: {} {}", p.x, p.y);
      DrawDebugBox(collider);
    }
    ```

=== "After（直した例）"

    ```cpp
    void Update() {
      LOG_DEBUG("player pos: {} {}", p.x, p.y);
    #ifdef ENABLE_DEBUG_DRAW
      DrawDebugBox(collider);
    #endif
    }
    ```

    ログのレベルと、ビルド構成で消えるマクロで、製品版には、残らないようにします（[ログとデバッグ支援](logging-debug.md)、[プリプロセッサマクロ](../../vs/preprocessor.md)）。

### 当たり判定・AI を全員 × 全員で調べる

| 症状 | 全員と全員を総当たり（[O(n²)](../../basics/big-o.md#on2)） |
| --- | --- |
| 困ること | 数が増えると、急に重くなる（1000 体で 100 万回） |

=== "Before（悪い例）"

    ```cpp
    for (Enemy& a : enemies) {
      for (Enemy& b : enemies) {
        if (&a != &b && Overlap(a, b)) Resolve(a, b);
      }
    }
    ```

=== "After（直した例）"

    ```cpp
    grid.Clear();
    for (Enemy& e : enemies) grid.Insert(e);

    for (Enemy& a : enemies) {
      grid.ForEachNear(a.position, a.radius, [&](Enemy& b) {
        if (&a != &b && Overlap(a, b)) Resolve(a, b);
      });
    }
    ```

    空間分割（グリッド・四分木）で、近いものだけを調べます（[アルゴリズム](../../optimize/algorithms.md)、[3D の衝突判定](../../3d/collision-3d.md)）。

### コンポーネントを毎フレーム `dynamic_cast` で探す

| 症状 | 毎フレーム、`dynamic_cast` で、必要なコンポーネントを探している |
| --- | --- |
| 困ること | 遅い。型を調べるコストが毎回かかる |

=== "Before（悪い例）"

    ```cpp
    void Update() {
      for (auto& c : components_) {
        if (auto* r = dynamic_cast<Renderer*>(c.get())) {
          r->Draw();
        }
      }
    }
    ```

=== "After（直した例）"

    ```cpp
    class GameObject {
     public:
      void Update() {
        if (renderer_) renderer_->Draw();
      }

     private:
      Renderer* renderer_ = nullptr;
      std::vector<std::unique_ptr<Component>> components_;
    };
    ```

    よく使うコンポーネントは、ポインタを覚えておく。または、種類ごとの配列にします（[コンポーネント](../../engine/component.md)、[ECS](../patterns/ecs.md)）。

## 組織・進め方のアンチパターン

| アンチパターン | 症状 | 直し方 |
| --- | --- | --- |
| **ビッグバン統合** | 各自が長期間バラバラに作って、最後に一気に合体して壊れる | こまめに統合（毎日、動くものを共有） |
| コピーで管理 | `game_final.cpp`、`game_final2.cpp`… | Git で履歴を管理する |
| ドキュメントなし | 作った本人しか分からない | 重要な設計と、使い方だけ書く |
| レビューなし | 1 人で作り、バグに気づかない | 他の人に読んでもらう |
| 全部作り直したくなる | 「最初から作り直せばきれいに」 | ほとんどの場合、少しずつ直すほうが速い |

## よくあるミス（このページ自体の使い方）

??? failure "全部のアンチパターンを今すぐ直そうとする"
    小さなゲームでは、許せるものもあります。**困っているものだけ**直します。

??? failure "アンチパターンを避けるために、別のアンチパターンに入る"
    「グローバルが悪い」と聞いて、何でも引数で渡して、10 個の引数になる、など。コンテキスト構造体にまとめるなどで、バランスを取ります。

??? failure "名前だけを覚えて、理由を理解しない"
    「シングルトンは悪」という言葉だけだと、本当に 1 つしかないものまで、無理に避けてしまいます。なぜ困るのかを理解して、判断します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アンチパターン ＝ よくやるが、あとで困る書き方
    - [x] 大きく分けると「集めすぎ（神クラス）」「触れすぎ（グローバル）」「先回りしすぎ（YAGNI 違反）」
    - [x] ゲームに多い：毎フレームの確保、フレームレート依存、ポインタの保持、文字列比較、総当たり
    - [x] 全部を避けない。**困りそうなもの**から直す
    - [x] 名前より、なぜ困るかを理解する

## 関連ページ

- [リファクタリングとコードの臭い](refactoring-smells.md)
- [設計の基本原則](../foundations/principles.md)
- [継承と合成](../foundations/composition-vs-inheritance.md)
- [パフォーマンス設計](performance-design.md)
- [エラー処理の方針](../foundations/error-handling.md)
