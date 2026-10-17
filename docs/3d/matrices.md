---
title: 行列
tags:
  - 3Dゲーム
---

# 行列

**行列**は、**座標を変換する計算を、1 つの表（4×4 の数字）にまとめたもの**です。移動（平行移動）、回転、拡大・縮小、そして遠近感をつける投影まで、3D の変換は、すべて 4×4 の行列で表せます。しかも、**行列どうしを掛け合わせると、複数の変換が 1 つの行列にまとまる**ので、頂点 1 つ 1 つに、**1 回の掛け算**で、全部の変換を適用できます。3D の描画は、この「行列を作って、掛けて、頂点に適用する」ことの連続です。このページは、行列の**しくみ**と、**掛ける順番**という、一番間違えやすいところを説明します。

!!! tip "ポイント"
    - <strong>3D の変換は、4×4 の行列</strong>で表す。<strong>同次座標</strong>（`x, y, z, w`）を使うので、<strong>平行移動も行列で書ける</strong>。
    - <strong>行列の掛け算は、順番で結果が変わる</strong>（<strong>交換できない</strong>）。<strong>拡大 → 回転 → 平行移動</strong>の順が、ワールド行列の基本。
    - このカテゴリ（SimpleMath）は<strong>行ベクトル規約</strong>：<strong>`v * M`</strong>、<strong>左から右へ</strong>掛ける（`S * R * T`）。
    - <strong>`Vector3::Transform`（位置）と `TransformNormal`（方向）</strong>を使い分ける。
    - <strong>逆行列</strong>は「変換を元に戻す」。<strong>ビュー行列は、カメラのワールド行列の逆行列</strong>。
    - <strong>行列は、毎フレーム作り直さず、変わったときだけ更新</strong>する（ダーティ フラグ）。

## 同次座標

3D の位置 `(x, y, z)` を、**4 つ目の値 w を足した `(x, y, z, w)`** で表します。これが**同次座標**です。なぜ 4 つにするかというと、**3×3 の行列では、平行移動を表せない**からです（掛け算だけでは、足し算の「移動」を表現できない）。w を 1 にすることで、**平行移動も行列の掛け算**にできます。

| 種類 | 同次座標 | 平行移動 |
| --- | --- | --- |
| <strong>位置（点）</strong> | `(x, y, z, 1)` | **効く** |
| <strong>方向（ベクトル）</strong> | `(x, y, z, 0)` | **効かない** |

## 基本の変換行列

SimpleMath は、**行ベクトル規約**（`v' = v * M`）です。平行移動の値は、**行列の 4 行目**に入ります。

### 平行移動

```text
        ┌ 1  0  0  0 ┐
T(x,y,z)│ 0  1  0  0 │      4 行目 (x, y, z, 1) が、移動量
        │ 0  0  1  0 │
        └ x  y  z  1 ┘
```

```cpp
Matrix t = Matrix::CreateTranslation(Vector3(3.0f, 0.0f, -2.0f));
```

### 拡大・縮小

```text
        ┌ sx 0  0  0 ┐
S(sx,sy,sz)│ 0  sy 0  0 │     対角線が、各軸の倍率
        │ 0  0  sz 0 │
        └ 0  0  0  1 ┘
```

```cpp
Matrix s = Matrix::CreateScale(2.0f);                    // 全部 2 倍
Matrix s2 = Matrix::CreateScale(Vector3(1.0f, 2.0f, 1.0f));   // Y だけ 2 倍
```

### 回転

軸まわりの回転は、`sin` と `cos` が入った行列です。SimpleMath の `CreateRotationX/Y/Z` は、**ラジアン**で角度を受け取ります。

```cpp
Matrix ry = Matrix::CreateRotationY(DirectX::XM_PIDIV2);              // Y 軸まわりに 90 度
Matrix r = Matrix::CreateFromAxisAngle(Vector3::UnitY, angle);        // 任意の軸まわり
Matrix rq = Matrix::CreateFromQuaternion(q);                          // クォータニオンから
```

| 角度の単位 | 変換 |
| --- | --- |
| 度 → ラジアン | `degrees * XM_PI / 180`（`DirectX::XMConvertToRadians(deg)`） |
| ラジアン → 度 | `XMConvertToDegrees(rad)` |

**右手系の回転方向**: 軸の正の方向から見て、**反時計回り**が正（[座標系](coordinate-systems.md)）。

## 行列を掛ける順番

**一番間違えやすい**ところです。行ベクトル規約では、**変換を適用する順番の通りに、左から右へ**並べます。

```cpp
// 「拡大 → 回転 → 平行移動」の順に適用するワールド行列
Matrix world = Matrix::CreateScale(2.0f)
             * Matrix::CreateRotationY(angle)
             * Matrix::CreateTranslation(position);

// 頂点の変換：頂点 × ワールド × ビュー × プロジェクション（左から順に）
Vector4 clip = Vector4::Transform(Vector4(local.x, local.y, local.z, 1.0f), world * view * proj);
```

| 規約 | 変換の式 | `拡大 → 回転 → 平行移動` の書き方 |
| --- | --- | --- |
| **行ベクトル**（SimpleMath、DirectXMath、HLSL の `mul(v, M)`） | `v' = v * M` | **`S * R * T`**（左から右） |
| **列ベクトル**（glm、OpenGL の数式、数学の教科書） | `v' = M * v` | **`T * R * S`**（右から左） |

### 順番を変えると、何が起きるか

「**回転 → 平行移動**」と「**平行移動 → 回転**」は、結果が全然違います。

<div class="anim" data-type="graph" data-label="順番で結果が変わる：回転してから移動 vs 移動してから回転">
n o 原点 0 1
n a 物体 1 1 hit
# 最初：物体は原点から右に 1 離れている
---
n o 原点 0 1
n a 物体 1 0 hit
l o a hit 原点まわりに回転
# 回転 → 移動：まず自分の中心で回る（その場で向きが変わる）。そのあとで、決まった場所へ動く。普通のワールド行列はこれ
---
n o 原点 0 1
n a 物体 1 2 hit
l o a hit 回転してから移動した位置
# 移動 → 回転：まず離れた位置へ動き、それから原点まわりに回る。物体が、原点のまわりを、公転するように動く
</div>

| 順番 | 動き | 使いどころ |
| --- | --- | --- |
| **拡大 → 回転 → 平行移動**（`S * R * T`） | 物体が、**その場で**回って、決まった位置に置かれる | **普通のワールド行列**（物体を、世界に置く） |
| **平行移動 → 回転**（`T * R`） | 物体が、**原点を中心に**回る（公転） | 「原点のまわりを回る」動き（衛星） |
| **回転 → 拡大**（`R * S`） | 回転した軸に沿って、ゆがんで拡大される（せん断） | 避ける（意図しない変形になる） |

**親子関係**（階層）は、**子のローカル行列 × 親のワールド行列**で、ワールド行列を求めます。

```cpp
// 子オブジェクトのワールド行列 ＝ 子のローカル行列 × 親のワールド行列
Matrix child_world = child_local * parent_world;
```

## 位置と方向の変換

```cpp
Vector3 world_pos = Vector3::Transform(local_pos, world);          // 位置：平行移動も効く
Vector3 world_dir = Vector3::TransformNormal(local_dir, world);     // 方向：平行移動は効かない
```

| 変換するもの | 使う関数 | 理由 |
| --- | --- | --- |
| **位置**（頂点、オブジェクトの場所） | `Vector3::Transform` | w = 1 として、平行移動も適用 |
| **方向**（前方向、速度） | `Vector3::TransformNormal` | w = 0 として、回転と拡大だけ適用 |
| **法線**（面の向き） | 逆転置行列で（[ライティング](lighting-normals.md)） | **非均一な拡大**があると、普通の方向の変換では、ずれる |

## 行列から取り出す

| 取り出すもの | 方法 |
| --- | --- |
| **位置**（平行移動） | `world.Translation()`（4 行目） |
| **前・上・右の方向** | `world.Forward()`、`world.Up()`、`world.Right()`（回転の部分。拡大があると、長さが 1 ではない） |
| **拡大・回転・位置に分解** | `world.Decompose(scale, rotation, translation)` |

```cpp
Vector3 scale, translation;
Quaternion rotation;
if (world.Decompose(scale, rotation, translation)) {
  // scale, rotation, translation が得られる
}
```

## 逆行列

**逆行列**は、「**ある変換を、元に戻す変換**」です（`M × M⁻¹ = 単位行列`）。

```cpp
Matrix inverse = world.Invert();            // 逆行列を返す（元は変わらない版：Invert(result)）

Matrix inv;
world.Invert(inv);                          // 結果を、別の変数に
```

| 使いどころ | 説明 |
| --- | --- |
| **ビュー行列** | **カメラのワールド行列の逆行列**。カメラを世界に置く変換の逆が、「世界をカメラから見る」変換 |
| **ワールド → ローカル** | 世界の座標を、あるオブジェクトの内側の座標に直す（レイと、動くオブジェクトの当たり判定） |
| **スクリーン → ワールド** | プロジェクションとビューの逆行列で、マウス位置から 3D の位置を求める（[ピッキング](picking-raycast.md)） |
| **法線の変換** | 逆行列を転置したもの |

| 注意 | 説明 |
| --- | --- |
| **逆行列は、重い** | 毎フレーム何度も求めない。変わったときだけ、結果を覚える |
| **拡大が 0 の行列は、逆行列がない** | 拡大に 0 を入れない |
| **回転と平行移動だけの行列は、安く求まる** | 回転部分を転置して、平行移動を逆に変換（汎用の `Invert` より速い） |

## 行優先と列優先（メモリ上の並び）

4×4 の行列を、メモリにどう並べるかが、**行優先**と**列優先**で違います。**ベクトルの規約（行 / 列）とは別の話**ですが、混同しやすいので、整理します。

| 項目 | 内容 |
| --- | --- |
| **SimpleMath の `Matrix`** | 行優先（`_11, _12, _13, _14, _21, ...` の順） |
| **HLSL の既定** | 列優先（`column_major`） |
| **glm / OpenGL** | 列優先 |
| **ImGuizmo** | 列優先の `float[16]` を想定 |

SimpleMath の行列を、HLSL に渡すとき、**`row_major` を指定するか、転置して送る**必要があります（[MVP 変換](transforms-mvp.md)）。

## 速さ

| 項目 | 説明 |
| --- | --- |
| **行列の掛け算** | 4×4 で、64 回の掛け算と 48 回の足し算。SIMD で速い |
| **頂点ごとに、`world * view * proj` を計算しない** | **CPU で 1 回だけ**掛けて（`mvp`）、GPU に渡す |
| **静的なオブジェクトは、ワールド行列を覚える** | 毎フレーム作り直さない |
| **ダーティ フラグ** | 位置・回転・拡大が変わったときだけ、行列を再計算（[アルゴリズムとデータ構造](../optimize/algorithms.md#dirty)） |
| **大量のオブジェクト** | 行列を連続した配列に並べて、SIMD で一括して計算（[メモリとキャッシュ](../optimize/memory-cache.md)） |

## ゲームでの使いどころ

| 場面 | 行列 |
| --- | --- |
| オブジェクトを、世界に置く | ワールド行列 ＝ `S * R * T` |
| 親（キャラ）に、子（武器）が付いて動く | `子のローカル * 親のワールド` |
| カメラから見た画面にする | ビュー行列・プロジェクション行列（[MVP](transforms-mvp.md)） |
| ボーンのアニメーション | ボーンごとの行列の階層（[スキニング](skinning-animation.md)） |
| ビルボード（常にカメラを向く板） | ビュー行列の回転を使って、向きを作る（`Matrix::CreateBillboard`） |
| マウスの位置から、3D のレイを作る | 逆行列で、スクリーン → ワールド |

## よくあるミス

??? failure "掛け順を、列ベクトルの感覚で書く"
    行ベクトル規約（SimpleMath）では、`S * R * T` です。`T * R * S` と書くと、平行移動が拡大・回転の影響を受けて、物体が遠くへ飛びます。

??? failure "位置を `TransformNormal`、方向を `Transform` で変換する"
    位置は `Transform`（平行移動が効く）、方向は `TransformNormal`（効かない）です。逆にすると、位置がずれる・方向が狂います。

??? failure "非均一な拡大のモデルで、法線を普通に変換する"
    `(1, 2, 1)` のような拡大があると、法線の向きが狂って、ライティングが壊れます。逆転置行列を使います（[ライティング](lighting-normals.md)）。

??? failure "毎フレーム、逆行列を何度も計算する"
    重い計算です。結果を覚えて、元の行列が変わったときだけ、求め直します。

??? failure "HLSL に、SimpleMath の行列をそのまま渡して、画面がおかしくなる"
    メモリの並び（行優先）と、HLSL の既定（列優先）が違います。`row_major` を指定するか、転置して送ります。

??? failure "角度を度で渡す"
    `CreateRotationY(90.0f)` は、90 ラジアン（約 5157 度）です。ラジアン（`XMConvertToRadians(90.0f)` など）で渡します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 3D の変換は<strong>4×4 の行列</strong>。<strong>同次座標</strong>（位置は w=1、方向は w=0）
    - [x] <strong>行ベクトル規約</strong>（SimpleMath）：<strong>`S * R * T`</strong>、<strong>左から右</strong>に掛ける。順番で結果が変わる
    - [x] <strong>位置は `Transform`、方向は `TransformNormal`</strong>
    - [x] <strong>ビュー行列 ＝ カメラのワールド行列の逆行列</strong>。逆行列は重いので、覚える
    - [x] 行列は<strong>CPU で 1 回掛けて</strong> GPU に渡す。変わったときだけ更新する
    - [x] 角度は<strong>ラジアン</strong>。HLSL には <strong>`row_major`</strong>（または転置）

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [SimpleMath](simplemath.md)
- [MVP 変換](transforms-mvp.md)
- [座標系](coordinate-systems.md)
- [回転とクォータニオン](rotation.md)
