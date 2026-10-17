---
title: ピッキングとレイキャスト
tags:
  - 3Dゲーム
---

# ピッキングとレイキャスト

**画面上のクリック位置から、3D 空間のどの物体を指したかを求める**のが**ピッキング**です。やり方は、「**画面の点から、奥へ向かう光線（レイ）を作り、物体と交差判定する**」です。**レイキャスト**は、レイを飛ばして、当たりを調べる処理全般を指し、射撃（ヒットスキャン）、地面の高さ、視線が通るかの判定にも使います。このページは、スクリーン座標からレイを作る方法と、各形状との交差判定をまとめます。

!!! tip "ポイント"
    - <strong>スクリーン座標 → レイ</strong>：<strong>近い面（z=0）と遠い面（z=1）の 2 点を逆変換</strong>して、結ぶ。SimpleMath は <strong>`Viewport::Unproject`</strong>。
    - レイは、<strong>`Ray`（始点 + 向き）</strong>。向きは、<strong>正規化</strong>する。
    - 交差判定は、<strong>`Ray::Intersects(...)`</strong>。当たれば<strong>距離 `dist`</strong> が返る。
    - <strong>複数当たったら、最も近いもの</strong>を選ぶ。
    - レイは<strong>ワールド空間</strong>。物体の境界も<strong>ワールド空間</strong>にそろえる。
    - 数が多いなら、<strong>空間分割（BVH など）で、候補を絞る</strong>。

## 仕組み

画面の 1 点は、3D 空間では、**カメラから奥へ伸びる 1 本の線**に対応します。**MVP 変換の逆**（スクリーン → ワールド）で、その線を作ります。

<svg class="fig flow" viewBox="0 0 741 280" role="img" aria-label="ピッキング：画面の 1 点から、奥へ向かうレイを作る"><defs><marker id="fl56895" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ピッキング：画面の 1 点から、奥へ向かうレイを作る</text><line x1="162.0" y1="125.0" x2="264.5" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl56895)"/><text x="213.2" y="100.0" text-anchor="middle" style="font-size:12px">z=0 をワールドへ</text><line x1="162.0" y1="171.0" x2="264.5" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl56895)"/><text x="213.2" y="184.0" text-anchor="middle" style="font-size:12px">z=1 をワールドへ</text><line x1="400.6" y1="87.0" x2="522.9" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl56895)"/><line x1="400.6" y1="209.0" x2="522.9" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl56895)"/><rect x="28.0" y="128.0" width="144" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="100.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">画面の点 (sx,sy)</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="236.0" y="44.0" width="181" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="326.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">近い面の点 near point</text><circle cx="238.0" cy="46.0" r="10" fill="#2ea043"/><text x="238.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="240.0" y="212.0" width="173" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="326.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">遠い面の点 far point</text><circle cx="242.0" cy="214.0" r="10" fill="#e5a828"/><text x="242.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="481.0" y="128.0" width="232" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="597.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">レイ 始点near・向き=far-near</text><circle cx="483.0" cy="130.0" r="10" fill="#e5484d"/><text x="483.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

## スクリーン座標からレイを作る

SimpleMath の `Viewport::Unproject` が、**逆変換を、まとめて**やってくれます。

```cpp
#include <SimpleMath.h>
using namespace DirectX::SimpleMath;

Ray MakePickRay(float mouse_x, float mouse_y, const Viewport& viewport,
                const Matrix& proj, const Matrix& view) {
  Vector3 near_point = viewport.Unproject(Vector3(mouse_x, mouse_y, 0.0f),
                                          proj, view, Matrix::Identity);
  Vector3 far_point = viewport.Unproject(Vector3(mouse_x, mouse_y, 1.0f),
                                         proj, view, Matrix::Identity);

  Vector3 direction = far_point - near_point;
  direction.Normalize();
  return Ray(near_point, direction);
}
```

| 引数 | 説明 |
| --- | --- |
| 点の `x, y` | **ウィンドウのクライアント領域の、ピクセル座標**（左上が原点） |
| 点の `z` | **0**：近い面。**1**：遠い面 |
| `viewport` | 描画に使っている `Viewport`（サイズ・深度の範囲を含む） |
| `proj`, `view`, `world` | 射影・ビュー・ワールド行列。**ワールド空間のレイが欲しいなら、`world` は単位行列** |

!!! warning "リバース Z のとき"
    リバース Z では、**近い面が 1、遠い面が 0** です（[深度とカリング](depth-culling.md)）。`z` の 0 と 1 を、**入れ替え**ます。レイの向きが、逆になります。

### マウス座標の注意

| 注意 | 説明 |
| --- | --- |
| **クライアント座標** | `GetCursorPos` はスクリーン全体の座標。**`ScreenToClient`** で、ウィンドウ内に変換 |
| **DPI スケーリング** | 高 DPI だと、論理座標と、ピクセルがずれる。**実際のピクセル**を使う |
| **ビューポートのサイズ** | ウィンドウサイズではなく、**描画領域**（ビューポート）を渡す |

### 手で作る（仕組みの確認）

```cpp
Ray MakePickRayManual(float mouse_x, float mouse_y, float width, float height,
                      const Matrix& proj, const Matrix& view) {
  float ndc_x = 2.0f * mouse_x / width - 1.0f;
  float ndc_y = 1.0f - 2.0f * mouse_y / height;

  Matrix inverse = (view * proj).Invert();
  Vector3 near_point = Vector3::Transform(Vector3(ndc_x, ndc_y, 0.0f), inverse);
  Vector3 far_point = Vector3::Transform(Vector3(ndc_x, ndc_y, 1.0f), inverse);
  ...
}
```

**`Vector3::Transform` は、`w` で割る処理を含みません**。射影行列を含む変換では、`Vector3::TransformCoord`（`w` で割る）に相当する処理が必要です。**`Unproject` を使うのが、安全**です。

## Ray と交差判定

`Ray` は、**始点 `position`** と **向き `direction`**（長さ 1）を持ちます。**`Intersects` が、当たれば `true`、距離を `dist` に返します**。

```cpp
float dist;
if (ray.Intersects(sphere, dist)) {
  Vector3 hit = ray.position + ray.direction * dist;
}
```

### 球

```cpp
DirectX::BoundingSphere sphere(center, radius);
float dist;
if (ray.Intersects(sphere, dist)) { }
```

最も速く、**当たり判定の第一候補**です。

### 軸平行ボックス（AABB）

```cpp
DirectX::BoundingBox box(center, half_extents);
if (ray.Intersects(box, dist)) { }
```

### 回転した箱（OBB）

```cpp
DirectX::BoundingOrientedBox obb(center, half_extents, rotation);
if (ray.Intersects(obb, dist)) { }
```

### 平面

```cpp
Plane ground(Vector3::Up, 0.0f);
if (ray.Intersects(ground, dist)) {
  Vector3 hit = ray.position + ray.direction * dist;
}
```

地面をクリックして、**キャラクターを移動**させる場面で、最もよく使います。

### 三角形

```cpp
if (ray.Intersects(v0, v1, v2, dist)) { }
```

**メッシュの正確な当たり判定**に使います。三角形が多いと遅いので、**まず境界（球・箱）で絞って**から、判定します。

| 形状 | 速さ | 精度 | 使いどころ |
| --- | --- | --- | --- |
| **球** | 最速 | 粗い | 最初の絞り込み、弾、敵 |
| **AABB** | 速い | 粗い | 建物、箱、ワールドの大まかな判定 |
| **OBB** | やや速い | 中 | 回転した箱 |
| **平面** | 最速 | 無限の平面 | 地面、床 |
| **三角形** | 1 つなら速いが、数が多いと重い | **正確** | メッシュの精密な判定 |

## 最も近いものを選ぶ

```cpp
struct Hit {
  Object* object = nullptr;
  float distance = FLT_MAX;
};

Hit Pick(const Ray& ray, std::vector<Object>& objects) {
  Hit best;
  for (Object& obj : objects) {
    float dist;
    if (ray.Intersects(obj.bounds, dist) && dist < best.distance) {
      best.object = &obj;
      best.distance = dist;
    }
  }
  return best;
}
```

**奥のものを貫通して選ばない**ように、**最も近い距離**を採用します。

## 物体のローカル空間で判定する

境界（ローカル座標）が、物体の回転・スケールで、ワールドに置かれている場合、**レイをローカル空間に変換**すると、**境界はそのまま**使えます。

```cpp
Matrix inverse_world = obj.world.Invert();
Ray local_ray(Vector3::Transform(ray.position, inverse_world),
              Vector3::TransformNormal(ray.direction, inverse_world));
local_ray.direction.Normalize();
```

スケールがあると、**距離が、スケールされる**ことがあります。距離が必要なときは、ワールド空間に戻して計算します。

## 使いどころ

| 用途 | やり方 |
| --- | --- |
| **マウスで物体を選ぶ**（RTS、エディター） | 画面のレイ → 全物体と判定 → 最も近い |
| **地面をクリックして移動** | 画面のレイ → 地面の平面と交差 |
| <strong>射撃（ヒットスキャン）</strong> | 銃口から、カメラの向きにレイ |
| **視線が通るか** | 敵とプレイヤーの間にレイ。壁に先に当たれば、見えない |
| **カメラの壁抜け防止** | 注視点からカメラへレイ。当たったら、手前に寄せる（[カメラ](camera.md)） |
| **地面の高さ** | キャラの上から、真下へレイ |
| **ギズモの操作** | レイと、軸の形状の判定（[ImGuizmo](../libs/imgui/imguizmo.md)） |

## たくさんの物体があるとき

全物体との判定は、**物体が数千を超えると、重く**なります。

| 方法 | 説明 |
| --- | --- |
| **空間分割**（グリッド、八分木、BVH） | **レイが通るセルだけ**を調べる（[空間分割](../optimize/algorithms.md)） |
| **境界で絞る** | まず球・AABB で判定し、当たったものだけを三角形で |
| **距離の上限** | `max_distance` を超えるものは、判定しない |
| **レイヤー** | 判定する物体の種類を絞る（敵だけ、地形だけ） |

物理エンジンには、**高速なレイキャスト**があります。物理を使うなら、そちらを使うのが、普通です（[Jolt](../libs/jolt/index.md)）。

## よくあるミス

??? failure "クリックした位置と、選ばれる物体がずれる"
    マウス座標が、**ウィンドウ全体の座標**になっています。`ScreenToClient`、DPI、ビューポートのサイズを確認します。

??? failure "レイの向きが、逆になる"
    リバース Z で、`z` の 0 と 1 が逆です。または、ビュー行列の逆を、間違えています。

??? failure "手前の物体ではなく、奥のものが選ばれる"
    最も近い距離を、比較していません。

??? failure "ワールド座標のレイと、ローカル座標の境界を比べている"
    空間が、そろっていません。どちらかを変換します。

??? failure "`direction` が正規化されておらず、距離が、おかしい"
    `Ray` の向きは、長さ 1 にします。

??? failure "近い面のすぐ前にある物体に、当たらない"
    レイの始点が、**近い面**にあります。`near` より手前は、判定されません。必要なら、カメラ位置から飛ばします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`Viewport::Unproject`</strong> で、近い面（z=0）と遠い面（z=1）を逆変換 → <strong>レイ</strong>（向きは正規化）
    - [x] マウス座標は<strong>クライアント座標・実ピクセル</strong>。<strong>リバース Z なら、0 と 1 が逆</strong>
    - [x] 判定は <strong>`ray.Intersects(形状, dist)`</strong>。<strong>最も近いもの</strong>を選ぶ
    - [x] <strong>ワールド空間にそろえる</strong>。多数なら<strong>空間分割</strong>で絞る

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [射影](projection.md)
- [3D の衝突判定](collision-3d.md)
- [空間分割](../optimize/algorithms.md)
