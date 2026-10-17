---
title: 描画の最適化（詳細）
tags:
  - 最適化
  - 3Dゲーム
---

# 描画の最適化（詳細）

[描画の最適化](../rendering.md)は、**入口**（CPU と GPU のどちらが遅いか・ドロー コールの減らし方）でした。このカテゴリは、<strong>現代のゲームの描画が、「何が重くて」「どう直してきたか」</strong>を、**段階を追って**、**言葉で**説明します。<strong>「ライティングを、Forward から Deferred に」「ライトを、タイルで分ける（Tiled）」「3 次元に分ける（Clustered）」「カリングを、GPU に任せる（GPU Driven）」「三角形の塊（Meshlet）で、細かくカリング」「ビジビリティ バッファ」</strong>など、**名前だけは聞くが、何が嬉しいのか分からない**手法を、<strong>目的（何を、減らしたいのか）</strong>から、理解することが狙いです。**コードは、要点だけ**で、**考え方**が中心です。

!!! tip "ポイント"
    - 描画の最適化は、<strong>「何が足りないのか」を、先に決める</strong>：<strong>CPU の時間・GPU の計算・メモリ帯域・ピクセル数（塗る面積）</strong>。
    - 手法は<strong>「無駄な仕事を、減らす」か「仕事の単位を、変えて、まとめる」</strong>のどちらか。
    - ライティングの流れ：<strong>Forward → Deferred → Tiled → Clustered</strong>。<strong>「物体 × ピクセル × ライト」を、「ピクセル × ライト」に、さらに「ピクセル × 近くのライトだけ」に</strong>減らしていく。
    - ジオメトリの流れ：<strong>ドロー コールを減らす → カリング → GPU Driven → Meshlet（Mesh Shader）</strong>。<strong>「CPU が 1 つずつ判断」から「GPU が、まとめて判断」へ</strong>。
    - <strong>メモリ帯域</strong>は、近年の<strong>最大の敵</strong>。<strong>計算（ALU）は、安く、メモリアクセスが、高い</strong>。
    - <strong>まず測る</strong>。<strong>ボトルネックでない所を、最適化しても、速くならない</strong>。

## ページ一覧

**読む順番**：何が重いか → ライティング → ジオメトリ → ピクセル・解像度 → 周辺の最適化。

| ページ | 内容 |
| --- | --- |
| [何が重いのか（ボトルネック）](bottlenecks.md) | CPU と GPU、頂点・ピクセル・帯域。**どう見分けるか** |
| [メモリ帯域幅](bandwidth.md) | 帯域とは何か、G-Buffer が重い理由、フォーマットの選び方 |
| [Forward と Deferred](forward-deferred.md) | ライティングの基本の 2 方式。**何が、改善するのか** |
| [Tiled と Clustered](light-culling.md) | ライトを、タイル・3 次元のセルに分ける。**Tiled / Clustered の Deferred と Forward** |
| [ドロー コールとバッチ](draw-calls.md) | CPU 側の負担、バッチ・インスタンシング・ステートの整理 |
| [カリング](culling.md) | 視錐台・オクルージョン・距離・LOD。**見えないものを、描かない** |
| [GPU Driven Rendering](gpu-driven.md) | カリングと描画命令を、**GPU が作る**。1 回の描画に |
| [Mesh Shader と Meshlet](mesh-shaders.md) | **三角形の塊**単位の、細かいカリング |
| [Visibility Buffer](visibility-buffer.md) | G-Buffer を、**三角形の ID だけ**に |
| [オーバードローと Z プリパス](overdraw.md) | 無駄に塗る問題・Early-Z・小さな三角形の問題 |
| [低解像度のエフェクト](low-res-effects.md) | AO・ブルーム・霧などを、縮小バッファで。アップサンプル |
| [Hi-Z とスクリーン空間トレース](hiz.md) | 階層的な深度。反射・AO・オクルージョンの高速化 |
| [シェーダーのコスト](shader-cost.md) | 計算 vs メモリ・分岐・占有率・精度 |
| [そのほかの最適化](others.md) | 影・LOD・テクスチャ・VRS・動的解像度・TAA・非同期コンピュート |

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
| **CPU：ドロー コールが多い** | **1 回の命令ごとに、ドライバが、時間を使う** | バッチ・インスタンシング・状態の整理 | [ドロー コール](draw-calls.md) |
| **CPU：判断が多い**（何を描くか） | **物体 1 つずつ、見えるか判断** | **GPU Driven**・階層カリング | [カリング](culling.md)・[GPU Driven](gpu-driven.md) |
| **GPU：見えない物の頂点処理** | **画面外・隠れた物も、頂点を計算** | カリング・**Meshlet** | [Mesh Shader](mesh-shaders.md) |
| **GPU：ピクセルの計算が多い**（ライト） | **ピクセル × ライトの数** | **Deferred・Tiled・Clustered** | [Forward と Deferred](forward-deferred.md)・[Tiled と Clustered](light-culling.md) |
| **GPU：同じピクセルを、何度も塗る** | **オーバードロー** | **Z プリパス・Visibility Buffer** | [オーバードロー](overdraw.md)・[Visibility Buffer](visibility-buffer.md) |
| **GPU：帯域が足りない** | **G-Buffer・RT の読み書き** | **フォーマット・圧縮・Visibility Buffer** | [帯域](bandwidth.md) |
| **GPU：高解像度の重い効果**（AO・反射） | **全ピクセルで、重い計算** | **低解像度・Hi-Z・時間方向の再利用** | [低解像度](low-res-effects.md)・[Hi-Z](hiz.md) |
| **GPU：シェーダーが重い** | **ALU・テクスチャ読み込み・分岐** | **簡略化・FP16・バリアント** | [シェーダーのコスト](shader-cost.md) |

## 関連ページ

- [描画の最適化（入口）](../rendering.md)
- [計測（プロファイリング）](../measure.md)
- [フレーム時間の設計](../frame-budget.md)
- [PBR（物理ベースレンダリング）](../../3d/pbr.md)
- [深度とカリング](../../3d/depth-culling.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
