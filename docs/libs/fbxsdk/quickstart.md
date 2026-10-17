---
title: FBX SDK の基本
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# FBX SDK の基本

FBX SDK の使い方は、<strong>「マネージャー（FbxManager）→ インポーター（FbxImporter）→ シーン（FbxScene）」</strong>の流れです。**オブジェクトの管理**（**`Create` と `Destroy`**）に、**独特のルール**があります。このページは、**最小の読み込み**、**座標系・単位の変換**、**三角形化**、**シーンの構造**をまとめます（FBX 自体の説明は、[FBX と ufbx の基本](../ufbx/quickstart.md)）。

!!! tip "ポイント"
    - <strong>最初に `FbxManager::Create()`</strong>。<strong>最後に `manager->Destroy()`</strong>（<strong>これで、関連するすべてのオブジェクトが、解放</strong>される）。
    - <strong>オブジェクトは、`new` / `delete` ではなく、`Create` / `Destroy`</strong>。<strong>FBX SDK が、メモリを管理</strong>。
    - 読み込みは<strong>`FbxImporter::Initialize` → `Import(scene)`</strong>。<strong>`Import` の後、インポーターは、破棄してよい</strong>。
    - <strong>`FbxAxisSystem::DirectX.ConvertScene(scene)`</strong> で、<strong>座標系を変換</strong>（<strong>※右手系か左手系かに、注意</strong>）。<strong>`FbxSystemUnit::m.ConvertScene`</strong> で、メートルに。
    - <strong>`FbxGeometryConverter::Triangulate`</strong> で、<strong>全メッシュを、三角形化</strong>。
    - <strong>シーンは、ノードの木</strong>（<strong>`GetRootNode()` → `GetChild(i)`</strong>）。<strong>ノードが、属性（メッシュなど）を持つ</strong>。

## 最小の読み込み

```cpp
#include <fbxsdk.h>

FbxScene* LoadFbx(FbxManager* manager, const char* path) {
  FbxIOSettings* ios = FbxIOSettings::Create(manager, IOSROOT);
  manager->SetIOSettings(ios);

  FbxImporter* importer = FbxImporter::Create(manager, "");
  if (!importer->Initialize(path, -1, manager->GetIOSettings())) {
    std::println("読み込みに失敗: {}", importer->GetStatus().GetErrorString());
    importer->Destroy();
    return nullptr;
  }

  FbxScene* scene = FbxScene::Create(manager, "scene");
  importer->Import(scene);
  importer->Destroy();
  return scene;
}

int main() {
  FbxManager* manager = FbxManager::Create();

  FbxScene* scene = LoadFbx(manager, "assets/character.fbx");
  if (scene) {
    FbxNode* root = scene->GetRootNode();
    std::println("子ノード数: {}", root->GetChildCount());
  }

  manager->Destroy();
}
```

| 部分 | 意味 |
| --- | --- |
| **`FbxManager::Create()`** | **SDK 全体の管理者**。**最初に 1 つ作る** |
| **`FbxIOSettings::Create(manager, IOSROOT)`** | **入出力の設定**（**何を読み込むか**） |
| **`FbxImporter::Create(manager, "")`** | **インポーター**（ファイルを読む係） |
| **`importer->Initialize(path, -1, ios)`** | **ファイルを開く**（**`-1` ＝ 形式を、自動判定**）。**失敗は `false`** |
| **`FbxScene::Create(manager, "scene")`** | **シーン**（**読み込み先の入れ物**） |
| **`importer->Import(scene)`** | **ファイルの内容を、シーンに**読む |
| **`importer->Destroy()`** | **インポーターを破棄**（**`Import` の後、不要**） |
| **`manager->Destroy()`** | **すべてのオブジェクトを、解放** |

### Create と Destroy

**FBX SDK のオブジェクトは、`new` / `delete` ではなく、`Create` / `Destroy`**で扱います。

| ルール | 説明 |
| --- | --- |
| **`Create`**（`FbxXxx::Create(manager, ...)`） | **SDK が、メモリを確保** |
| **`Destroy()`** | **個別に破棄**。**`manager->Destroy()` で、まとめて** |
| **`delete` は禁止** | **SDK の内部のメモリ管理と、衝突** |
| **シーンから取得したポインタ** | **`manager->Destroy()` の後は、無効**。**先に、ゲーム用にコピー** |

!!! note "unique_ptr と組み合わせる"
    `std::unique_ptr<FbxManager, void(*)(FbxManager*)>` に、<strong>カスタム削除子（`Destroy` を呼ぶ）</strong>を渡すと、**例外・早期 return でも、解放**されます（[RAII](../../design/patterns/raii.md)）。

## 座標系・単位の変換

**FBX は、ツールごとに、座標系・単位が違います**。**読み込み後に、変換**します。

```cpp
FbxAxisSystem target_axes = FbxAxisSystem::eDirectX;
FbxAxisSystem scene_axes = scene->GetGlobalSettings().GetAxisSystem();
if (scene_axes != target_axes) {
  target_axes.ConvertScene(scene);
}

FbxSystemUnit scene_unit = scene->GetGlobalSettings().GetSystemUnit();
if (scene_unit != FbxSystemUnit::m) {
  FbxSystemUnit::m.ConvertScene(scene);
}
```

| 設定 | 意味 |
| --- | --- |
| **`FbxAxisSystem::DirectX`** | **DirectX 用の座標系**（**Y 上・左手系**）。**このサイトの規約と同じ**。**これを使う** |
| **`FbxAxisSystem::OpenGL`** | **OpenGL 用**（**Y 上・右手系**）。このサイトの規約（左手系）とは違う |
| **`FbxAxisSystem::MayaYUp`** | Maya の Y 上 |
| **`ConvertScene(scene)`** | **シーン全体を、その座標系に変換** |
| **`FbxSystemUnit::m`** | **メートル**（`cm`・`inch` もある）。**`ConvertScene`** で、スケールを変換 |

!!! warning "DirectX 用の座標系は、左手系"
    **`FbxAxisSystem::DirectX` は、左手系**です。<strong>このサイトは、右手系（SimpleMath）</strong>なので、**`FbxAxisSystem::OpenGL`**（**右手系・Y 上**）を、使うか、**左手系 → 右手系の変換**（Z の反転・巻き順の反転）を、自分で行います（[座標系](../../gamemath/coordinate-systems.md)）。**変換後、実際に表示して、確認**します。

## 三角形化

**FBX のメッシュは、多角形（四角形以上）を含みます**。**GPU は三角形**なので、**変換**します。

```cpp
FbxGeometryConverter converter(manager);
converter.Triangulate(scene, true);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| **`Triangulate(scene, replace)`** | `FbxScene*`, `bool` | **シーンの全メッシュを、三角形化**。**`true` ＝ 元のメッシュを、置き換える** |
| **効果** | — | **以後、`GetPolygonSize(p)` が、すべて 3** |

**スキン・ブレンドシェイプも、保ったまま、三角形化**されます。

## シーンの構造

**シーンは、ノードの木**で、**ノードに、属性（メッシュ・カメラ・ライトなど）が付きます**。

<svg class="fig flow" viewBox="0 0 950 280" role="img" aria-label="FBX SDK のシーン：ノードの木と、ノードが持つ属性"><defs><marker id="fl42827" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">FBX SDK のシーン：ノードの木と、ノードが持つ属性</text><line x1="119.0" y1="148.0" x2="177.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42827)"/><text x="148.0" y="142.0" text-anchor="middle" style="font-size:12px">GetRootNode</text><line x1="294.3" y1="125.0" x2="375.7" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42827)"/><text x="335.0" y="100.0" text-anchor="middle" style="font-size:12px">GetChild</text><line x1="294.3" y1="171.0" x2="375.7" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42827)"/><text x="335.0" y="184.0" text-anchor="middle" style="font-size:12px">GetChild</text><line x1="479.0" y1="64.0" x2="545.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42827)"/><text x="512.0" y="58.0" text-anchor="middle" style="font-size:12px">GetMesh</text><line x1="695.0" y1="64.0" x2="761.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42827)"/><line x1="479.0" y1="232.0" x2="537.0" y2="232.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42827)"/><rect x="28.0" y="128.0" width="88" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="72.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FbxScene</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="180.0" y="128.0" width="130" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="245.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ルート FbxNode</text><circle cx="182.0" cy="130.0" r="10" fill="#2ea043"/><text x="182.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="374.0" y="44.0" width="102" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="425.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">子 FbxNode</text><circle cx="376.0" cy="46.0" r="10" fill="#e5a828"/><text x="376.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="374.0" y="212.0" width="102" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="425.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">子 FbxNode</text><circle cx="376.0" cy="214.0" r="10" fill="#e5a828"/><text x="376.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="548.0" y="44.0" width="144" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="620.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FbxMesh （属性）</text><circle cx="550.0" cy="46.0" r="10" fill="#e5484d"/><text x="550.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="764.0" y="44.0" width="158" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="843.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FbxSkin （スキン）</text><circle cx="766.0" cy="46.0" r="10" fill="#e5484d"/><text x="766.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="540.0" y="212.0" width="160" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="620.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FbxSkeleton （ボーン）</text><circle cx="542.0" cy="214.0" r="10" fill="#e5484d"/><text x="542.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

| クラス | 役割 |
| --- | --- |
| **`FbxScene`** | **シーン全体** |
| **`FbxNode`** | **ノード**（**階層・変換**）。**`GetChild(i)`・`GetChildCount()`・`GetParent()`** |
| **`FbxNodeAttribute`** | **ノードに付く、中身**（メッシュ・ボーン・カメラ・ライト） |
| **`FbxMesh`** | **メッシュ** |
| **`FbxSkeleton`** | **ボーン** |
| **`FbxSurfaceMaterial`** | **マテリアル** |
| **`FbxAnimStack` / `FbxAnimLayer`** | **アニメーション**（テイクとレイヤー） |

```cpp
void Traverse(FbxNode* node) {
  FbxNodeAttribute* attribute = node->GetNodeAttribute();
  if (attribute && attribute->GetAttributeType() == FbxNodeAttribute::eMesh) {
    FbxMesh* mesh = node->GetMesh();
  }
  for (int i = 0; i < node->GetChildCount(); ++i) {
    Traverse(node->GetChild(i));
  }
}
```

**ポインタ**で、つながっています（ufbx と同じ。glTF の「番号」とは違う）。

## よくあるミス

??? failure "`delete` で、FBX SDK のオブジェクトを解放して、クラッシュ"
    **`Destroy()`**、または **`manager->Destroy()`** を使います。

??? failure "`manager->Destroy()` の後に、ノード・メッシュを触る"
    **すべて無効**です。**先に、ゲーム用のデータに、コピー**します。

??? failure "座標系の変換をしないで、モデルが、横倒し・裏返しになる"
    **`ConvertScene`**（座標系・単位）を呼びます。**`FbxAxisSystem::DirectX`**（左手系）を指定し、**巻き順（CW が表）も確認**します。

??? failure "三角形化せずに、四角形を扱って、形が崩れる"
    **`FbxGeometryConverter::Triangulate`**。

??? failure "`importer->Initialize` が `false` で、理由が分からない"
    **`importer->GetStatus().GetErrorString()`** を、表示します。**パスの文字コード**（UTF-8）も確認。

## 関連ページ

- [FBX SDK（目次）](index.md)
- [データの取り出し方](reading.md)
- [FBX と ufbx の基本](../ufbx/quickstart.md)
- [座標系](../../gamemath/coordinate-systems.md)
