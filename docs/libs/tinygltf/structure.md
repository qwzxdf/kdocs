---
title: glTF の構造
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# glTF の構造

glTF のファイルは、**種類ごとの配列**（`nodes`、`meshes`、`accessors` ...）の集まりです。**配列の要素同士は、ポインタではなく、「配列の何番目か」という番号（インデックス）でつながっています**。この<strong>「参照は、インデックスで表す」</strong>という約束を理解すれば、glTF の構造は、ほぼ、分かります。このページは、**各配列の役割**と、**番号でつながる仕組み**を、図と一緒に説明します。ここで説明する構造は、そのまま、tinygltf の `tinygltf::Model` の構造です。

!!! tip "ポイント"
    - glTF の中の<strong>「参照」は、すべて「配列の番号（インデックス）」</strong>。<strong>ポインタでも、名前でもない</strong>。
    - たとえば、<strong>`"mesh": 0`</strong> は、「<strong>`meshes` 配列の、0 番目</strong>」という意味。
    - <strong>どの配列の番号なのかは、キーの名前で決まっている</strong>（`mesh` なら `meshes`、`material` なら `materials`）。
    - <strong>データ本体は、`buffers` → `bufferViews` → `accessors` の 3 段階</strong>で、「どこを、どう読むか」を指定する。
    - <strong>番号は 0 始まり</strong>。<strong>配列の順番を変えると、番号の参照が、すべてずれる</strong>（書き換えるときは、全部直す）。
    - tinygltf では、<strong>`model.meshes[i]`、`model.accessors[j]` のように、番号で、そのまま配列を引く</strong>。

## 参照は「番号」で表す

glTF の要素は、**配列の中に並んでいます**。ほかの要素を指したいときは、**その要素が、配列の何番目かを書く**だけです。

<svg class="fig" viewBox="0 0 640 300" role="img" aria-label="配列の番号による参照">
<defs><marker id="sa" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">nodes（配列）</text>
<rect x="20" y="36" width="150" height="34" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><text x="30" y="58">[0] 床</text>
<rect x="20" y="76" width="150" height="34" fill="rgba(76,139,245,0.35)" stroke="currentColor"/><text x="30" y="98">[1] 敵  "mesh": 1</text>
<rect x="20" y="116" width="150" height="34" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><text x="30" y="138">[2] 木</text>
<text x="240" y="22" class="fig-title">meshes（配列）</text>
<rect x="240" y="36" width="170" height="34" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><text x="250" y="58">[0] 床のメッシュ</text>
<rect x="240" y="76" width="170" height="34" fill="rgba(76,139,245,0.35)" stroke="currentColor"/><text x="250" y="98">[1] 敵のメッシュ</text>
<line x1="170" y1="93" x2="238" y2="93" stroke="currentColor" stroke-width="2" marker-end="url(#sa)"/>
<text x="176" y="84" style="font-size:11px">1 番目</text>
<text x="480" y="22" class="fig-title">materials（配列）</text>
<rect x="480" y="36" width="140" height="34" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><text x="490" y="58">[0] 石</text>
<rect x="480" y="76" width="140" height="34" fill="rgba(46,160,67,0.35)" stroke="currentColor"/><text x="490" y="98">[1] 敵の皮膚</text>
<text x="240" y="150" style="font-size:12px">"material": 1 が、meshes[1] の中に書いてある</text>
<line x1="410" y1="93" x2="478" y2="93" stroke="currentColor" stroke-width="2" marker-end="url(#sa)"/>
<text x="20" y="195" class="fig-title">どの配列の番号かは、キーの名前で決まる</text>
<text x="20" y="220">"mesh": 1　→ meshes の 1 番目　　　"material": 1　→ materials の 1 番目</text>
<text x="20" y="245">"children": [2, 3]　→ nodes の 2 番目と 3 番目　　"texture" の "index": 0　→ textures の 0 番目</text>
<text x="20" y="275" style="font-size:12px">番号だけでは、「どの配列か」は分からない。キー名で判断する</text>
</svg>

### なぜ「番号」なのか

| 理由 | 説明 |
| --- | --- |
| **ファイルに書ける** | ポインタ（アドレス）は、ファイルに保存しても意味がない。**番号なら、そのまま保存できる** |
| **読み込み側で、自由に配置できる** | メモリのどこに置くかは、**読み込む側が決める**。番号は、**配列の位置**さえ分かれば、引ける |
| **共有しやすい** | **1 つのメッシュを、複数のノードから参照**（インスタンス）できる。**同じ番号を書く**だけ |
| **コンパクト** | 数字 1 つで済む |
| **どの言語でも読める** | JSON の数字なので、**言語に依存しない** |

[ハンドル](../../engine/handle.md)や、[ポインタをインデックスにする](../../optimize/data-layout.md)のと、同じ考え方です。

### 番号は、配列の何番目か（0 始まり）

```json
{
  "nodes":  [ { "name": "A" }, { "name": "B", "mesh": 0 }, { "name": "C" } ],
  "meshes": [ { "name": "Enemy" } ]
}
```

| 書き方 | 意味 |
| --- | --- |
| `nodes[1]` の `"mesh": 0` | `meshes` 配列の **0 番目**（`Enemy`）を使う |
| `-1`（tinygltf の既定値） | **参照なし**（その要素は、使わない） |

**tinygltf では、「参照なし」は `-1` で表されます**（`int` の既定値が `-1`）。**使う前に、`-1` かどうかを必ず調べます**。

```cpp
const tinygltf::Node& node = model.nodes[1];
if (node.mesh >= 0) {
  const tinygltf::Mesh& mesh = model.meshes[node.mesh];
}
```

## 全体の地図

<div class="anim" data-type="graph" data-label="glTF の構造：矢印はすべて「番号（インデックス）」で参照する">
n scene scenes 0 0 hit
n node nodes 1 0
l scene node hit nodes_（番号）
---
n scene scenes 0 0
n node nodes 1 0 hit
n mesh meshes 2 0 new
n skin skins 1 1 new
l scene node nodes
l node mesh hit mesh
l node skin hit skin
---
n node nodes 1 0
n mesh meshes 2 0 hit
n acc accessors 3 0 new
n mat materials 2 1 new
l node mesh mesh
l mesh acc hit attributes_/_indices
l mesh mat hit material
---
n mesh meshes 2 0
n acc accessors 3 0 hit
n bv bufferViews 4 0 new
n buf buffers 4 1 new
l mesh acc attributes_/_indices
l acc bv hit bufferView
l bv buf hit buffer
---
n mat materials 2 1 hit
n tex textures 3 1 new
n img images 3 2 new
n smp samplers 4 2 new
l mat tex hit baseColorTexture_.index
l tex img hit source
l tex smp hit sampler
</div>

| 参照元 | キー | 参照先（配列） |
| --- | --- | --- |
| **`scenes[i].nodes`** | `[...]` | `nodes` |
| **`nodes[i].children`** | `[...]` | `nodes`（子ノード） |
| **`nodes[i].mesh`** | 番号 | `meshes` |
| **`nodes[i].skin`** | 番号 | `skins` |
| **`nodes[i].camera`** | 番号 | `cameras` |
| **`meshes[i].primitives[j].attributes`** | `{"POSITION": 番号, ...}` | `accessors` |
| **`meshes[i].primitives[j].indices`** | 番号 | `accessors` |
| **`meshes[i].primitives[j].material`** | 番号 | `materials` |
| **`accessors[i].bufferView`** | 番号 | `bufferViews` |
| **`bufferViews[i].buffer`** | 番号 | `buffers` |
| **`materials[i]....baseColorTexture.index`** | 番号 | `textures` |
| **`textures[i].source`** | 番号 | `images` |
| **`textures[i].sampler`** | 番号 | `samplers` |
| **`skins[i].joints`** | `[...]` | `nodes`（骨になるノード） |
| **`skins[i].inverseBindMatrices`** | 番号 | `accessors` |
| **`animations[i].channels[j].target.node`** | 番号 | `nodes` |
| **`animations[i].samplers[j].input / output`** | 番号 | `accessors`（時刻・値） |

## 実際のファイルを読んでみる

glTF の最も小さな例（三角形 1 つ）です。**番号で、どうつながっているか**を、追いかけます。

```json
{
  "scene": 0,
  "scenes":  [ { "nodes": [ 0 ] } ],
  "nodes":   [ { "mesh": 0 } ],
  "meshes":  [ { "primitives": [ { "attributes": { "POSITION": 1 }, "indices": 0 } ] } ],
  "buffers": [ { "uri": "triangle.bin", "byteLength": 44 } ],
  "bufferViews": [
    { "buffer": 0, "byteOffset": 0, "byteLength": 6,  "target": 34963 },
    { "buffer": 0, "byteOffset": 8, "byteLength": 36, "target": 34962 }
  ],
  "accessors": [
    { "bufferView": 0, "componentType": 5123, "count": 3, "type": "SCALAR" },
    { "bufferView": 1, "componentType": 5126, "count": 3, "type": "VEC3", "max": [1, 1, 0], "min": [0, 0, 0] }
  ],
  "asset": { "version": "2.0" }
}
```

### 番号を、順に追いかける

<div class="anim" data-type="graph" data-label="三角形の頂点の位置を探す：番号をたどって、バイナリのどこかを見つける">
n scn scene_=_0 0 0 hit
---
n scn scene_=_0 0 0
n sc scenes[0]_.nodes=[0] 1 0 hit
l scn sc hit
---
n sc scenes[0]_.nodes=[0] 1 0
n nd nodes[0]_.mesh=0 2 0 hit
l sc nd hit
---
n nd nodes[0]_.mesh=0 2 0
n ms meshes[0]_POSITION=1 3 0 hit
l nd ms hit
---
n ms meshes[0]_POSITION=1 3 0
n ac accessors[1]_.bufferView=1 3 1 hit
l ms ac hit POSITION
---
n ac accessors[1]_.bufferView=1 3 1
n bv bufferViews[1]_.buffer=0_offset=8 2 1 hit
l ac bv hit
---
n bv bufferViews[1]_.buffer=0_offset=8 2 1
n bf buffers[0]_triangle.bin 1 1 hit
l bv bf hit
</div>

| 手順 | 見るところ | 値 | 意味 |
| --- | --- | --- | --- |
| 1 | `scene` | `0` | 表示する**シーン**は、`scenes[0]` |
| 2 | `scenes[0].nodes` | `[0]` | シーンの**ノード**は、`nodes[0]` |
| 3 | `nodes[0].mesh` | `0` | そのノードの**メッシュ**は、`meshes[0]` |
| 4 | `meshes[0].primitives[0].attributes.POSITION` | `1` | **頂点の位置**は、`accessors[1]` |
| 5 | `accessors[1].bufferView` | `1` | そのデータは、`bufferViews[1]` の範囲 |
| 6 | `bufferViews[1].buffer` | `0` | その範囲は、`buffers[0]`（`triangle.bin`）の、**8 バイト目から 36 バイト** |
| 7 | `meshes[0].primitives[0].indices` | `0` | <strong>インデックス（三角形の番号リスト）</strong>は、`accessors[0]` |

**番号をたどるだけで、「どのファイルの、何バイト目から、何を読むか」が、分かります**。

## データ本体：buffers・bufferViews・accessors

**頂点やインデックスなどの数値**は、**バイナリ**で保存されています。それを取り出すために、**3 段階**で指定します。

<svg class="fig" viewBox="0 0 640 300" role="img" aria-label="buffer・bufferView・accessor の関係">
<defs><marker id="sb" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">buffer（バイナリ全体）</text>
<rect x="20" y="34" width="600" height="36" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-width="2"/>
<rect x="20" y="34" width="100" height="36" fill="rgba(229,170,40,0.45)" stroke="currentColor"/><text x="30" y="57">インデックス</text>
<rect x="130" y="34" width="300" height="36" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="140" y="57">頂点（位置・法線・UV が、まとまっている）</text>
<rect x="440" y="34" width="180" height="36" fill="rgba(46,160,67,0.4)" stroke="currentColor"/><text x="450" y="57">アニメーションの値</text>
<text x="20" y="102" class="fig-title">bufferView（buffer の、どこからどこまでか）</text>
<rect x="20" y="114" width="100" height="30" fill="rgba(229,170,40,0.45)" stroke="currentColor"/><text x="28" y="134">view[0]</text>
<rect x="130" y="114" width="300" height="30" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="138" y="134">view[1]  buffer=0, byteOffset, byteLength, byteStride</text>
<line x1="70" y1="72" x2="70" y2="112" stroke="currentColor" stroke-width="1.5" marker-end="url(#sb)"/>
<line x1="280" y1="72" x2="280" y2="112" stroke="currentColor" stroke-width="1.5" marker-end="url(#sb)"/>
<text x="20" y="180" class="fig-title">accessor（bufferView の中の、どう読むか）</text>
<rect x="130" y="192" width="90" height="30" fill="rgba(76,139,245,0.7)" stroke="currentColor"/><text x="138" y="212" style="fill:#fff">位置</text>
<rect x="220" y="192" width="90" height="30" fill="rgba(46,160,67,0.7)" stroke="currentColor"/><text x="228" y="212" style="fill:#fff">法線</text>
<rect x="310" y="192" width="60" height="30" fill="rgba(229,72,77,0.7)" stroke="currentColor"/><text x="316" y="212" style="fill:#fff">UV</text>
<rect x="370" y="192" width="90" height="30" fill="rgba(76,139,245,0.7)" stroke="currentColor"/><text x="378" y="212" style="fill:#fff">位置</text>
<text x="20" y="250" style="font-size:12px">POSITION accessor：componentType=FLOAT, type=VEC3, count=頂点数, byteOffset=0</text>
<text x="20" y="270" style="font-size:12px">NORMAL accessor：byteOffset=12 …（同じ bufferView の、別の場所）</text>
<line x1="180" y1="146" x2="180" y2="190" stroke="currentColor" stroke-width="1.5" marker-end="url(#sb)"/>
</svg>

| 段階 | 役割 | 主なキー |
| --- | --- | --- |
| **buffer** | **バイナリ全体**（`.bin` ファイル、または `.glb` 内のデータ） | `uri`（ファイル名）、`byteLength` |
| **bufferView** | buffer の**ある範囲** | `buffer`（番号）、`byteOffset`、`byteLength`、`byteStride`、`target` |
| **accessor** | bufferView の中の、<strong>「どう読むか」</strong> | `bufferView`（番号）、`byteOffset`、`componentType`、`count`、`type` |

### accessor が持つ情報

| キー | 意味 | 例 |
| --- | --- | --- |
| **`componentType`** | **1 つの数の型** | `5126`＝float、`5123`＝unsigned short、`5125`＝unsigned int、`5121`＝unsigned byte |
| **`type`** | **まとまりの種類** | `"SCALAR"`（1 つ）、`"VEC2"`、`"VEC3"`、`"VEC4"`、`"MAT4"` |
| **`count`** | **要素の個数** | 頂点の数 |
| **`byteOffset`** | bufferView の先頭からの、ずれ | `0`、`12` |
| `normalized` | 整数を、0〜1 に変換して読むか | UV や色（`unsigned byte`）に使う |
| `min` / `max` | 値の範囲 | **POSITION は必須**（境界の計算に使える） |

<strong>「`VEC3` の `float` が、`count` 個」</strong>と指定すれば、**頂点の位置の並び**が、取り出せます。

### byteStride（インターリーブ）

**位置・法線・UV を、1 頂点ぶんずつ交互に並べる**（インターリーブ）と、**頂点バッファそのまま**で GPU に渡せます。

```text
通常：  [位置×N] [法線×N] [UV×N]           （項目ごとに、まとまる）
交互：  [位置 法線 UV][位置 法線 UV] ...     （1 頂点ずつ、まとまる）  → byteStride = 32 など
```

| 項目 | 説明 |
| --- | --- |
| **`byteStride` が無い** | 要素は、**隙間なく**並ぶ |
| **`byteStride` がある** | **次の要素までの距離**。要素の大きさより大きい |

tinygltf では、**`Accessor::ByteStride(bufferView)`** が、**実際の間隔**を返します（隙間なしなら、要素のサイズ）。

## シーンとノード

**ノード**は、<strong>3D 空間の中の、1 つの「物」</strong>です。**親子関係**を持ち、**位置・回転・拡大**を持ちます。

```json
"nodes": [
  { "name": "Character", "children": [1, 2], "translation": [0, 0, 5] },
  { "name": "Body", "mesh": 0 },
  { "name": "Weapon", "mesh": 1, "translation": [0.5, 1, 0], "rotation": [0, 0, 0, 1] }
]
```

<div class="anim" data-type="graph" data-label="ノードは親子の木。子の位置は、親の位置を基準にした相対値">
n s scenes[0] 0 1 hit
---
n s scenes[0] 0 1
n c nodes[0]_Character 1 1 new
l s c hit nodes=[0]
---
n s scenes[0] 0 1 dim
n c nodes[0]_Character 1 1
n b nodes[1]_Body_(mesh_0) 2 0 new
n w nodes[2]_Weapon_(mesh_1) 2 2 new
l c b hit children
l c w hit children
</div>

| キー | 意味 |
| --- | --- |
| **`children`** | **子ノードの番号**のリスト。**子の位置・回転は、親からの相対値** |
| **`mesh`** | このノードに**表示するメッシュ**の番号 |
| **`translation`** | 位置 `[x, y, z]` |
| **`rotation`** | 回転 `[x, y, z, w]`（クォータニオン） |
| **`scale`** | 拡大 `[x, y, z]` |
| **`matrix`** | 上の 3 つの代わりに、**4×4 行列**（16 個、列優先）で指定 |
| `skin` | **骨**を使うとき、スキンの番号 |
| `camera` | カメラを使うとき、カメラの番号 |

!!! warning "TRS と matrix は、どちらか一方"
    `translation` / `rotation` / `scale` と `matrix` は、**どちらか一方**で指定されます。tinygltf では、**`matrix` が空かどうかで、判断**します（[データの取り出し方](reading.md)）。

**`scenes[i].nodes`** は、**そのシーンの根（ルート）のノード**の番号です。**根から `children` をたどると、全ノードに到達**します。

## メッシュとプリミティブ

**`meshes` の 1 つ**は、<strong>複数の「プリミティブ」</strong>を持ちます。**プリミティブ**は、**1 つのマテリアルで描く、三角形の集まり**です。

```json
"meshes": [
  {
    "name": "Character",
    "primitives": [
      { "attributes": { "POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2 }, "indices": 3, "material": 0 },
      { "attributes": { "POSITION": 4, "NORMAL": 5, "TEXCOORD_0": 6 }, "indices": 7, "material": 1 }
    ]
  }
]
```

| キー | 意味 |
| --- | --- |
| **`attributes`** | **頂点の項目名 → accessor の番号**の対応 |
| **`indices`** | **三角形のインデックス**の accessor の番号（無ければ、頂点を順に並べる） |
| **`material`** | **マテリアルの番号**（省略すると、既定のマテリアル） |
| `mode` | 描画の種類（`4`＝三角形のリスト。**通常**） |

### 頂点属性の名前

| 名前 | 内容 | type |
| --- | --- | --- |
| **`POSITION`** | 位置 | `VEC3` float |
| **`NORMAL`** | 法線 | `VEC3` float |
| **`TANGENT`** | 接線（法線マップ用）。<strong>w は、従接線の向き（±1）</strong> | `VEC4` float |
| **`TEXCOORD_0`** | UV（1 組目） | `VEC2` |
| `TEXCOORD_1` | UV（2 組目。ライトマップなど） | `VEC2` |
| `COLOR_0` | 頂点カラー | `VEC3` / `VEC4` |
| **`JOINTS_0`** | **影響を受ける骨**の番号（4 つ） | `VEC4` unsigned byte/short |
| **`WEIGHTS_0`** | **骨の重み**（4 つ。合計 1） | `VEC4` float |

**このプリミティブごとに、1 回の描画**（`DrawIndexed`）になります。**マテリアルが 2 つなら、プリミティブは 2 つ**です（[メッシュとテクスチャ](../../3d/mesh-textures.md)）。

## マテリアル・テクスチャ・画像・サンプラー

**マテリアル**は、**質感の設定**です。**テクスチャ**を、番号で参照します。

```json
"materials": [
  {
    "name": "Skin",
    "pbrMetallicRoughness": {
      "baseColorTexture": { "index": 0 },
      "baseColorFactor": [1, 1, 1, 1],
      "metallicFactor": 0.0,
      "roughnessFactor": 0.8,
      "metallicRoughnessTexture": { "index": 1 }
    },
    "normalTexture": { "index": 2 },
    "occlusionTexture": { "index": 1 },
    "emissiveFactor": [0, 0, 0]
  }
],
"textures": [
  { "source": 0, "sampler": 0 },
  { "source": 1, "sampler": 0 },
  { "source": 2, "sampler": 0 }
],
"images":   [ { "uri": "skin_albedo.png" }, { "uri": "skin_orm.png" }, { "uri": "skin_normal.png" } ],
"samplers": [ { "magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497 } ]
```

<div class="anim" data-type="graph" data-label="マテリアル → テクスチャ → 画像・サンプラー。ここも、すべて番号でつながる">
n m materials[0] 0 1 hit
---
n m materials[0] 0 1
n t textures[0] 1 1 new
l m t hit baseColorTexture.index=0
---
n m materials[0] 0 1 dim
n t textures[0] 1 1
n i images[0]_skin_albedo.png 2 0 new
n s samplers[0] 2 2 new
l t i hit source=0
l t s hit sampler=0
</div>

| 配列 | 役割 | 主なキー |
| --- | --- | --- |
| **`materials`** | 質感の設定 | `pbrMetallicRoughness`（`baseColorFactor`・`metallicFactor`・`roughnessFactor`・各テクスチャ）、`normalTexture`、`occlusionTexture`、`emissiveTexture`、`alphaMode` |
| **`textures`** | **画像 + サンプラー**の組み合わせ | **`source`**（画像の番号）、**`sampler`**（サンプラーの番号） |
| **`images`** | **画像データ** | `uri`（ファイル名）、または `bufferView`（`.glb` に埋め込み） |
| **`samplers`** | **読み方の設定** | `magFilter`、`minFilter`、`wrapS`、`wrapT` |

### テクスチャの参照は 2 段階

| 段階 | 内容 |
| --- | --- |
| **マテリアル → テクスチャ** | `{ "index": 0 }` ＝ `textures[0]` |
| **テクスチャ → 画像・サンプラー** | `source` ＝ `images[…]`、`sampler` ＝ `samplers[…]` |

**同じ画像を、別のサンプラーで使う**ときは、`textures` の要素が増えます（画像は 1 つ、テクスチャが 2 つ）。

### PBR のテクスチャ

| 場所 | 内容 | 色空間 |
| --- | --- | --- |
| `baseColorTexture` | ベースカラー（RGB + A） | **sRGB** |
| `metallicRoughnessTexture` | **G ＝ roughness、B ＝ metallic** | リニア |
| `normalTexture` | 法線マップ | リニア |
| `occlusionTexture` | **R ＝ AO**（metallicRoughness と、**同じ画像**を使うことが多い） | リニア |
| `emissiveTexture` | 自己発光 | sRGB |

**色空間を、間違えない**ようにします（[PBR](../../3d/pbr.md#色空間とトーンマッピング)）。

## スキンとアニメーション

### スキン（骨）

**骨は、普通のノードです**。**スキン**は、<strong>「どのノードを、骨として使うか」の一覧</strong>を持ちます。

```json
"skins": [
  { "joints": [3, 4, 5, 6], "inverseBindMatrices": 8, "skeleton": 3 }
]
```

| キー | 意味 |
| --- | --- |
| **`joints`** | **骨になるノードの番号**のリスト。**順番が、`JOINTS_0` の番号に対応** |
| **`inverseBindMatrices`** | **逆バインド行列**の accessor の番号（`MAT4`）。**骨ごとに 1 つ**（[スキニング](../../3d/skinning-animation.md)の、オフセット行列） |
| `skeleton` | 骨の根のノードの番号 |

<strong>頂点の `JOINTS_0` の値 `2` は、「`skins[0].joints[2]` の骨」</strong>という意味です（**ノードの番号そのものではなく、`joints` 配列の位置**）。ここも、**番号の、もう 1 段の参照**です。

<div class="anim" data-type="graph" data-label="頂点の骨番号は、joints 配列の位置。その先が、ノードの番号">
n v JOINTS_0_=_2 0 1 hit
---
n v JOINTS_0_=_2 0 1
n j skins[0].joints[2]_=_5 1 1 hit
l v j hit joints_の_2_番目
---
n j skins[0].joints[2]_=_5 1 1
n nd nodes[5]_（骨） 2 1 hit
l j nd hit ノード番号
</div>

### アニメーション

**アニメーション**は、<strong>「どのノードの、何を、どう変えるか」</strong>です。

```json
"animations": [
  {
    "name": "Walk",
    "samplers": [ { "input": 10, "output": 11, "interpolation": "LINEAR" } ],
    "channels": [ { "sampler": 0, "target": { "node": 5, "path": "rotation" } } ]
  }
]
```

<div class="anim" data-type="graph" data-label="アニメーション：channel が、sampler と、動かすノードを指す">
n a animations[0] 0 1 hit
---
n a animations[0] 0 1
n c channels[0] 1 1 new
l a c hit
---
n c channels[0] 1 1
n sm samplers[0] 2 0 new
n nd nodes[5]_.rotation 2 2 new
l c sm hit sampler=0
l c nd hit target.node=5
---
n sm samplers[0] 2 0
n i accessors[10]_（時刻） 3 -0.3 new
n o accessors[11]_（回転の値） 3 0.7 new
l sm i hit input
l sm o hit output
</div>

| 要素 | 意味 |
| --- | --- |
| **`channels[j].target.node`** | **動かすノードの番号** |
| **`channels[j].target.path`** | **何を動かすか**：`translation` / `rotation` / `scale` / `weights` |
| **`channels[j].sampler`** | **`samplers` の番号**（値の出所） |
| **`samplers[j].input`** | **時刻**の accessor の番号（`SCALAR` float） |
| **`samplers[j].output`** | **値**の accessor の番号（`VEC3` / `VEC4`） |
| `interpolation` | 補間：`LINEAR`、`STEP`、`CUBICSPLINE` |

**時刻の配列と、値の配列は、同じ数**で、**時刻 `input[k]` のときの値が `output[k]`** です（[スキニング](../../3d/skinning-animation.md)の、キーフレーム）。

## 構造の覚え方

| 質問 | 答え |
| --- | --- |
| **何を表示するか** | `scenes` → `nodes`（親子の木） |
| **ノードは何を持つか** | **位置・回転・拡大**（TRS）と、`mesh` / `skin` / `camera` の**番号** |
| **メッシュの形は** | `meshes` → `primitives` → `attributes` / `indices`（**accessor の番号**） |
| **数値の実体は** | `accessors` → `bufferViews` → `buffers`（**3 段階**で、番号をたどる） |
| **見た目は** | `primitives[].material` → `materials` → `textures` → `images` + `samplers` |
| **骨は** | `skins[].joints`（**ノードの番号の一覧**）、頂点の `JOINTS_0` は、**joints の位置** |
| **動きは** | `animations` → `channels`（**どのノードを**）、`samplers`（**時刻と値の accessor**） |

**すべて、「配列の何番目か」で、つながっています**。

## よくあるミス

??? failure "番号を、別の配列の番号と取り違える"
    `nodes[1].mesh = 0` は、**`meshes[0]`**です。`nodes[0]` ではありません。**キー名で、配列を判断**します。

??? failure "`-1`（参照なし）を調べず、`model.meshes[-1]` を引く"
    範囲外アクセスです。**使う前に、`>= 0` を確認**します。

??? failure "`JOINTS_0` の値を、ノード番号として使う"
    **`skins[…].joints[値]`** を引いた先が、ノード番号です。

??? failure "`byteStride` を無視して、隙間なしで読む"
    **インターリーブ**のデータは、`byteStride` ごとに、次の要素が来ます。

??? failure "accessor の `byteOffset` と、bufferView の `byteOffset` の、足し忘れ"
    **データの先頭 ＝ buffer の先頭 ＋ bufferView.byteOffset ＋ accessor.byteOffset** です。

??? failure "配列の順番を入れ替えて、参照が壊れる"
    **番号の参照は、すべて、ずれます**。入れ替えたら、**参照している場所も、すべて書き換え**ます（ツールを使う）。

??? failure "1 つのメッシュに、複数のプリミティブがあることを忘れる"
    **マテリアルごとに、プリミティブが分かれます**。`primitives[0]` だけを読むと、**一部が表示されません**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] glTF は<strong>種類ごとの配列</strong>。<strong>参照は、すべて「配列の番号（0 始まり）」</strong>
    - [x] <strong>どの配列かは、キー名で決まる</strong>（`mesh` → `meshes`、`material` → `materials`）。<strong>`-1` は、参照なし</strong>
    - [x] <strong>データ本体は、buffer → bufferView → accessor の 3 段階</strong>。<strong>accessor が「どう読むか」</strong>
    - [x] <strong>ノードは親子の木</strong>。<strong>メッシュは、プリミティブ（マテリアルごと）の集まり</strong>
    - [x] <strong>マテリアル → texture → image + sampler</strong>。<strong>骨の番号（`JOINTS_0`）は、`joints` の位置</strong>
    - [x] <strong>アニメーションは、channel（どのノード）＋ sampler（時刻と値の accessor）</strong>

## 関連ページ

- [tinygltf（glTF の読み込み）](index.md)
- [データの取り出し方](reading.md)
- [ハンドル](../../engine/handle.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
- [PBR（物理ベースレンダリング）](../../3d/pbr.md)
