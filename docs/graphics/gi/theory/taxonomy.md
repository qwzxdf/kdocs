---
title: Taxonomy of Methods
tags:
  - 描画
---

# Taxonomy of Methods

<strong>GI の手法は数多くありますが、「2 つの軸」で整理すると見通しが良くなります</strong>。1 つ目は「静的 ↔ 動的」、2 つ目は「画面内の情報 ↔ 世界の情報」です。このページでは 2 つの軸と代表的な手法の位置づけを説明します。

!!! tip "ポイント"
    - 軸 1：静的（ベイク）か、動的（リアルタイム）か。
    - 軸 2：画面の情報だけか、世界全体の情報か。
    - ライトマップ ＝ 静的・世界。SSGI ＝ 動的・画面。DDGI・Lumen ＝ 動的・世界。
    - 用途と予算に合わせて選ぶ。

!!! info "このページを読む前に"
    - [GI Theory](index.md)（このセクション全体の地図と、読む順番）

## 手法を分ける 2 つの軸

### 軸 1：いつ計算するか

1 つ目の軸は計算の時点です。

<strong>事前（ベイク）</strong>はオフラインで時間をかけて計算し、結果を保存します。ライトマップとベイク済みプローブが代表です。実行時のコストが小さく品質も高く出せますが、光が動くと対応できません。準動的はジオメトリは静的なままで、光だけを動的に更新する方式です。プローブの再ライティングや DDGI が当てはまります。太陽が動くライトのオン・オフを切り替えるといった変化に対応できます。完全動的はジオメトリも光も動いてよい方式で、毎フレーム計算します。SSGI・ボクセル GI・レイトレ GI が当てはまります。自由度が最も高い代わりにコストが最も大きくなります。

### 軸 2：どこに情報を持つか

2 つ目の軸は光の情報の保存先です。

面（テクスチャ）はオブジェクトの表面の UV 上に保存します（ライトマップ）。空間の点は 3D 空間の格子や点に保存します（プローブ・DDGI）。画面は今見えている画素の情報だけを使います（SSGI）。ボクセルは 3D の格子にシーンの光と形を保存します（ボクセル GI）。世界（レイ）は保存せず光線を飛ばしてその場で調べます（レイトレ GI）。

各手法がこの 2 軸のどこに位置するかで、長所と短所がほぼ決まります。たとえば、ライトマップは「静的・面」なので、実行時は速いが動的な光に対応できず、動く物体には使えません（別にプローブが必要）。SSGI は「動的・画面」なので、何でも動かせるが画面に映らない物からの光は取れません。DDGI や Lumen は「動的・世界」なので、動的で画面外の光も扱えますが、システムが大きくコストが重く、ハードウェア要件も上がります。

どれが「最良」ということはなく、ゲームのジャンルと対象ハードウェアで選びます。昼夜が変わらない屋内中心のゲームならライトマップが最も効率的で、オープンワールドで時刻が変わるなら動的な方式が必要です。多くの商用ゲームは複数の手法を組み合わせて使います（[GI Comparison](../comparison.md)）。

<!-- fig:gi-color-bleeding:begin -->

<svg class="fig illust motion" data-fig="gi-color-bleeding" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gi-color-bleeding" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<linearGradient id="gi-bleed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5a5f" stop-opacity="0.75"/>
<stop offset="1" stop-color="#ff5a5f" stop-opacity="0"/>
</linearGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">間接光:光が壁で跳ね返って、隣の面に色がにじむ</text>
<rect x="80" y="60" width="480" height="270" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<rect x="72" y="60" width="16" height="270" fill="#e5484d"/>
<text x="86" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">赤い壁</text>
<rect x="80" y="330" width="480" height="14" fill="#94a3b8"/>
<rect x="80" y="320" width="180" height="10" fill="url(#gi-bleed)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></rect>
<circle cx="330" cy="72" r="12" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="348" y="78" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光源</text>
<line x1="330" y1="84" x2="420" y2="328" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1739;1.0000" values="1;1;0;0"/></line>
<polygon points="420,328 411.36,319.67 421.16,316.06" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></polygon>
<rect x="386" y="320" width="68" height="10" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></rect>
<line x1="320" y1="82" x2="86" y2="190" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2435;0.3304;1.0000" values="1;1;0;0"/></line>
<polygon points="86,190 93.62,180.73 98.0,190.21" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="130" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3826;0.4522;1.0000" values="1;1;0;0"/></line>
<polygon points="130,328 121.74,319.29 131.69,316.12" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="210" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4174;0.4870;1.0000" values="1;1;0;0"/></line>
<polygon points="210,328 198.9,323.45 206.66,316.47" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="290" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4522;0.5217;1.0000" values="1;1;0;0"/></line>
<polygon points="290,328 278.13,326.27 283.97,317.62" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></polygon>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光源から出た光<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 床に当たる（直接光）→ 明るくなる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 赤い壁に当たる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 壁は赤い光だけを反射して、四方に跳ね返す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 壁の近くの床が赤っぽくなる（色のにじみ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="80" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">間接光は、直接光が当たった面が「次の光源」になる。リアルタイムでは、プローブやボクセルで近似する。</text>
<text x="590" y="90" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">光の跳ね返り</text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">0 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（直接）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（壁へ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">2 回（壁 → 床）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gi-color-bleeding:end -->

## 代表的な手法を並べる

GI の手法は <strong>多く</strong>ありますが、2 つの軸（いつ計算するか、どこに情報を持つか）で整理すると、見通しがよくなります。

| 手法 | いつ計算 | 情報の置き場 | 動的な物 | 動的な光 | 見える範囲 |
| --- | --- | --- | --- | --- | --- |
| ライトマップ | 事前（ベイク） | テクスチャ（面に貼る） | △（受け取れない） | ×（固定） | 世界全体（事前に、計算済み） |
| プローブ GI（ベイク） | 事前 | 空間の点（プローブ） | ○（プローブから、受け取る） | × | 世界全体 |
| DDGI | 実行時 | 空間の点（プローブ） | ○ | ○ | 世界全体（レイトレーシングが必要） |
| ボクセル GI（VXGI） | 実行時 | ボクセル（3D グリッド） | ○ | ○ | 世界全体（ボクセル化した範囲） |
| SSGI | 実行時 | 画面（G バッファ、深度） | ○ | ○ | 画面に映る範囲だけ |
| Lumen 型 | 実行時 | 距離場、サーフェス キャッシュ、画面 | ○ | ○ | 世界全体 |
| ReSTIR GI | 実行時 | 画素ごとの、サンプル | ○ | ○ | 世界全体（レイトレーシング） |
| Radiance Cascades | 実行時 | カスケード（レイの、束） | ○ | ○ | 画面または、世界 |

## 軸 1：いつ計算するか

| | 事前（ベイク） | 実行時（リアルタイム） |
| --- | --- | --- |
| 品質 | 最高（時間をかけて、計算） | 手法による（近似が多い） |
| 動的な光（昼夜、動くライト） | 対応できない（光が固定） | 対応できる |
| 動的な物（扉、移動する壁） | 反映できない（物が動いても光はそのまま） | 反映できる |
| 実行時のコスト | 最小（テクスチャを読むだけ） | 大きい（毎フレーム、計算） |
| 制作の手間 | ベイクの、待ち時間（数分〜数時間）、UV、データ管理 | ベイク不要 |

<strong>静的な場面</strong>（光も物も動かない）なら、ベイクが最高品質で最安です。時間帯が変わる物が壊れる場面では、実行時の手法が必要です。

## 軸 2：どこに情報を持つか

| | 画面（スクリーン スペース） | 世界（ワールド スペース） |
| --- | --- | --- |
| 内容 | 画面に映っている範囲の、情報（深度、法線、色）だけ | 世界全体の情報（プローブ、ボクセル、距離場、BVH） |
| 画面の外の光 | 使えない（画面の端で、破綻） | 使える |
| コスト | 画面の解像度に比例。シーンの複雑さに依存しない | 世界の、複雑さに依存（ボクセル化、キャッシュ更新） |
| 実装 | 簡単（ポスト プロセス） | 複雑（空間データ構造の、管理） |

<strong>画面空間</strong>の手法は 簡単で、軽い一方、見えていない物（画面の外、物の裏）からの光が反映されません。世界空間の手法はそのような制限がありませんがデータ構造の維持が重く、複雑です。

## どう選ぶか

```text
場面は、静的か？（光も、物も、動かない）
 ├ Yes → ライトマップ（+ 動く物のための、ライト プローブ）
 └ No ↓
レイトレーシングに、対応できるか？（GPU が、DXR に、対応）
 ├ Yes → DDGI、ReSTIR GI、Lumen 型（ハードウェア RT）
 └ No ↓
世界全体の、情報が、必要か？（画面外の、光が、重要）
 ├ Yes → ボクセル GI、Lumen 型（ソフトウェア）、ベイクしたプローブ + 動的な、更新
 └ No ↓
とにかく、軽く → SSGI（画面空間）+ ベイクしたプローブ（画面外の、フォールバック）
```

## 組み合わせる

<strong>1 つの手法ですべてをまかなう</strong>のは、難しいので複数を組み合わせることが、多いです。

| 組み合わせ | 内容 |
| --- | --- |
| ライトマップ（静的）+ プローブ（動く物） | 背景は、ライトマップ、キャラクターはプローブから補間（古典的な、構成） |
| SSGI + プローブ（フォールバック） | 画面に映る範囲は、SSGI で正確に画面外はプローブで、補う |
| ベイクしたライトマップ + 動的な、太陽の影 | 間接光は焼き込み、直接光だけ動的 |
| Lumen 型（距離場 + 画面 + サーフェス キャッシュ） | 近くは、画面空間で正確、遠くは距離場・キャッシュで近似。複数の手法を内部で組み合わせた、1 つの製品 |

## ゲームのジャンルで選ぶ

| ジャンル | 光 | おすすめ |
| --- | --- | --- |
| 狭い室内のホラー、一本道 | 静的 | ライトマップ |
| オープン ワールド（昼夜） | 動的 | Lumen 型、DDGI、プローブの動的更新 |
| レース、スポーツ | ほぼ静的（天気は、変わる） | ライトマップ + 時間帯の、補間 |
| モバイル | 軽さ最優先 | ライトマップ、SH プローブ（ベイク） |
| スタイライズ（アニメ調） | 簡単でよい | 半球ライト、環境光（GI なし） |

## よくあるミス

??? failure "動的な光にライトマップを使ってしまう"
    <strong>動的な光には動的な GI</strong>（プローブ・SSGI など）を選ぶ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 静的か動的か、画面か世界か
    - [x] 用途に合わせて選ぶ

## 参考

- Kajiya, "The Rendering Equation", SIGGRAPH 1986（レンダリング方程式の原典）
- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001（放射照度を 9 個の SH 係数で表す）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、放射照度、SH の章）
- Wright, Narkowicz, Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games

## 関連ページ

- [GI Theory](index.md)
- [GI Comparison](../comparison.md)
- [Lightmaps](../lightmaps/index.md)
