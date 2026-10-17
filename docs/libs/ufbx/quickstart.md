---
title: FBX と ufbx の基本
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# FBX と ufbx の基本

FBX は、**3D の制作ツールの間で、モデル・アニメーションをやり取りする**ための、**事実上の標準**です。**glTF**（**配布・実行向きの、軽い形式**）と違い、**制作の途中データ**（**ツールの情報を、多く含む**）を持ちます。このページは、**FBX の特徴**、**ufbx の最小の読み込み**、**座標系・単位の変換**、**シーンの構造**をまとめます。

!!! tip "ポイント"
    - FBX は<strong>Autodesk の独自形式</strong>（<strong>仕様は、非公開</strong>）。<strong>ツールの、ほぼすべてが対応</strong>。
    - <strong>ファイルが、大きく複雑</strong>（<strong>ツール固有の情報</strong>も含む）。<strong>ゲームに出すときは、glTF やゲーム専用形式に変換</strong>することが多い。
    - ufbx は <strong>`ufbx_load_file(path, &opts, &error)`</strong> で読む。<strong>失敗は `nullptr`</strong>、<strong>`error` に理由</strong>。
    - <strong>`ufbx_load_opts` で、座標系・単位・三角形化・法線の生成</strong>などを指定。
    - <strong>座標系は、FBX の中で、ツールごとに違う</strong>。<strong>読み込み時に、自分の座標系（左手・Y 上）に変換</strong>する。
    - <strong>メッシュは、「面（Face）」ごとの、ポリゴン</strong>（<strong>四角形以上もある</strong>）。<strong>三角形化が必要</strong>。

## FBX とは

| 項目 | 内容 |
| --- | --- |
| **作った所** | **Autodesk**（旧 Kaydara） |
| **形式** | **バイナリ**（主流）と、**ASCII** |
| **含むもの** | **メッシュ・マテリアル・テクスチャ・ボーン（スキン）・アニメーション・カメラ・ライト**、**ツール固有の情報** |
| **長所** | **ほぼ全てのツールが、書き出せる・読める**。**アニメーションに強い** |
| **短所** | **仕様が非公開**。**ファイルが、複雑・大きい**。**座標系・単位が、ツールごとに違う** |
| **ライセンス** | **形式は、Autodesk のもの**。**ufbx は、独自に解析**（FBX SDK を使わない） |

### FBX と glTF

| | FBX | glTF |
| --- | --- | --- |
| **目的** | **制作ツール間の、やり取り** | **配布・実行時の読み込み** |
| **仕様** | **非公開**（Autodesk） | <strong>公開（Khronos）</strong> |
| **読み込み** | **複雑**（ufbx・FBX SDK） | **簡単**（tinygltf・fastgltf） |
| **PBR** | 限定的（マテリアルの形が、ツール依存） | **標準**（メタリック・ラフネス） |
| **向く用途** | **制作パイプラインの入口** | **ゲーム・Web の実行時** |

**制作データは FBX で受け取り、ゲーム用に glTF や独自形式に変換**する流れが、よくあります（[ベイク](../../optimize/baking.md)）。**FBX を、そのまま実行時に読む**ことも、小規模なゲームでは、行われます。

## 最小の読み込み

```cpp
#include "ufbx.h"

ufbx_scene* LoadFbx(const char* path) {
  ufbx_load_opts opts = {};
  opts.target_axes = ufbx_axes_left_handed_y_up;
  opts.target_unit_meters = 1.0f;
  opts.generate_missing_normals = true;

  ufbx_error error;
  ufbx_scene* scene = ufbx_load_file(path, &opts, &error);
  if (scene == nullptr) {
    std::println("FBX の読み込みに失敗: {}", error.description.data);
    return nullptr;
  }
  return scene;
}

void Example() {
  ufbx_scene* scene = LoadFbx("assets/character.fbx");
  if (!scene) return;

  std::println("ノード数: {}、メッシュ数: {}", scene->nodes.count, scene->meshes.count);

  ufbx_free_scene(scene);
}
```

| 部分 | 意味 |
| --- | --- |
| **`ufbx_load_opts`** | **読み込みの設定**。**`= {}` で、ゼロ初期化**（**既定値**になる） |
| **`ufbx_load_file(path, &opts, &error)`** | **ファイルを読んで、`ufbx_scene*` を返す<strong>。</strong>失敗は `nullptr`** |
| **`ufbx_error`** | **失敗の理由**（`error.description.data` が、説明の文字列） |
| **`ufbx_free_scene`** | **解放**（**必ず呼ぶ**。**シーンのすべてのデータが、一括で解放**） |
| **`scene->nodes.count`** | **ノードの数**（`ufbx_node_list`：<strong>`.data`（配列）と `.count`（個数）</strong>） |

!!! note "ファイルパスは UTF-8"
    **`ufbx_load_file` のパスは、UTF-8**です（**Windows でも、日本語パスを扱える**）。**メモリから読む**には、`ufbx_load_memory(data, size, &opts, &error)` です。

## 座標系と単位を変換する

**FBX は、座標系も単位も、ツール次第**です（**Maya は Y 上・右手系・センチメートル**、**3ds Max は Z 上**、**Blender は Z 上・メートル** ...）。**読み込み時に、変換**します。

```cpp
ufbx_load_opts opts = {};
opts.target_axes = ufbx_axes_left_handed_y_up;
opts.target_unit_meters = 1.0f;
opts.space_conversion = UFBX_SPACE_CONVERSION_MODIFY_GEOMETRY;
```

| 設定 | 意味 |
| --- | --- |
| **`target_axes`** | **目的の座標系**。**`ufbx_axes_left_handed_y_up`** が、**このサイトの規約**（左手系・Y 上）と同じ（[座標系](../../gamemath/coordinate-systems.md)） |
| **`target_unit_meters`** | **1 単位が、何メートルか**（**`1.0f` ＝ メートル**） |
| **`space_conversion`** | **変換の方法**：**`ADJUST_TRANSFORMS`**（**ノードの変換行列に、補正を足す**。**頂点は、そのまま**）、**`MODIFY_GEOMETRY`**（**頂点そのものを、変換**） |
| `target_camera_axes` / `target_light_axes` | **カメラ・ライトの、向き** |

!!! warning "座標系の確認は、必須"
    **変換しないと、モデルが、横倒し・巨大・裏返し**になります。<strong>このサイトの規約（左手系・Y 上・前は +Z）</strong>に合わせる設定にして、**実際に、表示して確認**します。**ufbx の `target_axes` は、`front`（前方向）も指定**できます。

### 巻き順と UV

| 点 | 説明 |
| --- | --- |
| <strong>巻き順（CW が表にする）</strong> | **FBX は、反時計回りが表**。左手系へ変換すると鏡像になるので、**巻き順を反転して CW にする**（ufbx の `reverse_winding` などのオプション、または自分でインデックスを入れ替える。**表示して確認**。[深度とカリング](../../3d/depth-culling.md)） |
| **UV の原点** | **FBX は、左下が原点**（V が上向き）。**DirectX は左上**なので、**`v = 1 - v`** で変換（[メッシュとテクスチャ](../../3d/mesh-textures.md)） |

## シーンの構造

**`ufbx_scene`** の中は、**種類ごとのリスト**です。

<svg class="fig flow" viewBox="0 0 550 280" role="img" aria-label="ufbx_scene の構造：ノードがメッシュやマテリアルを指す（ポインタでつながる）"><defs><marker id="fl91992" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ufbx_scene の構造：ノードがメッシュやマテリアルを指す（ポインタでつながる）</text><line x1="124.1" y1="125.0" x2="201.5" y2="85.1" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><line x1="134.0" y1="148.0" x2="201.5" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><line x1="124.1" y1="171.0" x2="197.9" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><line x1="242.5" y1="87.0" x2="242.5" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><text x="242.5" y="100.0" text-anchor="middle" style="font-size:12px">mesh</text><line x1="242.5" y1="171.0" x2="242.5" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><text x="242.5" y="184.0" text-anchor="middle" style="font-size:12px">materials</text><line x1="293.0" y1="232.0" x2="374.0" y2="232.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><line x1="283.5" y1="148.0" x2="351.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91992)"/><rect x="28.0" y="128.0" width="103" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="79.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ufbx scene</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="204.5" y="44.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="242.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes</text><circle cx="206.5" cy="46.0" r="10" fill="#2ea043"/><text x="206.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="204.5" y="128.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="242.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">meshes</text><circle cx="206.5" cy="130.0" r="10" fill="#2ea043"/><text x="206.5" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="195.0" y="212.0" width="95" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="242.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">materials</text><circle cx="197.0" cy="214.0" r="10" fill="#2ea043"/><text x="197.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="377.0" y="212.0" width="88" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="421.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">textures</text><circle cx="379.0" cy="214.0" r="10" fill="#e5a828"/><text x="379.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="354.0" y="128.0" width="134" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="421.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">skin deformers</text><circle cx="356.0" cy="130.0" r="10" fill="#e5a828"/><text x="356.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="365.5" y="44.0" width="111" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="421.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">anim stacks</text><circle cx="367.5" cy="46.0" r="10" fill="#e5a828"/><text x="367.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| リスト | 内容 |
| --- | --- |
| **`scene->nodes`** | **ノード**（階層・変換）。**`ufbx_node*`** |
| **`scene->meshes`** | **メッシュ**（頂点・面） |
| **`scene->materials`** | **マテリアル** |
| **`scene->textures`** | **テクスチャ** |
| **`scene->skin_deformers`** | **スキン**（ボーンと重み） |
| **`scene->anim_stacks`** | **アニメーション**（**テイク**） |
| `scene->cameras`・`scene->lights` | カメラ・ライト |
| **`scene->root_node`** | **ルートのノード** |

### 参照は「ポインタ」

<strong>glTF は「番号」</strong>で参照しますが、<strong>ufbx は、「ポインタ」</strong>でつながります。

| | glTF（tinygltf・fastgltf） | ufbx |
| --- | --- | --- |
| **参照の方法** | **配列の番号**（`size_t`） | **ポインタ**（`ufbx_mesh*` など） |
| **ノード → メッシュ** | `node.mesh`（番号）→ `meshes[番号]` | **`node->mesh`**（ポインタ） |
| **親 → 子** | `children`（番号） | **`node->children`**（`ufbx_node_list`） |
| **シーンを解放すると** | — | **すべてのポインタが、無効**（`ufbx_free_scene`） |

**ポインタが、シーンの中のデータを指す**ので、**`ufbx_free_scene` の後は、触らない**ようにします。**ゲーム用のデータに、変換して、コピー**します。

## ufbx の特徴

| 特徴 | 説明 |
| --- | --- |
| **単一ファイル・依存なし** | **導入が、簡単** |
| **速い** | **公式 SDK より、速い**ことが多い |
| **メモリ安全を意識** | **不正なファイルでも、クラッシュしにくい**（ファジングで検証されている） |
| **スレッド対応** | **読み込みを、別スレッドで**できる |
| **読み込み専用** | **書き出しは、できない** |
| **ライセンス** | **MIT またはパブリックドメイン**（**製品に、組み込みやすい**） |
| **アニメーションの評価** | **`ufbx_evaluate_transform`** で、**任意の時刻の姿勢**を求められる |

## よくあるミス

??? failure "`ufbx_load_file` が `nullptr` を返すのに、`error` を見ない"
    **`error.description.data`** に、理由があります。**ログに出します**。

??? failure "`ufbx_free_scene` の後に、メッシュのポインタを使う"
    **すべて無効**です。**ゲーム用のデータに、コピー**してから、解放します。

??? failure "座標系を指定せず、モデルが、横倒し・巨大に表示される"
    **`target_axes`・`target_unit_meters`** を指定します。

??? failure "UV が、上下逆になる"
    **FBX は、左下原点**。**`v = 1 - v`**。

??? failure "四角形のポリゴンを、そのまま三角形として扱って、形が崩れる"
    **面は、四角形以上もあります**。**三角形化**します（[データの取り出し方](reading.md)）。

## 関連ページ

- [ufbx（目次）](index.md)
- [データの取り出し方](reading.md)
- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
- [座標系](../../gamemath/coordinate-systems.md)
- [FBX SDK](../fbxsdk/index.md)
