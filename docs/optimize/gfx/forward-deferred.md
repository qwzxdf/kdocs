---
title: Forward と Deferred
tags:
  - 最適化
  - 3Dゲーム
---

# Forward と Deferred

**ライティング**（光の計算）を、**どの順番で、行うか**で、**描画の、重さの構造**が、大きく変わります。多くのエンジンは、**最初は Forward**（物体を描くたびに、光も計算）で、**ライトが、増える**と、**Deferred**（**形を先に描き、光を、あとでまとめて計算**）に移ります。このページは、**Forward の、何が重いのか**、**Deferred で、何が改善するのか**、**その代償**を、**目的から**説明します。

!!! tip "ポイント"
    - <strong>Forward</strong>：<strong>物体を描きながら、ピクセルごとに、全ライトを計算</strong>。<strong>コスト ≒ 物体のピクセル（オーバードロー込み）× ライトの数</strong>。
    - <strong>問題</strong>：<strong>あとで隠れるピクセルにも、重いライティングをする</strong>（無駄）。<strong>ライトが多いと、ピクセルシェーダーが、爆発</strong>。
    - <strong>Deferred</strong>：<strong>① G-Buffer に、形・材質の情報だけ書く　② 画面の、各ピクセルで、1 回だけ、ライティング</strong>。<strong>コスト ≒ 画面のピクセル × ライト</strong>。
    - <strong>改善</strong>：<strong>「物体の数」と「ライトの数」が、掛け算でなく、足し算に</strong>。<strong>オーバードローの、ライティングが、消える</strong>。
    - <strong>代償</strong>：<strong>G-Buffer の、帯域（書き込み・読み込み）</strong>。<strong>MSAA・半透明・材質の多様性が、難しい</strong>。
    - <strong>ライトごとに、フルスクリーンで読む</strong>のは、<strong>帯域が重い</strong>。→ <strong>Tiled / Clustered へ</strong>（[Tiled と Clustered](light-culling.md)）。

## Forward（前向き）レンダリング

**物体を描くとき、その場で、色（ライティング込み）を、完成させる**方式です。

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="Forward レンダリングの流れ">
<defs><marker id="fd1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">Forward：物体ごとに、ピクセルごとに、ライトの数だけ、計算する</text>
<rect x="30" y="50" width="120" height="70" rx="10" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="3"/><text x="90" y="82" text-anchor="middle" style="font-weight:700">物体 A</text><text x="90" y="102" text-anchor="middle" style="font-size:12px">頂点 → ピクセル</text>
<rect x="30" y="140" width="120" height="70" rx="10" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="3"/><text x="90" y="172" text-anchor="middle" style="font-weight:700">物体 B</text><text x="90" y="192" text-anchor="middle" style="font-size:12px">頂点 → ピクセル</text>
<line x1="158" y1="85" x2="258" y2="125" stroke="currentColor" stroke-width="3" marker-end="url(#fd1)"/><line x1="158" y1="175" x2="258" y2="135" stroke="currentColor" stroke-width="3" marker-end="url(#fd1)"/>
<rect x="266" y="90" width="270" height="80" rx="12" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/>
<text x="401" y="122" text-anchor="middle" style="font-weight:700">ピクセルシェーダー</text><text x="401" y="144" text-anchor="middle" style="font-size:12px">全ライトを、ループで計算</text><text x="401" y="160" text-anchor="middle" style="font-size:12px">（隠れるピクセルでも、実行）</text>
<line x1="544" y1="130" x2="614" y2="130" stroke="currentColor" stroke-width="3" marker-end="url(#fd1)"/>
<rect x="622" y="90" width="150" height="80" rx="12" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="3"/><text x="697" y="124" text-anchor="middle" style="font-weight:700">完成した色</text><text x="697" y="146" text-anchor="middle" style="font-size:12px">画面へ</text>
<text x="20" y="245" style="font-size:12px">コスト ＝ Σ（各物体のピクセル数 ×（オーバードロー）× 影響するライトの数）</text>
</svg>

### 何が重いのか

| 問題 | 説明 |
| --- | --- |
| **オーバードロー** | **手前の物体が、後から描かれる**と、**奥の物体の、ライティング済みの色が、無駄**になる。**重い計算を、捨てている** |
| **ライトが、多いと** | **1 ピクセルごとに、全ライトを、ループ**。**100 個で、100 倍** |
| **ライトの数が、物体ごとに、違う** | **物体ごとに、シェーダー（バリアント）を切り替える**（**ライト数 N の、シェーダー**）。**ドロー コール・状態切り替えが、増える** |
| **範囲外のライト** | **遠いライトも、計算**（**影響が、ゼロでも**）してしまう |

### 工夫と限界

| 工夫 | 説明 |
| --- | --- |
| **Z プリパス**（深度だけ、先に描く） | **オーバードローの、ライティングを、避ける**（[オーバードロー](overdraw.md)）。**ジオメトリを、2 回描く** |
| **ライトの上限**（物体ごとに、近い 4 つだけ） | **簡単だが、ライトが、ちらつく・多数のライトが、使えない** |
| **ライトの、事前の絞り込み** | **Tiled / Clustered Forward**（[Tiled と Clustered](light-culling.md)） |

### Forward の、長所

| 長所 | 説明 |
| --- | --- |
| **帯域が、少ない** | **G-Buffer が、不要**。**直接、画面に書く** |
| **MSAA が、使える** | **ハードウェアの、アンチエイリアシングが、素直に使える** |
| **半透明が、扱える** | **普通に、ブレンドできる** |
| **材質が、自由** | **物体ごとに、シェーダーを変えて、特殊な表現**（髪・肌・布）ができる |
| **単純** | **仕組みが、分かりやすい** |

**ライトが、少ない**（太陽 ＋ 数個）なら、**Forward が、最適**なことも多いです（**VR・モバイル・スタイライズされた表現**）。

## Deferred（遅延）レンダリング

<strong>「形と材質の情報」を、先に、バッファ（G-Buffer）に書き</strong>、<strong>「ライティング」を、あとで、画面全体に対して、まとめて行う</strong>方式です。

<svg class="fig illust" viewBox="0 0 820 300" role="img" aria-label="Deferred レンダリングの流れ">
<defs><marker id="fd2" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">Deferred：① 形と材質を G-Buffer に書く　② 画面のピクセルごとに 1 回だけ、ライティング</text>
<rect x="20" y="60" width="130" height="100" rx="10" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="3"/><text x="85" y="96" text-anchor="middle" style="font-weight:700">全ての物体</text><text x="85" y="118" text-anchor="middle" style="font-size:12px">材質の情報を</text><text x="85" y="136" text-anchor="middle" style="font-size:12px">書くだけ（軽い）</text>
<line x1="158" y1="110" x2="228" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#fd2)"/><text x="193" y="98" text-anchor="middle" style="font-size:12px">① 書く</text>
<g>
<rect x="236" y="48" width="140" height="30" fill="rgba(229,170,40,0.4)" stroke="currentColor" stroke-width="2"/><text x="306" y="68" text-anchor="middle" style="font-size:12px">アルベド（色）</text>
<rect x="236" y="82" width="140" height="30" fill="rgba(46,160,67,0.4)" stroke="currentColor" stroke-width="2"/><text x="306" y="102" text-anchor="middle" style="font-size:12px">法線</text>
<rect x="236" y="116" width="140" height="30" fill="rgba(150,100,230,0.4)" stroke="currentColor" stroke-width="2"/><text x="306" y="136" text-anchor="middle" style="font-size:12px">金属度・粗さ・AO</text>
<rect x="236" y="150" width="140" height="30" fill="rgba(229,72,77,0.35)" stroke="currentColor" stroke-width="2"/><text x="306" y="170" text-anchor="middle" style="font-size:12px">深度（位置を復元）</text>
</g>
<text x="306" y="198" text-anchor="middle" style="font-weight:700">G-Buffer</text>
<line x1="386" y1="110" x2="466" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#fd2)"/><text x="426" y="98" text-anchor="middle" style="font-size:12px">② 読む</text>
<rect x="474" y="60" width="170" height="100" rx="10" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/><text x="559" y="96" text-anchor="middle" style="font-weight:700">ライティング パス</text><text x="559" y="118" text-anchor="middle" style="font-size:12px">画面の各ピクセルに、</text><text x="559" y="136" text-anchor="middle" style="font-size:12px">1 回だけ、光を計算</text>
<line x1="652" y1="110" x2="716" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#fd2)"/>
<rect x="724" y="60" width="80" height="100" rx="10" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="3"/><text x="764" y="116" text-anchor="middle" style="font-weight:700">画面</text>
<text x="20" y="250" style="font-size:12px">コスト ＝ ジオメトリ（G-Buffer への書き込み）＋ 画面のピクセル × ライト（物体の数に、無関係）</text>
<text x="20" y="272" style="font-size:12px">オーバードローしても、ライティングは「最後に残ったピクセル」だけ。無駄が、なくなる</text>
</svg>

### 何が、改善するのか

| 改善 | 説明 |
| --- | --- |
| **オーバードローの、ライティングが、消える** | **ライティングは、最終的に、見えるピクセルだけ**（1 ピクセル 1 回） |
| <strong>「物体 × ライト」が、「物体 ＋ ライト」に</strong> | **ジオメトリの数と、ライトの数が、独立**。**ライトを、たくさん置ける** |
| **ライトの範囲を、使える** | **ライトが、影響する範囲（球・円錐）のピクセルだけ**、計算できる（ライト ボリューム） |
| **シェーダーの切り替えが、減る** | **ライティングの、シェーダーは、1 種類**。**材質の違いは、G-Buffer の値** |
| **ポストエフェクトに、使える** | **G-Buffer（法線・深度）を、AO・SSR・デカールが、再利用** |

**ライトが、数百個**（**街灯・たいまつ・窓の明かり**）ある**大規模なシーン**で、**Deferred が、使われます**。

### ライト ボリューム

**ライトごとに、影響する範囲**（球・円錐）を、**簡単な形**として描き、**その形が覆うピクセルだけ**を、**ライティング**します。

| ライトの種類 | 描く形 |
| --- | --- |
| **ポイントライト** | **球** |
| **スポットライト** | **円錐** |
| <strong>ディレクショナル（太陽）</strong> | **フルスクリーン**（画面全体） |

**遠くのライトは、小さな範囲**なので、**少ないピクセル**で済みます。**ライトごとに、G-Buffer を、読み直す**——これが、次の問題になります。

### 代償（何が、悪くなるか）

| 問題 | 説明 |
| --- | --- |
| **帯域が、重い** | **G-Buffer の書き込み**（複数 RT）と、**ライトごとの、読み込み**。**100 ライトで、数百 GB/s**（[メモリ帯域幅](bandwidth.md)） |
| **MSAA が、難しい** | **G-Buffer が、サンプル数倍**になる。**TAA・FXAA** で代用 |
| **半透明が、使えない** | **G-Buffer に、1 ピクセル 1 つの情報しか、書けない**。**半透明は、別の Forward パス**で描く |
| **材質の多様性が、制限される** | **G-Buffer に入る項目だけ**。**特殊な材質（髪・肌・布）は、工夫**（シェーディング モデル ID） |
| **ライトの、ブレンドの帯域** | **ライトごとに、結果を、加算ブレンドで、書く**（読み書きが、重なる） |
| **G-Buffer の設計が、難しい** | **何を、どのフォーマットで、詰めるか** |

## 比べ

| | **Forward** | **Deferred** |
| --- | --- | --- |
| **ライティングの回数** | <strong>物体ごと（オーバードロー込み）</strong> | **ピクセルごとに、1 回** |
| **ライトが多い** | **苦手**（掛け算） | **得意** |
| **帯域** | **少ない** | **多い**（G-Buffer） |
| **MSAA** | **◎** | **×**（難しい） |
| **半透明** | **◎** | **×**（別パス） |
| **材質の自由度** | **◎** | **△**（G-Buffer に収まる範囲） |
| **向く場面** | **ライトが少ない・VR・モバイル** | **ライトが多い・大規模な屋外** |

**実際のエンジンは、組み合わせ**ます：**不透明は Deferred、半透明は Forward**。**Clustered / Tiled** で、**どちらも、ライトが、多くても、速く**できます。

## 流れの、まとめ（次の段階へ）

<svg class="fig illust" viewBox="0 0 800 130" role="img" aria-label="ライティング手法の進化">
<defs><marker id="fd3" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<rect x="10" y="30" width="150" height="70" rx="10" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-width="2"/><text x="85" y="58" text-anchor="middle" style="font-weight:700">Forward</text><text x="85" y="80" text-anchor="middle" style="font-size:11px">物体×ピクセル×ライト</text>
<line x1="166" y1="65" x2="206" y2="65" stroke="currentColor" stroke-width="3" marker-end="url(#fd3)"/>
<rect x="214" y="30" width="150" height="70" rx="10" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/><text x="289" y="58" text-anchor="middle" style="font-weight:700">Deferred</text><text x="289" y="80" text-anchor="middle" style="font-size:11px">ピクセル×ライト</text>
<line x1="370" y1="65" x2="410" y2="65" stroke="currentColor" stroke-width="3" marker-end="url(#fd3)"/>
<rect x="418" y="30" width="170" height="70" rx="10" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="503" y="58" text-anchor="middle" style="font-weight:700">Tiled</text><text x="503" y="80" text-anchor="middle" style="font-size:11px">ピクセル×近くのライト</text>
<line x1="594" y1="65" x2="634" y2="65" stroke="currentColor" stroke-width="3" marker-end="url(#fd3)"/>
<rect x="642" y="30" width="150" height="70" rx="10" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="717" y="58" text-anchor="middle" style="font-weight:700">Clustered</text><text x="717" y="80" text-anchor="middle" style="font-size:11px">3 次元で、さらに絞る</text>
</svg>

**次のページ**：[Tiled と Clustered](light-culling.md)（ライトの絞り込みで、**帯域も計算も、減らす**）。

## よくあるミス

??? failure "ライトが数個なのに、Deferred にして、遅くなる"
    **G-Buffer の帯域**が、**メリットを、上回ります**。**Forward が、速い**こともあります。

??? failure "Deferred で、MSAA を使おうとして、帯域が爆発する"
    **TAA** など、別の方式にします。

??? failure "半透明を、Deferred のパスで描こうとする"
    **半透明は、Forward パス**で、**後から**描きます。

??? failure "ライトごとに、フルスクリーンで、描画する"
    **帯域が、尽きます**。**ライト ボリューム**で範囲を絞るか、**Tiled / Clustered**に。

??? failure "G-Buffer に、位置（RGBA32F）を、保存する"
    **深度から復元**します（[メモリ帯域幅](bandwidth.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>Forward ＝ 物体を描きながら、ライティング</strong>。<strong>コスト ＝ 物体のピクセル（オーバードロー込み）× ライト</strong>
    - [x] <strong>Deferred ＝ G-Buffer に書いてから、画面の各ピクセルで 1 回だけ、ライティング</strong>
    - [x] 改善：<strong>オーバードローの、ライティングが、消える</strong>。<strong>物体とライトの、掛け算が、足し算に</strong>
    - [x] 代償：<strong>G-Buffer の帯域・MSAA・半透明・材質の自由度</strong>
    - [x] <strong>ライトが少なければ Forward、多ければ Deferred</strong>。<strong>半透明は Forward で</strong>
    - [x] 次は<strong>Tiled / Clustered</strong>（ライトの絞り込み）

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [メモリ帯域幅](bandwidth.md)
- [Tiled と Clustered](light-culling.md)
- [オーバードローと Z プリパス](overdraw.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [PBR](../../3d/pbr.md)
