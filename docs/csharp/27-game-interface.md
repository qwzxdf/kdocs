---
title: 第 27 章 Game DLL のインターフェース
tags:
  - C#連携
---

# 第 27 章 Game DLL のインターフェース

この章から第 6 部です。ここまで作ったエディタは、シーンを<strong>編集</strong>できます。しかし、<strong>ゲームとして動かす</strong>ことは、まだできません。この章では、<strong>ゲームのコードを `Game.dll` に分離</strong>し、エンジンが読み込んで動かす仕組み（ゲーム インターフェース）を作ります。この仕組みが、次の章の<strong>ホット リロード</strong>（動かしたままコードを差し替える）と、その次の <strong>Play モード</strong>の土台になります。

## この章の考え方

### なぜ、ゲームを別の DLL にするのか

ゲームのコードは、<strong>頻繁に書き換わる</strong>部分です。エンジンの中核（描画、シーン、アセット）は、めったに変わりません。同じ DLL に入れると、ゲームのコードを 1 行変えるたびに、エンジンごとビルドし直し、エディタを再起動することになります。

| 構成 | 1 行変えたとき |
| --- | --- |
| 全部が 1 つ | エンジンごと再ビルド → エディタを終了 → 再起動 → シーンを開き直す |
| <strong>ゲームだけが DLL</strong> | `Game.dll` だけ再ビルド → <strong>エディタを動かしたまま</strong>差し替え |

```text
Editor.exe ──▶ EngineApi.dll ──▶ Engine.dll ──読み込む──▶ Game.dll   ← 頻繁に作り直される
                                       ▲                    │
                                       └──── IGameHost ─────┘   （ゲームがエンジンを呼ぶ窓口）
```

### DLL の境界を越える形

`Game.dll` と `Engine.dll` の境界には、<strong>3 つの選択肢</strong>があります。

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| A: C の関数だけ | すべて `extern "C"` の関数と、構造体で受け渡す | 最も壊れにくい。コンパイラーが違っても動く | ゲームのコードが書きにくい（クラスが使いにくい） |
| <strong>B: 純粋仮想クラス</strong>（採用） | <strong>仮想関数だけ</strong>を持つクラス（インターフェース）で受け渡す | ゲームのコードが C++ のクラスで書ける。仮想関数テーブルの形は、MSVC なら安定 | 同じコンパイラー、同じ設定で作る必要がある。STL の型を境界に出せない |
| C: C++ のクラスをそのまま export | `__declspec(dllexport)` でクラスを出す | 書くのは楽 | 名前修飾、STL のメモリ、バージョン管理で壊れやすい |

B は A と C の中間です。<strong>境界に出すのは、「仮想関数だけを持つ抽象クラス」と「基本型の引数」だけ</strong>にすれば、実用上、安全に使えます。ただし、<strong>ゲームとエンジンを同じコンパイラーの同じ版、同じランタイム設定（`/MD`）で作る</strong>ことが前提です（これは、1 つのソリューションの中で作るので、満たされます）。

### 3 つの約束（境界で破ってはいけないこと）

1. <strong>STL の型（`std::string`、`std::vector`）を、境界の関数の引数・戻り値に出さない。</strong> 実装やデバッグ設定が違うと、レイアウトが変わる。
2. <strong>メモリは、確保した側で解放する。</strong> ゲームが `new` した物は、ゲームの `Destroy` で解放する。
3. <strong>C++ の例外を、境界の外に出さない。</strong> 呼び出す側（エンジン）が `try/catch` で受け止める。

## この章のゴール

- `Engine` の公開ヘッダーに、`IGameModule`（ゲームが実装）と `IGameHost`（エンジンが提供）を定義する。
- `Game.dll` に、実際のゲーム（回転する物）を実装する。
- エンジンが `Game.dll` を読み込み、毎フレーム更新する。
- `Player` から、これを動かして確かめる。

## 手順 1：インターフェースを定義する

`Engine\include\Engine\Game.h`:

### エンジンが提供する窓口（IGameHost）

```cpp
#pragma once

#include <cstdint>

#include "Engine/Export.h"

namespace mini {

using ObjectId = std::uint32_t;      // 0 は「なし」

// ゲームの API の版。インターフェースを変えたら増やす。読み込み時に、エンジンとゲームの版を照合する。
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `class IGameHost` + `= 0` | <strong>純粋仮想関数</strong>だけを持つ抽象クラス（インターフェース）。実装はエンジンが持つ。C# の `interface` に当たる |
| `const char* name_utf8` | 文字列は、`const char*`（UTF-8）で受け渡す。`std::string` は境界に出さない |
| `char* buffer, buffer_size` | 文字列を<strong>受け取る</strong>ときは、呼び出し側が用意したバッファー（第 13 章と同じ作法） |
| `float position[3]` | 配列引数。実際は `float*` として渡される |
| `protected: ~IGameHost() = default;` | デストラクターを `protected` にして、ゲーム側から `delete host` できなくする。<strong>所有者は、エンジン</strong> |
| `kGameApiVersion` | インターフェースの版。形を変えたら増やして、古いゲーム DLL を読み込まないようにする |

### ゲームが実装するクラス（IGameModule）

```cpp
// ゲームが実装するクラス。ゲーム DLL が作り、エンジンが呼ぶ。
class IGameModule {
 public:
  virtual void OnLoad(IGameHost* host) = 0;        // DLL を読み込んだ直後（1 回）
  virtual void OnUnload() = 0;                     // DLL を外す直前（1 回）

  virtual void OnPlay() = 0;                       // Play を始めたとき
  virtual void OnStop() = 0;                       // Play を止めたとき
  virtual void OnUpdate(float delta_seconds) = 0;  // Play 中、毎フレーム

  // ホット リロードのとき、状態を引き継ぐための保存と復元（第 28 章）
  virtual std::uint32_t GetStateSize() = 0;
  virtual void SaveState(void* buffer, std::uint32_t size) = 0;
  virtual void LoadState(const void* buffer, std::uint32_t size) = 0;

 protected:
  ~IGameModule() = default;                        // 破棄は DestroyGame を通す
};
```

### DLL が公開する関数

ゲーム DLL が書き出すのは、<strong>2 つの C の関数</strong>だけです。クラスそのものを export せず、<strong>生成と破棄の関数</strong>を export します。

```cpp
// ゲーム DLL が書き出す関数の型。エンジンが GetProcAddress で取り出す。
extern "C" {
using GetGameApiVersionFn = std::uint32_t (*)();
using CreateGameFn = mini::IGameModule* (*)();
using DestroyGameFn = void (*)(mini::IGameModule*);
}

}  // namespace mini
```

ゲーム DLL 側は、次の名前で export します。

| 関数 | 役割 |
| --- | --- |
| `GetGameApiVersion` | このゲームが作られた `kGameApiVersion` を返す |
| `CreateGame` | `IGameModule` の実体を `new` して返す |
| `DestroyGame` | `CreateGame` で作った物を `delete` する（<strong>確保した DLL の中で解放する</strong>） |

なぜ `IGameModule` を直接 `delete` しないのか。`new` したのが `Game.dll` の中なら、`delete` も `Game.dll` の中で行うのが原則だからです（約束 2）。ホット リロードで DLL を外すとき、DLL の中のコードを呼べる状態で、破棄する必要もあります。

## 手順 2：Game.dll を作る

`Game` プロジェクトの設定は、`EngineApi` と同じです（C++23、`/MD`、`/W4 /WX`、`Engine` への参照、インクルード ディレクトリに Engine の `include`）。プリプロセッサの定義に `GAME_EXPORTS` を足します。

### エクスポートする関数

`Game\src\GameExports.cpp`:

```cpp
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

`IGameModule` のデストラクターは `protected` なので、`delete game` はできません。<strong>派生クラス `SpinnerGame` の型にキャストして `delete`</strong> します。`SpinnerGame` のデストラクターは `public` です。

### ゲームの本体

「名前が `Spin` で始まる物を、Y 軸まわりに回し続ける」ゲームを作ります。

`Game\src\SpinnerGame.h`:

```cpp
#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "Engine/Game.h"

// 名前が "Spin" で始まる物を、Y 軸まわりに回す。
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

| 部分 | 説明 |
| --- | --- |
| `final` | これ以上継承しない |
| `override` | 基底クラスの仮想関数を上書きしていることを、コンパイラーに確かめさせる |
| `std::vector` を<strong>内部で</strong>使う | `SpinnerGame` の内部の型は、境界に出ない。DLL の<strong>中だけで</strong>使うなら、STL を使ってよい |
| `OnPlay` で物を集める | Play の開始時に、一度だけ探して覚える。毎フレーム探すより速い |
| `kSpeed` | 回転の速さ。次の章のホット リロードの実験で変える |
| `GetStateSize` / `SaveState` / `LoadState` | DLL を差し替えても、<strong>回転の角度が飛ばない</strong>ように、状態を保存／復元する。`angle_` 1 つだけ。ポインターは保存しない（差し替えで無効になる） |

## 手順 3：エンジン側に、IGameHost を実装する

`Engine\src\GameHost.h`:

```cpp
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

主要な実装:

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

`FindObject` は、`Scene` を走査して名前が一致する最初の物の ID を返します。同様に書けます。

## 手順 4：エンジンがゲーム DLL を読み込む

`Engine\src\GameModule.h`:

```cpp
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

`Engine\src\GameModule.cpp`:

```cpp
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `LoadLibraryW` | DLL を、実行時に読み込む Win32 API。`W` 付きで UTF-16 のパス |
| `GetProcAddress(HMODULE, "名前")` | DLL から、関数のアドレスを取り出す。`extern "C"` で export した関数は、素の名前で探せる |
| `reinterpret_cast<GetGameApiVersionFn>` | `FARPROC`（汎用の関数ポインター）を、正しい型に読み替える |
| `FreeLibrary` | DLL を外す。<strong>DLL の中から作ったオブジェクトを、すべて壊してから</strong>呼ぶ。残っていると、そのアドレスを呼んだときにクラッシュする |
| 順序 | `OnUnload` → `DestroyGame` → `FreeLibrary`。逆にしてはいけない |
| API の版の照合 | 古いゲーム DLL を、新しいエンジンで読み込んで、仮想関数テーブルの形が合わずにクラッシュする事故を、<strong>前もって防ぐ</strong> |
| `try/catch` | ゲームの `OnLoad` が例外を投げても、エンジンは落ちない |

## 手順 5：エンジンのループに組み込む

`Engine` に、`GameLibrary` と `GameHost` を持たせます。

```cpp
// Engine.h（公開）
bool LoadGame(const char* path_utf8);        // 失敗したら false。理由はログ
void UnloadGame();
void SetPlaying(bool playing);               // Play モードの開始・停止（第 29 章で詳しく）
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
  // …（第 19・20 章の入力、描画の準備）

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Utf8ToWide` | UTF-8 の文字列を、`LoadLibraryW` のための UTF-16 に変える関数（`MultiByteToWideChar(CP_UTF8, …)` を使う。[文字コード](../encoding/index.md)） |
| 更新の位置 | 描画の<strong>前</strong>に更新する。更新した結果の位置で描くため |
| 例外で Play を止める | 同じ例外を毎フレーム出し続けると、ログがあふれる。止めて、利用者に気づかせる |

## 手順 6：Player で動かして確かめる

エディタを使う前に、Player で、Game.dll の読み込みと更新を確かめます。第 4 章の Player に、<strong>回す物を作る処理</strong>と、`LoadGame` を足します。

```cpp
// Player の wWinMain、Engine::Create の直後
g_engine->LoadGame("Game.dll");                    // 実行ファイルと同じフォルダーの Game.dll

// 回す物を作る（名前が "Spin" で始まる）
mini::ObjectId id = g_engine->CreateObject("Spin_Box", 0);       // ※ Engine に CreateObject を足す
g_engine->SetObjectColor(id, 1.0f, 0.5f, 0.2f);
g_engine->SetPlaying(true);                        // すぐに Play を始める
```

`Engine` に `CreateObject` などの簡単な窓口を足します（`Scene::Create` を呼ぶだけ）。

`F5` で Player を実行すると、<strong>橙色の箱が、原点で回り続けます</strong>。ログに「SpinnerGame を読み込みました」「回す物を集めました」が出れば成功です。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| ビルド | `Game` が `Game.dll` を作る。`dumpbin /exports Game.dll` に 3 つの関数 |
| Player の起動 | ログに「ゲームを読み込みました」が出る |
| 画面 | 箱が Y 軸まわりに回る |
| Game.dll を消して起動 | 「ゲームを読み込めませんでした」が出るが、Player は落ちない |
| `kGameApiVersion` を変えて `Game` だけビルド | 「API の版が違います」と出て、読み込まれない |

## よくあるミス

??? failure "`GetProcAddress` が null を返す"
    `extern "C"` が付いていない、または `__declspec(dllexport)` が付いていない。`dumpbin /exports` で、名前が `CreateGame` のままか確認する。

??? failure "`LoadLibrary` が失敗（エラー 126）"
    `Game.dll` が `Engine.dll` を必要としているが、見つからない。出力先をそろえる（第 1 章）。または、パスが相対で、作業ディレクトリが違う。`GetModuleFileName` で、実行ファイルのフォルダーを基準にする。

??? failure "`delete game` で、ヒープ破損のクラッシュ"
    ゲームの DLL で `new` した物を、エンジンの側で `delete` している。`DestroyGame` を通す。両方が `/MD` で、同じ CRT を共有していても、このルールは守る。

??? failure "ゲームが `Scene` に直接アクセスしようとして、リンクできない"
    ゲームが触れるのは、`IGameHost` の関数だけ。`Scene` の型は、ゲームに見せない。必要な機能は、`IGameHost` に仮想関数を<strong>足して</strong>、版を上げる。

??? failure "仮想関数を足したら、古いゲーム DLL が落ちる"
    仮想関数テーブルの並びが変わった。`kGameApiVersion` を上げる。<strong>新しい関数は、末尾に足す</strong>と壊れにくい。

## この章のまとめ

- ゲームは <strong>`IGameModule`（純粋仮想クラス）</strong> を実装し、DLL は <strong>生成・破棄・版の 3 関数</strong>を export する。
- エンジンは <strong>`IGameHost`</strong> を提供し、ゲームはそれだけを通して、エンジンを触る。
- 境界では、STL の型を使わず、メモリを確保した側が解放し、例外を外へ出さない。
- 読み込み時に、<strong>API の版</strong>を照合する。

## 次の章へ

次の章（[第 28 章 ホット リロード](28-hot-reload.md)）では、<strong>エディタを動かしたまま</strong>、`Game.dll` を差し替える仕組みを作ります。ファイルのロックを避けるシャドウ コピー、状態の引き継ぎ、失敗したときの復旧を扱います。
