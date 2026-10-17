---
title: Jolt の最小の流れ
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt の最小の流れ

初期化から、球が落ちるまでの**骨組み**です。

初期化から、球が落ちるまでの**骨組み**です。**レイヤーの定義**（`BroadPhaseLayerInterface` など）は長いので、[レイヤー](layers.md)で説明します。

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

  // ---- 2. 世界を作る（レイヤーは、レイヤーのページで説明） ----
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

## 流れ

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

## 関連ページ

- [Jolt Physics（目次）](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)

