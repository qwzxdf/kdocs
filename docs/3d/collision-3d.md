---
title: 3D の衝突判定
tags:
  - 3Dゲーム
---

# 3D の衝突判定

3D の衝突判定は、**複雑なモデルを、単純な形（球・箱・カプセル）で近似**して、**重なりを調べる**のが基本です。DirectXMath に付属する **DirectXCollision**（`BoundingSphere`・`BoundingBox`・`BoundingOrientedBox`・`BoundingFrustum`）を使えば、基本の形の判定が、すぐに使えます。このページは、各形状の選び方、判定の書き方、カプセルや、段階的な判定をまとめます。

!!! tip "ポイント"
    - 複雑な形は、<strong>単純な形（コライダー）で近似</strong>する。<strong>球・箱・カプセル</strong>が基本。
    - <strong>DirectXCollision</strong>：<strong>`BoundingSphere`・`BoundingBox`（AABB）・`BoundingOrientedBox`（OBB）・`BoundingFrustum`</strong>。
    - 判定は <strong>`Intersects`</strong>（交差するか）と <strong>`Contains`</strong>（`DISJOINT` / `INTERSECTS` / `CONTAINS`）。
    - <strong>球が最速</strong>、<strong>AABB が次</strong>、<strong>OBB は重い</strong>。<strong>まず軽い形で絞る</strong>。
    - <strong>衝突判定（重なったか）と、衝突応答（どう動くか）は別</strong>。応答は、物理エンジンに任せる手もある。
    - 数が多いなら、<strong>空間分割</strong>で、判定する組み合わせを減らす。

## 形状の選び方

| 形状 | クラス | 速さ | 向いているもの |
| --- | --- | --- | --- |
| **球** | `BoundingSphere` | **最速** | 弾、キャラクターの大まかな判定、近接の検出 |
| **AABB**（軸に平行な箱） | `BoundingBox` | 速い | 建物、地形の区画、大まかな範囲 |
| **OBB**（回転した箱） | `BoundingOrientedBox` | 中 | 回転する箱、車、細長いもの |
| **カプセル** | **自作**（線分 + 半径） | 中 | **人型のキャラクター**（球と円柱の合成） |
| **視錐台** | `BoundingFrustum` | 中 | カメラの視界（[カリング](depth-culling.md)） |
| **メッシュ** | 三角形ごと | 重い | 地形・複雑な形の、**正確な**判定 |

## DirectXCollision

### 作る

```cpp
#include <DirectXCollision.h>
using namespace DirectX;

BoundingSphere sphere(XMFLOAT3(0, 0, 0), 1.0f);
BoundingBox box(XMFLOAT3(0, 0, 0), XMFLOAT3(1, 1, 1));
BoundingOrientedBox obb(XMFLOAT3(0, 0, 0), XMFLOAT3(1, 0.5f, 2), XMFLOAT4(0, 0, 0, 1));
```

| 引数 | 説明 |
| --- | --- |
| 球 | **中心**、**半径** |
| AABB | **中心**、**半分の大きさ**（`Extents`）。幅の半分であることに注意 |
| OBB | 中心、半分の大きさ、<strong>回転（クォータニオン）</strong> |

SimpleMath の `Vector3` は `XMFLOAT3` から派生しているので、**そのまま渡せます**。

### 点から作る

```cpp
BoundingBox box;
BoundingBox::CreateFromPoints(box, vertices.size(), &vertices[0].position, sizeof(Vertex));

BoundingSphere sphere;
BoundingSphere::CreateFromPoints(sphere, vertices.size(), &vertices[0].position, sizeof(Vertex));
```

メッシュの頂点から、**ぴったりの境界**を求められます。**モデル読み込み時に、1 回**計算します。

### 判定

```cpp
if (sphere.Intersects(box)) { }
if (box.Intersects(obb)) { }

ContainmentType type = box.Contains(point);
```

| 関数 | 結果 |
| --- | --- |
| **`Intersects(相手)`** | **重なっているか**（`bool`） |
| **`Contains(相手)`** | `DISJOINT`（離れている）/ `INTERSECTS`（交差）/ `CONTAINS`（完全に含む） |
| `Intersects(ray 始点, 向き, dist)` | レイとの交差（[ピッキング](picking-raycast.md)） |

### 動かす（Transform）

```cpp
BoundingSphere world_sphere;
local_sphere.Transform(world_sphere, world_matrix);
```

**ローカルの境界を、ワールドに変換**して使います。球・OBB は、回転にも対応します。**AABB は、回転すると、箱が大きくなる**（軸に平行なまま、包み直し）ことに注意します。

## 自作の判定

### 球と球

```cpp
bool SphereVsSphere(const Vector3& c1, float r1, const Vector3& c2, float r2) {
  float r = r1 + r2;
  return Vector3::DistanceSquared(c1, c2) <= r * r;
}
```

**平方根を避ける**ため、**距離の 2 乗**で比べます。

### AABB と AABB

```cpp
bool AabbVsAabb(const Vector3& min1, const Vector3& max1,
                const Vector3& min2, const Vector3& max2) {
  return min1.x <= max2.x && max1.x >= min2.x &&
         min1.y <= max2.y && max1.y >= min2.y &&
         min1.z <= max2.z && max1.z >= min2.z;
}
```

**3 つの軸のすべてで、区間が重なっている**ときに、衝突しています。

### 点から線分への最短点

カプセルの判定に必要です。

```cpp
Vector3 ClosestPointOnSegment(const Vector3& p, const Vector3& a, const Vector3& b) {
  Vector3 ab = b - a;
  float t = (p - a).Dot(ab) / ab.LengthSquared();
  t = std::clamp(t, 0.0f, 1.0f);
  return a + ab * t;
}
```

### カプセル

**カプセル**は、**線分 + 半径**です。**人型のキャラクター**に、最も向いています（転がり・段差・壁との当たりが自然）。

```cpp
struct Capsule {
  Vector3 a;
  Vector3 b;
  float radius;
};

bool CapsuleVsSphere(const Capsule& capsule, const Vector3& center, float radius) {
  Vector3 closest = ClosestPointOnSegment(center, capsule.a, capsule.b);
  float r = capsule.radius + radius;
  return Vector3::DistanceSquared(closest, center) <= r * r;
}
```

**カプセルと球の判定は、「線分上の最も近い点」と球の中心の距離**で決まります。**カプセル同士**も、線分同士の最短距離を求めて、半径の和と比べます。

## 衝突の深さと押し戻し

**当たった**だけでなく、**どれだけ食い込んでいるか**が分かれば、**押し戻し**ができます。

```cpp
struct Contact {
  Vector3 normal;
  float depth;
};

bool SphereVsSphereContact(const Vector3& c1, float r1, const Vector3& c2, float r2,
                           Contact& contact) {
  Vector3 diff = c2 - c1;
  float dist_sq = diff.LengthSquared();
  float r = r1 + r2;
  if (dist_sq > r * r) return false;
  float dist = std::sqrt(dist_sq);
  contact.normal = dist > 0.0001f ? diff / dist : Vector3::UnitY;
  contact.depth = r - dist;
  return true;
}
```

| 値 | 意味 |
| --- | --- |
| **法線** | 押し戻す向き |
| **深さ** | 食い込んだ量。**`法線 × 深さ`** だけ動かせば、離れる |

## 段階的な判定（ブロードフェーズとナローフェーズ）

物体が多いと、**全部の組み合わせ**（N²）を調べるのは、重すぎます。**2 段階**にします。

| 段階 | 目的 | 方法 |
| --- | --- | --- |
| **ブロードフェーズ** | **当たりそうな組だけ**を、**安く**選ぶ | 空間分割（グリッド・八分木・BVH）、AABB、sweep and prune |
| **ナローフェーズ** | 選んだ組を、**正確に**判定 | 球・OBB・カプセル・GJK・三角形 |

```text
全物体 1000 個 → ブロード（近くの組だけ）→ 50 組 → ナロー（正確に）→ 5 組が衝突
```

空間分割は、[空間分割](../optimize/algorithms.md)で、詳しく解説しています。

## 高速な物体（トンネリング）

**弾のように速い**物体は、**1 フレームで、壁を通り抜ける**ことがあります（トンネリング）。

| 対策 | 説明 |
| --- | --- |
| <strong>レイキャスト（スイープ）</strong> | **前フレームの位置から、今の位置へ**レイを飛ばして、間の壁を検出 |
| **サブステップ** | 1 フレームを、**小さな時間に分割**して、何度も判定 |
| <strong>連続衝突判定（CCD）</strong> | 物理エンジンの機能（Jolt など） |
| **壁を厚くする** | 簡単だが、限界がある |

## 地形・メッシュとの判定

| 方法 | 説明 |
| --- | --- |
| **高さマップ** | 地形が高さの配列なら、**XZ から高さを引く**だけで、床判定ができる。**非常に速い** |
| **三角形メッシュ** | 正確。**BVH** で、三角形を絞ってから判定 |
| **ボクセル・グリッド** | ブロック状の世界（マインクラフト風）。**セルの配列**を調べるだけ |
| **ナビメッシュ** | 歩ける場所を、多角形で。**経路探索**に使う |

## 衝突判定と衝突応答

| 役割 | 内容 |
| --- | --- |
| **衝突判定** | **重なったか**、法線・深さは何か |
| **衝突応答** | **どう動くか**（押し戻す、跳ね返る、止まる、ダメージ） |

**物理的な応答**（跳ね返り・摩擦・積み重なり）まで必要なら、**物理エンジン**（Jolt・Bullet）が適しています（[Jolt Physics](../libs/jolt/index.md)）。**自作する**のは、**当たったら、ダメージ**のような、単純な用途に向きます。

## よくあるミス

??? failure "AABB のサイズを、幅で渡してしまう"
    `BoundingBox` の第 2 引数は、**半分の大きさ**（`Extents`）です。

??? failure "ローカルの境界を、そのまま使って、当たらない"
    `Transform` で、**ワールド空間に変換**してから判定します。

??? failure "回転した物体の AABB が、大きすぎる"
    回転すると、軸に平行な箱は、大きくなります。**OBB・カプセル**を使います。

??? failure "弾が、壁を通り抜ける"
    トンネリングです。**レイキャスト**や**サブステップ**を使います。

??? failure "全物体の総当たりで、重い"
    **ブロードフェーズ**（空間分割）を入れます。

??? failure "球の判定で `sqrt` を毎回呼んで、遅い"
    **距離の 2 乗**で比べます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複雑な形は、<strong>球・AABB・OBB・カプセル</strong>で近似。<strong>速さは、球 > AABB > OBB</strong>
    - [x] <strong>DirectXCollision</strong> の <strong>`Intersects` / `Contains`</strong>。<strong>AABB の大きさは「半分」</strong>で渡す
    - [x] <strong>ワールド空間にそろえて</strong>判定（<strong>`Transform`</strong>）。<strong>2 乗の距離</strong>で比べる
    - [x] 数が多いなら、<strong>ブロードフェーズ（空間分割）→ ナローフェーズ</strong>
    - [x] 速い物は、<strong>レイキャスト・サブステップ</strong>で、トンネリングを防ぐ
    - [x] 物理的な応答が必要なら、<strong>物理エンジン</strong>

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [ピッキングとレイキャスト](picking-raycast.md)
- [深度とカリング](depth-culling.md)
- [空間分割](../optimize/algorithms.md)
- [Jolt Physics](../libs/jolt/index.md)
