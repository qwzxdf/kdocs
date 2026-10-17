---
title: 形（Shape）
tags:
  - 外部ライブラリ
  - 物理演算
---

# 形（Shape）

<strong>形（Shape）</strong>は、<strong>物体の「衝突判定に使う形」</strong>です。**見た目のモデル**（数万ポリゴン）**とは別**に<strong>単純な形（箱・球・カプセル）</strong>や、**凸包・メッシュ**を**物理用に用意**します（[3D の衝突判定](../../3d/collision-3d.md)）。**形によって、速さ・正確さ・使える物体の種類が変わります**。このページは**形の種類**、**作り方**、**複合形状**、**スケール・重心のずれ**、**選び方**をまとめます。

!!! tip "ポイント"
    - 形は<strong>`XxxShapeSettings` で設定して、`Create()` で作る</strong>。<strong>結果は `ShapeRefC`（参照カウント付き）</strong>。<strong>エラーを確認</strong>する。
    - <strong>基本の形：箱・球・カプセル・円柱</strong>。<strong>最も速く、安定</strong>。<strong>まずこれ</strong>。
    - <strong>凸包（`ConvexHull`）</strong>は<strong>凸の形</strong>。<strong>動く物体に使える</strong>。<strong>三角形メッシュは、静的な物体だけ</strong>。
    - <strong>複合形状（Compound）</strong>で、<strong>複数の形を、1 つの物体にまとめる</strong>（<strong>凹んだ形を凸の集まりで近似</strong>）。
    - <strong>形は共有できる</strong>（<strong>同じ形を多数の物体で使い回し</strong>）。<strong>1 回だけ作る</strong>。
    - <strong>見た目と物理の形は、別</strong>。<strong>物理はできるだけ単純に</strong>。

## 形の作り方

```cpp
BoxShapeSettings box_settings(Vec3(0.5f, 0.5f, 0.5f));
ShapeSettings::ShapeResult result = box_settings.Create();

if (result.HasError()) {
  Log::Error("形の作成に失敗: {}", result.GetError().c_str());
  return;
}

ShapeRefC box_shape = result.Get();
```

| 点 | 説明 |
| --- | --- |
| **`XxxShapeSettings`** | **形の設定**（大きさなど） |
| **`Create()`** | **形を作る**。**`ShapeResult`** を返す（**エラーが含まれうる**） |
| **`HasError()` / `GetError()`** | **失敗の確認と理由** |
| **`ShapeRefC`** | <strong>形への参照（参照カウント）</strong>。**コピーすると共有**される。**最後の参照が消えると解放** |

**単純な形**（`BoxShape`・`SphereShape`）は、**直接 `new`** で作ることもできます（**エラーが起きにくい**ため）。

```cpp
new SphereShape(0.5f)
new BoxShape(Vec3(1, 0.5f, 2))
```

### 形を共有する

**同じ形の物体が多数**（弾・木・箱）あるなら、**形を 1 回だけ作って、使い回します**。

```cpp
ShapeRefC bullet_shape = new SphereShape(0.1f);

for (...) {
  BodyCreationSettings s(bullet_shape, pos, Quat::sIdentity(), EMotionType::Dynamic, Layers::PLAYER_BULLET);
  bodies.CreateAndAddBody(s, EActivation::Activate);
}
```

**参照カウント**で管理されるので、**形を物体が持っている間は、解放されません**。**メモリの節約**になります。

## 基本の形

| 形 | 作り方 | 特徴 | 用途 |
| --- | --- | --- | --- |
| **箱**（`BoxShape`） | `BoxShape(Vec3 half_extent, float convex_radius = 0.05f)` | **直方体**。**半分の大きさ**で指定 | **壁・箱・建物** |
| **球**（`SphereShape`） | `SphereShape(float radius)` | **最も速く、安定** | **ボール・弾・簡易な敵** |
| **カプセル**（`CapsuleShape`） | `CapsuleShape(float half_height, float radius)` | **円柱の両端に半球**。**転がりやすく、段差に強い** | **人型のキャラクター** |
| **円柱**（`CylinderShape`） | `CylinderShape(float half_height, float radius)` | **円柱** | **樽・柱・車輪** |
| **テーパー カプセル** | `TaperedCapsuleShape` | **両端の半径が違う** | **手足** |

### 半分の大きさ（half extent）

<strong>箱の大きさは、「半分」</strong>で指定します（**中心から面までの距離**）。**幅 2m・高さ 1m・奥行き 4m の箱**なら、`Vec3(1.0f, 0.5f, 2.0f)` です（[3D の衝突判定](../../3d/collision-3d.md)の `BoundingBox` と同じ）。

### 凸半径（convex radius）

**箱などの角はわずかに丸められ**ます（**凸半径**、既定 0.05）。**衝突判定の安定性と速さ**のためです。**小さな物体**（**大きさが凸半径より小さい**）は、**凸半径を小さく**します。

```cpp
BoxShape(Vec3(0.05f, 0.05f, 0.05f), 0.01f)
```

### 向き（円柱・カプセルの軸）

**カプセルや円柱は、Y 軸方向**に伸びます（**立っている形**）。**横向き**にしたければ、**回転した物体**にするか、**`RotatedTranslatedShape`** で包みます。

## 凸包（ConvexHull）

**頂点の集まり（点群）の、外側を包む、凸の形**です。

```cpp
Array<Vec3> points = {Vec3(-1, 0, -1), Vec3(1, 0, -1), Vec3(0, 0, 1), Vec3(0, 2, 0)};
ConvexHullShapeSettings hull_settings(points);
ShapeRefC hull = hull_settings.Create().Get();
```

| 点 | 説明 |
| --- | --- |
| <strong>凸（へこみがない）</strong> | **どの 2 点を結んでも、形の内側**に収まる |
| **動く物体に使える** | **三角形メッシュと違い、`Dynamic` の物体でも OK** |
| **点の数** | **数十〜百個程度**に抑える（**増えると重い**） |
| **見た目のメッシュから作る** | **頂点を渡す**（**簡略化**した点群で） |

**凹んだ形**（ドーナツ・椅子）は、**1 つの凸包では表せません**。**複数の凸包に分割して、複合形状**にします。

## 三角形メッシュ（MeshShape）

**三角形のメッシュそのもの**を、衝突の形にします。**正確**ですが**制限があります**。

```cpp
TriangleList triangles;
triangles.push_back(Triangle(Float3(0, 0, 0), Float3(10, 0, 0), Float3(0, 0, 10)));

MeshShapeSettings mesh_settings(triangles);
ShapeRefC mesh = mesh_settings.Create().Get();
```

| 点 | 説明 |
| --- | --- |
| **静的な物体だけ**（`Static`） | **`Dynamic` の物体には、使えない**（**重い・不安定**） |
| **中が空洞** | **メッシュは表面だけ**。**内側に入った物体は、外に出せない**ことがある |
| **三角形が多い** | **メモリを使う**。**BVH（空間分割）が、自動で作られる** |
| **用途** | **地形・建物・洞窟の静的な背景** |

**地形**には、**`HeightFieldShape`**（**高さの配列**）も使えます（**メッシュより、軽くて速い**）。

## 複合形状（Compound）

**複数の形を、1 つの物体にまとめます**。**位置と向きを形ごとに指定**できます。

```cpp
StaticCompoundShapeSettings compound;
compound.AddShape(Vec3(0, 0, 0), Quat::sIdentity(), new BoxShape(Vec3(1, 0.1f, 1)));
compound.AddShape(Vec3(0, 0.5f, 0), Quat::sIdentity(), new BoxShape(Vec3(0.1f, 0.5f, 0.1f)));
ShapeRefC table = compound.Create().Get();
```

| 種類 | 説明 |
| --- | --- |
| **`StaticCompoundShape`** | **作った後、変更できない**。**速い**（**普通はこれ**） |
| **`MutableCompoundShape`** | **後から、形の追加・削除・移動**ができる。**やや重い** |

**用途**：
- **凹んだ形を凸の組み合わせ**で近似（椅子・テーブル）
- **キャラクターの部位ごとの判定**（頭・胴・腕）
- **見た目が複雑な物体を、少数の単純な形で**近似

## 形をずらす・回す・拡大する

| 形 | 説明 |
| --- | --- |
| **`RotatedTranslatedShape`** | **形を位置・向きをずらして包む**（**中心が物体の原点と違う**とき） |
| **`ScaledShape`** | **形を拡大・縮小して包む**（**同じ形を違う大きさで共有**） |
| **`OffsetCenterOfMassShape`** | **重心をずらす**（**傾きやすい・安定しやすい**を調整） |

```cpp
ShapeRefC lying_capsule = RotatedTranslatedShapeSettings(
    Vec3::sZero(), Quat::sRotation(Vec3::sAxisZ(), JPH_PI * 0.5f), new CapsuleShape(1.0f, 0.3f)).Create().Get();

ShapeRefC big_box = new ScaledShape(box_shape, Vec3(2, 1, 2));
```

!!! warning "非一様スケールには、制限がある"
    **`ScaledShape` で、軸ごとに違う倍率**（非一様スケール）を使うと**一部の形**（**球・カプセル**）は、**正しく扱えません**。**一様スケール**（全軸同じ）が、安全です。

## 重心と慣性

<strong>物体の「重心」</strong>は、**形の体積の中心**で**自動計算**されます。

| 点 | 説明 |
| --- | --- |
| **重心と物体の原点が違う** | **`GetCenterOfMassPosition`** と **`GetPosition`** で、**位置が違う** |
| **重心をずらしたい** | **`OffsetCenterOfMassShape`** |
| <strong>慣性（回しやすさ）</strong> | **形と質量から、自動計算**。**手動で変える**こともできる |

**細長い形を立てると倒れやすい**（**重心が高い**）。**重心を少し下げる**と**安定**します。

## 形の選び方

| 物体 | 形 | 理由 |
| --- | --- | --- |
| **ボール・弾** | **球** | **最速・安定** |
| **人型のキャラクター** | **カプセル** | **段差・坂に強い** |
| **箱・壁・建物** | **箱** | **単純で速い** |
| **樽・柱** | **円柱** | |
| <strong>岩・石（動く）</strong> | **凸包** | **動かせて、形が自由** |
| <strong>椅子・テーブル（動く）</strong> | <strong>複合形状（箱の組み合わせ）</strong> | 凹みがある |
| <strong>地形（動かない）</strong> | **`HeightFieldShape`**、**`MeshShape`** | 静的な背景 |
| <strong>建物・洞窟（動かない）</strong> | **`MeshShape`** | 凹凸が複雑 |

**物理の形はできるだけ単純に**します（**頂点数・三角形数が少ないほど速い**）。**見た目のモデルと完全に同じ形にする必要は、ありません**。

!!! note "ベイク（事前計算）"
    **凸包の計算・メッシュの BVH の構築**は、**重い**処理です。**ステージのロード時に毎回やらず**、**ビルド時に物理用データとして焼いておく**（**クッキング**）と、**ロードが速く**なります（[ベイク](../../optimize/baking.md)）。Jolt は、**`Shape::SaveBinaryState` / `RestoreFromBinaryState`** で、**形のバイナリ保存**ができます。

## 形の情報を調べる

| 関数 | 内容 |
| --- | --- |
| `GetLocalBounds()` | **ローカル空間の境界ボックス** |
| `GetWorldSpaceBounds(transform, scale)` | **ワールド空間の境界ボックス** |
| `GetVolume()` | **体積** |
| `GetMassProperties()` | **質量・慣性**（密度から） |
| `GetSubType()` | **形の種類**（`EShapeSubType::Box` など） |

## よくあるミス

??? failure "`Create()` のエラーを確認せず、`Get()` して、クラッシュする"
    **`HasError()` を確認**します。

??? failure "動く物体に、`MeshShape` を使って、エラー・不安定になる"
    **`MeshShape` は、静的な物体だけ**。**動く物体は凸包・複合形状**に。

??? failure "同じ形を、物体ごとに作って、メモリを使いすぎる"
    **形を 1 回作って、`ShapeRefC` を共有**します。

??? failure "箱の大きさを、全体の幅で渡して、倍の大きさになる"
    <strong>半分の大きさ（half extent）</strong>です。

??? failure "小さな物体で、凸半径が大きくて、形が丸くなる"
    **凸半径を小さく**します。

??? failure "非一様スケールで、球が楕円にならない"
    **一部の形は非一様スケールに対応しません**。**一様スケール**にするか、**別の形**に。

??? failure "物理の形を、見た目のメッシュと同じにして、重い"
    **単純な形**（箱・カプセル・凸包）に、**簡略化**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 形は<strong>`XxxShapeSettings` ＋ `Create()`</strong>。<strong>`HasError()` を確認</strong>。<strong>結果は `ShapeRefC`（共有できる）</strong>
    - [x] <strong>基本は、箱・球・カプセル・円柱</strong>。<strong>人はカプセル</strong>。<strong>箱は半分の大きさ</strong>
    - [x] <strong>凸包は、動く物体に</strong>。<strong>`MeshShape` は、静的な物体だけ</strong>。<strong>地形は `HeightFieldShape`</strong>
    - [x] <strong>複合形状（`StaticCompoundShape`）</strong>で、<strong>凹んだ形を凸の集まりで近似</strong>
    - [x] <strong>形は共有</strong>。<strong>物理の形は見た目より単純に</strong>。<strong>重い計算はベイクしておく</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [物体（Body）](bodies.md)
- [クエリ（レイキャストなど）](queries.md)
- [3D の衝突判定](../../3d/collision-3d.md)
- [ベイク（事前計算）](../../optimize/baking.md)
