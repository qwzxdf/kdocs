---
title: Mesh Shader と Meshlet
tags:
  - 最適化
  - 3Dゲーム
---

# Mesh Shader と Meshlet

[GPU Driven](gpu-driven.md)で、**カリングを GPU に任せ**てもカリングの単位が「物体」「サブメッシュ」だと大きな物体の一部だけが見えているとき、見えない部分の頂点も全部処理してしまいます。メッシュを小さな「塊」（Meshlet）にあらかじめ分割しておけば、塊ごとにカリングできます。Mesh Shaderは、この塊をそのまま処理する、新しいシェーダー段です。このページは、Meshlet とは何か、何が改善するのか、従来のパイプラインとの違い、使える環境（DX12 Ultimate）と、DX11 での代替を説明します。

!!! tip "ポイント"
    - <strong>Meshlet</strong> ＝ <strong>メッシュを約 64 頂点・約 124 三角形の小さな塊に分割したもの</strong>（ビルド時に作る）。
    - 目的：カリングの単位を細かくする。見えない塊は頂点処理をまるごと省く。
    - Meshlet ごとの、カリング情報：境界球・法線の円錐（Normal Cone）。円錐で裏向きの塊をまとめて除外。
    - Mesh Shader パイプライン：Task（Amplification）Shader（塊ごとのカリング）→ Mesh Shader（頂点・三角形の出力）→ ピクセルシェーダー。従来の頂点シェーダー・ジオメトリ シェーダー・入力アセンブラを置き換える。
    - DX12 Ultimate（Mesh Shader 対応）の機能。DX11 では、使えない。DX11 でも、Meshlet 単位の、コンピュート カリングは、できる。
    - 応用：連続 LOD（Nanite 風）・マイクロポリゴン。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 従来の頂点処理の限界

**従来**は入力アセンブラが頂点バッファ・インデックスバッファを順に読み、頂点シェーダーを 1 頂点ずつ実行し、三角形に組み立てて、ラスタライザへという固定の流れです。

| 限界 | 説明 |
| --- | --- |
| カリングの粒度が粗い | 物体・サブメッシュ単位。一部が見える大きな物体は、全体の頂点を処理 |
| 三角形ごとのカリングが遅い | 頂点シェーダーの後でないと、三角形が見えないと分からない（頂点処理はすでに無駄） |
| 固定の入力形式 | 頂点バッファ ＋ インデックスの形式に縛られる（圧縮・自由な形式が使いにくい） |
| ジオメトリ シェーダーが遅い | 新しい三角形を作る処理は、効率が悪い |
| データの再利用 | 同じ頂点を複数の三角形が共有するがキャッシュ頼り |

## Meshlet（小さな塊）

**Meshlet** は、メッシュを頂点数・三角形数の上限付きで小さく分割した塊です。

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="メッシュを、Meshlet に分割">
<text x="20" y="24" class="fig-title">1 つのメッシュを小さな塊（Meshlet）に分割。塊ごとに、見えるか判定する</text>
<g stroke="currentColor" stroke-width="2">
<polygon points="60,200 130,110 200,200" fill="rgba(76,139,245,0.35)"/>
<polygon points="130,110 200,200 270,110" fill="rgba(46,160,67,0.35)"/>
<polygon points="200,200 270,110 340,200" fill="rgba(229,170,40,0.4)"/>
<polygon points="270,110 340,200 400,100" fill="rgba(229,72,77,0.3)"/>
<polygon points="130,110 200,60 270,110" fill="rgba(150,100,230,0.35)"/>
<polygon points="270,110 330,60 400,100" fill="rgba(76,139,245,0.25)"/>
</g>
<text x="60" y="226" style="font-size:12px">それぞれの色が 1 つの Meshlet</text>
<text x="450" y="60" style="font-weight:700">1 つの Meshlet が、持つもの</text>
<text x="450" y="84" style="font-size:12px">・頂点：最大 64 個（目安）</text>
<text x="450" y="104" style="font-size:12px">・三角形：最大 124 個（目安）</text>
<text x="450" y="124" style="font-size:12px">・境界球（見えるか判定）</text>
<text x="450" y="144" style="font-size:12px">・法線の円錐（裏向きか判定）</text>
<text x="450" y="180" style="font-weight:700">ビルド時に作る（ベイク）</text>
<text x="450" y="204" style="font-size:12px">meshoptimizer などの、ライブラリで分割</text>
<text x="450" y="224" style="font-size:12px">→ 実行時は、塊の配列を読むだけ</text>
</svg>

| 項目 | 説明 |
| --- | --- |
| サイズの目安 | 最大 64 頂点・126 三角形（NVIDIA の推奨）。GPU のスレッド グループに収まる大きさ |
| 作る方法 | ビルド時に meshoptimizer（`meshopt_buildMeshlets`）などでメッシュを近い三角形でまとめる |
| Meshlet に持たせる情報 | 頂点インデックス（Meshlet 内の局所番号）・三角形のインデックス・境界球・法線の円錐 |
| 局所インデックス | Meshlet 内の頂点は、小さな番号（8 ビット）で、参照（メモリ節約） |

### Meshlet カリング

| 判定 | 説明 |
| --- | --- |
| 視錐台 | 境界球が視錐台の外なら、除外 |
| オクルージョン（Hi-Z） | 境界球が隠れていれば、除外（[Hi-Z](hiz.md)） |
| 法線の円錐（Normal Cone） | Meshlet の全三角形がカメラと反対向き（裏向き）なら、まとめて除外（バックフェイス カリングの、Meshlet 版） |
| 距離・小さな塊 | 遠すぎる・小さすぎる塊を除外 |

三角形を 1 つずつ見る前に塊ごと（数十〜百の三角形）を一度に除外できます。頂点処理・三角形の組み立てがまるごと省けます。

## Mesh Shader パイプライン

**Mesh Shader** は、従来の「入力アセンブラ → 頂点シェーダー → （ジオメトリ シェーダー）」を置き換える、新しいパイプラインです。

<svg class="fig flow" viewBox="0 0 584 238" role="img" aria-label="従来のパイプラインと、Mesh Shader パイプライン"><defs><marker id="fl7108" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">従来のパイプラインと、Mesh Shader パイプライン</text><line x1="197.0" y1="64.0" x2="255.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7108)"/><line x1="385.0" y1="64.0" x2="443.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7108)"/><line x1="169.5" y1="190.0" x2="261.5" y2="190.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7108)"/><line x1="378.5" y1="190.0" x2="443.0" y2="190.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7108)"/><rect x="28.0" y="44.0" width="166" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="111.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">従来：入力アセンブラ</text><rect x="258.0" y="44.0" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="320.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">頂点シェーダー</text><rect x="446.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="501.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ラスタライザ</text><rect x="55.5" y="170.0" width="111" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="111.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Task Shader</text><rect x="264.5" y="170.0" width="111" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="320.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Mesh Shader</text><rect x="446.0" y="170.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="501.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ラスタライザ</text></svg>

| 段 | 役割 |
| --- | --- |
| Task Shader（Amplification Shader） | Meshlet ごとの、カリング。見える Meshlet だけ、Mesh Shader を起動（起動する数を動的に決める） |
| Mesh Shader | 1 つの Meshlet をスレッド グループで処理。頂点の位置・三角形を自分で出力（メモリから、自由に読める） |
| ラスタライザ・ピクセルシェーダー | 従来と同じ |

```hlsl
[outputtopology("triangle")]
[numthreads(128, 1, 1)]
void MeshMain(uint gtid : SV_GroupThreadID, uint gid : SV_GroupID,
              out vertices VertexOut verts[64], out indices uint3 tris[124]) {
  Meshlet m = meshlets[gid];
  SetMeshOutputCounts(m.vertex_count, m.triangle_count);
  if (gtid < m.vertex_count) verts[gtid] = TransformVertex(m, gtid);
  if (gtid < m.triangle_count) tris[gtid] = LoadTriangle(m, gtid);
}
```

| 点 | 説明 |
| --- | --- |
| `SetMeshOutputCounts` | この Meshlet が、出す頂点数・三角形数 |
| 出力配列 | 頂点と三角形（インデックス）を直接、書く |
| スレッドが協調して処理 | スレッド グループ全体で、1 つの Meshlet |

### 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| カリングが細かい | Meshlet 単位で、頂点処理の前に除外。頂点・三角形の処理が大幅に減る |
| メモリの自由度 | 頂点データを自由な形式（圧縮・量子化）で、持てる |
| 入力アセンブラのボトルネックを回避 | 頂点バッファ → 頂点シェーダー の、固定の流れから、解放 |
| GPU Driven と、自然に統合 | Task Shader が、カリングをパイプライン内で |
| 動的な、ジオメトリ生成 | テッセレーション・LOD の柔軟な制御 |

## 使える環境

| 環境 | 対応 |
| --- | --- |
| **DirectX 12 Ultimate**（Feature Level 12_2） | Mesh Shader（Shader Model 6.5 以降） |
| Vulkan | `VK_EXT_mesh_shader`（NVIDIA・AMD・Intel の新しい GPU） |
| DirectX 11 | 使えない |
| GPU | NVIDIA（Turing 以降）・AMD（RDNA2 以降）・Intel（Arc） |

!!! warning "DX11 では、Mesh Shader は使えない"
    このサイトの描画の例は、DX11ですが、Mesh Shader は、DX12 Ultimate / Vulkan の機能です。DX11 でも、Meshlet の考え方は活かせます（下記）。

### DX11 での、代わりの方法

| 方法 | 説明 |
| --- | --- |
| Meshlet 単位の、コンピュート カリング | コンピュート シェーダーで、Meshlet を判定し、生き残った Meshlet の三角形をインデックス バッファに書き出す（フィルタリング）。`DrawIndexedInstancedIndirect` で、描く |
| クラスター単位のインダイレクト | Meshlet を描画単位にして、インダイレクト引数で描く |
| 三角形フィルタリング | コンピュートで見えない三角形を除外し、インデックスバッファを詰め直す（頂点処理の前） |

効果は、Mesh Shader ほどではないですが、「頂点処理の前に塊ごとに除外」という、考え方は使えます。

## 連続 LOD とマイクロポリゴン（Nanite 風）

**Meshlet は、「細かい詳細度の制御」の、土台**にもなります。

| 概念 | 説明 |
| --- | --- |
| クラスター階層（連続 LOD） | Meshlet を階層（木）にし、画面上の大きさに応じて、適切な詳細度の Meshlet だけを選ぶ。ポップのない、滑らかな LOD |
| マイクロポリゴン | 三角形が 1 ピクセル以下になる。ハードウェアのラスタライザは、小さな三角形が苦手（[オーバードロー](overdraw.md)）。ソフトウェアのラスタライズ（コンピュート）を併用 |
| Visibility Buffer | 三角形の ID だけを書き、後で材質を計算（[Visibility Buffer](visibility-buffer.md)） |

Unreal Engine 5 の Naniteは、これらの組み合わせ（クラスター階層・GPU Driven・ソフトウェア ラスタライズ・Visibility Buffer）です。数十億の三角形を画面のピクセル数に見合う量だけ描きます。

## 導入の判断

| 状況 | 方針 |
| --- | --- |
| **三角形が少ない（数十万）・DX11** | Meshlet は、不要。普通のカリング・LOD |
| 三角形が多い・高密度のメッシュ | Meshlet ＋ GPU Driven（DX12 / Vulkan） |
| 連続 LOD が欲しい | クラスター階層（ビルド時の処理が大変） |

Meshlet のメリットは、「高密度のメッシュ」で、大きく出ます。普通のゲームの中程度のモデルでは、従来のパイプラインで十分なことが多いです。

## よくあるミス

??? failure "Mesh Shader を DX11 で使おうとする"
    **DX12 Ultimate / Vulkan** が必要です。

??? failure "三角形が少ないのに、Meshlet 化して、遅くなる"
    Meshlet のオーバーヘッドが利点を上回ります。

??? failure "Meshlet の大きさを GPU に合わせずに効率が落ちる"
    ベンダーの推奨（64 頂点・124〜126 三角形）に合わせます。

??? failure "法線の円錐が不正確で見えるはずの物が消える"
    保守的な判定にします（少し、多めに残す）。

??? failure "Meshlet を実行時に毎回、作る"
    ビルド時に作ります（[ベイク](../optimize/baking.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>Meshlet ＝ 約 64 頂点・124 三角形の小さな塊</strong>。ビルド時に分割
    - [x] 目的：カリングの単位を細かく。塊ごとに頂点処理の前に除外（境界球・法線の円錐・Hi-Z）
    - [x] Mesh Shader ＝ Task Shader（カリング）→ Mesh Shader（頂点・三角形の出力）。従来の頂点処理を置き換える
    - [x] DX12 Ultimate / Vulkan の機能。DX11 では、使えない（コンピュートで近いことができる）
    - [x] 応用：連続 LOD・マイクロポリゴン・Visibility Buffer（Nanite 風）

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [カリング](culling.md)
- [GPU Driven Rendering](gpu-driven.md)
- [Visibility Buffer](visibility-buffer.md)
- [Hi-Z とスクリーン空間トレース](hiz.md)
