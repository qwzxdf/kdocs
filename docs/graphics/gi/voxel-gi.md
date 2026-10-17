---
title: ボクセル GI
tags:
  - 描画
---

# ボクセル GI

**SSGI**は**画面に映っているもの**しか見えませんでした。**ボクセル GI**（Voxel Cone Tracing、**VXGI**）は、**シーン全体を 3D の格子（ボクセル）に変換**し、**そこに「形（遮蔽）」と「光（出射光）」を保存**します。**画素から、半球の方向に「円錐（コーン）」を飛ばし**、**ボクセルの上をミップ マップをたどりながら進む**ことで、**画面外・裏側も含めた間接光**を<strong>ノイズなし（または少なく）</strong>で得られます。**2011 年の Crassin らの手法**で、**当時、リアルタイム GI の大きな進歩**でした。

!!! tip "ポイント"
    - シーンを<strong>ボクセル化</strong>し、<strong>各ボクセルに「不透明度」と「出射光（放射輝度）」</strong>を保存。
    - <strong>ボクセルのミップ マップ</strong>を作る（粗い階層）。<strong>遠くほど粗いミップを読む</strong>。
    - <strong>コーン トレース</strong>：<strong>画素から円錐を飛ばし</strong>、<strong>円錐の広がりに合うミップ</strong>を<strong>前から後ろへ累積</strong>。
    - <strong>拡散</strong>は<strong>広い円錐を数本</strong>（5〜6 本）、<strong>鏡面</strong>は<strong>細い円錐 1 本</strong>。
    - <strong>画面外も反映</strong>。<strong>ノイズが少ない</strong>（円錐が空間をまとめて積分）。
    - 欠点：<strong>ボクセルの解像度が粗い</strong>（<strong>光漏れ</strong>）。<strong>メモリ・更新コスト</strong>が重い。

## 原理

### ① ボクセル化

**シーンのジオメトリ**を、**3D の格子**（例：256³）に**書き込みます**。**各ボクセル**に<strong>そこにある表面の「色（アルベド）」・「法線」・「不透明度」</strong>を**保存**します。

| 方式 | 内容 |
| --- | --- |
| **保守的ラスタライズ ＋ GS** | **三角形を最も面積の大きくなる軸**に**投影**し、**ピクセル シェーダーで 3D テクスチャに書く**（**保守的ラスタライズ**で**小さな三角形も漏れなく**） |
| **コンピュート** | **三角形ごとにボクセルへ書き込む** |
| **更新** | **静的な部分はキャッシュ**。**動く物だけ、毎フレーム更新** |

### ② 光の注入

**各ボクセルに**、**直接光**（光源から、**シャドウ マップ**を使って）を**当てて**、<strong>そのボクセルの「出射光」</strong>（**アルベド × 直接光**）を計算し、**3D テクスチャに保存**します。

| 項目 | 内容 |
| --- | --- |
| **保存する値** | <strong>放射輝度（RGB）</strong>と<strong>不透明度（A）</strong>。**方向性**も持たせる（<strong>6 方向のテクスチャ（異方性ボクセル）</strong>） |
| **異方性ボクセル** | **±X, ±Y, ±Z の 6 方向**ごとに、**その方向から見たときの値**を保存。**方向による違い**（**薄い壁の表と裏**）を**表せる** |

### ③ ミップ マップの生成

**3D テクスチャ**に**ミップ マップ**を作ります。<strong>上位のミップほど、粗く（広い範囲の平均）</strong>なります。**円錐が広がるにつれて**、**粗いミップ**を読むことで、**円錐の太さに合った**、**範囲の平均**を得ます。

**異方性ボクセル**では、**ミップを作る際、方向ごとの値をそれぞれ平均**します。

### ④ コーン トレース

**画素から**、**半球に数本の円錐**を**飛ばします**。**円錐は進むにつれて、広がり**ます。**各ステップで円錐の太さに対応するミップ**を**読み**、**前から後ろへ（アルファ ブレンドのように）累積**します。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="コーン トレース">
<text x="20" y="24" class="fig-title">円錐が広がるにつれて、粗いミップを読み、前から後ろへ累積する</text>
<circle cx="80" cy="140" r="6" fill="currentColor"/><text x="60" y="166" style="font-size:12px">画素</text>
<polygon points="80,140 700,60 700,220" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-dasharray="4 3"/>
<circle cx="140" cy="132" r="8" fill="none" stroke="currentColor"/><circle cx="220" cy="122" r="16" fill="none" stroke="currentColor"/><circle cx="350" cy="106" r="32" fill="none" stroke="currentColor"/><circle cx="550" cy="82" r="60" fill="none" stroke="currentColor"/>
<text x="110" y="210" style="font-size:12px">細かいミップ</text><text x="500" y="210" style="font-size:12px">粗いミップ</text>
<text x="40" y="250" style="font-size:12px">ステップごとに、円の大きさ（円錐の太さ）に合うミップ レベルを読む。不透明度が 1 に達したら終了</text>
</svg>

<div class="formula">color ← color + (1 − α) · c_i　、　α ← α + (1 − α) · a_i　（前から後ろへ）</div>

```hlsl
float4 ConeTrace(float3 origin, float3 dir, float aperture) {
  float4 acc = 0.0;
  float dist = kVoxelSize;
  [loop] for (int i = 0; i < kConeSteps && acc.a < 1.0; ++i) {
    float diameter = max(kVoxelSize, 2.0 * aperture * dist);
    float mip = log2(diameter / kVoxelSize);
    float3 uvw = WorldToVoxelUVW(origin + dir * dist);
    float4 s = voxel_tex.SampleLevel(linear_sampler, uvw, mip);
    acc += (1.0 - acc.a) * s;
    dist += diameter * 0.5;
  }
  return acc;
}
```

| 点 | 説明 |
| --- | --- |
| **`aperture`** | **円錐の開き**（`tan(半角)`）。**広いほど、ぼやけた結果** |
| **`diameter`** | **その距離での円錐の太さ**（`2 · aperture · dist`）。**ミップ選択**に使う |
| **`mip = log2(diameter / voxel_size)`** | **太さがボクセル何個分か**を**ミップ レベル**に**変換** |
| **前から後ろ** | **不透明度が 1 に達する**と、**以降は見えない**ので**打ち切る** |

### 拡散と鏡面

| 種類 | 円錐 |
| --- | --- |
| **拡散の間接光** | **半球に、5〜6 本の広い円錐**（**余弦重み付き**） |
| **鏡面の間接光** | **反射方向に細い円錐 1 本**（**粗さで開きを調整**） |
| **AO** | **短い距離の円錐の不透明度**から、**環境光遮蔽**も得られる |

## 利点と限界

| 利点 | 限界 |
| --- | --- |
| **画面外・裏側**も**反映**（**世界全体が対象**） | **ボクセルが粗い**（256³ で数 cm〜数十 cm の分解能） |
| **ノイズが少ない**（**円錐が積分済みの値を読む**） | **光漏れ**（**薄い壁**で**ボクセルが混ざる**） |
| **動く物・動くライトが反映される** | **メモリ**（3D テクスチャ ＋ ミップ ＋ 異方性） |
| <strong>鏡面（粗めの反射）</strong>も、**同じ構造**で得られる | **ボクセル化・注入・ミップ生成が毎フレームのコスト** |
| **AO も同時に得られる** | **カスケード**で**遠くを粗く**する工夫が必要（視点の周りのみ） |

### 光漏れ

**ボクセルが粗いと薄い壁の両側が同じボクセルに入り**、**壁を貫通して、光が漏れ**ます。

| 対策 | 内容 |
| --- | --- |
| **異方性ボクセル** | **方向ごとの値**を持ち、**表と裏を区別** |
| **ボクセルを細かく** | **解像度を上げる**（メモリ・コストが増える） |
| **壁の厚みを増やす** | **レベル デザインで薄い壁を避ける** |
| **オフセット** | **サンプル位置を法線方向にずらす** |

## カスケード（クリップマップ）

**シーン全体を細かいボクセルで覆う**ことは、**メモリが足りません**。**視点の周りに入れ子になった複数のボクセル グリッド**（**カスケード**）を置き、**近くは細かく、遠くは粗く**します（[カスケード シャドウ マップ](../shadows/cascaded.md)と同じ発想）。**カメラの移動に応じて、グリッドをスクロール**させます。

## 現在の位置づけ

**Crassin の VXGI** は、**NVIDIA の VXGI**として製品化されましたが、**メモリ・コスト・光漏れ**の問題から、**現在の主流ではありません**。

| 後継・類似 | 内容 |
| --- | --- |
| <strong>Lumen（Unreal Engine 5）</strong> | **Software Ray Tracing では、距離場（SDF）・サーフェス キャッシュ**。**画面空間 → 距離場 → グローバル SDF** の**階層** |
| <strong>SDFGI（Godot）</strong> | **カスケードの SDF** ＋ **プローブ** |
| **Radiance Cascades** | **新しい、空間・方向の階層構造**（[レイトレ GI](rt-gi/index.md)） |

<strong>「ボクセル（またはそれに類する 3D 格子）に光を保存し、円錐/レイでたどる」</strong>という**考え方**は、**多くの動的 GI に受け継がれています**。

## よくあるミス

??? failure "ボクセル化で小さい三角形が、漏れて、穴が空く"
    **保守的ラスタライズ**を使います。

??? failure "円錐のミップ選択が合わず、ぼやけすぎ・ブロック状になる"
    **`mip = log2(diameter / voxel_size)`** で、**太さに合わせて**選びます。

??? failure "薄い壁の向こうの光が、漏れる"
    **異方性ボクセル**・**壁を厚く**・**サンプル位置のオフセット**。

??? failure "メモリを使いすぎる"
    **カスケード**で**遠くを粗く**・**ボクセルの解像度を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボクセル GI ＝ <strong>シーンを 3D 格子に変換</strong>し、<strong>不透明度と出射光を保存</strong>、<strong>ミップ マップ</strong>を作る
    - [x] <strong>コーン トレース</strong>：<strong>円錐の太さに合うミップ</strong>を、<strong>前から後ろへ累積</strong>
    - [x] <strong>拡散は広い円錐を数本</strong>、<strong>鏡面は細い円錐 1 本</strong>
    - [x] <strong>画面外も反映・ノイズ少ない</strong>が<strong>解像度が粗い・光漏れ・メモリが重い</strong>
    - [x] <strong>現在は Lumen・SDFGI などの派生</strong>に、<strong>考え方が受け継がれている</strong>

## 参考

- Crassin et al., "Interactive Indirect Illumination Using Voxel Cone Tracing"（Pacific Graphics 2011）
- Crassin, "GigaVoxels"（博士論文、2011）
- Godot, "SDFGI"（ドキュメント）

## 関連ページ

- [間接光（GI）](index.md)
- [GI の理論](theory/index.md)
- [SSGI](ssgi.md)
- [レイトレ GI](rt-gi/index.md)
- [カスケード シャドウ マップ](../shadows/cascaded.md)
