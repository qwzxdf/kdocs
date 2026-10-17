---
title: シーン管理
tags:
  - ゲームエンジン
---

# シーン管理

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

**シーン**は、**タイトル画面・ゲーム本編・リザルト画面のような「場面」ごとのまとまり**です。シーンごとに Update と Draw を持たせ、**シーンマネージャ**が「今のシーン」だけを動かします。シーンを切り替えると前のシーンのオブジェクトがまとめて片付くので、メモリの管理も楽になります。ポーズメニューのように「今のシーンの上に別のシーンを重ねる」なら、シーンをスタックで持ちます。

!!! tip "ポイント"
    - 基底クラス `Scene`（`Update` / `Draw`）を作り、各場面はそれを継承する。
    - マネージャは `std::unique_ptr<Scene>` で今のシーンを持つ。切り替えると前のシーンは自動で消える。
    - **切り替えは「予約」して、フレームの最後に行う**（Update の途中で自分自身を消すと落ちる）。
    - ポーズやメニューを重ねるなら、`std::vector<std::unique_ptr<Scene>>` をスタックとして使う。

!!! info "このページを読む前に"
    [継承と仮想関数](../basics/virtual.md)、[`std::unique_ptr`](../stl/utilities/unique_ptr.md) を使います。

## 基本

```cpp
#include <memory>
#include <print>
#include <utility>

class SceneManager;

class Scene {
 public:
  virtual ~Scene() = default;
  virtual void Update(SceneManager& manager) = 0;
  virtual void Draw() const = 0;
};

class SceneManager {
 public:
  // すぐには切り替えず、予約だけしておく
  void ChangeScene(std::unique_ptr<Scene> next) { next_ = std::move(next); }

  void Update() {
    if (current_) {
      current_->Update(*this);
    }
    if (next_) {  // フレームの最後に切り替える
      current_ = std::move(next_);
    }
  }

  void Draw() const {
    if (current_) {
      current_->Draw();
    }
  }

 private:
  std::unique_ptr<Scene> current_;
  std::unique_ptr<Scene> next_;
};

class ResultScene : public Scene {
 public:
  explicit ResultScene(int score) : score_(score) {}
  void Update(SceneManager&) override {}
  void Draw() const override { std::println("リザルト: {} 点", score_); }

 private:
  int score_;
};

class GameScene : public Scene {
 public:
  void Update(SceneManager& manager) override {
    score_ += 100;
    if (score_ >= 300) {  // ゲーム終了
      manager.ChangeScene(std::make_unique<ResultScene>(score_));
    }
  }
  void Draw() const override { std::println("ゲーム中: {} 点", score_); }

 private:
  int score_ = 0;
};

class TitleScene : public Scene {
 public:
  void Update(SceneManager& manager) override {
    manager.ChangeScene(std::make_unique<GameScene>());  // ボタンが押されたとする
  }
  void Draw() const override { std::println("タイトル"); }
};

int main() {
  SceneManager manager;
  manager.ChangeScene(std::make_unique<TitleScene>());
  manager.Update();  // 最初のシーンを入れる

  for (int frame = 0; frame < 5; ++frame) {
    manager.Draw();
    manager.Update();
  }
}
```

```text title="実行結果"
タイトル
ゲーム中: 0 点
ゲーム中: 100 点
ゲーム中: 200 点
リザルト: 300 点
```

<div class="anim" data-type="graph" data-label="シーンの切り替え">
n title タイトル 0 0 hit
n game ゲーム 1 0
n result リザルト 2 0
l title game
l game result
l result title
# タイトルから始まる
---
n title タイトル 0 0
n game ゲーム 1 0 hit
n result リザルト 2 0
l title game hit 開始
l game result
l result title
# 開始すると、ゲームへ（前のシーンは片付けられる）
---
n title タイトル 0 0
n game ゲーム 1 0
n result リザルト 2 0 hit
l title game
l game result hit クリア
l result title
# クリアすると、リザルトへ
---
n title タイトル 0 0 hit
n game ゲーム 1 0
n result リザルト 2 0
l title game
l game result
l result title hit 戻る
# 戻ると、タイトルへ。シーンは、同時に 1 つだけ動く
</div>

## 詳しく

### なぜ切り替えを予約するのか

`GameScene::Update` の中で `current_ = std::make_unique<ResultScene>()` を直接実行すると、**今動いている GameScene 自身が消されて**、Update の残りの処理が消えたオブジェクトの上で動くことになります（未定義動作）。予約しておいて、Update が終わってから切り替えれば安全です。

### シーンのスタック（ポーズ・メニュー）

```cpp
#include <memory>
#include <print>
#include <vector>

struct Scene {
  virtual ~Scene() = default;
  virtual void Draw() const = 0;
  virtual bool IsOpaque() const { return true; }  // 下のシーンを隠すか
};

struct Game : Scene {
  void Draw() const override { std::println("  ゲーム画面"); }
};

struct Pause : Scene {
  void Draw() const override { std::println("  ポーズメニュー（半透明）"); }
  bool IsOpaque() const override { return false; }  // 下のゲーム画面も見える
};

int main() {
  std::vector<std::unique_ptr<Scene>> stack;
  stack.push_back(std::make_unique<Game>());
  stack.push_back(std::make_unique<Pause>());  // 上に重ねる

  // 描画は下から。Update は一番上だけ（ポーズ中はゲームが止まる）
  std::println("描画:");
  for (const auto& scene : stack) {
    scene->Draw();
  }

  stack.pop_back();  // ポーズを閉じる
  std::println("閉じたあと: {} 枚", stack.size());
}
```

```text title="実行結果"
描画:
  ゲーム画面
  ポーズメニュー（半透明）
閉じたあと: 1 枚
```

| 操作 | 意味 |
| --- | --- |
| Push | 今のシーンの上に重ねる（ポーズ、インベントリ、会話ウィンドウ） |
| Pop | 一番上を閉じて、下に戻る |
| Change | 全部（または一番上）を入れ替える（タイトル → ゲーム） |

### シーンに入る・出るときの処理

| 関数 | 呼ぶタイミング | 使い道 |
| --- | --- | --- |
| `Enter` / `OnEnter` | シーンが始まるとき | リソースの読み込み、BGM の再生 |
| `Exit` / `OnExit` | シーンが終わるとき | セーブ、BGM の停止 |
| `Pause` / `Resume` | 上に別のシーンが重なる・外れるとき | 時間を止める・再開する |

コンストラクタとデストラクタで代用することもできます（unique_ptr なので、切り替えると自動でデストラクタが呼ばれる）。

### シーン間でデータを渡す

| 方法 | 例 |
| --- | --- |
| 次のシーンのコンストラクタに渡す | `std::make_unique<ResultScene>(score)` |
| 共有のデータ（ゲーム全体の状態）を参照で渡す | `GameContext& ctx`（セーブデータ、設定、リソース） |

グローバル変数にすると、どのシーンがいつ書き換えるか分からなくなるので、マネージャやコンテキストから渡すのがおすすめです。

### ロード画面

重いシーンを読み込む間に止まって見えないよう、ロード画面のシーンを挟み、別スレッドで読み込みます（`std::async` / `std::jthread`）。読み込みが終わったら本命のシーンに切り替えます。

## ゲームでの例

| シーン | 中身 |
| --- | --- |
| TitleScene | ロゴ、メニュー |
| GameScene | プレイヤー、敵、ステージ |
| PauseScene | ポーズメニュー（スタックで重ねる） |
| ResultScene | スコア表示 |
| LoadingScene | 読み込み中の表示 |

## よくあるミス

??? failure "Update の中ですぐに切り替える"
    上の「なぜ切り替えを予約するのか」を参照してください。

??? failure "シーンの外にオブジェクトを置いて、切り替えても消えない"
    グローバル変数や static にオブジェクトを置くと、シーンを切り替えても残り続け、前のシーンの敵が次のシーンに出てくるようなバグになります。シーンのメンバとして持ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 場面ごとに Scene を作り、マネージャが今のシーンだけ動かす
    - [x] unique_ptr で持てば、切り替えると自動で片付く
    - [x] 切り替えは予約してフレームの最後に
    - [x] 重ねるならスタック

## 関連ページ

- [ゲームループ](game-loop.md)
- [ステートマシン](../design/patterns/state-machine.md)
- [リソース管理](resource.md)
