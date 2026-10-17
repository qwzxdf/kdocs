---
title: インターフェース設計
tags:
  - 設計
---

# インターフェース設計

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

**インターフェース**は、「このクラスは、こういう呼び方ができる」という<strong>約束事（契約）</strong>です。使う側は、**中身（どう実装されているか）を知らなくても**、インターフェースだけ知っていれば使えます。たとえば、サウンド システムの `Play("jump")` が、中で FMOD を使っていても、自作のミキサーでも、呼ぶ側は気にしません。インターフェースをよく設計しておくと、**中身を入れ替える・テストで偽物に差し替える・チームで分担する**ことができます。C++ では、<strong>抽象クラス（仮想関数）</strong>と<strong>concepts（テンプレートの条件）</strong>の 2 つで書きます。

!!! tip "ポイント"
    - インターフェースは、**使う側の目線**で作る。「実装が何をできるか」ではなく「使う側が何をしたいか」。
    - 実行時に差し替えるなら**抽象クラス**（`virtual`）。コンパイル時に決まるなら **concepts**（テンプレート）。
    - **小さく**作る。関数が多すぎるインターフェースは、実装する側が大変で、使う側も混乱する。
    - 抽象クラスは **データを持たず、純粋仮想関数だけ**にする。デストラクタは **`virtual`**。
    - 実装の詳細（`std::vector`、`FMOD_SYSTEM*` など）は、**インターフェースに出さない**。

## 抽象クラスによるインターフェース

```cpp
// インターフェース：中身は持たず、呼び方だけを決める
class IAudio {
 public:
  virtual ~IAudio() = default;              // デストラクタは virtual
  virtual void Play(std::string_view name) = 0;
  virtual void Stop(std::string_view name) = 0;
  virtual void SetVolume(float volume) = 0;
};

// 実装 1：本物のサウンド（FMOD を使う）
class FmodAudio : public IAudio {
 public:
  void Play(std::string_view name) override { /* FMOD の呼び出し */ }
  void Stop(std::string_view name) override { /* ... */ }
  void SetVolume(float volume) override { /* ... */ }
};

// 実装 2：何もしない（サイレントモード、テスト用）
class NullAudio : public IAudio {
 public:
  void Play(std::string_view) override {}
  void Stop(std::string_view) override {}
  void SetVolume(float) override {}
};

// 使う側は、IAudio だけ知っていればよい
class Player {
 public:
  explicit Player(IAudio& audio) : audio_(audio) {}
  void Jump() { audio_.Play("jump"); }

 private:
  IAudio& audio_;  // 借りるだけ（持ち主は別）
};
```

<div class="anim" data-type="graph" data-label="インターフェースで、実装を差し替える">
n player プレイヤー 0 1
n iface IAudio 1 1 hit
n fmod FmodAudio 2 0 hit
n null NullAudio 2 2 dim
l player iface hit Play
l iface fmod hit
# 通常：IAudio を通して、FmodAudio が鳴らす
---
n player プレイヤー 0 1
n iface IAudio 1 1 hit
n fmod FmodAudio 2 0 dim
n null NullAudio 2 2 hit
l player iface hit Play
l iface null hit
# テスト・サイレント：プレイヤーのコードを変えずに NullAudio に差し替え
</div>

## 良いインターフェースの条件

| 条件 | 説明 |
| --- | --- |
| **使う側が欲しい操作だけ** | 実装の都合で出てくる関数（`InitFmod()` など）は入れない |
| **小さい**（関数 3〜7 個） | 大きいインターフェースは、実装が大変で、一部しか使わない人にも全部を求める（インターフェース分離の原則） |
| **実装の型を出さない** | 引数や戻り値に `FMOD_SOUND*` や `std::vector` を出すと、実装が変えられなくなる |
| **エラーの返し方が決まっている** | 失敗するなら、`bool`、`std::optional`、`std::expected` のどれかに統一する |
| **名前が目的を表す** | `Play`、`Load` など。`DoStuff` や `Process2` は避ける |
| <strong>「呼ぶ順番」の約束が少ない</strong> | 「`Init` を呼んでから `Play`」のような順序を、できるだけ減らす（コンストラクタで初期化する） |

## 悪い例：太ったインターフェース

```cpp
class IGameObject {
 public:
  virtual ~IGameObject() = default;
  virtual void Update(float dt) = 0;
  virtual void Draw() = 0;
  virtual void OnCollision(IGameObject& other) = 0;
  virtual void Save(Json& j) = 0;
  virtual void Load(const Json& j) = 0;
  virtual void OnGui() = 0;           // デバッグ UI
  virtual void PlaySound() = 0;       // 全員が音を出すわけではない
  virtual void SetNetworkOwner(int id) = 0;
};
```

壁のような「ただの背景」にも、**全部の関数を実装**させる必要があります（ほとんど空の関数になる）。関数を追加するたびに、**すべての派生クラスを直す**必要も出ます。

### 良い例：役割ごとに小さく分ける

```cpp
class IUpdatable { public: virtual ~IUpdatable() = default; virtual void Update(float dt) = 0; };
class IDrawable  { public: virtual ~IDrawable() = default;  virtual void Draw() = 0; };
class ISerializable { public: virtual ~ISerializable() = default; virtual void Save(Json&) const = 0; };

// 必要なものだけを実装する
class Wall : public IDrawable {};                      // 動かない背景は、描くだけ
class Enemy : public IUpdatable, public IDrawable {};  // 動いて、描く
```

インターフェースの多重継承は、データを持たなければ安全です。さらに分けるなら、機能ごとの**コンポーネント**にします（[継承と合成](composition-vs-inheritance.md)）。

## concepts によるインターフェース（コンパイル時）

実行時に差し替えるのではなく、**コンパイル時に型が決まる**場合は、C++20 の **concepts**（テンプレートの条件）で、インターフェースを書けます。仮想関数のコストがなく、速いです。

```cpp
#include <concepts>

// 「Play(string_view) を呼べて、SetVolume(float) を呼ける型」という条件
template <class T>
concept Audio = requires(T audio, std::string_view name, float volume) {
  audio.Play(name);
  audio.SetVolume(volume);
};

// この関数は、Audio の条件を満たす型なら何でも受け取れる
template <Audio A>
void PlayJumpSound(A& audio) {
  audio.Play("jump");
}
```

| 比べる項目 | 抽象クラス（`virtual`） | concepts（テンプレート） |
| --- | --- | --- |
| 差し替えのタイミング | **実行時**（設定で切り替え、プラグイン） | **コンパイル時**（ビルドで決まる） |
| 速さ | 仮想呼び出し（少し遅い） | インライン化されて**速い** |
| 継承が必要か | 必要（`: public IAudio`） | **不要**（関数があれば満たす） |
| コード サイズ | 1 つ | 型ごとに生成される |
| エラーメッセージ | 分かりやすい | concepts で、分かりやすくできる |
| ヘッダ | 実装を `.cpp` に隠せる | テンプレートなので、**ヘッダに実装が出る** |

迷ったら、**抽象クラス**から始めます。速さが問題になった場所（毎フレーム何万回も呼ぶ所）だけ、concepts や [CRTP](../patterns/crtp-policy.md) にします。

## インターフェースの安定性

| ルール | 理由 |
| --- | --- |
| **公開した関数を、後から変えにくい**と心得る | 使っている人が全員壊れる。最初に慎重に決める |
| **追加は簡単、削除・変更は大変** | 迷う機能は、**最初は入れない**（YAGNI）。欲しくなってから足す |
| **既定の実装がある関数は、`virtual` で空実装** | 実装側が、必要なものだけ上書きできる |
| **バージョン違いに備える** | プラグインや DLL の境界では、インターフェースにバージョンを持たせる |

## ゲームでの使いどころ

| 場面 | インターフェース |
| --- | --- |
| サウンド、描画、入力、ファイル読み込み | `IAudio`、`IRenderer`、`IInput`、`IFileSystem`（差し替え・テスト用の偽物） |
| シーン | `IScene`（`OnEnter`、`Update`、`Draw`、`OnExit`） |
| 敵の AI の動き | `IBehavior`（[ストラテジー](../patterns/strategy.md)） |
| デバッグ用の機能 | `IDebugDraw`（Release では何もしない `NullDebugDraw`） |
| 保存できるもの | `ISerializable`（保存と読み込み） |

## よくあるミス

??? failure "基底クラスのデストラクタが `virtual` でない"
    基底のポインタで `delete`（`unique_ptr<IAudio>` の破棄など）すると、派生クラスのデストラクタが呼ばれず、リークや未定義動作になります。インターフェースには `virtual ~IAudio() = default;` を必ず書きます。

??? failure "インターフェースにデータを持たせる"
    メンバ変数を持つと、派生クラスはそれを引き継ぎます。「実装の詳細」を持ち込むことになり、変更しにくくなります。データは、実装側に持たせます。

??? failure "実装が 1 つだけなのに、インターフェースを作る"
    差し替える予定も、テストで偽物にする予定もないなら、まだ要りません。**2 つ目の実装が必要になったとき**に、インターフェースを抜き出します（YAGNI）。

??? failure "コピーできてしまう"
    抽象クラスのコピー（スライシング）を防ぐため、コピーを禁止します。`IAudio(const IAudio&) = delete;`（または、ムーブとコピーを `= delete` にする）。

??? failure "インターフェースの関数が、実装の型を引数に取る"
    `void Play(FMOD_SOUND* sound)` のように、実装の型が見えると、実装を変えられません。名前（`string_view`）や ID（ハンドル）など、**実装に依存しない型**で受け渡します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] インターフェース ＝ 使う側から見た、呼び方の約束
    - [x] 実行時の差し替えは抽象クラス、コンパイル時は concepts
    - [x] 小さく作る。データを持たせず、`virtual` デストラクタを書く
    - [x] 実装の型や詳細を、インターフェースに出さない
    - [x] 2 つ目の実装が必要になってから、インターフェースを抜き出す

## 関連ページ

- [設計の基本原則](principles.md)
- [継承と合成](composition-vs-inheritance.md)
- [テスト容易性の設計](testability.md)
- [依存性の注入](../patterns/dependency-injection.md)
- [CRTP とポリシーベース設計](../patterns/crtp-policy.md)
- [テンプレートと concepts（基礎）](../../basics/template.md)
