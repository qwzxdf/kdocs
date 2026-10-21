---
title: 第 20 章 シーンのデータと API
tags:
  - C#連携
---

# 第 20 章 シーンのデータと API

この章から第 5 部（エディタの機能）です。ビューポートに<strong>物（オブジェクト）を置ける</strong>ようにします。エンジンにシーンを足し、C# から作成・削除・移動できる API を作り、C# 側にも<strong>シーンのデータ</strong>（ドキュメント）を持たせます。シーン ツリー（第 21 章）、プロパティ（第 22 章）、Undo/Redo（第 24 章）、保存（第 25 章）の、すべての土台になる章です。

## この章の考え方

### 「データの持ち主」を決める

エディタとエンジンの両方が「シーン」を知っています。<strong>どちらが正しいデータを持つのか</strong>を、最初に決めておかないと、あとで必ず矛盾します。

| 案 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| <strong>A: エンジンが持つ</strong> | C# は、必要になるたび、エンジンに問い合わせる | データが 1 か所 | 問い合わせるたびに境界を越える。Undo、保存、ツリー表示のたびに、大量の呼び出し。C# の型で扱いにくい |
| <strong>B: エディタが持つ</strong>（採用） | C# が「編集用のデータ」を持ち、変更を<strong>命令として</strong>エンジンに送る | Undo/Redo、保存、ツリー表示が、C# の中で完結。境界の呼び出しは「変更したとき」だけ | データが 2 か所にある（エンジンは、複製） |

この教材では <strong>B</strong> を採用します。エディタのシーン（<strong>ドキュメント</strong>）が<strong>正</strong>で、エンジンのシーンは、<strong>表示と実行のための写し</strong>です。実際の商用エディタも、この構造が一般的です。

```text
┌──────── Editor（C#）────────┐         ┌──── Engine（C++）────┐
│ SceneDocument（正）          │ 命令    │ Scene（写し）          │
│  ├ SceneObject               │ ──────▶│  ├ 描画                │
│  ├ SceneObject               │        │  └ ピッキング           │
│ Undo/Redo、保存、ツリー表示    │ ◀──────│ （結果だけ返す）         │
└───────────────────────────┘         └───────────────────┘
```

この構造から、2 つのルールが決まります。

1. <strong>変更は必ず、ドキュメントを通す</strong>。ドキュメントが変わったら、それに対応する命令を、エンジンに送る。
2. <strong>エンジンは、状態を勝手に変えない</strong>（編集モードのとき）。変わる場合（ピッキング、Play モード）は、結果を C# に返し、C# が反映する。

### ID

物を区別する番号（ID）は、<strong>C# が決めて、エンジンに渡します</strong>。エンジンが決めて返す方式だと、Undo で「削除した物を復活」させるとき、元と同じ ID に戻せません。

| 規則 | 理由 |
| --- | --- |
| ID は `uint`（32 ビット、0 は「なし」） | `0` を「親なし」に使える |
| C# が採番する | Undo/Redo や保存で、同じ ID を再利用できる |
| 一度使った ID は、シーン内で重複させない | 衝突を防ぐ |

## この章のゴール

- エンジンに `Scene` を作り、物をワイヤーフレームの箱として描く。
- C の API で、物の作成・削除・親子づけ・名前・変換（位置、回転、拡大）・色を、設定できる。
- C# に `SceneObject` と `SceneDocument` を作り、変更をエンジンに送る。
- ビューポートに、箱が表示される。

## 手順 1：エンジン側の Scene

`Engine\src\Scene.h`:

```cpp
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

| 部分 | 説明 |
| --- | --- |
| `ObjectId` | 物の番号。`0` は「親なし」の意味 |
| 回転の持ち方 | オイラー角（ラジアン）。エディタでは扱いやすい。複雑な回転（補間など）が要る段階で、クォータニオンに置き換える |
| `LocalMatrix` | 親から見た変換。拡大 → 回転 → 移動の順 |
| `WorldMatrix` | ワールド空間の変換。<strong>親のワールド行列を掛ける</strong> |
| `unordered_map` | ID で引ける表。`std::unordered_map<K, V>` |

`Engine\src\Scene.cpp`:

```cpp
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

| 部分 | 説明 |
| --- | --- |
| `objects_.contains(id)` | C++20 の `contains`。要素があるか |
| `emplace` | 要素を、その場で作って入れる |
| `Destroy` の集め方 | 破棄する物の ID を、幅優先で集めてから消す。走査中に `erase` すると、イテレーターが無効になる |
| `IsDescendant` | <strong>輪を防ぐ</strong>。「A の親を、A の子孫にする」と、親をたどって終わらなくなる |
| 掛け順 | 行ベクトルでは、`v * S * R * T * ParentS * ParentR * ParentT`…の順に適用される。つまり、<strong>行列は左から右へ</strong>「自分 → 親 → さらに親」の順で掛ける |

## 手順 2：ワイヤーフレームの箱を描く

物を、<strong>単位立方体の枠線</strong>として描きます。物ごとに変換して、12 本の辺（24 頂点）を追加します。

`Engine.cpp` の `Tick` に追加します。

```cpp
namespace {

// 単位立方体（-0.5〜0.5）の枠線を、変換して線の頂点に追加する。
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

角の番号 `i` の bit0 が X、bit1 が Y、bit2 が Z を表します。<strong>隣り合う角</strong>（1 ビットだけ違う角）を結べば、立方体の 12 本の辺になります。`kBitEdges` は、その 12 組です。

`Tick` の線の組み立てに、物の描画を足します。

```cpp
for (const auto& [id, object] : s.scene.Objects()) {
  const bool selected = s.selection.contains(id);
  const Vector4 color = selected ? Vector4(1.0f, 0.85f, 0.2f, 1.0f) : object.color;
  AddWireBox(lines, s.scene.WorldMatrix(object), color);
}
```

| 部分 | 説明 |
| --- | --- |
| `(i & 1) ? 0.5f : -0.5f` | 角の番号 `i` のビットで、各軸の ±0.5 を決める。8 つの角が作れる |
| `Vector3::Transform(local, world)` | SimpleMath の関数。ベクトルを、行列で変換する（行ベクトルの `local * world`） |
| 選択中は黄色 | 第 21 章以降で、選択に使う |
| `s.selection` | 選択中の ID の集合（`std::unordered_set<ObjectId>`）。次の手順で、API から設定する |

## 手順 3：C の API を足す

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

`Engine` には、`Scene& GetScene()` と `SetSelection(std::span<const ObjectId>)` を足します。

| 部分 | 説明 |
| --- | --- |
| `const char* name_utf8` | UTF-8 の文字列。変数名に `_utf8` を付けて、文字コードを明示する（[文字コード](../encoding/index.md)） |
| `const uint32_t* ids, uint32_t count` | <strong>配列の渡し方</strong>。先頭のポインターと個数のペア。C++ の `std::span` に当たる |
| `std::span<const uint32_t>(ids, count)` | 配列とその長さを 1 つにまとめた<strong>非所有</strong>の参照（C++20）。コピーしない |
| `NOT_FOUND` | 存在しない ID。呼び出し側のバグか、同期のずれを示す |

!!! warning "Engine::GetScene は公開しない"
    `Scene` を `Engine` の公開ヘッダー（`Engine.h`）に出すと、`SimpleMath.h` を利用者全員が読むことになります。実際は、`Engine.h` には `CreateObject(...)` のような<strong>メソッド</strong>を置き、`Scene` の実体は `Impl` の中に隠します。この教材では、記述を短くするために、`GetScene()` の形で示しています。

## 手順 4：C# 側のモデル

### SceneObject

エディタが持つ「物」のデータです。`BindableBase` を継承して、値が変わったときに画面へ通知します。

`Models\SceneObject.cs`:

```csharp
using System.Collections.ObjectModel;
using System.Numerics;
using Prism.Mvvm;

namespace Editor.Models;

public class SceneObject : BindableBase
{
    public uint Id { get; }

    public SceneObject(uint id, string name)
    {
        Id = id;
        _name = name;
    }

    private string _name;
    public string Name
    {
        get => _name;
        set => SetProperty(ref _name, value);
    }

    // 位置（メートル）
    private Vector3 _position = Vector3.Zero;
    public Vector3 Position
    {
        get => _position;
        set => SetProperty(ref _position, value);
    }

    // 回転（度）。エンジンへは、ラジアンに変換して送る
    private Vector3 _rotationDegrees = Vector3.Zero;
    public Vector3 RotationDegrees
    {
        get => _rotationDegrees;
        set => SetProperty(ref _rotationDegrees, value);
    }

    private Vector3 _scale = Vector3.One;
    public Vector3 Scale
    {
        get => _scale;
        set => SetProperty(ref _scale, value);
    }

    private Vector4 _color = new(0.8f, 0.8f, 0.8f, 1f);
    public Vector4 Color
    {
        get => _color;
        set => SetProperty(ref _color, value);
    }

    // 親子（木構造）。Parent は、ドキュメントが管理する
    public SceneObject? Parent { get; internal set; }
    public ObservableCollection<SceneObject> Children { get; } = new();
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `System.Numerics.Vector3` | .NET 標準の 3 次元ベクトル。`float` が 3 つ並んだ<strong>構造体</strong>（12 バイト）。C++ の `Vector3` と<strong>同じ並び</strong>なので、エンジンにそのまま渡せる |
| `Vector3.Zero` / `Vector3.One` | 定数。SimpleMath と同じ名前 |
| `new(0.8f, 0.8f, 0.8f, 1f)` | 対象型 new。`Vector4` が推論される |
| `SetProperty` と構造体 | `Vector3` は値型。`Position = new Vector3(1, 2, 3)` と<strong>丸ごと入れ替える</strong>と通知される。`Position.X = 5` は<strong>できない</strong>（コピーを書き換えるだけ）。個別の成分の編集は、第 22 章で扱う |
| `{ get; internal set; }` | 外からは読み取りのみ、同じプロジェクト内からは設定できる |
| ID を `get` のみ | 一度決めたら変えない |

### SceneDocument

物の集まりと、木構造の変更を管理します。

`Models\SceneDocument.cs`:

```csharp
using System.Collections.ObjectModel;

namespace Editor.Models;

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Dictionary<uint, SceneObject>` | ID から物を引く表 |
| `uint? id = null` | 省略できる、`null` 許容の引数 |
| `id ?? AllocateId()` | `id` が `null` のとき、新しい ID を採番する |
| `_nextId++` | 現在の値を返してから、1 増やす（後置インクリメント） |
| `(parent?.Children ?? Roots)` | 親がいればその `Children`、いなければ `Roots`。<strong>親の有無で、入れ物を切り替える</strong>書き方 |
| `.ToList()` | 反復中に集合を変更するのを避けるため、コピーを作ってから回す |
| `record SceneChange(…)` | 変更の内容を運ぶ、値の入れ物 |
| `event Action<SceneChange>? Changed` | 変更があったとき、購読者に通知する。<strong>エンジンへの同期</strong>と、<strong>ツリーの更新</strong>が、これを購読する |
| `for (var p = newParent; p != null; p = p.Parent)` | 輪を防ぐ検査。`newParent` から親をたどり、`obj` に出会ったら不可 |
| `Math.Max(_nextId, actualId + 1)` | 指定した ID が大きいとき、次の採番がそれを越えるように調整 |

## 手順 5：エンジンへの同期

ドキュメントの変更を、エンジンへの命令に変えるクラスです。

### P/Invoke の宣言

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

`MeTransform` が `Vector3` を 3 つ並べているのは、`System.Numerics.Vector3` が `float` を 3 つ（12 バイト、パディングなし）持つ<strong>blittable</strong> な構造体だからです。C の `float position[3]; float rotation[3]; float scale[3];`（36 バイト）と、メモリ上で同じ並びになります。

### IEngineService にシーン操作を足す

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

`PInvokeEngineService` には、それぞれ `NativeMethods.ThrowIfFailed(NativeMethods.me_scene_xxx(Handle, …))` の 1 行を書きます。

### SceneEngineSync

`Services\SceneEngineSync.cs`:

```csharp
using Editor.Models;

namespace Editor.Services;

// SceneDocument の変更を、エンジンに送る
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `* (MathF.PI / 180f)` | `Vector3` と `float` の掛け算（要素ごと）。`MathF` は `float` 版の数学関数 |
| 値をコピーしてから `Post` | ラムダは<strong>変数を捕まえる</strong>ので、`o.Position` のまま渡すと、実行時（描画スレッド）に<strong>最新の値</strong>を読んでしまい、UI スレッドと競合する。送る時点の値を、ローカル変数にコピーしておく |
| 1 つの `Post` に複数の命令 | `Created` で、作成・変換・色を<strong>まとめて</strong>実行する。途中で他の命令が割り込まない |

`App.xaml.cs` で登録します。`SceneEngineSync` は、`SceneDocument` を購読するだけで、誰も参照しないので、<strong>起動時に1度、解決しておく</strong>必要があります。

```csharp
containerRegistry.RegisterSingleton<SceneDocument>();
containerRegistry.RegisterSingleton<SceneEngineSync>();

// OnInitialized で
Container.Resolve<SceneEngineSync>();    // 作っておく（コンストラクターで購読する）
```

## 手順 6：試す

`MainWindowViewModel` に、仮のボタンを足します。

```csharp
public DelegateCommand AddBoxCommand { get; }

// コンストラクターの中
AddBoxCommand = new DelegateCommand(() =>
{
    var obj = _document.Create($"Box {_document.AllocateId()}");
    obj.Position = new Vector3(Random.Shared.Next(-5, 6), 0.5f, Random.Shared.Next(-5, 6));
    _document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
});
```

押すたびに、ビューポートの原点の周りに、箱が 1 つ増えます。

注意：`obj.Position = …` は<strong>ドキュメントの値を変えるだけで、通知は出ません</strong>（`SceneObject` の `PropertyChanged` は画面用）。エンジンへの同期は、`NotifyChanged` で明示します。<strong>プロパティが変わるたびに、自動で `SceneChangeKind.TransformChanged` を出す</strong>仕組みは、第 22 章（プロパティ）と第 24 章（Undo/Redo）で整えます。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | グリッドと軸が出る |
| 「箱を追加」ボタン | 箱の枠線が、ランダムな位置に増える |
| カメラを動かす | 箱が、正しい位置で、立体的に見える |
| ログ | エラーが出ない |
| 親子 | `Create(name, parent)` で作ると、親の動きに追従する（第 21 章で確認） |

## よくあるミス

??? failure "箱が出ない"
    `SceneEngineSync` を、一度も解決していない（`Container.Resolve` を呼んでいない）ため、購読されていない。または、`Created` の命令で `SceneCreate` が失敗している（ログを見る）。

??? failure "箱が潰れている／傾いている"
    `Vector3 scale` の初期値が `Zero` になっている。`Vector3.One` にする。回転の順序が、ヨー・ピッチ・ロールの引数順を取り違えている（`CreateFromYawPitchRoll(yaw, pitch, roll)`）。

??? failure "親を動かしても、子が動かない"
    `WorldMatrix` が親を掛けていない、または掛け順が逆。行ベクトルでは、`子のローカル * 親のローカル`。

??? failure "削除した物のあと、エンジンで落ちる"
    `Destroy` の後に、その ID に対する `SetTransform` が届く。順序の入れ替わりを防ぐため、`Post` は<strong>積んだ順に実行</strong>される（`ConcurrentQueue` が順序を保つ）ことを確認する。同じ ID を、削除後に使っていないか確認する。

??? failure "ID の重複で例外になる"
    Undo で、同じ ID で再作成するとき、元の物が残っている。`Destroy` を先に呼ぶ。

## この章のまとめ

- <strong>データの持ち主はエディタ</strong>。エンジンは、命令を受けて写しを作る。
- ID は C# が採番し、Undo/Redo や保存で再利用できるようにする。
- エンジンへの送信は、`SceneDocument.Changed` を購読する `SceneEngineSync` が担う。
- 送るデータは、`Post` の前にコピーしておく。

## 次の章へ

次の章（[第 21 章 シーン ツリー](21-scene-tree.md)）では、`SceneDocument` を `TreeView` に表示し、物の選択、名前の変更、親子づけ（ドラッグ アンド ドロップ）、追加・削除のコマンドを作ります。
