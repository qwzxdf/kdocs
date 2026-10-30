---
title: 第 40 章 シーンのデータと API
tags:
  - C#連携
---

# 第 40 章 シーンのデータと API

この章から第 5 部、エディタの機能です。ビューポートに物（オブジェクト）を置けるようにします。エンジンにシーンを足して、C# から作成・削除・移動できる API を作り、C# 側にも、シーンのデータ（ドキュメント）を持たせます。シーン ツリー、プロパティ、Undo/Redo、保存と、このあとの機能は全部、この章の作りの上に乗ります。

!!! info "このページを読む前に"
    - [第 39 章 入力とエディタ カメラ](39-input-camera.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! note "これまでのダミーのデータは、ここで置き換わる"
    第 23 章までの Editor のシーン ツリーは、`SceneTreeViewModel` の中に `Camera`、`Cube`、`Light` のダミーを持っていました（`SceneObjectViewModel`）。この章からは、本物のシーンのデータ（`SceneDocument` と `SceneObject`）を作って、エンジンとつなぎます。ツリーとプロパティを、そのデータに結び直すのは第 40・41 章です。

## データの持ち主を決める

エディタもエンジンも、「シーン」を知っています。では、どちらが正しいデータを持つのでしょうか。ここを最初に決めておかないと、あとで必ず矛盾が出ます。

選択肢は 2 つあります。

- エンジンが持つ。C# は必要になるたびにエンジンに問い合わせます。データが 1 か所にまとまる利点はありますが、問い合わせるたびに境界を越えます。ツリーの表示、Undo、保存のたびに大量の呼び出しが発生しますし、C# の型としても扱いにくくなります。
- エディタが持つ。C# が編集用のデータを持ち、変更を命令としてエンジンに送ります。Undo/Redo、保存、ツリー表示が C# の中で完結しますし、境界を越えるのは変更したときだけです。代わりに、データが 2 か所に存在します。

この教材は、後者を選びます。エディタのシーン（ドキュメント）が正で、エンジンのシーンは、表示と実行のための写しです。商用のエディタも、だいたいこの構造です。

```text
┌──────── Editor（C#）────────┐         ┌──── Engine（C++）────┐
│ SceneDocument（正）          │ 命令    │ Scene（写し）          │
│  ├ SceneObject               │ ──────▶│  ├ 描画                │
│  ├ SceneObject               │        │  └ ピッキング           │
│ Undo/Redo、保存、ツリー表示    │ ◀──────│ （結果だけ返す）         │
└───────────────────────────┘         └───────────────────┘
```

この構造から、ルールが 2 つ決まります。

1. 変更は、必ずドキュメントを通す。ドキュメントが変わったら、対応する命令をエンジンに送る。
2. 編集モードのあいだ、エンジンは状態を勝手に変えない。変わる場合（ピッキング、Play モード）は、結果を C# に返して、C# が反映する。

### ID は C# が決める

物を区別する番号（ID）は、C# が決めてエンジンに渡します。エンジンが決めて返す方式だと、Undo で削除した物を復活させるときに、元と同じ ID に戻せないからです。ID は `uint`（32 ビット）で、0 は「なし」を表します（「親がない」を `0` で表せるように）。一度使った ID は、シーンの中で重複させません。

## エンジン側の Scene

まず、物とシーンのクラスです。

```cpp title="Engine/src/Scene.h"
#pragma once

#include <SimpleMath.h>

#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

namespace mini {

using ObjectId = std::uint32_t;      // 0 は「なし」

struct SceneObject {
  ObjectId id = 0;
  ObjectId parent = 0;
  std::string name;
  DirectX::SimpleMath::Vector3 position = DirectX::SimpleMath::Vector3::Zero;
  DirectX::SimpleMath::Vector3 rotation = DirectX::SimpleMath::Vector3::Zero;   // ラジアン。X=ピッチ, Y=ヨー, Z=ロール
  DirectX::SimpleMath::Vector3 scale = DirectX::SimpleMath::Vector3::One;
  DirectX::SimpleMath::Vector4 color = {0.8f, 0.8f, 0.8f, 1.0f};
};

// シーン：物の集まり。Engine が持つ。
class Scene {
 public:
  using Matrix = DirectX::SimpleMath::Matrix;

  void Clear();
  bool Create(ObjectId id, ObjectId parent, std::string name);
  bool Destroy(ObjectId id);                          // 子孫も一緒に破棄する
  bool SetParent(ObjectId id, ObjectId parent);
  SceneObject* Find(ObjectId id);
  const SceneObject* Find(ObjectId id) const;

  Matrix LocalMatrix(const SceneObject& object) const;
  Matrix WorldMatrix(const SceneObject& object) const;           // 親をたどって掛ける

  const std::unordered_map<ObjectId, SceneObject>& Objects() const { return objects_; }

 private:
  bool IsDescendant(ObjectId candidate, ObjectId ancestor) const;

  std::unordered_map<ObjectId, SceneObject> objects_;
};

}  // namespace mini
```

回転はオイラー角（ラジアン）で持ちます。エディタでは扱いやすいからです。補間のような複雑な回転が必要になった段階で、クォータニオンに置き換えます。`LocalMatrix` は親から見た変換で、拡大 → 回転 → 移動の順に組み立てます。`WorldMatrix` はワールド空間での変換で、親のワールド行列を掛けて求めます。

```cpp title="Engine/src/Scene.cpp"
#include "Scene.h"

#include <algorithm>

namespace mini {

using DirectX::SimpleMath::Matrix;

void Scene::Clear() {
  objects_.clear();
}

bool Scene::Create(ObjectId id, ObjectId parent, std::string name) {
  if (id == 0 || objects_.contains(id)) return false;               // 0 と重複は不可
  if (parent != 0 && !objects_.contains(parent)) return false;      // 親が存在しない
  SceneObject object;
  object.id = id;
  object.parent = parent;
  object.name = std::move(name);
  objects_.emplace(id, std::move(object));
  return true;
}

bool Scene::Destroy(ObjectId id) {
  if (!objects_.contains(id)) return false;
  // 子孫を先に集める（走査しながら消さない）
  std::vector<ObjectId> doomed = {id};
  for (std::size_t i = 0; i < doomed.size(); ++i) {
    for (const auto& [child_id, child] : objects_) {
      if (child.parent == doomed[i]) doomed.push_back(child_id);
    }
  }
  for (ObjectId doomed_id : doomed) objects_.erase(doomed_id);
  return true;
}

bool Scene::IsDescendant(ObjectId candidate, ObjectId ancestor) const {
  // candidate から親をたどり、ancestor に着くか
  for (ObjectId current = candidate; current != 0;) {
    if (current == ancestor) return true;
    const SceneObject* object = Find(current);
    if (!object) return false;
    current = object->parent;
  }
  return false;
}

bool Scene::SetParent(ObjectId id, ObjectId parent) {
  SceneObject* object = Find(id);
  if (!object) return false;
  if (parent != 0 && !objects_.contains(parent)) return false;
  if (parent != 0 && IsDescendant(parent, id)) return false;        // 自分の子孫の下には置けない（輪になる）
  object->parent = parent;
  return true;
}

SceneObject* Scene::Find(ObjectId id) {
  auto it = objects_.find(id);
  return it == objects_.end() ? nullptr : &it->second;
}

const SceneObject* Scene::Find(ObjectId id) const {
  auto it = objects_.find(id);
  return it == objects_.end() ? nullptr : &it->second;
}

Matrix Scene::LocalMatrix(const SceneObject& o) const {
  // 行ベクトルの約束：左から右へ「拡大 → 回転 → 移動」の順に適用される。
  return Matrix::CreateScale(o.scale) * Matrix::CreateFromYawPitchRoll(o.rotation.y, o.rotation.x, o.rotation.z) *
         Matrix::CreateTranslation(o.position);
}

Matrix Scene::WorldMatrix(const SceneObject& o) const {
  Matrix world = LocalMatrix(o);
  // 親のワールド行列を右から掛ける（行ベクトル：子 → 親の順に適用）
  for (ObjectId parent = o.parent; parent != 0;) {
    const SceneObject* p = Find(parent);
    if (!p) break;
    world = world * LocalMatrix(*p);
    parent = p->parent;
  }
  return world;
}

}  // namespace mini
```

注目したい点が 3 つあります。

- `Destroy` は、壊す物の ID を先に全部集めてから消しています。`unordered_map` を走査しながら `erase` すると、イテレーターが無効になるからです。
- `SetParent` の `IsDescendant` は、輪を防ぐ検査です。「A の親を A の子孫にする」と、親をたどっても終わらなくなってしまいます。
- `WorldMatrix` の掛け順は、行ベクトルの約束で、`自分 → 親 → さらに親` の順に左から右へ掛けます。`v * S * R * T * 親のS * 親のR * 親のT ...` と適用されるイメージです。

## ワイヤーフレームの箱を描く

物を単位立方体の枠線として描きます。物ごとに変換して、12 本の辺（24 頂点）を追加します。`Engine.cpp` に追加するコードです。

```cpp
namespace {

// 単位立方体（-0.5〜0.5）の枠線を変換して線の頂点に追加する。
void AddWireBox(std::vector<LineVertex>& lines, const Matrix& world, const Vector4& color) {
  Vector3 corners[8];
  for (int i = 0; i < 8; ++i) {
    const Vector3 local((i & 1) ? 0.5f : -0.5f, (i & 2) ? 0.5f : -0.5f, (i & 4) ? 0.5f : -0.5f);
    corners[i] = Vector3::Transform(local, world);          // 行ベクトル：local * world
  }
  // 角の番号を (x, y, z) のビットに合わせた辺の一覧
  static const int kBitEdges[12][2] = {{0, 1}, {2, 3}, {4, 5}, {6, 7}, {0, 2}, {1, 3},
                                       {4, 6}, {5, 7}, {0, 4}, {1, 5}, {2, 6}, {3, 7}};
  for (const auto& edge : kBitEdges) {
    lines.push_back({corners[edge[0]], color});
    lines.push_back({corners[edge[1]], color});
  }
}

}  // namespace
```

角の番号 `i` の bit0 が X、bit1 が Y、bit2 が Z を表します。隣り合う角（1 ビットだけ違う角）を結べば、立方体の 12 本の辺になり、`kBitEdges` はその 12 組です。

`Tick` の線の組み立てに、物の描画を足します。

```cpp
for (const auto& [id, object] : s.scene.Objects()) {
  const bool selected = s.selection.contains(id);
  const Vector4 color = selected ? Vector4(1.0f, 0.85f, 0.2f, 1.0f) : object.color;
  AddWireBox(lines, s.scene.WorldMatrix(object), color);
}
```

選択中の物は黄色にします。`s.selection` は、選択中の ID の集合（`std::unordered_set<ObjectId>`）で、次の節の API から設定します。

## C の API を足す

`EngineApi.h` に追加します。

```c
/* 変換（36 バイト）：位置、回転（ラジアン、X=ピッチ, Y=ヨー, Z=ロール）、拡大 */
typedef struct MeTransform {
  float position[3];
  float rotation[3];
  float scale[3];
} MeTransform;

/* シーン */
ME_API MeResult me_scene_clear(MeEngine* engine);
ME_API MeResult me_scene_create_object(MeEngine* engine, uint32_t id, uint32_t parent_id, const char* name_utf8);
ME_API MeResult me_scene_destroy_object(MeEngine* engine, uint32_t id);
ME_API MeResult me_scene_set_parent(MeEngine* engine, uint32_t id, uint32_t parent_id);
ME_API MeResult me_scene_set_name(MeEngine* engine, uint32_t id, const char* name_utf8);
ME_API MeResult me_scene_set_transform(MeEngine* engine, uint32_t id, const MeTransform* transform);
ME_API MeResult me_scene_set_color(MeEngine* engine, uint32_t id, float r, float g, float b, float a);
ME_API MeResult me_scene_set_selection(MeEngine* engine, const uint32_t* ids, uint32_t count);
```

実装は、どれも同じ形です。代表として 3 つを示します。

```cpp
MeResult me_scene_create_object(MeEngine* engine, uint32_t id, uint32_t parent_id, const char* name_utf8) {
  return Guard([&]() -> MeResult {
    if (!engine || !name_utf8) {
      SetLastError("引数が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    if (!engine->engine->GetScene().Create(id, parent_id, name_utf8)) {
      SetLastError("物を作れません（ID の重複、または親がありません）");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    return ME_OK;
  });
}

MeResult me_scene_set_transform(MeEngine* engine, uint32_t id, const MeTransform* t) {
  return Guard([&]() -> MeResult {
    if (!engine || !t) {
      SetLastError("引数が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    auto* object = engine->engine->GetScene().Find(id);
    if (!object) {
      SetLastError("物が見つかりません");
      return ME_ERROR_NOT_FOUND;
    }
    object->position = {t->position[0], t->position[1], t->position[2]};
    object->rotation = {t->rotation[0], t->rotation[1], t->rotation[2]};
    object->scale = {t->scale[0], t->scale[1], t->scale[2]};
    return ME_OK;
  });
}

MeResult me_scene_set_selection(MeEngine* engine, const uint32_t* ids, uint32_t count) {
  return Guard([&]() -> MeResult {
    if (!engine || (count > 0 && !ids)) {
      SetLastError("引数が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    engine->engine->SetSelection(std::span<const uint32_t>(ids, count));
    return ME_OK;
  });
}
```

`Engine` には、`Scene& GetScene()` と、`SetSelection(std::span<const ObjectId>)` を足します。

文字列は `const char* name_utf8` で受けます。変数名に `_utf8` を付けて、文字コードを明示するのは、あとで読んだ人が迷わないようにするためです（[文字コード](../encoding/index.md)）。配列は、先頭のポインターと個数のペアで受け取ります。C++20 の `std::span<const uint32_t>(ids, count)` は、配列とその長さを 1 つにまとめた非所有の参照で、コピーは発生しません。`ME_ERROR_NOT_FOUND` は、存在しない ID を指したときのエラーで、呼び出し側のバグか、同期のずれを示します。

!!! warning "GetScene() は、本当は公開しない"
    `Scene` を `Engine` の公開ヘッダー（`Engine.h`）に出すと、`SimpleMath.h` を利用者全員が読むことになります。実際には、`Engine.h` には `CreateObject(...)` のようなメソッドだけを置いて、`Scene` の実体は `Impl` の中に隠します。この教材では、コードを短くするために `GetScene()` の形で書いています。

## C# 側のモデル

エディタが持つ「物」のデータを作ります。`ObservableObject` を継承して、値が変わったときに画面へ通知できるようにします（第 14 章）。

```csharp title="Scene/SceneObject.cs"
using System.Collections.ObjectModel;
using System.Numerics;
using CommunityToolkit.Mvvm.ComponentModel;

namespace Editor.Scene;

public partial class SceneObject : ObservableObject
{
    public uint Id { get; }

    public SceneObject(uint id, string name)
    {
        Id = id;
        _name = name;
    }

    [ObservableProperty]
    private string _name;

    // 位置（メートル）
    [ObservableProperty]
    private Vector3 _position = Vector3.Zero;

    // 回転（度）。エンジンへは、ラジアンに変換して送る
    [ObservableProperty]
    private Vector3 _rotationDegrees = Vector3.Zero;

    [ObservableProperty]
    private Vector3 _scale = Vector3.One;

    [ObservableProperty]
    private Vector4 _color = new(0.8f, 0.8f, 0.8f, 1f);

    // 親子（木構造）。Parent は、ドキュメントが管理する
    public SceneObject? Parent { get; internal set; }
    public ObservableCollection<SceneObject> Children { get; } = new();
}
```

`System.Numerics.Vector3` は、.NET 標準の 3 次元ベクトルです。`float` が 3 つ並んだ構造体（12 バイト）で、C++ の `Vector3` と同じ並びなので、エンジンにそのまま渡せます。`Vector3.Zero` や `Vector3.One` といった定数の名前も SimpleMath と同じです。

構造体なので、`Position.X = 5` のような書き方はできません（コピーを書き換えるだけになります）。`Position = new Vector3(1, 2, 3)` のように、丸ごと入れ替えると通知されます。成分ごとの編集は、第 42 章で扱います。ID は `get` だけにして、一度決めたら変えません。

次に、物の集まりと木構造の変更を管理する `SceneDocument` です。

```csharp title="Scene/SceneDocument.cs"
using System.Collections.ObjectModel;

namespace Editor.Scene;

// 変更の種類。エンジンへの同期や、ツリーの更新が購読する
public enum SceneChangeKind { Created, Destroyed, Reparented, Renamed, TransformChanged, ColorChanged }

public sealed record SceneChange(SceneChangeKind Kind, SceneObject Object);

public class SceneDocument
{
    private readonly Dictionary<uint, SceneObject> _objects = new();
    private uint _nextId = 1;

    // 最上位の物（親がない）
    public ObservableCollection<SceneObject> Roots { get; } = new();

    // 変更の通知
    public event Action<SceneChange>? Changed;

    public IEnumerable<SceneObject> AllObjects => _objects.Values;
    public SceneObject? Find(uint id) => _objects.TryGetValue(id, out var o) ? o : null;

    public uint AllocateId() => _nextId++;

    // 物を作る。id を指定すれば、その番号で作る（Undo で復活させるため）
    public SceneObject Create(string name, SceneObject? parent = null, uint? id = null)
    {
        uint actualId = id ?? AllocateId();
        if (_objects.ContainsKey(actualId)) throw new InvalidOperationException($"ID {actualId} は使用済みです");
        _nextId = Math.Max(_nextId, actualId + 1);

        var obj = new SceneObject(actualId, name) { Parent = parent };
        _objects.Add(actualId, obj);
        (parent?.Children ?? Roots).Add(obj);
        Changed?.Invoke(new SceneChange(SceneChangeKind.Created, obj));
        return obj;
    }

    // 物を壊す。子も一緒に壊す（子から先に通知を出す）
    public void Destroy(SceneObject obj)
    {
        foreach (var child in obj.Children.ToList())
        {
            Destroy(child);
        }
        (obj.Parent?.Children ?? Roots).Remove(obj);
        _objects.Remove(obj.Id);
        Changed?.Invoke(new SceneChange(SceneChangeKind.Destroyed, obj));
    }

    public void Reparent(SceneObject obj, SceneObject? newParent)
    {
        for (var p = newParent; p != null; p = p.Parent)
        {
            if (p == obj) throw new InvalidOperationException("自分の子孫の下には置けません");
        }
        (obj.Parent?.Children ?? Roots).Remove(obj);
        obj.Parent = newParent;
        (newParent?.Children ?? Roots).Add(obj);
        Changed?.Invoke(new SceneChange(SceneChangeKind.Reparented, obj));
    }

    public void Clear()
    {
        foreach (var root in Roots.ToList()) Destroy(root);
        _nextId = 1;
    }

    public void NotifyChanged(SceneChangeKind kind, SceneObject obj) => Changed?.Invoke(new SceneChange(kind, obj));
}
```

読みどころを拾います。

- `Create` の `uint? id = null` は、省略できる引数です。省略されたら `AllocateId()` で新しい ID を振り、指定されたら、その番号で作ります（Undo で復活させるときのため）。
- `(parent?.Children ?? Roots)` は、親がいればその `Children` をいなければ `Roots` を使う書き方です。親の有無で入れ物を切り替えるのに、よく使います。
- `Destroy` で `obj.Children.ToList()` とコピーしているのは、反復中にコレクションが変わるのを避けるためです。
- `Reparent` の `for` 文は、輪を防ぐ検査です。新しい親から親をたどって、`obj` に出会ったら不可にします。
- `Changed` は、変更があったときに購読者へ知らせるイベントで、エンジンへの同期とツリーの更新がこれを購読します。

## エンジンへの同期

ドキュメントの変更をエンジンへの命令に変えるクラスを作ります。まず、P/Invoke の宣言です。

```csharp
[StructLayout(LayoutKind.Sequential)]
internal struct MeTransform
{
    public Vector3 Position;       // float × 3（12 バイト）
    public Vector3 Rotation;
    public Vector3 Scale;
}

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_clear(EngineHandle engine);

[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_create_object(EngineHandle engine, uint id, uint parentId, string name);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_destroy_object(EngineHandle engine, uint id);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_set_parent(EngineHandle engine, uint id, uint parentId);

[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_set_name(EngineHandle engine, uint id, string name);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_set_transform(EngineHandle engine, uint id, in MeTransform transform);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_scene_set_color(EngineHandle engine, uint id, float r, float g, float b, float a);
```

`MeTransform` が `Vector3` を 3 つ並べているのは、`System.Numerics.Vector3` が `float` を 3 つ（12 バイト、隙間なし）持つ、そのまま渡せる構造体だからです。C の `float position[3]; float rotation[3]; float scale[3];`（36 バイト）と、メモリ上で同じ並びになります。

`IEngineService` に、シーンの操作を足します。

```csharp
// IEngineService に追加
void SceneClear();
void SceneCreate(uint id, uint parentId, string name);
void SceneDestroy(uint id);
void SceneSetParent(uint id, uint parentId);
void SceneSetName(uint id, string name);
void SceneSetTransform(uint id, Vector3 position, Vector3 rotationRadians, Vector3 scale);
void SceneSetColor(uint id, Vector4 color);
```

`PInvokeEngineService` には、それぞれ `NativeMethods.ThrowIfFailed(NativeMethods.me_scene_xxx(Handle, ...))` の 1 行を書きます。

そして、ドキュメントの変更を拾ってエンジンに送るクラスです。

```csharp title="Engine/SceneEngineSync.cs"
using Editor.Scene;
using Editor.Viewport;

namespace Editor.Engine;

// SceneDocument の変更をエンジンに送る
public sealed class SceneEngineSync
{
    private readonly IRenderLoop _loop;

    public SceneEngineSync(SceneDocument document, IRenderLoop loop)
    {
        _loop = loop;
        document.Changed += OnChanged;
    }

    private void OnChanged(SceneChange change)
    {
        var o = change.Object;
        // 値をコピーしてから、描画スレッドの命令に渡す（後で o が変わっても、この時点の値を送る）
        uint id = o.Id;
        uint parentId = o.Parent?.Id ?? 0;
        string name = o.Name;
        var position = o.Position;
        var rotation = o.RotationDegrees * (MathF.PI / 180f);     // 度 → ラジアン
        var scale = o.Scale;
        var color = o.Color;

        switch (change.Kind)
        {
            case SceneChangeKind.Created:
                _loop.Post(e =>
                {
                    e.SceneCreate(id, parentId, name);
                    e.SceneSetTransform(id, position, rotation, scale);
                    e.SceneSetColor(id, color);
                });
                break;
            case SceneChangeKind.Destroyed:
                _loop.Post(e => e.SceneDestroy(id));
                break;
            case SceneChangeKind.Reparented:
                _loop.Post(e => e.SceneSetParent(id, parentId));
                break;
            case SceneChangeKind.Renamed:
                _loop.Post(e => e.SceneSetName(id, name));
                break;
            case SceneChangeKind.TransformChanged:
                _loop.Post(e => e.SceneSetTransform(id, position, rotation, scale));
                break;
            case SceneChangeKind.ColorChanged:
                _loop.Post(e => e.SceneSetColor(id, color));
                break;
        }
    }
}
```

ここで大事なのは、`Post` に渡す前に値をローカル変数にコピーしていることです。ラムダ式は変数を捕まえるので、`o.Position` のままにしておくと、描画スレッドが実行するとき（あとで）の最新の値を読んでしまい、UI スレッドと競合します。送る時点の値を手元にコピーしておきます。また、`Created` では、作成、変換、色を 1 つの `Post` にまとめています。途中で他の命令が割り込まないようにするためです。

`SceneEngineSync` は、`SceneDocument` を購読するだけで、誰からも参照されません。そのまま放っておくと作られないので、起動時に一度解決して、コンストラクターで購読させます。

```csharp
containerRegistry.RegisterSingleton<SceneDocument>();
containerRegistry.RegisterSingleton<SceneEngineSync>();

// OnInitialized で
Container.Resolve<SceneEngineSync>();    // 作っておく（コンストラクターで購読する）
```

## 試してみる

`MainWindowViewModel` に、仮のボタンを足します。

```csharp
[RelayCommand]
private void AddBox()                            // AddBoxCommand が生成される
{
    var obj = _document.Create($"Box {_document.AllocateId()}");
    obj.Position = new Vector3(Random.Shared.Next(-5, 6), 0.5f, Random.Shared.Next(-5, 6));
    _document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
}
```

押すたびに、ビューポートの原点の周りに、箱が 1 つずつ増えます。

注意してほしいのは、`obj.Position = ...` が変えるのはドキュメントの値だけで、エンジンへの通知は出ないことです（`SceneObject` の `PropertyChanged` は画面用の通知です）。エンジンへの同期は、`NotifyChanged` で明示しています。プロパティが変わるたびに自動で通知する仕組みは、第 42 章と第 44 章で整えます。

確かめたいのは次の点です。

- 起動するとグリッドと軸が出る。
- ボタンを押すと、箱の枠線がランダムな位置に増える。
- カメラを動かすと、箱が正しい位置で立体的に見える。

??? failure "箱が出ない"
    `SceneEngineSync` を一度も解決していないため、購読されていません。または、`Created` の命令で `SceneCreate` が失敗しています（ログを見ます）。

??? failure "箱が潰れている、傾いている"
    `scale` の初期値が `Zero` になっています。`Vector3.One` にします。回転の順序で、ヨー・ピッチ・ロールの引数を取り違えているかもしれません（`CreateFromYawPitchRoll(yaw, pitch, roll)`）。

??? failure "親を動かしても、子が動かない"
    `WorldMatrix` が親を掛けていないか、掛け順が逆です。行ベクトルでは、`子のローカル * 親のローカル` です。

??? failure "削除した物のあとで、エンジンが落ちる"
    `Destroy` のあとに、その ID に対する `SetTransform` が届いている可能性があります。`Post` は、積んだ順に実行される（`ConcurrentQueue` が順序を保つ）ので、同じ ID を削除後に使っていないかを確かめます。

??? failure "ID の重複で例外になる"
    Undo で同じ ID で再作成するときに、元の物が残っています。`Destroy` を先に呼びます。

## この章のまとめ

- データの持ち主はエディタ。エンジンは、命令を受けて写しを作る。
- ID は C# が採番して、Undo や保存で再利用できるようにする。
- エンジンへの送信は、`SceneDocument.Changed` を購読する `SceneEngineSync` が担う。
- 送るデータは、`Post` の前にコピーしておく。

次の章では、ドキュメントを `TreeView` に表示して、選択、名前の変更、親子づけ、追加・削除ができるようにします。

[第 41 章 シーン ツリー](41-scene-tree.md) へ進みます。
