---
title: SimpleMath
tags:
  - 3Dゲーム
  - 数学ライブラリ
---

# SimpleMath

<div class="page-badges" markdown>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11〜</span>
`#include "SimpleMath.h"`
</div>

**SimpleMath**（シンプル マス）は、Microsoft の <strong>DirectX Tool Kit（DirectXTK）</strong> に入っている、**DirectXMath を、普通の C++ らしく書けるようにしたラッパー**です。DirectXMath の `XMVECTOR` と `XMFLOAT3` を、**1 つの型**（`Vector3`）にまとめ、`+`、`-`、`*` などの<strong>演算子</strong>と、メンバ関数（`v.Length()`、`v.Dot(w)`）で書けます。メンバ変数にも、計算にも、<strong>同じ型でそのまま</strong>使えます（16 バイト境界の問題もありません）。内部では DirectXMath を呼ぶので、遅くはなりません。<strong>普通のゲームのコードは、SimpleMath で書き、本当に速さが必要な所だけ、DirectXMath を直接使う</strong>のが、おすすめです。このサイトのサンプルは、SimpleMath の型で書き、**座標系は左手系・Y-up・+Z が前**にそろえています（SimpleMath の `Create…` 関数は右手系なので、そこだけ注意が必要です。[下](#convention)）。

!!! tip "ポイント"
    - 型は <strong>`Vector2` / `Vector3` / `Vector4`、`Matrix`、`Quaternion`、`Plane`、`Ray`、`Color`、`Viewport`</strong>。<strong>`DirectX::SimpleMath` 名前空間</strong>。
    - <strong>演算子とメンバ関数で書ける。</strong>メンバにも、`vector` の要素にもできる（アラインメントの問題なし）。
    - <strong>`XMVECTOR` / `XMMATRIX` に、自動で変換</strong>できる。DirectXMath の関数も、そのまま呼べる。
    - SimpleMath の `Create…`（`CreateLookAt` など）と `Vector3::Forward` は<strong>右手系</strong>（前は −Z）。<strong>このサイトは左手系・+Z が前</strong>なので、<strong>ビュー・射影は DirectXMath の `LH` 関数を使い、前は自前の `kForward`</strong>を使う（[下](#convention)）。
    - <strong>行ベクトル規約</strong>（`v * M`）。<strong>掛け順は左から右</strong>（`S * R * T`）。
    - 導入は <strong>vcpkg の `directxtk`</strong>（SimpleMath を含む）。

## 導入（Visual Studio）

SimpleMath は、**DirectX Tool Kit** に含まれています（[GitHub](https://github.com/microsoft/DirectXTK)）。

| 方法 | 手順 |
| --- | --- |
| <strong>vcpkg</strong> | `vcpkg install directxtk:x64-windows`（[外部ライブラリの入れ方](../vs/libraries.md#vcpkg)）。`#include <SimpleMath.h>` で使える |
| **ソースを追加** | DirectXTK のリポジトリの `Inc/SimpleMath.h`、`Inc/SimpleMath.inl`、`Src/SimpleMath.cpp` を、プロジェクトに追加する。**DirectXMath があれば**、SimpleMath だけを、ソースで追加するのが簡単 |
| NuGet | `directxtk_desktop_win10` パッケージ |

DirectXMath（`<DirectXMath.h>`）は、**Windows SDK に含まれる**ので、別に入れる必要はありません。

```cpp
#include <SimpleMath.h>

using namespace DirectX::SimpleMath;   // Vector3、Matrix、Quaternion などが使える
```

## 型

| 型 | 中身 | 対応する DirectXMath の型 |
| --- | --- | --- |
| **`Vector2`** / **`Vector3`** / **`Vector4`** | `x, y, (z, (w))` の `float` | `XMFLOAT2/3/4` |
| **`Matrix`** | 4×4 の行列（`_11`〜`_44`） | `XMFLOAT4X4` |
| **`Quaternion`** | `x, y, z, w` | `XMFLOAT4` |
| **`Plane`** | 平面（法線 + 距離） | `XMFLOAT4` |
| **`Ray`** | レイ（`position` + `direction`） | （SimpleMath 独自） |
| **`Color`** | RGBA（0〜1） | `XMFLOAT4` |
| **`Viewport`** | 画面の領域（`x, y, width, height, minDepth, maxDepth`） | `D3D11_VIEWPORT` |
| `Rectangle` | 整数の矩形 | `RECT` |

どの型も、**普通の `float` の並び**なので、メンバ変数、配列、ファイル、定数バッファにそのまま使えます。

## Vector3

```cpp
Vector3 player(1.0f, 0.0f, 2.0f);
Vector3 enemy(4.0f, 0.0f, 6.0f);

Vector3 to_enemy = enemy - player;           // 引き算（演算子）
float distance = to_enemy.Length();           // 長さ：5.0
Vector3 direction = to_enemy;
direction.Normalize();                        // その場で正規化（長さ 0 のときは、そのまま）

player += direction * (3.0f * dt);            // 加算代入、スカラー倍
```

### よく使うメンバ・静的関数

| 書き方 | 意味 | [DirectXMath](directxmath.md#dx-vector) の対応 |
| --- | --- | --- |
| `v.Length()` / `v.LengthSquared()` | [長さ](vectors.md#basics) / [長さの 2 乗](vectors.md#distance) | `XMVector3Length` / `XMVector3LengthSq` |
| `v.Normalize()` | **その場で**[正規化](vectors.md#normalize)（戻り値なし） | `XMVector3Normalize` |
| `v.Normalize(Vector3& result)` | 結果を別の変数に | `XMVector3Normalize` |
| `v.Dot(w)` | [内積](vectors.md#dot) | `XMVector3Dot` |
| `v.Cross(w)` | [外積](vectors.md#cross) | `XMVector3Cross` |
| `Vector3::Distance(a, b)` / `DistanceSquared(a, b)` | 2 点間の[距離](vectors.md#distance) / その 2 乗 | `XMVector3Length(a - b)` |
| `Vector3::Lerp(a, b, t)` | [線形補間](vectors.md#lerp) | `XMVectorLerp` |
| `Vector3::Reflect(v, normal)` | [反射](vectors.md#reflect) | `XMVector3Reflect` |
| `Vector3::Min(a, b)` / `Max(a, b)` / `Clamp(v, lo, hi)` | [要素ごと](vectors.md#componentwise) | `XMVectorMin` / `XMVectorMax` / `XMVectorClamp` |
| `Vector3::Transform(v, matrix)` | [**位置**](vectors.md#position-direction)を[行列で変換](matrices.md#transform-point)（平行移動も） | `XMVector3TransformCoord` |
| `Vector3::TransformNormal(v, matrix)` | [**方向**](vectors.md#position-direction)を[行列で変換](matrices.md#transform-point)（平行移動なし） | `XMVector3TransformNormal` |
| `Vector3::Transform(v, quaternion)` | [クォータニオン](rotation.md#quaternion)で回転 | `XMVector3Rotate` |

### 定数

| 定数 | 値 | 意味 |
| --- | --- | --- |
| `Vector3::Zero` / `One` | `(0,0,0)` / `(1,1,1)` | |
| `Vector3::UnitX` / `UnitY` / `UnitZ` | 軸の単位ベクトル | |
| **`Vector3::Up`** / `Down` | `(0,1,0)` / `(0,-1,0)` | 上・下 |
| **`Vector3::Right`** / `Left` | `(1,0,0)` / `(-1,0,0)` | 右・左 |
| `Vector3::Forward` / `Backward` | `(0,0,-1)` / `(0,0,1)` | **右手系の前は −Z**。**このサイトの左手系（前が +Z）では使わない**（[下](#convention)） |

**`Forward` が `(0, 0, -1)` であること**に注意します。これは右手系の「前」です。このサイトは左手系なので、**`Vector3::Forward` と `Backward` の意味が逆**になります。自前の定数（`kForward`）を使います（[座標系](coordinate-systems.md)）。

## Matrix

```cpp
// ワールド行列：拡大 → 回転 → 平行移動（左から右へ掛ける）
Matrix world = Matrix::CreateScale(2.0f)
             * Matrix::CreateRotationY(angle)
             * Matrix::CreateTranslation(position);

// ビュー行列とプロジェクション行列（左手系：DirectXMath の LH 関数を使う）
Matrix view = XMMatrixLookAtLH(camera_pos, target, Vector3::Up);
Matrix proj = XMMatrixPerspectiveFovLH(fov_y, aspect, 0.1f, 1000.0f);

// 頂点を、クリップ空間へ
Matrix mvp = world * view * proj;
```

### よく使うメンバ・静的関数

| 書き方 | 意味 | [DirectXMath](directxmath.md#dx-matrix) の対応 |
| --- | --- | --- |
| `Matrix::Identity` | [単位行列](matrices.md#identity) | `XMMatrixIdentity` |
| `Matrix::CreateTranslation(Vector3)` | [平行移動](matrices.md#translation) | `XMMatrixTranslation` |
| `Matrix::CreateScale(float)` / `CreateScale(Vector3)` | [拡大・縮小](matrices.md#scale) | `XMMatrixScaling` |
| `Matrix::CreateRotationX/Y/Z(float)` | 軸まわりの[回転](matrices.md#rotation-matrix)（ラジアン） | `XMMatrixRotationX` / `XMMatrixRotationY` / `XMMatrixRotationZ` |
| `Matrix::CreateFromAxisAngle(axis, angle)` | 任意の軸まわりの[回転](rotation.md#quaternion)（軸と角度） | `XMMatrixRotationAxis` |
| `Matrix::CreateFromQuaternion(q)` | [クォータニオン](rotation.md#quaternion)から | `XMMatrixRotationQuaternion` |
| `Matrix::CreateFromYawPitchRoll(yaw, pitch, roll)` | [オイラー角](rotation.md#euler)から | `XMMatrixRotationRollPitchYaw` |
| `Matrix::CreateWorld(position, forward, up)` | 位置と向きから、[ワールド行列](../3d/transforms-mvp.md#model)。**右手系の前（−Z）を想定**。このサイトでは使わず、自前の `MakeWorld`（[下](#convention)） | なし（自分で組む） |
| `Matrix::CreateLookAt(eye, target, up)` | [ビュー行列](../3d/transforms-mvp.md#view)（**右手系**。このサイトでは `XMMatrixLookAtLH` を使う。[カメラ](../3d/camera.md)） | `XMMatrixLookAtRH` |
| `Matrix::CreatePerspectiveFieldOfView(fovY, aspect, near, far)` | [透視投影](../3d/projection.md)（右手系。このサイトでは `XMMatrixPerspectiveFovLH`） | `XMMatrixPerspectiveFovRH` |
| `Matrix::CreateOrthographic(w, h, near, far)` | [正射投影](../3d/projection.md#orthographic)（右手系。このサイトでは `XMMatrixOrthographicLH`） | `XMMatrixOrthographicRH` |
| `m.Invert()` / `m.Invert(Matrix& result)` | [逆行列](matrices.md#inverse) | `XMMatrixInverse` |
| `m.Transpose()` | [転置](matrices.md#transpose) | `XMMatrixTranspose` |
| `m.Decompose(scale, rotation, translation)` | [分解](matrices.md#extract)（拡大・回転・平行移動） | `XMMatrixDecompose` |
| `m.Translation()` | [平行移動](matrices.md#extract)の成分（4 行目） | `m.r[3]` |
| `m.Right()` / `m.Up()` | 行列の、右・上の方向（回転の軸） | `m.r[0]` / `m.r[1]` |
| `m.Backward()` | 行列の 3 行目（Z 軸）。**このサイトの左手系では、これが前方向**。`m.Forward()`（その反対）は使わない | `m.r[2]` |
| `Matrix::Lerp(a, b, t)` | 行列の補間（要素ごと。回転の補間には向かない。回転は [Slerp](rotation.md#slerp)） | なし |

**ここのメンバ関数名の `Create…` は、すべて静的関数**です（`Matrix::CreateRotationY(...)`）。

## Quaternion

```cpp
// Y 軸まわりに 90 度回転
Quaternion q = Quaternion::CreateFromAxisAngle(Vector3::UnitY, XM_PIDIV2);

// ベクトルを、クォータニオンで回転する
Vector3 rotated = Vector3::Transform(kForward, q);

// 球面線形補間
Quaternion mid = Quaternion::Slerp(q0, q1, 0.5f);

// 行列に変換
Matrix m = Matrix::CreateFromQuaternion(q);
```

| 書き方 | 意味 | [DirectXMath](directxmath.md#dx-quaternion) の対応 |
| --- | --- | --- |
| `Quaternion::Identity` | 回転なし | `XMQuaternionIdentity` |
| `Quaternion::CreateFromAxisAngle(axis, angle)` | [軸と角度](rotation.md#create)から | `XMQuaternionRotationAxis` |
| `Quaternion::CreateFromYawPitchRoll(yaw, pitch, roll)` | オイラー角から | `XMQuaternionRotationRollPitchYaw` |
| `Quaternion::CreateFromRotationMatrix(m)` | 行列から | `XMQuaternionRotationMatrix` |
| `Quaternion::Slerp(a, b, t)` / `Lerp(a, b, t)` | [補間](rotation.md#slerp) | `XMQuaternionSlerp` |
| `q.Normalize()` | [正規化](rotation.md#quaternion)（長さを 1 に戻す） | `XMQuaternionNormalize` |
| `q.Inverse()` / `q.Conjugate()` | [逆回転](rotation.md#inverse) / 共役 | `XMQuaternionInverse` / `XMQuaternionConjugate` |
| `q1 * q2` | [回転の合成](rotation.md#compose)（**先に q1、次に q2**。行ベクトル規約） | `XMQuaternionMultiply` |
| `q.ToEuler()` | オイラー角へ（`Vector3`：pitch, yaw, roll） | なし |

詳しくは [回転とクォータニオン](rotation.md) を見てください。

## Ray、Plane、Viewport、Color

| 型 | 使い方 |
| --- | --- |
| **`Ray`** | `Ray ray(origin, direction);`。`ray.Intersects(box, distance)`（`BoundingBox`、`BoundingSphere`、三角形、平面との交差判定） |
| **`Plane`** | 平面。`Plane(point, normal)`、`plane.DotNormal(v)`、`plane.DotCoordinate(p)`（点との距離） |
| **`Viewport`** | `Viewport vp(0, 0, width, height);`。**`vp.Project(world_pos, proj, view, world)`**（3D → 画面）、**`vp.Unproject(screen_pos, proj, view, world)`**（画面 → 3D） |
| **`Color`** | `Color(r, g, b, a)`。`Color(Colors::Red)` のような名前付きの色もある |

`Viewport::Unproject` は、**マウスのクリック位置から、3D の位置を求める**（[ピッキング](../3d/picking-raycast.md)）のに使います。

## DirectXMath との相互変換

SimpleMath の型は、**`XMVECTOR`、`XMMATRIX`、`XMFLOAT3` などに、自動で変換**できます。

```cpp
Vector3 v(1, 2, 3);

// SimpleMath → DirectXMath（暗黙の変換）
XMVECTOR xv = v;                                       // Vector3 → XMVECTOR
XMVECTOR n = XMVector3Normalize(v);                    // DirectXMath の関数に、そのまま渡せる

// DirectXMath → SimpleMath（代入）
Vector3 back = XMVector3Cross(v, Vector3::Up);         // XMVECTOR → Vector3

// Matrix も同様
Matrix m;
XMMATRIX xm = m;
Matrix m2 = XMMatrixTranslation(1, 2, 3);
```

つまり、**SimpleMath を基本にして、DirectXMath の関数が必要なときだけ、混ぜて使えます**。

## 速さ

| 項目 | 説明 |
| --- | --- |
| **内部は DirectXMath** | 各演算が、`XMLoad` → 計算 → `XMStore`。**1 回の演算は、SIMD** |
| **DirectXMath を、手で連続して使う場合より、少し遅い** | 演算のたびに、ロード・ストアが入る（コンパイラの最適化で、かなり消える） |
| **ふつうのゲームでは、十分速い** | 毎フレームの、数百〜数千回の演算なら、問題ない |
| **ホット ループ**（数万個ぶん）は、`XMVECTOR` で直接 | [SIMD](../optimize/simd.md)、[DirectXMath](directxmath.md) |

**最適化は、計測してから**です（[計測](../optimize/measure.md)）。

## このサイトの規約（左手系・+Z が前） {#convention}

SimpleMath の `Create…` 関数（`CreateLookAt`・`CreatePerspectiveFieldOfView`・`CreateWorld`）と、`Vector3::Forward`・`Matrix::Forward()` は、<strong>右手系（前が −Z）</strong>です。**型そのもの**（`Vector3`・`Matrix`・`Quaternion`）と、四則演算・内積・外積・`CreateTranslation`・`CreateScale`・`CreateRotationX/Y/Z`・クォータニオンの演算は、**手系に依存しません**。このサイトの規約（**左手系・Y-up・+Z が前**）では、**依存する部分だけを、次のように置き換えます**。

| 右手系の SimpleMath | このサイトで使うもの |
| --- | --- |
| `Matrix::CreateLookAt(eye, target, up)` | `XMMatrixLookAtLH(eye, target, up)` |
| `Matrix::CreatePerspectiveFieldOfView(...)` | `XMMatrixPerspectiveFovLH(...)` |
| `Matrix::CreateOrthographic(...)` | `XMMatrixOrthographicLH(...)` |
| `Matrix::CreateWorld(position, forward, up)` | 自前の `MakeWorld`（下） |
| `Vector3::Forward`（`(0,0,-1)`） | 自前の `kForward`（`(0,0,1)`） |
| `m.Forward()` | `m.Backward()`（3 行目。または自前の `ForwardOf`） |

```cpp
inline const Vector3 kForward(0.0f, 0.0f, 1.0f);
inline const Vector3 kBackward(0.0f, 0.0f, -1.0f);
inline const Vector3 kRight = Vector3::Right;
inline const Vector3 kUp = Vector3::Up;

inline Matrix MakeWorld(const Vector3& position, const Vector3& forward, const Vector3& up) {
  Vector3 z = forward;
  z.Normalize();
  Vector3 x = up.Cross(z);
  x.Normalize();
  Vector3 y = z.Cross(x);
  Matrix m = Matrix::Identity;
  m._11 = x.x; m._12 = x.y; m._13 = x.z;
  m._21 = y.x; m._22 = y.y; m._23 = y.z;
  m._31 = z.x; m._32 = z.y; m._33 = z.z;
  m._41 = position.x; m._42 = position.y; m._43 = position.z;
  return m;
}
```

| 点 | 説明 |
| --- | --- |
| **外積の向き** | 成分の式は同じ（`up.Cross(z)` ＝ 右）。<strong>左手系なので、幾何的な向きは「左手の法則」</strong>になる |
| **回転の向き** | `CreateRotationY(θ)` の正は、**上から見て時計回り**（前 +Z が、右 +X へ向く）。右手系の「反時計回り」と逆 |
| **三角形の巻き方向** | **時計回りが表**（Direct3D の既定）。法線は `Cross(v1 - v0, v2 - v0)` |
| **一貫性** | ビュー・射影を `LH` にそろえる。1 つでも `RH` が混ざると、画面が反転する |

DirectXTK には、`#define DIRECTX_MATH_LH` のような**全体の設定はありません**。上の置き換えを、**1 つのヘッダ（`math_conventions.h`）にまとめて**、プロジェクト全体で使います（[座標系](coordinate-systems.md)）。

## よくあるミス

??? failure "`Normalize()` の戻り値を使おうとする"
    `v.Normalize()` は、**その場で書き換えて、戻り値はありません**。結果を別に欲しいときは、`Vector3 n; v.Normalize(n);` か、コピーしてから `Normalize()` します。

??? failure "`Vector3::Forward` で前へ進んで、後ろへ進む"
    SimpleMath の `Vector3::Forward` は、**`(0, 0, -1)`**（右手系の前）です。このサイトは左手系（前が +Z）なので、`kForward` を使います。

??? failure "位置を `TransformNormal` で、方向を `Transform` で変換する"
    **位置は `Transform`**（平行移動が効く）、**方向は `TransformNormal`**（平行移動が効かない）です。逆にすると、ずれます。

??? failure "掛け順を、列ベクトルの感覚で書く"
    行ベクトル規約なので、`world = S * R * T`（拡大 → 回転 → 平行移動）です。

??? failure "`Matrix::Lerp` で、回転を補間する"
    要素ごとの補間なので、回転がつぶれます。回転は、**クォータニオンの `Slerp`** で補間します。

??? failure "右手系と左手系の関数を、混ぜて呼ぶ"
    `CreateLookAt`（右手系）と `XMMatrixPerspectiveFovLH`（左手系）を混ぜると、画面がおかしくなります。ビュー・射影は `LH` に統一します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SimpleMath ＝ <strong>DirectXMath を、普通の C++ で書けるようにしたラッパー</strong>（DirectX Tool Kit）
    - [x] 型は <strong>`Vector3`、`Matrix`、`Quaternion`、`Ray`、`Plane`、`Viewport`</strong>。メンバにも配列にも使える
    - [x] 関数の既定は<strong>右手系</strong>（前は `(0, 0, -1)`）。<strong>このサイトは左手系・+Z が前</strong>で、<strong>ビュー・射影は `LH`、前は `kForward`</strong>。<strong>行ベクトル</strong>（`S * R * T`）
    - [x] <strong>`XMVECTOR` / `XMMATRIX` と、自動で変換</strong>できる。速さが必要な所だけ DirectXMath を直接
    - [x] 導入は <strong>`vcpkg install directxtk`</strong>。普段のコードは SimpleMath で

## 関連ページ

- [3D ゲーム（目次）](../3d/index.md)
- [DirectXMath](directxmath.md)
- [座標系](coordinate-systems.md)
- [行列](matrices.md)
- [DirectX Tool Kit：SimpleMath（GitHub Wiki）](https://github.com/microsoft/DirectXTK/wiki/SimpleMath)
