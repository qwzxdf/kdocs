---
title: シングルトンとグローバル
tags:
  - 設計
---

# シングルトンとグローバル

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**シングルトン**は、「そのクラスのオブジェクトは 1 つだけ」と決めて、どこからでも `Audio::Instance()` のように取り出せるようにするパターンです。サウンド、入力、リソースマネージャなど、ゲームに 1 つしかないものに使われがちで、学生のゲームでもよく見かけます。とても手軽な反面、**実質的にはグローバル変数**なので、使いすぎると「どこからでも何でも書き換えられる」状態になり、バグの原因を追いにくくなります。

!!! tip "ポイント"
    - シングルトン = 便利なグローバル変数。**本当に 1 つしかなく、どこからでも必要なもの**だけにする。
    - まずは「必要なものを引数やコンストラクタで渡す」を考える（[依存性の注入](dependency-injection.md)）。
    - 使うなら、関数の中の `static` 変数で作る（Meyers' Singleton）。初期化の順番の問題が起きにくい。
    - 「ゲーム全体のサービスをまとめた入れ物（コンテキスト）を 1 つ渡す」が、学生のゲームではちょうどいい落としどころ。

## 基本の形（Meyers' Singleton）

```cpp
#include <print>
#include <string>

class Audio {
 public:
  static Audio& Instance() {
    static Audio instance;  // 最初に呼ばれたときに 1 回だけ作られる（スレッドセーフ）
    return instance;
  }

  void Play(const std::string& name) {
    ++play_count_;
    std::println("再生: {}", name);
  }
  int play_count() const { return play_count_; }

  Audio(const Audio&) = delete;  // コピーで 2 つ目を作らせない
  Audio& operator=(const Audio&) = delete;

 private:
  Audio() = default;  // 外から作らせない
  int play_count_ = 0;
};

int main() {
  Audio::Instance().Play("jump.wav");
  Audio::Instance().Play("coin.wav");
  std::println("{} 回", Audio::Instance().play_count());
}
```

```text title="実行結果"
再生: jump.wav
再生: coin.wav
2 回
```

## 何が困るのか

| 問題 | 具体例 |
| --- | --- |
| どこからでも書き換えられる | 敵の AI が勝手に BGM を止めていて、原因を探すのに 1 日かかる |
| 依存が見えない | `Enemy::Update()` の中で `Score::Instance()` を呼んでいても、関数の引数を見ただけでは分からない |
| 差し替えられない | テストで「音を鳴らさない Audio」に替えたくてもできない |
| 初期化・終了の順番 | Audio の終了処理より後に、別のシングルトンのデストラクタが Audio を使って落ちる |
| 「1 つだけ」が崩れる | 2 人プレイで入力が 2 つ必要になったとき、全部書き直し |

## 代わりの方法

### 1. 必要なものを渡す

```cpp
class Enemy {
 public:
  void Update(float dt, Audio& audio) {  // 何を使うかが引数で分かる
    if (attacked_) {
      audio.Play("hit.wav");
    }
  }

 private:
  bool attacked_ = false;
};
```

### 2. コンテキスト（サービスの入れ物）を渡す

渡すものが多くなってきたら、ゲーム全体のサービスを 1 つにまとめて渡します。

```cpp
#include <print>
#include <string>

struct Audio {
  void Play(const std::string& name) { std::println("再生: {}", name); }
};
struct Input {
  bool jump_pressed = true;
};

// ゲーム全体で共有するものをまとめる
struct GameContext {
  Audio& audio;
  Input& input;
};

class Player {
 public:
  void Update(GameContext& ctx) {
    if (ctx.input.jump_pressed) {
      ctx.audio.Play("jump.wav");
    }
  }
};

int main() {
  Audio audio;
  Input input;
  GameContext ctx{audio, input};  // main で作って、必要な所へ渡していく

  Player player;
  player.Update(ctx);
}
```

```text title="実行結果"
再生: jump.wav
```

グローバルではないので、テストのときは別の Audio を入れたコンテキストを作るだけで差し替えられます。

### 3. サービスロケータ

「どこからでも取り出せる」は残しつつ、**中身を差し替えられる**ようにした形です。

```cpp
#include <memory>
#include <print>
#include <string>
#include <utility>

class IAudio {
 public:
  virtual ~IAudio() = default;
  virtual void Play(const std::string& name) = 0;
};

class NullAudio : public IAudio {  // 何もしない（テスト用・音なしモード）
 public:
  void Play(const std::string&) override {}
};

class ConsoleAudio : public IAudio {
 public:
  void Play(const std::string& name) override { std::println("再生: {}", name); }
};

class Services {
 public:
  static IAudio& Audio() { return *audio_; }
  static void Provide(std::unique_ptr<IAudio> audio) { audio_ = std::move(audio); }

 private:
  static inline std::unique_ptr<IAudio> audio_ = std::make_unique<NullAudio>();
};

int main() {
  Services::Audio().Play("a.wav");  // まだ NullAudio なので何も出ない
  Services::Provide(std::make_unique<ConsoleAudio>());
  Services::Audio().Play("b.wav");
}
```

```text title="実行結果"
再生: b.wav
```

## 使い分け

| 方法 | 手軽さ | 依存の見えやすさ | 差し替え |
| --- | --- | --- | --- |
| シングルトン | ◎ | × | × |
| サービスロケータ | ○ | × | ○ |
| コンテキストを渡す | ○ | ○ | ○ |
| 必要なものだけ引数で渡す | △ | ◎ | ◎ |

**学生のゲームなら「コンテキストを渡す」がおすすめ**です。シングルトンを使うなら、ログやデバッグ表示のように「本当にどこからでも使い、書き換えても他に影響しない」ものに限ります。

## ゲームでの例

| もの | おすすめ |
| --- | --- |
| ログ出力、デバッグ描画 | シングルトンでも OK |
| サウンド、入力、リソース | コンテキストで渡す（またはサービスロケータ） |
| スコア、プレイヤーの状態 | シングルトンにしない。持ち主（シーンなど）が持って渡す |

## よくある失敗

??? failure "マネージャを全部シングルトンにする"
    `GameManager::Instance()`、`EnemyManager::Instance()`、`UIManager::Instance()`… が全部お互いを呼び合うと、どこを直しても全部に影響する構造になります。

??? failure "グローバル変数の初期化順に頼る"
    別々の .cpp にあるグローバル変数（`static` メンバ含む）の初期化の順番は決まっていません。片方がもう片方を使うと、まだ作られていないものを使うことがあります。関数の中の `static`（Meyers' Singleton）なら、最初に使われたときに作られるので安全です。

## 理解度チェック

!!! question "Q1. 2 人協力プレイを追加することになった。`Input::Instance()` で入力を取っていたコードはどうなる？"
    <div class="spoiler" markdown>

    **答え:** 入力が 1 つしか無い前提で書かれているので、プレイヤーごとに入力を分けるために、使っている所を全部直す必要があります。最初から `Player` に自分の `Input&` を渡す形にしておけば、2 つ作って渡すだけで済みます。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] シングルトンは便利なグローバル変数。使いすぎない
    - [x] 必要なものは引数やコンテキストで渡す
    - [x] 使うなら関数内 static で作る

## 関連ページ

- [依存性の注入](dependency-injection.md)
- [Game Programming Patterns: Singleton](https://gameprogrammingpatterns.com/singleton.html)
- [Game Programming Patterns: Service Locator](https://gameprogrammingpatterns.com/service-locator.html)
