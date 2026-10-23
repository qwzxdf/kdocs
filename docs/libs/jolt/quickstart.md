---
title: Jolt の最小の流れ
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt の最小の流れ

初期化から、球が落ちるまでの**骨組み**です。

!!! info "このページを読む前に"
    - [Jolt Physics](index.md)（このセクション全体の地図と、読む順番）
    - [物理演算の全体像](overview.md)（Jolt の全体像）


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

<svg class="fig flow" viewBox="0 0 806 112" role="img" aria-label="Jolt の使い方の流れ"><defs><marker id="fl46462" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Jolt の使い方の流れ</text><line x1="107.0" y1="64.0" x2="165.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl46462)"/><line x1="267.0" y1="64.0" x2="325.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl46462)"/><line x1="427.0" y1="64.0" x2="485.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl46462)"/><line x1="641.0" y1="64.0" x2="699.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl46462)"/><rect x="28.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">初期化</text><rect x="168.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="216.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">世界を作る</text><rect x="328.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="376.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">物体を作る</text><rect x="488.0" y="44.0" width="150" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="563.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">毎フレーム Update</text><rect x="702.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="740.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">片付け</text></svg>

## 関連ページ

- [Jolt Physics（目次）](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)

