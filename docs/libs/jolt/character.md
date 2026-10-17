---
title: キャラクター
tags:
  - 外部ライブラリ
  - 物理演算
---

# キャラクター

**プレイヤーや敵の、キャラクターの移動**は、**普通の剛体で作る**と、**操作感が悪く**なります（**滑る・坂で止まらない・段差で引っかかる**）。**Jolt には、キャラクター専用の仕組み**があり、**階段・坂・動く床・壁ずり**を、**ゲームに合う操作感**で扱えます。このページは、<strong>`CharacterVirtual`（仮想キャラクター）</strong>を中心に、**接地判定・ジャンプ・階段・動く床**、<strong>`Character`（剛体版）</strong>との違いをまとめます。

!!! tip "ポイント"
    - <strong>キャラクターは「普通の剛体」にしない</strong>。<strong>専用の `CharacterVirtual`</strong> を使う。
    - <strong>`CharacterVirtual`</strong>は<strong>物理シミュレーションの外で動き</strong>（<strong>自分で、速度を決める</strong>）、<strong>衝突は、世界に対して判定</strong>する。<strong>操作感を、ゲーム側で制御</strong>できる。
    - 形は<strong>カプセル</strong>。<strong>最大の坂の角度（`mMaxSlopeAngle`）</strong>、<strong>階段の高さ</strong>を設定。
    - 毎フレーム（固定ステップ）<strong>`ExtendedUpdate`</strong>（階段・床への吸着を含む更新）。<strong>速度を設定してから呼ぶ</strong>。
    - <strong>接地状態</strong>は <strong>`GetGroundState()`</strong>（<strong>`OnGround`・`OnSteepGround`・`InAir`</strong>）。<strong>ジャンプは、接地しているときだけ</strong>。
    - <strong>動く床の速度</strong>（<strong>`GetGroundVelocity()`</strong>）を<strong>足して</strong>、乗っているものを運ぶ。
    - <strong>`Character`（剛体版）</strong>は<strong>物理世界の中の剛体</strong>。<strong>押し合いが自然</strong>だが、<strong>操作感の調整は、難しい</strong>。

## なぜ専用のキャラクターか

<strong>キャラクターを、`Dynamic` な剛体（カプセル）</strong>にして、**力で動かすと**、次のような問題が起きます。

| 問題 | 説明 |
| --- | --- |
| **滑る** | **摩擦で、止まる・動くが、思い通りにならない** |
| **坂で、ずり落ちる** | **傾斜で、勝手に滑る** |
| **段差に、引っかかる** | **カプセルの端が、段差に当たって、止まる** |
| **壁に張り付く** | **壁に向かって押すと、摩擦で、止まる** |
| **ジャンプの高さが、不安定** | **衝突で、勢いが変わる** |
| **回転する** | **倒れる**（回転を固定する必要） |

<strong>ゲームのキャラクターは、「物理的に正しい」より、「操作しやすい」</strong>ことが大切です。**`CharacterVirtual`** は、**ゲーム側が、動きを決め、物理は、衝突の判定だけ**に使います。

## CharacterVirtual（仮想キャラクター）

**物理世界の中に、物体として存在せず**、**自分で動きを管理**します。**世界の物体との衝突は、判定**しますが、**物理的な押し合い**は、**最小限**です。

<div class="anim" data-type="graph" data-label="CharacterVirtual：ゲームが速度を決め、Jolt が、衝突・階段・坂を処理する">
n in 入力_（移動の向き） 0 1 hit
---
n in 入力_（移動の向き） 0 1
n vel 速度を決める_（ゲーム側） 1 1 new
l in vel hit
---
n vel 速度を決める_（ゲーム側） 1 1
n ch CharacterVirtual_ExtendedUpdate 2 1 new
l vel ch hit 設定
---
n ch CharacterVirtual_ExtendedUpdate 2 1
n pos 衝突を解決した_位置 3 1 new
l ch pos hit 階段・坂・壁
</div>

### 作る

```cpp
Ref<CharacterVirtualSettings> settings = new CharacterVirtualSettings();
settings->mShape = RotatedTranslatedShapeSettings(
    Vec3(0, 0.9f, 0), Quat::sIdentity(), new CapsuleShape(0.6f, 0.3f)).Create().Get();
settings->mMaxSlopeAngle = DegreesToRadians(45.0f);
settings->mUp = Vec3::sAxisY();
settings->mSupportingVolume = Plane(Vec3::sAxisY(), -0.3f);
settings->mMass = 70.0f;
settings->mMaxStrength = 100.0f;

character = new CharacterVirtual(settings, RVec3(0, 2, 0), Quat::sIdentity(), &physics_system);
```

| 設定 | 意味 |
| --- | --- |
| **`mShape`** | **カプセル**（**足元が、原点**になるよう、**`RotatedTranslatedShape` で、持ち上げる**） |
| **`mMaxSlopeAngle`** | **歩ける坂の、最大の角度**（これより急な坂は、登れない・滑り落ちる） |
| **`mUp`** | **上方向**（通常 `Y`） |
| **`mSupportingVolume`** | **足元の判定領域**（**この範囲に、触れていれば、接地**）。**カプセルの下半分** |
| **`mMass` / `mMaxStrength`** | **ほかの動的な物体を、押す**ときの、**質量と力の上限** |
| `mPredictiveContactDistance` | **接触を、予測する距離**（**めり込みを防ぐ**） |

## 毎フレームの更新

```cpp
void UpdateCharacter(float dt, const Vec3& move_direction, bool jump) {
  Vec3 current = character->GetLinearVelocity();

  Vec3 ground_velocity = character->GetGroundVelocity();
  bool on_ground = character->GetGroundState() == CharacterBase::EGroundState::OnGround;

  Vec3 new_velocity;
  if (on_ground) {
    new_velocity = move_direction * kMoveSpeed + ground_velocity;
    if (jump) new_velocity += Vec3(0, kJumpSpeed, 0);
  } else {
    new_velocity = Vec3(move_direction.GetX() * kAirControl, current.GetY(), move_direction.GetZ() * kAirControl);
    new_velocity += physics_system.GetGravity() * dt;
  }
  character->SetLinearVelocity(new_velocity);

  CharacterVirtual::ExtendedUpdateSettings update_settings;
  update_settings.mStickToFloorStepDown = Vec3(0, -0.5f, 0);
  update_settings.mWalkStairsStepUp = Vec3(0, 0.4f, 0);

  character->ExtendedUpdate(dt, physics_system.GetGravity(), update_settings,
                            physics_system.GetDefaultBroadPhaseLayerFilter(Layers::PLAYER),
                            physics_system.GetDefaultLayerFilter(Layers::PLAYER),
                            {}, {}, *temp_allocator);
}
```

| 手順 | 内容 |
| --- | --- |
| **1. 接地状態を調べる** | **`GetGroundState()`** |
| **2. 速度を決める** | **入力から**、**移動速度・ジャンプ・重力**（**ゲーム側のロジック**） |
| **3. `SetLinearVelocity`** | **速度を、キャラクターに設定** |
| **4. `ExtendedUpdate`** | **移動を、衝突を考慮して、実行**（階段・床への吸着を含む） |

### ExtendedUpdate の設定

| 設定 | 意味 |
| --- | --- |
| **`mStickToFloorStepDown`** | **足が少し浮いても、床に吸着**（**下り坂・階段で、浮かない**）。**下向きの、ベクトル** |
| **`mWalkStairsStepUp`** | **登れる段差の高さ**（**階段**）。**上向きの、ベクトル** |
| `mWalkStairsMinStepForward` / `mWalkStairsStepForwardTest` | **階段の、判定の細かい設定** |

| 関数 | 違い |
| --- | --- |
| **`Update`** | **基本の更新**（**衝突の解決のみ**） |
| **`ExtendedUpdate`** | **`Update` ＋ 階段を登る ＋ 床に吸着**。**普通は、こちら** |

## 接地状態

**`GetGroundState()`** で、**今、地面に立っているか**が分かります。

| 状態 | 意味 | 動き |
| --- | --- | --- |
| **`OnGround`** | **歩ける地面に、立っている** | **歩く・ジャンプできる** |
| **`OnSteepGround`** | **急すぎる坂**（`mMaxSlopeAngle` を超える）の上 | **滑り落ちる**（**登れない**） |
| **`NotSupported`** | **何かに触れているが、立てない**（壁の側面など） | **空中と、同じ扱い** |
| **`InAir`** | **空中** | **重力で落ちる** |

```cpp
switch (character->GetGroundState()) {
  case CharacterBase::EGroundState::OnGround: ...
  case CharacterBase::EGroundState::OnSteepGround: ...
  case CharacterBase::EGroundState::NotSupported: ...
  case CharacterBase::EGroundState::InAir: ...
}
```

**ジャンプは、`OnGround` のときだけ**にします。<strong>落ち始めて少しの間、ジャンプを許す（コヨーテタイム）</strong>など、**操作感の調整**は、**ゲーム側**で行います。

## 動く床・エレベーター

**動く床の上に立つ**キャラクターは、**床と一緒に動く**必要があります。

```cpp
Vec3 ground_velocity = character->GetGroundVelocity();
new_velocity = move_direction * kMoveSpeed + ground_velocity;
```

| 点 | 説明 |
| --- | --- |
| **`GetGroundVelocity()`** | **足元の地面（物体）の、速度**（動く床・エレベーター・回転する床） |
| **速度に足す** | **キャラクターの速度に、地面の速度を加える**と、**床に乗って、運ばれる** |
| **キネマティックな物体** | **`MoveKinematic`** で動く床（[物体](bodies.md)） |

## 壁ずり・押し出し

| 動き | 説明 |
| --- | --- |
| **壁に向かって歩く** | **壁に沿って、滑る**（**壁ずり**）。**張り付かない** |
| **動的な物体を押す** | **`mMass`・`mMaxStrength`** で、**押す力**が決まる。**重い物は、動かない** |
| **挟まれる** | **押しつぶされない**ように、**位置を補正** |

## キャラクターのリスナー（接触の通知）

**`CharacterContactListener`** で、**キャラクターの接触を、処理**できます。

```cpp
class MyCharacterListener : public CharacterContactListener {
 public:
  void OnContactAdded(const CharacterVirtual* character, const BodyID& body2,
                      const SubShapeID& sub_shape_id2, RVec3Arg contact_position,
                      Vec3Arg contact_normal, CharacterContactSettings& io_settings) override {
  }

  void OnAdjustBodyVelocity(const CharacterVirtual* character, const Body& body2,
                            Vec3& io_linear_velocity, Vec3& io_angular_velocity) override {
  }
};

character->SetListener(&listener);
```

| 用途 | 説明 |
| --- | --- |
| **特定の物体と、すり抜ける** | **`io_settings.mCanPushCharacter = false`** などで、**押し合いを調整** |
| **ダメージ床・トリガー** | **接触した物体を、ゲーム側で処理** |
| **動く床の速度の調整** | **`OnAdjustBodyVelocity`** |

## Character（剛体版）

**`Character`**は、**物理世界の中の、本物の剛体**として存在する**キャラクター**です。

| | **CharacterVirtual** | <strong>Character（剛体版）</strong> |
| --- | --- | --- |
| **物理世界での存在** | **なし**（外で動く） | **あり**（剛体） |
| **ほかの物体との押し合い** | **簡易**（質量・強さで調整） | **物理的に、自然** |
| **操作感の調整** | **自由**（ゲーム側が、速度を決める） | **難しい**（物理に影響される） |
| **階段・坂** | **専用の機能**（`ExtendedUpdate`） | **標準では、なし**（自分で工夫） |
| **処理の重さ** | **軽い** | やや重い |
| **向く用途** | <strong>プレイヤー・敵（アクション）</strong> | <strong>物理が主体のゲーム（重い物を押す・押される）</strong> |

**`Character` は、`PostSimulation`** を、**`Update` の後に、呼びます**（接地の判定を、更新）。

```cpp
character->PostSimulation(0.05f);
```

**多くのアクションゲームは、`CharacterVirtual`**で足ります。

## 敵・NPC のキャラクター

**敵の移動も、`CharacterVirtual`**で作れます。**経路探索（ナビメッシュ）の結果**から、**移動の向きを決め**、**同じ更新**を使います。

| 点 | 説明 |
| --- | --- |
| **大量の敵** | **数百体の `CharacterVirtual`** は、**やや重い**。**遠くの敵は、簡易な移動**（物理なし）に切り替える |
| **ナビメッシュと組み合わせる** | **経路 → 次の目標点 → 速度 → `ExtendedUpdate`**（[ベイク](../../optimize/baking.md)のナビメッシュ） |
| **レイヤー** | **敵どうしの衝突を、レイヤーで制御**（[レイヤー](layers.md)） |

## よくあるミス

??? failure "キャラクターを、`Dynamic` な剛体にして、操作感が悪い"
    **`CharacterVirtual`** を使います。

??? failure "`mShape` の原点が、カプセルの中心で、足元が地面に埋まる"
    **足元を原点**にするよう、**`RotatedTranslatedShape` で、持ち上げます**。

??? failure "階段を、登れない"
    **`mWalkStairsStepUp`** の高さを、**段差より大きく**します。**`ExtendedUpdate`**（`Update` ではなく）を使っているか確認。

??? failure "下り坂で、浮いて、落ちる"
    **`mStickToFloorStepDown`** を設定します。

??? failure "動く床に乗ると、置いていかれる"
    **`GetGroundVelocity()`** を、**速度に足します**。

??? failure "空中で、何度もジャンプできる"
    **`GetGroundState() == OnGround`** のときだけ、ジャンプを許します。

??? failure "可変の `dt` で、ジャンプの高さが、フレームレートで変わる"
    **固定ステップ**で更新します（[世界の初期化と更新](system.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>キャラクターは、剛体にせず `CharacterVirtual`</strong>。<strong>ゲーム側が速度を決め、Jolt が、衝突・坂・階段を処理</strong>
    - [x] 形は<strong>カプセル（足元が原点）</strong>。<strong>`mMaxSlopeAngle`</strong>（坂）、<strong>`mWalkStairsStepUp`</strong>（階段）、<strong>`mStickToFloorStepDown`</strong>（床への吸着）
    - [x] 毎フレーム<strong>「速度を設定 → `ExtendedUpdate`」</strong>（<strong>固定ステップ</strong>）
    - [x] <strong>接地は `GetGroundState()`</strong>。<strong>ジャンプは `OnGround` のときだけ</strong>
    - [x] <strong>動く床は `GetGroundVelocity()` を速度に足す</strong>
    - [x] <strong>`Character`（剛体版）</strong>は、<strong>物理が主体のゲーム</strong>向け

## 関連ページ

- [Jolt Physics](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)
- [クエリ（レイキャストなど）](queries.md)
- [カメラ](../../3d/camera.md)
