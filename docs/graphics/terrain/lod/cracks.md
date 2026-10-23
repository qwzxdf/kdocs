---
title: Cracks and Seams
tags:
  - 描画
---

# Cracks and Seams

<strong>LOD の異なる区画が隣り合うと境界で頂点が合わず隙間（クラック）ができます</strong>。境界の頂点を調整することで、隙間を埋められます。このページでは継ぎ目の原因と対策を説明します。

!!! tip "ポイント"
    - 原因 ＝ 隣の区画の頂点が、粗い側にはない。
    - 対策 1：粗い側に合わせて、細かい側の境界頂点を動かす。
    - 対策 2：境界にスカート（垂れ幕）を付ける。
    - CDLOD はモーフィングで自然に解決する。

!!! info "このページを読む前に"
    - [Terrain LOD](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:lod-cracks:begin -->

<svg class="fig illust motion" data-fig="lod-cracks" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lod-cracks" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">LOD の継ぎ目の割れ目: 粗い側と細かい側で、境の頂点の高さが食い違うと、穴が空く。細かい側を、粗い側に合わせる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。左は LOD 1(間隔 2)、右は LOD 0(間隔 1)。境(x = 8)の近くの高さを、計算して、割れ目の大きさを測る</text>
<rect x="30" y="96" width="900" height="260" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 高さ(黒 = 細かい LOD の頂点、赤い線 = 粗い LOD の辺)</text>
<path d="M60.0,259.8 L110.0,195.96 L160.0,174.65 L210.0,175.28 L260.0,231.02 L310.0,235.1 L360.0,203.12 L410.0,196.94 L460.0,228.4 L510.0,229.44 L560.0,274.97 L610.0,264.42 L660.0,242.93 L710.0,249.79 L760.0,229.36 L810.0,235.07 L860.0,253.01" fill="none" stroke="#1f2937" stroke-width="2.5"/>
<circle cx="60.0" cy="259.8" r="4" fill="#1f2937"/>
<circle cx="110.0" cy="195.96" r="4" fill="#1f2937"/>
<circle cx="160.0" cy="174.65" r="4" fill="#1f2937"/>
<circle cx="210.0" cy="175.28" r="4" fill="#1f2937"/>
<circle cx="260.0" cy="231.02" r="4" fill="#1f2937"/>
<circle cx="310.0" cy="235.1" r="4" fill="#1f2937"/>
<circle cx="360.0" cy="203.12" r="4" fill="#1f2937"/>
<circle cx="410.0" cy="196.94" r="4" fill="#1f2937"/>
<circle cx="460.0" cy="228.4" r="4" fill="#1f2937"/>
<circle cx="510.0" cy="229.44" r="4" fill="#1f2937"/>
<circle cx="560.0" cy="274.97" r="4" fill="#1f2937"/>
<circle cx="610.0" cy="264.42" r="4" fill="#1f2937"/>
<circle cx="660.0" cy="242.93" r="4" fill="#1f2937"/>
<circle cx="710.0" cy="249.79" r="4" fill="#1f2937"/>
<circle cx="760.0" cy="229.36" r="4" fill="#1f2937"/>
<circle cx="810.0" cy="235.07" r="4" fill="#1f2937"/>
<circle cx="860.0" cy="253.01" r="4" fill="#1f2937"/>
<line x1="460.0" y1="110" x2="460.0" y2="330.0" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="466.0" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">LOD の境</text>
<path d="M60.0,259.8 L85.0,238.51 L110.0,217.22 L135.0,195.94 L160.0,174.65 L185.0,188.74 L210.0,202.84 L235.0,216.93 L260.0,231.02 L285.0,224.05 L310.0,217.07 L335.0,210.1 L360.0,203.12 L385.0,209.44 L410.0,215.76 L435.0,222.08 L460.0,228.4" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1243;0.1244;1.0000" values="0;0;1;1"/><line x1="110.0" y1="195.96" x2="110.0" y2="217.22" stroke="#e5aa28" stroke-width="5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1509;0.1511;1.0000" values="0;0;1;1"/><line x1="210.0" y1="175.28" x2="210.0" y2="202.84" stroke="#e5aa28" stroke-width="5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;1.0000" values="0;0;1;1"/><line x1="310.0" y1="235.1" x2="310.0" y2="217.07" stroke="#e5aa28" stroke-width="5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2043;0.2044;1.0000" values="0;0;1;1"/><line x1="410.0" y1="196.94" x2="410.0" y2="215.76" stroke="#e5aa28" stroke-width="5"/>
</g>
<text x="70" y="134" text-anchor="start" style="font-size:13px;font-weight:700;fill:#b45309" opacity="0">オレンジ = 割れ目(同じ x で、高さが違う)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">奇数の頂点での割れ目:</text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1243;0.1244;1.0000" values="1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">59<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1243;0.1244;0.1509;0.1511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">77<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1509;0.1511;0.1776;0.1778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">50<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;0.2043;0.2044;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">52<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2043;0.2044;1.0000" values="0;0;1;1"/></text>
<text x="290" y="384" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(×0.01 m。粗い辺と、細かい頂点の高さの差)</text>
<path d="M60.0,259.8 L110.0,217.22 L160.0,174.65 L210.0,202.84 L260.0,231.02 L310.0,217.07 L360.0,203.12 L410.0,215.76 L460.0,228.4 L510.0,229.44 L560.0,274.97 L610.0,264.42 L660.0,242.93 L710.0,249.79 L760.0,229.36 L810.0,235.07 L860.0,253.01" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="0;0;1;1"/></path>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">対策: 粗い辺の上にある、細かい頂点を、粗い辺の高さへ下ろす(奇数番目を、両隣の平均にする)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="0;0;1;1"/><rect x="40" y="446" width="880" height="60" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="56" y="470" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">割れ目の最大 0.77 m → 対策後 0 m</text>
<text x="56" y="494" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">頂点の高さを、LOD 境でだけ、粗い側に合わせると、継ぎ目が閉じる(スカートで、隠す方法もある)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">LOD の異なる地形が、隣り合う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">細かい側の頂点が、粗い辺の上にないと、高さが食い違って、穴が見える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.3109;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">境の頂点を、粗い辺に載せれば、割れ目が閉じる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:lod-cracks:end -->

## 継ぎ目（クラック）
<strong>LOD の違うタイルが隣り合う</strong>と 境界で頂点の位置が合わず隙間（クラック）ができます。細かい側の境界の頂点が粗い側の辺の上にないためです。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="LOD の継ぎ目">
<text x="20" y="24" class="fig-title">LOD の継ぎ目：細かい側の頂点が、粗い側の辺から浮く</text>
<line x1="120" y1="150" x2="420" y2="150" stroke="currentColor" stroke-opacity="0.7" stroke-width="2"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="2" points="120,150 195,128 270,150 345,118 420,150"/>
<circle cx="195" cy="128" r="4" fill="#e5484d"/><circle cx="345" cy="118" r="4" fill="#e5484d"/>
<text x="120" y="190" style="font-size:12px">粗い側の辺 / 細かい側（青）の中間頂点が、辺から離れる → 隙間</text>
<line x1="500" y1="150" x2="740" y2="150" stroke="currentColor" stroke-opacity="0.7" stroke-width="2"/>
<polyline fill="none" stroke="#2ea043" stroke-width="2" points="500,150 560,150 620,150 680,150 740,150"/>
<text x="500" y="190" style="font-size:12px">対策：中間頂点を、辺の上へ寄せる</text>
</svg>

| 対策 | 内容 |
| --- | --- |
| モーフィング | 境界の頂点が粗い側の辺の上に来るまで、距離で寄せる。連続的（CDLOD はこれ） |
| スカート | タイルの縁から、下向きに垂れ幕を追加して隙間を隠す。簡単だが見た目が少し粗い |
| 境界専用のインデックス | 隣が粗いとき細かい側の境界を三角形の貼り方で繋ぐ（LOD の組み合わせごとにメッシュが要る） |
| 共通の頂点を使う | 境界の頂点の高さを両側で同じ式（粗い側の補間）で決める |
| 隣のレベル差を 1 までに制限 | 隣接するタイルの LOD の差を 1 以内にする（四分木の制約） |

## 隙間が生まれる仕組み

LOD の違うタイルが辺を共有して隣り合っているとします。細かい側には辺の途中に頂点があり粗い側には、その頂点がありません。

```text
  細かい側        境界        粗い側
   ●───●───●   ←  辺  →   ●───────●
       ↑                      （途中の頂点が無い）
   この頂点は、高さが、粗い辺から、ずれている
```

細かい側の「途中の頂点」は地形の高さを読んで、持ち上がったり下がったりしています。粗い側の辺は両端の頂点を <strong>まっすぐ結んだだけ</strong>です。両者の高さが違えばその間に 三角形 1 枚分の隙間ができます。画面では背景（空）が 1 画素ぐらいの線として見えます。

この現象を T 字型の接合部（T ジャンクション）と呼ぶこともあります。3 本の辺が T の字に出会うからです。T ジャンクションでは浮動小数点の丸め誤差も加わるので、頂点の高さが同じになるように作っても、隙間が出ることがあります。

## 対策を 1 つずつ見る

### ① スカート（垂れ幕）

タイルの縁から下向きに <strong>壁（スカート）</strong>を足します。隙間は壁の裏に隠れます。

```cpp
// 格子の周囲に、スカートの頂点を足す。
// 縁の頂点を複製して、高さだけを下げる。
struct SkirtVertex { float x, z; float skirt; };  // skirt = 0（地面）or 1（下げる）

void AddSkirt(std::vector<SkirtVertex>& vertices, std::vector<uint16_t>& indices,
              int n /* 辺の頂点数 */) {
  // 縁の頂点を並べ直して、skirt=1 の複製を作り、縁と複製の間に三角形を張る
  // （実装は、4 辺について同じ）
}
```

```hlsl
// 頂点シェーダー: skirt が 1 の頂点は、高さを一定量下げる。
float skirt_depth = node_size * 0.05;   // ノードの大きさに比例させる
float h = SampleHeight(xz) - input.skirt * skirt_depth;
```

| 長所 | 短所 |
| --- | --- |
| 実装が簡単。どの LOD の組み合わせでも使える | 壁が、ひび割れのように見えることがある（特に急な斜面と強い光） |
| 事前処理が要らない | 壁の分だけ三角形が増える |
| チャンク LOD（Ulrich 2002）が提案した定番の方法 | 影やデプスの計算に、壁が映る |

壁が見えてしまう場合は 壁の法線を隣の地面の法線と同じにする、壁のテクスチャを地面と同じ座標から引くと目立たなくなります。

### ② 境界の頂点を寄せる（ステッチング）

隣が粗いときだけ細かい側の境界の頂点を粗い側の辺の上へ動かします。動かす先は「粗い辺が通る高さ」です。

```hlsl
// 境界の、奇数番の頂点: 粗い側の辺（両隣の偶数番を結ぶ線）の高さに合わせる。
// edge_flags: 4 辺のうち、隣が粗い辺のビット
float StitchHeight(float2 grid, float h, float2 xz, float step, uint edge_flags) {
  if ((edge_flags & 1) && grid.x == 0.0 && IsOdd(grid.y)) {
    h = 0.5 * (SampleHeight(xz - float2(0, step)) + SampleHeight(xz + float2(0, step)));
  }
  // ほかの 3 辺も同様
  return h;
}
```

| 長所 | 短所 |
| --- | --- |
| 隙間がなく壁も見えない | 隣の LOD が、変わるたびにどの辺が粗いかの情報をノードごとに更新する必要がある |
| 追加の三角形がない | ポップは、残る（寄せる量が急に変わる）→ モーフィングへ進む |

### ③ 境界専用のインデックス（geomipmapping の方式）

隣が粗いときは 細かい側の境界の三角形の貼り方を変えます。奇数番の頂点を使わずに偶数番の頂点だけで、三角形を作ります。

| 隣のレベル | 必要なインデックス |
| --- | --- |
| 同じまたは細かい | 通常のインデックス |
| 粗い（辺ごとに 4 辺） | 4 辺それぞれの粗い／細かいの組み合わせ（2⁴ = 16 通り） |

LOD の組み合わせごとにインデックス バッファを用意する必要があります。頂点の位置は変えないので見た目は 1 画素の隙間もありません。

| 長所 | 短所 |
| --- | --- |
| 頂点シェーダーが単純 | 16 種類のインデックス バッファを管理する |
| 継ぎ目に余計な負荷がない | インスタンシングが、種類ごとに分かれる |

### ④ モーフィング（CDLOD の方式）

細かい側の境界頂点を 距離に応じて、連続的に粗い側の位置へ寄せます。粗いレベルの範囲に入る時点で、すべての奇数番の頂点が偶数番に重なっているので、境界の隙間は 自動的になくなります。

CDLOD はこの仕組みで継ぎ目の専用処理が、いっさい要りません。ただし、隣のノードのレベルが 2 以上違わないことが、前提です。違うとモーフィングで片方しか寄らず隙間が出ます（[Geomorphing](morphing.md)）。

### ⑤ 共通の関数で高さを決める

境界の頂点の高さを 両側のノードが、同じ関数で決める方法です。たとえば、「境界上の高さは粗い側の補間で決める」と決めれば、細かい側もその値を使えば隙間はできません。クリップマップの層の境界で使われる考え方です。

## 方式の選び方

| 状況 | おすすめ |
| --- | --- |
| まず動かしたい | スカート |
| 四分木の LOD を新しく作る | モーフィング（CDLOD） |
| 古い GPU を含むチャンク LOD | スカート ＋ チャンクごとのモーフィング |
| 高さを頂点で読まない（CPU でメッシュを作る） | 境界のステッチング、または専用インデックス |
| 水面・クリップマップ | トランジション領域（層の端で補間） |

## 隙間を見つける

見た目だけでは 1 画素の隙間は見逃します。次の方法で見つけます。

- 背景色を目立つ色（赤・マゼンタ）にして、地形を表示する。隙間が点線のように赤く光る
- ワイヤーフレームで境界を拡大する
- 地形に近づいて境界を斜めから見る

## よくあるミス

??? failure "LOD の境界に背景が見える隙間が出る"
    <strong>スカート</strong>または境界の頂点調整を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 境界の頂点を合わせるかスカートで隠す

## 参考

- Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes（チャンク LOD、スカート、ジオモーフ）
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009（CDLOD の原典。作者の公開サンプル `fstrugar/CDLOD` が GitHub にある）
- Losasso, Hoppe, "Geometry Clipmaps: Terrain Rendering Using Nested Regular Grids", ACM Transactions on Graphics (SIGGRAPH 2004)
- Lindstrom et al., "Real-Time, Continuous Level of Detail Rendering of Height Fields", SIGGRAPH 1996
- Duchaineau et al., "ROAM: Real-Time Optimally Adapting Meshes", IEEE Visualization 1997

## 関連ページ

- [Terrain LOD](index.md)
- [Geomorphing](morphing.md)
