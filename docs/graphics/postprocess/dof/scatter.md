---
title: Scatter Method
tags:
  - 描画
---

# Scatter Method

<strong>スキャッター（Scatter）</strong>は、**ギャザーの逆**で、<strong>「各画素が自分の色を、CoC の円盤として周りに広げる（散らす）」</strong>方式の DOF です。<strong>特に明るい小さな点が大きな円盤（ボケ）</strong>として**広がる様子**を**ギャザーより正確に**表現できます。**映画のような、光の玉ボケ**が**得られる**反面、**重い**ため、**使い所を絞り**ます。このページでは、<strong>ギャザーとの違い・スプライトで散らす方法・明るさの扱い・コスト・使い分け（ハイブリッド）</strong>を説明します。

!!! tip "ポイント"
    - スキャッター ＝ <strong>各画素が、自分の色を CoC の大きさの円盤として周りに足し込む</strong>。
    - <strong>ギャザー</strong>は<strong>小さなボケは得意</strong>、<strong>大きな明るいボケの形（玉ボケ）</strong>は<strong>苦手</strong>。<strong>スキャッターは玉ボケが得意</strong>。
    - 実装は<strong>画素ごとにスプライト（板ポリ）を描き、加算ブレンド</strong>。<strong>ジオメトリ数が画素数</strong>になり<strong>重い</strong>。
    - <strong>ボケが大きい（CoC が閾値以上）画素だけ</strong>を<strong>スキャッター</strong>し、<strong>残りはギャザー</strong>にする（<strong>ハイブリッド</strong>）。
    - <strong>明るさ</strong>：<strong>円盤は面積で割って、エネルギーを保存</strong>する。
    - <strong>描画順（奥から手前）</strong>が<strong>重要</strong>。

## Difference from Gather {#ギャザーとの違い}

| 項目 | ギャザー（集める） | スキャッター（散らす） |
| --- | --- | --- |
| **発想** | **自分が周りから集める** | **自分が周りへ広げる** |
| **処理の単位** | **出力画素** | <strong>入力画素（スプライト）</strong> |
| **大きな明るいボケ** | **サンプルが足りず、ざらつく・形が出にくい** | **円盤として、正確に出る** |
| **重なりの順序** | **扱いにくい** | **奥から描けば、自然** |
| **コスト** | **サンプル数 × 画素数** | <strong>画素数 × 円盤の面積（描画）</strong> |

<strong>光源が円盤として広がる「玉ボケ」</strong>は、**スキャッターがもっとも得意**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="スキャッター">
<text x="20" y="26" class="fig-title">スキャッター：明るい点が、円盤として広がる</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="200" height="160" fill="#0f172a"/>
<circle cx="60" cy="60" r="3" fill="#fff7d1"/><circle cx="140" cy="100" r="3" fill="#fff7d1"/><circle cx="90" cy="130" r="3" fill="#fff7d1"/>
<text x="0" y="182" style="font-size:12px">入力：小さな明るい点</text>
</g>
<g transform="translate(300,50)">
<rect x="0" y="0" width="200" height="160" fill="#0f172a"/>
<circle cx="60" cy="60" r="32" fill="#fff7d1" fill-opacity="0.5"/><circle cx="140" cy="100" r="26" fill="#fff7d1" fill-opacity="0.5"/><circle cx="90" cy="130" r="38" fill="#fff7d1" fill-opacity="0.4"/>
<text x="0" y="182" style="font-size:12px">スキャッター：円盤（玉ボケ）</text>
</g>
<g transform="translate(560,50)">
<rect x="0" y="0" width="200" height="160" fill="#0f172a"/>
<circle cx="60" cy="60" r="30" fill="#fff7d1" fill-opacity="0.12"/><circle cx="140" cy="100" r="24" fill="#fff7d1" fill-opacity="0.12"/><circle cx="90" cy="130" r="36" fill="#fff7d1" fill-opacity="0.1"/>
<text x="0" y="182" style="font-size:12px">ギャザー：薄くにじむだけ</text>
</g>
</svg>

## Implementation: Scattering with Sprites {#実装スプライトで散らす}

**各画素について、CoC の大きさの四角形（スプライト）を描き、円盤状のマスクで色を加算**します。

### Method 1: Geometry Shader / Mesh Shader {#方式-1ジオメトリ-シェーダーメッシュ-シェーダー}

**画素をポイントとして描き**、**ジオメトリ シェーダー（またはメッシュ シェーダー）で、CoC の大きさの四角形に拡大**します。

```hlsl
struct VSOutput {
  float4 position : SV_POSITION;
  float2 uv : TEXCOORD0;
  float3 color : COLOR0;
  float radius : TEXCOORD1;
};

[maxvertexcount(4)]
void GSMain(point VSInput input[1], inout TriangleStream<VSOutput> stream) {
  float2 center = input[0].position_ndc;
  float radius_ndc = input[0].coc_pixels * texel_ndc;
  float area = 3.14159265 * input[0].coc_pixels * input[0].coc_pixels;
  float3 color = input[0].color / max(area, 1.0);
  VSOutput v;
  v.color = color;
  v.radius = 1.0;
  float2 corners[4] = { float2(-1, -1), float2(-1, 1), float2(1, -1), float2(1, 1) };
  for (int i = 0; i < 4; ++i) {
    v.position = float4(center + corners[i] * radius_ndc, 0, 1);
    v.uv = corners[i];
    stream.Append(v);
  }
}
```

```hlsl
float4 PSMain(VSOutput input) : SV_Target {
  float distance_from_center = length(input.uv);
  float mask = saturate((1.0 - distance_from_center) * 8.0);
  return float4(input.color * mask, 0);
}
```

コードの要点です。円の面積で割るのは、エネルギー保存のためで、大きく広がっても全体の明るさは同じになります。加算ブレンド（ONE, ONE）で、円盤を重ねて足します。円盤のマスクは `length(uv) < 1` の内側だけで、縁は少し滑らかにします。

### Method 2: Tiling with Compute {#方式-2コンピュートでタイル分け}

**ボケの大きい画素だけを、コンピュートで分類してから描画**する方法もあります。**画素の数が多いので**ボケが大きい画素（CoC が閾値以上）だけ**を**スキャッター**します。

## Hybrid (the Practical Standard) {#ハイブリッド実用の標準}

**全画素をスキャッター**すると**重すぎる**ので、**使い分けます**。

全画素をスキャッターすると重すぎるので、使い分けます。ボケが小さい（CoC が数画素未満）ならギャザー、またはそのままにします。ボケが大きく（CoC がしきい値以上）、かつ明るいなら、スキャッターで玉ボケを作ります。

<strong>「明るい点」だけをスキャッター</strong>するのが**効果的**です（**暗い・平らな領域はギャザーで十分きれい**）。

<!-- fig:dof-scatter-gather:begin -->

<svg class="fig illust motion" data-fig="dof-scatter-gather" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-scatter-gather" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">スキャッター(広げる)とギャザー(集める): ぼけの半径が大きいほど、直接のスキャッターは高い。タップ数を固定したギャザーは、一定</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1920×1080。ぼける半径(画素)ごとの、1 画素あたりの処理の回数を、数えて比べる</text>
<rect x="30" y="96" width="900" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 1 画素あたり、必要な処理の回数(対数目盛)</text>
<line x1="70" y1="346.0" x2="900" y2="346.0" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="66" y="350.0" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<line x1="70" y1="286.52" x2="900" y2="286.52" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="66" y="290.52" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">10</text>
<line x1="70" y1="227.05" x2="900" y2="227.05" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="66" y="231.05" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">100</text>
<line x1="70" y1="167.57" x2="900" y2="167.57" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="66" y="171.57" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">1000</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/><rect x="90.0" y="262.86" width="54" height="83.14" fill="#e5484d" opacity="0.88"/>
<text x="117.0" y="257.86" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">25</text>
<rect x="152.0" y="262.86" width="54" height="83.14" fill="#2ea043" opacity="0.88"/>
<text x="179.0" y="257.86" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">25</text>
<text x="148.0" y="364" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">半径 2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2093;1.0000" values="0;0;1;1"/><rect x="250.0" y="232.49" width="54" height="113.51" fill="#e5484d" opacity="0.88"/>
<text x="277.0" y="227.49" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">81</text>
<rect x="312.0" y="245.47" width="54" height="100.53" fill="#2ea043" opacity="0.88"/>
<text x="339.0" y="240.47" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">49</text>
<text x="308.0" y="364" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">半径 4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3487;0.3488;1.0000" values="0;0;1;1"/><rect x="410.0" y="199.64" width="54" height="146.36" fill="#e5484d" opacity="0.88"/>
<text x="437.0" y="194.64" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">289</text>
<rect x="472.0" y="245.47" width="54" height="100.53" fill="#2ea043" opacity="0.88"/>
<text x="499.0" y="240.47" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">49</text>
<text x="468.0" y="364" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">半径 8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4882;0.4884;1.0000" values="0;0;1;1"/><rect x="570.0" y="165.37" width="54" height="180.63" fill="#e5484d" opacity="0.88"/>
<text x="597.0" y="160.37" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">1089</text>
<rect x="632.0" y="245.47" width="54" height="100.53" fill="#2ea043" opacity="0.88"/>
<text x="659.0" y="240.47" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">49</text>
<text x="628.0" y="364" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">半径 16</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6277;0.6279;1.0000" values="0;0;1;1"/><rect x="730.0" y="130.35" width="54" height="215.65" fill="#e5484d" opacity="0.88"/>
<text x="757.0" y="125.35" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">4225</text>
<rect x="792.0" y="245.47" width="54" height="100.53" fill="#2ea043" opacity="0.88"/>
<text x="819.0" y="240.47" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">49</text>
<text x="788.0" y="364" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">半径 32</text>
</g>
<circle cx="86" cy="120" r="6" fill="#e5484d"/>
<text x="96" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">広げる(円盤を全部書き込む)</text>
<circle cx="271.6" cy="120" r="6" fill="#2ea043"/>
<text x="281.6" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">集める(タップ数に上限 49)</text>
<text x="40" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画面全体の、広げる処理の書き込み(百万回):</text>
<text x="430" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0835;0.0837;1.0000" values="1;1;0;0"/></text>
<text x="430" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">51<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0835;0.0837;0.2231;0.2233;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">167<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2231;0.2233;0.3626;0.3628;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">599<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3626;0.3628;0.5021;0.5023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">2,258<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5021;0.5023;0.6417;0.6419;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">8,760<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6417;0.6419;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7673;0.7674;1.0000" values="0;0;1;1"/><rect x="40" y="436" width="880" height="80" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="460" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">半径 32 では、広げる 4,225 回 / 画素、集める(上限つき)49 回 / 画素(約 86 倍)</text>
<text x="56" y="484" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">集める方は、サンプルを減らすので、粗くなる(ノイズ・縞)。広げる方は、きれいだが重い</text>
<text x="56" y="506" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">だから、ぼけの小さい所は、集める。明るい大きなぼけだけを、広げる、という組み合わせが多い</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ぼかし方は、広げる(スキャッター)と、集める(ギャザー)の 2 通り<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ぼけが大きくなると、円盤の面積が、半径の 2 乗で増える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.7673;0.7674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">上限つきの集めは、一定のコスト。見た目とコストを、天秤にかける<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7673;0.7674;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:dof-scatter-gather:end -->

## Handling Brightness {#明るさの扱い}

**玉ボケの見た目は、元の点の「明るさ」で決まります**。**HDR の高い値（1 を超える）が、そのまま円盤に広がる**ことで、**明るい玉ボケ**が**できます**。

玉ボケの見た目は、元の点の明るさで決まります。HDR の高い値（1 を超える）が、そのまま円盤に広がるので、明るい玉ボケができます。そのため、トーンマップの前の HDR で処理します。面積で割る（エネルギー保存）ことで、広げても合計の明るさは同じになり、円盤は薄くても十分明るくなります。極端に明るい 1 点が巨大な円盤になって目立つファイアフライには、輝度のクランプを併用します。

## Cost {#コスト}

コストです。ジオメトリ数は、スキャッターする画素の数で、数万〜数十万になります。フィルレートは、円盤の面積の合計で、大きいボケの画素が多いと爆発的に増えます。対策は、スキャッターを明るい画素だけに限定する、半解像度にする、タイルごとの上限を設ける、といった方法です。

## Better Approaches {#より良いやり方}

| 工夫 | 内容 |
| --- | --- |
| **ハイブリッド** | **小さいボケはギャザー、大きく明るいボケだけスキャッター** |
| **半解像度で描く** | **フィルレートを 1/4** |
| **輝度クランプ** | **極端な点で巨大な円盤が出るのを防ぐ** |
| <strong>円盤の中を均一でなく、「縁を明るく」</strong> | **実際のレンズの玉ボケ（縁が明るい）に近づく**（[ボケの形](bokeh-shape.md)） |
| **奥から手前の順** | **前景・背景を別パス**（[前景と背景](near-far.md)） |

## Common Mistakes {#よくあるミス}

??? failure "スキャッターで、画面全体が明るくなりすぎる"
    **面積で割っていない**。**エネルギー保存**にする。

??? failure "小さな明るい点が、巨大な円盤になって目立ちすぎる"
    **輝度のクランプ**、**CoC の最大値**を下げる。

??? failure "全画素をスキャッターして、フレームが落ちる"
    **大きく明るい画素だけ**にする（**ハイブリッド**）。

??? failure "前景と背景の円盤が、正しい順序で重ならない"
    **前景・背景を別々の画像に描き、合成**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] スキャッター ＝ <strong>各画素が、色を円盤として周りに広げる</strong>
    - [x] <strong>玉ボケ</strong>（<strong>明るい大きなボケ</strong>）が<strong>得意</strong>。<strong>重い</strong>
    - [x] <strong>面積で割って</strong>エネルギー保存。<strong>加算ブレンド</strong>
    - [x] <strong>ハイブリッド</strong>（<strong>小さいボケはギャザー</strong>）が<strong>実用的</strong>
    - [x] <strong>輝度クランプ</strong>と<strong>半解像度</strong>で<strong>コスト管理</strong>

## References {#参考}

- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）
- McIntosh et al., "Efficiently Simulating the Bokeh of Polygonal Apertures in a Post-Process Depth of Field Shader"（2012）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018, DOOM）

## Related Pages {#関連ページ}

- [Depth of Field (DOF)](index.md)
- [Gather Method](gather.md)
- [Foreground and Background](near-far.md)
- [Bokeh Shape](bokeh-shape.md)
