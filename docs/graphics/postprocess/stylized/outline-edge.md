---
title: 画面空間のエッジ検出
tags:
  - 描画
---

# 画面空間のエッジ検出

**背面法はモデルの外側の輪郭しか出ません**。**モデルの内側の折り目（鼻・袖・服のしわの境）や、物体どうしの境の線も出したい**場合は、**画面の画像（深度・法線・ID）から、「値が大きく変わる場所」を検出して線にする**、**画面空間のエッジ検出**を使います。**どんな形状でも後処理で線を引ける**ので**柔軟**ですが、**線の太さの制御や細部のちらつき**に**注意**が**必要**です。このページでは、**深度・法線・ID による検出・Sobel フィルタ・線の太さ・ちらつきの抑制・色の付け方**を説明します。

!!! tip "ポイント"
    - エッジ検出 ＝ <strong>隣り合う画素の、深度・法線・ID の差が大きい所を線にする</strong>。
    - <strong>深度</strong>：<strong>物体の輪郭・前後関係の境</strong>。<strong>法線</strong>：<strong>折り目・面の向きが変わる所</strong>。<strong>ID</strong>：<strong>物体・材質の境</strong>。
    - 3 つを<strong>組み合わせる</strong>と<strong>内側の線も外側の線も出る</strong>。
    - <strong>Sobel フィルタ</strong>が<strong>標準</strong>。<strong>勾配の大きさで線の強さ</strong>を決める。
    - <strong>線の太さ</strong>は<strong>サンプル間隔</strong>で調整する。<strong>距離で補正</strong>。
    - <strong>斜めの面で深度の差が出て、不要な線</strong>が出る → <strong>深度勾配で補正</strong>。

## 3 つの検出

**検出に使う画像**は、**不透明パスの出力**（**深度バッファ・法線バッファ・ID バッファ**）です。

| 入力 | 検出される線 | 弱点 |
| --- | --- | --- |
| **深度** | **物体の外側の輪郭・手前と奥の境** | **同じ深度の折り目は出ない・斜めの面で誤検出** |
| **法線** | <strong>折り目・面の向きの境（内側の線）</strong> | **滑らかな面の境は出ない・法線マップの細かい凹凸で、ノイズ** |
| <strong>ID（材質・物体）</strong> | **材質・物体どうしの境** | **ID バッファが別途必要** |

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="エッジ検出の入力">
<text x="20" y="26" class="fig-title">深度・法線・ID から、それぞれ違う線が取れる</text>
<g font-size="12">
<g transform="translate(40,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><circle cx="100" cy="66" r="42" fill="#cbd5e1"/><circle cx="100" cy="66" r="42" fill="none" stroke="#111827" stroke-width="4"/><text x="0" y="152">深度：外側の輪郭</text></g>
<g transform="translate(290,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><rect x="50" y="30" width="100" height="76" fill="#e2e8f0"/><line x1="100" y1="30" x2="100" y2="106" stroke="#111827" stroke-width="4"/><line x1="50" y1="68" x2="150" y2="68" stroke="#111827" stroke-width="4"/><text x="0" y="152">法線：内側の折り目</text></g>
<g transform="translate(540,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><rect x="30" y="30" width="70" height="76" fill="#fecaca"/><rect x="100" y="30" width="70" height="76" fill="#bfdbfe"/><line x1="100" y1="30" x2="100" y2="106" stroke="#111827" stroke-width="4"/><text x="0" y="152">ID：物体・材質の境</text></g>
</g>
</svg>

## Sobel フィルタ

<strong>画像の勾配（変化の大きさ）</strong>を**測る標準的な方法**が**Sobel フィルタ**です。**周囲 3×3 の画素に、重みを掛けて、縦・横の勾配を求めます**。

```hlsl
float Sobel(Texture2D<float> source, float2 uv, float2 texel) {
  float tl = source.SampleLevel(point_clamp, uv + texel * float2(-1, -1), 0);
  float t  = source.SampleLevel(point_clamp, uv + texel * float2( 0, -1), 0);
  float tr = source.SampleLevel(point_clamp, uv + texel * float2( 1, -1), 0);
  float l  = source.SampleLevel(point_clamp, uv + texel * float2(-1,  0), 0);
  float r  = source.SampleLevel(point_clamp, uv + texel * float2( 1,  0), 0);
  float bl = source.SampleLevel(point_clamp, uv + texel * float2(-1,  1), 0);
  float b  = source.SampleLevel(point_clamp, uv + texel * float2( 0,  1), 0);
  float br = source.SampleLevel(point_clamp, uv + texel * float2( 1,  1), 0);
  float gx = (tr + 2.0 * r + br) - (tl + 2.0 * l + bl);
  float gy = (bl + 2.0 * b + br) - (tl + 2.0 * t + tr);
  return sqrt(gx * gx + gy * gy);
}
```

| 点 | 説明 |
| --- | --- |
| **`gx`・`gy`** | **横方向・縦方向の勾配**（**重み 1・2・1**） |
| **`sqrt(gx² + gy²)`** | **勾配の大きさ**（**エッジの強さ**） |
| **しきい値で 2 値化** | **`step(threshold, 強さ)` で、線あり・なし** |
| **簡易版** | **上下左右の 4 点だけの差（Roberts Cross など）も使える** |

<!-- fig:outline-edge-detect:begin -->

<svg class="fig illust motion" data-fig="outline-edge-detect" viewBox="0 0 780 430" role="img"><rect x="0" y="0" width="780" height="430" rx="14" fill="#ffffff"/>
<defs><marker id="arr-outline-edge-detect" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Sobel フィルタ:深度の差が大きい画素を、輪郭にする</text>
<rect x="40" y="80" width="35" height="35" fill="#ededed"/>
<rect x="76" y="80" width="35" height="35" fill="#ededed"/>
<rect x="112" y="80" width="35" height="35" fill="#ededed"/>
<rect x="148" y="80" width="35" height="35" fill="#ededed"/>
<rect x="184" y="80" width="35" height="35" fill="#ededed"/>
<rect x="220" y="80" width="35" height="35" fill="#ededed"/>
<rect x="256" y="80" width="35" height="35" fill="#ededed"/>
<rect x="292" y="80" width="35" height="35" fill="#ededed"/>
<rect x="328" y="80" width="35" height="35" fill="#ededed"/>
<rect x="364" y="80" width="35" height="35" fill="#ededed"/>
<rect x="400" y="80" width="35" height="35" fill="#ededed"/>
<rect x="436" y="80" width="35" height="35" fill="#ededed"/>
<rect x="40" y="116" width="35" height="35" fill="#ededed"/>
<rect x="76" y="116" width="35" height="35" fill="#ededed"/>
<rect x="112" y="116" width="35" height="35" fill="#ededed"/>
<rect x="148" y="116" width="35" height="35" fill="#ededed"/>
<rect x="184" y="116" width="35" height="35" fill="#ededed"/>
<rect x="220" y="116" width="35" height="35" fill="#949494"/>
<rect x="256" y="116" width="35" height="35" fill="#949494"/>
<rect x="292" y="116" width="35" height="35" fill="#ededed"/>
<rect x="328" y="116" width="35" height="35" fill="#ededed"/>
<rect x="364" y="116" width="35" height="35" fill="#ededed"/>
<rect x="400" y="116" width="35" height="35" fill="#ededed"/>
<rect x="436" y="116" width="35" height="35" fill="#ededed"/>
<rect x="40" y="152" width="35" height="35" fill="#ededed"/>
<rect x="76" y="152" width="35" height="35" fill="#ededed"/>
<rect x="112" y="152" width="35" height="35" fill="#ededed"/>
<rect x="148" y="152" width="35" height="35" fill="#949494"/>
<rect x="184" y="152" width="35" height="35" fill="#949494"/>
<rect x="220" y="152" width="35" height="35" fill="#949494"/>
<rect x="256" y="152" width="35" height="35" fill="#949494"/>
<rect x="292" y="152" width="35" height="35" fill="#949494"/>
<rect x="328" y="152" width="35" height="35" fill="#949494"/>
<rect x="364" y="152" width="35" height="35" fill="#ededed"/>
<rect x="400" y="152" width="35" height="35" fill="#ededed"/>
<rect x="436" y="152" width="35" height="35" fill="#ededed"/>
<rect x="40" y="188" width="35" height="35" fill="#ededed"/>
<rect x="76" y="188" width="35" height="35" fill="#ededed"/>
<rect x="112" y="188" width="35" height="35" fill="#949494"/>
<rect x="148" y="188" width="35" height="35" fill="#949494"/>
<rect x="184" y="188" width="35" height="35" fill="#949494"/>
<rect x="220" y="188" width="35" height="35" fill="#949494"/>
<rect x="256" y="188" width="35" height="35" fill="#949494"/>
<rect x="292" y="188" width="35" height="35" fill="#949494"/>
<rect x="328" y="188" width="35" height="35" fill="#949494"/>
<rect x="364" y="188" width="35" height="35" fill="#949494"/>
<rect x="400" y="188" width="35" height="35" fill="#ededed"/>
<rect x="436" y="188" width="35" height="35" fill="#ededed"/>
<rect x="40" y="224" width="35" height="35" fill="#ededed"/>
<rect x="76" y="224" width="35" height="35" fill="#ededed"/>
<rect x="112" y="224" width="35" height="35" fill="#949494"/>
<rect x="148" y="224" width="35" height="35" fill="#949494"/>
<rect x="184" y="224" width="35" height="35" fill="#949494"/>
<rect x="220" y="224" width="35" height="35" fill="#949494"/>
<rect x="256" y="224" width="35" height="35" fill="#949494"/>
<rect x="292" y="224" width="35" height="35" fill="#949494"/>
<rect x="328" y="224" width="35" height="35" fill="#949494"/>
<rect x="364" y="224" width="35" height="35" fill="#949494"/>
<rect x="400" y="224" width="35" height="35" fill="#ededed"/>
<rect x="436" y="224" width="35" height="35" fill="#ededed"/>
<rect x="40" y="260" width="35" height="35" fill="#ededed"/>
<rect x="76" y="260" width="35" height="35" fill="#ededed"/>
<rect x="112" y="260" width="35" height="35" fill="#ededed"/>
<rect x="148" y="260" width="35" height="35" fill="#949494"/>
<rect x="184" y="260" width="35" height="35" fill="#949494"/>
<rect x="220" y="260" width="35" height="35" fill="#949494"/>
<rect x="256" y="260" width="35" height="35" fill="#949494"/>
<rect x="292" y="260" width="35" height="35" fill="#949494"/>
<rect x="328" y="260" width="35" height="35" fill="#949494"/>
<rect x="364" y="260" width="35" height="35" fill="#ededed"/>
<rect x="400" y="260" width="35" height="35" fill="#ededed"/>
<rect x="436" y="260" width="35" height="35" fill="#ededed"/>
<rect x="40" y="296" width="35" height="35" fill="#ededed"/>
<rect x="76" y="296" width="35" height="35" fill="#ededed"/>
<rect x="112" y="296" width="35" height="35" fill="#ededed"/>
<rect x="148" y="296" width="35" height="35" fill="#ededed"/>
<rect x="184" y="296" width="35" height="35" fill="#ededed"/>
<rect x="220" y="296" width="35" height="35" fill="#949494"/>
<rect x="256" y="296" width="35" height="35" fill="#949494"/>
<rect x="292" y="296" width="35" height="35" fill="#ededed"/>
<rect x="328" y="296" width="35" height="35" fill="#ededed"/>
<rect x="364" y="296" width="35" height="35" fill="#ededed"/>
<rect x="400" y="296" width="35" height="35" fill="#ededed"/>
<rect x="436" y="296" width="35" height="35" fill="#ededed"/>
<rect x="40" y="332" width="35" height="35" fill="#ededed"/>
<rect x="76" y="332" width="35" height="35" fill="#ededed"/>
<rect x="112" y="332" width="35" height="35" fill="#ededed"/>
<rect x="148" y="332" width="35" height="35" fill="#ededed"/>
<rect x="184" y="332" width="35" height="35" fill="#ededed"/>
<rect x="220" y="332" width="35" height="35" fill="#ededed"/>
<rect x="256" y="332" width="35" height="35" fill="#ededed"/>
<rect x="292" y="332" width="35" height="35" fill="#ededed"/>
<rect x="328" y="332" width="35" height="35" fill="#ededed"/>
<rect x="364" y="332" width="35" height="35" fill="#ededed"/>
<rect x="400" y="332" width="35" height="35" fill="#ededed"/>
<rect x="436" y="332" width="35" height="35" fill="#ededed"/>
<rect x="40" y="80" width="107" height="107" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="x" dur="13s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.0846;0.0923;0.1000;0.1077;0.1154;0.1231;0.1308;0.1385;0.1462;0.1538;0.1615;0.1692;0.1769;0.1846;0.1923;0.2000;0.2077;0.2154;0.2231;0.2308;0.2385;0.2462;0.2538;0.2615;0.2692;0.2769;0.2846;0.2923;0.3000;0.3077;0.3154;0.3231;0.3308;0.3385;0.3462;0.3538;0.3615;0.3692;0.3769;0.3846;0.3923;0.4000;0.4077;0.4154;0.4231;0.4308;0.4385;0.4462;0.4538;0.4615;0.4692;0.4769;0.4846;0.4923;0.5000;0.5077;0.5154;0.5231;0.5308;0.5385;0.5462;0.5538;0.5615;0.5692;0.5769;0.5846;0.5923;0.6000;0.6077;0.6154;0.6231;0.6308;0.6385;0.6462;0.6538;0.6615;0.6692;0.6769;0.6846;0.6923;0.7000;0.7077;0.7154;0.7231;0.7308;0.7385;0.7462;0.7538;0.7615;0.7692;0.7769;0.7846;0.7923;0.8000;0.8077" values="40;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400;4;40;76;112;148;184;220;256;292;328;364;400"/><animate attributeName="y" dur="13s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.0846;0.0923;0.1000;0.1077;0.1154;0.1231;0.1308;0.1385;0.1462;0.1538;0.1615;0.1692;0.1769;0.1846;0.1923;0.2000;0.2077;0.2154;0.2231;0.2308;0.2385;0.2462;0.2538;0.2615;0.2692;0.2769;0.2846;0.2923;0.3000;0.3077;0.3154;0.3231;0.3308;0.3385;0.3462;0.3538;0.3615;0.3692;0.3769;0.3846;0.3923;0.4000;0.4077;0.4154;0.4231;0.4308;0.4385;0.4462;0.4538;0.4615;0.4692;0.4769;0.4846;0.4923;0.5000;0.5077;0.5154;0.5231;0.5308;0.5385;0.5462;0.5538;0.5615;0.5692;0.5769;0.5846;0.5923;0.6000;0.6077;0.6154;0.6231;0.6308;0.6385;0.6462;0.6538;0.6615;0.6692;0.6769;0.6846;0.6923;0.7000;0.7077;0.7154;0.7231;0.7308;0.7385;0.7462;0.7538;0.7615;0.7692;0.7769;0.7846;0.7923;0.8000;0.8077" values="80;44;44;44;44;44;44;44;44;44;44;44;44;80;80;80;80;80;80;80;80;80;80;80;80;116;116;116;116;116;116;116;116;116;116;116;116;152;152;152;152;152;152;152;152;152;152;152;152;188;188;188;188;188;188;188;188;188;188;188;188;224;224;224;224;224;224;224;224;224;224;224;224;260;260;260;260;260;260;260;260;260;260;260;260;296;296;296;296;296;296;296;296;296;296;296;296"/><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.0766;0.0769;0.8151;0.8154;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220" y="80" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1151;0.1154;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="256" y="80" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1228;0.1231;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="148" y="116" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1920;0.1923;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="184" y="116" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="220" y="116" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2074;0.2077;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="256" y="116" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2151;0.2154;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="292" y="116" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2228;0.2231;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="328" y="116" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2305;0.2308;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="112" y="152" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2766;0.2769;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="148" y="152" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2843;0.2846;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="184" y="152" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2920;0.2923;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="292" y="152" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3151;0.3154;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="328" y="152" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3228;0.3231;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="364" y="152" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3305;0.3308;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="76" y="188" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3612;0.3615;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="112" y="188" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3689;0.3692;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="364" y="188" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4228;0.4231;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="400" y="188" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4305;0.4308;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="76" y="224" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4535;0.4538;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="112" y="224" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4612;0.4615;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="364" y="224" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5151;0.5154;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="400" y="224" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5228;0.5231;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="112" y="260" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5535;0.5538;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="148" y="260" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5612;0.5615;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="184" y="260" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5689;0.5692;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="292" y="260" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5920;0.5923;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="328" y="260" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5997;0.6000;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="364" y="260" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6074;0.6077;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="148" y="296" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6535;0.6538;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="184" y="296" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6612;0.6615;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="220" y="296" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6689;0.6692;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="256" y="296" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6766;0.6769;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="292" y="296" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6843;0.6846;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="328" y="296" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6920;0.6923;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="220" y="332" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7612;0.7615;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="256" y="332" width="35" height="35" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7689;0.7692;1.0000" values="0;0;0.9;0.9"/></rect>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.0766;0.0769;0.0843;0.0846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.0843;0.0846;0.0920;0.0923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.0920;0.0923;0.0997;0.1000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.0997;0.1000;0.1074;0.1077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1074;0.1077;0.1151;0.1154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1151;0.1154;0.1228;0.1231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1228;0.1231;0.1305;0.1308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1305;0.1308;0.1382;0.1385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1382;0.1385;0.1458;0.1462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1458;0.1462;0.1535;0.1538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1535;0.1538;0.1612;0.1615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1612;0.1615;0.1689;0.1692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1689;0.1692;0.1766;0.1769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1766;0.1769;0.1843;0.1846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1843;0.1846;0.1920;0.1923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1920;0.1923;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.2074;0.2077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2074;0.2077;0.2151;0.2154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2151;0.2154;0.2228;0.2231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2228;0.2231;0.2305;0.2308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2305;0.2308;0.2382;0.2385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2382;0.2385;0.2458;0.2462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2458;0.2462;0.2535;0.2538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2538;0.2612;0.2615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2612;0.2615;0.2689;0.2692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2689;0.2692;0.2766;0.2769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.33 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2766;0.2769;0.2843;0.2846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2843;0.2846;0.2920;0.2923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2920;0.2923;0.2997;0.3000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.2997;0.3000;0.3074;0.3077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3074;0.3077;0.3151;0.3154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3151;0.3154;0.3228;0.3231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3228;0.3231;0.3305;0.3308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.33 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3305;0.3308;0.3382;0.3385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3382;0.3385;0.3458;0.3462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3458;0.3462;0.3535;0.3538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3535;0.3538;0.3612;0.3615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3612;0.3615;0.3689;0.3692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3689;0.3692;0.3766;0.3769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3766;0.3769;0.3843;0.3846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3843;0.3846;0.3920;0.3923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3920;0.3923;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4074;0.4077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4074;0.4077;0.4151;0.4154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4151;0.4154;0.4228;0.4231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4228;0.4231;0.4305;0.4308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4305;0.4308;0.4382;0.4385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4382;0.4385;0.4458;0.4462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4458;0.4462;0.4535;0.4538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4535;0.4538;0.4612;0.4615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4612;0.4615;0.4689;0.4692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4689;0.4692;0.4766;0.4769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4766;0.4769;0.4843;0.4846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4843;0.4846;0.4920;0.4923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4920;0.4923;0.4997;0.5000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.4997;0.5000;0.5074;0.5077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5074;0.5077;0.5151;0.5154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5151;0.5154;0.5228;0.5231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5228;0.5231;0.5305;0.5308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5305;0.5308;0.5382;0.5385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5382;0.5385;0.5458;0.5462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5458;0.5462;0.5535;0.5538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.33 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5535;0.5538;0.5612;0.5615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5612;0.5615;0.5689;0.5692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5689;0.5692;0.5766;0.5769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5766;0.5769;0.5843;0.5846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5843;0.5846;0.5920;0.5923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5920;0.5923;0.5997;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.5997;0.6000;0.6074;0.6077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.33 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6074;0.6077;0.6151;0.6154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6151;0.6154;0.6228;0.6231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6228;0.6231;0.6305;0.6308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6305;0.6308;0.6382;0.6385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6382;0.6385;0.6458;0.6462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6458;0.6462;0.6535;0.6538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6535;0.6538;0.6612;0.6615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6612;0.6615;0.6689;0.6692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6689;0.6692;0.6766;0.6769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6766;0.6769;0.6843;0.6846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 2.46 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6843;0.6846;0.6920;0.6923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6920;0.6923;0.6997;0.7000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.6997;0.7000;0.7074;0.7077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7074;0.7077;0.7151;0.7154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7151;0.7154;0.7228;0.7231;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7228;0.7231;0.7305;0.7308;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7305;0.7308;0.7382;0.7385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7382;0.7385;0.7458;0.7462;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7458;0.7462;0.7535;0.7538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7535;0.7538;0.7612;0.7615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7612;0.7615;0.7689;0.7692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 1.74 → 輪郭（しきい値 0.8 超え）<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7689;0.7692;0.7766;0.7769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.78 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7766;0.7769;0.7843;0.7846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7843;0.7846;0.7920;0.7923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7920;0.7923;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.7997;0.8000;0.8074;0.8077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">Sobel = 0.00 → 輪郭ではない<animate attributeName="opacity" dur="13s" repeatCount="indefinite" keyTimes="0.0000;0.8074;0.8077;0.8151;0.8154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">灰色が濃い = 手前（深度が小さい）。橙の枠（3×3）を動かして、周囲との差を調べる</text>
<text x="500" y="120" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">手前の楕円と、奥の背景</text>
<text x="500" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">差が大きい所 = 物体の縁</text>
<text x="500" y="184" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">深度だけだと、同じ深さの折れ目は</text>
<text x="500" y="206" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">検出できない → 法線の差も使う</text>
</svg>

<!-- fig:outline-edge-detect:end -->

## 深度によるエッジ

**線形化した深度**に**Sobel を適用**し、**差が一定以上の所を線**に**します**。

```hlsl
float DepthEdge(float2 uv) {
  float center = LinearDepth(uv);
  float edge = Sobel(linear_depth, uv, texel);
  float threshold = kDepthThreshold * center;
  return step(threshold, edge);
}
```

| 点 | 説明 |
| --- | --- |
| **線形な深度を使う** | **非線形な深度では、遠くで差が出ない** |
| **しきい値を深度に比例** | **遠い物体ほど、深度の差が大きく出るので、補正する** |
| **斜めの面の誤検出** | <strong>地面のような、斜めの面は隣の画素で深度が少し違う（勾配）</strong> → **深度の勾配を法線から予測して、差し引く** |

### 斜めの面の誤検出の対策

**斜めの面では隣の画素との深度の差が、自然に生じます**（**エッジではない**）。**法線と視線の角度**から、**その差の予想値**を**求め、予想を超える差だけをエッジ**とします。

```hlsl
float DepthEdgeCorrected(float2 uv, float3 normal, float3 view_dir) {
  float center = LinearDepth(uv);
  float cos_angle = abs(dot(normal, view_dir));
  float expected_difference = center * texel_world_size / max(cos_angle, 0.05);
  float edge = Sobel(linear_depth, uv, texel);
  return step(expected_difference * kSlopeScale + kBias, edge);
}
```

## 法線によるエッジ

**隣り合う法線の差（内積）が小さい所**が**折り目**です。

```hlsl
float NormalEdge(float2 uv) {
  float3 n = normal_buffer.SampleLevel(point_clamp, uv, 0).xyz * 2.0 - 1.0;
  float3 n_r = normal_buffer.SampleLevel(point_clamp, uv + float2(texel.x, 0), 0).xyz * 2.0 - 1.0;
  float3 n_b = normal_buffer.SampleLevel(point_clamp, uv + float2(0, texel.y), 0).xyz * 2.0 - 1.0;
  float d = (1.0 - dot(n, n_r)) + (1.0 - dot(n, n_b));
  return step(kNormalThreshold, d);
}
```

| 点 | 説明 |
| --- | --- |
| **`1 − dot(n, n_neighbor)`** | **同じ向きなら 0、直角で 1** |
| **法線マップの影響** | **細かい凹凸の法線マップが入ると、ノイズ**。**ジオメトリの法線（法線マップなし）を別に使う** |

## ID によるエッジ

**物体 ID・材質 ID を画素ごとに別のバッファへ書き**、**隣と ID が違えば線**とします。

| 用途 | 内容 |
| --- | --- |
| **物体どうしの境** | **キャラクターと背景の境・キャラ同士の境** |
| **材質の境** | **髪と肌・服と肌** |
| **選択した物体の強調** | <strong>選択された ID だけ輪郭を出す（ハイライト）</strong> |

```hlsl
float IdEdge(float2 uv) {
  uint id = id_buffer.Load(int3(uv * resolution, 0));
  uint id_r = id_buffer.Load(int3(uv * resolution + int2(1, 0), 0));
  uint id_b = id_buffer.Load(int3(uv * resolution + int2(0, 1), 0));
  return (id != id_r || id != id_b) ? 1.0 : 0.0;
}
```

## 線の太さ

| 方法 | 内容 |
| --- | --- |
| **サンプル間隔を広げる** | **`texel × 2` など、隣より離れた画素と比べる**と、**線が太くなる** |
| **距離による補正** | <strong>遠くで間隔を狭める（細く）</strong>・**近くで広げる** |
| **複数の間隔を混ぜる** | **細い線 ＋ 太い線で強弱** |
| **ぼかしで太く** | **検出後に軽くぼかして太くする** |

**注意**：**間隔を広げると離れた 2 点の差を見るので、細かい形状の線が出にくく**なります。

## ちらつきと安定

**画面空間のエッジは、カメラが動くと検出される画素が変わり、線がちらつく**ことが**あります**。

| 対策 | 内容 |
| --- | --- |
| **TAA で平均** | **TAA の後に線を引く**のではなく、**線を引いてから TAA** で**滑らかに** |
| <strong>しきい値にソフトな境（`smoothstep`）</strong> | **線の強さが連続的に変わる** |
| **アンチエイリアス済みの深度・法線から検出** | **ジャギーが少ない** |
| **線をジオメトリ側（背面法）で出す部分を併用** | **外側の輪郭は背面法で安定** |

## 色の付け方

| 方法 | 内容 |
| --- | --- |
| **黒** | **標準** |
| **元の色の暗い版** | <strong>柔らかい絵（線が浮かない）</strong> |
| **材質ごとの色** | **肌は赤っぽい、髪は暗い** |
| **深度でフェード** | **遠くの線を薄く** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **深度・法線・ID を組み合わせる** | **内側・外側の線を両方** |
| **斜めの面の補正** | **地面の誤検出を防ぐ** |
| <strong>ジオメトリの法線（法線マップなし）</strong> | **細かい凹凸でノイズが出ない** |
| **TAA を併用** | **ちらつきを抑える** |
| **背面法と併用** | **外側は背面法、内側は画面空間** |
| **線の強さを `smoothstep`** | **滑らか** |

## よくあるミス

??? failure "地面（斜めの面）に、縞のような線が出る"
    **深度の勾配補正**を入れる。

??? failure "法線マップのせいで、細かい線がうるさい"
    **法線マップを含まない、ジオメトリの法線**を別に書く。

??? failure "遠くで線が太く、近くで細い"
    **距離でサンプル間隔を補正**する。

??? failure "動くと線がちらつく"
    **`smoothstep` で滑らかに**、**TAA を併用**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画面空間エッジ ＝ <strong>隣の画素との、深度・法線・ID の差が大きい所を線にする</strong>
    - [x] <strong>深度は外側の輪郭、法線は内側の折り目、ID は物体・材質の境</strong>
    - [x] <strong>Sobel フィルタ</strong>で<strong>勾配の大きさ</strong>を測る
    - [x] <strong>斜めの面の誤検出</strong>は<strong>深度勾配の補正</strong>で防ぐ
    - [x] <strong>背面法と併用</strong>。<strong>TAA でちらつきを抑える</strong>

## 参考

- Saito & Takahashi, "Comprehensible Rendering of 3-D Shapes"（SIGGRAPH 1990）
- Decaudin, "Cartoon-Looking Rendering of 3D-Scenes"（1996）
- Vergne et al., "Apparent Relief"（SIGGRAPH 2011）

## 関連ページ

- [輪郭線・トゥーン](index.md)
- [背面法の輪郭線](outline-hull.md)
- [セル シェーディング](cel-shading.md)
- [TAA](../antialiasing/taa.md)
