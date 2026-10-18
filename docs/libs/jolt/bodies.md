---
title: 物体（Body）
tags:
  - 外部ライブラリ
  - 物理演算
---

# 物体（Body）

<strong>物体（Body）</strong>は**物理の世界にある、1 つの剛体**（硬くて形が変わらない物）です。**形（Shape）・位置・向き・動き方・レイヤー・質量・摩擦・反発**を持ちます。**物体の作成・追加・削除**は **`BodyInterface`**、**作るときの設定**は **`BodyCreationSettings`** を使います。このページは**物体の作り方**、<strong>動き方の種類（静的・キネマティック・動的）</strong>、**力・速度の与え方**、<strong>休止（スリープ）</strong>、**センサー**、**接触リスナー**をまとめます。

!!! tip "ポイント"
    - <strong>物体は `BodyCreationSettings` で設定して、`BodyInterface::CreateAndAddBody` で作って追加</strong>。<strong>戻り値は `BodyID`</strong>（<strong>ポインタでなく、ID</strong>）。
    - <strong>動き方は 3 種類</strong>：<strong>`Static`（動かない）</strong>・<strong>`Kinematic`（プログラムが動かす）</strong>・<strong>`Dynamic`（物理で動く）</strong>。
    - <strong>力・速度は `BodyInterface`</strong>（`AddForce`、`AddImpulse`、`SetLinearVelocity`）。<strong>`Update` の外</strong>で呼ぶ。
    - <strong>キネマティックは `MoveKinematic`</strong>（<strong>速度を計算して、次のステップで目的の位置へ</strong>）。<strong>`SetPosition` は瞬間移動</strong>。
    - <strong>止まった物体は自動で休止（スリープ）</strong>。<strong>動かしたいときは `ActivateBody`</strong>。
    - <strong>センサー</strong>は<strong>衝突はせず重なりだけ</strong>を知る（トリガー）。
    - <strong>接触の通知は `ContactListener`</strong>。<strong>物理スレッドから呼ばれる</strong>ので、<strong>安全に扱う</strong>。

## 物体を作る

```cpp
BodyInterface& bodies = physics_system.GetBodyInterface();

BodyCreationSettings settings(
    new SphereShape(0.5f),
    RVec3(0.0_r, 5.0_r, 0.0_r),
    Quat::sIdentity(),
    EMotionType::Dynamic,
    Layers::ENEMY);

settings.mFriction = 0.5f;
settings.mRestitution = 0.3f;

BodyID id = bodies.CreateAndAddBody(settings, EActivation::Activate);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| <strong>形（`Shape`）</strong> | `const Shape*` | **`new SphereShape(...)`** や**作っておいた `ShapeRefC`**（[形](shapes.md)） |
| <strong>位置（`RVec3`）</strong> | `RVec3` | **ワールド座標**（倍精度ビルドでは `double`） |
| <strong>向き（`Quat`）</strong> | `Quat` | **回転**（`Quat::sIdentity()` ＝ 回転なし） |
| <strong>動き方（`EMotionType`）</strong> | `EMotionType` | `Static` / `Kinematic` / `Dynamic` |
| <strong>レイヤー（`ObjectLayer`）</strong> | `ObjectLayer` | **衝突のルール**（[レイヤー](layers.md)） |

### 作成と追加

| 関数 | 説明 |
| --- | --- |
| **`CreateAndAddBody(settings, activation)`** | **作って、世界に追加**（**これが普通**）。`BodyID` を返す |
| `CreateBody(settings)` | **作るだけ**（世界には追加しない）。`Body*` を返す |
| `AddBody(id, activation)` | **世界に追加**（**作った物体を後から**） |
| `RemoveBody(id)` | **世界から外す**（**物体は、残る**。再追加できる） |
| **`DestroyBody(id)`** | **物体を完全に破棄** |

**削除は `RemoveBody` → `DestroyBody`**の**2 段階**です（**どちらも必要**）。

!!! warning "RemoveBody だけでは、メモリが残る"
    **`RemoveBody` は世界から外すだけ**で、**物体のメモリは解放されません**。**完全に消すなら `DestroyBody` も呼びます**。

### 大量の物体をまとめて追加する

**数百〜数千の物体**を**1 つずつ `CreateAndAddBody`** すると、**ブロードフェーズの更新が、毎回起きて遅く**なります。**まとめて追加**します。

```cpp
BodyIDVector ids;
for (...) ids.push_back(bodies.CreateBody(settings)->GetID());

BodyInterface::AddState state = bodies.AddBodiesPrepare(ids.data(), (int)ids.size());
bodies.AddBodiesFinalize(ids.data(), (int)ids.size(), state, EActivation::Activate);
```

**ステージのロード**で**大量の静的な物体**を追加するときに使います。**追加した後は `OptimizeBroadPhase()`**（[世界の初期化と更新](system.md)）。

## BodyCreationSettings の主な項目

| 項目 | 意味 | 既定 |
| --- | --- | --- |
| **`mFriction`** | **摩擦**（0〜1。大きいほど滑らない） | 0.2 |
| **`mRestitution`** | **反発**（0〜1。大きいほどよく跳ねる） | 0 |
| `mLinearDamping` | **速度の減衰**（空気抵抗。0〜1） | 0.05 |
| `mAngularDamping` | **回転の減衰** | 0.05 |
| `mGravityFactor` | **重力の倍率**（0 で、浮く） | 1 |
| **`mIsSensor`** | **センサー**（衝突せず重なりだけ検出） | false |
| `mAllowSleeping` | **休止を許可** | true |
| **`mMotionQuality`** | **連続衝突判定**（`LinearCast`）で、**高速な物体のすり抜けを防ぐ** | `Discrete` |
| `mOverrideMassProperties` / `mMassPropertiesOverride.mMass` | **質量を直接指定** | 形の密度から計算 |
| `mAllowedDOFs` | **動ける自由度**（2D 風に軸を固定） | すべて |
| `mUserData` | **自分のデータ**（エンティティ ID など）を**64 ビット**で持たせる | 0 |
| `mObjectLayer` | **レイヤー** | 作成時に指定 |

### 質量

**質量は形の体積 × 密度**で、**自動計算**されます。

| 方法 | 説明 |
| --- | --- |
| **形の密度**（`ShapeSettings::mDensity`） | **体積から、質量が決まる**（既定 1000 kg/m³ ＝ 水） |
| **`mOverrideMassProperties = EOverrideMassProperties::CalculateInertia`**、**`mMassPropertiesOverride.mMass = 80.0f`** | **質量を直接指定**（慣性は、形から計算） |

**質量の違いが大きすぎる物体**（1kg と 100 万 kg）が**接触**すると、**不安定**になります。**質量比は極端にしない**（**10 倍程度まで**が、安定）。

### 摩擦と反発

| 値 | 効果 |
| --- | --- |
| **摩擦 0** | **氷のように滑る** |
| **摩擦 1** | **ほぼ滑らない** |
| **反発 0** | **跳ねない**（粘土） |
| **反発 1** | **完全に跳ね返る**（ゴムボール） |

**2 つの物体の摩擦・反発は混ぜられます**（既定は、**摩擦＝掛け算の平方根**、**反発＝大きい方**）。

## 動き方の種類（EMotionType）

| 種類 | 動き | 用途 |
| --- | --- | --- |
| **`Static`** | **動かない**（質量が無限大） | **地面・壁・建物** |
| **`Kinematic`** | **プログラムが動かす**。**力を受けない**が**ほかの物体を押す** | **動く床・エレベーター・ドア・プレイヤーが操作する足場** |
| **`Dynamic`** | **物理で動く**。**力・衝突・重力で動く** | <strong>ボール・箱・敵（物理で動くもの）</strong> |

**`Static` の物体を動かす**（位置を変える）ことは、**避けます**（**ブロードフェーズの木の再構築が、重い**）。**動かしたいなら `Kinematic`** にします。

## 位置・向き・速度

### 読み取り

```cpp
RVec3 position = bodies.GetCenterOfMassPosition(id);
Quat rotation = bodies.GetRotation(id);
Vec3 velocity = bodies.GetLinearVelocity(id);
RMat44 world = bodies.GetWorldTransform(id);
```

| 関数 | 意味 |
| --- | --- |
| **`GetCenterOfMassPosition`** | **重心の位置**（**物理が動かしている点**） |
| **`GetPosition`** | **物体の原点の位置**（形によって、**重心と違う**ことがある） |
| `GetRotation` | 向き |
| `GetWorldTransform` | **位置と向きの 4×4 行列**（**描画に使う**） |
| `GetLinearVelocity` / `GetAngularVelocity` | **速度・角速度** |

**ゲームの見た目の位置**に使うのは、**`GetPosition`**（物体の原点）が**メッシュの原点と合う**ことが多いです。**重心がずれた形**（`OffsetCenterOfMassShape`）では**違い**が出ます。

### 力・衝撃・速度を与える

| 関数 | 意味 | 使いどころ |
| --- | --- | --- |
| **`AddForce(id, force)`** | **力**を加える（**毎ステップ、加え続ける**） | **推進・風・磁力** |
| **`AddImpulse(id, impulse)`** | <strong>衝撃（瞬間の力）</strong> | **ジャンプ・爆風・弾を撃つ反動** |
| `AddTorque(id, torque)` | **回転の力** | 回す |
| **`SetLinearVelocity(id, v)`** | **速度を直接設定** | **キャラの移動・射出** |
| `SetAngularVelocity` | 角速度を設定 | |
| **`SetPosition(id, pos, activation)`** | **位置を瞬間移動** | **リスポーン** |
| `SetRotation` / `SetPositionAndRotation` | 向き・位置と向き | |

```cpp
bodies.AddImpulse(id, Vec3(0, 500.0f, 0));
bodies.SetLinearVelocity(id, Vec3(5.0f, 0, 0));
```

| 注意 | 説明 |
| --- | --- |
| **力は毎フレーム加える**（`AddForce`） | **1 回だけでは、すぐ消える**。**固定ステップごと**に |
| **衝撃は質量に反比例して効く** | **軽い物体は、大きく動く** |
| **`Update` の外で呼ぶ** | **物理が動いている間は、触らない** |
| **休止中の物体は動かない** | **`ActivateBody`**、または**`EActivation::Activate` を渡す** |

## キネマティック物体の動かし方

**キネマティック物体**を**`SetPosition` で、直接動かす**と**ほかの物体を突き飛ばせません**（**瞬間移動なので、速度がない**）。

```cpp
bodies.MoveKinematic(platform_id, target_position, target_rotation, dt);
```

| 方法 | 動き |
| --- | --- |
| **`MoveKinematic(id, 位置, 向き, dt)`** | **`dt` 後に目標の位置にいるよう**、**速度を計算して設定**。**乗っている物を運べる** |
| `SetPosition` | **瞬間移動**。**速度なし**（乗っている物を運べない） |

**動く床・エレベーター**は**`MoveKinematic`** を**固定ステップごとに呼びます**。

## スリープ（休止）

**止まった物体**は**自動で休止**（スリープ）して、**計算を省きます**。

| 状態 | 説明 |
| --- | --- |
| **アクティブ** | **毎ステップ、計算**される |
| **スリープ** | **一定時間、ほぼ動かないと休止**。**計算されず軽い** |

```cpp
bodies.ActivateBody(id);
bodies.DeactivateBody(id);
bool active = bodies.IsActive(id);
```

| 点 | 説明 |
| --- | --- |
| **起こす** | **休止中の物体に力を加える・ほかの物体が当たる**と、**自動で起きる**。**`ActivateBody`** で手動でも |
| **力が効かない** | **休止中**だと**`AddForce` が、効かない**ことがある。**`ActivateBody`** を呼ぶ |
| **無効にする** | **`mAllowSleeping = false`**（**常に動かしたい物体**） |

**大量の物体**がある場合、**スリープが大きな節約**になります。

## センサー（トリガー）

**センサー**は <strong>物理的には衝突せず（すり抜け）</strong>、<strong>「重なった」ことだけを通知</strong>します。**エリアの判定**（**ゴール・ダメージ床・イベント開始**）に使います。

```cpp
BodyCreationSettings sensor_settings(new BoxShape(Vec3(2, 2, 2)), position, Quat::sIdentity(),
                                     EMotionType::Static, Layers::TRIGGER);
sensor_settings.mIsSensor = true;
bodies.CreateAndAddBody(sensor_settings, EActivation::DontActivate);
```

| 点 | 説明 |
| --- | --- |
| **`mIsSensor = true`** | **衝突しない**。**接触リスナーで重なりを通知** |
| **レイヤー** | **センサー専用のレイヤー**を作り**反応させたい相手とだけ `true`** |
| **静的なセンサーは動く物体だけを検出**する場合がある | **バージョンで違う**（`mSensorDetectsStatic`）。**ドキュメントで確認** |

## 接触リスナー（衝突の通知）

**物体どうしが接触した・離れたとき**に**通知を受け取る**仕組みです。

```cpp
class MyContactListener : public ContactListener {
 public:
  ValidateResult OnContactValidate(const Body& body1, const Body& body2, RVec3Arg base_offset,
                                   const CollideShapeResult& result) override {
    return ValidateResult::AcceptAllContactsForThisBodyPair;
  }

  void OnContactAdded(const Body& body1, const Body& body2, const ContactManifold& manifold,
                      ContactSettings& io_settings) override {
    std::lock_guard lock(mutex_);
    events_.push_back({body1.GetID(), body2.GetID(), ContactEvent::kBegin});
  }

  void OnContactRemoved(const SubShapeIDPair& pair) override {
    std::lock_guard lock(mutex_);
    events_.push_back({pair.GetBody1ID(), pair.GetBody2ID(), ContactEvent::kEnd});
  }

  std::vector<ContactEvent> TakeEvents() {
    std::lock_guard lock(mutex_);
    return std::exchange(events_, {});
  }

 private:
  std::mutex mutex_;
  std::vector<ContactEvent> events_;
};

MyContactListener listener;
physics_system.SetContactListener(&listener);
```

| 関数 | 呼ばれるとき |
| --- | --- |
| **`OnContactValidate`** | **接触が、判定される前**（**接触を無視する**こともできる） |
| **`OnContactAdded`** | **新しく接触したとき** |
| **`OnContactPersisted`** | **接触が、続いているとき**（毎ステップ） |
| **`OnContactRemoved`** | **接触が、なくなったとき** |

!!! warning "リスナーは、物理スレッドから呼ばれる"
    **接触リスナーは物理のジョブ（複数スレッド）から、同時に呼ばれる**ことがあります。**スレッド安全**に書きます（**ミューテックス**、または**スレッドごとのバッファ**）。**リスナーの中で物体を削除・変更しません**。**イベントを溜めて `Update` の後にメインスレッドで処理**します（[ECS・ゲームとの連携](integration.md)）。

### 接触の情報

| 情報 | 取得 |
| --- | --- |
| **どの物体か** | `body1.GetID()`、**`body.GetUserData()`**（**エンティティ ID**） |
| **接触点・法線** | **`ContactManifold`**（`mBaseOffset`、`mWorldSpaceNormal`、`mPenetrationDepth`） |
| **接触の性質** | **`ContactSettings`**（`mCombinedFriction`、`mCombinedRestitution`）を**書き換えて摩擦・反発をその場で変えられる** |

## BodyID と Body へのアクセス

| 型 | 説明 |
| --- | --- |
| **`BodyID`** | **物体を指す ID**（**インデックス ＋ 連番**）。**ハンドルに近く安全** |
| **`Body*`** | **物体そのものへのポインタ<strong>。</strong>危険<strong>（</strong>物体が消えるとぶら下がり**） |

**普通は、`BodyID` ＋ `BodyInterface`** を使います。**`Body*` を直接触る**必要があるとき（**詳細な情報<strong>）は、</strong>ロック**を使います。

```cpp
BodyLockRead lock(physics_system.GetBodyLockInterface(), id);
if (lock.Succeeded()) {
  const Body& body = lock.GetBody();
  float friction = body.GetFriction();
}
```

**`BodyLockRead` / `BodyLockWrite`**は**物体をスレッド安全に読み書き**できる**ロック**です（[ハンドル](../../engine/handle.md)に、近い考え方）。

## よくあるミス

??? failure "`Static` の物体を `SetPosition` で動かして、重い・おかしい"
    **動かすなら `Kinematic`**。

??? failure "`RemoveBody` だけで、メモリが増え続ける"
    **`DestroyBody` も呼びます**。

??? failure "休止した物体に `AddForce` して、動かない"
    **`ActivateBody`**、または `EActivation::Activate`。

??? failure "キネマティックを `SetPosition` で動かして、乗っている物が運ばれない"
    **`MoveKinematic`** を使います。

??? failure "接触リスナーの中で、物体を削除してクラッシュする"
    **イベントを溜めて、あとで処理**します。

??? failure "質量が、極端に違う物体どうしで不安定になる"
    **質量比を 10 倍程度に**抑えます。

??? failure "高速な弾が、壁をすり抜ける"
    **`mMotionQuality = LinearCast`**、または**`collision_steps` を増やす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`BodyCreationSettings` ＋ `CreateAndAddBody`</strong> で作り <strong>`BodyID`</strong> で扱う。<strong>削除は `RemoveBody` → `DestroyBody`</strong>
    - [x] 動き方は<strong>`Static`（動かない）・`Kinematic`（プログラムが動かす）・`Dynamic`（物理）</strong>。<strong>動かすなら Kinematic</strong>
    - [x] <strong>力は `AddForce`（毎ステップ）、衝撃は `AddImpulse`、速度は `SetLinearVelocity`</strong>。<strong>`Update` の外で</strong>
    - [x] <strong>キネマティックは `MoveKinematic`</strong>。<strong>休止中は `ActivateBody`</strong>
    - [x] <strong>センサー ＝ 衝突せず重なりだけ</strong>。<strong>接触リスナーはスレッド安全に</strong>
    - [x] <strong>`mUserData` にエンティティ ID を入れる</strong>（[統合](integration.md)）

## 関連ページ

- [Jolt Physics](index.md)
- [形（Shape）](shapes.md)
- [レイヤー](layers.md)
- [世界の初期化と更新](system.md)
- [ECS・ゲームとの連携](integration.md)
- [ハンドル](../../engine/handle.md)
