---
title: 第 37 章 ピッキングとギズモ
tags:
  - C#連携
---

# 第 37 章 ピッキングとギズモ

この章で、ビューポートの物をクリックして選べるようにして、選んだ物に出る矢印（ギズモ）をドラッグして動かせるようにします。3D エディタの操作感を決める章です。数学（レイ、逆行列、2 本の直線の最近点）が多く出てきますが、ひとつずつ説明します。

!!! info "このページを読む前に"
    - [第 36 章 プロパティ パネル](36-property-panel.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## 画面の 1 点は、3D では 1 本の線

画面の上の 1 点（ピクセル）は、3D の世界では、カメラの目から出て、そのピクセルを通って奥へ伸びる半直線（レイ）に当たります。

```text
 カメラ ●───────────────────────────────▶  レイ（クリックした点を通る線）
        \                       箱 ■ ← この箱に当たれば「選んだ」
         ╲  ピクセル
          ▕ 画面
```

この線が、どの物と最初に交わるかを調べるのがピッキングです。やることは 3 つです。クリックしたピクセルからレイを作ること（逆行列で、画面から世界へ戻す）、レイと各物の交差を調べること、いちばん近い物を返すことです。

### 誰が何を担当するか

第 34 章で、データの持ち主はエディタ、エンジンは写し、と決めました。ここでの役割分担も、その延長で決めます。

| 仕事 | 担当 | 理由 |
| --- | --- | --- |
| 物との交差判定（ピッキング） | エンジン | 物の形（メッシュ、当たり判定）を知っているのはエンジン |
| カメラの行列を教える | エンジン | カメラはエンジンが持っている |
| ギズモを描く | エンジン | 描画はエンジンの仕事 |
| ギズモのドラッグ操作（どの矢印か、どれだけ動かすか） | エディタ | 結果は「物を動かす編集」で、Undo/Redo の対象になる。編集はエディタの責任 |

エンジンは、カメラの情報とピッキングの結果を返し、エディタはそれを使って編集する、という分担です。

## レイと箱の交差（エンジン側）

まず、画面の点からレイを作ります。

```cpp title="Engine/src/Picking.h"
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

```cpp title="Engine/src/Picking.cpp"
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

ピクセル座標は、上が 0 ですが、正規化デバイス座標（NDC、左端が −1、右端が +1、下端が −1、上端が +1）は上が +1 なので、Y を反転しています。`view * projection` は「世界から画面」への変換でしたから、その逆行列が「画面から世界」へ戻す変換です。手前の面（`z = 0`）と奥の面（`z = 1`、Direct3D の深度は 0〜1）の、同じピクセルに対応する 2 点を世界へ戻し、結べば、レイの方向が分かります。`Vector3::Transform` は、点を変換して最後に `w` で割ってくれます（遠近の除算）。

次に、レイと箱の交差です。箱の判定は、物のローカル空間に直すと簡単になります。箱の変換（回転、拡大、移動）の逆をレイに掛ければ、「軸に平行な単位立方体」と「レイ」の判定に変わるからです。

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

これは「スラブ法」といって、箱を、X、Y、Z それぞれの「2 枚の平行な平面にはさまれた領域（スラブ）」の共通部分と見なします。軸ごとに、レイがそのスラブに入る距離 `t1` と出る距離 `t2` を求めて、3 軸ぶんの重なりを取ります。入る距離（`t_min`）が出る距離（`t_max`）を超えたら、入る前に出てしまっているので、当たりません。軸に平行なレイでは割り算ができないので、スラブの内側にあれば OK、外側なら絶対に当たらない、と別に判定します。

`TransformNormal` は、方向ベクトル用の変換で、平行移動（行列の最下行）を無視します。方向を正規化し直さないのは、意図的です。ローカル空間では長さが変わりますが、`origin + t * direction` の `t` は、ワールドでもローカルでも同じ値になるので、そのままワールドの距離として使えます。

## ピッキングとカメラ情報の API

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

`me_scene_pick` の中身（エンジン側）は、すべての物に対してレイとの交差を調べ、いちばん近いものを返します。

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

C# の宣言は次のとおりです。

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

`System.Numerics.Matrix4x4` は、`float` が 16 個（`M11` から `M44`）、行優先で並ぶ構造体（64 バイト）です。C++ の SimpleMath の `Matrix` と同じ並びで、行ベクトルの約束も同じなので、そのまま受け取れます。

`IEngineService` に、`Pick`、`GetCameraInfo`、`SetGizmo` を足します（P/Invoke の呼び出しを 1 行ずつ包むだけです）。

```csharp
public sealed record CameraInfo(Matrix4x4 View, Matrix4x4 Projection, uint Width, uint Height);

uint Pick(float x, float y);
CameraInfo GetCameraInfo();
void SetGizmo(bool visible, Vector3 position, float sizePixels, int activeAxis);
```

## クリックで選ぶ

クリックとドラッグは、押した位置と離した位置が近ければクリック、と区別します。`ViewportViewModel` が、`ISelectionService` と `SceneDocument` も受け取る形にします。

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

カメラを動かすのは右と中ボタンだけ（第 33 章）なので、左ボタンの入力はエンジンに送りません。クリックのピッキングは、結果が欲しいので `Invoke`（同期）で聞きますが、1 クリックに 1 回だけなので、待っても問題ありません。

`ctrl` は、`Ctrl` キーが押されているかです。`ViewportHost` の `Raise` の中で、`GetKeyState` から取って、イベントの引数に足します。

```csharp
// ViewportHost の Raise の中で
bool ctrl = (Win32.GetKeyState(0x11) & 0x8000) != 0;   // VK_CONTROL
```

第 33 章でビューに書いた `Host.InputReceived += ...` の行も、`ctrl` を渡す形に直します（`ViewportInputEventArgs` に `Ctrl` プロパティを足して、`ViewModel?.OnInput(e.Type, e.Button, e.X, e.Y, e.Delta, e.Ctrl)` と呼びます）。

## ギズモを描く（エンジン側）

選んだ物の位置に、3 本の矢印を描きます。大きさは、画面上で一定（たとえば 90 ピクセル）にします。カメラを遠ざけても、小さくならないようにするためです。

そのために、「画面の 1 ピクセルが、その位置では世界でどれだけの長さか」を求めます。

```cpp
// position の位置で、画面上の 1 ピクセルが、世界でどれだけの長さか
float WorldPerPixel(const Vector3& position, const Vector3& camera_position, float fov_y, float viewport_height) {
  const float distance = Vector3::Distance(position, camera_position);
  return 2.0f * distance * std::tan(fov_y * 0.5f) / viewport_height;
}
```

視野角 `fov` のとき、距離 `d` にある面の高さは `2 * d * tan(fov / 2)` です。その高さをビューポートの高さ（ピクセル）で割れば、1 ピクセルの長さが出ます。ギズモの長さは `size_pixels * WorldPerPixel(...)` とすれば、遠いほど世界の長さが大きくなり、画面上では一定になります。

矢印は、線で作ります。

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

`Tick` の線の組み立てに、ギズモを追加します（表示するときだけ）。ギズモの長さは、`size_pixels * WorldPerPixel(position, camera.Position(), fov, height)` です。

第 33 章の線描画は、深度テストをしていないので、あとから描いた線が上に出ます。ギズモを最後に追加すれば、常に手前に見えます。ギズモとしては、むしろ望ましい動きです。

## ギズモのドラッグ（エディタ側）

ギズモの操作は、エディタが行います。必要なものは、マウスのレイ（カメラの行列から作る）、軸（原点と方向）、レイと軸の最近点の 3 つです。

### カメラ情報からレイを作る

エンジン側の `MakeRay` を、そのまま C# に書き直します。ギズモの操作のたびにエンジンへ聞き直すと遅延が出るので、カメラ情報を一度だけ取って、手元で計算します。

```csharp title="Services/GizmoController.cs"
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

### 軸との最近点

ドラッグ中、マウスのレイと軸の位置関係から、「軸の上のどこをつまんでいるか」を求めます。2 本の直線（マウスのレイ `O + s*R` と、軸 `P + t*D`）の最近点を求める問題です。

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

この式は、「`(O + sR - P - tD)` が `R` と `D` の両方に垂直」という条件を、連立方程式として解いたものです。`AxisT` が軸上の最近点の位置で、`Distance` が 2 直線の最短距離（マウスが軸にどれだけ近いか）です。2 直線がほぼ平行（カメラが軸の真正面）のときは、解が決まらないので、別扱いにしています。

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

押した瞬間に、各軸について最近点を調べて、矢印の長さの範囲内で、マウスに近い（`tolerance` 以内の）軸があれば、その軸のドラッグを始めます。ドラッグ中は、現在の最近点の位置 `t` から、ドラッグ開始時の `t` を引いた分だけ物を動かします。これで、マウスを押した瞬間に物が飛ぶことがありません。

カメラ情報は、押した瞬間に一度だけ取ります。左ボタンのドラッグ中は、カメラが動かないので、それで足ります。`WorldPerPixel` のほうは、`inverseView.Translation`（ビュー行列の逆の移動成分、つまりワールドでのカメラ位置）と、`Projection.M22`（`1 / tan(fov / 2)`）から、エンジンと同じ式を再現しています。エンジンと C# で、同じ式が 2 か所にあるのは割り切りです。式がずれると、見た目の矢印と当たり判定がずれるので、変えるときは両方を変えます。

## ビューポートの入力を振り分ける

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
        // ...（前の節の、クリック判定）
    }
    // ...（右・中ボタン、ホイールは、エンジンのカメラ操作へ）
}
```

`GizmoController` は `RegisterSingleton` して、`ViewportViewModel` のコンストラクターで受け取ります。

## 動かして確かめる

- 箱をクリックすると、その箱が選ばれて、ツリーでも選択表示になる。黄色の枠と矢印が出る。
- 何もない所をクリックすると、選択が解除されて、矢印が消える。`Ctrl + クリック` で、選択に追加される。
- 赤い矢印をドラッグすると、箱が X 方向に動く。プロパティ パネルの位置 X が、リアルタイムに変わる。
- カメラを遠ざけても、矢印の長さは画面上で一定。
- 右ドラッグ中は、矢印の操作は始まらない。

??? failure "クリックしても選ばれない"
    ピッキングが `0` を返しています。`MakeRay` の `ndc_y` の反転忘れ、`view_proj` の掛け順が逆、`Resize` でビューポートの幅や高さが更新されていない、の 3 つを確かめます。

??? failure "選ぶ位置が、少しずれる"
    クリック座標は、ビューポートのクライアント座標（物理ピクセル）です。DPI が 100% 以外のとき、`GetClientRect` と同じ物理ピクセルで計算しているかを確認します。

??? failure "ギズモが、画面上で大きさが変わる"
    エンジンの `WorldPerPixel` と、C# の `WorldPerPixel` の式が違っています。または、エンジンで `fov` を固定の値で使っています。

??? failure "矢印をドラッグすると、物が飛ぶ"
    開始時の `t` を引いていません。または、最近点の計算で `denom` がほぼ 0 になっています（軸の真正面から見ている）。カメラを少し回して試します。

??? failure "矢印のドラッグ中に、カメラが回ってしまう"
    `IsDragging` のときに、入力をエンジンに送っています。ドラッグ中は `return` して、カメラに送らないようにします。

??? failure "物を動かすと、ギズモが遅れてついてくる"
    `UpdateGizmo` を呼んでいません。`SetPosition` のあとに、毎回呼びます。

## この章のまとめ

- 画面の点は、逆行列でレイに戻せる。ピッキングは、レイと物の交差判定。
- 箱との交差は、レイをローカル空間に戻して、スラブ法で調べる。
- ギズモの大きさは、距離と視野角から、ピクセル数を世界の長さに換算して、一定にする。
- ギズモの操作はエディタが行い、結果は `ISceneEditor` を通して、編集として確定する。

次の章では、ここまでの編集をすべて、元に戻せるようにします。

[第 38 章 Undo/Redo](38-undo-redo.md) へ進みます。
