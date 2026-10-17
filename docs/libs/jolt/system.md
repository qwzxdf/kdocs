---
title: 世界の初期化と更新
tags:
  - 外部ライブラリ
  - 物理演算
---

# 世界の初期化と更新

Jolt の**物理の世界**は、**`PhysicsSystem`** です。**物体（Body）・制約（Constraint）が、この中に入り**、**毎フレームの `Update` で、時間が進みます**。このページは、**アプリの最初にやる初期化**、**`PhysicsSystem::Init` の引数の意味**、**`Update` の使い方**、**固定タイムステップ**、<strong>一時メモリ（`TempAllocator`）とジョブ システム（スレッド）</strong>、**終了時の片付け**を、まとめます。

!!! tip "ポイント"
    - 初期化の順番：<strong>① メモリ確保の登録 → ② `Factory` → ③ `RegisterTypes` → ④ `TempAllocator`・`JobSystem` → ⑤ `PhysicsSystem::Init`</strong>。
    - `PhysicsSystem::Init` には<strong>上限の数</strong>（<strong>最大の物体数・ペア数・接触数</strong>）と、<strong>3 つのレイヤー設定</strong>を渡す。<strong>上限を超えると、物体が追加できない</strong>。
    - <strong>`Update(dt, collision_steps, temp_allocator, job_system)` を、毎フレーム 1 回</strong>。<strong>`dt` は固定（1/60 秒など）</strong>。
    - <strong>可変の `dt` は、結果が不安定</strong>。<strong>蓄積して、固定の刻みで進める</strong>（[ゲームループ](../../engine/game-loop.md)）。
    - <strong>`TempAllocator`</strong> は<strong>1 回の `Update` の、一時メモリ</strong>。<strong>`JobSystem`</strong> は<strong>複数スレッドで計算</strong>するための仕組み。
    - <strong>終了時は、物体を消してから、`Factory` を解放</strong>（初期化の逆順）。

## 初期化の全体像

<svg class="fig flow" viewBox="0 0 1039 112" role="img" aria-label="Jolt の初期化：下準備を整えてから、物理の世界を作る"><defs><marker id="fl35027" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Jolt の初期化：下準備を整えてから、物理の世界を作る</text><line x1="177.0" y1="64.0" x2="235.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl35027)"/><line x1="321.0" y1="64.0" x2="379.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl35027)"/><line x1="511.0" y1="64.0" x2="569.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl35027)"/><line x1="778.0" y1="64.0" x2="836.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl35027)"/><rect x="28.0" y="44.0" width="146" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="101.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">メモリ確保 の登録</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="238.0" y="44.0" width="80" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="278.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Factory</text><circle cx="240.0" cy="46.0" r="10" fill="#2ea043"/><text x="240.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="382.0" y="44.0" width="126" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="445.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">RegisterTypes</text><circle cx="384.0" cy="46.0" r="10" fill="#e5a828"/><text x="384.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="572.0" y="44.0" width="203" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="673.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">TempAllocator JobSystem</text><circle cx="574.0" cy="46.0" r="10" fill="#e5484d"/><text x="574.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="839.0" y="44.0" width="172" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="925.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">PhysicsSystem::Init</text><circle cx="841.0" cy="46.0" r="10" fill="#9664e6"/><text x="841.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text></svg>

```cpp
#include <Jolt/Jolt.h>
#include <Jolt/Core/Factory.h>
#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Core/TempAllocator.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/RegisterTypes.h>

JPH_SUPPRESS_WARNINGS

using namespace JPH;

class PhysicsWorld {
 public:
  PhysicsWorld() {
    RegisterDefaultAllocator();

    Factory::sInstance = new Factory();
    RegisterTypes();

    temp_allocator_ = std::make_unique<TempAllocatorImpl>(10 * 1024 * 1024);
    job_system_ = std::make_unique<JobSystemThreadPool>(
        cMaxPhysicsJobs, cMaxPhysicsBarriers, std::thread::hardware_concurrency() - 1);

    constexpr uint kMaxBodies = 65536;
    constexpr uint kNumBodyMutexes = 0;
    constexpr uint kMaxBodyPairs = 65536;
    constexpr uint kMaxContactConstraints = 10240;

    system_.Init(kMaxBodies, kNumBodyMutexes, kMaxBodyPairs, kMaxContactConstraints,
                 broad_phase_layer_interface_, object_vs_broadphase_filter_, object_pair_filter_);
  }

  ~PhysicsWorld() {
    UnregisterTypes();
    delete Factory::sInstance;
    Factory::sInstance = nullptr;
  }

  void Step(float dt) {
    system_.Update(dt, 1, temp_allocator_.get(), job_system_.get());
  }

 private:
  BPLayerInterfaceImpl broad_phase_layer_interface_;
  ObjectVsBroadPhaseLayerFilterImpl object_vs_broadphase_filter_;
  ObjectLayerPairFilterImpl object_pair_filter_;

  std::unique_ptr<TempAllocatorImpl> temp_allocator_;
  std::unique_ptr<JobSystemThreadPool> job_system_;
  PhysicsSystem system_;
};
```

（`BPLayerInterfaceImpl` などの **3 つのレイヤー設定**は、[レイヤー](layers.md)で説明します）

### 各ステップの意味

| 手順 | 内容 |
| --- | --- |
| **`RegisterDefaultAllocator()`** | **Jolt が使う、メモリ確保関数**を登録（既定は `malloc` / `free`）。**自作のアロケータに替えたいときは、`Allocate` / `Free` の関数ポインタを設定**（[アロケータ](../../optimize/allocators/index.md)） |
| **`Factory::sInstance = new Factory()`** | **型の登録簿**（`Factory`）を作る。**形（Shape）などの型を、名前から作る**仕組み |
| **`RegisterTypes()`** | **標準の型**（BoxShape・SphereShape など）を、`Factory` に登録 |
| **`TempAllocatorImpl`** | **1 回の `Update` の間だけ使う、一時メモリ** |
| **`JobSystemThreadPool`** | **物理の計算を、複数スレッドに分ける** |
| **`PhysicsSystem::Init`** | **物理の世界を、実際に作る** |

## PhysicsSystem::Init の引数

```cpp
system.Init(max_bodies, num_body_mutexes, max_body_pairs, max_contact_constraints,
            broad_phase_layer_interface, object_vs_broadphase_layer_filter, object_layer_pair_filter);
```

| 引数 | 意味 | 目安 |
| --- | --- | --- |
| **`max_bodies`** | **同時に存在できる、物体の最大数** | 実際の最大数に**余裕**を持たせる（数千〜数万） |
| **`num_body_mutexes`** | **物体のロック（ミューテックス）の数**（**0 で自動**） | 通常は **0** |
| **`max_body_pairs`** | **ブロードフェーズが、保持する、ペアの最大数** | **物体の数 × 数倍**（**足りないと、衝突が検出されない**） |
| **`max_contact_constraints`** | **接触の制約の、最大数** | **同時に接触する数**（**足りないと、貫通する**） |
| **レイヤー設定 3 つ** | **どの物体が衝突するか** | [レイヤー](layers.md) |

!!! warning "上限を超えると、無言で失敗する"
    **`max_body_pairs` や `max_contact_constraints` を超える**と、**衝突が、検出されない**（物体がすり抜ける）ことがあります。**Debug では警告が出る**ことがあります。**物体が多いシーンで、すり抜けが起きたら、まず、この上限を疑います**。**メモリは、事前確保**なので、**必要な分だけ**にします。

## 世界の設定

```cpp
system.SetGravity(Vec3(0.0f, -9.81f, 0.0f));

PhysicsSettings settings = system.GetPhysicsSettings();
settings.mNumVelocitySteps = 10;
settings.mNumPositionSteps = 2;
settings.mAllowSleeping = true;
system.SetPhysicsSettings(settings);
```

| 設定 | 意味 |
| --- | --- |
| **`SetGravity`** | **重力**（既定 `(0, -9.81, 0)`）。**Y が上** |
| `mNumVelocitySteps` | **速度の解決の反復回数**（**多いほど正確・重い**） |
| `mNumPositionSteps` | **位置の補正の反復回数** |
| `mAllowSleeping` | **止まった物体を、休止**させる（**軽くなる**） |
| `mPenetrationSlop` | **許容するめり込みの量** |

**重力の向きは、Y 軸の負**（Jolt は、**右手系・Y 上**）。このサイトの左手系とは、Z の向きが逆なので、**物理の世界と描画の世界の境界で、Z を反転**するか、物理側の座標を、左手系の値として扱います（[Jolt とゲームの連携](integration.md)）。**ゲームの単位は、メートル・キログラム・秒**で、考えます。

## Update：時間を進める

```cpp
void Update(float dt, int collision_steps, TempAllocator* temp_allocator, JobSystem* job_system);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| **`dt`** | `float` | <strong>進める時間（秒）</strong>。**固定値**にする |
| **`collision_steps`** | `int` | **1 回の `Update` を、何回の衝突判定に分けるか**（**通常 1**） |
| **`temp_allocator`** | `TempAllocator*` | **一時メモリ** |
| **`job_system`** | `JobSystem*` | **ジョブ システム** |

### 固定タイムステップ

**可変の `dt`（フレームごとに違う値）を渡すと、物理が、不安定**になります（物体が跳ねる・すり抜ける・震える）。**固定の刻み**（`1/60` 秒）で、**何度も進めます**。

```cpp
constexpr float kPhysicsDt = 1.0f / 60.0f;
float accumulator = 0.0f;

void Frame(float frame_dt) {
  accumulator += std::min(frame_dt, 0.25f);

  while (accumulator >= kPhysicsDt) {
    physics.Step(kPhysicsDt);
    accumulator -= kPhysicsDt;
  }

  float alpha = accumulator / kPhysicsDt;
  Render(alpha);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>蓄積（`accumulator`）</strong> | **フレームの時間を溜めて、固定の刻みで消費** |
| <strong>上限（`0.25f`）</strong> | **長い停止のあと**の、**更新の暴走（死のスパイラル）を防ぐ**（[フレーム時間の設計](../../optimize/frame-budget.md)） |
| <strong>補間（`alpha`）</strong> | **描画は、前回と今回の物理の位置の間を補間**して、**滑らか**に（[統合](integration.md)） |

!!! note "高速な物体と collision_steps"
    **弾のように速い物体**は、**1 回の `Update` で、壁を通り抜ける**（トンネリング）ことがあります。**`collision_steps` を 2 以上**にして、**1 ステップの移動量を小さく**するか、**物体の `mMotionQuality = LinearCast`**（連続衝突判定）を使います（[物体](bodies.md)）。

## 一時メモリ（TempAllocator）

**`TempAllocatorImpl`** は、**1 回の `Update` の中で、一時的に使うメモリ**を、**ポインタを進めるだけで貸す**アロケータです（[リニアアロケータ](../../optimize/allocators/linear.md)と、同じ考え方）。

```cpp
TempAllocatorImpl temp_allocator(10 * 1024 * 1024);
```

| 点 | 説明 |
| --- | --- |
| **大きさ** | **10MB** が、よく使われる値。**物体・接触が多いと、足りない**ことがある |
| **足りないと** | **`malloc` にフォールバック**する（**遅くなる**）。**Debug で、警告が出る**ことがある |
| **`Update` ごとに、使い回される** | **毎フレーム確保しない**ので、**速い** |

## ジョブ システム（スレッド）

**`JobSystemThreadPool`** は、**物理の計算を、複数のスレッドに分担**します。

```cpp
JobSystemThreadPool job_system(cMaxPhysicsJobs, cMaxPhysicsBarriers,
                               std::thread::hardware_concurrency() - 1);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| **`cMaxPhysicsJobs`** | `uint` | **同時に存在できる、ジョブの最大数**（定数） |
| **`cMaxPhysicsBarriers`** | `uint` | **バリアの最大数**（定数） |
| **スレッド数** | `int` | **ワーカーの数**。**CPU のコア数 − 1**（**メイン スレッドの分を、引く**）が定番 |

**自分のゲームが、ジョブ システムを持っている**場合は、**Jolt の `JobSystem` を継承して、自分のものにつなぐ**こともできます（**スレッドの数を、1 つの管理にまとめる**）（[マルチスレッド化](../../optimize/multithreading.md)）。

## ブロードフェーズの最適化

```cpp
system.OptimizeBroadPhase();
```

**最初に、大量の物体を追加した後**に、**1 回呼ぶ**と、**衝突判定の、空間分割（ブロードフェーズ）が、最適化**されます。**ステージのロード後**に呼ぶのが、定番です。

## 物理の更新を、ほかの処理と順番づける

| 順番 | 内容 |
| --- | --- |
| **1. 入力・ゲームロジック** | **力・速度の設定**（`AddForce`、`SetLinearVelocity`）、**キネマティック物体の移動** |
| **2. 物理の `Update`** | **固定ステップで、何回か** |
| **3. 結果の読み取り** | **物体の位置・向きを、ゲームのオブジェクトに反映**（[統合](integration.md)） |
| **4. 描画** | **補間した位置で描く** |

**物理の `Update` の最中**に、**物体を追加・削除・変更**してはいけません（**別スレッドで動いている**ため）。**`Update` の外**（前後）で行います。**接触リスナーの中**で、**直接、物体を消さない**（**通知して、あとで処理**）。

## 終了処理

```cpp
bodies.RemoveBody(id);
bodies.DestroyBody(id);

UnregisterTypes();
delete Factory::sInstance;
Factory::sInstance = nullptr;
```

| 手順 | 内容 |
| --- | --- |
| **1. 物体・制約を、すべて削除** | **`RemoveBody` → `DestroyBody`**（追加したものを、すべて） |
| **2. `PhysicsSystem` を破棄** | **デストラクタ**で |
| **3. `UnregisterTypes`** | **型の登録を解除** |
| **4. `Factory` を `delete`** | **`sInstance` を `nullptr` に** |

**初期化の逆順**で、片付けます。

## よくあるミス

??? failure "`Factory::sInstance` を作らず、`RegisterTypes` を呼んでクラッシュする"
    **`Factory` を先に作る**。

??? failure "可変の `dt` を `Update` に渡して、物体が震える・跳ねる"
    **固定タイムステップ**にします。

??? failure "`max_body_pairs` を小さくしすぎて、物体がすり抜ける"
    **物体の数に合わせて、増やします**。

??? failure "`Update` の最中に、別スレッドから物体を追加・削除する"
    **`Update` の外**で行います。

??? failure "接触リスナーの中で、`RemoveBody` を呼ぶ"
    **スレッド安全でない**。**イベントを溜めて、あとで処理**します。

??? failure "終了時に、`Factory` を先に解放して、物体のデストラクタでクラッシュ"
    **物体をすべて消してから**、`Factory` を解放します。

??? failure "スレッド数が多すぎて、ゲーム全体が遅くなる"
    **ゲームの他のスレッドと、コアを取り合います**。**物理に使うスレッド数を、調整**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 初期化は<strong>「メモリ確保 → Factory → RegisterTypes → TempAllocator・JobSystem → PhysicsSystem::Init」</strong>
    - [x] `Init` の<strong>上限（物体・ペア・接触）</strong>と、<strong>3 つのレイヤー設定</strong>。<strong>上限超えは、すり抜けの原因</strong>
    - [x] <strong>`Update(固定の dt, 1, temp, job)`</strong>。<strong>可変の `dt` は避け、蓄積して固定刻みで</strong>
    - [x] <strong>高速な物体は、`collision_steps` を増やすか、`LinearCast`</strong>
    - [x] <strong>`Update` の最中は、物体を変更しない</strong>。<strong>終了は、初期化の逆順</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [レイヤー](layers.md)
- [物体（Body）](bodies.md)
- [ECS・ゲームとの連携](integration.md)
- [ゲームループ](../../engine/game-loop.md)
- [フレーム時間の設計](../../optimize/frame-budget.md)
- [リニアアロケータ](../../optimize/allocators/linear.md)
