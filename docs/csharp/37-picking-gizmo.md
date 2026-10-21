---
title: 第 37 章 ピッキングとギズモ
tags:
  - C#連携
---

# 第 37 章 ピッキングとギズモ

この章で、ビューポートの<strong>物をクリックして選べる</strong>ようにし、選んだ物に出る<strong>矢印（ギズモ）をドラッグして動かせる</strong>ようにします。3D エディタの操作感を決める、大事な章です。数学（レイ、逆行列、2 本の直線の最近点）が多く出てきますが、1 つずつ説明します。

## この章の考え方

### 2D の画面から、3D の世界を指す

画面上の 1 点（ピクセル）は、3D の世界では<strong>1 本の半直線（レイ）</strong>に対応します。カメラの目から出て、そのピクセルを通り、奥へ伸びる線です。

```text
 カメラ ●───────────────────────────────▶  レイ（クリックした点を通る線）
        \                       箱 ■ ← この箱に当たれば「選んだ」
         ╲  ピクセル
          ▕ 画面
```

この線が、どの物と最初に交わるかを調べるのが、<strong>ピッキング</strong>です。やることは 3 つです。

1. クリックしたピクセルから、<strong>レイを作る</strong>（逆行列で、画面 → 世界に戻す）。
2. レイと各物（箱）の<strong>交差を調べる</strong>。
3. 一番近い物を返す。

### 誰が何を担当するか

第 34 章で「データの持ち主はエディタ、エンジンは写し」と決めました。ここでの役割分担は次のとおりです。

| 仕事 | 担当 | 理由 |
| --- | --- | --- |
| 物との交差判定（ピッキング） | <strong>エンジン</strong> | 物の形（メッシュ、当たり判定）を知っているのは、エンジン |
| カメラの行列を教える | <strong>エンジン</strong> | カメラ（回転・ズーム）は、エンジンが持つ |
| ギズモを<strong>描く</strong> | <strong>エンジン</strong> | 描画はエンジンの仕事 |
| ギズモの<strong>ドラッグ操作</strong>（どの矢印か、どれだけ動かすか） | <strong>エディタ</strong> | 結果は「物を動かす編集」で、Undo/Redo の対象になる。編集は、エディタの責任 |

エンジンは、「<strong>カメラの情報</strong>」と「<strong>ピッキングの結果</strong>」を返し、エディタは、それを使って<strong>編集</strong>します。

## この章のゴール

- クリックで物を選べる。`Ctrl + クリック`で追加選択。何もない所をクリックで選択解除。
- 選んだ物の位置に、X（赤）・Y（緑）・Z（青）の矢印が出る。画面上の大きさは一定。
- 矢印をドラッグすると、その軸方向に物が動く。
- 矢印のドラッグ中は、カメラが動かず、物だけが動く。

## 手順 1：レイと箱の交差（エンジン）

### 画面の点から、レイを作る

`Engine\src\Picking.h`:

```cpp
#pragma once

#include <SimpleMath.h>

namespace mini {

struct Ray {
  DirectX::SimpleMath::Vector3 origin;
  DirectX::SimpleMath::Vector3 direction;   // 正規化済み
};

// ピクセル座標 (x, y)（左上が原点）から、ワールド空間のレイを作る。
Ray MakeRay(float x, float y, float width, float height, const DirectX::SimpleMath::Matrix& view_proj);

// レイと、ワールド行列を持つ単位立方体（-0.5〜0.5）の交差。当たれば t（レイ上の距離）を返す。
bool IntersectBox(const Ray& ray, const DirectX::SimpleMath::Matrix& world, float* out_t);

}  // namespace mini
```

`Engine\src\Picking.cpp`:

```cpp
#include "Picking.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace mini {

using namespace DirectX::SimpleMath;

Ray MakeRay(float x, float y, float width, float height, const Matrix& view_proj) {
  // ① ピクセル座標を、正規化デバイス座標 (-1〜1) に変える。画面の上が +Y なので、Y は反転する。
  const float ndc_x = 2.0f * x / width - 1.0f;
  const float ndc_y = 1.0f - 2.0f * y / height;

  // ② 画面から世界へ戻す行列は、view_proj の逆行列。
  const Matrix inverse = view_proj.Invert();

  // ③ 手前の面 (z = 0) と奥の面 (z = 1) の 2 点を、世界へ戻す。Direct3D の深度は 0〜1。
  const Vector3 near_point = Vector3::Transform(Vector3(ndc_x, ndc_y, 0.0f), inverse);
  const Vector3 far_point = Vector3::Transform(Vector3(ndc_x, ndc_y, 1.0f), inverse);

  Ray ray;
  ray.origin = near_point;
  ray.direction = far_point - near_point;
  ray.direction.Normalize();
  return ray;
}
```

| 部分 | 説明 |
| --- | --- |
| 正規化デバイス座標（NDC） | 画面の左端が −1、右端が +1、下端が −1、上端が +1 の座標。投影行列の出力が、この範囲になる |
| `1.0f - 2.0f * y / height` | ピクセルは<strong>上が 0</strong>、NDC は<strong>上が +1</strong>なので、反転する |
| `view_proj.Invert()` | 逆行列。`view * projection` で「世界 → 画面」に変えたので、逆行列で「画面 → 世界」に戻せる |
| `Vector3::Transform(v, m)` | 点を行列で変換し、<strong>最後に w で割る</strong>（遠近の除算）。逆の変換でも、必要 |
| 2 点を結ぶ | 手前の面と奥の面の、<strong>同じピクセルに対応する 2 点</strong>を結べば、レイの方向が分かる |
| `Normalize()` | 長さを 1 にする |

### 箱との交差（スラブ法）

箱の判定は、<strong>物のローカル空間</strong>に直すと簡単になります。箱の変換（回転・拡大・移動）の逆を、レイに掛ければ、「軸に平行な、単位立方体」と「レイ」の判定になるからです。

```cpp
bool IntersectBox(const Ray& ray, const Matrix& world, float* out_t) {
  // レイを、箱のローカル空間に移す。
  const Matrix inverse = world.Invert();
  const Vector3 origin = Vector3::Transform(ray.origin, inverse);
  const Vector3 direction = Vector3::TransformNormal(ray.direction, inverse);   // 方向は平行移動を受けない

  // スラブ法：3 つの軸ごとに、「この 2 枚の平面の間に入っている t の範囲」を求め、重なりを取る。
  float t_min = 0.0f;
  float t_max = std::numeric_limits<float>::max();
  const float o[3] = {origin.x, origin.y, origin.z};
  const float d[3] = {direction.x, direction.y, direction.z};

  for (int axis = 0; axis < 3; ++axis) {
    if (std::abs(d[axis]) < 1e-8f) {
      // この軸に平行：スラブの外にいれば当たらない
      if (o[axis] < -0.5f || o[axis] > 0.5f) return false;
      continue;
    }
    float t1 = (-0.5f - o[axis]) / d[axis];
    float t2 = (0.5f - o[axis]) / d[axis];
    if (t1 > t2) std::swap(t1, t2);
    t_min = std::max(t_min, t1);
    t_max = std::min(t_max, t2);
    if (t_min > t_max) return false;
  }
  *out_t = t_min;
  return true;
}

}  // namespace mini
```

| 部分 | 説明 |
| --- | --- |
| `TransformNormal` | 方向のベクトル用の変換。平行移動（行列の最下行）を<strong>無視</strong>する |
| 方向を正規化しない | ローカル空間では長さが変わる（拡大のため）。ただし、<strong>レイ上の位置 `origin + t * direction` は、ワールドとローカルで同じ `t`</strong> なので、そのまま `t` をワールドの距離として使える（`direction` の長さがワールドの長さとして保たれているため） |
| スラブ | 2 枚の平行な平面にはさまれた領域。箱は、X、Y、Z の 3 つのスラブの共通部分 |
| `t_min`/`t_max` | レイが箱に<strong>入る</strong>距離と<strong>出る</strong>距離。`t_min > t_max` なら、入る前に出ている＝当たらない |
| 平行のとき | `d[axis] ≈ 0` なら除算できない。レイがスラブの内側にあれば常に OK、外側なら絶対に当たらない |

## 手順 2：ピッキングとカメラ情報の API

`EngineApi.h` に追加します。

```c
/* カメラ情報：行列は 4x4 の行優先（行ベクトル用）、float 16 個 */
typedef struct MeCameraInfo {
  float    view[16];
  float    projection[16];
  uint32_t viewport_width;
  uint32_t viewport_height;
} MeCameraInfo;

/* ピッキング：(x, y) は、ビューポート内のピクセル座標。当たらなければ *out_id = 0 */
ME_API MeResult me_scene_pick(MeEngine* engine, float x, float y, uint32_t* out_id);
ME_API MeResult me_camera_get_info(MeEngine* engine, MeCameraInfo* out_info);

/* ギズモ：visible が 0 なら消す。position はワールド座標。size_pixels は画面上の矢印の長さ。
   active_axis は強調する軸（0=X, 1=Y, 2=Z, -1=なし） */
ME_API MeResult me_gizmo_set(MeEngine* engine, int32_t visible, const float position[3], float size_pixels,
                             int32_t active_axis);
```

`me_scene_pick` の実装の中身（エンジン側）:

```cpp
ObjectId Engine::Pick(float x, float y) {
  auto& s = *impl_;
  const float w = float(s.desc.width), h = float(s.desc.height);
  const Matrix view_proj = s.camera.View() * s.camera.Projection(w / h);
  const Ray ray = MakeRay(x, y, w, h, view_proj);

  ObjectId best = 0;
  float best_t = std::numeric_limits<float>::max();
  for (const auto& [id, object] : s.scene.Objects()) {
    float t;
    if (IntersectBox(ray, s.scene.WorldMatrix(object), &t) && t < best_t) {
      best_t = t;
      best = id;
    }
  }
  return best;
}
```

C# の宣言（`NativeMethods`）:

```csharp
[StructLayout(LayoutKind.Sequential)]
internal unsafe struct MeCameraInfo
{
    public Matrix4x4 View;           // float × 16（64 バイト）
    public Matrix4x4 Projection;
    public uint ViewportWidth;
    public uint ViewportHeight;
}

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_pick(EngineHandle engine, float x, float y, out uint id);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_camera_get_info(EngineHandle engine, out MeCameraInfo info);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static unsafe partial MeResult me_gizmo_set(EngineHandle engine, int visible, float* position, float sizePixels, int activeAxis);
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `System.Numerics.Matrix4x4` | 4×4 の行列。`float` が 16 個（`M11`〜`M44`）、行優先で並ぶ構造体（64 バイト）。<strong>C++ の SimpleMath の `Matrix` と同じ並び</strong>で、行ベクトルの約束も同じ |
| `Matrix4x4.CreateLookAt` など | 右手系の作成関数が、そろっている |
| `out MeCameraInfo info` | 出力引数として構造体を受け取る。構造体全体は、C 側が書き込む |

`IEngineService` に、`Pick`、`GetCameraInfo`、`SetGizmo` を足します（P/Invoke の呼び出しを 1 行ずつ包むだけです）。

```csharp
public sealed record CameraInfo(Matrix4x4 View, Matrix4x4 Projection, uint Width, uint Height);

uint Pick(float x, float y);
CameraInfo GetCameraInfo();
void SetGizmo(bool visible, Vector3 position, float sizePixels, int activeAxis);
```

## 手順 3：クリックで選ぶ

クリックとドラッグを区別します。<strong>押した位置と離した位置が近ければクリック</strong>です。

`ViewportViewModel` を、第 32 章の `IRenderLoop` に加えて、`ISelectionService` と `SceneDocument` を受け取る形にします。

```csharp
private Vector2 _downPosition;
private bool _leftDown;
private const float ClickTolerance = 4f;      // ピクセル

public void OnInput(Controls.InputType type, int button, float x, float y, float delta, bool ctrl)
{
    // 左ボタン以外・左ボタンの移動は、エンジンのカメラ操作へ
    if (button == 0)
    {
        if (type == Controls.InputType.ButtonDown)
        {
            _leftDown = true;
            _downPosition = new Vector2(x, y);
        }
        else if (type == Controls.InputType.ButtonUp && _leftDown)
        {
            _leftDown = false;
            if (Vector2.Distance(_downPosition, new Vector2(x, y)) <= ClickTolerance)
            {
                PickAt(x, y, ctrl);               // 動いていない → クリック
            }
        }
        return;
    }
    _loop.Post(engine => engine.SendInput((int)type, button, x, y, delta, 0, 0));
}

private void PickAt(float x, float y, bool additive)
{
    uint id = _loop.Invoke(engine => engine.Pick(x, y));     // 結果が欲しいので、同期で聞く
    var obj = id == 0 ? null : _document.Find(id);
    if (obj == null && !additive) _selection.Clear();
    else if (obj != null) _selection.Select(obj, additive);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Vector2.Distance(a, b)` | 2 点間の距離 |
| `_loop.Invoke(engine => engine.Pick(x, y))` | 描画スレッドに頼んで、結果を<strong>待って</strong>受け取る（第 32 章）。クリック 1 回に 1 回だけなので、待ってよい |
| 左ボタンのカメラ操作 | 右・中ボタンだけがカメラを動かす（第 33 章）。左ボタンの `MouseMove` も、エンジンには送らない |
| `ctrl` | `Ctrl` キーが押されているか。`ViewportHost` で `GetKeyState(VK_CONTROL)` から取って、イベントの引数に足す |

第 33 章でビューに書いた `Host.InputReceived += …` の行も、`ctrl` を渡す形に直します（`ViewportInputEventArgs` に `Ctrl` プロパティを足し、`ViewModel?.OnInput(e.Type, e.Button, e.X, e.Y, e.Delta, e.Ctrl)` と呼びます）。

```csharp
// ViewportHost の Raise の中で
bool ctrl = (Win32.GetKeyState(0x11) & 0x8000) != 0;   // VK_CONTROL
```

## 手順 4：ギズモを描く（エンジン）

選択した物の位置に、3 本の矢印を描きます。大きさは、<strong>画面上で一定</strong>（例えば 90 ピクセル）にします。カメラが遠ざかっても、小さくなりません。

### 画面上の大きさを、世界の長さにする

```cpp
// position の位置で、画面上の 1 ピクセルが、世界でどれだけの長さか
float WorldPerPixel(const Vector3& position, const Vector3& camera_position, float fov_y, float viewport_height) {
  const float distance = Vector3::Distance(position, camera_position);
  return 2.0f * distance * std::tan(fov_y * 0.5f) / viewport_height;
}
```

| 部分 | 説明 |
| --- | --- |
| 距離 `d` での画面の高さ | 視野角 `fov` のとき、距離 `d` にある面の高さは `2 * d * tan(fov / 2)` |
| 1 ピクセル | その高さを、ビューポートの高さ（ピクセル）で割った値 |
| ギズモの長さ | `size_pixels * WorldPerPixel(…)`。遠いほど世界の長さは大きくなり、画面上では一定 |

### 矢印を線にする

```cpp
void AddGizmo(std::vector<LineVertex>& lines, const Vector3& origin, float length, int active_axis) {
  const Vector3 axes[3] = {Vector3::UnitX, Vector3::UnitY, Vector3::UnitZ};
  const Vector4 colors[3] = {{1.0f, 0.25f, 0.25f, 1.0f}, {0.25f, 1.0f, 0.25f, 1.0f}, {0.35f, 0.5f, 1.0f, 1.0f}};

  for (int i = 0; i < 3; ++i) {
    const Vector4 color = (i == active_axis) ? Vector4(1.0f, 0.9f, 0.2f, 1.0f) : colors[i];
    const Vector3 tip = origin + axes[i] * length;
    lines.push_back({origin, color});
    lines.push_back({tip, color});

    // 矢じり：先端から後ろへ少し戻った位置に、軸に垂直な 4 方向の点を取り、先端と結ぶ
    const Vector3 u = axes[(i + 1) % 3];
    const Vector3 v = axes[(i + 2) % 3];
    const Vector3 base = tip - axes[i] * (length * 0.18f);
    const float r = length * 0.06f;
    for (const Vector3& spoke : {u * r, -u * r, v * r, -v * r}) {
      lines.push_back({tip, color});
      lines.push_back({base + spoke, color});
    }
  }
}
```

`Tick` の線の組み立てに、ギズモを追加します（`visible` のときだけ）。ギズモの長さは、`size_pixels * WorldPerPixel(position, camera.Position(), fov, height)` です。

### 注意：奥行きの扱い

第 33 章の線描画は、深度テストを<strong>していない</strong>ので、後から描いた線が上に出ます。ギズモを<strong>最後に</strong>追加すれば、常に手前に見えます（これは、ギズモとしては望ましい動作です）。

## 手順 5：ギズモのドラッグ（エディタ）

ギズモの操作は、<strong>エディタが行います</strong>。必要なのは、

- マウスのレイ（カメラの行列から作る）
- 軸（原点と方向）
- レイと軸の<strong>最近点</strong>

です。

### カメラ情報からレイを作る（C#）

`Services\GizmoController.cs`:

```csharp
using System.Numerics;
using Editor.Models;

namespace Editor.Services;

public readonly record struct Ray(Vector3 Origin, Vector3 Direction);

public sealed class GizmoController
{
    private const float SizePixels = 90f;        // エンジンが描く矢印の長さと同じにする
    private const float PickTolerancePixels = 8f;

    private readonly IRenderLoop _loop;
    private readonly ISelectionService _selection;
    private readonly ISceneEditor _editor;

    private CameraInfo? _camera;          // ドラッグ中に使う、カメラ情報のコピー
    private int _dragAxis = -1;           // 動かしている軸（-1: なし）
    private Vector3 _dragOrigin;          // ドラッグ開始時の物の位置
    private float _dragStartT;            // ドラッグ開始時の、軸上の位置

    public GizmoController(IRenderLoop loop, ISelectionService selection, ISceneEditor editor)
    {
        _loop = loop;
        _selection = selection;
        _editor = editor;
        _selection.SelectionChanged += UpdateGizmo;
    }

    public bool IsDragging => _dragAxis >= 0;

    // 選択に合わせて、ギズモの表示を更新する
    public void UpdateGizmo()
    {
        var target = _selection.Primary;
        bool visible = target != null;
        Vector3 position = target?.Position ?? Vector3.Zero;
        int axis = _dragAxis;
        _loop.Post(e => e.SetGizmo(visible, position, SizePixels, axis));
    }
```

### マウスのレイ

```csharp
    private static Ray MakeRay(CameraInfo cam, float px, float py)
    {
        // ピクセル → 正規化デバイス座標。上が +Y なので、Y を反転する。
        float ndcX = 2f * px / cam.Width - 1f;
        float ndcY = 1f - 2f * py / cam.Height;

        Matrix4x4.Invert(cam.View * cam.Projection, out var inverse);       // 行ベクトル：view → projection の順

        Vector3 Unproject(float z)
        {
            var p = Vector4.Transform(new Vector4(ndcX, ndcY, z, 1f), inverse);
            return new Vector3(p.X, p.Y, p.Z) / p.W;                          // w で割る
        }

        Vector3 near = Unproject(0f);
        Vector3 far = Unproject(1f);
        return new Ray(near, Vector3.Normalize(far - near));
    }
```

エンジン側の `MakeRay`（C++）を、そのまま C# に書き直した形です。<strong>同じ計算を C# でも持つ</strong>ことになりますが、ギズモの操作ごとにエンジンへ聞き直すと遅延が出るので、カメラ情報を一度取って、手元で計算します。

### 軸との最近点

2 本の直線（マウスのレイ `O + s*R` と、軸 `P + t*D`）の最近点を求めます。

```csharp
    // レイと軸（直線）の最近点。軸上の位置 t と、2 直線の距離を返す。
    private static (float AxisT, float Distance) ClosestOnAxis(Ray ray, Vector3 axisOrigin, Vector3 axisDir)
    {
        Vector3 w = ray.Origin - axisOrigin;
        float a = Vector3.Dot(ray.Direction, ray.Direction);      // 1（正規化済み）
        float b = Vector3.Dot(ray.Direction, axisDir);
        float c = Vector3.Dot(axisDir, axisDir);                  // 1
        float d = Vector3.Dot(ray.Direction, w);
        float e = Vector3.Dot(axisDir, w);

        float denom = a * c - b * b;
        if (MathF.Abs(denom) < 1e-6f)
        {
            // ほぼ平行：レイの原点から軸への射影を使う
            return (-e / c, float.MaxValue);
        }
        float s = (b * e - c * d) / denom;     // レイ上の位置
        float t = (a * e - b * d) / denom;     // 軸上の位置
        Vector3 onRay = ray.Origin + ray.Direction * s;
        Vector3 onAxis = axisOrigin + axisDir * t;
        return (t, Vector3.Distance(onRay, onAxis));
    }
```

| 部分 | 説明 |
| --- | --- |
| 最近点の式 | 2 直線の最短距離を与える点の組を、連立方程式で解いたもの。導出は、`(O + sR - P - tD)` が `R` と `D` の両方に垂直、という条件から |
| `denom ≈ 0` | 2 直線が平行。解が一意に決まらない。レイが軸とほぼ平行（カメラが軸の真正面）のとき、起きる |
| `AxisT` | 軸上の最近点の位置。<strong>ドラッグ量を、この差分で決める</strong> |
| `Distance` | 2 直線の最短距離。マウスが軸にどれだけ近いかを表す |

### 当たり判定とドラッグ

```csharp
    // マウスの左ボタンを押した：矢印に当たっていれば、ドラッグを始める。当たったら true（ほかの処理をしない）
    public bool TryBeginDrag(float px, float py)
    {
        var target = _selection.Primary;
        if (target == null) return false;

        _camera = _loop.Invoke(e => e.GetCameraInfo());            // ドラッグ中のカメラ情報を、1 度だけ取る
        var cam = _camera;
        Ray ray = MakeRay(cam, px, py);

        Vector3 origin = target.Position;
        float worldPerPixel = WorldPerPixel(cam, origin);
        float length = SizePixels * worldPerPixel;
        float tolerance = PickTolerancePixels * worldPerPixel;

        Vector3[] axes = { Vector3.UnitX, Vector3.UnitY, Vector3.UnitZ };
        int best = -1;
        float bestDistance = tolerance;
        for (int i = 0; i < 3; ++i)
        {
            var (t, distance) = ClosestOnAxis(ray, origin, axes[i]);
            if (t < 0f || t > length) continue;                      // 矢印の長さの範囲外
            if (distance < bestDistance)
            {
                bestDistance = distance;
                best = i;
            }
        }
        if (best < 0) return false;

        _dragAxis = best;
        _dragOrigin = origin;
        _dragStartT = ClosestOnAxis(ray, origin, axes[best]).AxisT;
        UpdateGizmo();                                              // 強調表示
        return true;
    }

    public void Drag(float px, float py)
    {
        if (_dragAxis < 0 || _camera == null || _selection.Primary is not { } target) return;

        Vector3 axis = _dragAxis switch { 0 => Vector3.UnitX, 1 => Vector3.UnitY, _ => Vector3.UnitZ };
        Ray ray = MakeRay(_camera, px, py);
        float t = ClosestOnAxis(ray, _dragOrigin, axis).AxisT;
        Vector3 position = _dragOrigin + axis * (t - _dragStartT);   // 開始時からの差分だけ動かす
        _editor.SetPosition(target, position);                       // 編集は、窓口を通す（第 38 章で Undo 対象）
        UpdateGizmo();
    }

    public void EndDrag()
    {
        _dragAxis = -1;
        _camera = null;
        UpdateGizmo();
    }

    // position の位置で、画面の 1 ピクセルが、世界でどれだけの長さか
    private static float WorldPerPixel(CameraInfo cam, Vector3 position)
    {
        Matrix4x4.Invert(cam.View, out var inverseView);
        Vector3 cameraPosition = inverseView.Translation;          // ビュー行列の逆行列の移動成分が、カメラの位置
        float distance = Vector3.Distance(position, cameraPosition);
        float tanHalfFov = 1f / cam.Projection.M22;                // 投影行列の M22 = 1 / tan(fov / 2)
        return 2f * distance * tanHalfFov / cam.Height;
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `readonly record struct Ray(Vector3 Origin, Vector3 Direction)` | 値の入れ物（構造体のレコード）。レイを表す |
| `var (t, distance) = …` | タプルの<strong>分解</strong>。戻り値の 2 つを、別々の変数に受ける |
| `Vector3 Unproject(float z)` | ローカル関数 |
| `inverseView.Translation` | `Matrix4x4` の `Translation`（`M41`〜`M43`）。ビュー行列の<strong>逆</strong>の移動成分が、ワールドでのカメラ位置 |
| `cam.Projection.M22` | 透視投影行列の `M22` は `1 / tan(fov_y / 2)`。ここから視野角を逆算する |
| `_dragAxis switch { 0 => …, _ => … }` | switch 式（第 5 章） |
| 「開始時からの差分」 | 現在の最近点の位置 `t` から、<strong>開始時の `t`</strong> を引いた分だけ動かす。マウスを押した瞬間に、物が飛ばない |
| `Invoke` は 1 度だけ | ドラッグの間は、<strong>カメラが動かない</strong>（左ボタンのドラッグでは、カメラは動かさない）ので、最初に取ったカメラ情報で足りる |

## 手順 6：ビューポートの入力を振り分ける

`ViewportViewModel.OnInput` の最初に、ギズモの処理を挟みます。

```csharp
public void OnInput(Controls.InputType type, int button, float x, float y, float delta, bool ctrl)
{
    if (button == 0 || _gizmo.IsDragging)
    {
        if (type == Controls.InputType.ButtonDown && button == 0 && _gizmo.TryBeginDrag(x, y))
        {
            return;                                   // ギズモに当たった。ピッキングはしない
        }
        if (_gizmo.IsDragging)
        {
            if (type == Controls.InputType.MouseMove) _gizmo.Drag(x, y);
            else if (type == Controls.InputType.ButtonUp) _gizmo.EndDrag();
            return;
        }
        // …（第 3 節の、クリック判定）
    }
    // …（右・中ボタン、ホイールは、エンジンのカメラ操作へ）
}
```

`GizmoController` は `RegisterSingleton` し、`ViewportViewModel` のコンストラクターで受け取ります。

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 箱をクリック | その箱が選ばれ、ツリーでも選択表示になる。黄色の枠、矢印が出る |
| 何もない所をクリック | 選択が解除される。矢印が消える |
| `Ctrl + クリック` | 選択に追加される |
| 赤い矢印をドラッグ | 箱が X 方向に動く。プロパティ パネルの位置 X が、リアルタイムに変わる |
| カメラを遠ざける | 矢印の長さは、画面上で一定 |
| 矢印の上でクリック | 矢印が黄色になり、ドラッグ中だけ強調 |
| 右ドラッグ中 | 矢印の操作は始まらない（カメラの操作が優先） |

## よくあるミス

??? failure "クリックしても選ばれない"
    ピッキングが `0` を返している。`MakeRay` の `ndc_y` の反転忘れ、`view_proj` の掛け順の逆、ビューポートの幅・高さが `Resize` で更新されていない、を確認する。

??? failure "選ぶ位置が、少しずれる"
    クリック座標は、ビューポートの<strong>クライアント座標</strong>（ピクセル）で、DPI が 100% 以外のときは、`GetClientRect` と同じ物理ピクセルで計算する。`lParam` からの値が、すでに物理ピクセル（子ウィンドウのクライアント座標）である。

??? failure "ギズモが、画面上で大きさが変わる"
    エンジンの `WorldPerPixel` と、C# の `WorldPerPixel` の式が違う。または、エンジンで `fov` を固定の値で使っている。

??? failure "矢印をドラッグすると、物が飛ぶ"
    開始時の `t` を引いていない。または、最近点の計算で `denom` がほぼ 0（軸の真正面から見ている）。カメラを少し回して試す。

??? failure "矢印のドラッグ中に、カメラが回ってしまう"
    `IsDragging` のときに、入力をエンジンに送っている。ドラッグ中は `return` して、カメラに送らない。

??? failure "物を動かすと、ギズモが遅れてついてくる"
    ギズモの位置の更新（`UpdateGizmo`）を呼んでいない。`SetPosition` の後に毎回呼ぶ。

## この章のまとめ

- 画面の点は、逆行列で<strong>レイ</strong>に戻せる。ピッキングは、レイと物の交差判定。
- 箱との交差は、レイをローカル空間に戻して、<strong>スラブ法</strong>。
- ギズモの大きさは、<strong>距離と視野角から、ピクセル数を世界の長さに換算</strong>して一定にする。
- ギズモの操作は、<strong>エディタ</strong>が行い、結果は `ISceneEditor` を通して編集として確定する。

## 次の章へ

次の章（[第 38 章 Undo/Redo](38-undo-redo.md)）では、ここまでの編集をすべて<strong>元に戻せる</strong>ようにします。コマンド パターンと、ドラッグのような連続操作を 1 つにまとめる方法を学びます。
