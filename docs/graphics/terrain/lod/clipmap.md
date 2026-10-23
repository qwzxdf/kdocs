---
title: Geometry Clipmaps
tags:
  - 描画
---

# Geometry Clipmaps

<strong>クリップマップはカメラを中心に同心の格子を重ねる手法</strong>で、外側ほど粗くなります。メッシュがシンプルで四分木が要りません。このページではクリップマップの仕組みを説明します。

!!! tip "ポイント"
    - カメラ中心に入れ子の格子（リング）を並べる。
    - 外側のリングほど 2 倍の大きさ・粗さ。
    - カメラが動くと格子をずらす。
    - 高さデータも同じ入れ子で持つ。

## クリップマップ
<strong>ジオメトリ クリップマップ</strong>（Losasso & Hoppe、2004）は カメラを中心に入れ子になった正方形リングでLOD を表現します。一番内側が最も細かく外側ほど 2 倍ずつ粗くなります。

| 項目 | 内容 |
| --- | --- |
| 構造 | 同じ頂点数の正方形リングが、倍々の大きさで重なる（例：各 255×255） |
| カメラ追従 | カメラが動くとリングをグリッド単位でスクロール（円環バッファで高さを更新） |
| 利点 | 三角形の数が一定。構造が単純。GPU に向く |
| 欠点 | 視点から遠くてもリングの数だけは描く（画面外を捨てにくい）。高さデータをリングごとに管理 |
| 用途 | 広大な地形・海面（[Water Waves](../../water/waves/index.md)と同じ構造） |

四分木はノードごとにカリングができて柔軟、クリップマップは構造が単純で三角形数が一定という違いがあります。

<!-- fig:clipmap-rings:begin -->

<svg class="fig illust motion" data-fig="clipmap-rings" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-clipmap-rings" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">クリップマップ: 同じ頂点数の層を、倍々の広さで入れ子にする。頂点数は一定で、遠くまで届く</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。層ごとに、33 頂点。層 0 の間隔が 1 m、層 1 が 2 m、層 2 が 4 m、…。カメラの周りだけ、細かい</text>
<rect x="30" y="96" width="900" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">層の広がり(横 = カメラからの距離 m、対数)</text>
<line x1="60" y1="330.0" x2="900" y2="330.0" stroke="#94a3b8" stroke-width="2"/>
<circle cx="70.0" cy="330.0" r="7" fill="#1f2937"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><rect x="70.0" y="130" width="402.21" height="26" fill="#2ea043" opacity="0.8"/>
<text x="76.0" y="148" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 0: 間隔 1 m、〜 16 m</text>
<line x1="70.0" y1="156" x2="70.0" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="70.0" y1="156" x2="70.0" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="169.45" y1="156" x2="169.45" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="227.62" y1="156" x2="227.62" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="268.9" y1="156" x2="268.9" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="300.91" y1="156" x2="300.91" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="327.07" y1="156" x2="327.07" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="349.19" y1="156" x2="349.19" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="368.34" y1="156" x2="368.34" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="385.24" y1="156" x2="385.24" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="400.36" y1="156" x2="400.36" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="414.03" y1="156" x2="414.03" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="426.52" y1="156" x2="426.52" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="438.0" y1="156" x2="438.0" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="448.63" y1="156" x2="448.63" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="458.53" y1="156" x2="458.53" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="467.79" y1="156" x2="467.79" y2="162" stroke="#2ea043" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2176;0.2178;1.0000" values="0;0;1;1"/><rect x="70.0" y="166" width="501.66" height="26" fill="#2563eb" opacity="0.8"/>
<text x="76.0" y="184" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 1: 間隔 2 m、〜 33 m</text>
<line x1="70.0" y1="192" x2="70.0" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="169.45" y1="192" x2="169.45" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.9" y1="192" x2="268.9" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="327.07" y1="192" x2="327.07" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="368.34" y1="192" x2="368.34" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="400.36" y1="192" x2="400.36" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="426.52" y1="192" x2="426.52" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="448.63" y1="192" x2="448.63" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="467.79" y1="192" x2="467.79" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="484.69" y1="192" x2="484.69" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="499.81" y1="192" x2="499.81" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="513.48" y1="192" x2="513.48" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="525.97" y1="192" x2="525.97" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="537.45" y1="192" x2="537.45" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="548.08" y1="192" x2="548.08" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="557.98" y1="192" x2="557.98" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="567.24" y1="192" x2="567.24" y2="198" stroke="#2563eb" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3687;0.3689;1.0000" values="0;0;1;1"/><rect x="70.0" y="202" width="601.1" height="26" fill="#e5aa28" opacity="0.8"/>
<text x="76.0" y="220" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 2: 間隔 4 m、〜 66 m</text>
<line x1="70.0" y1="228" x2="70.0" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="268.9" y1="228" x2="268.9" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="368.34" y1="228" x2="368.34" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="426.52" y1="228" x2="426.52" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="467.79" y1="228" x2="467.79" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="499.81" y1="228" x2="499.81" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="525.97" y1="228" x2="525.97" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="548.08" y1="228" x2="548.08" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="567.24" y1="228" x2="567.24" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="584.14" y1="228" x2="584.14" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="599.26" y1="228" x2="599.26" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="612.93" y1="228" x2="612.93" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="625.41" y1="228" x2="625.41" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="636.9" y1="228" x2="636.9" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="647.53" y1="228" x2="647.53" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="657.43" y1="228" x2="657.43" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="666.69" y1="228" x2="666.69" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5198;0.5200;1.0000" values="0;0;1;1"/><rect x="70.0" y="238" width="700.55" height="26" fill="#e5484d" opacity="0.8"/>
<text x="76.0" y="256" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 3: 間隔 8 m、〜 132 m</text>
<line x1="70.0" y1="264" x2="70.0" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="368.34" y1="264" x2="368.34" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="467.79" y1="264" x2="467.79" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="525.97" y1="264" x2="525.97" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="567.24" y1="264" x2="567.24" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="599.26" y1="264" x2="599.26" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="625.41" y1="264" x2="625.41" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="647.53" y1="264" x2="647.53" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="666.69" y1="264" x2="666.69" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="683.59" y1="264" x2="683.59" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="698.7" y1="264" x2="698.7" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="712.38" y1="264" x2="712.38" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="724.86" y1="264" x2="724.86" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="736.35" y1="264" x2="736.35" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="746.98" y1="264" x2="746.98" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="756.88" y1="264" x2="756.88" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="766.14" y1="264" x2="766.14" y2="270" stroke="#e5484d" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6709;0.6711;1.0000" values="0;0;1;1"/><rect x="70.0" y="274" width="800.0" height="26" fill="#7c3aed" opacity="0.8"/>
<text x="76.0" y="292" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 4: 間隔 16 m、〜 264 m</text>
<line x1="70.0" y1="300" x2="70.0" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="467.79" y1="300" x2="467.79" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="567.24" y1="300" x2="567.24" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="625.41" y1="300" x2="625.41" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="666.69" y1="300" x2="666.69" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="698.7" y1="300" x2="698.7" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="724.86" y1="300" x2="724.86" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="746.98" y1="300" x2="746.98" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="766.14" y1="300" x2="766.14" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="783.04" y1="300" x2="783.04" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="798.15" y1="300" x2="798.15" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="811.83" y1="300" x2="811.83" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="824.31" y1="300" x2="824.31" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="835.79" y1="300" x2="835.79" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="846.43" y1="300" x2="846.43" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="856.33" y1="300" x2="856.33" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="865.59" y1="300" x2="865.59" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
</g>
<text x="40" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">頂点の数(層ごとに 33×33):</text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1,089<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2176;0.2178;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">2,178<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2176;0.2178;0.3687;0.3689;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3,267<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3687;0.3689;0.5198;0.5200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4,356<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5198;0.5200;0.6709;0.6711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">5,445<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6709;0.6711;1.0000" values="0;0;1;1"/></text>
<text x="40" y="436" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">同じ範囲を、全部 1 m 間隔で作ると:</text>
<text x="330" y="436" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">278,784 頂点(約 51 倍)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8220;0.8222;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000" values="0;0;1;1"/><rect x="40" y="456" width="880" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="480" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">5 層 5,445 頂点で、半径 264 m まで届く。近く(1 m 間隔)から、遠く(16 m 間隔)まで、頂点数は一定</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くの地形を、近くと同じ細かさで描くのは、無駄<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">層を足すごとに、広さが 2 倍、間隔も 2 倍になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8665;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが動くと、層ごとに、動く単位(間隔)ぶんだけ、ずらして、追いかける<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:clipmap-rings:end -->

## 論文の考え方

Losasso と Hoppe の方式は、<strong>「見える範囲の地形を画面の解像度で必要な分だけ持つ」</strong>という発想から来ています。画面に映る範囲は近くが細かく、遠くが粗くてよいので同じ頂点数の格子を 倍々の大きさで、入れ子にします。

| 層 | 格子の間隔 | 覆う範囲 |
| --- | --- | --- |
| レベル 0 | 1 m | 255 m 四方（中心はカメラ） |
| レベル 1 | 2 m | 510 m 四方 |
| レベル 2 | 4 m | 1,020 m 四方 |
| レベル 3 | 8 m | 2,040 m 四方 |
| … | 倍々 | 倍々 |

どの層も 255 × 255 頂点（とは限りません。2 のべき乗に近い同じ頂点数）です。層の数を 1 つ増やすたびに覆う範囲は 2 倍になりますが、三角形の数は層 1 つ分しか増えません。10 層あれば約 260 km 四方を数十万個ほどの三角形で覆えます。

### 論文のもう 1 つの柱：データの供給

クリップマップは描画の仕組みだけでなく、巨大な高さデータの置き方も提案しています。高さのデータは全部でテラバイト級になることもありメモリに載りません。そこで、層ごとにカメラの周りだけをメモリ上の正方形の窓として持つようにします。

| 項目 | 内容 |
| --- | --- |
| メモリ上の窓 | 層ごとに正方形の高さデータ（例：255×255）を持つ |
| カメラが動くと | 窓を動かして、新しく視界に入る帯の部分だけをディスクから読む |
| 窓の置き方 | 円環バッファ（トロイダル アドレッシング）。窓の端を超えたら反対側から使い直す |
| 圧縮 | 層をまたぐ高さの違い（残差）だけを圧縮して持つ |

円環バッファは窓全体をずらしてコピーせず 書き込み位置だけをずらすやり方です。テクスチャでは `WRAP` の アドレッシング モードで、端を超えた座標が反対側に戻るので、実現が簡単です。

```hlsl
// 層ごとの高さテクスチャを、円環バッファとして読む。
// clip_origin: この層の窓の左下が、ワールドのどのセルにあたるか（整数のセル）
float SampleClipHeight(Texture2D<float> tex, float2 world_xz, float cell_size) {
  float2 cell = world_xz / cell_size;
  // WRAP サンプラーなので、窓の外へ出ても、反対側から読まれる。
  float2 uv = cell / kClipSize;
  return tex.SampleLevel(g_linear_wrap, uv, 0);
}
```

窓を動かすときは 新しく見える帯の部分だけを `UpdateSubresource` やステージング テクスチャのコピーで書き換えます。窓を動かす単位は その層の格子の間隔の倍数（できれば 2 倍の間隔）に揃えます。そうしないと層の格子がカメラの動きに合わせてなめらかに動いて、地形が泳いで見えます。

## 論文を GPU で動かす（Asirvatham と Hoppe）

2004 年の論文は CPU でメッシュを組み立てる方式でした。翌年の GPU Gems 2 で、<strong>GPU の頂点シェーダーで動く形</strong>に作り直されています。

| 項目 | 2004（原型） | 2005（GPU 版） |
| --- | --- | --- |
| 高さの置き場所 | CPU のメモリ上の頂点バッファ | 頂点テクスチャ（頂点シェーダーで読む） |
| メッシュ | 毎フレーム、CPU で作る | 静的な頂点バッファを使い回す |
| 層の形 | 正方形のリング | 同じ形のブロックに分割して、描き分ける |
| 視錐台カリング | 層ごと | ブロックごと |
| 法線 | 頂点に持つ | 別の法線マップとして、層ごとに持つ |

### 層を同じブロックに分ける

層の格子はカメラの周りに 輪（リング）の形で置かれます。内側の層がその輪の穴を埋めています。これを同じ形の小さな正方形（ブロック）に分けて、ブロック 1 種類のメッシュを位置だけ変えて並べます。

| 部品 | 数（1 層あたり） | 役割 |
| --- | --- | --- |
| ブロック（m×m） | 12 個 | 輪の本体 |
| 輪の内側の縁（インテリア トリム） | 4 個 | 層の内側のずれを調整する細い帯 |
| 継ぎ目（フィックスアップ） | 1 個 | 隣の層との隙間を埋める細い帯 |
| 縮退三角形のリング | 1 個 | 内側と外側の頂点数の違いを吸収する |

細かい仕組みは多いですがここでは「1 種類のブロックを決まった配置で並べるだけで、輪ができる」と覚えてください。実際の配置は、論文と実装の例（Asirvatham の記事）を見ながら作ります。

!!! note "そのまま使うならまず「1 層 = 正方形 1 枚の格子」から"
    初めて作るときは論文のブロック分割をそのまま真似なくてかまいません。層ごとに同じ頂点数の正方形の格子（穴あき）を 1 枚用意して `DrawIndexedInstanced` で、層の数だけ描く形から始めると、仕組みが追いやすくなります。

## 層の間のつなぎ目をどうするか

内側の層と外側の層は格子の間隔が 2 倍違います。この境目に <strong>頂点がずれた隙間</strong>ができます。論文では 境界の近くで頂点の高さを外側の層の高さと少しずつ補間する（トランジション領域）ことで、隙間を消します。

```hlsl
// 層の端に近づくほど、高さを、外側の粗い層の高さへ寄せる。
float BlendHeight(float2 world_xz, float fine_h, float coarse_h, float2 clip_center,
                  float half_extent, float blend_width) {
  float2 d = abs(world_xz - clip_center);
  float edge_dist = max(d.x, d.y);   // 正方形の中心からの距離（最大値ノルム）
  float t = saturate((edge_dist - (half_extent - blend_width)) / blend_width);
  return lerp(fine_h, coarse_h, t);
}
```

これは CDLOD のモーフィングと同じ考え方です。違うのは 寄せる基準がカメラまでの距離ではなく、層の端までの距離であることです。

## クリップマップと CDLOD をどう選ぶか

| 観点 | クリップマップ | CDLOD |
| --- | --- | --- |
| 三角形の数 | ほぼ一定（層の数 × 1 層ぶん） | カメラの位置や、地形の起伏で変わる |
| 描く範囲の選び方 | カメラ中心の入れ子。カメラが動くたび窓を動かす | 四分木で、必要な部分だけを選ぶ |
| 視錐台カリング | ブロック単位でできる。ただし、後ろ側の層も一部が残る | ノード単位で、細かく捨てられる |
| 高さデータの置き方 | 窓（円環バッファ）。超巨大な地形で強い | 通常のテクスチャでよい。巨大地形は別途ストリーミング |
| 実装の複雑さ | 継ぎ目の処理（ブロック、トリム）が複雑 | 四分木とモーフィングだけ。単純 |
| 向く用途 | 海面（FFT 海）、巨大な地球規模の地形、フライト シミュレーター | 一般的なゲームの地形（数 km〜数十 km） |

水面はクリップマップがよく使われます。カメラの周りだけ細かく遠くは粗くてよいという性質が、そのまま合うからです（[Water Waves](../../water/waves/index.md)）。

## よくあるミス

??? failure "カメラの移動で、地形が揺れる"
    <strong>格子の幅の整数倍で移動</strong>して、スナップする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カメラ中心の入れ子の格子

## 参考

- Losasso, Hoppe, "Geometry Clipmaps: Terrain Rendering Using Nested Regular Grids", ACM Transactions on Graphics (SIGGRAPH 2004)
- Asirvatham, Hoppe, "Terrain Rendering Using GPU-Based Geometry Clipmaps", GPU Gems 2, Chapter 2, 2005
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009（CDLOD の原典。作者の公開サンプル `fstrugar/CDLOD` が GitHub にある）
- Tanner, Migdal, Jones, "The Clipmap: A Virtual Mipmap", SIGGRAPH 1998（クリップマップという名前と、窓として持つ考え方の原点。地形ではなくテクスチャの話）

## 関連ページ

- [Terrain LOD](index.md)
- [CDLOD](cdlod.md)
