---
title: 制約（Constraint）
tags:
  - 外部ライブラリ
  - 物理演算
---

# 制約（Constraint）

<strong>制約（Constraint）</strong>は、**2 つの物体の動きをつなぐ**仕組みです。**ドアのヒンジ**（回転だけ許す）、**バネ**、**固定**（くっつける）、**距離を保つ**（ロープ・鎖）、**モーター**（回す）など、**関節のある物の動き**を作れます。**ラグドール**（人形のように力が抜けた体）も、**制約の集まり**です。このページは**制約の種類**、**作り方**、**ヒンジ・バネ・固定・距離**、**モーター**、**ラグドール**をまとめます。

!!! tip "ポイント"
    - 制約は<strong>2 つの物体（Body）をつなぐ</strong>（<strong>片方はワールド（動かない地面）</strong>でもよい）。
    - 作り方：<strong>`XxxConstraintSettings` を設定して、`Create(body1, body2)`</strong>→<strong>`physics_system.AddConstraint(c)`</strong>。
    - 主な種類：<strong>固定（Fixed）・点（Point）・ヒンジ（Hinge）・スライダー（Slider）・距離（Distance、バネ）・円錐（Cone）・スイング ツイスト（Swing-Twist、関節）</strong>。
    - <strong>接続点は物体ごとのローカル座標、またはワールド座標</strong>で指定。<strong>`mSpace` で選ぶ</strong>。
    - <strong>モーター</strong>で<strong>回転・移動を能動的に駆動</strong>できる（ドア・車輪・ロボット）。
    - <strong>制約は削除（`RemoveConstraint`）してから、物体を削除</strong>。<strong>`Update` の外</strong>で追加・削除。
    - <strong>制約でつないだ物体どうしは、既定で衝突しない</strong>設定にもできる（<strong>連結部のめり込み対策</strong>）。

## 制約の考え方

**物体は普通、6 つの自由度**（移動 3 + 回転 3）で、**自由に動きます**。**制約はその自由度を制限**します。

| 制約 | 制限するもの | 残る動き |
| --- | --- | --- |
| <strong>固定（Fixed）</strong> | **全部** | **動かない**（**2 つが、1 つの塊**） |
| <strong>点（Point）</strong> | **移動 3 つ**（接続点が一致） | **回転は自由**（**ボールジョイント**） |
| <strong>ヒンジ（Hinge）</strong> | **移動 3 つ + 回転 2 つ** | **1 軸まわりの回転だけ**（**ドア・扉**） |
| <strong>スライダー（Slider）</strong> | **回転 3 つ + 移動 2 つ** | **1 軸に沿った移動だけ**（**引き出し・ピストン**） |
| <strong>距離（Distance）</strong> | **2 点の距離** | **距離が範囲内**（**ロープ・バネ**） |
| <strong>円錐（Cone）</strong> | **回転が円錐の範囲** | **ボールジョイントに範囲の制限** |
| **スイング ツイスト** | **スイング（曲げ）とツイスト（ねじり）の、範囲** | **人間の関節**（**肩・股関節**） |
| <strong>6 自由度（SixDOF）</strong> | **軸ごとに自由に**設定 | **汎用** |

## 制約を作る

```cpp
HingeConstraintSettings settings;
settings.mPoint1 = settings.mPoint2 = RVec3(0.0_r, 1.0_r, 0.0_r);
settings.mHingeAxis1 = settings.mHingeAxis2 = Vec3::sAxisY();
settings.mNormalAxis1 = settings.mNormalAxis2 = Vec3::sAxisX();
settings.mLimitsMin = -JPH_PI * 0.5f;
settings.mLimitsMax = JPH_PI * 0.5f;

Constraint* hinge = settings.Create(door_body, Body::sFixedToWorld);
physics_system.AddConstraint(hinge);
```

| 手順 | 内容 |
| --- | --- |
| **1. 設定を作る** | **種類ごとの `ConstraintSettings`**。**接続点・軸・制限**を設定 |
| **2. `Create(body1, body2)`** | **2 つの物体を渡して**、**制約を作る**。**`Body` への参照**（`BodyID` ではない）を渡す |
| **3. `AddConstraint`** | **世界に追加** |
| **削除** | **`RemoveConstraint(c)`** |

### ワールドに固定する

**片方を動かない地面**にしたいときは、**`Body::sFixedToWorld`** を、**もう一方の引数**に渡します。

```cpp
Constraint* c = settings.Create(body, Body::sFixedToWorld);
```

**吊り橋・ブランコ・壁に付いたドア**は、**片方がワールド**です。

### 接続点の座標系

| `mSpace` | 意味 |
| --- | --- |
| **`EConstraintSpace::WorldSpace`**（既定） | **接続点をワールド座標**で指定（**今の配置から、自動で各物体のローカルに変換**） |
| **`EConstraintSpace::LocalToBodyCOM`** | **各物体の重心からのローカル座標**で指定 |

**ワールド座標**で指定する方が、**簡単**です（**今、物体が置いてある場所に、ヒンジを置く**だけ）。

## 主な制約

### 固定（Fixed）

**2 つの物体をくっつけます**（**溶接**）。

```cpp
FixedConstraintSettings settings;
settings.mAutoDetectPoint = true;
Constraint* c = settings.Create(body1, body2);
```

| 用途 | 説明 |
| --- | --- |
| **物体の組み立て** | **車体にパーツをくっつける** |
| **壊れる接続** | **制約に強さの上限があれば、力を超えると外れる**（`mMaxForce`）。**壊れる橋・扉** |

<strong>複合形状（Compound）</strong>で作る方が**軽い**場合もあります（**壊さないなら**）。

### ヒンジ（Hinge）

**1 つの軸まわりに回転**できる、**蝶番**です。

```cpp
HingeConstraintSettings settings;
settings.mPoint1 = settings.mPoint2 = hinge_position;
settings.mHingeAxis1 = settings.mHingeAxis2 = Vec3::sAxisY();
settings.mNormalAxis1 = settings.mNormalAxis2 = Vec3::sAxisX();
settings.mLimitsMin = Degrees(-90);
settings.mLimitsMax = Degrees(90);
```

| 設定 | 意味 |
| --- | --- |
| **`mPoint1` / `mPoint2`** | **接続点**（2 つの物体で**同じ場所**） |
| **`mHingeAxis1` / `mHingeAxis2`** | **回転の軸** |
| **`mNormalAxis1` / `mNormalAxis2`** | **軸に垂直な基準方向**（**角度 0 の向き**）。**制限・モーターの角度の基準** |
| **`mLimitsMin` / `mLimitsMax`** | **角度の範囲**（ラジアン。`-π` 〜 `π`） |
| **`mMaxFrictionTorque`** | **摩擦**（動きにくさ） |

**ドア・扉・振り子・車輪**に使います。

### 点（Point）

**1 点でつなぎます**（**回転は自由**）。**ボールジョイント**。

```cpp
PointConstraintSettings settings;
settings.mPoint1 = settings.mPoint2 = joint_position;
```

**ぶら下がる物体・チェーン・振り子**に使います。

### 距離（Distance）とバネ

**2 つの点の距離を保つ**制約です。**バネ**にもできます。

```cpp
DistanceConstraintSettings settings;
settings.mPoint1 = anchor_position;
settings.mPoint2 = object_position;
settings.mMinDistance = 0.5f;
settings.mMaxDistance = 5.0f;

settings.mLimitsSpringSettings.mFrequency = 2.0f;
settings.mLimitsSpringSettings.mDamping = 0.5f;
```

| 設定 | 意味 |
| --- | --- |
| **`mMinDistance` / `mMaxDistance`** | **距離の範囲**（**最小 = 最大 ＝ ロッド**（硬い棒）、**最大のみ ＝ ロープ**） |
| **`mLimitsSpringSettings`** | **バネ**（<strong>`mFrequency` ＝ 固さ（Hz）</strong>、**`mDamping` ＝ 減衰**）。**設定しないと硬い制約** |

**ロープ・グラップリングフック・ゴムひも・サスペンション**に使います。

### スライダー（Slider）

**1 つの軸に沿って、移動**します（**引き出し・ピストン**）。

```cpp
SliderConstraintSettings settings;
settings.mAutoDetectPoint = true;
settings.SetSliderAxis(Vec3::sAxisX());
settings.mLimitsMin = -2.0f;
settings.mLimitsMax = 2.0f;
```

**エレベーター・引き出し・スライドドア**に使います。

### スイング ツイスト（SwingTwist）

**人間の関節**（**肩・股関節**）のように<strong>曲げ（スイング）と、ねじり（ツイスト）</strong>の**範囲を別々に制限**します。

```cpp
SwingTwistConstraintSettings settings;
settings.mPosition1 = settings.mPosition2 = shoulder_position;
settings.mTwistAxis1 = settings.mTwistAxis2 = Vec3::sAxisX();
settings.mPlaneAxis1 = settings.mPlaneAxis2 = Vec3::sAxisY();
settings.mNormalHalfConeAngle = Degrees(45);
settings.mPlaneHalfConeAngle = Degrees(30);
settings.mTwistMinAngle = Degrees(-30);
settings.mTwistMaxAngle = Degrees(30);
```

**ラグドール**の関節の基本です。

## モーター

**制約にモーター**を付けると**能動的に動かせます**（**ドアを開ける・車輪を回す・ロボットの関節**）。

```cpp
HingeConstraint* hinge = static_cast<HingeConstraint*>(constraint);
hinge->SetMotorState(EMotorState::Velocity);
hinge->SetTargetAngularVelocity(JPH_PI);
```

| モーターの状態 | 動き |
| --- | --- |
| **`EMotorState::Off`** | **モーターなし**（自由に動く） |
| **`EMotorState::Velocity`** | **目標の速度**で回す |
| **`EMotorState::Position`** | <strong>目標の位置（角度）</strong>に、向かう（**バネのように**） |

| 設定 | 意味 |
| --- | --- |
| **`SetTargetAngularVelocity`** / **`SetTargetAngle`** | **目標の角速度・角度** |
| **`GetMotorSettings()`** | **モーターの強さ**（**`mMaxTorqueLimit`** ＝ 出せる力の上限）、**バネの固さ** |

**`Position` モード**に、**バネ**を使うと<strong>「目標の姿勢に引き戻される」関節</strong>になります（**アニメーションに物理的に追従する、キャラクター**）。

## ラグドール

**ラグドール**は**人間の体を剛体（部位）と、制約（関節）で作り**、**死んだ・気絶したキャラクターが、力なく崩れる**表現です。

| 構成 | 内容 |
| --- | --- |
| <strong>部位（Body）</strong> | **頭・胴・腕・脚**などを**カプセルや箱**で |
| <strong>関節（Constraint）</strong> | **スイング ツイスト**で**部位をつなぐ** |
| **`Skeleton`** | **ボーンの階層**（親子関係） |
| **`RagdollSettings`** | **部位と関節をまとめて定義** |

```cpp
Ref<RagdollSettings> ragdoll_settings = CreateRagdollSettings();
Ragdoll* ragdoll = ragdoll_settings->CreateRagdoll(0, 0, &physics_system);
ragdoll->AddToPhysicsSystem(EActivation::Activate);
```

**アニメーションの姿勢を、ラグドールに設定**して、**そこから物理で崩れさせます**（`SetPose`）。**部位の位置をボーンの姿勢に書き戻して**描画します（[スキニングとアニメーション](../../3d/skinning-animation.md)）。

!!! note "ラグドールの作成は、大変"
    **ボーンの構造・関節の範囲・質量の配分**を、**1 つずつ調整**する必要があり、**手間がかかります**。**モデルのツール（Blender など）の、ラグドール生成**や、**Jolt のサンプル**（`RagdollTest`）が、参考になります。

## 連結した物体の衝突

**制約でつないだ 2 つの物体が、お互いに衝突すると不安定**になります（**関節の部分でめり込む**）。

| 方法 | 説明 |
| --- | --- |
| <strong>衝突グループ（`CollisionGroup`）</strong> | **同じグループの物体どうしは、衝突しない**（`mCollisionGroup`） |
| **レイヤーで分ける** | **連結部の部位を別のレイヤー**にして、衝突を無効に |

**ラグドールの隣り合う部位どうし**は、**衝突を無効**にします（Jolt の `GroupFilterTable` で、**部位ペアごと**に設定できます）。

## 制約の削除と物体の削除

```cpp
physics_system.RemoveConstraint(constraint);

bodies.RemoveBody(id);
bodies.DestroyBody(id);
```

| 順番 | 理由 |
| --- | --- |
| **制約を先に削除** | **物体が消えた後の制約は、無効なポインタを持つ** |
| **`Update` の外で** | **物理の最中は変更しない** |

<strong>制約は参照カウント（`Ref<Constraint>`）</strong>で管理することもできます。

## 使いどころ

| 場面 | 制約 |
| --- | --- |
| **ドア・扉・蓋** | **ヒンジ**（制限付き） |
| **エレベーター・引き出し** | **スライダー** |
| **ロープ・鎖・ブランコ** | **距離・点**（鎖は点の連続） |
| **グラップリングフック・ゴムひも** | <strong>距離（バネ付き）</strong> |
| **壊れる橋・建物** | <strong>固定（力の上限付き）</strong> |
| **ラグドール** | **スイング ツイスト** |
| **ロボット・乗り物の関節** | **ヒンジ ＋ モーター** |
| **車のサスペンション** | <strong>距離（バネ）</strong>、または**車両の機能**（[車両](vehicles.md)） |

## よくあるミス

??? failure "制約を作って、`AddConstraint` するのを忘れる"
    **作っただけでは、効きません**。**世界に追加**します。

??? failure "接続点がずれて、物体が勢いよく動く"
    **2 つの接続点が一致**するようにします（**ワールド座標で同じ点**）。

??? failure "ヒンジの軸の指定が、2 つの物体で食い違う"
    **`mHingeAxis1` と `mHingeAxis2` を、同じ向き**（ワールドで）にします。

??? failure "連結した部位が、お互いに衝突して、震える"
    **衝突グループ**で**衝突を無効**にします。

??? failure "物体を削除したのに、制約が残って、クラッシュする"
    **制約を先に削除**します。

??? failure "質量が極端に違う物体を、制約でつないで不安定になる"
    **質量比を抑えます**（10 倍程度まで）。**反復回数を増やす**方法もあります。

??? failure "モーターを `Update` の最中に、変更する"
    **`Update` の外**で呼びます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 制約は<strong>2 つの物体の動きを、つなぐ</strong>。<strong>`Settings` ＋ `Create(body1, body2)` ＋ `AddConstraint`</strong>
    - [x] 種類：<strong>固定・点・ヒンジ（1 軸の回転）・スライダー（1 軸の移動）・距離（ロープ・バネ）・スイング ツイスト（関節）</strong>
    - [x] <strong>片方をワールドに固定</strong>するなら <strong>`Body::sFixedToWorld`</strong>。<strong>接続点はワールド座標で指定</strong>（簡単）
    - [x] <strong>モーター</strong>（<strong>`Velocity`・`Position`</strong>）で、能動的に駆動
    - [x] <strong>ラグドール ＝ 部位（剛体）＋ 関節（スイング ツイスト）</strong>。<strong>隣り合う部位の衝突は、無効</strong>に
    - [x] <strong>削除は、制約が先、次に物体</strong>。<strong>`Update` の外で</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [物体（Body）](bodies.md)
- [車両・ソフトボディ](vehicles.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
