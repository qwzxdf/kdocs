---
title: 第 46 章 Game DLL のインターフェース
tags:
  - C#連携
---

# 第 46 章 Game DLL のインターフェース

この章から第 6 部です。ここまでに作ったエディタは、シーンを編集できます。しかし、ゲームとして動かすことは、まだできません。この章では、ゲームのコードを `Game.dll` に分けて、エンジンが読み込んで動かす仕組み（ゲーム インターフェース）を作ります。この仕組みが、次の章のホット リロード（動かしたままコードを差し替える）と、その次の Play モードの土台になります。

!!! info "このページを読む前に"
    - [第 45 章 アセット ブラウザ](45-asset-browser.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## なぜ、ゲームを別の DLL にするのか

ゲームのコードは、頻繁に書き換わる部分です。エンジンの中核（描画、シーン、アセット）は、めったに変わりません。同じ DLL に入れてしまうと、ゲームのコードを 1 行変えるたびに、エンジンごとビルドし直して、エディタを再起動することになります。

| 構成 | 1 行変えたとき |
| --- | --- |
| 全部が 1 つ | エンジンごと再ビルド → エディタを終了 → 再起動 → シーンを開き直す |
| ゲームだけが DLL | `Game.dll` だけ再ビルド → エディタを動かしたまま差し替え |

```text
Editor.exe ──▶ EngineApi.dll ──▶ Engine.dll ──読み込む──▶ Game.dll   ← 頻繁に作り直される
                                       ▲                    │
                                       └──── IGameHost ─────┘   （ゲームがエンジンを呼ぶ窓口）
```

## DLL の境界を越える形

`Game.dll` と `Engine.dll` の境界には、3 つの選択肢があります。

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| A: C の関数だけ | すべて `extern "C"` の関数と構造体で受け渡す | 最も壊れにくい。コンパイラーが違っても動く | ゲームのコードが書きにくい（クラスが使いにくい） |
| B: 純粋仮想クラス（採用） | 仮想関数だけを持つクラス（インターフェース）で受け渡す | ゲームのコードを C++ のクラスで書ける。仮想関数テーブルの形は MSVC なら安定 | 同じコンパイラー、同じ設定で作る必要がある。STL の型を境界に出せない |
| C: クラスをそのまま export | `__declspec(dllexport)` でクラスを出す | 書くのは楽 | 名前修飾、STL のメモリ、バージョン管理で壊れやすい |

B は A と C の中間です。境界に出すのは、「仮想関数だけを持つ抽象クラス」と「基本型の引数」だけにすれば、実用上、安全に使えます。ただし、ゲームとエンジンを同じコンパイラーの同じ版、同じランタイム設定（`/MD`）で作ることが前提です。1 つのソリューションの中で作るので、これは満たされます。

境界では、次の 3 つの約束を守ります。破ると、原因の分かりにくい不具合になります。

1. STL の型（`std::string`、`std::vector`）を境界の関数の引数にも戻り値にも出さない。実装やデバッグ設定が違うと、型のレイアウトが変わるからです。
2. メモリは、確保した側で解放する。ゲームが `new` した物は、ゲームの側の `Destroy` で解放します。
3. C++ の例外を境界の外に出さない。呼ぶ側（エンジン）が `try/catch` で受け止めます。

この章のゴールは、次のとおりです。

- `Engine` の公開ヘッダーに `IGameModule`（ゲームが実装）と `IGameHost`（エンジンが提供）を定義する。
- `Game.dll` に、実際のゲーム（回転する物）を実装する。
- エンジンが `Game.dll` を読み込んで、毎フレーム更新する。
- `Player` から動かして確かめる。

## インターフェースを定義する

2 つのインターフェースを `Engine/include/Engine/Game.h` に書きます。まず、エンジンがゲームに提供する窓口 `IGameHost` です。

```cpp title="Engine/include/Engine/Game.h"
#pragma once

#include <cstdint>

#include "Engine/Export.h"

namespace mini {

using ObjectId = std::uint32_t;      // 0 は「なし」

// ゲームの API の版。インターフェースを変えたら増やす。読み込み時にエンジンとゲームの版を照合する。
inline constexpr std::uint32_t kGameApiVersion = 1;

// ゲームがエンジンを呼ぶための窓口。エンジンが実装して、ゲームに渡す。
// 仮想関数だけを持つ抽象クラス。STL の型は、引数にも戻り値にも使わない。
class IGameHost {
 public:
  virtual void Log(std::int32_t level, const char* message_utf8) = 0;      // 0:情報, 1:警告, 2:エラー

  // 名前でオブジェクトを探す。見つからなければ 0
  virtual ObjectId FindObject(const char* name_utf8) = 0;

  // 物の個数と、番号による取得（走査用）
  virtual std::uint32_t ObjectCount() = 0;
  virtual ObjectId ObjectAt(std::uint32_t index) = 0;

  // 名前（UTF-8）。buffer に書く。書いた文字数（終端を除く）を返す
  virtual std::uint32_t GetName(ObjectId id, char* buffer, std::uint32_t buffer_size) = 0;

  // 変換。位置、回転（ラジアン）、拡大は、いずれも float[3]
  virtual bool GetTransform(ObjectId id, float position[3], float rotation[3], float scale[3]) = 0;
  virtual bool SetTransform(ObjectId id, const float position[3], const float rotation[3], const float scale[3]) = 0;

 protected:
  ~IGameHost() = default;           // ゲームから delete させない
};
```

`= 0` が付いた仮想関数（純粋仮想関数）だけを持つクラスは、実装を持たない約束事だけのクラスで、C# の `interface` に当たります。実装はエンジンが持ち、ゲームは、この約束を通してだけエンジンを呼びます。文字列は `const char*`（UTF-8）で渡し、文字列を受け取るときは、呼ぶ側が用意したバッファーに書いてもらいます（第 31 章の作法と同じです）。デストラクターを `protected` にしているのは、ゲーム側から `delete host` できなくするためです。所有者はエンジンです。`kGameApiVersion` は、インターフェースの形を変えたら増やす版番号で、古いゲーム DLL を読み込まないための照合に使います。

次は、ゲームが実装する側の `IGameModule` です。

```cpp
// ゲームが実装するクラス。ゲーム DLL が作り、エンジンが呼ぶ。
class IGameModule {
 public:
  virtual void OnLoad(IGameHost* host) = 0;        // DLL を読み込んだ直後（1 回）
  virtual void OnUnload() = 0;                     // DLL を外す直前（1 回）

  virtual void OnPlay() = 0;                       // Play を始めたとき
  virtual void OnStop() = 0;                       // Play を止めたとき
  virtual void OnUpdate(float delta_seconds) = 0;  // Play 中、毎フレーム

  // ホット リロードのとき、状態を引き継ぐための保存と復元（第 47 章）
  virtual std::uint32_t GetStateSize() = 0;
  virtual void SaveState(void* buffer, std::uint32_t size) = 0;
  virtual void LoadState(const void* buffer, std::uint32_t size) = 0;

 protected:
  ~IGameModule() = default;                        // 破棄は DestroyGame を通す
};
```

最後に、DLL が書き出す関数の型です。ゲーム DLL が export するのは、クラスそのものではなく、生成と破棄の C の関数です。

```cpp
// ゲーム DLL が書き出す関数の型。エンジンが GetProcAddress で取り出す。
extern "C" {
using GetGameApiVersionFn = std::uint32_t (*)();
using CreateGameFn = mini::IGameModule* (*)();
using DestroyGameFn = void (*)(mini::IGameModule*);
}

}  // namespace mini
```

| 関数 | 役割 |
| --- | --- |
| `GetGameApiVersion` | このゲームが作られたときの `kGameApiVersion` を返す |
| `CreateGame` | `IGameModule` の実体を `new` して返す |
| `DestroyGame` | `CreateGame` で作った物を `delete` する（確保した DLL の中で解放する） |

エンジンが `IGameModule` を直接 `delete` しないのは、約束 2 のためです。`new` したのが `Game.dll` の中なら、`delete` も `Game.dll` の中で行います。ホット リロードで DLL を外すときも、DLL の中のコードを呼べる状態のうちに、破棄する必要があります。

## Game.dll を作る

`Game` プロジェクトの設定は `EngineApi` と同じです（C++23、`/MD`、`/W4 /WX`、`Engine` への参照、インクルード ディレクトリに Engine の `include`）。プリプロセッサの定義に `GAME_EXPORTS` を足します。

まず、export する 3 つの関数です。

```cpp title="Game/src/GameExports.cpp"
#include "Engine/Game.h"

#include "SpinnerGame.h"

#define GAME_API extern "C" __declspec(dllexport)

GAME_API std::uint32_t GetGameApiVersion() {
  return mini::kGameApiVersion;
}

GAME_API mini::IGameModule* CreateGame() {
  return new SpinnerGame();
}

GAME_API void DestroyGame(mini::IGameModule* game) {
  delete static_cast<SpinnerGame*>(game);
}
```

`IGameModule` のデストラクターは `protected` なので、`delete game` はできません。派生クラス `SpinnerGame` の型にキャストして、`delete` します。`SpinnerGame` のデストラクターは `public` です。

次がゲームの本体です。「名前が `Spin` で始まる物を Y 軸まわりに回し続ける」ゲームを作ります。

```cpp title="Game/src/SpinnerGame.h"
#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "Engine/Game.h"

// 名前が "Spin" で始まる物を Y 軸まわりに回す。
class SpinnerGame final : public mini::IGameModule {
 public:
  ~SpinnerGame() = default;

  void OnLoad(mini::IGameHost* host) override {
    host_ = host;
    host_->Log(0, "SpinnerGame を読み込みました");
  }

  void OnUnload() override {
    host_->Log(0, "SpinnerGame を外します");
    host_ = nullptr;
  }

  void OnPlay() override {
    angle_ = 0.0f;
    spinners_.clear();
    // 名前が "Spin" で始まる物を集める
    for (std::uint32_t i = 0; i < host_->ObjectCount(); ++i) {
      mini::ObjectId id = host_->ObjectAt(i);
      char name[64] = {};
      host_->GetName(id, name, sizeof(name));
      if (std::strncmp(name, "Spin", 4) == 0) spinners_.push_back(id);
    }
    host_->Log(0, "回す物を集めました");
  }

  void OnStop() override { spinners_.clear(); }

  void OnUpdate(float delta_seconds) override {
    angle_ += kSpeed * delta_seconds;                 // 回転の速さ（ラジアン / 秒）
    for (mini::ObjectId id : spinners_) {
      float position[3], rotation[3], scale[3];
      if (!host_->GetTransform(id, position, rotation, scale)) continue;
      rotation[1] = angle_;                           // Y 軸まわり（ヨー）
      host_->SetTransform(id, position, rotation, scale);
    }
  }

  // ── ホット リロードで引き継ぐ状態：回転の角度だけ ──
  std::uint32_t GetStateSize() override { return sizeof(angle_); }
  void SaveState(void* buffer, std::uint32_t size) override {
    if (size >= sizeof(angle_)) std::memcpy(buffer, &angle_, sizeof(angle_));
  }
  void LoadState(const void* buffer, std::uint32_t size) override {
    if (size >= sizeof(angle_)) std::memcpy(&angle_, buffer, sizeof(angle_));
  }

 private:
  static constexpr float kSpeed = 1.5f;               // ← ホット リロードで、この値を変えてみる

  mini::IGameHost* host_ = nullptr;
  std::vector<mini::ObjectId> spinners_;
  float angle_ = 0.0f;
};
```

読みどころは次のとおりです。

- `std::vector` を使っていますが、`SpinnerGame` の内部の型は境界に出ません。DLL の中だけで使うなら、STL を使ってよいのです。
- `OnPlay` で回す物を一度だけ集めて覚えます。毎フレーム探すより速いからです。
- `GetStateSize`、`SaveState`、`LoadState` は、DLL を差し替えても回転の角度が飛ばないようにするための、状態の保存と復元です。保存するのは `angle_` だけで、ポインターは保存しません。差し替えるとアドレスが無効になるからです。
- `kSpeed` は、次の章のホット リロードの実験で書き換える値です。

## エンジン側に IGameHost を実装する

ゲームから呼ばれる窓口の実体をエンジンの側に作ります。`Scene` とログへの橋渡しです。

```cpp title="Engine/src/GameHost.h"
#pragma once

#include "Engine/Game.h"
#include "Scene.h"

namespace mini {

// IGameHost の実装。エンジンの Scene と、ログに橋渡しする。
class GameHost final : public IGameHost {
 public:
  explicit GameHost(Scene* scene) : scene_(scene) {}

  void Log(std::int32_t level, const char* message_utf8) override;
  ObjectId FindObject(const char* name_utf8) override;
  std::uint32_t ObjectCount() override;
  ObjectId ObjectAt(std::uint32_t index) override;
  std::uint32_t GetName(ObjectId id, char* buffer, std::uint32_t buffer_size) override;
  bool GetTransform(ObjectId id, float position[3], float rotation[3], float scale[3]) override;
  bool SetTransform(ObjectId id, const float position[3], const float rotation[3], const float scale[3]) override;

 private:
  Scene* scene_;
  std::vector<ObjectId> order_;       // ObjectAt のための、ID の並び（毎回作り直す）
};

}  // namespace mini
```

実装の主要な部分です。

```cpp
#include "GameHost.h"

#include <algorithm>
#include <cstring>

#include "Engine/Log.h"

namespace mini {

void GameHost::Log(std::int32_t level, const char* message) {
  Write(static_cast<LogLevel>(level), message ? message : "");     // 第 2 章のログ
}

std::uint32_t GameHost::ObjectCount() {
  // 走査のたびに ID の並びを作り直す（Scene の中身は、走査中に変わらない前提）
  order_.clear();
  for (const auto& [id, object] : scene_->Objects()) order_.push_back(id);
  std::sort(order_.begin(), order_.end());                          // 順序を安定させる
  return static_cast<std::uint32_t>(order_.size());
}

ObjectId GameHost::ObjectAt(std::uint32_t index) {
  return index < order_.size() ? order_[index] : 0;
}

std::uint32_t GameHost::GetName(ObjectId id, char* buffer, std::uint32_t size) {
  const SceneObject* object = scene_->Find(id);
  if (!object || !buffer || size == 0) return 0;
  const std::size_t n = std::min<std::size_t>(object->name.size(), size - 1);
  std::memcpy(buffer, object->name.data(), n);
  buffer[n] = '\0';
  return static_cast<std::uint32_t>(n);
}

bool GameHost::GetTransform(ObjectId id, float position[3], float rotation[3], float scale[3]) {
  const SceneObject* o = scene_->Find(id);
  if (!o) return false;
  position[0] = o->position.x; position[1] = o->position.y; position[2] = o->position.z;
  rotation[0] = o->rotation.x; rotation[1] = o->rotation.y; rotation[2] = o->rotation.z;
  scale[0] = o->scale.x; scale[1] = o->scale.y; scale[2] = o->scale.z;
  return true;
}

bool GameHost::SetTransform(ObjectId id, const float p[3], const float r[3], const float s[3]) {
  SceneObject* o = scene_->Find(id);
  if (!o) return false;
  o->position = {p[0], p[1], p[2]};
  o->rotation = {r[0], r[1], r[2]};
  o->scale = {s[0], s[1], s[2]};
  return true;
}

}  // namespace mini
```

`FindObject` は、`Scene` を走査して、名前が一致する最初の物の ID を返します。同じ要領で書けます。

## エンジンがゲーム DLL を読み込む

DLL の読み込みと破棄を `GameLibrary` というクラスにまとめます。

```cpp title="Engine/src/GameModule.h"
#pragma once

#include <windows.h>

#include <string>

#include "Engine/Game.h"

namespace mini {

// ゲーム DLL を 1 つ読み込んで、IGameModule の実体を持つ。
class GameLibrary {
 public:
  GameLibrary() = default;
  ~GameLibrary() { Unload(); }
  GameLibrary(const GameLibrary&) = delete;
  GameLibrary& operator=(const GameLibrary&) = delete;

  // 読み込む。失敗したら false にして、理由を error に入れる
  bool Load(const std::wstring& path, IGameHost* host, std::string* error);
  void Unload();

  bool IsLoaded() const { return module_ != nullptr; }
  IGameModule* Module() const { return module_; }

 private:
  HMODULE library_ = nullptr;
  IGameModule* module_ = nullptr;
  DestroyGameFn destroy_ = nullptr;
};

}  // namespace mini
```

```cpp title="Engine/src/GameModule.cpp"
#include "GameModule.h"

#include "Engine/Log.h"

namespace mini {

bool GameLibrary::Load(const std::wstring& path, IGameHost* host, std::string* error) {
  Unload();

  library_ = LoadLibraryW(path.c_str());
  if (!library_) {
    *error = "LoadLibrary に失敗しました（Win32 エラー " + std::to_string(GetLastError()) + "）";
    return false;
  }

  auto get_version = reinterpret_cast<GetGameApiVersionFn>(GetProcAddress(library_, "GetGameApiVersion"));
  auto create = reinterpret_cast<CreateGameFn>(GetProcAddress(library_, "CreateGame"));
  destroy_ = reinterpret_cast<DestroyGameFn>(GetProcAddress(library_, "DestroyGame"));
  if (!get_version || !create || !destroy_) {
    *error = "ゲーム DLL に GetGameApiVersion / CreateGame / DestroyGame がありません";
    Unload();
    return false;
  }
  if (get_version() != kGameApiVersion) {
    *error = "ゲーム DLL の API の版が違います（エンジン " + std::to_string(kGameApiVersion) + "、ゲーム " +
             std::to_string(get_version()) + "）。ゲームを再ビルドしてください";
    Unload();
    return false;
  }

  try {
    module_ = create();
    if (!module_) throw std::runtime_error("CreateGame が null を返しました");
    module_->OnLoad(host);
  } catch (const std::exception& e) {
    *error = std::string("ゲームの初期化で例外: ") + e.what();
    Unload();
    return false;
  }
  return true;
}

void GameLibrary::Unload() {
  if (module_) {
    try {
      module_->OnUnload();
      destroy_(module_);                 // 確保した DLL の中で解放する
    } catch (...) {
      LogError("ゲームの終了処理で例外が出ました");
    }
    module_ = nullptr;
  }
  if (library_) {
    FreeLibrary(library_);
    library_ = nullptr;
  }
  destroy_ = nullptr;
}

}  // namespace mini
```

`LoadLibraryW` は、DLL を実行時に読み込む Win32 API です（`W` 付きで UTF-16 のパスを取ります）。`GetProcAddress` は、DLL から関数のアドレスを取り出します。`extern "C"` で export した関数は、飾りのない素の名前で探せます。返ってくるのは汎用の関数ポインター（`FARPROC`）なので、`reinterpret_cast` で正しい型に読み替えます。

読み込みで大事なのは、API の版の照合です。古いゲーム DLL を新しいエンジンで読み込むと、仮想関数テーブルの形が合わずにクラッシュします。それを起動の時点でエラーメッセージにして防ぎます。`OnLoad` が例外を投げても、`try/catch` で受け止めるので、エンジンは落ちません。

外すときの順序は、`OnUnload`、`DestroyGame`、`FreeLibrary` です。逆にしてはいけません。DLL の中で作ったオブジェクトをすべて壊してから `FreeLibrary` を呼ばないと、そのアドレスを呼んだ瞬間にクラッシュします。

## エンジンのループに組み込む

`Engine` に `GameLibrary` と `GameHost` を持たせて、公開の窓口を足します。

```cpp
// Engine.h（公開）
bool LoadGame(const char* path_utf8);        // 失敗したら false。理由はログ
void UnloadGame();
void SetPlaying(bool playing);               // Play モードの開始・停止（第 48 章で詳しく）
bool IsPlaying() const;
```

```cpp
// Engine.cpp
bool Engine::LoadGame(const char* path_utf8) {
  std::string error;
  if (!impl_->game.Load(Utf8ToWide(path_utf8), &impl_->host, &error)) {
    LogError("ゲームを読み込めませんでした: {}", error);
    return false;
  }
  LogInfo("ゲームを読み込みました: {}", path_utf8);
  return true;
}

void Engine::SetPlaying(bool playing) {
  auto& s = *impl_;
  if (s.playing == playing) return;
  s.playing = playing;
  if (s.game.IsLoaded()) {
    if (playing) s.game.Module()->OnPlay();
    else s.game.Module()->OnStop();
  }
}

void Engine::Tick(float delta_seconds) {
  auto& s = *impl_;
  // …（第 37・38 章の入力、描画の準備）

  // Play 中だけ、ゲームを更新する
  if (s.playing && s.game.IsLoaded()) {
    try {
      s.game.Module()->OnUpdate(delta_seconds);
    } catch (const std::exception& e) {
      LogError("ゲームの更新で例外: {}", e.what());
      SetPlaying(false);                        // 例外が出続けないよう、Play を止める
    }
  }
  // …（描画）
}
```

`Utf8ToWide` は、UTF-8 の文字列を `LoadLibraryW` 用の UTF-16 に変える関数です（`MultiByteToWideChar(CP_UTF8, …)` を使います。[文字コード](../encoding/index.md)）。ゲームの更新は、描画の前に行います。更新した結果の位置で描くためです。更新で例外が出たら Play を止めます。同じ例外を毎フレーム出し続けると、ログがあふれるので、止めて利用者に気づかせます。

## Player で動かして確かめる

エディタを使う前に Player で `Game.dll` の読み込みと更新を確かめます。第 4 章の Player に、回す物を作る処理と `LoadGame` を足します。

```cpp
// Player の wWinMain、Engine::Create の直後
g_engine->LoadGame("Game.dll");                    // 実行ファイルと同じフォルダーの Game.dll

// 回す物を作る（名前が "Spin" で始まる）
mini::ObjectId id = g_engine->CreateObject("Spin_Box", 0);       // ※ Engine に CreateObject を足す
g_engine->SetObjectColor(id, 1.0f, 0.5f, 0.2f);
g_engine->SetPlaying(true);                        // すぐに Play を始める
```

`Engine` に `CreateObject` などの簡単な窓口を足します（`Scene::Create` を呼ぶだけです）。

`F5` で Player を実行すると、橙色の箱が原点で回り続けます。ログに「SpinnerGame を読み込みました」「回す物を集めました」が出れば成功です。

| 見る所 | 期待する結果 |
| --- | --- |
| ビルド | `Game` が `Game.dll` を作る。`dumpbin /exports Game.dll` に 3 つの関数が出る |
| Player の起動 | ログに「ゲームを読み込みました」が出る |
| 画面 | 箱が Y 軸まわりに回る |
| `Game.dll` を消して起動 | 「ゲームを読み込めませんでした」が出るが、Player は落ちない |
| `kGameApiVersion` を変えて `Game` だけビルド | 「API の版が違います」と出て、読み込まれない |

??? failure "`GetProcAddress` が null を返す"
    `extern "C"` か `__declspec(dllexport)` が付いていません。`dumpbin /exports` で、名前が `CreateGame` のままか確認します。

??? failure "`LoadLibrary` が失敗する（エラー 126）"
    `Game.dll` が必要とする `Engine.dll` が見つかりません。出力先をそろえます（第 1 章）。または、パスが相対で、作業ディレクトリが違います。`GetModuleFileName` で、実行ファイルのフォルダーを基準にします。

??? failure "`delete game` でヒープ破損のクラッシュ"
    ゲームの DLL で `new` した物をエンジンの側で `delete` しています。`DestroyGame` を通します。両方が `/MD` で同じ CRT を共有していても、このルールは守ります。

??? failure "ゲームが `Scene` に直接アクセスしようとして、リンクできない"
    ゲームが触れるのは、`IGameHost` の関数だけです。`Scene` の型は、ゲームに見せません。必要な機能は、`IGameHost` に仮想関数を足して、版を上げます。

??? failure "仮想関数を足したら、古いゲーム DLL が落ちる"
    仮想関数テーブルの並びが変わりました。`kGameApiVersion` を上げます。新しい関数は、末尾に足すと壊れにくくなります。

## この章のまとめ

- ゲームは `IGameModule`（純粋仮想クラス）を実装し、DLL は生成・破棄・版の 3 関数を export する。
- エンジンは `IGameHost` を提供し、ゲームはそれだけを通して、エンジンを触る。
- 境界では、STL の型を使わず、メモリを確保した側が解放し、例外を外へ出さない。
- 読み込み時に API の版を照合する。

次の章では、エディタを動かしたまま `Game.dll` を差し替える、ホット リロードを作ります。

[第 47 章 ホット リロード](47-hot-reload.md) へ進みます。
