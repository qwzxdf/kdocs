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

## 誰が、誰を参照しているか（全体の参照図）

**どの配列の、どのフィールドが、どの配列を指しているか**を、1 枚にまとめた図です。

<svg class="fig" viewBox="0 0 760 470" role="img" aria-label="glTF の要素が、誰を参照しているか"><defs><marker id="rf" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="18" class="fig-title">矢印の元が、「番号」を持っている側。矢印の先が、その番号が指す配列</text><rect x="20" y="40" width="120" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="30" y="68" style="font-weight:700">scenes</text><rect x="200" y="40" width="120" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="210" y="68" style="font-weight:700">nodes</text><rect x="390" y="40" width="120" height="56" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="400" y="68" style="font-weight:700">meshes</text><rect x="590" y="40" width="130" height="56" rx="6" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="2"/><text x="600" y="68" style="font-weight:700">accessors</text><rect x="20" y="170" width="120" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="30" y="198" style="font-weight:700">cameras</text><rect x="200" y="170" width="120" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="210" y="198" style="font-weight:700">skins</text><rect x="390" y="170" width="120" height="56" rx="6" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="2"/><text x="400" y="198" style="font-weight:700">materials</text><rect x="590" y="170" width="130" height="56" rx="6" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="2"/><text x="600" y="198" style="font-weight:700">bufferViews</text><rect x="20" y="300" width="120" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="30" y="328" style="font-weight:700">animations</text><rect x="390" y="300" width="120" height="56" rx="6" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="2"/><text x="400" y="328" style="font-weight:700">textures</text><rect x="590" y="300" width="130" height="56" rx="6" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="2"/><text x="600" y="328" style="font-weight:700">buffers</text><rect x="390" y="410" width="120" height="48" rx="6" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="2"/><text x="400" y="438" style="font-weight:700">images</text><rect x="590" y="410" width="130" height="48" rx="6" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="2"/><text x="600" y="438" style="font-weight:700">samplers</text><line x1="140" y1="68" x2="198" y2="68" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="142" y="60" style="font-size:11px">.nodes[]</text><line x1="320" y1="68" x2="388" y2="68" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="334" y="60" style="font-size:11px">.mesh</text><line x1="510" y1="60" x2="588" y2="60" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="510" y="52" style="font-size:11px">.attributes</text><line x1="510" y1="78" x2="588" y2="78" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="520" y="92" style="font-size:11px">.indices</text><line x1="260" y1="170" x2="260" y2="98" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="264" y="140" style="font-size:11px">.joints[]</text><line x1="210" y1="96" x2="100" y2="168" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="110" y="128" style="font-size:11px">.camera</text><line x1="450" y1="96" x2="450" y2="168" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="455" y="134" style="font-size:11px">.material</text><line x1="655" y1="96" x2="655" y2="168" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="660" y="134" style="font-size:11px">.bufferView</text><line x1="655" y1="226" x2="655" y2="298" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="660" y="266" style="font-size:11px">.buffer</text><line x1="450" y1="226" x2="450" y2="298" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="455" y="262" style="font-size:11px">.baseColorTexture.index など</text><line x1="450" y1="356" x2="450" y2="408" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="455" y="386" style="font-size:11px">.source</text><line x1="510" y1="340" x2="590" y2="420" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)" /><text x="552" y="372" style="font-size:11px">.sampler</text><path d="M 20 330 L 8 330 L 8 118 L 230 118 L 230 98" fill="none" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)"/><text x="14" y="318" style="font-size:11px">.channels[].target.node</text><path d="M 300 40 C 300 14 240 14 240 38" fill="none" stroke="currentColor" stroke-width="1.8" marker-end="url(#rf)"/><text x="224" y="12" style="font-size:11px">.children[]</text><text x="20" y="400" style="font-size:11px">そのほか：skins.inverseBindMatrices → accessors　／　animations.samplers[].input・output → accessors</text></svg>

### 実際の参照の連なり（キャラクターの例）

**1 体のキャラクターが、どの番号をたどって、数値データまで行きつくか**を、ツリーで示します。`→` の先が、その番号が指す要素です。

<ul class="reftree">
<li><code>scene: 0</code> → <b>scenes[0]</b>
<ul>
<li><code>nodes: [0]</code> → <b>nodes[0]</b>（Character）
<ul>
<li><code>children: [1, 2]</code> → <b>nodes[1]</b>（Body）、<b>nodes[2]</b>（Weapon）
<ul>
<li><b>nodes[1]</b>：<code>mesh: 0</code> → <b>meshes[0]</b>
<ul>
<li><code>primitives[0].attributes.POSITION: 1</code> → <b>accessors[1]</b> → <code>bufferView: 1</code> → <b>bufferViews[1]</b> → <code>buffer: 0</code> → <b>buffers[0]</b>
</li>
<li><code>primitives[0].indices: 0</code> → <b>accessors[0]</b> → <code>bufferView: 0</code> → <b>bufferViews[0]</b> → <code>buffer: 0</code> → <b>buffers[0]</b>
</li>
<li><code>primitives[0].material: 0</code> → <b>materials[0]</b>
<ul>
<li><code>baseColorTexture.index: 0</code> → <b>textures[0]</b>
<ul>
<li><code>source: 0</code> → <b>images[0]</b>（skin_albedo.png）</li>
<li><code>sampler: 0</code> → <b>samplers[0]</b></li>
</ul>
</li>
<li><code>normalTexture.index: 2</code> → <b>textures[2]</b> → <code>source: 2</code> → <b>images[2]</b></li>
</ul>
</li>
</ul>
</li>
<li><b>nodes[2]</b>：<code>mesh: 1</code> → <b>meshes[1]</b>（以下、同じ形）</li>
</ul>
</li>
<li><b>nodes[0]</b>：<code>skin: 0</code> → <b>skins[0]</b>
<ul>
<li><code>joints: [3, 4, 5]</code> → <b>nodes[3]</b>・<b>nodes[4]</b>・<b>nodes[5]</b>（骨になるノード）</li>
<li><code>inverseBindMatrices: 8</code> → <b>accessors[8]</b></li>
</ul>
</li>
</ul>
</li>
<li><b>animations[0]</b>
<ul>
<li><code>channels[0].target.node: 5</code> → <b>nodes[5]</b>（動かすノード）</li>
<li><code>channels[0].sampler: 0</code> → <b>animations[0].samplers[0]</b>（※ このアニメーションの中の配列）
<ul>
<li><code>input: 10</code> → <b>accessors[10]</b>（時刻）</li>
<li><code>output: 11</code> → <b>accessors[11]</b>（値）</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>

**読み方のコツ**：<strong>どの行も、「フィールド名: 番号 → その番号の配列の要素」</strong>の形です。**`buffer` の行まで来たら、数値データ（バイナリ）の実体に着きます**。

| 参照を持つ側 | フィールド | 指す先 |
| --- | --- | --- |
| **scenes** | `nodes[]` | nodes |
| **nodes** | `children[]` / `mesh` / `skin` / `camera` | nodes / meshes / skins / cameras |
| **meshes**（primitives） | `attributes.*` / `indices` / `material` | accessors / accessors / materials |
| **accessors** | `bufferView` | bufferViews |
| **bufferViews** | `buffer` | buffers |
| **materials** | `*Texture.index` | textures |
| **textures** | `source` / `sampler` | images / samplers |
| **skins** | `joints[]` / `inverseBindMatrices` | nodes / accessors |
| **animations** | `channels[].target.node` / `samplers[].input・output` | nodes / accessors |
| **images**（`.glb` 内） | `bufferView` | bufferViews |

**参照を、持たない側**（**images（外部ファイル時）・samplers・buffers・cameras**）が、**行き止まり**です。

## 全体の地図

<svg class="fig flow" viewBox="0 0 765 280" role="img" aria-label="glTF の構造：矢印はすべて「番号（インデックス）」で参照する"><defs><marker id="fl27197" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">glTF の構造：矢印はすべて「番号（インデックス）」で参照する</text><line x1="107.0" y1="64.0" x2="165.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="136.0" y="58.0" text-anchor="middle" style="font-size:12px">nodes （番号）</text><line x1="247.0" y1="64.0" x2="314.5" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="280.8" y="58.0" text-anchor="middle" style="font-size:12px">mesh</text><line x1="206.0" y1="87.0" x2="206.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="206.0" y="100.0" text-anchor="middle" style="font-size:12px">skin</text><line x1="396.5" y1="64.0" x2="464.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="430.2" y="58.0" text-anchor="middle" style="font-size:12px">attributes / indices</text><line x1="355.5" y1="87.0" x2="355.5" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="355.5" y="100.0" text-anchor="middle" style="font-size:12px">material</text><line x1="565.0" y1="64.0" x2="623.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="594.0" y="58.0" text-anchor="middle" style="font-size:12px">bufferView</text><line x1="681.5" y1="87.0" x2="681.5" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="681.5" y="100.0" text-anchor="middle" style="font-size:12px">buffer</text><line x1="406.0" y1="148.0" x2="467.5" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="436.8" y="142.0" text-anchor="middle" style="font-size:12px">baseColorTexture .index</text><line x1="514.5" y1="171.0" x2="514.5" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="514.5" y="184.0" text-anchor="middle" style="font-size:12px">source</text><line x1="560.2" y1="171.0" x2="635.8" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27197)"/><text x="598.0" y="184.0" text-anchor="middle" style="font-size:12px">sampler</text><rect x="28.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">scenes</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="168.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes</text><circle cx="170.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="170.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="317.5" y="44.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="355.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">meshes</text><circle cx="319.5" cy="46.0" r="10" fill="#2ea043"/><text x="319.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="168.0" y="128.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="206.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">skins</text><circle cx="170.0" cy="130.0" r="10" fill="#2ea043"/><text x="170.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="467.0" y="44.0" width="95" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="514.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">accessors</text><circle cx="469.0" cy="46.0" r="10" fill="#e5a828"/><text x="469.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="308.0" y="128.0" width="95" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="355.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">materials</text><circle cx="310.0" cy="130.0" r="10" fill="#e5a828"/><text x="310.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="626.0" y="44.0" width="111" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="681.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bufferViews</text><circle cx="628.0" cy="46.0" r="10" fill="#e5484d"/><text x="628.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="641.5" y="128.0" width="80" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="681.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">buffers</text><circle cx="643.5" cy="130.0" r="10" fill="#e5484d"/><text x="643.5" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="470.5" y="128.0" width="88" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="514.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">textures</text><circle cx="472.5" cy="130.0" r="10" fill="#9664e6"/><text x="472.5" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="476.5" y="212.0" width="76" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="514.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">images</text><circle cx="478.5" cy="214.0" r="10" fill="#9664e6"/><text x="478.5" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="637.5" y="212.0" width="88" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="681.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">samplers</text><circle cx="639.5" cy="214.0" r="10" fill="#9664e6"/><text x="639.5" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text></svg>

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

<svg class="fig flow" viewBox="0 0 1052 196" role="img" aria-label="三角形の頂点の位置を探す：番号をたどって、バイナリのどこかを見つける"><defs><marker id="fl5299" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">三角形の頂点の位置を探す：番号をたどって、バイナリのどこかを見つける</text><line x1="126.0" y1="64.0" x2="195.5" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl5299)"/><line x1="381.5" y1="64.0" x2="516.5" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl5299)"/><line x1="671.5" y1="64.0" x2="818.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl5299)"/><line x1="911.0" y1="87.0" x2="911.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl5299)"/><text x="911.0" y="100.0" text-anchor="middle" style="font-size:12px">POSITION</text><line x1="795.0" y1="148.0" x2="737.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl5299)"/><line x1="451.0" y1="148.0" x2="393.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl5299)"/><rect x="28.0" y="44.0" width="95" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="75.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">scene = 0</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="198.5" y="44.0" width="180" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="288.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">scenes[0] .nodes=[0]</text><circle cx="200.5" cy="46.0" r="10" fill="#2ea043"/><text x="200.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="519.5" y="44.0" width="149" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="594.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes[0] .mesh=0</text><circle cx="521.5" cy="46.0" r="10" fill="#e5a828"/><text x="521.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="821.0" y="44.0" width="180" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="911.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">meshes[0] POSITION=1</text><circle cx="823.0" cy="46.0" r="10" fill="#e5484d"/><text x="823.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="798.0" y="128.0" width="226" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="911.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">accessors[1] .bufferView=1</text><circle cx="800.0" cy="130.0" r="10" fill="#9664e6"/><text x="800.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="454.0" y="128.0" width="280" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="594.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bufferViews[1] .buffer=0 offset=8</text><circle cx="456.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="456.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">6</text><rect x="187.0" y="128.0" width="203" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="288.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">buffers[0] triangle.bin</text><circle cx="189.0" cy="130.0" r="10" fill="#2ea043"/><text x="189.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">7</text></svg>

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

<svg class="fig flow" viewBox="0 0 655 280" role="img" aria-label="ノードは親子の木。子の位置は、親の位置を基準にした相対値"><defs><marker id="fl22118" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ノードは親子の木。子の位置は、親の位置を基準にした相対値</text><line x1="126.0" y1="148.0" x2="184.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl22118)"/><text x="155.0" y="142.0" text-anchor="middle" style="font-size:12px">nodes=[0]</text><line x1="338.5" y1="125.0" x2="452.5" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl22118)"/><text x="395.5" y="100.0" text-anchor="middle" style="font-size:12px">children</text><line x1="338.5" y1="171.0" x2="452.5" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl22118)"/><text x="395.5" y="184.0" text-anchor="middle" style="font-size:12px">children</text><rect x="28.0" y="128.0" width="95" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="75.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">scenes[0]</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="187.0" y="128.0" width="165" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="269.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes[0] Character</text><circle cx="189.0" cy="130.0" r="10" fill="#2ea043"/><text x="189.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="424.0" y="44.0" width="195" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="521.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes[1] Body (mesh 0)</text><circle cx="426.0" cy="46.0" r="10" fill="#e5a828"/><text x="426.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="416.0" y="212.0" width="211" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="521.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes[2] Weapon (mesh 1)</text><circle cx="418.0" cy="214.0" r="10" fill="#e5a828"/><text x="418.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

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

<svg class="fig flow" viewBox="0 0 632 280" role="img" aria-label="マテリアル → テクスチャ → 画像・サンプラー。ここも、すべて番号でつながる"><defs><marker id="fl91863" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">マテリアル → テクスチャ → 画像・サンプラー。ここも、すべて番号でつながる</text><line x1="149.0" y1="148.0" x2="207.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91863)"/><text x="178.0" y="142.0" text-anchor="middle" style="font-size:12px">baseColorTexture.index=0</text><line x1="324.0" y1="126.5" x2="431.8" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl91863)"/><text x="377.9" y="100.8" text-anchor="middle" style="font-size:12px">source=0</text><line x1="324.0" y1="169.5" x2="436.0" y2="210.5" stroke="currentColor" stroke-width="2" marker-end="url(#fl91863)"/><text x="380.0" y="184.0" text-anchor="middle" style="font-size:12px">sampler=0</text><rect x="28.0" y="128.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="87.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">materials[0]</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="210.0" y="128.0" width="111" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="265.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">textures[0]</text><circle cx="212.0" cy="130.0" r="10" fill="#2ea043"/><text x="212.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="385.0" y="44.0" width="219" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="494.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">images[0] skin albedo.png</text><circle cx="387.0" cy="46.0" r="10" fill="#e5a828"/><text x="387.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="439.0" y="212.0" width="111" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="494.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">samplers[0]</text><circle cx="441.0" cy="214.0" r="10" fill="#e5a828"/><text x="441.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

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

<svg class="fig flow" viewBox="0 0 634 112" role="img" aria-label="頂点の骨番号は、joints 配列の位置。その先が、ノードの番号"><defs><marker id="fl7390" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">頂点の骨番号は、joints 配列の位置。その先が、ノードの番号</text><line x1="149.0" y1="64.0" x2="207.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7390)"/><text x="178.0" y="58.0" text-anchor="middle" style="font-size:12px">joints の 2 番目</text><line x1="408.0" y1="64.0" x2="466.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7390)"/><text x="437.0" y="58.0" text-anchor="middle" style="font-size:12px">ノード番号</text><rect x="28.0" y="44.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="87.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">JOINTS 0 = 2</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="210.0" y="44.0" width="195" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="307.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">skins[0].joints[2] = 5</text><circle cx="212.0" cy="46.0" r="10" fill="#2ea043"/><text x="212.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="469.0" y="44.0" width="137" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="537.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes[5] （骨）</text><circle cx="471.0" cy="46.0" r="10" fill="#e5a828"/><text x="471.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

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

<svg class="fig flow" viewBox="0 0 868 305" role="img" aria-label="アニメーション：channel が、sampler と、動かすノードを指す"><defs><marker id="fl6720" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">アニメーション：channel が、sampler と、動かすノードを指す</text><line x1="157.0" y1="173.2" x2="215.0" y2="173.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl6720)"/><line x1="328.8" y1="150.2" x2="420.2" y2="112.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl6720)"/><text x="374.5" y="125.2" text-anchor="middle" style="font-size:12px">sampler=0</text><line x1="328.8" y1="196.2" x2="420.2" y2="234.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl6720)"/><text x="374.5" y="209.2" text-anchor="middle" style="font-size:12px">target.node=5</text><line x1="534.0" y1="83.4" x2="633.0" y2="73.7" stroke="currentColor" stroke-width="2" marker-end="url(#fl6720)"/><text x="583.5" y="72.5" text-anchor="middle" style="font-size:12px">input</text><line x1="534.0" y1="102.7" x2="631.1" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl6720)"/><text x="582.5" y="107.8" text-anchor="middle" style="font-size:12px">output</text><rect x="28.0" y="153.2" width="126" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="91.0" y="173.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">animations[0]</text><circle cx="30.0" cy="155.2" r="10" fill="#4c8bf5"/><text x="30.0" y="155.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="218.0" y="153.2" width="111" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="273.5" y="173.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">channels[0]</text><circle cx="220.0" cy="155.2" r="10" fill="#2ea043"/><text x="220.0" y="155.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="420.0" y="69.2" width="111" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="475.5" y="89.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">samplers[0]</text><circle cx="422.0" cy="71.2" r="10" fill="#e5a828"/><text x="422.0" y="71.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="393.0" y="237.2" width="165" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="475.5" y="257.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes[5] .rotation</text><circle cx="395.0" cy="239.2" r="10" fill="#e5a828"/><text x="395.0" y="239.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="636.0" y="44.0" width="190" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="731.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">accessors[10] （時刻）</text><circle cx="638.0" cy="46.0" r="10" fill="#e5484d"/><text x="638.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="622.0" y="128.0" width="218" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="731.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">accessors[11] （回転の値）</text><circle cx="624.0" cy="130.0" r="10" fill="#e5484d"/><text x="624.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

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
