---
title: 描画最適化
tags:
  - 最適化
  - 3Dゲーム
---

# 描画最適化

このセクションは、<strong>現代のゲームの描画が、「何が重くて」「どう直してきたか」</strong>を、**段階を追って**、**言葉で**説明します。<strong>「ライティングを、Forward から Deferred に」「ライトをタイルで分ける（Tiled）」「3 次元に分ける（Clustered）」「カリングを、GPU に任せる（GPU Driven）」「三角形の塊（Meshlet）で、細かくカリング」「ビジビリティ バッファ」</strong>など、**名前だけは聞くが何が嬉しいのか分からない**手法を、<strong>目的（何を減らしたいのか）</strong>から、理解することが狙いです。**コードは要点だけ**で**考え方**が中心です。

## ページ一覧

**読む順番**：しくみと測り方 → ライティング → ジオメトリ → ピクセル・解像度 → 周辺の最適化 → 実践。

**減らせるもの**の列は、その手法が主に何を減らすかを表します。ピクセルや頂点は「減らす量」、計算（ALU）や帯域幅は「楽になる資源」です。

<div class="gain-legend"><span class="gain gain-cpu">🖥️ CPU の命令減</span> <span class="gain gain-vtx">🔺 頂点量減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> <span class="gain gain-bw">📶 帯域幅減</span> <span class="gain gain-alu">🧮 計算（ALU）減</span> <span class="gain gain-vram">💾 VRAM 減</span> <span class="gain gain-gpu">⏱️ GPU の空き活用</span></div>

| ページ | 内容 | 減らせるもの |
| --- | --- | --- |
| [描画のしくみ](pipeline.md) | CPU から画面までの流れと、基本用語 | — |
| [何が重いのか（ボトルネック）](bottlenecks.md) | CPU と GPU、頂点・ピクセル・帯域。**どう見分けるか** | — |
| [メモリ帯域幅](bandwidth.md) | 帯域とは何か、G-Buffer が重い理由、フォーマットの選び方 | <span class="gain gain-bw">📶 帯域幅減</span> <span class="gain gain-vram">💾 VRAM 減</span> |
| [Forward と Deferred](forward-deferred.md) | ライティングの基本の 2 方式。**何が改善するのか** | <span class="gain gain-alu">🧮 計算（ALU）減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [Tiled と Clustered](light-culling.md) | ライトをタイル・3 次元のセルに分ける | <span class="gain gain-alu">🧮 計算（ALU）減</span> <span class="gain gain-bw">📶 帯域幅減</span> |
| [ドロー コールとバッチ](draw-calls.md) | CPU 側の負担、バッチ・インスタンシング・ステートの整理 | <span class="gain gain-cpu">🖥️ CPU の命令減</span> |
| [カリング](culling.md) | 視錐台・オクルージョン・距離。**見えないものを描かない** | <span class="gain gain-cpu">🖥️ CPU の命令減</span> <span class="gain gain-vtx">🔺 頂点量減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [GPU Driven Rendering](gpu-driven.md) | カリングと描画命令を、**GPU が作る** | <span class="gain gain-cpu">🖥️ CPU の命令減</span> |
| [Mesh Shader と Meshlet](mesh-shaders.md) | **三角形の塊**単位の細かいカリング | <span class="gain gain-vtx">🔺 頂点量減</span> <span class="gain gain-bw">📶 帯域幅減</span> |
| [Visibility Buffer](visibility-buffer.md) | G-Buffer を**三角形の ID だけ**に | <span class="gain gain-bw">📶 帯域幅減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [オーバードローと Z プリパス](overdraw.md) | 無駄に塗る問題・Early-Z・小さな三角形 | <span class="gain gain-pix">🎨 ピクセル量減</span> <span class="gain gain-alu">🧮 計算（ALU）減</span> |
| [低解像度のエフェクト](low-res-effects.md) | AO・ブルーム・霧などを縮小バッファで | <span class="gain gain-pix">🎨 ピクセル量減</span> <span class="gain gain-bw">📶 帯域幅減</span> <span class="gain gain-alu">🧮 計算（ALU）減</span> |
| [Hi-Z とスクリーン空間トレース](hiz.md) | 階層的な深度。反射・AO・オクルージョンの高速化 | <span class="gain gain-cpu">🖥️ CPU の命令減</span> <span class="gain gain-alu">🧮 計算（ALU）減</span> |
| [シェーダーのコスト](shader-cost.md) | 計算 vs メモリ・分岐・占有率・精度 | <span class="gain gain-alu">🧮 計算（ALU）減</span> <span class="gain gain-bw">📶 帯域幅減</span> |
| [LOD とインポスター](lod.md) | 遠くの物の詳細度を下げる | <span class="gain gain-vtx">🔺 頂点量減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [影のコスト](shadows.md) | カスケード・影用カリング・更新頻度 | <span class="gain gain-cpu">🖥️ CPU の命令減</span> <span class="gain gain-vtx">🔺 頂点量減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [テクスチャとストリーミング](texture-streaming.md) | 圧縮・ミップ・必要な分だけ常駐 | <span class="gain gain-vram">💾 VRAM 減</span> <span class="gain gain-bw">📶 帯域幅減</span> |
| [TAA・アップスケーラ・VRS](taa-upscaling.md) | 低解像度で描いて、時間情報で補う | <span class="gain gain-pix">🎨 ピクセル量減</span> <span class="gain gain-alu">🧮 計算（ALU）減</span> |
| [非同期コンピュート](async-compute.md) | 描画とコンピュートを同時に走らせる | <span class="gain gain-gpu">⏱️ GPU の空き活用</span> |
| [パーティクルと半透明](particles.md) | 重なりのコストを減らす | <span class="gain gain-pix">🎨 ピクセル量減</span> <span class="gain gain-bw">📶 帯域幅減</span> |
| [ポストプロセス](postprocess.md) | 全画面の効果をまとめて軽く | <span class="gain gain-bw">📶 帯域幅減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [2D ゲームの描画](2d.md) | スプライト・タイルマップ・UI | <span class="gain gain-cpu">🖥️ CPU の命令減</span> <span class="gain gain-pix">🎨 ピクセル量減</span> |
| [調査ツール](tools.md) | RenderDoc・PIX・Nsight の使いどころ | — |
| [場面別の直し方](cases.md) | よくある症状と効く手法の対応 | — |

## 描画の全体像（どこが重くなるか）

<svg class="fig illust" viewBox="0 0 820 300" role="img" aria-label="描画の流れと、各段階で重くなるもの">
<defs><marker id="gx1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">描画の 1 フレーム：CPU が命令を作り、GPU が頂点 → ピクセルの順に処理する</text>
<rect x="20" y="60" width="150" height="90" rx="12" fill="rgba(76,139,245,0.2)" stroke="currentColor" stroke-width="3"/>
<text x="95" y="92" text-anchor="middle" style="font-weight:700">CPU</text><text x="95" y="114" text-anchor="middle" style="font-size:12px">ゲームの更新</text><text x="95" y="134" text-anchor="middle" style="font-size:12px">描画命令を作る</text>
<line x1="178" y1="105" x2="238" y2="105" stroke="currentColor" stroke-width="3" marker-end="url(#gx1)"/><text x="208" y="94" text-anchor="middle" style="font-size:12px">命令</text>
<rect x="246" y="60" width="130" height="90" rx="12" fill="rgba(46,160,67,0.2)" stroke="currentColor" stroke-width="3"/>
<text x="311" y="92" text-anchor="middle" style="font-weight:700">頂点処理</text><text x="311" y="114" text-anchor="middle" style="font-size:12px">三角形の位置を</text><text x="311" y="134" text-anchor="middle" style="font-size:12px">計算</text>
<line x1="384" y1="105" x2="444" y2="105" stroke="currentColor" stroke-width="3" marker-end="url(#gx1)"/>
<rect x="452" y="60" width="130" height="90" rx="12" fill="rgba(229,170,40,0.22)" stroke="currentColor" stroke-width="3"/>
<text x="517" y="92" text-anchor="middle" style="font-weight:700">ラスタライズ</text><text x="517" y="114" text-anchor="middle" style="font-size:12px">三角形を</text><text x="517" y="134" text-anchor="middle" style="font-size:12px">ピクセルに分解</text>
<line x1="590" y1="105" x2="650" y2="105" stroke="currentColor" stroke-width="3" marker-end="url(#gx1)"/>
<rect x="658" y="60" width="142" height="90" rx="12" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/>
<text x="729" y="92" text-anchor="middle" style="font-weight:700">ピクセル処理</text><text x="729" y="114" text-anchor="middle" style="font-size:12px">色を計算</text><text x="729" y="134" text-anchor="middle" style="font-size:12px">（ライティング）</text>
<text x="95" y="186" text-anchor="middle" style="font-size:12px;fill:#e5484d;font-weight:700">命令が多い</text><text x="95" y="204" text-anchor="middle" style="font-size:12px">ドロー コール・状態変更</text>
<text x="311" y="186" text-anchor="middle" style="font-size:12px;fill:#e5484d;font-weight:700">頂点が多い</text><text x="311" y="204" text-anchor="middle" style="font-size:12px">高ポリゴン・見えない物</text>
<text x="517" y="186" text-anchor="middle" style="font-size:12px;fill:#e5484d;font-weight:700">小さな三角形</text><text x="517" y="204" text-anchor="middle" style="font-size:12px">効率が落ちる</text>
<text x="729" y="186" text-anchor="middle" style="font-size:12px;fill:#e5484d;font-weight:700">ピクセル × 計算</text><text x="729" y="204" text-anchor="middle" style="font-size:12px">ライト・オーバードロー</text>
<rect x="20" y="236" width="780" height="40" rx="8" fill="rgba(150,150,150,0.15)" stroke="currentColor" stroke-dasharray="5 4"/>
<text x="410" y="261" text-anchor="middle" style="font-weight:700">メモリ帯域：頂点・テクスチャ・G-Buffer・レンダーターゲットの読み書きが、全段階で、帯域を使う</text>
</svg>

## 手法の地図

| 重いもの | 起きていること | 主な手法 | ページ |
| --- | --- | --- | --- |
| **CPU：ドロー コールが多い** | **1 回の命令ごとにドライバが時間を使う** | バッチ・インスタンシング・状態の整理 | [ドロー コール](draw-calls.md) |
| **CPU：判断が多い**（何を描くか） | **物体 1 つずつ、見えるか判断** | **GPU Driven**・階層カリング | [カリング](culling.md)・[GPU Driven](gpu-driven.md) |
| **GPU：見えない物の頂点処理** | **画面外・隠れた物も頂点を計算** | カリング・**Meshlet** | [Mesh Shader](mesh-shaders.md) |
| **GPU：ピクセルの計算が多い**（ライト） | **ピクセル × ライトの数** | **Deferred・Tiled・Clustered** | [Forward と Deferred](forward-deferred.md)・[Tiled と Clustered](light-culling.md) |
| **GPU：同じピクセルを何度も塗る** | **オーバードロー** | **Z プリパス・Visibility Buffer** | [オーバードロー](overdraw.md)・[Visibility Buffer](visibility-buffer.md) |
| **GPU：帯域が足りない** | **G-Buffer・RT の読み書き** | **フォーマット・圧縮・Visibility Buffer** | [帯域](bandwidth.md) |
| **GPU：高解像度の重い効果**（AO・反射） | **全ピクセルで重い計算** | **低解像度・Hi-Z・時間方向の再利用** | [低解像度](low-res-effects.md)・[Hi-Z](hiz.md) |
| **GPU：シェーダーが重い** | **ALU・テクスチャ読み込み・分岐** | **簡略化・FP16・バリアント** | [シェーダーのコスト](shader-cost.md) |

## 関連ページ

- [計測（プロファイリング）](../optimize/measure.md)
- [フレーム時間の設計](../optimize/frame-budget.md)
- [PBR（物理ベースレンダリング）](../3d/pbr.md)
- [深度とカリング](../3d/depth-culling.md)
- [メッシュとテクスチャ](../3d/mesh-textures.md)
