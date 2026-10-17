---
title: カリング
tags:
  - 最適化
  - 3Dゲーム
---

# カリング

**カリング**は**見えないものを描かない**ことです。**最も効果が大きく、基本の最適化**で**ドロー コール・頂点処理・ピクセル処理**のすべてを、**減らせます**。このページは**カリングの種類**（視錐台・オクルージョン・距離・LOD）、**それぞれが何を減らすのか**、**CPU でやる場合の課題**、<strong>段階的な発展（GPU Driven・Meshlet へ）</strong>を、説明します。基本は [深度とカリング](../3d/depth-culling.md) にあります。

!!! tip "ポイント"
    - <strong>カリングの目的</strong>：<strong>描画命令・頂点・ピクセルの無駄をなくす</strong>。<strong>早い段階で除外するほど、効果が大きい</strong>。
    - <strong>視錐台カリング</strong>：<strong>カメラの視界の外</strong>を除外。<strong>最も基本</strong>。
    - <strong>オクルージョン カリング</strong>：<strong>ほかの物に隠れた物</strong>を除外。<strong>効果が大きいが実装が難しい</strong>。
    - <strong>距離・小物カリング、LOD</strong>：<strong>遠い・小さい物</strong>を除外・簡略化。
    - <strong>CPU でのカリングの限界</strong>：<strong>物体数が増える</strong>と<strong>判断自体が、CPU の負担</strong>。→ <strong>階層構造・GPU Driven・Meshlet</strong>。
    - <strong>カリングの単位</strong>（物体・クラスター・三角形）を、<strong>細かくする</strong>ほど、<strong>無駄が減る</strong>（が、判断の数は増える）。

## カリングの種類

<svg class="fig illust" viewBox="0 0 800 300" role="img" aria-label="カリングの種類（真上から見た図）">
<text x="20" y="24" class="fig-title">真上から見た図：カメラから見えるもの（緑）と、見えないもの（赤）</text>
<circle cx="90" cy="170" r="7" fill="currentColor"/><text x="70" y="196" style="font-size:12px">カメラ</text>
<polygon points="90,170 420,50 420,290" fill="rgba(76,139,245,0.1)" stroke="currentColor" stroke-width="2"/>
<rect x="190" y="150" width="30" height="30" fill="rgba(46,160,67,0.5)" stroke="currentColor"/><text x="186" y="198" style="font-size:11px">描く</text>
<rect x="330" y="120" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="318" y="168" style="font-size:11px">壁の裏（隠れる）</text>
<rect x="300" y="60" width="16" height="190" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="288" y="52" style="font-size:11px">大きな壁</text>
<rect x="180" y="50" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="150" y="44" style="font-size:11px">視錐台の外</text>
<rect x="190" y="250" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="150" y="296" style="font-size:11px">視錐台の外</text>
<rect x="470" y="130" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="440" y="178" style="font-size:11px">遠すぎる</text>
<text x="560" y="80" style="font-weight:700">視錐台カリング</text><text x="560" y="100" style="font-size:12px">視界の外を、除外</text>
<text x="560" y="140" style="font-weight:700">オクルージョン カリング</text><text x="560" y="160" style="font-size:12px">壁の裏に、隠れた物を除外</text>
<text x="560" y="200" style="font-weight:700">距離カリング</text><text x="560" y="220" style="font-size:12px">遠すぎ・小さすぎを、除外</text>
</svg>

| カリング | 何を除外するか | どこで効くか |
| --- | --- | --- |
| **視錐台カリング** | **画面の外**（カメラの後ろ・左右・上下） | **ドロー コール・頂点** |
| **オクルージョン カリング** | **ほかの物に隠れた物** | **ドロー コール・頂点・ピクセル** |
| **距離カリング** | **遠すぎる物** | 同上 |
| **小物（スモール オブジェクト）カリング** | **画面で数ピクセル以下の物** | 同上 |
| **バックフェイス カリング** | **裏を向いた三角形** | **ピクセル**（約半分） |
| **LOD** | **遠い物を簡易なモデルに** | **頂点・ピクセル** |

## 視錐台カリング

**カメラの視界（視錐台）の外**の物体を**描画しない**。**物体の境界（球・箱）が、視錐台と交わるか**で判定します（[深度とカリング](../3d/depth-culling.md)）。

| 点 | 説明 |
| --- | --- |
| **効果** | **振り向いたとき、背後の物体は描かれない**。**視界が狭い（FOV が小さい）ほど、効く** |
| **判定の速さ** | **球は速い**。**箱（AABB）は、正確** |
| **CPU の負担** | **物体 1 つずつ、6 つの平面と判定**（**数万個で重い**） |

### 階層構造で速くする

**物体を、1 つずつ判定する**のは、**遅い**です。<strong>空間を階層（木）</strong>にして、<strong>「木の枝全体が外」なら、中の物をまとめて除外</strong>します。

| 構造 | 説明 |
| --- | --- |
| **八分木（Octree）・BVH** | **空間を再帰的に分割**。**親が外なら、子は判定しない** |
| **グリッド** | **セルごとに物体を持つ**。**セル単位で判定** |
| **効果** | **判定の回数が、O(n) から O(log n) に**（[空間分割](../optimize/algorithms.md)） |

## オクルージョン カリング

**壁・建物・地形の裏に隠れた物**を**除外**します。**視錐台カリングより、効果が大きい**（**都市・室内**）が、**実装が難しい**です。

### 手法

| 手法 | 仕組み | 長所 | 短所 |
| --- | --- | --- | --- |
| <strong>事前計算（PVS）</strong> | <strong>「この場所から見える物」を、あらかじめ計算</strong>（ベイク） | **実行時がほぼゼロ** | **動くものに使えない**・ビルドが重い |
| **ソフトウェア ラスタライザ** | **CPU で低解像度の深度バッファを描き**、**物体の境界が隠れるか判定** | **GPU を使わない・同期待ちなし** | **CPU の負担** |
| **GPU オクルージョン クエリ** | **物体の境界を描いて、1 ピクセルでも通れば、見える**と判定 | **GPU の深度を使える** | **結果が遅れて届く**（数フレーム） |
| <strong>Hi-Z（階層的な深度）</strong> | **前フレームの深度から、階層（ミップ）を作り**、**GPU で物体が隠れるか判定** | **GPU で並列・高速** | **前フレームの情報**（動きに遅れる）（[Hi-Z](hiz.md)） |

### 時間の遅れの問題

**GPU クエリ**や **Hi-Z** は、**前のフレームの深度**を使うことが多く、<strong>カメラが急に動くと、「見えるはずの物がまだ見えない」</strong>（**ポップイン**）ことが起きます。**対策**：**保守的に**（**少し、多めに描く**）、**2 パス**（**前フレームで見えていた物を、先に描き、その深度で残りを判定**）にします（[GPU Driven](gpu-driven.md)）。

## 距離カリング・小物カリング

| カリング | 説明 |
| --- | --- |
| **距離カリング** | **ある距離より遠い物は、描かない**（**フォグで隠す**） |
| **小物カリング** | **画面上の大きさが数ピクセル以下**なら、**描かない**（**見た目にほぼ影響しない**） |

<strong>物体の「画面上の大きさ」</strong>は、**境界球の半径 ÷ 距離**で、**簡単に**求められます。

## LOD（Level of Detail）

**遠い物を頂点の少ない、簡易なモデルに切り替える**。

| 種類 | 説明 |
| --- | --- |
| **離散 LOD** | **LOD0（詳細）・LOD1・LOD2 ...** を距離で切り替え |
| <strong>インポスター（ビルボード）</strong> | **非常に遠い物を画像 1 枚**に（木・建物） |
| **連続 LOD・クラスター LOD** | **三角形の塊（Meshlet）単位**で**滑らかに詳細度を変える**（[Mesh Shader](mesh-shaders.md)） |

**LOD の切り替わりが、目立つ**（ポップ）ときは<strong>ディザリング（ディザ フェード）</strong>で、**混ぜます**。

## バックフェイス カリング・そのほか

| カリング | 説明 |
| --- | --- |
| **バックフェイス** | **裏向きの三角形**を**ラスタライズ前に除外**（**ハードウェアの機能**。`CullMode = BACK`） |
| **ポータル・セル** | <strong>部屋（セル）と、ドア（ポータル）</strong>で、**見える部屋だけ**を描く（**室内ゲーム**） |
| **影のカリング** | **影を落とさない物・影が見えない物**を**影マップの描画から**、除外 |

## カリングの単位を、細かくする

カリングは**どの単位で判定するか**で**効果と判定のコスト**が変わります。

<svg class="fig illust" viewBox="0 0 800 240" role="img" aria-label="カリングの単位の、細かさ">
<defs><marker id="cu1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">単位を細かくするほど、無駄は減るが、判定の数は、増える</text>
<rect x="20" y="50" width="170" height="90" rx="10" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/><text x="105" y="82" text-anchor="middle" style="font-weight:700">物体ごと</text><text x="105" y="104" text-anchor="middle" style="font-size:12px">（CPU で判定）</text><text x="105" y="122" text-anchor="middle" style="font-size:12px">一部が見えれば、全部描く</text>
<line x1="196" y1="95" x2="246" y2="95" stroke="currentColor" stroke-width="3" marker-end="url(#cu1)"/>
<rect x="254" y="50" width="170" height="90" rx="10" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="3"/><text x="339" y="82" text-anchor="middle" style="font-weight:700">サブメッシュごと</text><text x="339" y="104" text-anchor="middle" style="font-size:12px">（GPU Driven）</text><text x="339" y="122" text-anchor="middle" style="font-size:12px">物体の一部を、除外</text>
<line x1="430" y1="95" x2="480" y2="95" stroke="currentColor" stroke-width="3" marker-end="url(#cu1)"/>
<rect x="488" y="50" width="170" height="90" rx="10" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="3"/><text x="573" y="82" text-anchor="middle" style="font-weight:700">Meshlet ごと</text><text x="573" y="104" text-anchor="middle" style="font-size:12px">（64 頂点ほどの塊）</text><text x="573" y="122" text-anchor="middle" style="font-size:12px">細かく除外</text>
<line x1="664" y1="95" x2="704" y2="95" stroke="currentColor" stroke-width="3" marker-end="url(#cu1)"/>
<rect x="712" y="50" width="78" height="90" rx="10" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="3"/><text x="751" y="86" text-anchor="middle" style="font-weight:700">三角形</text><text x="751" y="108" text-anchor="middle" style="font-size:11px">最も細かい</text>
<text x="20" y="190" style="font-size:12px">粗い（物体）：判定は少ない／無駄は多い　→　細かい（三角形）：無駄は少ない／判定は多い（GPU で並列にやる）</text>
</svg>

| 単位 | 説明 |
| --- | --- |
| <strong>物体（インスタンス）</strong> | **CPU で判定**。**大きな物体は一部だけ見えても全体を描く** |
| **サブメッシュ** | **物体を分割**（建物の部屋ごと）。**無駄が減る** |
| <strong>Meshlet（クラスター）</strong> | **64 頂点・124 三角形ほどの塊**。**GPU が塊ごとにカリング**（[Mesh Shader](mesh-shaders.md)） |
| **三角形** | **最も細かい**。**GPU のフィクスト ファンクションが、行う**（バックフェイスなど） |

**物体数が多く・形が複雑**になるほど、**判定を、CPU から GPU へ**、**単位を細かく**——**この流れ**が**次の GPU Driven・Meshlet**です。

## 段階のまとめ

| 段階 | 手法 | カリングの場所 | 単位 |
| --- | --- | --- | --- |
| **1** | <strong>視錐台カリング（CPU）</strong> | CPU | 物体 |
| **2** | <strong>階層構造（Octree・BVH）</strong> | CPU | 物体 |
| **3** | <strong>オクルージョン（Hi-Z・ソフトウェア）</strong> | CPU / GPU | 物体 |
| **4** | <strong>GPU Driven（コンピュートでカリング）</strong> | **GPU** | 物体・サブメッシュ |
| **5** | <strong>Meshlet カリング（Mesh Shader）</strong> | **GPU** | **Meshlet** |

## よくあるミス

??? failure "境界ボックスが、大きすぎて、カリングが効かない"
    **物体にぴったりの境界**にします（回転で広がる AABB に注意）。

??? failure "オクルージョンで、見えるはずの物が消える"
    **前フレームの情報の遅れ**です。**保守的な判定**・**2 パス**にします。

??? failure "カリングの判定が、重すぎて、CPU が詰まる"
    **階層構造**にする、**GPU に任せる**。

??? failure "LOD の切り替わりが、目立つ"
    **ディザ フェード**・**切り替え距離のヒステリシス**。

??? failure "影の描画で、カリングしていない"
    **影を落とす物・見える範囲**で**別にカリング**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カリング ＝ <strong>見えないものを、描かない</strong>。<strong>早い段階で除外するほど、効果が大きい</strong>
    - [x] 種類：<strong>視錐台・オクルージョン・距離・小物・バックフェイス・LOD</strong>
    - [x] <strong>視錐台カリングは、基本</strong>。<strong>階層構造（Octree・BVH）</strong>で、速くする
    - [x] <strong>オクルージョンは、効果大・難しい</strong>。<strong>Hi-Z が主流</strong>。<strong>前フレームの遅れに注意</strong>
    - [x] <strong>単位を細かく</strong>（物体 → サブメッシュ → Meshlet）。<strong>判定を、CPU から GPU へ</strong>

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [ドロー コールとバッチ](draw-calls.md)
- [GPU Driven Rendering](gpu-driven.md)
- [Hi-Z とスクリーン空間トレース](hiz.md)
- [深度とカリング](../3d/depth-culling.md)
- [空間分割（アルゴリズム）](../optimize/algorithms.md)
