---
title: Hi-Z SSR
tags:
  - 描画
---

# Hi-Z SSR

[SSR の基礎](ssr-basics/index.md)の線形マーチ（1 ピクセルずつ進む）は、<strong>遠くまで進むとステップが何十〜何百回</strong>にもなり、<strong>重く</strong>なります。Hi-Z SSRは、<strong>階層的な深度バッファ（Hi-Z）</strong>を使って、空いている領域を一気に飛ばすことで、少ないステップで遠くまでレイを進めます。粗い反射・長いレイ・精度の高い当たり判定が要る、現在の主流の方式です。このページでは、Hi-Z の作り方・探索のアルゴリズム・精度の工夫を順に説明します。

!!! tip "ポイント"
    - <strong>Hi-Z</strong> ＝ <strong>各セルが、「その範囲で最も手前の深度（最小）」を持つミップ チェーン</strong>。
    - レイを進めるとき、<strong>粗いミップで大きなセルごとに</strong>、<strong>「レイはこのセルの中のどの面よりも手前にいる」</strong>なら、<strong>セルの端まで一気に飛ばす</strong>。
    - 当たりそうな所では、<strong>ミップを下りて、細かく</strong>確かめる。
    - 画面空間では、<strong>レイは、(x, y, 深度) の空間で直線</strong>。<strong>深度（z/w）は、画面上で線形</strong>なので計算が簡単。
    - <strong>ステップ数が距離に依存せず、数十回に収まる</strong>。
    - 終盤に<strong>厚み（thickness）の検証</strong>が必要。

## なぜ速くなるか

線形マーチは<strong>空いている空間でも、1 ピクセルずつ</strong>進みます。<strong>レイの周りに何も遮る物がない</strong>と分かれば、一気に進めるはずです。

<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="Hi-Z でレイを飛ばす">
<text x="20" y="24" class="fig-title">粗いミップ（大きなセル）で、空いている領域を一気に飛ばし、近づいたら細かいミップへ下りる</text>
<line x1="60" y1="240" x2="720" y2="240" stroke="currentColor" stroke-width="2"/>
<g stroke="currentColor" stroke-width="1" fill="rgba(76,139,245,0.15)"><rect x="60" y="150" width="160" height="90"/><rect x="220" y="150" width="160" height="90"/><rect x="380" y="100" width="160" height="140"/><rect x="540" y="150" width="180" height="90"/></g>
<text x="64" y="144" style="font-size:12px">セルの「最小深度」（最も手前の面）</text>
<polyline points="80,60 220,100 380,140" fill="none" stroke="#e5484d" stroke-width="3"/>
<g fill="#e5484d"><circle cx="80" cy="60" r="5"/><circle cx="220" cy="100" r="5"/><circle cx="380" cy="140" r="5"/></g>
<text x="90" y="52" style="font-size:12px;fill:#e5484d;font-weight:700">大きなセルを、1 ステップで飛ばす</text>
<polyline points="380,140 420,155 460,170 480,182" fill="none" stroke="#2ea043" stroke-width="3"/>
<g fill="#2ea043"><circle cx="420" cy="155" r="4"/><circle cx="460" cy="170" r="4"/><circle cx="480" cy="182" r="4"/></g>
<text x="400" y="272" style="font-size:12px;fill:#2ea043;font-weight:700">近づいたら、細かいセルで確かめる</text>
</svg>

線形マーチのステップ数は、距離（ピクセル）に比例し、数百回に及ぶことがあります。Hi-Z は<strong>距離の対数</strong>に比例する数十回で済みます。空いている所は一気に飛べるからです。この違いは、特に遠くまで届く反射（長いレイ）で効いてきます。

## Hi-Z の作り方

<strong>深度バッファから、ミップ チェーン</strong>を作ります。<strong>各ミップの 1 画素は、下のミップの 2×2 画素の「最小」</strong>（最も手前＝<strong>標準 Z では最小値</strong>）です。

<div class="formula">HiZ[level + 1](x, y) = min( HiZ[level](2x, 2y), HiZ[level](2x+1, 2y), HiZ[level](2x, 2y+1), HiZ[level](2x+1, 2y+1) )</div>

| 点 | 説明 |
| --- | --- |
| <strong>最小（最も手前）</strong> | 「このセルの中で最も手前の面」の深度。これより手前にいるレイは、このセルの中のどの面にも当たらない |
| reverse-Z | 深度が反転しているので、最大値を取る |
| 平均ではない | [SAO (Scalable AO)](../ao/sao.md)は、境界の嘘の深度を避けるための選択でしたが、Hi-Z は保守的な判定のため、<strong>最小（または最大）</strong>が正しい |
| 非 2 の冪の画面 | 端の画素を取りこぼさない（切り上げ） |
| 作成コスト | <strong>コンピュート 1 回（複数ミップをグループ内で一度に）</strong>で、0.1〜0.3 ms 程度 |

```hlsl
float HiZMin(Texture2D<float> src, int2 pixel) {
  float a = src.Load(int3(pixel * 2 + int2(0, 0), 0));
  float b = src.Load(int3(pixel * 2 + int2(1, 0), 0));
  float c = src.Load(int3(pixel * 2 + int2(0, 1), 0));
  float d = src.Load(int3(pixel * 2 + int2(1, 1), 0));
  return min(min(a, b), min(c, d));
}
```

## 画面空間でのレイ

Hi-Z の探索は、<strong>ビュー空間ではなく、(画面 x, 画面 y, 深度) の空間</strong>で行います。<strong>透視投影の性質</strong>：画面上の直線は、ビュー空間の直線であり、非線形深度 z/w（NDC の z）も、画面上で線形に変化します。つまり、レイは (x, y, z_ndc) の空間で直線です。

ビュー空間では、レイは直線ですが、画面上の歩幅が不均一になります。(画面 xy, NDC の z) の空間では、レイは直線で、均一に補間できます。Hi-Z のトレースは、後者の空間で行うと扱いやすくなります。

```hlsl
float3 origin_ss = float3(uv0, ndc_z0);
float3 end_ss = float3(uv1, ndc_z1);
float3 dir_ss = end_ss - origin_ss;
```

<strong>始点と終点をそれぞれ射影して</strong>画面空間に変換し、その間を直線で結びます（`uv` は 0〜1、`ndc_z` は深度バッファの値と同じ）。<strong>深度バッファの値と直接比べられる</strong>のが利点です。

<!-- fig:ssr-hiz-steps:begin -->

<svg class="fig illust motion" data-fig="ssr-hiz-steps" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssr-hiz-steps" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">SSR の光線追跡: 1 マスずつ進める方法と、Hi-Z で大きく飛ばす方法</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">同じ深度、同じ光線。当たる場所が同じでも、深度バッファを読む回数は大きく違う</text>
<rect x="30" y="96.0" width="900" height="150" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="86.0" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">線形に追跡(1 マスずつ)</text>
<polygon points="50.0,240.0 50.0,217.0 63.0,217.0 63.0,217.0 76.0,217.0 76.0,217.0 89.0,217.0 89.0,217.0 102.0,217.0 102.0,217.0 115.0,217.0 115.0,217.0 128.0,217.0 128.0,217.0 141.0,217.0 141.0,217.0 154.0,217.0 154.0,217.0 167.0,217.0 167.0,217.0 180.0,217.0 180.0,217.0 193.0,217.0 193.0,217.0 206.0,217.0 206.0,217.0 219.0,217.0 219.0,217.0 232.0,217.0 232.0,159.8 245.0,159.8 245.0,159.8 258.0,159.8 258.0,159.8 271.0,159.8 271.0,159.8 284.0,159.8 284.0,217.0 297.0,217.0 297.0,217.0 310.0,217.0 310.0,217.0 323.0,217.0 323.0,217.0 336.0,217.0 336.0,217.0 349.0,217.0 349.0,217.0 362.0,217.0 362.0,217.0 375.0,217.0 375.0,217.0 388.0,217.0 388.0,217.0 401.0,217.0 401.0,217.0 414.0,217.0 414.0,217.0 427.0,217.0 427.0,217.0 440.0,217.0 440.0,170.2 453.0,170.2 453.0,170.2 466.0,170.2 466.0,170.2 479.0,170.2 479.0,217.0 492.0,217.0 492.0,217.0 505.0,217.0 505.0,217.0 518.0,217.0 518.0,217.0 531.0,217.0 531.0,217.0 544.0,217.0 544.0,217.0 557.0,217.0 557.0,217.0 570.0,217.0 570.0,217.0 583.0,217.0 583.0,217.0 596.0,217.0 596.0,217.0 609.0,217.0 609.0,217.0 622.0,217.0 622.0,217.0 635.0,217.0 635.0,217.0 648.0,217.0 648.0,217.0 661.0,217.0 661.0,217.0 674.0,217.0 674.0,217.0 687.0,217.0 687.0,217.0 700.0,217.0 700.0,217.0 713.0,217.0 713.0,217.0 726.0,217.0 726.0,133.8 739.0,133.8 739.0,133.8 752.0,133.8 752.0,133.8 765.0,133.8 765.0,133.8 778.0,133.8 778.0,133.8 791.0,133.8 791.0,133.8 804.0,133.8 804.0,133.8 817.0,133.8 817.0,133.8 830.0,133.8 830.0,133.8 843.0,133.8 843.0,133.8 856.0,133.8 856.0,133.8 869.0,133.8 869.0,133.8 882.0,133.8 882.0,240.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="76.0" y1="113.0" x2="882.0" y2="141.21" stroke="#fca5a5" stroke-width="2" stroke-dasharray="6 5"/>
<circle cx="76.0" cy="113.0" r="6" fill="#1f2937"/>
<text x="84.0" y="105.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">光線の出発点</text>
<rect x="30" y="284.0" width="900" height="150" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="274.0" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">Hi-Z で追跡(深度の最小値のミップで飛ばす)</text>
<polygon points="50.0,428.0 50.0,405.0 63.0,405.0 63.0,405.0 76.0,405.0 76.0,405.0 89.0,405.0 89.0,405.0 102.0,405.0 102.0,405.0 115.0,405.0 115.0,405.0 128.0,405.0 128.0,405.0 141.0,405.0 141.0,405.0 154.0,405.0 154.0,405.0 167.0,405.0 167.0,405.0 180.0,405.0 180.0,405.0 193.0,405.0 193.0,405.0 206.0,405.0 206.0,405.0 219.0,405.0 219.0,405.0 232.0,405.0 232.0,347.8 245.0,347.8 245.0,347.8 258.0,347.8 258.0,347.8 271.0,347.8 271.0,347.8 284.0,347.8 284.0,405.0 297.0,405.0 297.0,405.0 310.0,405.0 310.0,405.0 323.0,405.0 323.0,405.0 336.0,405.0 336.0,405.0 349.0,405.0 349.0,405.0 362.0,405.0 362.0,405.0 375.0,405.0 375.0,405.0 388.0,405.0 388.0,405.0 401.0,405.0 401.0,405.0 414.0,405.0 414.0,405.0 427.0,405.0 427.0,405.0 440.0,405.0 440.0,358.2 453.0,358.2 453.0,358.2 466.0,358.2 466.0,358.2 479.0,358.2 479.0,405.0 492.0,405.0 492.0,405.0 505.0,405.0 505.0,405.0 518.0,405.0 518.0,405.0 531.0,405.0 531.0,405.0 544.0,405.0 544.0,405.0 557.0,405.0 557.0,405.0 570.0,405.0 570.0,405.0 583.0,405.0 583.0,405.0 596.0,405.0 596.0,405.0 609.0,405.0 609.0,405.0 622.0,405.0 622.0,405.0 635.0,405.0 635.0,405.0 648.0,405.0 648.0,405.0 661.0,405.0 661.0,405.0 674.0,405.0 674.0,405.0 687.0,405.0 687.0,405.0 700.0,405.0 700.0,405.0 713.0,405.0 713.0,405.0 726.0,405.0 726.0,321.8 739.0,321.8 739.0,321.8 752.0,321.8 752.0,321.8 765.0,321.8 765.0,321.8 778.0,321.8 778.0,321.8 791.0,321.8 791.0,321.8 804.0,321.8 804.0,321.8 817.0,321.8 817.0,321.8 830.0,321.8 830.0,321.8 843.0,321.8 843.0,321.8 856.0,321.8 856.0,321.8 869.0,321.8 869.0,321.8 882.0,321.8 882.0,428.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="76.0" y1="301.0" x2="882.0" y2="329.21" stroke="#fca5a5" stroke-width="2" stroke-dasharray="6 5"/>
<circle cx="76.0" cy="301.0" r="6" fill="#1f2937"/>
<text x="84.0" y="293.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">光線の出発点</text>
<circle cx="82.5" cy="113.23" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></circle>
<circle cx="95.5" cy="113.68" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0697;0.0700;1.0000" values="0;0;1;1"/></circle>
<circle cx="108.5" cy="114.14" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0752;0.0755;1.0000" values="0;0;1;1"/></circle>
<circle cx="121.5" cy="114.59" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0807;0.0810;1.0000" values="0;0;1;1"/></circle>
<circle cx="134.5" cy="115.05" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0862;0.0865;1.0000" values="0;0;1;1"/></circle>
<circle cx="147.5" cy="115.5" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0917;0.0919;1.0000" values="0;0;1;1"/></circle>
<circle cx="160.5" cy="115.96" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0972;0.0974;1.0000" values="0;0;1;1"/></circle>
<circle cx="173.5" cy="116.41" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;1.0000" values="0;0;1;1"/></circle>
<circle cx="186.5" cy="116.87" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1081;0.1084;1.0000" values="0;0;1;1"/></circle>
<circle cx="199.5" cy="117.32" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1136;0.1139;1.0000" values="0;0;1;1"/></circle>
<circle cx="212.5" cy="117.78" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1191;0.1194;1.0000" values="0;0;1;1"/></circle>
<circle cx="225.5" cy="118.23" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1246;0.1248;1.0000" values="0;0;1;1"/></circle>
<circle cx="238.5" cy="118.69" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1303;1.0000" values="0;0;1;1"/></circle>
<circle cx="251.5" cy="119.14" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1355;0.1358;1.0000" values="0;0;1;1"/></circle>
<circle cx="264.5" cy="119.6" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1410;0.1413;1.0000" values="0;0;1;1"/></circle>
<circle cx="277.5" cy="120.05" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1465;0.1468;1.0000" values="0;0;1;1"/></circle>
<circle cx="290.5" cy="120.51" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1520;0.1523;1.0000" values="0;0;1;1"/></circle>
<circle cx="303.5" cy="120.96" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1575;0.1577;1.0000" values="0;0;1;1"/></circle>
<circle cx="316.5" cy="121.42" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1630;0.1632;1.0000" values="0;0;1;1"/></circle>
<circle cx="329.5" cy="121.87" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1685;0.1687;1.0000" values="0;0;1;1"/></circle>
<circle cx="342.5" cy="122.33" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1739;0.1742;1.0000" values="0;0;1;1"/></circle>
<circle cx="355.5" cy="122.78" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1794;0.1797;1.0000" values="0;0;1;1"/></circle>
<circle cx="368.5" cy="123.24" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1852;1.0000" values="0;0;1;1"/></circle>
<circle cx="381.5" cy="123.69" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1904;0.1906;1.0000" values="0;0;1;1"/></circle>
<circle cx="394.5" cy="124.15" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1959;0.1961;1.0000" values="0;0;1;1"/></circle>
<circle cx="407.5" cy="124.6" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2014;0.2016;1.0000" values="0;0;1;1"/></circle>
<circle cx="420.5" cy="125.06" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2068;0.2071;1.0000" values="0;0;1;1"/></circle>
<circle cx="433.5" cy="125.51" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;1.0000" values="0;0;1;1"/></circle>
<circle cx="446.5" cy="125.97" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2178;0.2181;1.0000" values="0;0;1;1"/></circle>
<circle cx="459.5" cy="126.42" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2233;0.2235;1.0000" values="0;0;1;1"/></circle>
<circle cx="472.5" cy="126.88" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2288;0.2290;1.0000" values="0;0;1;1"/></circle>
<circle cx="485.5" cy="127.33" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2343;0.2345;1.0000" values="0;0;1;1"/></circle>
<circle cx="498.5" cy="127.79" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2397;0.2400;1.0000" values="0;0;1;1"/></circle>
<circle cx="511.5" cy="128.24" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2452;0.2455;1.0000" values="0;0;1;1"/></circle>
<circle cx="524.5" cy="128.7" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2507;0.2510;1.0000" values="0;0;1;1"/></circle>
<circle cx="537.5" cy="129.15" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2562;0.2565;1.0000" values="0;0;1;1"/></circle>
<circle cx="550.5" cy="129.61" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2617;0.2619;1.0000" values="0;0;1;1"/></circle>
<circle cx="563.5" cy="130.06" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2672;0.2674;1.0000" values="0;0;1;1"/></circle>
<circle cx="576.5" cy="130.52" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2726;0.2729;1.0000" values="0;0;1;1"/></circle>
<circle cx="589.5" cy="130.97" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2781;0.2784;1.0000" values="0;0;1;1"/></circle>
<circle cx="602.5" cy="131.43" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2836;0.2839;1.0000" values="0;0;1;1"/></circle>
<circle cx="615.5" cy="131.88" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2891;0.2894;1.0000" values="0;0;1;1"/></circle>
<circle cx="628.5" cy="132.34" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2946;0.2948;1.0000" values="0;0;1;1"/></circle>
<circle cx="641.5" cy="132.79" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3001;0.3003;1.0000" values="0;0;1;1"/></circle>
<circle cx="654.5" cy="133.25" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3055;0.3058;1.0000" values="0;0;1;1"/></circle>
<circle cx="667.5" cy="133.7" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3110;0.3113;1.0000" values="0;0;1;1"/></circle>
<circle cx="680.5" cy="134.16" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3165;0.3168;1.0000" values="0;0;1;1"/></circle>
<circle cx="693.5" cy="134.61" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3220;0.3223;1.0000" values="0;0;1;1"/></circle>
<circle cx="706.5" cy="135.07" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3275;0.3277;1.0000" values="0;0;1;1"/></circle>
<circle cx="719.5" cy="135.52" r="3.5" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3332;1.0000" values="0;0;1;1"/></circle>
<circle cx="732.5" cy="135.98" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3385;0.3387;1.0000" values="0;0;1;1"/></circle>
<text x="500" y="84" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">深度の読み込み:</text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.0697;0.0700;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0697;0.0700;0.0752;0.0755;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0752;0.0755;0.0807;0.0810;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0807;0.0810;0.0862;0.0865;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0862;0.0865;0.0917;0.0919;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0917;0.0919;0.0972;0.0974;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0972;0.0974;0.1026;0.1029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;0.1081;0.1084;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1081;0.1084;0.1136;0.1139;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1136;0.1139;0.1191;0.1194;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1191;0.1194;0.1246;0.1248;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1246;0.1248;0.1301;0.1303;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1303;0.1355;0.1358;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1355;0.1358;0.1410;0.1413;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1410;0.1413;0.1465;0.1468;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1465;0.1468;0.1520;0.1523;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">17<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1520;0.1523;0.1575;0.1577;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">18<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1575;0.1577;0.1630;0.1632;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">19<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1630;0.1632;0.1685;0.1687;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1685;0.1687;0.1739;0.1742;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">21<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1739;0.1742;0.1794;0.1797;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">22<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1794;0.1797;0.1849;0.1852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">23<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1852;0.1904;0.1906;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1904;0.1906;0.1959;0.1961;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">25<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1959;0.1961;0.2014;0.2016;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">26<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2014;0.2016;0.2068;0.2071;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">27<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2068;0.2071;0.2123;0.2126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;0.2178;0.2181;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">29<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2178;0.2181;0.2233;0.2235;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">30<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2233;0.2235;0.2288;0.2290;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">31<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2288;0.2290;0.2343;0.2345;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">32<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2343;0.2345;0.2397;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">33<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2397;0.2400;0.2452;0.2455;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">34<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2452;0.2455;0.2507;0.2510;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">35<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2507;0.2510;0.2562;0.2565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">36<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2562;0.2565;0.2617;0.2619;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">37<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2617;0.2619;0.2672;0.2674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">38<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2672;0.2674;0.2726;0.2729;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">39<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2726;0.2729;0.2781;0.2784;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">40<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2781;0.2784;0.2836;0.2839;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">41<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2836;0.2839;0.2891;0.2894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">42<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2891;0.2894;0.2946;0.2948;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">43<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2946;0.2948;0.3001;0.3003;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">44<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3001;0.3003;0.3055;0.3058;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">45<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3055;0.3058;0.3110;0.3113;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">46<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3110;0.3113;0.3165;0.3168;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">47<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3165;0.3168;0.3220;0.3223;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">48<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3220;0.3223;0.3275;0.3277;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">49<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3275;0.3277;0.3330;0.3332;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">50<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3332;0.3385;0.3387;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="86" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">51<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3385;0.3387;1.0000" values="0;0;1;1"/></text>
<rect x="76.0" y="288.0" width="13.0" height="140" fill="#22c55e" fill-opacity="0.18" stroke="#22c55e" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></rect>
<text x="82.5" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#22c55e" opacity="0">L0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></text>
<circle cx="89.0" cy="301.45" r="4" fill="#22c55e" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></circle>
<rect x="76.0" y="288.0" width="26.0" height="140" fill="#3b82f6" fill-opacity="0.18" stroke="#3b82f6" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0997;0.1000;1.0000" values="0;0;1;1"/></rect>
<text x="89.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#3b82f6" opacity="0">L1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0997;0.1000;1.0000" values="0;0;1;1"/></text>
<circle cx="102.0" cy="301.91" r="4" fill="#3b82f6" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0997;0.1000;1.0000" values="0;0;1;1"/></circle>
<rect x="102.0" y="288.0" width="52.0" height="140" fill="#a855f7" fill-opacity="0.18" stroke="#a855f7" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1352;0.1355;1.0000" values="0;0;1;1"/></rect>
<text x="128.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#a855f7" opacity="0">L2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1352;0.1355;1.0000" values="0;0;1;1"/></text>
<circle cx="154.0" cy="303.73" r="4" fill="#a855f7" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1352;0.1355;1.0000" values="0;0;1;1"/></circle>
<rect x="154.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1707;0.1710;1.0000" values="0;0;1;1"/></rect>
<text x="206.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1707;0.1710;1.0000" values="0;0;1;1"/></text>
<circle cx="258.0" cy="307.37" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1707;0.1710;1.0000" values="0;0;1;1"/></circle>
<rect x="258.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2062;0.2065;1.0000" values="0;0;1;1"/></rect>
<text x="310.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2062;0.2065;1.0000" values="0;0;1;1"/></text>
<circle cx="362.0" cy="311.01" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2062;0.2065;1.0000" values="0;0;1;1"/></circle>
<rect x="362.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2417;0.2419;1.0000" values="0;0;1;1"/></rect>
<text x="414.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2417;0.2419;1.0000" values="0;0;1;1"/></text>
<circle cx="466.0" cy="314.65" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2417;0.2419;1.0000" values="0;0;1;1"/></circle>
<rect x="466.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2772;0.2774;1.0000" values="0;0;1;1"/></rect>
<text x="518.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2772;0.2774;1.0000" values="0;0;1;1"/></text>
<circle cx="570.0" cy="318.29" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2772;0.2774;1.0000" values="0;0;1;1"/></circle>
<rect x="570.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3126;0.3129;1.0000" values="0;0;1;1"/></rect>
<text x="622.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3126;0.3129;1.0000" values="0;0;1;1"/></text>
<circle cx="674.0" cy="321.93" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3126;0.3129;1.0000" values="0;0;1;1"/></circle>
<rect x="674.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3481;0.3484;1.0000" values="0;0;1;1"/></rect>
<text x="726.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3481;0.3484;1.0000" values="0;0;1;1"/></text>
<circle cx="778.0" cy="325.57" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3481;0.3484;1.0000" values="0;0;1;1"/></circle>
<rect x="674.0" y="288.0" width="52.0" height="140" fill="#a855f7" fill-opacity="0.18" stroke="#a855f7" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3836;0.3839;1.0000" values="0;0;1;1"/></rect>
<text x="700.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#a855f7" opacity="0">L2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3836;0.3839;1.0000" values="0;0;1;1"/></text>
<circle cx="726.0" cy="323.75" r="4" fill="#a855f7" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3836;0.3839;1.0000" values="0;0;1;1"/></circle>
<rect x="674.0" y="288.0" width="104.0" height="140" fill="#f97316" fill-opacity="0.18" stroke="#f97316" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4191;0.4194;1.0000" values="0;0;1;1"/></rect>
<text x="726.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#f97316" opacity="0">L3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4191;0.4194;1.0000" values="0;0;1;1"/></text>
<circle cx="778.0" cy="325.57" r="4" fill="#f97316" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4191;0.4194;1.0000" values="0;0;1;1"/></circle>
<rect x="726.0" y="288.0" width="52.0" height="140" fill="#a855f7" fill-opacity="0.18" stroke="#a855f7" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4546;0.4548;1.0000" values="0;0;1;1"/></rect>
<text x="752.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#a855f7" opacity="0">L2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4546;0.4548;1.0000" values="0;0;1;1"/></text>
<circle cx="778.0" cy="325.57" r="4" fill="#a855f7" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4546;0.4548;1.0000" values="0;0;1;1"/></circle>
<rect x="726.0" y="288.0" width="26.0" height="140" fill="#3b82f6" fill-opacity="0.18" stroke="#3b82f6" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4903;1.0000" values="0;0;1;1"/></rect>
<text x="739.0" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#3b82f6" opacity="0">L1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4903;1.0000" values="0;0;1;1"/></text>
<circle cx="752.0" cy="324.66" r="4" fill="#3b82f6" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4903;1.0000" values="0;0;1;1"/></circle>
<rect x="726.0" y="288.0" width="13.0" height="140" fill="#22c55e" fill-opacity="0.18" stroke="#22c55e" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5255;0.5258;1.0000" values="0;0;1;1"/></rect>
<text x="732.5" y="423.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">命中<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5255;0.5258;1.0000" values="0;0;1;1"/></text>
<circle cx="739.0" cy="324.2" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5255;0.5258;1.0000" values="0;0;1;1"/></circle>
<text x="500" y="272" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">深度の読み込み:</text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.0997;0.1000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0997;0.1000;0.1352;0.1355;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1352;0.1355;0.1707;0.1710;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1707;0.1710;0.2062;0.2065;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2062;0.2065;0.2417;0.2419;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2417;0.2419;0.2772;0.2774;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2772;0.2774;0.3126;0.3129;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">8<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3126;0.3129;0.3481;0.3484;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">9<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3481;0.3484;0.3836;0.3839;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">10<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3836;0.3839;0.4191;0.4194;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">11<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4191;0.4194;0.4546;0.4548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">12<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4546;0.4548;0.4901;0.4903;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">13<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4903;0.5255;0.5258;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="274" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">14<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5255;0.5258;1.0000" values="0;0;1;1"/></text>
<circle cx="46" cy="446" r="6" fill="#22c55e"/>
<text x="56" y="450" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">L0: 1 マス</text>
<circle cx="163.2" cy="446" r="6" fill="#3b82f6"/>
<text x="173.2" y="450" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">L1: 2 マス</text>
<circle cx="280.4" cy="446" r="6" fill="#a855f7"/>
<text x="290.4" y="450" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">L2: 4 マス</text>
<circle cx="397.59999999999997" cy="446" r="6" fill="#f97316"/>
<text x="407.59999999999997" y="450" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">L3: 8 マス</text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6126;0.6129;1.0000" values="0;0;1;1"/><rect x="30" y="462" width="900" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="486" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1e3a8a">命中は同じ(列 52)。深度の読み込みは 線形 51 回 → Hi-Z 14 回(約 3.6 分の 1)</text>
</g>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ地形(灰色)に、同じ光線を飛ばす<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">上: 毎回 1 マス進む。 下: 空いている所は、大きな枠でまとめて飛ばす<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.5610;0.5613;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">手前の遮蔽物が無い所を、一気に飛ばせるのが Hi-Z の強み<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5610;0.5613;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ssr-hiz-steps:end -->

## 探索アルゴリズム

<strong>ミップ レベルを上げ下げしながら</strong>、レイを進めます。

探索では、ミップ レベルを上げ下げしながらレイを進めます。レイが現在のセルの最小深度より手前にある（空いている）場合は、セルの端まで進み、ミップを上げます。次はもっと大きく飛べます。レイがセルの内部で最小深度の面に届く場合は、届く位置まで進んで、ミップを下げて精査します。ミップ 0 に達してもまだ当たりなら、それが交点であり、厚みを検証します。

```hlsl
bool TraceHiZ(float3 origin, float3 dir, out float3 hit) {
  int level = kStartLevel;
  float t = 0.0;
  float2 inv_dir = 1.0 / dir.xy;
  int2 step_dir = int2(dir.x > 0 ? 1 : 0, dir.y > 0 ? 1 : 0);

  for (int i = 0; i < kMaxIterations && level >= 0; ++i) {
    float3 p = origin + dir * t;
    if (any(p.xy < 0.0) || any(p.xy > 1.0)) return false;

    float2 dims = hiz_size >> level;
    int2 cell = int2(p.xy * dims);
    float min_z = hiz.Load(int3(cell, level)).r;

    float2 boundary = (cell + step_dir) / dims;
    float2 t_xy = (boundary - origin.xy) * inv_dir;
    float t_boundary = min(t_xy.x, t_xy.y);

    float t_z = (min_z - origin.z) / dir.z;

    if (p.z < min_z) {
      if (t_z < t_boundary) {
        t = t_z;
        level -= 1;
      } else {
        t = t_boundary + kEpsilon;
        level = min(level + 1, kMaxLevel);
      }
    } else {
      level -= 1;
    }
  }
  hit = origin + dir * t;
  return level < 0;
}
```

| 点 | 説明 |
| --- | --- |
| `cell + step_dir` | レイの進む向きのセルの境界（右・下なら、次のセルの端） |
| `t_boundary` | レイがセルの境界に達する時刻 t（x・y のうち早い方） |
| `t_z` | レイがセルの最小深度の面に達する時刻 |
| `p.z < min_z` | レイがこのセルの全ての面より手前（空いている） |
| `t_z < t_boundary` | セルの中で最小深度の面に届く（当たりの候補） → 下りて精査 |
| それ以外 | セルを抜ける（何にも当たらない） → 端まで進み、上がる |
| `level < 0` | ミップ 0 の最も細かいセルで当たり |

!!! note "アルゴリズムは、実装で細部が違う"
    境界の扱い（epsilon）、<strong>レイの向きによる、セルの選び方</strong>、<strong>ミップ 0 での終了条件</strong>など、細部は実装ごとに異なります。ここは考え方を示したものです。詳しい実装は参考の資料（Stachowiak の講演、Uludag の章）を参照してください。

## 厚みの検証

Hi-Z は<strong>レイが最も細かいセルで深度に達した</strong>所を当たりとします。<strong>この点が本当に「その物体の表面」</strong>かを<strong>厚み</strong>で検証します。

Hi-Z は、レイが最も細かいセルで深度に達した所を当たりとします。この点が本当に物体の表面かどうかは、<strong>厚み</strong>で検証します。当たった位置のレイのビュー空間の奥行きと、その画素の深度の差が、厚み以内かを調べます。範囲外なら、薄い物のはるか後ろに突き抜けたとみなして当たりとせず、レイを続けるか、その方向を諦めます。

```hlsl
float ray_z = LinearizeDepth(hit.z);
float scene_z = LinearizeDepth(depth_tex.Load(int3(hit_pixel, 0)).r);
bool valid = (ray_z - scene_z) < thickness;
```

<strong>単純に諦める</strong>と<strong>手前の細い物の後ろにある面が、反射に映らず</strong>、穴が開きます。厚みで弾かれたら、探索を続ける実装もあります（手前の物体を飛び越えて、奥を探す）。

## 精度とアーティファクト

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| セルの境界の取りこぼし | 浮動小数点の誤差で境界のすぐ手前で止まる（無限ループ・飛び越し） | epsilon を境界に足す（`t_boundary + eps`）。反復回数の上限 |
| 斜めのレイが深度の面に平行 | `dir.z` が 0 に近い（0 除算） | `dir.z` の符号・大きさをチェック |
| 画面外 | レイが画面の範囲を出た | 範囲外で打ち切り（当たりなし） |
| ミップ 0 以外で誤った当たり | 最小深度は保守的（実際の面より手前） | ミップ 0 で必ず確かめる |
| ミップの精度 | 低い精度の深度 | 32 ビット浮動小数点の深度 |
| ステップ数の上限 | 複雑なシーンで収束しない | 上限を設けて、当たらなかった扱い（または近似） |

## Hi-Z SSR の全体像

| パス | 内容 |
| --- | --- |
| ① Hi-Z の作成 | 深度の最小ミップ チェーン |
| ② 反射方向（レイ）の生成 | G-Buffer の法線・粗さから |
| ③ Hi-Z トレース | ビュー → 画面空間に変換して、探索 |
| ④ 色の取得 | 当たった画素の色（前フレーム・動きベクトル） |
| ⑤ フェード・合成 | 信頼度でフォールバックと混ぜる（[SSR Fallback and Compositing](ssr-fallback.md)） |

## 線形マーチ（DDA）との使い分け

| 状況 | おすすめ |
| --- | --- |
| 短いレイ・粗いレイ・単純な実装 | 画面空間の DDA |
| 長いレイ・多くの粗い反射・精度が要る | Hi-Z |
| <strong>確率的 SSR（粗さでサンプルが多様）</strong> | Hi-Z（レイ長さがばらつく） |
| モバイル | 軽い DDA か、SSR を省く |

<strong>併用</strong>する実装もあります（<strong>近距離は DDA、遠距離は Hi-Z</strong>）。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| 遠くまでのレイが少ないステップ | Hi-Z の作成コスト（小さい） |
| 取りこぼしが少ない（セルの最小深度で保守的） | 実装が複雑（境界・epsilon・ミップの上下） |
| 確率的 SSR と相性が良い | 厚みの扱いは基礎の SSR と同じ課題 |
| ステップ数が距離に依存しない | 画面外・裏側が映らない限界は同じ |


原典は、Uludag の "Hi-Z Screen-Space Cone Tracing"（GPU Pro 5, 2014）で、Hi-Z によるレイ トレースを広めました。その後、Stachowiak らの確率的 SSR の発表が、Hi-Z と確率的サンプリングの組み合わせを標準にしました。

原典は、Uludag の "Hi-Z Screen-Space Cone Tracing"（GPU Pro 5, 2014）で、Hi-Z によるレイ トレースを広めました。その後、Stachowiak らの確率的 SSR の発表が、Hi-Z と確率的サンプリングの組み合わせを標準にしました。

## よくあるミス

??? failure "Hi-Z を、平均でミップ化して、誤った当たりが出る"
    <strong>最小（reverse-Z なら最大）</strong>で作ります。

??? failure "reverse-Z なのに、最小のままで探索して、全く当たらない"
    深度の向きに合わせます（<strong>reverse-Z は、最大値のミップ</strong>）。

??? failure "セルの境界で止まって、無限ループ・飛び越し"
    <strong>epsilon</strong>を足し、<strong>反復回数の上限</strong>を設けます。

??? failure "ミップ 0 の確認を省いて、粗いセルの当たりをそのまま採用"
    最後は<strong>ミップ 0 で必ず確認</strong>します。

??? failure "ビュー空間と画面空間の、座標を混ぜる"
    探索は、<strong>(画面 xy, NDC の z)</strong> で一貫させます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Hi-Z SSR ＝ <strong>階層的な最小深度で、空いている領域を一気に飛ばす</strong>レイ探索
    - [x] Hi-Z ＝ <strong>各セルが、範囲内の最も手前の深度（最小）</strong>のミップ。<strong>reverse-Z は最大</strong>
    - [x] <strong>空いていれば端まで進んで、ミップを上げ</strong>、<strong>当たりそうなら下りて精査</strong>
    - [x] 探索は<strong>(画面 xy, NDC の z) の直線</strong>。<strong>最後に厚みで検証</strong>
    - [x] <strong>ステップ数が、距離に依存しない</strong>。<strong>確率的 SSR の基盤</strong>

## 参考

- Uludag, "Hi-Z Screen-Space Cone-Tracing"（GPU Pro 5, 2014）
- Stachowiak, Uludag, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015 Advances in Real-Time Rendering、Frostbite）

## 関連ページ

- [Reflections](index.md)
- [SSR Basics](ssr-basics/index.md)
- [Stochastic SSR](ssr-stochastic.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
- [SAO (Scalable AO)](../ao/sao.md)
