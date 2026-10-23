---
title: ufbx のデータの取り出し方
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# ufbx のデータの取り出し方

ufbx で読み込んだ**シーン**から、メッシュ（頂点・インデックス）・ノード・マテリアル・スキン・アニメーションをゲーム用のデータに取り出す方法をまとめます。FBX のメッシュは、「面（Face）」＝ 多角形の集まりで三角形にするのが最初の仕事です。

!!! tip "ポイント"
    - <strong>メッシュは「面（Face）」の集まり</strong>。<strong>面は三角形・四角形・それ以上</strong>。`ufbx_triangulate_face` で、三角形にする。
    - 頂点の属性（位置・法線・UV）は、「インデックス → 値」の 2 段構成（`vertex_position.values` と `.indices`）。
    - FBX は、属性ごとにインデックスが別。GPU 用には、頂点を重複させて、1 つのインデックスにまとめる（`ufbx_generate_indices`）。
    - ノードの変換は `node->node_to_world`（ワールド行列）。列優先の 3×4。
    - マテリアルは `material->pbr`（メタリック・ラフネス）。
    - スキンは `ufbx_skin_deformer`。アニメーションは `ufbx_evaluate_transform` で、時刻の姿勢。
    - `ufbx_free_scene` の前に、ゲーム用にコピーする。

## メッシュ

### 構造

**`ufbx_mesh`** は、面（`faces`）と、頂点の属性を持ちます。

| メンバ | 意味 |
| --- | --- |
| `num_vertices` | 位置が異なる頂点の数 |
| `num_indices` | 面の角（コーナー）の数（四角形 1 つで 4） |
| `num_faces` | 面の数 |
| `faces` | 各面の、`index_begin` と `num_indices`（角の範囲） |
| `vertex_position` | 位置。`.values`（値の配列）と `.indices`（角ごとの値の番号） |
| `vertex_normal` | 法線（同様） |
| `vertex_uv` | UV（同様） |
| `materials` | 使うマテリアルのリスト |
| `face_material` | 面ごとのマテリアルの番号 |

角（コーナー）ごとに位置・法線・UV の値を引くときは、`mesh->vertex_normal[corner]` のように、インデックスでアクセスできます（ufbx のヘルパー）。

### 三角形にして、取り出す

```cpp
struct Vertex {
  Vector3 position;
  Vector3 normal;
  Vector2 uv;
};

void ReadMesh(const ufbx_mesh* mesh, std::vector<Vertex>& vertices, std::vector<uint32_t>& indices) {
  std::vector<uint32_t> tri_indices(mesh->max_face_triangles * 3);

  for (size_t face_index = 0; face_index < mesh->num_faces; ++face_index) {
    ufbx_face face = mesh->faces.data[face_index];
    uint32_t num_triangles = ufbx_triangulate_face(tri_indices.data(), tri_indices.size(), mesh, face);

    for (uint32_t i = 0; i < num_triangles * 3; ++i) {
      uint32_t corner = tri_indices[i];

      ufbx_vec3 position = ufbx_get_vertex_vec3(&mesh->vertex_position, corner);
      ufbx_vec3 normal = ufbx_get_vertex_vec3(&mesh->vertex_normal, corner);
      ufbx_vec2 uv = ufbx_get_vertex_vec2(&mesh->vertex_uv, corner);

      Vertex v;
      v.position = Vector3(position.x, position.y, position.z);
      v.normal = Vector3(normal.x, normal.y, normal.z);
      v.uv = Vector2(uv.x, 1.0f - uv.y);

      indices.push_back(static_cast<uint32_t>(vertices.size()));
      vertices.push_back(v);
    }
  }
}
```

| 関数 | 意味 |
| --- | --- |
| `mesh->max_face_triangles` | 1 つの面の三角形の最大数（作業バッファの大きさに） |
| `ufbx_triangulate_face(out, size, mesh, face)` | 面を三角形に分割。角の番号（コーナー・インデックス）を、`out` に書く。三角形の数を返す |
| `ufbx_get_vertex_vec3(&attr, corner)` | 角（コーナー）の、属性値（位置・法線）。インデックスを引いた値 |
| `ufbx_get_vertex_vec2` | UV |
| `1.0f - uv.y` | UV の V を反転（FBX は左下原点 → DirectX は左上原点） |

この書き方は頂点を角ごとに重複して作る（インデックスは、連番）ので簡単ですが頂点が多くなります。

### 頂点の重複を減らす（ufbx_generate_indices）

同じ位置・法線・UV の頂点をまとめて、インデックスで共有するには、`ufbx_generate_indices` を使います。

```cpp
ufbx_vertex_stream streams[3] = {
    {vertices.data(), vertices.size(), sizeof(Vertex)},
};

std::vector<uint32_t> result_indices(tri_indices_count);
ufbx_error error;
size_t unique = ufbx_generate_indices(streams, 1, result_indices.data(), result_indices.size(), nullptr, &error);
vertices.resize(unique);
```

| 点 | 説明 |
| --- | --- |
| `ufbx_vertex_stream` | 重複を判定する、頂点データのストリーム（先頭・個数・1 つの大きさ） |
| 返り値 | 重複を除いた、頂点の数 |
| 効果 | 頂点数が数分の一に（頂点バッファのメモリ・GPU の頂点処理の節約） |

FBX は位置・法線・UV に別々のインデックスを持つので、そのままでは、GPU の頂点バッファ（1 つのインデックス）に、使えません。頂点を角ごとに展開して、重複をまとめる、というのが定番の変換です。

### 座標系・巻き順

`target_axes = right_handed_y_up` で変換済みなら、位置・法線はそのまま使えます。ルートに X 反転の行列を掛け、巻き順は、2 番目と 3 番目のインデックスを入れ替えて CW が表にします（[深度とカリング](../../3d/depth-culling.md)）。UV だけ、V を反転します。

## ノードの階層

```cpp
void Traverse(const ufbx_node* node, std::vector<DrawItem>& out) {
  if (node->mesh != nullptr) {
    Matrix world;
    const ufbx_matrix& m = node->node_to_world;
    world = Matrix(m.m00, m.m10, m.m20, 0.0f,
                   m.m01, m.m11, m.m21, 0.0f,
                   m.m02, m.m12, m.m22, 0.0f,
                   m.m03, m.m13, m.m23, 1.0f);
    out.push_back({node->mesh, world});
  }
  for (size_t i = 0; i < node->children.count; ++i) {
    Traverse(node->children.data[i], out);
  }
}

Traverse(scene->root_node, items);
```

| 点 | 説明 |
| --- | --- |
| **`node->node_to_world`** | ノードのワールド行列（親の変換を含めた結果）。自分で親から掛け算しなくてよい |
| `ufbx_matrix` | 3×4 の行列（列優先）：`m00`〜`m23`。4 行目 `(0, 0, 0, 1)` は、省略されている |
| SimpleMath の `Matrix` | 行ベクトル規約（平行移動が 4 行目）。転置して、詰める（上の書き方） |
| `node->local_transform` | 親からのローカルな変換（`translation`・`rotation`・`scale`）。アニメーション・階層の編集に |
| `node->mesh` | メッシュへのポインタ（なければ `nullptr`） |
| `node->children` | 子ノードのリスト |

!!! note "FBX のピボットと、変換の複雑さ"
    FBX はピボット（回転の中心）・事前回転など、複雑な変換を持ちます。`node_to_world` は、これらをすべて、反映した結果なので描画にはそれを使うと簡単です。`geometry_transform`（ノードのジオメトリだけの変換）も、考慮が必要な場合があります（`geometry_to_world`）。

## マテリアル

```cpp
const ufbx_material* material = mesh->materials.data[0];

Vector4 base_color(1, 1, 1, 1);
if (material->pbr.base_color.has_value) {
  const ufbx_vec4& c = material->pbr.base_color.value_vec4;
  base_color = Vector4(c.x, c.y, c.z, c.w);
}

float metallic = material->pbr.metalness.has_value ? (float)material->pbr.metalness.value_real : 0.0f;
float roughness = material->pbr.roughness.has_value ? (float)material->pbr.roughness.value_real : 0.5f;

if (material->pbr.base_color.texture != nullptr) {
  const ufbx_texture* texture = material->pbr.base_color.texture;
  std::string path = texture->filename.data;
}
```

| 点 | 説明 |
| --- | --- |
| **`material->pbr`** | PBR のパラメータ（ufbx が各種の FBX マテリアルを、PBR に変換） |
| `ufbx_material_map` | 値（`value_vec4`・`value_real`）と、`texture`。`has_value` で、設定があるか |
| `base_color`・`metalness`・`roughness`・`normal_map`・`emission_color` | 主な項目 |
| `texture->filename` | テクスチャのファイル名（相対・絶対）。`texture->content` に、埋め込みデータがある場合も |
| `material->fbx` | FBX 固有のマテリアル（Phong など）。`pbr` で足りないとき |

FBX のマテリアルは、ツールごとに違う形（Phong・Lambert・Stingray PBR ...）で、変換がツール依存です。見た目が合わない場合は、ツール側で、PBR のマテリアルを、書き出すようにしてもらいます（[PBR](../../3d/pbr.md)）。

## スキンとアニメーション

### スキン（ボーン）

```cpp
if (mesh->skin_deformers.count > 0) {
  const ufbx_skin_deformer* skin = mesh->skin_deformers.data[0];

  for (size_t i = 0; i < skin->clusters.count; ++i) {
    const ufbx_skin_cluster* cluster = skin->clusters.data[i];
    const ufbx_node* bone = cluster->bone_node;
    const ufbx_matrix& inverse_bind = cluster->geometry_to_bone;
  }

  for (size_t v = 0; v < mesh->num_vertices; ++v) {
    ufbx_skin_vertex sv = skin->vertices.data[v];
    for (uint32_t w = 0; w < sv.num_weights; ++w) {
      ufbx_skin_weight weight = skin->weights.data[sv.weight_begin + w];
      uint32_t cluster_index = weight.cluster_index;
      float weight_value = (float)weight.weight;
    }
  }
}
```

| 要素 | 意味 |
| --- | --- |
| **`skin_deformers`** | メッシュのスキン |
| `clusters` | ボーンごとの影響の情報。`bone_node`（ボーンのノード）、`geometry_to_bone`（逆バインド行列） |
| `skin->vertices[v]` | 頂点 v の重みの範囲（`weight_begin`・`num_weights`） |
| `skin->weights[]` | 各重み（`cluster_index` ＝ どのボーンか、`weight` ＝ 重み） |

頂点あたりの重みが、4 つを超えることがあります。`max_weights_per_vertex = 4`（`ufbx_load_opts` の `skin_deformer`・または `ufbx_skin_deformer` の設定）で、4 つに制限できます。GPU スキニングでは、頂点あたり 4 本が標準です（[スキニング](../../3d/skinning-animation.md)）。

### アニメーション

```cpp
const ufbx_anim_stack* stack = scene->anim_stacks.data[0];
const ufbx_anim* anim = stack->anim;

double time = 0.5;
ufbx_transform t = ufbx_evaluate_transform(anim, node, time);

Vector3 position(t.translation.x, t.translation.y, t.translation.z);
Quaternion rotation(t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w);
Vector3 scale(t.scale.x, t.scale.y, t.scale.z);
```

| 関数・型 | 意味 |
| --- | --- |
| `scene->anim_stacks` | アニメーションのテイク（歩き・走りなど） |
| `stack->time_begin` / `time_end` | 再生範囲（秒） |
| `ufbx_evaluate_transform(anim, node, time)` | ある時刻のノードの変換（TRS） |
| `ufbx_transform` | `translation`・`rotation`（クォータニオン）・`scale` |

ゲームでは毎フレームの評価を避けるため、事前に焼く（一定のレート、たとえば 30 FPS で、全ノードの姿勢をサンプリングして、配列に）のが定番です。`ufbx_bake_anim` が、キーフレームを焼く機能を、提供します（[ベイク](../../optimize/baking.md)）。

## ゲーム用にコピーして、解放する

```cpp
MeshData game_mesh = ConvertToGameMesh(scene->meshes.data[0]);
SkeletonData skeleton = ConvertSkeleton(scene);
AnimationClip clip = BakeAnimation(scene);

ufbx_free_scene(scene);
```

| やること | 説明 |
| --- | --- |
| **変換して、自分の構造体にコピー** | 頂点・インデックス・マテリアルの値・ボーンの階層 |
| `ufbx_free_scene` | コピー後に解放（ポインタが無効になる） |
| ビルド時に変換 | 開発中は FBX、製品は独自バイナリ（[ベイク](../../optimize/baking.md)、[シリアライズ](../../optimize/serialization-speed.md)） |

## よくあるミス

??? failure "四角形のポリゴンを、そのまま扱って、三角形が足りない"
    **`ufbx_triangulate_face`** で、三角形にします。

??? failure "位置と法線・UV を同じインデックスで引いて、値がずれる"
    FBX は属性ごとにインデックスが別です。`ufbx_get_vertex_vec3(&attr, corner)` で、角ごとに引きます。

??? failure "FBX の UV を、そのまま使って、テクスチャが上下逆になる"
    V を反転（`1 - v`）します。

??? failure "`ufbx_free_scene` の後に、ノードやメッシュを触る"
    ポインタが無効です。先にコピーします。

??? failure "ノードの変換を、自分で親から掛けて、二重にかける"
    `node_to_world` は、親の変換を含めた結果です。

??? failure "頂点のスキンの重みが 4 つを超えて、GPU に入らない"
    4 つに制限します（正規化し直す）。

## 関連ページ

- [ufbx（目次）](index.md)
- [FBX と ufbx の基本](quickstart.md)
- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
