---
title: 車両・ソフトボディ
tags:
  - 外部ライブラリ
  - 物理演算
---

# 車両・ソフトボディ

Jolt には、**剛体・制約・キャラクター**のほかに、**車両**（**エンジン・タイヤ・サスペンション**）と、**ソフトボディ**（**布・ゴム・ぬいぐるみのような、柔らかい物体**）の機能があります。このページは、**車両の仕組み**（**車輪付き車両・追従車両（戦車）・バイク**）と、**ソフトボディの基本**を、**概要**としてまとめます。**どちらも、設定項目が多く、バージョンで API が変わりやすい**ので、**公式のサンプル（`VehicleTest`、`SoftBodyTest`）を、参考に**します。

!!! tip "ポイント"
    - <strong>車両は「車体（剛体）＋ 車両制約（`VehicleConstraint`）」</strong>。<strong>車輪は、物体ではなく、制約の中の「レイキャスト」</strong>で、地面に触れる。
    - <strong>タイヤの動きは、サスペンション（バネ）と、摩擦（縦・横）</strong>で決まる。<strong>エンジン・変速機・差動装置</strong>で、駆動を表現。
    - 種類：<strong>車輪付き（`WheeledVehicleController`）</strong>・<strong>追従（戦車、`TrackedVehicleController`）</strong>・<strong>バイク（`MotorcycleController`）</strong>。
    - <strong>入力（アクセル・ブレーキ・ハンドル）</strong>を、毎フレーム、<strong>コントローラーに渡す</strong>。
    - <strong>ソフトボディ</strong>は、<strong>頂点（質点）と、エッジ（バネ）</strong>で、形を保つ。<strong>布・風船・ゴム</strong>に使う。
    - <strong>ソフトボディは、重く、制限もある</strong>（<strong>数が多いと、遅い</strong>）。
    - <strong>車両は、リアルさとゲームらしさの、バランス調整</strong>が、大変。<strong>アーケード風は、設定を大きく盛る</strong>。

## 車両

### 仕組み

**車両**は、<strong>1 つの剛体（車体）</strong>と、<strong>車両制約（`VehicleConstraint`）</strong>でできています。**車輪は、独立した物体ではありません**。

| 要素 | 役割 |
| --- | --- |
| <strong>車体（Body）</strong> | **剛体**（質量・形・重心） |
| **`VehicleConstraint`** | **車輪・サスペンション・コントローラー**をまとめた**制約** |
| <strong>車輪（Wheel）</strong> | **車体に付いた、レイキャストの点**（**地面までの距離を、毎フレーム測る**） |
| **サスペンション** | **車輪を、バネで、車体に支える**（**バネの強さ・減衰**） |
| **コントローラー** | **エンジン・変速機・差動装置**（**駆動**）、**ハンドル・ブレーキ** |

<div class="anim" data-type="graph" data-label="車両：車体に付いた車輪が、地面にレイを飛ばして、サスペンションと摩擦で力を生む">
n body 車体_（剛体） 0 1 hit
---
n body 車体_（剛体） 0 1
n wheel 車輪_（レイキャスト） 1 1 new
l body wheel hit 取り付け
---
n wheel 車輪_（レイキャスト） 1 1
n ground 地面 2 1 new
l wheel ground hit レイを飛ばす
---
n wheel 車輪_（レイキャスト） 1 1
n sus サスペンション_（バネ） 2 0 new
n fric タイヤの摩擦_（縦・横） 2 2 new
l wheel sus hit
l wheel fric hit
---
n sus サスペンション_（バネ） 2 0
n fric タイヤの摩擦_（縦・横） 2 2
n force 車体に力 3 1 new
l sus force hit
l fric force hit
</div>

**車輪を、物体（回転する円柱）にしない**のは、**安定して、速く**、**車の動きを、制御しやすい**ためです。

### 車輪付き車両（WheeledVehicle）

```cpp
Ref<BodyCreationSettings> car_body_settings = ...;
Body* car_body = bodies.CreateBody(*car_body_settings);
bodies.AddBody(car_body->GetID(), EActivation::Activate);

VehicleConstraintSettings vehicle;
vehicle.mUp = Vec3::sAxisY();
vehicle.mForward = Vec3::sAxisZ();

WheelSettingsWV* front_left = new WheelSettingsWV;
front_left->mPosition = Vec3(-0.9f, -0.3f, 1.4f);
front_left->mSuspensionDirection = Vec3(0, -1, 0);
front_left->mSuspensionMinLength = 0.3f;
front_left->mSuspensionMaxLength = 0.5f;
front_left->mSuspensionSpring.mFrequency = 1.5f;
front_left->mSuspensionSpring.mDamping = 0.5f;
front_left->mRadius = 0.35f;
front_left->mWidth = 0.25f;
front_left->mMaxSteerAngle = DegreesToRadians(30.0f);
front_left->mMaxBrakeTorque = 1500.0f;

vehicle.mWheels = {front_left, front_right, rear_left, rear_right};

WheeledVehicleControllerSettings* controller = new WheeledVehicleControllerSettings;
controller->mEngine.mMaxTorque = 500.0f;
controller->mTransmission.mMode = ETransmissionMode::Auto;
vehicle.mController = controller;

VehicleConstraint* constraint = new VehicleConstraint(*car_body, vehicle);
physics_system.AddConstraint(constraint);
physics_system.AddStepListener(constraint);
```

| 設定 | 意味 |
| --- | --- |
| **`mUp` / `mForward`** | **車体の、上と前の向き** |
| **`mPosition`** | **車輪の、取り付け位置**（車体のローカル座標） |
| **`mSuspensionDirection`** | **サスペンションが伸びる向き**（下向き） |
| **`mSuspensionMinLength` / `MaxLength`** | **サスペンションの、縮む長さ・伸びる長さ** |
| **`mSuspensionSpring`** | <strong>バネの、固さ（`mFrequency`）と、減衰（`mDamping`）</strong> |
| **`mRadius` / `mWidth`** | **タイヤの半径・幅** |
| **`mMaxSteerAngle`** | **ハンドルを、切れる最大の角度**（前輪だけ設定） |
| **`mMaxBrakeTorque`** | **ブレーキの強さ** |
| **`mEngine.mMaxTorque`** | **エンジンの最大トルク** |
| **`mTransmission.mMode`** | **変速機**（`Auto`：自動、`Manual`：手動） |

!!! warning "`AddStepListener` を忘れない"
    **`VehicleConstraint` は、物理の各ステップの前後に、処理が必要**なので、**`physics_system.AddStepListener(constraint)`** も呼びます。**忘れると、車が動きません**。

### 入力を渡す

```cpp
WheeledVehicleController* controller = static_cast<WheeledVehicleController*>(constraint->GetController());

controller->SetDriverInput(forward, right, brake, hand_brake);
```

| 引数 | 意味 |
| --- | --- |
| **`forward`**（-1〜1） | <strong>アクセル（正）・バック（負）</strong> |
| **`right`**（-1〜1） | **ハンドル**（右が正） |
| **`brake`**（0〜1） | **ブレーキ** |
| **`hand_brake`**（0〜1） | **サイドブレーキ**（後輪をロック。**ドリフト**に） |

<strong>毎フレーム（固定ステップごと）</strong>、**プレイヤーの入力から、これらを設定**します。**入力の値は、なめらかに変化**させる（**急に 1.0 にしない**）と、**運転しやすい**です。

### 車両の調整

| 調整 | 効果 |
| --- | --- |
| **重心を、低くする** | **横転しにくい**（`OffsetCenterOfMassShape`）（[形](shapes.md)） |
| **質量** | **重いほど、安定・鈍重** |
| **サスペンションの固さ** | **固い → 安定・ごつごつ**、**柔らかい → 揺れる・ふわふわ** |
| **タイヤの摩擦**（`mLongitudinalFriction`・`mLateralFriction`） | **グリップ**（**縦＝加速・ブレーキ、横＝カーブ**） |
| **エンジンのトルク・ギア比** | **加速・最高速度** |
| <strong>ハンドルの角度（速度に応じて減らす）</strong> | **高速で、切りすぎない** |
| **ダウンフォース・安定化の力** | **ゲームらしい、安定性**（**物理的ではないが、必要**） |

**リアルな車は、運転が難しい**ので、**ゲームでは、グリップを強く・重心を低く・横転防止の補正**など、**ゲーム向けに盛る**のが普通です。

### 戦車・バイク

| 種類 | コントローラー | 特徴 |
| --- | --- | --- |
| <strong>追従車両（戦車）</strong> | `TrackedVehicleController` | <strong>履帯（キャタピラ）</strong>。**左右の駆動の差で、旋回** |
| **バイク** | `MotorcycleController` | **2 輪**。**傾き（リーン）で、旋回** |

**設定の項目は、車輪付きと、似ています**（**公式サンプル**に、**一通りの例**があります）。

## ソフトボディ

**ソフトボディ**は、**形が変わる、柔らかい物体**です。**頂点（質点）を、エッジ（バネ）でつなぎ**、**形を保つ力**を与えます。**布・旗・風船・ゴム・ぬいぐるみ**に使えます。

### 仕組み

| 要素 | 内容 |
| --- | --- |
| <strong>頂点（Vertex）</strong> | **質点**（質量を持つ点）。**位置と速度** |
| **エッジ（Edge）制約** | **2 つの頂点の距離を、保つ**（**バネ**） |
| **体積（Volume）制約** | **四面体の体積を、保つ**（**膨らんだ形を保つ**） |
| <strong>面（Face）</strong> | **三角形**（**衝突判定・描画**に使う） |
| **圧力** | **内側から、膨らむ力**（**風船**） |

### 作り方

```cpp
Ref<SoftBodySharedSettings> shared = new SoftBodySharedSettings;

for (...) {
  SoftBodySharedSettings::Vertex v;
  v.mPosition = Float3(x, y, z);
  shared->mVertices.push_back(v);
}

for (...) {
  SoftBodySharedSettings::Face f(i0, i1, i2);
  shared->AddFace(f);
}

shared->CreateConstraints(...);

SoftBodyCreationSettings settings(shared, RVec3(0, 5, 0), Quat::sIdentity(), Layers::MOVING);
settings.mPressure = 10.0f;

BodyID id = bodies.CreateAndAddSoftBody(settings, EActivation::Activate);
```

| 設定 | 意味 |
| --- | --- |
| **`SoftBodySharedSettings`** | **頂点・面・制約の定義**（**共有できる**） |
| **`CreateConstraints`** | **面から、エッジ制約を、自動生成** |
| **`SoftBodyCreationSettings`** | **位置・レイヤー・圧力などの、個別の設定** |
| **`mPressure`** | **膨らむ圧力**（風船） |
| **`CreateAndAddSoftBody`** | **ソフトボディとして、追加**（普通の `CreateAndAddBody` ではない） |

### 描画

**ソフトボディの頂点位置は、毎フレーム変わる**ので、**位置を、取り出して、メッシュに反映**して描画します。

```cpp
BodyLockRead lock(physics_system.GetBodyLockInterface(), id);
const SoftBodyMotionProperties* props = static_cast<const SoftBodyMotionProperties*>(lock.GetBody().GetMotionProperties());
for (const auto& vertex : props->GetVertices()) {
  Vec3 position = vertex.mPosition;
}
```

**頂点バッファ**を、**毎フレーム更新**（`D3D11_USAGE_DYNAMIC` ＋ `Map`）して、描きます（[メッシュとテクスチャ](../../3d/mesh-textures.md)）。

### 制限と性能

| 点 | 説明 |
| --- | --- |
| **重い** | **頂点・制約が多いほど、遅い**（**数百〜数千頂点程度**に） |
| **剛体との相互作用** | **剛体との衝突は、できる**が、**押し返す力は、限定的** |
| **ソフトボディどうしの衝突** | **機能が、限られる**（バージョンによる） |
| **布のシミュレーション** | **専用の、布のライブラリ**（NVIDIA Cloth、Chaos Cloth など）や、**頂点シェーダーでの簡易な布**のほうが、**ゲーム向き**なことも |
| **用途の絞り込み** | **数を、限る**（**主人公の、マントなど**）。**多数のオブジェクトは、剛体・アニメーション** |

!!! note "ソフトボディは、慎重に使う"
    <strong>見た目の効果（旗・草・髪）</strong>は、**頂点シェーダーでの、簡易な風の揺れ**や、**骨ベースの物理**（**ジグルボーン**）で、**軽く**実現するのが、**ゲームでは一般的**です。**本物のソフトボディ**は、**特別な見せ場**に、使います。

## 使い分け

| 作りたいもの | 手段 |
| --- | --- |
| **車・トラック** | **車輪付き車両** |
| **戦車・ブルドーザー** | **追従車両** |
| **バイク** | **バイク コントローラー** |
| **人・敵** | **キャラクター**（[キャラクター](character.md)） |
| **ドア・ロープ・関節** | **制約**（[制約](constraints.md)） |
| **布・旗・風船・ゴム** | **ソフトボディ**（**重い。慎重に**） |
| **髪・マント・しっぽ** | <strong>ジグルボーン（骨 ＋ バネ）</strong>、または**頂点シェーダー** |

## よくあるミス

??? failure "車が、動かない"
    **`AddStepListener`** を呼んでいない、**入力（`SetDriverInput`）を、設定していない**、**サスペンションの長さが、地面に届かない**、が考えられます。

??? failure "車が、すぐ横転する"
    **重心を下げる**、**サスペンションを固く**、**質量を増やす**、**ハンドルの角度を、速度で減らす**。

??? failure "車が、勝手に滑る・グリップしない"
    **タイヤの摩擦**を、上げます。

??? failure "車輪の見た目が、車体と合わない"
    **車輪の位置（`mPosition`）と、モデルの車輪の位置**を、そろえます。**描画は、`vehicle->GetWheelLocalTransform` などから、車輪の位置・回転**を取得します。

??? failure "ソフトボディが、重すぎる"
    **頂点・制約を、減らします**。**数も限ります**。

??? failure "ソフトボディを、`CreateAndAddBody` で追加して、動かない"
    **`CreateAndAddSoftBody`** を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 車両は<strong>車体（剛体）＋ `VehicleConstraint`</strong>。<strong>車輪は、レイキャスト</strong>で、<strong>サスペンション（バネ）と摩擦</strong>が、力を生む
    - [x] <strong>`AddConstraint` と `AddStepListener` の両方</strong>。<strong>入力は `SetDriverInput`（アクセル・ハンドル・ブレーキ）</strong>
    - [x] <strong>ゲーム向けに、グリップを強く・重心を低く</strong>調整する
    - [x] <strong>ソフトボディ ＝ 頂点（質点）＋ エッジ制約（バネ）</strong>。<strong>`CreateAndAddSoftBody`</strong>。<strong>重いので、慎重に</strong>
    - [x] <strong>布・髪などは、軽い代替（ジグルボーン・シェーダー）</strong>も検討

## 関連ページ

- [Jolt Physics](index.md)
- [制約（Constraint）](constraints.md)
- [キャラクター](character.md)
- [物体（Body）](bodies.md)
- [公式サンプル（GitHub）](https://github.com/jrouwe/JoltPhysics)
