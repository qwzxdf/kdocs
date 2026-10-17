---
title: FBX SDK のデータの取り出し方
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# FBX SDK のデータの取り出し方

FBX SDK で読み込んだ**シーン**から、**メッシュ・法線・UV・マテリアル・スキン・アニメーション**を取り出す方法をまとめます。**FBX SDK は、API が、細かく、独特**（<strong>「コントロール ポイント」と「ポリゴン頂点」の区別</strong>など）で、**慣れが必要**です。**三角形化済み**（[基本](quickstart.md)）の前提で説明します。

!!! tip "ポイント"
    - <strong>メッシュの頂点は「コントロール ポイント」</strong>（<strong>位置が、異なる点</strong>）。<strong>面の角（「ポリゴン頂点」）が、コントロール ポイントの番号を指す</strong>。
    - <strong>`GetPolygonVertex(poly, i)`</strong> で、<strong>面の i 番目の角が、どのコントロール ポイントか</strong>。
    - <strong>法線・UV は、「ポリゴン頂点ごと」「コントロール ポイントごと」などの、マッピング方式</strong>で持つ。<strong>`GetPolygonVertexNormal` / `GetPolygonVertexUV` が、面倒を吸収</strong>。
    - <strong>ノードのワールド変換は `EvaluateGlobalTransform()`</strong>（<strong>`FbxAMatrix`</strong>）。
    - <strong>スキンは `FbxSkin` ＞ `FbxCluster`</strong>（<strong>骨ごとの、影響する頂点と重み</strong>）。
    - <strong>アニメーションは、時刻を指定して、姿勢を評価</strong>（<strong>`FbxTime`</strong>）。
    - <strong>`manager->Destroy()` の前に、ゲーム用にコピー</strong>。

## メッシュ

```cpp
struct Vertex {
  Vector3 position;
  Vector3 normal;
  Vector2 uv;
};

void ReadMesh(FbxMesh* mesh, std::vector<Vertex>& vertices, std::vector<uint32_t>& indices) {
  FbxVector4* control_points = mesh->GetControlPoints();

  FbxStringList uv_sets;
  mesh->GetUVSetNames(uv_sets);
  const char* uv_name = uv_sets.GetCount() > 0 ? uv_sets.GetStringAt(0) : nullptr;

  int polygon_count = mesh->GetPolygonCount();
  for (int p = 0; p < polygon_count; ++p) {
    int size = mesh->GetPolygonSize(p);
    for (int i = 0; i < size; ++i) {
      int control_point_index = mesh->GetPolygonVertex(p, i);
      FbxVector4 position = control_points[control_point_index];

      FbxVector4 normal;
      mesh->GetPolygonVertexNormal(p, i, normal);

      FbxVector2 uv(0, 0);
      bool unmapped = false;
      if (uv_name) mesh->GetPolygonVertexUV(p, i, uv_name, uv, unmapped);

      Vertex v;
      v.position = Vector3(float(position[0]), float(position[1]), float(position[2]));
      v.normal = Vector3(float(normal[0]), float(normal[1]), float(normal[2]));
      v.uv = Vector2(float(uv[0]), 1.0f - float(uv[1]));

      indices.push_back(static_cast<uint32_t>(vertices.size()));
      vertices.push_back(v);
    }
  }
}
```

| 関数 | 意味 |
| --- | --- |
| **`mesh->GetControlPoints()`** | **コントロール ポイント（位置）の配列**（`FbxVector4`：**`double` の 4 つ**） |
| **`GetPolygonCount()`** | **面の数** |
| **`GetPolygonSize(p)`** | **面 p の、角の数**（三角形化済みなら、3） |
| **`GetPolygonVertex(p, i)`** | **面 p の i 番目の角が、指すコントロール ポイントの番号** |
| **`GetPolygonVertexNormal(p, i, normal)`** | **面 p の i 番目の角の、法線**（**マッピング方式を、吸収**） |
| **`GetPolygonVertexUV(p, i, uv_set, uv, unmapped)`** | **UV**（**UV セットの名前**を指定） |
| **`1.0f - uv[1]`** | **UV の V を反転**（**FBX は左下原点**、DirectX は左上） |

**`FbxVector4` は、`double`**です。**`float` に変換**して使います。<strong>4 つ目の成分（`w`）</strong>は、**位置では 1**。

!!! note "コントロール ポイントと、ポリゴン頂点"
    **同じ位置のコントロール ポイント**が、**複数の面で共有**されます。**面の角ごとに、法線・UV が違う**ことがあります（**角の立った箱**）。<strong>角ごとに、頂点を作る（重複させる）</strong>のが、**GPU 向けの、簡単な変換**です。**後で、重複をまとめる**（[メッシュの最適化](../../optimize/data-layout.md)）。

## ノードの変換

```cpp
FbxAMatrix global = node->EvaluateGlobalTransform();

Matrix world;
for (int row = 0; row < 4; ++row) {
  for (int col = 0; col < 4; ++col) {
    world.m[row][col] = static_cast<float>(global.Get(row, col));
  }
}
```

| 関数 | 意味 |
| --- | --- |
| **`node->EvaluateGlobalTransform(time)`** | **ワールド変換**（`FbxAMatrix`）。<strong>時刻（既定は 0）</strong> |
| **`EvaluateLocalTransform(time)`** | **親からの、ローカル変換** |
| **`FbxAMatrix::Get(row, col)`** | **要素**（**`double`**） |
| **行列の規約** | <strong>FBX の `FbxAMatrix` は、行ベクトル規約（平行移動が 4 行目）</strong>。**SimpleMath と同じ並び**で、**そのまま写せる**ことが多い（**座標系の変換を、先に済ませる**） |
| **`GetGeometricTranslation`・`Rotation`・`Scaling`** | **ノードの、ジオメトリだけの変換**（**ピボットの、オフセット**）。**必要なら、掛ける** |

## マテリアル

```cpp
int material_count = node->GetMaterialCount();
for (int i = 0; i < material_count; ++i) {
  FbxSurfaceMaterial* material = node->GetMaterial(i);

  FbxProperty diffuse = material->FindProperty(FbxSurfaceMaterial::sDiffuse);
  if (diffuse.IsValid()) {
    FbxDouble3 color = diffuse.Get<FbxDouble3>();

    int texture_count = diffuse.GetSrcObjectCount<FbxFileTexture>();
    if (texture_count > 0) {
      FbxFileTexture* texture = diffuse.GetSrcObject<FbxFileTexture>(0);
      const char* file_name = texture->GetFileName();
    }
  }
}
```

| 関数 | 意味 |
| --- | --- |
| **`node->GetMaterialCount()` / `GetMaterial(i)`** | **ノードの、マテリアル** |
| **`FindProperty(FbxSurfaceMaterial::sDiffuse)`** | **拡散色のプロパティ**（`sNormalMap`・`sSpecular`・`sEmissive` なども） |
| **`Get<FbxDouble3>()`** | <strong>色（RGB）</strong> |
| **`GetSrcObject<FbxFileTexture>`** | **プロパティに、つながるテクスチャ** |
| **`GetFileName()`** | **テクスチャのファイル名**（**絶対パスのことが多い**。**ファイル名だけ取り出して、自分のフォルダーで探す**） |

**FBX のマテリアルは、Phong / Lambert が、中心**で、**PBR（メタリック・ラフネス）は、ツール依存**です。**PBR が必要なら、glTF の方が、自然**です（[3D モデルの読み込みライブラリの選び方](../model-loading.md)）。

## スキン（骨）

```cpp
int skin_count = mesh->GetDeformerCount(FbxDeformer::eSkin);
for (int s = 0; s < skin_count; ++s) {
  FbxSkin* skin = static_cast<FbxSkin*>(mesh->GetDeformer(s, FbxDeformer::eSkin));

  int cluster_count = skin->GetClusterCount();
  for (int c = 0; c < cluster_count; ++c) {
    FbxCluster* cluster = skin->GetCluster(c);
    FbxNode* bone = cluster->GetLink();

    int* indices = cluster->GetControlPointIndices();
    double* weights = cluster->GetControlPointWeights();
    int count = cluster->GetControlPointIndicesCount();

    FbxAMatrix link_matrix;
    cluster->GetTransformLinkMatrix(link_matrix);
  }
}
```

| 関数 | 意味 |
| --- | --- |
| **`GetDeformer(i, eSkin)`** | **スキン** |
| **`FbxCluster`** | **1 本の骨の、影響の情報** |
| **`cluster->GetLink()`** | **骨のノード** |
| **`GetControlPointIndices()` / `GetControlPointWeights()`** | **この骨が、影響する、コントロール ポイントと、重み** |
| **`GetTransformLinkMatrix`** | **バインド時の、骨の変換**（**逆行列が、逆バインド行列**） |

**頂点（コントロール ポイント）ごとに、骨と重みを、集め直す**（**頂点側から見た形**）と、**GPU スキニング**に使えます（[スキニング](../../3d/skinning-animation.md)）。**1 つの頂点に、4 つを超える重み**は、**上位 4 つに絞って、正規化**します。

## アニメーション

```cpp
FbxAnimStack* stack = scene->GetCurrentAnimationStack();
FbxTimeSpan span = stack->GetLocalTimeSpan();
double start = span.GetStart().GetSecondDouble();
double stop = span.GetStop().GetSecondDouble();

for (double t = start; t <= stop; t += 1.0 / 30.0) {
  FbxTime time;
  time.SetSecondDouble(t);
  FbxAMatrix transform = node->EvaluateLocalTransform(time);
}
```

| 関数 | 意味 |
| --- | --- |
| **`scene->GetCurrentAnimationStack()`** | <strong>今の、アニメーション（テイク）</strong> |
| **`GetLocalTimeSpan()`** | **開始・終了の時刻** |
| **`FbxTime`** | **時刻**（**`SetSecondDouble` で、秒から作る**） |
| **`node->EvaluateLocalTransform(time)`** | **その時刻の、ローカル変換** |

**一定のレート（30 FPS など）で、全ノードの姿勢を、サンプリング**して、**ゲーム用の配列に焼く**のが、定番です（[ベイク](../../optimize/baking.md)）。**FBX SDK のまま、実行時に評価する**と、**重い**ので、**ツールで変換**します。

## ゲーム用に、コピーして、解放する

| やること | 説明 |
| --- | --- |
| **ゲーム用の構造体に、コピー** | **頂点・インデックス・骨・アニメ** |
| **`manager->Destroy()`** | **コピー後に、解放** |
| **ビルド時に変換するツールにする** | **FBX SDK を使うのは、ツールだけ**。**ゲームの実行ファイルには、リンクしない**（**配布・ライセンス・サイズの面で、楽**） |

## よくあるミス

??? failure "コントロール ポイントの番号と、頂点の番号を、混同する"
    **`GetPolygonVertex(p, i)`** が返すのは、**コントロール ポイント**の番号です。**法線・UV は、角（ポリゴン頂点）ごと**に、別の関数で。

??? failure "`FbxVector4` の `w` を、位置に含めて、間違える"
    **`[0]`〜`[2]`** だけ使います。

??? failure "UV が、上下逆になる"
    **V を反転**します。

??? failure "テクスチャのパスが、制作者の PC の絶対パスで、見つからない"
    **ファイル名だけ取り出して**、**ゲームのフォルダー**で探します。

??? failure "実行時に、FBX SDK でアニメーションを評価して、重い"
    **ツールで、事前に焼きます**。

## 関連ページ

- [FBX SDK（目次）](index.md)
- [FBX SDK の基本](quickstart.md)
- [ufbx のデータの取り出し方](../ufbx/reading.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
