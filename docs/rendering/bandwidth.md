---
title: メモリ帯域幅
tags:
  - 最適化
  - 3Dゲーム
---

# メモリ帯域幅

**メモリ帯域幅**（バンド幅、bandwidth）は、**GPU がメモリ（VRAM）と、データをやり取りできる、速さ**（1 秒あたりの量。たとえば **256 GB/s**）です。**描画が重い**理由の**大きな割合**が**計算ではなく、メモリの読み書き**です。**Deferred・G-Buffer・高解像度・ポストエフェクト**が**帯域を食う**ので**多くの最適化**（**Tiled・Visibility Buffer・低解像度・フォーマットの工夫**）の**目的は、「帯域を減らす」こと**です。このページは**帯域とは何か**、**何が帯域を使うか**、**計算の仕方**、**減らす方法**をまとめます。

!!! tip "ポイント"
    - 帯域は<strong>「1 フレームでメモリを読み書きできる量」の上限</strong>。<strong>60 FPS で、256 GB/s なら、1 フレームあたり約 4.3 GB</strong>。
    - 帯域を使うもの：<strong>レンダーターゲットの書き込み・読み込み、G-Buffer、テクスチャ、頂点・インデックス、深度、ポストエフェクト</strong>。
    - <strong>ピクセルあたりのバイト数 × ピクセル数 × 回数</strong>で、<strong>概算</strong>できる。
    - 減らし方：<strong>フォーマットを小さく・パッキング・圧縮・低解像度・読み書き回数を減らす・キャッシュに乗せる</strong>。
    - <strong>モバイル GPU（タイル型）</strong>は、<strong>帯域がさらに貴重</strong>（<strong>オンチップ メモリ</strong>を活かす）。
    - <strong>「計算を増やして、メモリを減らす」</strong>が、近年の<strong>定番の方針</strong>。

## 帯域とは

**GPU が、1 つのピクセルを塗るためには、メモリから、データを読み**（テクスチャ・G-Buffer）、**結果をメモリに書き**（レンダーターゲット）ます。**この「運ぶ量」が、帯域の消費**です。

<svg class="fig illust" viewBox="0 0 760 240" role="img" aria-label="GPU とメモリの間の帯域">
<defs><marker id="bw1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">GPU ⇄ メモリの間の「道」。太さが、帯域。渋滞すると、計算が、待たされる</text>
<rect x="40" y="70" width="170" height="110" rx="12" fill="rgba(46,160,67,0.2)" stroke="currentColor" stroke-width="3"/>
<text x="125" y="112" text-anchor="middle" style="font-weight:700">GPU</text><text x="125" y="136" text-anchor="middle" style="font-size:12px">計算は速い</text><text x="125" y="156" text-anchor="middle" style="font-size:12px">（ALU が、たくさん）</text>
<rect x="260" y="82" width="240" height="34" fill="rgba(76,139,245,0.3)" stroke="currentColor" stroke-width="2"/><text x="380" y="104" text-anchor="middle" style="font-size:12px">読み込み：テクスチャ・G-Buffer</text>
<rect x="260" y="134" width="240" height="34" fill="rgba(229,72,77,0.3)" stroke="currentColor" stroke-width="2"/><text x="380" y="156" text-anchor="middle" style="font-size:12px">書き込み：レンダーターゲット</text>
<line x1="500" y1="99" x2="548" y2="99" stroke="currentColor" stroke-width="3" marker-end="url(#bw1)"/>
<line x1="548" y1="151" x2="502" y2="151" stroke="currentColor" stroke-width="3" marker-end="url(#bw1)"/>
<rect x="556" y="70" width="170" height="110" rx="12" fill="rgba(229,170,40,0.22)" stroke="currentColor" stroke-width="3"/>
<text x="641" y="112" text-anchor="middle" style="font-weight:700">VRAM</text><text x="641" y="136" text-anchor="middle" style="font-size:12px">容量は、大きいが</text><text x="641" y="156" text-anchor="middle" style="font-size:12px">運ぶ速さに、限り</text>
<text x="20" y="215" style="font-size:12px">帯域が、足りないと、GPU の計算は、データを、待って、遊んでしまう</text>
</svg>

| 用語 | 意味 |
| --- | --- |
| <strong>帯域幅（GB/s）</strong> | **1 秒に運べる、データの量** |
| **レイテンシ** | **データが届くまでの待ち時間**（帯域とは別） |
| **オンチップ** | **GPU の中にある、小さくて、超高速なメモリ**（キャッシュ・タイルメモリ） |
| **VRAM** | **GPU の外にある、大容量メモリ**（帯域がボトルネック） |

## 帯域を使うもの

| 項目 | 内容 |
| --- | --- |
| **カラー（RT）の書き込み** | **ピクセル × フォーマットのバイト数**（RGBA8 は 4 バイト、RGBA16F は 8 バイト） |
| <strong>ブレンド（半透明）</strong> | **読み込み ＋ 書き込み**（**2 倍**） |
| **深度の読み書き** | **深度テスト（読み）・書き込み** |
| **G-Buffer** | **複数のレンダーターゲットを、同時に書き込み**（Deferred） |
| **G-Buffer の読み込み** | **ライティングのたびに読む** |
| **テクスチャ** | **サンプリングごとの読み込み**（**ミップ・圧縮で軽減**） |
| **頂点・インデックス** | **ジオメトリの読み込み** |
| **ポストエフェクト** | **フルスクリーンごとに画面全体を読んで書く** |
| **MSAA** | **サンプル数 × 書き込み・読み込み** |

## 数字で見積もる

<strong>1920×1080（約 207 万ピクセル）</strong>で、**目安**を計算します。

| 項目 | 計算 | 1 フレームの量 |
| --- | --- | --- |
| **カラー RGBA8 の書き込み 1 回** | 207 万 × 4 B | 約 8 MB |
| **カラー RGBA16F の書き込み 1 回** | 207 万 × 8 B | 約 16 MB |
| **深度 D32 の書き込み 1 回** | 207 万 × 4 B | 約 8 MB |
| **G-Buffer（RGBA8 × 4 枚）の書き込み** | 207 万 × 16 B | **約 33 MB** |
| **G-Buffer ＋ 深度の読み込み 1 回** | 207 万 × 20 B | **約 41 MB** |
| <strong>フルスクリーン ポスト（RGBA16F を読んで書く）</strong> | 207 万 × 16 B | 約 33 MB |

**60 FPS なら、1 秒あたり**、**33 MB × 60 ＝ 約 2 GB/s**（G-Buffer の書き込みだけで）。**ライトごとに、G-Buffer をフルスクリーンで読む**と、**41 MB × ライト数 × 60 FPS**——**100 ライトなら、約 246 GB/s**で、**帯域が尽きます**。**これが、Tiled（G-Buffer を、1 回だけ読む）が、生まれた理由**です（[Tiled と Clustered](light-culling.md)）。

!!! note "あくまで、目安"
    **実際の GPU は、キャッシュ・圧縮・タイル処理**で**この数字より、少なく**なります。**ただし、「増えると効いてくる」傾向**は同じです。

## 減らす方法

### 1. フォーマットを、小さくする

| 用途 | 大きい選択 | 小さい選択 |
| --- | --- | --- |
| **HDR のカラー** | RGBA16F（8 B） | <strong>R11G11B10_FLOAT（4 B）</strong>（アルファなし・精度は少し落ちる） |
| **法線** | RGBA16F | **R10G10B10A2_UNORM**、または<strong>オクタヘドロン法線（2 チャンネル）</strong> |
| **ベースカラー** | RGBA16F | **RGBA8_UNORM_SRGB** |
| **AO・粗さ・金属度** | **別々の RT** | **1 枚にパッキング**（R8G8B8A8） |
| **深度** | D32_FLOAT_S8 | **D32_FLOAT**（ステンシル不要なら） |

### 2. 詰め込む（パッキング）

**G-Buffer の項目を、少ない RT に詰め込みます**。

| 工夫 | 説明 |
| --- | --- |
| **法線のオクタヘドロン エンコード** | **3 成分の法線を、2 成分**に（精度はほぼ同じ） |
| **位置を保存しない** | **深度から、再構築**（**ビュー行列の逆**）。**G-Buffer に位置を持たない** |
| **粗さ・金属度・AO を、1 つの RT に** | **チャンネルを共有** |
| **YCoCg など、色の変換** | **色を少ないビットで** |

### 3. 圧縮

| 圧縮 | 説明 |
| --- | --- |
| <strong>テクスチャ圧縮（BC1・BC5・BC7）</strong> | **メモリと帯域を、1/4〜1/8**に（[ベイク](../optimize/baking.md)） |
| <strong>DCC（デルタ カラー圧縮）</strong> | **GPU が自動で、RT を圧縮**（ハードウェア）。**RT の使い方次第で効く・効かない** |
| **深度の圧縮** | **GPU が自動**。**深度バッファを読み書き以外に使うと圧縮が解除されることがある** |

### 4. 解像度を、下げる

**低解像度のバッファ**（AO・霧・ブルーム）は、**ピクセル数が、1/4**です（[低解像度のエフェクト](low-res-effects.md)）。

### 5. 読み書きの回数を、減らす

| 工夫 | 説明 |
| --- | --- |
| **パスをまとめる** | **フルスクリーン パスを、1 つにまとめ**（ポストエフェクトを、1 つのシェーダーに） |
| **Tiled / Clustered** | **G-Buffer を、1 回だけ読む**（ライトごとに読まない） |
| **Visibility Buffer** | **G-Buffer を三角形の ID だけ**に（[Visibility Buffer](visibility-buffer.md)） |
| **ブレンドを減らす** | **半透明の重なりを減らす**（読み書きが倍） |
| **不要な RT クリアを、避ける** | **`DiscardView` で、内容を破棄**（**中身が不要なら**） |

### 6. キャッシュに、乗せる

| 工夫 | 説明 |
| --- | --- |
| **テクスチャを小さく・ミップを使う** | **遠くは小さなミップ**で**キャッシュに収まる** |
| **アクセスの局所性** | **隣のピクセルは、隣のテクセルを読む**（**ランダムアクセスを避ける**） |
| **サンプラーのフィルター** | **異方性を高くしすぎない**（読み込みが増える） |

## モバイル（タイル型 GPU）の場合

**スマートフォンなどの GPU は、画面を小さなタイルに分けて、描画**し、**タイルの内容をオンチップ メモリ**に置きます。**メインメモリへの書き込みは、タイルの完了時だけ**で**帯域を節約**できます。

| 注意 | 説明 |
| --- | --- |
| **オンチップの活用** | **1 つのパス内で完結**させる（**パスをまたぐとメモリに書き出す**） |
| **Deferred は、不利**になりがち | **G-Buffer のメインメモリへの書き出し**（**ただし、タイルメモリで完結させる方式**もある） |
| **ロード・ストア操作** | <strong>「クリア」「破棄」</strong>を、**明示**して、**不要な読み書きを避ける** |

**PC のデスクトップ GPU は、基本的に即時型**（タイル型ではない）ですが**近年の GPU は、内部でタイルに近い処理**を使うことがあります。

## 計算でメモリを減らす（再計算）

**メモリに保存して、読むより、必要なとき、再計算する**ほうが**速い**ことが**増えて**います。

| 例 | 説明 |
| --- | --- |
| **位置を深度から、再構築** | **G-Buffer に位置を、保存しない** |
| **法線を再計算** | **テクスチャの 2 成分から、3 成分目を計算** |
| **テーブルをやめる** | **LUT のメモリ読みより、数式の計算が速い**こともある（[コンパイル時の計算](../optimize/compile-time.md)） |

**計算は安く、メモリが高い**——という**GPU の性質**を、**活かします**。

<!-- fig:gbuffer-bytes:begin -->

<svg class="fig illust motion" data-fig="gbuffer-bytes" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gbuffer-bytes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">G-Buffer が 1 フレームに必要とするメモリ帯域（1920×1080、60fps）</text>
<text x="138" y="120" text-anchor="end" style="font-size:13px;font-weight:500;fill:#1f2937">アルベド</text>
<rect x="150" y="100" width="88" height="28" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></rect>
<text x="248" y="120" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4 バイト/画素<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></text>
<text x="138" y="160" text-anchor="end" style="font-size:13px;font-weight:500;fill:#1f2937">法線</text>
<rect x="150" y="140" width="88" height="28" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></rect>
<text x="248" y="160" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4 バイト/画素<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></text>
<text x="138" y="200" text-anchor="end" style="font-size:13px;font-weight:500;fill:#1f2937">材質(粗さ・金属)</text>
<rect x="150" y="180" width="88" height="28" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;1.0000" values="0;0;1;1"/></rect>
<text x="248" y="200" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4 バイト/画素<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;1.0000" values="0;0;1;1"/></text>
<text x="138" y="240" text-anchor="end" style="font-size:13px;font-weight:500;fill:#1f2937">エミッシブ</text>
<rect x="150" y="220" width="88" height="28" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></rect>
<text x="248" y="240" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4 バイト/画素<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></text>
<text x="138" y="280" text-anchor="end" style="font-size:13px;font-weight:500;fill:#1f2937">深度</text>
<rect x="150" y="260" width="88" height="28" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;1.0000" values="0;0;1;1"/></rect>
<text x="248" y="280" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4 バイト/画素<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;1.0000" values="0;0;1;1"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">画面の 1 画素あたり、各ターゲットが書き込むバイト数<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ターゲットを 1 つずつ足していく<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">合計 20 バイト/画素 × 207 万画素 = 約 41.5 MB / フレーム<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">60fps で 書き込み 約 2.5 GB/s。ライティングで読むと、合計 約 5 GB/s<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gbuffer-bytes:end -->

## よくあるミス

??? failure "G-Buffer に、RGBA32F を何枚も使う"
    **帯域が尽きます**。**フォーマットを小さく・パッキング**します。

??? failure "ポストエフェクトを、1 つずつ、フルスクリーンで行う"
    **読み書きが重なります**。**まとめる・低解像度**にします。

??? failure "深度を、わざわざ、色の RT にも書く"
    **深度バッファから、読める**ようにします（**SRV 経由**）。

??? failure "帯域が足りないのに、計算を最適化する"
    **ボトルネックが違います**。**メモリの読み書きを減らします**。

??? failure "MSAA を、Deferred で無理に使う"
    **G-Buffer がサンプル数倍**になります。**TAA などの別の手法**を検討します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>帯域 ＝ メモリと、やり取りできる速さ</strong>。<strong>描画の重さの大きな割合</strong>
    - [x] 概算は<strong>「ピクセル × バイト数 × 回数」</strong>。<strong>G-Buffer ＋ ライトごとの読み込みで、爆発</strong>
    - [x] 減らし方：<strong>フォーマット・パッキング・圧縮・低解像度・読み書きの回数</strong>
    - [x] <strong>計算は安く、メモリが高い</strong>。<strong>再計算でメモリを減らす</strong>
    - [x] <strong>Tiled・Visibility Buffer・低解像度</strong>は<strong>帯域を減らす</strong>手法

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [何が重いのか](bottlenecks.md)
- [Forward と Deferred](forward-deferred.md)
- [Tiled と Clustered](light-culling.md)
- [メモリとキャッシュ](../optimize/memory-cache.md)
