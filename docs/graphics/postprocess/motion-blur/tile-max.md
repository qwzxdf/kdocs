---
title: タイル最大速度
tags:
  - 描画
---

# タイル最大速度

**画素ごとに長い距離を多数サンプル**するのは**重い**うえ、**速い物体の輪郭の外側（背景）の画素は自分の速度が 0 なので、尾が伸びません**。**そこで画面を小さなタイル（例：16×16 画素）に分け、各タイルの「最大の速度」を求め、周囲のタイルの最大速度も合わせた「近傍最大速度」を作る**のが**標準の手法**です。**ぼかしの方向・長さ・スキップの判断に使えます**。このページでは、**TileMax・NeighborMax の 2 段階・実装・使い方・コスト**を説明します。

!!! tip "ポイント"
    - TileMax ＝ <strong>各タイル（16×16 画素）内で最大の速度ベクトル</strong>（<strong>長さが最大のもの</strong>）。
    - NeighborMax ＝ <strong>周囲 3×3 タイルの TileMax の中で、最大のもの</strong>。<strong>隣のタイルの速い動きが、流れ込む</strong>のを考慮。
    - ぼかしの<strong>方向と長さ</strong>は<strong>NeighborMax</strong>から決める。<strong>輪郭の外にも尾が伸びる</strong>。
    - <strong>NeighborMax の長さが閾値以下のタイル</strong>は<strong>ぼかしをスキップ</strong>（<strong>高速化</strong>）。
    - <strong>タイル サイズ ＝ 最大ブラー長</strong>にそろえる。
    - <strong>タイルの数は少ない</strong>（1080p で 120×68）。<strong>コストは小さい</strong>。

<!-- fig:tile-max:begin -->

<svg class="fig illust motion" data-fig="tile-max" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tile-max" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">タイル最大速度:タイルごとに、最も速い速度を求めて、ブラーの半径を決める</text>
<rect x="40" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="64.0" y1="104.0" x2="61.67" y2="106.38" stroke="#64748b" stroke-width="2"/>
<rect x="88" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="112.0" y1="104.0" x2="112.66" y2="103.26" stroke="#64748b" stroke-width="2"/>
<rect x="136" y="80" width="47" height="47" fill="#f8fafc"/>
<rect x="184" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="208.0" y1="104.0" x2="213.65" y2="107.14" stroke="#64748b" stroke-width="2"/>
<rect x="232" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="256.0" y1="104.0" x2="253.03" y2="101.34" stroke="#64748b" stroke-width="2"/>
<rect x="280" y="80" width="47" height="47" fill="#f8fafc"/>
<rect x="328" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="352.0" y1="104.0" x2="347.17" y2="105.51" stroke="#64748b" stroke-width="2"/>
<rect x="376" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="400.0" y1="104.0" x2="402.88" y2="108.36" stroke="#64748b" stroke-width="2"/>
<rect x="424" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="448.0" y1="104.0" x2="449.31" y2="105.1" stroke="#64748b" stroke-width="2"/>
<rect x="472" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="496.0" y1="104.0" x2="499.23" y2="102.31" stroke="#64748b" stroke-width="2"/>
<rect x="520" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="544.0" y1="104.0" x2="544.63" y2="99.8" stroke="#64748b" stroke-width="2"/>
<rect x="568" y="80" width="47" height="47" fill="#f8fafc"/>
<line x1="592.0" y1="104.0" x2="591.93" y2="101.24" stroke="#64748b" stroke-width="2"/>
<rect x="40" y="128" width="47" height="47" fill="#f8fafc"/>
<rect x="88" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="112.0" y1="152.0" x2="111.25" y2="147.2" stroke="#64748b" stroke-width="2"/>
<rect x="136" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="160.0" y1="152.0" x2="162.59" y2="153.59" stroke="#64748b" stroke-width="2"/>
<rect x="184" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="208.0" y1="152.0" x2="221.43" y2="148.83" stroke="#64748b" stroke-width="2"/>
<rect x="232" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="256.0" y1="152.0" x2="269.63" y2="155.45" stroke="#64748b" stroke-width="2"/>
<rect x="280" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="304.0" y1="152.0" x2="315.99" y2="155.83" stroke="#64748b" stroke-width="2"/>
<rect x="328" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="352.0" y1="152.0" x2="375.27" y2="143.34" stroke="#64748b" stroke-width="2"/>
<rect x="376" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="400.0" y1="152.0" x2="397.28" y2="152.15" stroke="#64748b" stroke-width="2"/>
<rect x="424" y="128" width="47" height="47" fill="#f8fafc"/>
<rect x="472" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="496.0" y1="152.0" x2="500.98" y2="156.22" stroke="#64748b" stroke-width="2"/>
<rect x="520" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="544.0" y1="152.0" x2="547.11" y2="154.96" stroke="#64748b" stroke-width="2"/>
<rect x="568" y="128" width="47" height="47" fill="#f8fafc"/>
<line x1="592.0" y1="152.0" x2="595.29" y2="149.44" stroke="#64748b" stroke-width="2"/>
<rect x="40" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="64.0" y1="200.0" x2="65.46" y2="200.08" stroke="#64748b" stroke-width="2"/>
<rect x="88" y="176" width="47" height="47" fill="#f8fafc"/>
<rect x="136" y="176" width="47" height="47" fill="#f8fafc"/>
<rect x="184" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="208.0" y1="200.0" x2="224.93" y2="205.93" stroke="#64748b" stroke-width="2"/>
<rect x="232" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="256.0" y1="200.0" x2="272.51" y2="198.65" stroke="#64748b" stroke-width="2"/>
<rect x="280" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="304.0" y1="200.0" x2="323.42" y2="193.45" stroke="#64748b" stroke-width="2"/>
<rect x="328" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="352.0" y1="200.0" x2="370.77" y2="194.97" stroke="#64748b" stroke-width="2"/>
<rect x="376" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="400.0" y1="200.0" x2="404.23" y2="198.85" stroke="#64748b" stroke-width="2"/>
<rect x="424" y="176" width="47" height="47" fill="#f8fafc"/>
<rect x="472" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="496.0" y1="200.0" x2="498.58" y2="203.52" stroke="#64748b" stroke-width="2"/>
<rect x="520" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="544.0" y1="200.0" x2="545.93" y2="199.93" stroke="#64748b" stroke-width="2"/>
<rect x="568" y="176" width="47" height="47" fill="#f8fafc"/>
<line x1="592.0" y1="200.0" x2="597.2" y2="204.96" stroke="#64748b" stroke-width="2"/>
<rect x="40" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="64.0" y1="248.0" x2="68.84" y2="246.44" stroke="#64748b" stroke-width="2"/>
<rect x="88" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="112.0" y1="248.0" x2="110.69" y2="246.91" stroke="#64748b" stroke-width="2"/>
<rect x="136" y="224" width="47" height="47" fill="#f8fafc"/>
<rect x="184" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="208.0" y1="248.0" x2="229.08" y2="249.52" stroke="#64748b" stroke-width="2"/>
<rect x="232" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="256.0" y1="248.0" x2="277.7" y2="240.55" stroke="#64748b" stroke-width="2"/>
<rect x="280" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="304.0" y1="248.0" x2="318.61" y2="252.38" stroke="#64748b" stroke-width="2"/>
<rect x="328" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="352.0" y1="248.0" x2="371.5" y2="247.24" stroke="#64748b" stroke-width="2"/>
<rect x="376" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="400.0" y1="248.0" x2="402.88" y2="247.74" stroke="#64748b" stroke-width="2"/>
<rect x="424" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="448.0" y1="248.0" x2="452.11" y2="248.48" stroke="#64748b" stroke-width="2"/>
<rect x="472" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="496.0" y1="248.0" x2="493.27" y2="253.07" stroke="#64748b" stroke-width="2"/>
<rect x="520" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="544.0" y1="248.0" x2="544.71" y2="251.04" stroke="#64748b" stroke-width="2"/>
<rect x="568" y="224" width="47" height="47" fill="#f8fafc"/>
<line x1="592.0" y1="248.0" x2="590.56" y2="250.85" stroke="#64748b" stroke-width="2"/>
<rect x="40" y="272" width="47" height="47" fill="#f8fafc"/>
<rect x="88" y="272" width="47" height="47" fill="#f8fafc"/>
<rect x="136" y="272" width="47" height="47" fill="#f8fafc"/>
<rect x="184" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="208.0" y1="296.0" x2="202.19" y2="296.11" stroke="#64748b" stroke-width="2"/>
<rect x="232" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="256.0" y1="296.0" x2="256.06" y2="301.11" stroke="#64748b" stroke-width="2"/>
<rect x="280" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="304.0" y1="296.0" x2="299.27" y2="298.42" stroke="#64748b" stroke-width="2"/>
<rect x="328" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="352.0" y1="296.0" x2="353.62" y2="295.62" stroke="#64748b" stroke-width="2"/>
<rect x="376" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="400.0" y1="296.0" x2="397.99" y2="298.07" stroke="#64748b" stroke-width="2"/>
<rect x="424" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="448.0" y1="296.0" x2="443.79" y2="300.54" stroke="#64748b" stroke-width="2"/>
<rect x="472" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="496.0" y1="296.0" x2="498.29" y2="300.23" stroke="#64748b" stroke-width="2"/>
<rect x="520" y="272" width="47" height="47" fill="#f8fafc"/>
<line x1="544.0" y1="296.0" x2="543.67" y2="302.06" stroke="#64748b" stroke-width="2"/>
<rect x="568" y="272" width="47" height="47" fill="#f8fafc"/>
<rect x="40" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="64.0" y1="344.0" x2="65.17" y2="343.59" stroke="#64748b" stroke-width="2"/>
<rect x="88" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="112.0" y1="344.0" x2="106.42" y2="339.6" stroke="#64748b" stroke-width="2"/>
<rect x="136" y="320" width="47" height="47" fill="#f8fafc"/>
<rect x="184" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="208.0" y1="344.0" x2="206.85" y2="344.97" stroke="#64748b" stroke-width="2"/>
<rect x="232" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="256.0" y1="344.0" x2="260.3" y2="343.06" stroke="#64748b" stroke-width="2"/>
<rect x="280" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="304.0" y1="344.0" x2="305.62" y2="345.97" stroke="#64748b" stroke-width="2"/>
<rect x="328" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="352.0" y1="344.0" x2="354.63" y2="347.07" stroke="#64748b" stroke-width="2"/>
<rect x="376" y="320" width="47" height="47" fill="#f8fafc"/>
<rect x="424" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="448.0" y1="344.0" x2="452.59" y2="346.01" stroke="#64748b" stroke-width="2"/>
<rect x="472" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="496.0" y1="344.0" x2="495.06" y2="340.89" stroke="#64748b" stroke-width="2"/>
<rect x="520" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="544.0" y1="344.0" x2="539.92" y2="347.7" stroke="#64748b" stroke-width="2"/>
<rect x="568" y="320" width="47" height="47" fill="#f8fafc"/>
<line x1="592.0" y1="344.0" x2="595.11" y2="349.58" stroke="#64748b" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;0.2963;0.2966;1.0000" values="0;0;1;1;0;0"/><rect x="40" y="80" width="143" height="143" fill="none" stroke="#e5aa28" stroke-width="4"/>
<line x1="112.0" y1="152.0" x2="111.25" y2="147.2" stroke="#e5484d" stroke-width="4"/>
<text x="46" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">最大 5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2687;0.2690;1.0000" values="0;0;1;1"/><rect x="636" y="110" width="70" height="34" fill="#f3e7ea" stroke="#94a3b8" stroke-width="1.5"/>
<text x="671" y="132" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2963;0.2966;0.4894;0.4897;1.0000" values="0;0;1;1;0;0"/><rect x="184" y="80" width="143" height="143" fill="none" stroke="#e5aa28" stroke-width="4"/>
<line x1="304.0" y1="200.0" x2="323.42" y2="193.45" stroke="#e5484d" stroke-width="4"/>
<text x="190" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">最大 23</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4618;0.4621;1.0000" values="0;0;1;1"/><rect x="636" y="152" width="70" height="34" fill="#f9b8b9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="671" y="174" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">23</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4894;0.4897;0.6825;0.6828;1.0000" values="0;0;1;1;0;0"/><rect x="184" y="224" width="143" height="143" fill="none" stroke="#e5aa28" stroke-width="4"/>
<line x1="256.0" y1="248.0" x2="277.7" y2="240.55" stroke="#e5484d" stroke-width="4"/>
<text x="190" y="360" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">最大 25</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6549;0.6552;1.0000" values="0;0;1;1"/><rect x="636" y="194" width="70" height="34" fill="#fab1b2" stroke="#94a3b8" stroke-width="1.5"/>
<text x="671" y="216" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">25</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6825;0.6828;0.8756;0.8759;1.0000" values="0;0;1;1;0;0"/><rect x="328" y="224" width="143" height="143" fill="none" stroke="#e5aa28" stroke-width="4"/>
<line x1="352.0" y1="248.0" x2="371.5" y2="247.24" stroke="#e5484d" stroke-width="4"/>
<text x="334" y="360" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">最大 22</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8480;0.8483;1.0000" values="0;0;1;1"/><rect x="636" y="236" width="70" height="34" fill="#f9bbbc" stroke="#94a3b8" stroke-width="1.5"/>
<text x="671" y="258" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">22</text>
</g>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">各画素の速度（灰色の矢印）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;1.0000" values="1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">3×3 画素のタイルごとに、最大の速度（赤い矢印）を取り出す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;0.9308;0.9310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">タイルの最大速度で、ブラーのサンプル範囲を決める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.9308;0.9310;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">速い物のタイルは、広くぼかす。静止した所は、ぼかさない（無駄な計算を省ける）。隣のタイルとも最大を取る（NeighborMax）。</text>
</svg>

<!-- fig:tile-max:end -->

## なぜ必要か

**速い物体のブラー**は、**物体の外側にも**尾を引くべきです。**画素 P 自身の速度**だけを**使う**と、**P が背景（速度 0）なら、ぼけません**。**P の近くに速い物体があれば、その速度の分だけ、P の周りを見る必要があります**。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="タイルの最大速度">
<text x="20" y="26" class="fig-title">タイルの最大速度：近くにある速い動きを、周りの画素に知らせる</text>
<g transform="translate(40,56)">
<rect x="0" y="0" width="320" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="80" y1="0" x2="80" y2="140"/><line x1="160" y1="0" x2="160" y2="140"/><line x1="240" y1="0" x2="240" y2="140"/><line x1="0" y1="35" x2="320" y2="35"/><line x1="0" y1="70" x2="320" y2="70"/><line x1="0" y1="105" x2="320" y2="105"/></g>
<rect x="165" y="45" width="30" height="20" fill="#2563eb"/>
<line x1="165" y1="55" x2="130" y2="55" stroke="#e5484d" stroke-width="3" marker-end="url(#tm2-arrow)"/>
<defs><marker id="tm2-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e5484d"/></marker></defs>
<rect x="160" y="35" width="80" height="35" fill="#e5aa28" fill-opacity="0.35"/>
<text x="164" y="30" style="font-size:11px">速い物体を含むタイル</text>
<rect x="80" y="35" width="80" height="35" fill="#e5484d" fill-opacity="0.2"/>
<text x="84" y="88" style="font-size:11px">隣のタイル（背景）にも伝える</text>
</g>
<g font-size="13"><text x="400" y="90" style="font-weight:700">2 段階</text>
<text x="400" y="116">① TileMax：各タイルの最大速度</text>
<text x="400" y="140">② NeighborMax：周囲 3×3 の最大</text>
<text x="400" y="176" style="font-weight:700">→ 背景のタイルにも、物体の速度が伝わる</text></g>
</svg>

## 手順

| 手順 | 内容 |
| --- | --- |
| **① TileMax** | **各タイル内の速度のうち、長さが最大のベクトル**を**求める**（**共有メモリで縮約**） |
| **② NeighborMax** | **周囲 3×3 の TileMax の最大**を**求める** |
| **③ ぼかし** | **NeighborMax の方向・長さ**で**サンプル**する |

## ① TileMax

```hlsl
Texture2D<float2> velocity_buffer : register(t0);
RWTexture2D<float2> tile_max : register(u0);

groupshared float2 s_velocity[256];

[numthreads(16, 16, 1)]
void TileMaxMain(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID, uint group_index : SV_GroupIndex) {
  float2 v = velocity_buffer.Load(int3(id.xy, 0));
  s_velocity[group_index] = v;
  GroupMemoryBarrierWithGroupSync();
  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) {
      float2 other = s_velocity[group_index + stride];
      if (dot(other, other) > dot(s_velocity[group_index], s_velocity[group_index])) {
        s_velocity[group_index] = other;
      }
    }
    GroupMemoryBarrierWithGroupSync();
  }
  if (group_index == 0) tile_max[group_id.xy] = s_velocity[0];
}
```

| 点 | 説明 |
| --- | --- |
| **16×16 のグループ ＝ 1 タイル** | **1 グループが 1 タイルを担当** |
| **`dot(v, v)`（長さの 2 乗）で比較** | **平方根を避ける** |
| **共有メモリでの縮約** | **256 → 1 を 8 回の比較**で**求める** |

## ② NeighborMax

<strong>TileMax の画像（小さい）</strong>を**読み、周囲 3×3 の最大**を**取ります**。

```hlsl
Texture2D<float2> tile_max_texture : register(t0);
RWTexture2D<float2> neighbor_max : register(u0);

[numthreads(8, 8, 1)]
void NeighborMaxMain(uint3 id : SV_DispatchThreadID) {
  float2 best = 0;
  float best_length_sq = 0;
  for (int y = -1; y <= 1; ++y) {
    for (int x = -1; x <= 1; ++x) {
      int2 p = clamp(int2(id.xy) + int2(x, y), 0, tile_count - 1);
      float2 v = tile_max_texture.Load(int3(p, 0));
      float len_sq = dot(v, v);
      if (len_sq > best_length_sq) {
        best = v;
        best_length_sq = len_sq;
      }
    }
  }
  neighbor_max[id.xy] = best;
}
```

| 点 | 説明 |
| --- | --- |
| **3×3** | **隣のタイルの速い物体が、1 タイル先まで影響する**ため（**タイルの大きさ ＝ 最大ブラー長**） |
| **端は `clamp`** | **画面の外は端のタイルを繰り返す** |

### より正確な NeighborMax

**単純な 3×3 の最大**は、**向きを無視して長さだけ**で選びます。<strong>「そのタイルの速度が自分のタイルに向かっているか」</strong>を**考慮**する**と**、**より正確**です（**McGuire 方式**）。

## ぼかしでの使い方

```hlsl
float2 neighbor_velocity = neighbor_max.SampleLevel(point_clamp, uv, 0).xy;
float neighbor_length = length(neighbor_velocity * resolution);
if (neighbor_length < kMinVelocityPixels) {
  return scene_color.SampleLevel(point_clamp, uv, 0).rgb;
}
```

| 用途 | 内容 |
| --- | --- |
| **ぼかしの方向** | **NeighborMax の向きにサンプルを配置** |
| **ぼかしの長さ** | **NeighborMax の長さ**（**最大ブラー長で制限**） |
| **スキップ判定** | **長さが小さいタイル（< 0.5 画素）は、ぼかしを省略** |
| **自分の速度との組み合わせ** | **サンプルの重み付けに自分の速度も使う**（[ぼかしの実装](blur-pass.md)） |

## コスト

| 項目 | 内容 |
| --- | --- |
| **TileMax** | **フル解像度の速度を 1 回読む**（**帯域は R16G16 のみ**） |
| **NeighborMax** | <strong>タイル数分（1080p で 120×68）</strong>。**ほぼ無料** |
| **効果** | **静止している多くの画素で、ぼかしをスキップ**。**フレーム全体で大幅に節約** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **タイル サイズ ＝ 最大ブラー長** | **16〜20 画素が一般的** |
| **NeighborMax に向きを考慮** | **精度が上がる** |
| **スキップ判定で分岐の一貫性** | **タイル単位で同じ分岐になり、GPU が効率的** |
| **DOF のタイルと共用** | **同じ 16×16 のタイルで、DOF の最大 CoC も計算**（[前景と背景](../dof/near-far.md)） |

## よくあるミス

??? failure "NeighborMax を使わず、輪郭の外にブラーが出ない"
    **周囲の速度をタイルの最大で伝える**。

??? failure "タイルの大きさがブラー長より小さく、速い物体の尾が届かない"
    **タイル サイズ ≧ 最大ブラー長**にする。

??? failure "画面の端のタイルで、範囲外を読んで壊れる"
    **`clamp` で端をそろえる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>TileMax</strong> ＝ <strong>タイルごとの最大速度</strong>。<strong>NeighborMax</strong> ＝ <strong>周囲 3×3 の最大</strong>
    - [x] <strong>背景の画素にも、近くの速い物体の速度を伝え、尾を伸ばす</strong>
    - [x] <strong>遅いタイルは、ぼかしをスキップ</strong>（<strong>高速化</strong>）
    - [x] <strong>タイル サイズ ＝ 最大ブラー長</strong>
    - [x] <strong>共有メモリで縮約</strong>

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [モーション ブラー](index.md)
- [速度バッファ](velocity-buffer.md)
- [ぼかしの実装](blur-pass.md)
- [前景と背景（DOF）](../dof/near-far.md)
