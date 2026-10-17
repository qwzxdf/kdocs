---
title: ECS・ゲームとの連携
tags:
  - 外部ライブラリ
  - 物理演算
---

# ECS・ゲームとの連携

Jolt の**物理の世界**と、**ゲームのオブジェクト（エンティティ）の世界**は**別のもの**として持ち、**つなぎます**。**ゲーム → 物理**（キャラクターの入力・位置の設定）、**物理 → ゲーム**（物体の位置の反映・衝突のイベント）という、**2 つの向きの同期**が必要です。このページは、**`BodyID` とエンティティの対応**、**位置の同期**、**固定ステップと補間**、**衝突イベントの処理**、**生成と破棄の管理**をまとめます。

!!! tip "ポイント"
    - <strong>物理の世界は、ゲームの世界とは別</strong>。<strong>エンティティが、`BodyID` を持つ</strong>（<strong>`Body*` ではなく ID</strong>）。
    - <strong>逆向き（`BodyID` → エンティティ）は、`mUserData` に、エンティティ ID を入れる</strong>。
    - <strong>毎フレーム、物理 `Update` の後に、物体の位置・向きをエンティティの Transform に反映</strong>する（<strong>動的な物体だけ</strong>）。
    - <strong>固定ステップ ＋ 補間</strong>で、<strong>描画を滑らか</strong>にする（<strong>前回と今回の位置を、`alpha` で混ぜる</strong>）。
    - <strong>衝突イベントは、接触リスナーで溜め、`Update` の後、メインスレッドで処理</strong>（<strong>リスナーの中で物体を変更しない</strong>）。
    - <strong>生成と破棄は、`Update` の外</strong>で。<strong>エンティティを消すとき、物体も消す</strong>（<strong>`RemoveBody` → `DestroyBody`</strong>）。
    - <strong>キネマティック・キャラクターは、ゲーム → 物理</strong>、<strong>動的な物体は物理 → ゲーム</strong>。

## 2 つの世界をつなぐ

```text
ゲームの世界（エンティティ）          物理の世界（Jolt）
  Entity 12 ─ BodyComponent ─ BodyID ─→  Body
  Entity 12 ←─ mUserData = 12 ──────────  Body
```

| 向き | つなぎ方 |
| --- | --- |
| **エンティティ → 物体** | **エンティティの持つ `BodyID`**（コンポーネントに保存） |
| **物体 → エンティティ** | **物体の `mUserData` に、エンティティ ID を入れる** |

```cpp
struct PhysicsBody {
  JPH::BodyID id;
};

BodyCreationSettings settings(shape, position, rotation, EMotionType::Dynamic, Layers::ENEMY);
settings.mUserData = entity.id;

PhysicsBody& component = registry.Add<PhysicsBody>(entity);
component.id = bodies.CreateAndAddBody(settings, EActivation::Activate);

uint64_t entity_id = bodies.GetUserData(body_id);
```

**`BodyID`** は、**インデックス ＋ 連番**で、**ハンドルに近い**ので**消えた物体の ID を使っても、安全に失敗**します（**ぶら下がらない**）（[ハンドル](../../engine/handle.md)）。**`Body*` を長く持たない**ようにします。

## 物理 → ゲーム：位置の同期

**動的な物体**（物理で動く）の**位置・向き**を**エンティティの Transform に、毎フレーム反映**します。

```cpp
void SyncPhysicsToGame(Registry& registry, BodyInterface& bodies) {
  registry.ForEach<Transform, PhysicsBody>([&](Entity e, Transform& transform, PhysicsBody& body) {
    if (!bodies.IsActive(body.id)) return;

    RVec3 position = bodies.GetPosition(body.id);
    Quat rotation = bodies.GetRotation(body.id);

    transform.position = Vector3(position.GetX(), position.GetY(), position.GetZ());
    transform.rotation = Quaternion(rotation.GetX(), rotation.GetY(), rotation.GetZ(), rotation.GetW());
  });
}
```

| 点 | 説明 |
| --- | --- |
| **座標系は、SimpleMath と同じ** | **Jolt は右手系・Y 上**。**変換は成分の写しだけ**（[座標系](../../3d/coordinate-systems.md)） |
| **クォータニオンの順** | **Jolt も `(x, y, z, w)`**。そのまま写せる（[回転](../../3d/rotation.md)） |
| **`IsActive` で絞る** | **休止中の物体は、動いていない**ので**同期を省ける**（**軽くなる**） |
| **`GetPosition` と `GetCenterOfMassPosition`** | **見た目の原点には、`GetPosition`**（**重心がずれた形**に注意） |
| **スケールは、Jolt にない** | **スケールはゲーム側で持つ**（**形を作るときに反映**） |

### 変換の関数

```cpp
inline Vector3 ToVector3(JPH::RVec3Arg v) { return Vector3(float(v.GetX()), float(v.GetY()), float(v.GetZ())); }
inline JPH::RVec3 ToJolt(const Vector3& v) { return JPH::RVec3(v.x, v.y, v.z); }
inline Quaternion ToQuaternion(JPH::QuatArg q) { return Quaternion(q.GetX(), q.GetY(), q.GetZ(), q.GetW()); }
inline JPH::Quat ToJolt(const Quaternion& q) { return JPH::Quat(q.x, q.y, q.z, q.w); }
```

**変換を、1 か所にまとめておく**と、**型の違い**（`float` と `double`・`Vec3` と `Vector3`）を、**意識せずに**済みます。

## ゲーム → 物理

**物理がゲームの値に従う**ものです。

| 対象 | 方法 |
| --- | --- |
| <strong>キャラクター（`CharacterVirtual`）</strong> | **速度を設定して `ExtendedUpdate`**（[キャラクター](character.md)） |
| **キネマティックな物体**（動く床） | **`MoveKinematic(id, 位置, 向き, dt)`**（[物体](bodies.md)） |
| **力・衝撃を与える** | **`AddForce` / `AddImpulse`**（ジャンプ・爆風） |
| **リスポーン・テレポート** | **`SetPosition`**（**速度はリセット**） |
| **エンティティを物理に追加** | **`CreateAndAddBody`** |

<strong>1 つの物体を、「ゲームが動かす」と同時に「物理が動かす」</strong>と、**喧嘩して不安定**になります。**どちらが位置の主導権を持つか**を、**物体ごとに決めます**。

## 固定ステップと補間

**物理は固定の刻み（1/60 秒）で進み**、**描画は画面のリフレッシュレート**（144Hz など）で動きます。**描画フレームが物理ステップの間に入る**と、**位置がカクつきます**。**前回と今回の物理の位置を、補間**して描きます。

```cpp
struct PhysicsTransform {
  Vector3 previous_position;
  Quaternion previous_rotation;
  Vector3 current_position;
  Quaternion current_rotation;
};

void Frame(float frame_dt) {
  accumulator += std::min(frame_dt, 0.25f);

  while (accumulator >= kPhysicsDt) {
    for (auto& t : transforms) { t.previous_position = t.current_position; t.previous_rotation = t.current_rotation; }
    PreStepGameLogic();
    physics.Step(kPhysicsDt);
    SyncPhysicsToTransforms();
    accumulator -= kPhysicsDt;
  }

  float alpha = accumulator / kPhysicsDt;
  for (auto& t : transforms) {
    render_position = Vector3::Lerp(t.previous_position, t.current_position, alpha);
    render_rotation = Quaternion::Slerp(t.previous_rotation, t.current_rotation, alpha);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **`previous` と `current`** | **物理ステップごとに前回の値を保存** |
| **`alpha`**（0〜1） | **次の物理ステップまでどれだけ進んだか** |
| **位置は `Lerp`、回転は `Slerp`** | **補間**（[回転](../../3d/rotation.md)） |
| **描画の位置は、1 ステップ遅れる** | **わずかな遅延**と引き換えに、**滑らか**になる |

（[ゲームループ](../../engine/game-loop.md)、[世界の初期化と更新](system.md)）

## 衝突イベントの処理

**接触リスナー**は、**物理のスレッドから呼ばれる**ので、**イベントを溜めて、あとでメインスレッドで処理**します。

```cpp
struct CollisionEvent {
  uint64_t entity_a;
  uint64_t entity_b;
  Vector3 point;
  Vector3 normal;
  float impulse;
};

class GameContactListener : public ContactListener {
 public:
  void OnContactAdded(const Body& body1, const Body& body2, const ContactManifold& manifold,
                      ContactSettings&) override {
    CollisionEvent e;
    e.entity_a = body1.GetUserData();
    e.entity_b = body2.GetUserData();
    e.point = ToVector3(manifold.GetWorldSpaceContactPointOn1(0));
    e.normal = ToVector3Normal(manifold.mWorldSpaceNormal);

    std::lock_guard lock(mutex_);
    events_.push_back(e);
  }

  std::vector<CollisionEvent> TakeEvents() {
    std::lock_guard lock(mutex_);
    return std::exchange(events_, {});
  }

 private:
  std::mutex mutex_;
  std::vector<CollisionEvent> events_;
};

void ProcessCollisionEvents() {
  for (const CollisionEvent& e : listener.TakeEvents()) {
    events.Publish(e);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **リスナーの中では、記録だけ** | <strong>溜める（ロック付き）</strong> |
| **`Update` の後に取り出して処理** | **メインスレッドでゲームのイベント**（ダメージ・音・エフェクト）に変換 |
| **`GetUserData`** | **物体 → エンティティ** |
| **ゲームのイベントシステムへ** | **`CollisionEvent` を、通知**（[イベントシステム](../../design/patterns/event.md)） |

!!! warning "リスナーの中で、物体を削除・変更しない"
    **スレッド安全でなく**、**物理の計算中**です。**イベントを溜めて、`Update` の後に**、**削除・変更を**行います。

### 衝突の強さ

**ダメージ・音の大きさ**に**衝突の強さ**を使いたいなら、**`ContactListener`** の中で、**相対速度**から、**計算**します。

```cpp
Vec3 relative_velocity = body1.GetLinearVelocity() - body2.GetLinearVelocity();
float impact = relative_velocity.Dot(manifold.mWorldSpaceNormal);
```

## 生成と破棄

| 場面 | 物理側の操作 |
| --- | --- |
| **エンティティを作る** | **`CreateAndAddBody`** → **`BodyID` を、コンポーネントに保存** |
| **エンティティを消す** | **`RemoveBody` → `DestroyBody`** → **コンポーネントを外す** |
| **ステージの切り替え** | **全物体をまとめて削除**（**ループで**）。**ステージの物体をまとめて追加**（`AddBodiesPrepare`） |

```cpp
void DestroyPhysicsBody(PhysicsBody& component, BodyInterface& bodies) {
  if (component.id.IsInvalid()) return;
  bodies.RemoveBody(component.id);
  bodies.DestroyBody(component.id);
  component.id = BodyID();
}
```

**エンティティ（コンポーネント）が消えるとき、必ず、物体も消す**ようにします（**デストラクタ・コンポーネントの削除処理**）。**消し忘れると物理の世界に物体が残り続けます**（**見えない壁**）。

### 遅延削除

**衝突イベントの処理中**（**弾が当たって、敵が死ぬ**）に、**すぐ物体を消す**と**同じフレームのほかの処理**で**無効な ID を使う**ことがあります。

| 方法 | 説明 |
| --- | --- |
| **削除キューに入れる** | <strong>「このフレームの終わりに、消す」</strong>を、**溜めて**、**まとめて処理**（[ECS](../../design/patterns/ecs.md)） |
| **`Update` の外で** | **物理の更新中でない**タイミングで |

## ECS（コンポーネント）との組み合わせ

| コンポーネント | 内容 |
| --- | --- |
| **`Transform`** | **位置・向き・拡大**（ゲームの基本） |
| **`PhysicsBody`** | **`BodyID`**（物理の物体への参照） |
| **`Collider`**（設定） | **形・レイヤー・摩擦・質量**（**物体を作るためのデータ**） |
| **`CharacterController`** | **`CharacterVirtual`**（キャラクター用） |

| システム | 役割 |
| --- | --- |
| **PhysicsSetupSystem** | **`Collider` ＋ `Transform` から、物体を作る**（**新しく追加されたとき**） |
| **PhysicsStepSystem** | **固定ステップで、`Update`** |
| **PhysicsSyncSystem** | **物理 → `Transform`** |
| **PhysicsEventSystem** | **衝突イベントをゲームのイベントに** |
| **PhysicsCleanupSystem** | **エンティティが消えたとき、物体も消す** |

**物理を、「システム」として、ECS に組み込む**と**ゲームの構造がすっきりします**（[ECS](../../design/patterns/ecs.md)、[データ指向設計](../../design/patterns/data-oriented.md)）。

## シリアライズ（セーブ・ロード）

| 方法 | 説明 |
| --- | --- |
| **ゲーム側のデータだけ保存** | **位置・速度・状態**を**エンティティのデータとして**保存。**ロード時に物体を作り直す**（**普通はこれ**） |
| **Jolt の状態を丸ごと保存** | **`SaveState` / `RestoreState`**（**物理の世界全体**）。**ロールバック・リプレイ**に（**決定性**） |

**普通のゲームは、位置・速度を保存**して、**ロード時に物体を作って、設定**すれば十分です（[シリアライズ](../../engine/serialization/index.md)）。

## よくあるミス

??? failure "`Body*` を、エンティティに保存して、物体が消えてクラッシュする"
    **`BodyID`** を保存します。

??? failure "接触リスナーの中で、エンティティを消して、クラッシュする"
    **イベントを溜めて、`Update` の後に**処理します。

??? failure "エンティティを消したのに、物体が残って、見えない壁になる"
    **エンティティの削除時に、`RemoveBody` → `DestroyBody`** を呼びます。

??? failure "描画が、カクつく"
    **固定ステップ ＋ 補間**にします。

??? failure "同じ物体を、ゲームも物理も動かして、震える"
    **位置の主導権を片方に決めます**（キネマティック・キャラクターは、ゲーム側）。

??? failure "休止中の物体の、同期を毎フレームやって、重い"
    **`IsActive`** で動いている物体だけにします。

??? failure "`mUserData` を設定し忘れて、衝突相手が分からない"
    **物体の作成時にエンティティ ID を、`mUserData` に入れます**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>エンティティが `BodyID` を持ち</strong>、<strong>物体の `mUserData` に、エンティティ ID</strong>。<strong>`Body*` は持たない</strong>
    - [x] <strong>物理 → ゲーム</strong>：<strong>動的な物体の位置・向きを毎フレーム Transform に反映</strong>。<strong>ゲーム → 物理</strong>：<strong>キャラクターの速度・キネマティックの移動</strong>
    - [x] <strong>固定ステップ ＋ 補間（`Lerp` / `Slerp`）</strong>で、描画を滑らかに
    - [x] <strong>衝突イベントは、リスナーで溜めて、`Update` の後に処理</strong>。<strong>リスナー内で物体を変更しない</strong>
    - [x] <strong>エンティティを消すとき、物体も消す</strong>（<strong>`RemoveBody` → `DestroyBody`</strong>）。<strong>削除は遅延</strong>
    - [x] <strong>物理を、ECS の「システム」として組み込む</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [物体（Body）](bodies.md)
- [キャラクター](character.md)
- [世界の初期化と更新](system.md)
- [ECS](../../design/patterns/ecs.md)
- [ハンドル](../../engine/handle.md)
- [イベントシステム](../../design/patterns/event.md)
