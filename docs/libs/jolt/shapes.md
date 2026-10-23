---
title: 形（Shape）
tags:
  - 外部ライブラリ
  - 物理演算
---

# 形（Shape）

<strong>形（Shape）</strong>は、物体の「衝突判定に使う形」です。見た目のモデル（数万ポリゴン）とは別に単純な形（箱・球・カプセル）や、凸包・メッシュを物理用に用意します（[3D の衝突判定](../../3d/collision-3d.md)）。形によって、速さ・正確さ・使える物体の種類が変わります。このページは形の種類、作り方、複合形状、スケール・重心のずれ、選び方をまとめます。

!!! tip "ポイント"
    - 形は<strong>`XxxShapeSettings` で設定して、`Create()` で作る</strong>。<strong>結果は `ShapeRefC`（参照カウント付き）</strong>。エラーを確認する。
    - 基本の形：箱・球・カプセル・円柱。最も速く、安定。まずこれ。
    - 凸包（`ConvexHull`）は凸の形。動く物体に使える。三角形メッシュは、静的な物体だけ。
    - 複合形状（Compound）で、複数の形を、1 つの物体にまとめる（凹んだ形を凸の集まりで近似）。
    - 形は共有できる（同じ形を多数の物体で使い回し）。1 回だけ作る。
    - 見た目と物理の形は、別。物理はできるだけ単純に。

!!! info "このページを読む前に"
    - [Jolt Physics](index.md)（このセクション全体の地図と、読む順番）
    - [物理演算の全体像](overview.md)（Jolt の全体像）

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
| **`XxxShapeSettings`** | 形の設定（大きさなど） |
| `Create()` | 形を作る。`ShapeResult` を返す（エラーが含まれうる） |
| `HasError()` / `GetError()` | 失敗の確認と理由 |
| `ShapeRefC` | 形への参照（参照カウント）。コピーすると共有される。最後の参照が消えると解放 |

単純な形（`BoxShape`・`SphereShape`）は、直接 `new` で作ることもできます（エラーが起きにくいため）。

```cpp
new SphereShape(0.5f)
new BoxShape(Vec3(1, 0.5f, 2))
```

### 形を共有する

同じ形の物体が多数（弾・木・箱）あるなら、形を 1 回だけ作って、使い回します。

```cpp
ShapeRefC bullet_shape = new SphereShape(0.1f);

for (...) {
  BodyCreationSettings s(bullet_shape, pos, Quat::sIdentity(), EMotionType::Dynamic, Layers::PLAYER_BULLET);
  bodies.CreateAndAddBody(s, EActivation::Activate);
}
```

参照カウントで管理されるので、形を物体が持っている間は、解放されません。メモリの節約になります。

## 基本の形

| 形 | 作り方 | 特徴 | 用途 |
| --- | --- | --- | --- |
| **箱**（`BoxShape`） | `BoxShape(Vec3 half_extent, float convex_radius = 0.05f)` | 直方体。半分の大きさで指定 | 壁・箱・建物 |
| 球（`SphereShape`） | `SphereShape(float radius)` | 最も速く、安定 | ボール・弾・簡易な敵 |
| カプセル（`CapsuleShape`） | `CapsuleShape(float half_height, float radius)` | 円柱の両端に半球。転がりやすく、段差に強い | 人型のキャラクター |
| 円柱（`CylinderShape`） | `CylinderShape(float half_height, float radius)` | 円柱 | 樽・柱・車輪 |
| テーパー カプセル | `TaperedCapsuleShape` | 両端の半径が違う | 手足 |

### 半分の大きさ（half extent）

箱の大きさは、「半分」で指定します（中心から面までの距離）。幅 2m・高さ 1m・奥行き 4m の箱なら、`Vec3(1.0f, 0.5f, 2.0f)` です（[3D の衝突判定](../../3d/collision-3d.md)の `BoundingBox` と同じ）。

### 凸半径（convex radius）

箱などの角はわずかに丸められます（凸半径、既定 0.05）。衝突判定の安定性と速さのためです。小さな物体（大きさが凸半径より小さい）は、凸半径を小さくします。

```cpp
BoxShape(Vec3(0.05f, 0.05f, 0.05f), 0.01f)
```

### 向き（円柱・カプセルの軸）

カプセルや円柱は、Y 軸方向に伸びます（立っている形）。横向きにしたければ、回転した物体にするか、`RotatedTranslatedShape` で包みます。

## 凸包（ConvexHull）

**頂点の集まり（点群）の、外側を包む、凸の形**です。

```cpp
Array<Vec3> points = {Vec3(-1, 0, -1), Vec3(1, 0, -1), Vec3(0, 0, 1), Vec3(0, 2, 0)};
ConvexHullShapeSettings hull_settings(points);
ShapeRefC hull = hull_settings.Create().Get();
```

| 点 | 説明 |
| --- | --- |
| 凸（へこみがない） | どの 2 点を結んでも、形の内側に収まる |
| 動く物体に使える | 三角形メッシュと違い、`Dynamic` の物体でも OK |
| 点の数 | 数十〜百個程度に抑える（増えると重い） |
| 見た目のメッシュから作る | 頂点を渡す（簡略化した点群で） |

凹んだ形（ドーナツ・椅子）は、1 つの凸包では表せません。複数の凸包に分割して、複合形状にします。

## 三角形メッシュ（MeshShape）

**三角形のメッシュそのもの**を、衝突の形にします。正確ですが制限があります。

```cpp
TriangleList triangles;
triangles.push_back(Triangle(Float3(0, 0, 0), Float3(10, 0, 0), Float3(0, 0, 10)));

MeshShapeSettings mesh_settings(triangles);
ShapeRefC mesh = mesh_settings.Create().Get();
```

| 点 | 説明 |
| --- | --- |
| 静的な物体だけ（`Static`） | `Dynamic` の物体には、使えない（重い・不安定） |
| 中が空洞 | メッシュは表面だけ。内側に入った物体は、外に出せないことがある |
| 三角形が多い | メモリを使う。BVH（空間分割）が、自動で作られる |
| 用途 | 地形・建物・洞窟の静的な背景 |

地形には、`HeightFieldShape`（高さの配列）も使えます（メッシュより、軽くて速い）。

## 複合形状（Compound）

**複数の形を、1 つの物体にまとめます**。位置と向きを形ごとに指定できます。

```cpp
StaticCompoundShapeSettings compound;
compound.AddShape(Vec3(0, 0, 0), Quat::sIdentity(), new BoxShape(Vec3(1, 0.1f, 1)));
compound.AddShape(Vec3(0, 0.5f, 0), Quat::sIdentity(), new BoxShape(Vec3(0.1f, 0.5f, 0.1f)));
ShapeRefC table = compound.Create().Get();
```

| 種類 | 説明 |
| --- | --- |
| `StaticCompoundShape` | 作った後、変更できない。速い（普通はこれ） |
| `MutableCompoundShape` | 後から、形の追加・削除・移動ができる。やや重い |

用途：
- 凹んだ形を凸の組み合わせで近似（椅子・テーブル）
- キャラクターの部位ごとの判定（頭・胴・腕）
- 見た目が複雑な物体を、少数の単純な形で近似

## 形をずらす・回す・拡大する

| 形 | 説明 |
| --- | --- |
| **`RotatedTranslatedShape`** | 形を位置・向きをずらして包む（中心が物体の原点と違うとき） |
| `ScaledShape` | 形を拡大・縮小して包む（同じ形を違う大きさで共有） |
| `OffsetCenterOfMassShape` | 重心をずらす（傾きやすい・安定しやすいを調整） |

```cpp
ShapeRefC lying_capsule = RotatedTranslatedShapeSettings(
    Vec3::sZero(), Quat::sRotation(Vec3::sAxisZ(), JPH_PI * 0.5f), new CapsuleShape(1.0f, 0.3f)).Create().Get();

ShapeRefC big_box = new ScaledShape(box_shape, Vec3(2, 1, 2));
```

!!! warning "非一様スケールには、制限がある"
    `ScaledShape` で、軸ごとに違う倍率（非一様スケール）を使うと一部の形（球・カプセル）は、正しく扱えません。一様スケール（全軸同じ）が、安全です。

## 重心と慣性

<strong>物体の「重心」</strong>は、形の体積の中心で自動計算されます。

| 点 | 説明 |
| --- | --- |
| 重心と物体の原点が違う | `GetCenterOfMassPosition` と `GetPosition` で、位置が違う |
| 重心をずらしたい | `OffsetCenterOfMassShape` |
| 慣性（回しやすさ） | 形と質量から、自動計算。手動で変えることもできる |

細長い形を立てると倒れやすい（重心が高い）。重心を少し下げると安定します。

## 形の選び方

| 物体 | 形 | 理由 |
| --- | --- | --- |
| **ボール・弾** | 球 | 最速・安定 |
| 人型のキャラクター | カプセル | 段差・坂に強い |
| 箱・壁・建物 | 箱 | 単純で速い |
| 樽・柱 | 円柱 | |
| 岩・石（動く） | 凸包 | 動かせて、形が自由 |
| 椅子・テーブル（動く） | 複合形状（箱の組み合わせ） | 凹みがある |
| 地形（動かない） | `HeightFieldShape`、`MeshShape` | 静的な背景 |
| 建物・洞窟（動かない） | `MeshShape` | 凹凸が複雑 |

物理の形はできるだけ単純にします（頂点数・三角形数が少ないほど速い）。見た目のモデルと完全に同じ形にする必要は、ありません。

!!! note "ベイク（事前計算）"
    凸包の計算・メッシュの BVH の構築は、重い処理です。ステージのロード時に毎回やらず、ビルド時に物理用データとして焼いておく（クッキング）と、ロードが速くなります（[ベイク](../../optimize/baking.md)）。Jolt は、`Shape::SaveBinaryState` / `RestoreFromBinaryState` で、形のバイナリ保存ができます。

## 形の情報を調べる

| 関数 | 内容 |
| --- | --- |
| `GetLocalBounds()` | **ローカル空間の境界ボックス** |
| `GetWorldSpaceBounds(transform, scale)` | ワールド空間の境界ボックス |
| `GetVolume()` | 体積 |
| `GetMassProperties()` | 質量・慣性（密度から） |
| `GetSubType()` | 形の種類（`EShapeSubType::Box` など） |

## よくあるミス

??? failure "`Create()` のエラーを確認せず、`Get()` して、クラッシュする"
    `HasError()` を確認します。

??? failure "動く物体に、`MeshShape` を使って、エラー・不安定になる"
    `MeshShape` は、静的な物体だけ。動く物体は凸包・複合形状に。

??? failure "同じ形を、物体ごとに作って、メモリを使いすぎる"
    形を 1 回作って、`ShapeRefC` を共有します。

??? failure "箱の大きさを、全体の幅で渡して、倍の大きさになる"
    半分の大きさ（half extent）です。

??? failure "小さな物体で、凸半径が大きくて、形が丸くなる"
    凸半径を小さくします。

??? failure "非一様スケールで、球が楕円にならない"
    一部の形は非一様スケールに対応しません。一様スケールにするか、別の形に。

??? failure "物理の形を、見た目のメッシュと同じにして、重い"
    単純な形（箱・カプセル・凸包）に、簡略化します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 形は`XxxShapeSettings` ＋ `Create()`。`HasError()` を確認。結果は `ShapeRefC`（共有できる）
    - [x] 基本は、箱・球・カプセル・円柱。人はカプセル。箱は半分の大きさ
    - [x] 凸包は、動く物体に。`MeshShape` は、静的な物体だけ。地形は `HeightFieldShape`
    - [x] 複合形状（`StaticCompoundShape`）で、凹んだ形を凸の集まりで近似
    - [x] 形は共有。物理の形は見た目より単純に。重い計算はベイクしておく

## 関連ページ

- [Jolt Physics](index.md)
- [物体（Body）](bodies.md)
- [クエリ（レイキャストなど）](queries.md)
- [3D の衝突判定](../../3d/collision-3d.md)
- [ベイク（事前計算）](../../optimize/baking.md)
