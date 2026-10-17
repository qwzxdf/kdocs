---
title: Jolt Physics
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt Physics

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17〜</span>
`#include <Jolt/Jolt.h>`
</div>

**Jolt Physics**（ジョルト・フィジクス）は、**3D の物理演算（剛体、衝突判定、キャラクターの移動など）を行う C++ ライブラリ**です。オランダのゲーム会社 Guerrilla Games の開発者 Jorrit Rouwé が、**PlayStation 5 の「Horizon Forbidden West」のために作った**エンジンを、オープンソース（MIT ライセンス）として公開したものです。**マルチスレッドで速く**、<strong>同じ入力から同じ結果が出る（決定的）</strong>ことを重視していて、Godot（4.4 以降の選択肢）や Unity 以外の多くの新しいゲームでも採用されています。Bullet や PhysX と同じ種類のライブラリですが、<strong>新しくてモダンな C++</strong>で書かれていて、導入しやすいのが特徴です。

!!! warning "TODO"
    Jolt Physics は内容が深いので、**複数のページに分けて**少しずつ書いていきます。このページは、**概要・導入（Visual Studio）・全体像・最小の流れ**だけです。詳しいページは、下の「これから書くページ」に、構成だけ用意しています。

!!! tip "ポイント"
    - 物理演算は、**`PhysicsSystem`（世界）に、`Body`（物体）を追加して、`Update` で時間を進める**のが基本の流れ。
    - 物体の形は **`Shape`<strong>（箱、球、カプセル、メッシュ…）、動き方は </strong>`EMotionType`**（`Static`、`Kinematic`、`Dynamic`）で決める。
    - **レイヤー**（`ObjectLayer` / `BroadPhaseLayer`）で「何と何が衝突するか」を決める。最初に必ず作る必要がある。
    - 初期化では **メモリ確保・ファクトリ・型の登録**（`RegisterDefaultAllocator`、`Factory`、`RegisterTypes`）が必要。
    - **ライブラリのビルド設定（プリプロセッサの定義）を、自分のプロジェクトと一致させる**。ずれると、原因のわかりにくいクラッシュになる。
    - 時間は**固定のステップ**（たとえば 1/60 秒）で進める（[ゲームループ](../../engine/game-loop.md)）。

## 導入（Visual Studio）

Visual Studio での入れ方を先に説明します。Jolt は**ソースからビルドする**ライブラリで、`.lib` を作ります。次の 2 つの方法があります。

### 方法 1：vcpkg（おすすめ・一番簡単）

```powershell
vcpkg install joltphysics:x64-windows
```

- vcpkg が、ダウンロード、ビルド、パスの設定まで**まとめてやってくれます**（初回は数分かかります）
- ビルド設定（Debug / Release、定義）は、**vcpkg の既定**で作られます
- マニフェスト モード（`vcpkg.json`）なら、次のように書きます

```json
{
  "dependencies": [ "joltphysics" ]
}
```

- プロジェクトでは、`#include <Jolt/Jolt.h>` と書くだけで使えます。リンクも自動で通ります（`vcpkg integrate install` が済んでいれば。[外部ライブラリの入れ方](../../vs/libraries.md#vcpkg)）
- 注意: vcpkg の既定は <strong>`/MD`（DLL 版のランタイム）</strong> です。プロジェクトの設定も合わせます（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)）

### 方法 2：Jolt のソースから Visual Studio のプロジェクトを作ってビルドする

1. [GitHub の JoltPhysics](https://github.com/jrouwe/JoltPhysics) を取得する（`git clone`。タグ（`v5.x.x`）を指定して、バージョンを固定する）
2. `Build` フォルダーにある、**`cmake_vs2022_cl.bat`**（Visual Studio 2022・MSVC 用）を実行する
3. `Build/VS2022_CL/Jolt.sln` ができる。Visual Studio で開く
4. 構成を **Debug** と **Release** の両方でビルドして、`Jolt.lib` を作る
5. 自分のプロジェクトで、次の 3 つを設定する（[手動の設定](../../vs/libraries.md#lib_dll)）

| 設定 | 値 |
| --- | --- |
| 追加のインクルード ディレクトリ | `$(SolutionDir)third_party\JoltPhysics`（`Jolt/Jolt.h` が見える親フォルダー） |
| 追加のライブラリ ディレクトリ | `Jolt.lib` のあるフォルダー（`$(Configuration)` を使って Debug / Release を分ける） |
| 追加の依存ファイル | `Jolt.lib` |

!!! warning "ビルド設定を一致させる（重要）"
    Jolt は、ビルドのときの**プリプロセッサの定義**によって、**クラスの中身（メンバ）が変わります**。ライブラリを作ったときと、**自分のプロジェクトで `#include` するとき**で、次の定義が**食い違うと、実行時に原因のわからないクラッシュ**が起きます。

    | 定義 | 意味 |
    | --- | --- |
    | `JPH_DEBUG_RENDERER` | デバッグ描画の機能を入れる（Debug で有効にするのが普通） |
    | `JPH_PROFILE_ENABLED` | プロファイラーを入れる |
    | `JPH_OBJECT_STREAM` | シーンをファイルに保存する機能を入れる |
    | `JPH_DOUBLE_PRECISION` | 位置を `double`（倍精度）で扱う（広い世界用） |
    | `JPH_ENABLE_ASSERTS` | アサートを有効にする |
    | `JPH_CROSS_PLATFORM_DETERMINISTIC` | プラットフォームをまたいで同じ結果を出す（少し遅い） |

    CMake で作ったライブラリを使うなら、`Jolt` のターゲットが**必要な定義を自動で付ける**ので、そちらを使うのが安全です（[CMake で使う](../../vs/cmake.md)）。

### 方法 3：CMake の FetchContent

```cmake
include(FetchContent)
FetchContent_Declare(
  JoltPhysics
  GIT_REPOSITORY https://github.com/jrouwe/JoltPhysics.git
  GIT_TAG v5.3.0          # 最新のタグは Releases で確認する
  SOURCE_SUBDIR Build)     # CMakeLists.txt は Build/ フォルダーにある
FetchContent_MakeAvailable(JoltPhysics)

target_link_libraries(MyGame PRIVATE Jolt)  # 定義も自動で引き継がれる
```

## 物理演算の全体像

| 用語 | 意味 |
| --- | --- |
| `PhysicsSystem` | **物理の世界**。物体、制約、衝突の判定をまとめて持つ。`Update` で時間を進める |
| `Body` | **物体**。位置、向き、速度、形を持つ |
| `BodyID` | 物体を指す**番号**（ポインタではない）。[ハンドル](../../engine/handle.md)と同じ考え方 |
| `BodyInterface` | 物体を作る・追加する・動かす**窓口**（`physics_system.GetBodyInterface()`） |
| `Shape` | 物体の**形**。`BoxShape`、`SphereShape`、`CapsuleShape`、`MeshShape` など |
| `EMotionType` | **動き方**。`Static`（動かない地面）、`Kinematic`（プログラムで動かす）、`Dynamic`（物理で動く） |
| レイヤー | **何と何が衝突するか**を決める分類（`ObjectLayer`、`BroadPhaseLayer`） |
| `JobSystem` | 物理の計算を、複数のスレッドに分けて動かす仕組み |
| `TempAllocator` | 1 回の `Update` の間だけ使う**一時メモリ**（[アリーナ](../../stl/memory/pmr.md)） |
| 制約（Constraint） | 物体どうしをつなぐ（ヒンジ、バネ、固定など） |
| `CharacterVirtual` | **キャラクターの移動**専用の、軽い仕組み（剛体として扱わない） |

<div class="anim" data-type="graph" data-label="Jolt の世界の構造">
n sys PhysicsSystem 0 1 hit
n floor 地面_Static 2 0
n ball ボール_Dynamic 2 1
n chara プレイヤー 2 2
# 物理の世界（PhysicsSystem）がある
---
n sys PhysicsSystem 0 1
n floor 地面_Static 2 0 new
n ball ボール_Dynamic 2 1 new
n chara プレイヤー 2 2
l sys floor new 物体を追加
l sys ball new 物体を追加
# Body（物体）を追加していく。地面は動かない（Static）、ボールは物理で動く（Dynamic）
---
n sys PhysicsSystem 0 1
n floor 地面_Static 2 0
n ball ボール_Dynamic 2 1
n chara プレイヤー 2 2 new
l sys floor
l sys ball
l sys chara new CharacterVirtual
# プレイヤーは剛体にせず、キャラクター専用の仕組み（CharacterVirtual）で動かす
---
n sys PhysicsSystem 0 1 hit
n floor 地面_Static 2 0
n ball ボール_Dynamic 2 1 hit
n chara プレイヤー 2 2 hit
l sys floor
l sys ball hit Update
l sys chara hit Update
# Update(1/60 秒) で、時間が進む。物体が動き、衝突が解決される
</div>


## 最小の流れ（骨組み）

初期化から、球が落ちるまでの**骨組み**です。**レイヤーの定義**（`BroadPhaseLayerInterface` など）は長いので、[レイヤー](layers.md)（TODO）に書きます。

```cpp
#include <Jolt/Jolt.h>
#include <Jolt/Core/Factory.h>
#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Core/TempAllocator.h>
#include <Jolt/Physics/Body/BodyCreationSettings.h>
#include <Jolt/Physics/Collision/Shape/BoxShape.h>
#include <Jolt/Physics/Collision/Shape/SphereShape.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/RegisterTypes.h>

JPH_SUPPRESS_WARNINGS  // Jolt のヘッダの警告を抑える

using namespace JPH;
using namespace JPH::literals;  // 0.0_r のように書ける

void RunPhysics() {
  // ---- 1. 初期化（アプリの最初に 1 回） ----
  RegisterDefaultAllocator();      // Jolt のメモリ確保
  Factory::sInstance = new Factory();
  RegisterTypes();                 // 形などの型を登録

  TempAllocatorImpl temp_allocator(10 * 1024 * 1024);  // 一時メモリ 10 MB
  JobSystemThreadPool job_system(cMaxPhysicsJobs, cMaxPhysicsBarriers, 3);  // スレッド 3 本

  // ---- 2. 世界を作る（レイヤーは TODO のページ） ----
  PhysicsSystem physics_system;
  // physics_system.Init(最大の物体数, ミューテックス数, 最大のペア数, 最大の接触数,
  //                     broad_phase_layer_interface,
  //                     object_vs_broadphase_layer_filter,
  //                     object_vs_object_layer_filter);
  BodyInterface& bodies = physics_system.GetBodyInterface();

  // ---- 3. 物体を作る ----
  // 地面（動かない大きな箱）
  BoxShapeSettings floor_shape_settings(Vec3(100.0f, 1.0f, 100.0f));
  ShapeRefC floor_shape = floor_shape_settings.Create().Get();
  BodyCreationSettings floor_settings(floor_shape, RVec3(0.0_r, -1.0_r, 0.0_r),
                                      Quat::sIdentity(), EMotionType::Static,
                                      /* ObjectLayer */ 0);
  bodies.CreateAndAddBody(floor_settings, EActivation::DontActivate);

  // ボール（物理で動く球）
  BodyCreationSettings sphere_settings(new SphereShape(0.5f), RVec3(0.0_r, 2.0_r, 0.0_r),
                                       Quat::sIdentity(), EMotionType::Dynamic,
                                       /* ObjectLayer */ 1);
  BodyID sphere_id = bodies.CreateAndAddBody(sphere_settings, EActivation::Activate);

  physics_system.OptimizeBroadPhase();  // 最初の 1 回、衝突判定の高速化の準備

  // ---- 4. 時間を進める（固定の 1/60 秒、毎フレーム） ----
  constexpr float kDeltaTime = 1.0f / 60.0f;
  for (int step = 0; step < 120; ++step) {
    physics_system.Update(kDeltaTime, 1, &temp_allocator, &job_system);
    RVec3 position = bodies.GetCenterOfMassPosition(sphere_id);  // ボールの今の位置
    // ... 描画に位置を渡す ...
  }

  // ---- 5. 片付け ----
  bodies.RemoveBody(sphere_id);
  bodies.DestroyBody(sphere_id);
  UnregisterTypes();
  delete Factory::sInstance;
  Factory::sInstance = nullptr;
}
```

### 流れ

<div class="anim" data-type="graph" data-label="Jolt の使い方の流れ">
n init 初期化 0 0 hit
n sys 世界を作る 1 0
n body 物体を作る 2 0
n upd 毎フレーム_Update 3 0
n end 片付け 4 0
l init sys
l sys body
l body upd
l upd end
# ① 初期化：RegisterDefaultAllocator、Factory、RegisterTypes
---
n init 初期化 0 0
n sys 世界を作る 1 0 hit
n body 物体を作る 2 0
n upd 毎フレーム_Update 3 0
n end 片付け 4 0
l init sys hit
l sys body
l body upd
l upd end
# ② 世界を作る：PhysicsSystem::Init（レイヤーと上限の数）
---
n init 初期化 0 0
n sys 世界を作る 1 0
n body 物体を作る 2 0 hit
n upd 毎フレーム_Update 3 0
n end 片付け 4 0
l init sys
l sys body hit
l body upd
l upd end
# ③ 物体を作る：Shape、BodyCreationSettings、CreateAndAddBody
---
n init 初期化 0 0
n sys 世界を作る 1 0
n body 物体を作る 2 0
n upd 毎フレーム_Update 3 0 hit
n end 片付け 4 0
l init sys
l sys body
l body upd hit
l upd end
# ④ 毎フレーム：固定の時間で Update して、位置を読み取る
---
n init 初期化 0 0
n sys 世界を作る 1 0
n body 物体を作る 2 0
n upd 毎フレーム_Update 3 0
n end 片付け 4 0 hit
l init sys
l sys body
l body upd
l upd end hit
# ⑤ 片付け：RemoveBody、DestroyBody、UnregisterTypes
</div>


## Jolt が得意なこと・不得意なこと

| 得意 | 不得意・注意 |
| --- | --- |
| 大量の剛体（数千〜数万個）を、**マルチスレッドで速く**動かす | **2D 専用ではない**（2D は Box2D など。Jolt で 2D を表現するなら、Z 軸を固定する） |
| **キャラクターの移動**（階段、坂、動く床）の専用機能 | 初期設定（レイヤー、初期化）が**長い**。最初の壁になる |
| 決定的な（再現できる）シミュレーション（リプレイ、ネットワーク同期） | 流体、布などは**標準では持たない**（ソフトボディは対応） |
| 車両、ラグドール、ソフトボディ | ドキュメントは、英語（公式の Docs と、HelloWorld、Samples が情報源） |
| メモリが少なく、動きが安定している | |

## 物理を使うときの考え方

| 考え方 | 説明 |
| --- | --- |
| 物理の世界と、**ゲームの世界は別**のものとして持つ | ゲームのオブジェクト（エンティティ）は、`BodyID` を**持つ**。毎フレーム、物理の位置を、ゲームの Transform に**コピー**する |
| **固定のステップ**で更新する | 可変の `dt` を渡すと、結果が不安定になる。`dt` は 1/60 などで固定し、足りない時間は複数回 `Update` する（[ゲームループと固定タイムステップ](../../engine/game-loop.md)） |
| **キャラクターは剛体にしない** | プレイヤーの動きは、`CharacterVirtual`（TODO）で、ゲームに合う操作感を作る |
| **衝突の分類を先に決める** | 「プレイヤーと弾は衝突する、弾どうしは衝突しない」など、レイヤーの設計を最初にする |

## これから書くページ

| ページ | 内容 | 状態 |
| --- | --- | --- |
| [ビルドと設定](build.md) | プリプロセッサの定義、Debug / Release、倍精度、決定性、vcpkg と CMake の違い | TODO |
| [世界の初期化と更新](system.md) | `PhysicsSystem::Init` の引数、`Update`、固定ステップ、サブステップ | TODO |
| [レイヤー](layers.md) | `ObjectLayer`、`BroadPhaseLayer`、衝突フィルターの書き方 | TODO |
| [物体（Body）](bodies.md) | 作成・追加・削除、力・速度、摩擦と反発、スリープ、センサー | TODO |
| [形（Shape）](shapes.md) | 箱・球・カプセル・凸包・メッシュ・複合形状、スケール、重心 | TODO |
| [クエリ（レイキャストなど）](queries.md) | レイキャスト、形状キャスト、重なり判定、衝突フィルター | TODO |
| [制約（Constraint）](constraints.md) | ヒンジ、バネ、固定、距離、モーター、ラグドール | TODO |
| [キャラクター](character.md) | `CharacterVirtual`、階段・坂・動く床、`Character`（剛体版） | TODO |
| [デバッグ描画](debug-renderer.md) | `DebugRenderer` を実装して、衝突の形を画面に出す。ImGui との組み合わせ | TODO |
| [ECS・ゲームとの連携](integration.md) | `BodyID` とエンティティ、位置の同期、イベント（接触リスナー） | TODO |
| [車両・ソフトボディ](vehicles.md) | 車両の物理、ソフトボディ | TODO |

## 関連ページ

- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
- [Visual Studio：CMake で使う](../../vs/cmake.md)
- [ゲームループと固定タイムステップ](../../engine/game-loop.md)
- [ハンドルと世代 ID](../../engine/handle.md)
- [ECS](../../design/patterns/ecs.md)
- [Dear ImGui（デバッグ画面）](../imgui/index.md)
- [JoltPhysics（GitHub）](https://github.com/jrouwe/JoltPhysics)
- [Jolt のドキュメント](https://jrouwe.github.io/JoltPhysics/)
