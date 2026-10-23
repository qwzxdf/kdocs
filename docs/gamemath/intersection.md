---
title: 交差判定の公式集
tags:
  - ゲーム数学
---

# 交差判定の公式集

当たり判定の**基本の形**は、「図形と図形が重なっているか」「光線が何に当たるか」の 2 つです。このページは、2D・3D のゲームで繰り返し使う交差判定の公式を、式とコードでまとめたものです。3D の衝突判定全体（SAT・GJK・ブロードフェーズ）は[3D の衝突判定](../3d/collision-3d.md)、光線でのクリック選択は[ピッキング](../3d/picking-raycast.md)に書いてあります。

!!! tip "ポイント"
    - 判定は<strong>「安い判定を先、高い判定を後」</strong>の順に行う（円・AABB → 詳細な形）。
    - 距離の比較は<strong>2 乗のまま</strong>。平方根を避ける。
    - 点と円・円と円・AABB と AABBは、最も基本で最も速い。
    - 線分・光線の判定はパラメータ t（`始点 + 方向 × t`）で考える。
    - 速く動く物は、すり抜ける。光線（スイープ）で判定する。
    - 数が多いときは空間分割で、判定する組み合わせを減らす。

## 点との判定

| 判定 | 式 | コード |
| --- | --- | --- |
| **点と円** | `|P - C|² ≤ r²` | 距離の 2 乗と半径の 2 乗を比べる |
| 点と矩形（AABB） | `min ≤ P ≤ max`（各軸） | 各軸で範囲内か |
| 点と球 | 円と同じ（3D） | `|P - C|² ≤ r²` |
| 点と多角形 | 光線法・外積法 | 下記 |

```cpp
bool PointInCircle(Vector2 p, Vector2 center, float radius) {
  Vector2 d = p - center;
  return d.LengthSquared() <= radius * radius;
}

bool PointInRect(Vector2 p, Vector2 min, Vector2 max) {
  return p.x >= min.x && p.x <= max.x && p.y >= min.y && p.y <= max.y;
}
```

### 点と多角形

光線法は点から右へ水平な線を伸ばして、多角形の辺と何回交わるかを数えます。奇数回なら内側です。

```cpp
bool PointInPolygon(Vector2 p, const std::vector<Vector2>& poly) {
  bool inside = false;
  size_t n = poly.size();
  for (size_t i = 0, j = n - 1; i < n; j = i++) {
    bool crosses = (poly[i].y > p.y) != (poly[j].y > p.y);
    if (crosses) {
      float x = (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x;
      if (p.x < x) {
        inside = !inside;
      }
    }
  }
  return inside;
}
```

| 点 | 説明 |
| --- | --- |
| 凹んだ多角形も OK | 光線法は凸でなくても使える |
| 凸多角形なら外積法 | 全辺で点が同じ側（左 or 右）にあれば内側 |
| 境界上の扱い | 境界上の点は結果が不安定。許容誤差を決める |

## 図形どうしの判定

### 円と円（球と球）

```cpp
bool CircleVsCircle(Vector2 c1, float r1, Vector2 c2, float r2) {
  float r = r1 + r2;
  return (c2 - c1).LengthSquared() <= r * r;
}
```

**中心間の距離 ≤ 半径の和**です。3D の球と球も同じ式です。

### AABB と AABB

軸平行の矩形（箱）どうしは各軸で範囲が重なっているかで判定します。全ての軸で重なっていれば交差です。

```cpp
bool AabbVsAabb(Vector2 min1, Vector2 max1, Vector2 min2, Vector2 max2) {
  return min1.x <= max2.x && max1.x >= min2.x && min1.y <= max2.y && max1.y >= min2.y;
}
```

| 点 | 説明 |
| --- | --- |
| 非常に速い | 比較だけ。ブロードフェーズ（大まかな判定）の基本 |
| 3D | z 軸の比較を足すだけ |
| 回転した箱には使えない | 回転後の AABB は、元より大きくなる（OBB・SAT を使う） |
| 押し出し量 | 重なりの量が最も小さい軸の方向に、その量だけ押し出す |

### 円と AABB

矩形上の円の中心に最も近い点を求め、その点と中心の距離を調べます。

```cpp
bool CircleVsAabb(Vector2 center, float radius, Vector2 min, Vector2 max) {
  Vector2 closest(std::clamp(center.x, min.x, max.x), std::clamp(center.y, min.y, max.y));
  return (center - closest).LengthSquared() <= radius * radius;
}
```

`clamp` で最近接点を出すのが、すっきりした書き方です（円の中心が矩形の中にあるときは、最近接点が中心自身になる）。

### 球と平面

平面の式（法線 n・平面上の点 Q）に対し、球の中心 C の符号付き距離は `d = (C - Q)・n` です。

| 条件 | 意味 |
| --- | --- |
| `|d| ≤ r` | 球が平面と交差 |
| `d > r` | 平面の表側にある（交差しない） |
| `d < -r` | 平面の裏側にある |

視錐台のカリングは、6 つの平面に対して、この判定を行うものです（[深度とカリング](../3d/depth-culling.md)）。

## 線分と線分（2D）

2 本の線分 **P + t・r** と Q + u・s が交わるかを外積で調べます。

```text
r = P1 - P0,  s = Q1 - Q0
t = cross(Q0 - P0, s) / cross(r, s)
u = cross(Q0 - P0, r) / cross(r, s)
```

`0 ≤ t ≤ 1` かつ `0 ≤ u ≤ 1` なら、交差しています。

```cpp
bool SegmentIntersect(Vector2 p0, Vector2 p1, Vector2 q0, Vector2 q1, Vector2* out) {
  Vector2 r = p1 - p0;
  Vector2 s = q1 - q0;
  float denom = Cross2D(r, s);
  if (std::abs(denom) < 1e-8f) {
    return false;
  }
  Vector2 qp = q0 - p0;
  float t = Cross2D(qp, s) / denom;
  float u = Cross2D(qp, r) / denom;
  if (t < 0.0f || t > 1.0f || u < 0.0f || u > 1.0f) {
    return false;
  }
  *out = p0 + r * t;
  return true;
}
```

| 点 | 説明 |
| --- | --- |
| `denom = 0` は平行 | 平行（または一直線上）は、別処理にする |
| 交点も求まる | `P + t・r` |
| 使いどころ | 壁との衝突・視線の遮断・ロープの交差 |

## 光線（レイ）の判定

**光線**は始点 O と方向 Dを持ち、`O + D × t`（`t ≥ 0`）の点の集まりです。当たったかと当たるまでの距離 tを求めます。

### 光線と平面

```text
t = ((Q - O)・n) / (D・n)
```

```cpp
bool RayVsPlane(Vector3 o, Vector3 d, Vector3 plane_point, Vector3 normal, float* t_out) {
  float denom = d.Dot(normal);
  if (std::abs(denom) < 1e-8f) {
    return false;
  }
  float t = (plane_point - o).Dot(normal) / denom;
  if (t < 0.0f) {
    return false;
  }
  *t_out = t;
  return true;
}
```

マウスのクリック位置から、地面（y = 0 の平面）上の点を求める、といった場面で使います（[ピッキング](../3d/picking-raycast.md)）。

### 光線と球

光線の式を球の式 `|P - C|² = r²` に代入すると、t の 2 次方程式になります。

```cpp
bool RayVsSphere(Vector3 o, Vector3 d, Vector3 center, float radius, float* t_out) {
  Vector3 oc = o - center;
  float b = oc.Dot(d);
  float c = oc.Dot(oc) - radius * radius;
  float discriminant = b * b - c;
  if (discriminant < 0.0f) {
    return false;
  }
  float t = -b - std::sqrt(discriminant);
  if (t < 0.0f) {
    t = -b + std::sqrt(discriminant);
  }
  if (t < 0.0f) {
    return false;
  }
  *t_out = t;
  return true;
}
```

| 点 | 説明 |
| --- | --- |
| `d` は単位ベクトル | この式は、`d・d = 1` を前提にしている |
| 判別式 | 負なら当たらない。0 なら接する。正なら 2 点で交わる |
| 手前の交点を採る | `t` の小さいほう。負なら奥（光線の後ろ）なのでもう一方 |

### 光線と AABB（スラブ法）

各軸で「箱に入る t」と「出る t」を求め、全軸の入る t の最大と出る t の最小を比べます。

```cpp
bool RayVsAabb(Vector3 o, Vector3 inv_d, Vector3 min, Vector3 max, float* t_out) {
  float t1 = (min.x - o.x) * inv_d.x;
  float t2 = (max.x - o.x) * inv_d.x;
  float tmin = std::min(t1, t2);
  float tmax = std::max(t1, t2);

  t1 = (min.y - o.y) * inv_d.y;
  t2 = (max.y - o.y) * inv_d.y;
  tmin = std::max(tmin, std::min(t1, t2));
  tmax = std::min(tmax, std::max(t1, t2));

  t1 = (min.z - o.z) * inv_d.z;
  t2 = (max.z - o.z) * inv_d.z;
  tmin = std::max(tmin, std::min(t1, t2));
  tmax = std::min(tmax, std::max(t1, t2));

  if (tmax < std::max(tmin, 0.0f)) {
    return false;
  }
  *t_out = tmin >= 0.0f ? tmin : tmax;
  return true;
}
```

| 点 | 説明 |
| --- | --- |
| `inv_d` ＝ 方向の逆数 | 割り算を避けるため、あらかじめ `1 / d` を用意（成分が 0 なら無限大になるが、IEEE の浮動小数点ではうまく動く） |
| 速い | BVH のノードの判定に、大量に使われる |
| 2D の矩形 | 同じ式から z を除く |

### 光線と三角形（Möller–Trumbore 法）

三角形との交差と当たった点の重心座標が、1 回の計算で求まります。

```cpp
bool RayVsTriangle(Vector3 o, Vector3 d, Vector3 v0, Vector3 v1, Vector3 v2, float* t_out, float* u_out, float* v_out) {
  Vector3 e1 = v1 - v0;
  Vector3 e2 = v2 - v0;
  Vector3 p = d.Cross(e2);
  float det = e1.Dot(p);
  if (std::abs(det) < 1e-8f) {
    return false;
  }
  float inv_det = 1.0f / det;
  Vector3 s = o - v0;
  float u = s.Dot(p) * inv_det;
  if (u < 0.0f || u > 1.0f) {
    return false;
  }
  Vector3 q = s.Cross(e1);
  float v = d.Dot(q) * inv_det;
  if (v < 0.0f || u + v > 1.0f) {
    return false;
  }
  float t = e2.Dot(q) * inv_det;
  if (t < 0.0f) {
    return false;
  }
  *t_out = t;
  *u_out = u;
  *v_out = v;
  return true;
}
```

| 点 | 説明 |
| --- | --- |
| `u`・`v` | 重心座標（残りは `1 - u - v`）。UV・法線の補間に使う |
| 裏面の扱い | `det` の符号で裏面を無視（カリング）することもできる |
| メッシュ全体 | 三角形が多いので、BVH で絞る（[空間分割](../optimize/algorithms.md)） |

<svg class="fig illust motion" data-fig="intersection-ray-sphere" viewBox="0 0 780 280" role="img" aria-label="レイと球の交差判定"><text x="20" y="24" class="fig-title">レイの向きを振ると、球に当たっている間だけ緑になり、最初の交点に印が出る</text><circle cx="470" cy="140" r="55" fill="#e5aa28" fill-opacity="0.35" stroke="currentColor" stroke-width="2"/><line x1="120" y1="140" stroke-width="3"><animate attributeName="x2" dur="10s" repeatCount="indefinite" values="480.0;480.5;482.0;484.5;488.1;492.6;497.9;504.2;511.3;519.1;527.5;536.6;546.1;556.1;566.3;576.7;587.2;597.7;607.9;617.9;627.5;636.6;645.1;652.8;659.8;665.8;670.8;674.8;677.7;679.4;680.0;679.4;677.7;674.8;670.8;665.8;659.8;652.8;645.1;636.6;627.5;617.9;607.9;597.7;587.2;576.7;566.3;556.1;546.1;536.6;527.5;519.1;511.3;504.2;497.9;492.6;488.1;484.5;482.0;480.5;480.0;480.5;482.0;484.5;488.1;492.6;497.9;504.2;511.3;519.1;527.5;536.6;546.1;556.1;566.3;576.7;587.2;597.7;607.9;617.9;627.5;636.6;645.1;652.8;659.8;665.8;670.8;674.8;677.7;679.4;680.0;679.4;677.7;674.8;670.8;665.8;659.8;652.8;645.1;636.6;627.5;617.9;607.9;597.7;587.2;576.7;566.3;556.1;546.1;536.6;527.5;519.1;511.3;504.2;497.9;492.6;488.1;484.5;482.0;480.5;480.0"/><animate attributeName="y2" dur="10s" repeatCount="indefinite" values="-289.0;-288.6;-287.3;-285.1;-282.0;-278.1;-273.2;-267.4;-260.6;-252.9;-244.1;-234.2;-223.3;-211.3;-198.2;-184.0;-168.7;-152.3;-134.8;-116.3;-96.7;-76.1;-54.6;-32.3;-9.2;14.6;39.0;63.8;89.0;114.4;140.0;165.6;191.0;216.2;241.0;265.4;289.2;312.3;334.6;356.1;376.7;396.3;414.8;432.3;448.7;464.0;478.2;491.3;503.3;514.2;524.1;532.9;540.6;547.4;553.2;558.1;562.0;565.1;567.3;568.6;569.0;568.6;567.3;565.1;562.0;558.1;553.2;547.4;540.6;532.9;524.1;514.2;503.3;491.3;478.2;464.0;448.7;432.3;414.8;396.3;376.7;356.1;334.6;312.3;289.2;265.4;241.0;216.2;191.0;165.6;140.0;114.4;89.0;63.8;39.0;14.6;-9.2;-32.3;-54.6;-76.1;-96.7;-116.3;-134.8;-152.3;-168.7;-184.0;-198.2;-211.3;-223.3;-234.2;-244.1;-252.9;-260.6;-267.4;-273.2;-278.1;-282.0;-285.1;-287.3;-288.6;-289.0"/><animate attributeName="stroke" dur="10s" repeatCount="indefinite" calcMode="discrete" values="#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d"/></line><circle r="8" fill="#2ea043" stroke="currentColor" stroke-width="2"><animate attributeName="cx" dur="10s" repeatCount="indefinite" values="120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;436.3;422.5;416.7;415.0;416.7;422.5;436.3;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;436.3;422.5;416.7;415.0;416.7;422.5;436.3;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0;120.0"/><animate attributeName="cy" dur="10s" repeatCount="indefinite" values="140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;96.6;112.3;126.4;140.0;153.6;167.7;183.4;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;183.4;167.7;153.6;140.0;126.4;112.3;96.6;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0;140.0"/><animate attributeName="opacity" dur="10s" repeatCount="indefinite" calcMode="discrete" values="0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;1;1;1;1;1;1;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;1;1;1;1;1;1;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0"/></circle><circle cx="120" cy="140" r="6" fill="currentColor"/><text x="106" y="164" style="font-size:12px;">原点</text><text x="20" y="262" style="font-size:12px;">当たる条件は「判別式 ≥ 0」。交点は、球に入る手前側（t が小さい方）</text></svg>

レイを少しずつ回して、当たる・外れるの切り替わりを見ます。接する瞬間（判別式が 0）が境目です。

## 速い物のすり抜け（トンネリング）

**1 フレームの移動量が、相手の厚みより大きい**と、両者が重ならないまま通り過ぎてしまいます。

| 対策 | 説明 |
| --- | --- |
| 光線で判定する | 弾の前フレームの位置から今の位置までを線分（光線）として、当たりを調べる |
| スイープ判定 | 動く図形が移動の間に当たる時刻を求める（円 vs 線分、AABB vs AABB） |
| サブステップ | 1 フレームを細かく分けて、判定する |
| 連続衝突判定（CCD） | 物理エンジンの機能（[Jolt の `Linear Cast`](../libs/jolt/queries.md)） |
| 壁を厚くする | 簡易な対処 |

<svg class="fig illust motion" data-fig="intersection-tunneling" viewBox="0 0 780 250" role="img" aria-label="すり抜け（トンネリング）"><text x="20" y="24" class="fig-title">速い弾は、1 フレームで壁を飛び越える。軌跡全体（掃引）で判定すると当たる</text><rect x="376" y="50" width="8" height="60" fill="currentColor" fill-opacity="0.6"/><text x="20" y="42" style="font-size:12px;font-weight:700">点だけ判定：すり抜ける</text><line x1="60.0" y1="80.0" x2="700.0" y2="80.0" stroke="currentColor" stroke-width="1" stroke-opacity="0.2"/><rect x="376" y="140" width="8" height="60" fill="currentColor" fill-opacity="0.6"/><text x="20" y="132" style="font-size:12px;font-weight:700">軌跡で判定：壁で止まる</text><line x1="60.0" y1="170.0" x2="700.0" y2="170.0" stroke="currentColor" stroke-width="1" stroke-opacity="0.2"/><circle cy="80" r="9" fill="#e5484d" cx="60"><animate attributeName="cx" dur="6s" repeatCount="indefinite" calcMode="discrete" values="60.0;140.0;220.0;300.0;380.0;460.0;540.0;620.0;700.0"/></circle><circle cx="60.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="140.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="220.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="300.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="380.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="460.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="540.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="620.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cx="700.0" cy="80" r="3" fill="#e5484d" fill-opacity="0.35"/><circle cy="170" r="9" fill="#2ea043" cx="60"><animate attributeName="cx" dur="6s" repeatCount="indefinite" calcMode="discrete" values="60.0;140.0;220.0;300.0;368.0;368.0;368.0;368.0;368.0"/></circle><circle cx="60.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="140.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="220.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="300.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="368.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="368.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="368.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="368.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><circle cx="368.0" cy="170" r="3" fill="#2ea043" fill-opacity="0.35"/><text x="20" y="232" style="font-size:12px;">小さな点は、各フレームでの弾の位置。点と点の間に壁があると、位置だけ調べる方式では気づけない</text></svg>

弾が速いと、1 フレームで壁を飛び越えます。位置だけでなく、前フレームから今フレームまでの軌跡（掃引）で判定するのが対策です。

## 判定の順番（ブロードとナロー）

| 段階 | 内容 |
| --- | --- |
| **ブロードフェーズ** | 大まかな絞り込み。グリッド・四分木・BVH・AABB で当たりそうな組だけを選ぶ |
| ナローフェーズ | 正確な判定。円・球・三角形・SAT など、選ばれた組だけ |

全ての組を調べると物体が n 個で n² になります。ブロードフェーズで組み合わせを減らすのが基本です（[3D の衝突判定](../3d/collision-3d.md)）。

## よくあるミス

??? failure "距離の比較で、毎回 `sqrt` を使う"
    2 乗のまま比べます。

??? failure "回転した箱を、AABB の判定で済ませる"
    回転後の AABB は、元より大きくなり、**余計に当たります**。OBB・SAT を使います。

??? failure "光線の方向が単位ベクトルでなく、`t` が距離にならない"
    方向を正規化するか、`t` を長さで補正します。

??? failure "平行な線分で `denom = 0` となり、NaN・無限大になる"
    閾値で平行を先に弾きます。

??? failure "速い弾が壁をすり抜ける"
    光線・スイープ判定・サブステップにします。

??? failure "全ての物体どうしを総当たりで判定する"
    空間分割で組み合わせを減らします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基本は<strong>点・円・AABB</strong>。距離は 2 乗のまま
    - [x] 円と AABB は`clamp` で最近接点。線分は外積で t・u
    - [x] 光線は`O + D × t`。球・平面・AABB（スラブ）・三角形（Möller–Trumbore）
    - [x] 速い物は光線・スイープ・サブステップですり抜けを防ぐ
    - [x] ブロード → ナローの 2 段階。総当たりを避ける

## 関連ページ

- [ゲーム数学](index.md)
- [ゲームでよく使うベクトル公式](vector-recipes.md)
- [3D の衝突判定](../3d/collision-3d.md)
- [ピッキング（光線）](../3d/picking-raycast.md)
- [空間分割](../optimize/algorithms.md)
