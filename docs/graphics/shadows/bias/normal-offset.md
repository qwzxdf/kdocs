---
title: Normal Offset
tags:
  - 描画
---

# Normal Offset

シャドウ マップの比較で面が自分自身の影の中に入ってしまう「アクネ」を防ぐ最も素朴な方法は、比較する深度を少し奥へずらす定数バイアスです。ところが、面が光に対して傾くほど同じ 1 テクセルの中で深度が大きく変わるので、定数のバイアスでは足りません。足りるまで大きくすると影が物から浮く「ピーター パンニング」が出ます。法線オフセットは深度ではなく、影を調べる点そのものを面の法線の向きに少しずらす方法です。点を光の側へ持ち上げると同時に面に沿って横へも動かすので、傾きに応じた補正が自然にかかります。このページではどれだけずらせば足りるかを導きよく見かける 3 つの重みを C++ で比べ、HLSL に落とします。

!!! tip "ポイント"
    - ずらす量はテクセルの大きさ T に比例させる。点サンプリングで足りるのは `d ≥ (T / 2) · sinθ`。PCF の半径が R テクセルなら `d ≥ (0.5 + R) · T · sinθ`。θ は面の法線と光の向きのなす角。
    - 重みに `(1 − N·L)` を使うと小さな傾きで足りない。5° では必要な量の約 10 分の 1 しかなく、45° でも倍率 1 でアクネが 8.8 % 残る。`sinθ` の重みなら倍率 1 で全部の角度が足りた。
    - `tanθ / cosθ` の重みは急な角度で過大になる。60° で必要な量の約 8 倍（倍率 1）になり影が欠ける。
    - 法線オフセットはジオメトリの法線（ノーマル マップなし）でずらす。角では補間した頂点法線を使いずらしすぎないようにする。
    - 小さな定数バイアスは併用する。法線オフセットで大部分を抑え深度の精度の誤差を定数で補う。

!!! info "このページを読む前に"
    - [Shadow Bias](index.md)（このセクション全体の地図と読む順番）
    - [Comparison Samplers](../shadow-map-basics/comparison-sampler.md)（影の比較の流れ）

## 読んだ資料とこのページの範囲 {#sources}

このページは特定の論文を読んで書いたものではありません。Isidoro の "Shadow Mapping: GPU-based Tips and Techniques"（GDC 2006）、Microsoft の "Common Techniques to Improve Shadow Depth Maps"、Dimitrov の "Cascaded Shadow Maps"（NVIDIA、2007）は読んでいません。必要なずらし量の式はこのページで導いたものです。導出が数値実験（C++）と合うことを確かめました。

旧版が書いていた重み `(1 − N·L)` と `sinθ` の 2 つの式は、互いに違う重みでどちらが正しいかの説明がありませんでした。このページで必要な量と比べて、どちらが足りるかを数えました。モデルは 2 次元の断面で光は平行（正射影）、シャドウ マップは点サンプリング（PCF は R で拡張）です。

HLSL は `fxc`（`ps_5_0`）でコンパイルして確かめました。C++ は MSVC で実行しました。

## なぜ自己影が出るのか {#why}

シャドウ マップはテクセルの中心で光から見た深度を保存します。ところが、傾いた面では 1 つのテクセルが覆う面の範囲の中で、深度が変わります。テクセルの幅を T とすると、光に対して角度 θ だけ傾いた面はテクセルの端と中心で、深度が `0.5 · T · tanθ` だけ違います。受け手の点がテクセルの中心から外れるほど保存された深度（中心の深度）より、受け手の深度が奥になり自分自身が影の中にあると判定されます。これがアクネです。

深度に定数バイアスを足すとこの差を埋められますが、必要な量は `tanθ` に比例して傾きとともに急に増えます。θ が 85° に近づくと `tanθ` は 11 を超えます。

<!-- fig:normal-offset:begin -->

<svg class="fig illust motion" data-fig="normal-offset" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-normal-offset" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">法線オフセット:受ける点を法線方向へ少しずらしてから、深度を比べる</text>
<line x1="60" y1="280" x2="700" y2="139.2" stroke="#b8794b" stroke-width="6"/>
<line x1="60" y1="110" x2="60" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="140" y1="110" x2="140" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="220" y1="110" x2="220" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="300" y1="110" x2="300" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="380" y1="110" x2="380" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="460" y1="110" x2="460" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="540" y1="110" x2="540" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="620" y1="110" x2="620" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="700" y1="110" x2="700" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<circle cx="80" cy="275.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="80;80;80;75.27;75.27;75.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="275.6;275.6;275.6;254.11;254.11;254.11"/></circle>
<line x1="80" y1="275.6" x2="75.27" y2="254.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="120" cy="266.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="120;120;120;115.27;115.27;115.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="266.8;266.8;266.8;245.31;245.31;245.31"/></circle>
<line x1="120" y1="266.8" x2="115.27" y2="245.31" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="160" cy="258.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="160;160;160;155.27;155.27;155.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="258;258;258;236.51;236.51;236.51"/></circle>
<line x1="160" y1="258.0" x2="155.27" y2="236.51" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="200" cy="249.2" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="200;200;200;195.27;195.27;195.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="249.2;249.2;249.2;227.71;227.71;227.71"/></circle>
<line x1="200" y1="249.2" x2="195.27" y2="227.71" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="240" cy="240.4" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="240;240;240;235.27;235.27;235.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="240.4;240.4;240.4;218.91;218.91;218.91"/></circle>
<line x1="240" y1="240.4" x2="235.27" y2="218.91" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="280" cy="231.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="280;280;280;275.27;275.27;275.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="231.6;231.6;231.6;210.11;210.11;210.11"/></circle>
<line x1="280" y1="231.6" x2="275.27" y2="210.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="320" cy="222.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="320;320;320;315.27;315.27;315.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="222.8;222.8;222.8;201.31;201.31;201.31"/></circle>
<line x1="320" y1="222.8" x2="315.27" y2="201.31" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="360" cy="214.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="360;360;360;355.27;355.27;355.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="214;214;214;192.51;192.51;192.51"/></circle>
<line x1="360" y1="214.0" x2="355.27" y2="192.51" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="400" cy="205.2" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="400;400;400;395.27;395.27;395.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="205.2;205.2;205.2;183.71;183.71;183.71"/></circle>
<line x1="400" y1="205.2" x2="395.27" y2="183.71" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="440" cy="196.4" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="440;440;440;435.27;435.27;435.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="196.4;196.4;196.4;174.91;174.91;174.91"/></circle>
<line x1="440" y1="196.4" x2="435.27" y2="174.91" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="480" cy="187.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="480;480;480;475.27;475.27;475.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="187.6;187.6;187.6;166.11;166.11;166.11"/></circle>
<line x1="480" y1="187.6" x2="475.27" y2="166.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="520" cy="178.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="520;520;520;515.27;515.27;515.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="178.8;178.8;178.8;157.31;157.31;157.31"/></circle>
<line x1="520" y1="178.8" x2="515.27" y2="157.31" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="560" cy="170.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="560;560;560;555.27;555.27;555.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="170;170;170;148.51;148.51;148.51"/></circle>
<line x1="560" y1="170.0" x2="555.27" y2="148.51" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="600" cy="161.2" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="600;600;600;595.27;595.27;595.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="161.2;161.2;161.2;139.71;139.71;139.71"/></circle>
<line x1="600" y1="161.2" x2="595.27" y2="139.71" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="640" cy="152.4" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="640;640;640;635.27;635.27;635.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="152.4;152.4;152.4;130.91;130.91;130.91"/></circle>
<line x1="640" y1="152.4" x2="635.27" y2="130.91" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="680" cy="143.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="680;680;680;675.27;675.27;675.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="143.6;143.6;143.6;122.11;122.11;122.11"/></circle>
<line x1="680" y1="143.6" x2="675.27" y2="122.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<text x="60" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">面上の点（赤 = 自己遮蔽のアクネ、緑 = OK）。矢印は法線<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="1;1;0;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">法線方向にずらしていく…<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.5997;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光に近い側へ持ち上げたので、アクネが消えた<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5997;0.6000;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">深度ではなく「位置」をずらすので、傾きによらず効く。ずらしすぎると、影の位置がわずかにずれる。</text>
</svg>

<!-- fig:normal-offset:end -->

## どれだけずらせば足りるか {#derive}

法線方向に `d` だけずらすと点は 2 つ動きます。光の側へ `d · cosθ` 持ち上がり面に沿った横方向へ `d · sinθ` ずれます。横にずれるので比べるテクセルも変わります。

受け手の点をずらしたあとの位置で最も近いテクセルの中心から、横に `u` だけ離れているとします（`|u| ≤ 0.5`、単位は T）。平面は `z = x · tanθ` として保存された深度（テクセル中心の平面の深度）とずらした受け手の深度の差は、次のようになります。

`差 = u · tanθ − d / cosθ`

アクネが出ないのは差が 0 以下のときです。最悪は `u = 0.5` なので必要な量は `d ≥ 0.5 · tanθ · cosθ = 0.5 · sinθ` です。**T を掛けて `d ≥ (T / 2) · sinθ`** になります。

PCF で半径 R テクセルの範囲を比べるなら最悪の `u` が `0.5 + R` まで広がるので、`d ≥ (0.5 + R) · T · sinθ` です。

C++ で確かめました。傾きθの平面をシャドウ マップに描きずらし量 `d` を二分探索で変えて、アクネが 0.1 % 未満になる最小の `d` を探しました（T = 1）。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="必要なずらし量(T 単位)と PCF 半径 R"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">必要なずらし量(T 単位)と PCF 半径 R</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="148.61538461538464" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="54" y="83.23076923076925" text-anchor="end" font-size="10" fill="currentColor">2</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="156.42857142857144" y="226" text-anchor="middle" font-size="10" fill="currentColor">15</text><text x="252.85714285714286" y="226" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="349.2857142857143" y="226" text-anchor="middle" font-size="10" fill="currentColor">45</text><text x="445.7142857142857" y="226" text-anchor="middle" font-size="10" fill="currentColor">60</text><text x="542.1428571428571" y="226" text-anchor="middle" font-size="10" fill="currentColor">75</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">面と光のなす角 θ(度)</text><polyline points="60.0,210.0 72.9,208.9 85.7,207.7 98.6,206.6 111.4,205.5 124.3,204.3 137.1,203.2 150.0,202.1 162.9,201.0 175.7,199.9 188.6,198.8 201.4,197.8 214.3,196.7 227.1,195.7 240.0,194.7 252.9,193.7 265.7,192.7 278.6,191.7 291.4,190.8 304.3,189.9 317.1,189.0 330.0,188.1 342.9,187.3 355.7,186.5 368.6,185.7 381.4,185.0 394.3,184.2 407.1,183.6 420.0,182.9 432.9,182.3 445.7,181.7 458.6,181.1 471.4,180.6 484.3,180.1 497.1,179.7 510.0,179.3 522.9,178.9 535.7,178.6 548.6,178.3 561.4,178.0 574.3,177.8 587.1,177.6 600.0,177.5" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">R = 0</text><polyline points="60.0,210.0 72.9,206.6 85.7,203.2 98.6,199.7 111.4,196.4 124.3,193.0 137.1,189.6 150.0,186.3 162.9,183.0 175.7,179.7 188.6,176.5 201.4,173.3 214.3,170.1 227.1,167.0 240.0,164.0 252.9,161.0 265.7,158.0 278.6,155.2 291.4,152.4 304.3,149.6 317.1,147.0 330.0,144.4 342.9,141.9 355.7,139.4 368.6,137.1 381.4,134.9 394.3,132.7 407.1,130.7 420.0,128.7 432.9,126.8 445.7,125.1 458.6,123.4 471.4,121.8 484.3,120.4 497.1,119.1 510.0,117.8 522.9,116.7 535.7,115.7 548.6,114.8 561.4,114.1 574.3,113.4 587.1,112.9 600.0,112.5" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">R = 1</text><polyline points="60.0,210.0 72.9,204.3 85.7,198.6 98.6,192.9 111.4,187.3 124.3,181.6 137.1,176.0 150.0,170.5 162.9,164.9 175.7,159.5 188.6,154.1 201.4,148.8 214.3,143.5 227.1,138.3 240.0,133.3 252.9,128.3 265.7,123.4 278.6,118.6 291.4,113.9 304.3,109.4 317.1,104.9 330.0,100.6 342.9,96.5 355.7,92.4 368.6,88.5 381.4,84.8 394.3,81.2 407.1,77.8 420.0,74.5 432.9,71.4 445.7,68.4 458.6,65.7 471.4,63.1 484.3,60.7 497.1,58.4 510.0,56.4 522.9,54.5 535.7,52.9 548.6,51.4 561.4,50.1 574.3,49.0 587.1,48.1 600.0,47.4" fill="none" stroke="#e5aa28" stroke-width="2.4"/><line x1="470" y1="80" x2="496" y2="80" stroke="#e5aa28" stroke-width="2.4"/><text x="502" y="84" text-anchor="start" font-size="11" fill="currentColor">R = 2</text></svg>

R = 0 では探索の結果はθ = 15° で 0.128、30° で 0.240、45° で 0.339、60° で 0.416 で式 `0.5 sinθ` の 0.129、0.250、0.354、0.433 と 0.015 以内で合いました。R = 1 では 0.386、0.747、1.047、1.293（式は 0.388、0.750、1.061、1.299）、R = 2 では 0.644、1.240、1.754、2.148（式は 0.647、1.250、1.768、2.165）です。**必要な量は `sinθ` に比例し最大でも `(0.5 + R)` テクセル分で頭打ちになります。**

## 3 つの重みを比べる {#weights}

ずらす量を `d = k · T · w(θ)` と書いたとき重み `w` として、よく次の 3 つが書かれます。

- **A: `1 − cosθ`（= `1 − N·L`）。** 小さな角度で効きが弱く、θ に対して 2 次で増えます。
- **B: `sinθ`。** 必要な量の形そのものです。
- **C: `sinθ / cos²θ`（= `tanθ / cosθ`）。** 上限（ここでは 4）つきです。

必要な量（R = 0）は `0.5 · sinθ` なので、B の倍率 `k` は 0.5 で足ります。余裕を見て k = 1 や 2 を使います。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="重みの比較(倍率 1、T 単位)と必要量"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">重みの比較(倍率 1、T 単位)と必要量</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="172.53658536585365" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="54" y="131.0731707317073" text-anchor="end" font-size="10" fill="currentColor">2</text><text x="54" y="89.60975609756096" text-anchor="end" font-size="10" fill="currentColor">3</text><text x="54" y="48.146341463414615" text-anchor="end" font-size="10" fill="currentColor">4</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="156.42857142857144" y="226" text-anchor="middle" font-size="10" fill="currentColor">15</text><text x="252.85714285714286" y="226" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="349.2857142857143" y="226" text-anchor="middle" font-size="10" fill="currentColor">45</text><text x="445.7142857142857" y="226" text-anchor="middle" font-size="10" fill="currentColor">60</text><text x="542.1428571428571" y="226" text-anchor="middle" font-size="10" fill="currentColor">75</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">面と光のなす角 θ(度)</text><polyline points="60.0,210.0 72.9,209.3 85.7,208.6 98.6,207.8 111.4,207.1 124.3,206.4 137.1,205.7 150.0,205.0 162.9,204.3 175.7,203.6 188.6,202.9 201.4,202.2 214.3,201.6 227.1,200.9 240.0,200.3 252.9,199.6 265.7,199.0 278.6,198.4 291.4,197.8 304.3,197.2 317.1,196.7 330.0,196.1 342.9,195.6 355.7,195.1 368.6,194.6 381.4,194.1 394.3,193.7 407.1,193.2 420.0,192.8 432.9,192.4 445.7,192.0 458.6,191.7 471.4,191.4 484.3,191.1 497.1,190.8 510.0,190.5 522.9,190.3 535.7,190.1 548.6,189.9 561.4,189.7 574.3,189.6 587.1,189.5 600.0,189.4" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">必要量(R=0)</text><polyline points="60.0,210.0 72.9,210.0 85.7,209.9 98.6,209.8 111.4,209.6 124.3,209.4 137.1,209.1 150.0,208.8 162.9,208.4 175.7,208.0 188.6,207.5 201.4,207.0 214.3,206.4 227.1,205.8 240.0,205.1 252.9,204.4 265.7,203.7 278.6,202.9 291.4,202.1 304.3,201.2 317.1,200.3 330.0,199.3 342.9,198.4 355.7,197.3 368.6,196.3 381.4,195.2 394.3,194.1 407.1,192.9 420.0,191.7 432.9,190.5 445.7,189.3 458.6,188.0 471.4,186.7 484.3,185.4 497.1,184.1 510.0,182.7 522.9,181.3 535.7,180.0 548.6,178.6 561.4,177.2 574.3,175.7 587.1,174.3 600.0,172.9" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">A: 1-cos</text><polyline points="60.0,210.0 72.9,208.6 85.7,207.1 98.6,205.7 111.4,204.2 124.3,202.8 137.1,201.4 150.0,200.0 162.9,198.6 175.7,197.2 188.6,195.8 201.4,194.5 214.3,193.1 227.1,191.8 240.0,190.5 252.9,189.3 265.7,188.0 278.6,186.8 291.4,185.6 304.3,184.5 317.1,183.3 330.0,182.3 342.9,181.2 355.7,180.2 368.6,179.2 381.4,178.2 394.3,177.3 407.1,176.5 420.0,175.6 432.9,174.8 445.7,174.1 458.6,173.4 471.4,172.7 484.3,172.1 497.1,171.6 510.0,171.0 522.9,170.6 535.7,170.1 548.6,169.8 561.4,169.4 574.3,169.2 587.1,168.9 600.0,168.8" fill="none" stroke="#e5aa28" stroke-width="2.4"/><line x1="470" y1="80" x2="496" y2="80" stroke="#e5aa28" stroke-width="2.4"/><text x="502" y="84" text-anchor="start" font-size="11" fill="currentColor">B: sin</text><polyline points="60.0,210.0 72.9,208.6 85.7,207.1 98.6,205.6 111.4,204.1 124.3,202.6 137.1,201.0 150.0,199.3 162.9,197.6 175.7,195.8 188.6,193.9 201.4,191.9 214.3,189.8 227.1,187.5 240.0,185.0 252.9,182.4 265.7,179.4 278.6,176.3 291.4,172.8 304.3,168.9 317.1,164.6 330.0,159.8 342.9,154.3 355.7,148.2 368.6,141.2 381.4,133.1 394.3,123.8 407.1,112.9 420.0,100.1 432.9,84.8 445.7,66.4 458.6,44.1 471.4,44.1 484.3,44.1 497.1,44.1 510.0,44.1 522.9,44.1 535.7,44.1 548.6,44.1 561.4,44.1 574.3,44.1 587.1,44.1 600.0,44.1" fill="none" stroke="#e5484d" stroke-width="2.4"/><line x1="470" y1="96" x2="496" y2="96" stroke="#e5484d" stroke-width="2.4"/><text x="502" y="100" text-anchor="start" font-size="11" fill="currentColor">C: tan/cos</text></svg>

アクネの割合を数えました（バイアスなし、点サンプリング）。何もしないとどの角度でも約 49.6 % が自己影になります。A は k = 1 で 5° が 45.6 %、15° が 36.8 %、30° が 23.2 %、45° が 8.8 %、60° 以上で 0 % です。k = 2 でも 5° が 41.2 %、15° が 23.6 % で残り 30° 以上で 0 % になります。**A は傾きが小さい面ほど足りません。** 小さな傾きは `1 − cosθ ≈ θ²/2` で必要な `0.5 sinθ ≈ 0.5θ` に比べて、ほとんど 0 になるからです。B と C は k = 1 と k = 2 の全部の角度で、0 % でした。

ただし、C は必要な量より急な角度でずっと大きく外します。倍率 1 でも 60° で C は 3.464（必要量 0.430 の約 8 倍）、75° では上限の 4.0 です。ずらしすぎると影が面から離れて欠けます。**B が必要な量に最も近い扱いやすい重み**です。

## 実装 {#implementation}

3 つの重みを HLSL で書き並べます。実際には B だけを使います。

```hlsl
// 法線オフセット: 影を調べる点を、面の法線の向きに少しずらしてから、光の空間へ変換する。
// 3 つの重み（光に対する面の傾きθに応じて、どれだけずらすか）を並べて書く。
//   A: (1 - cosθ)      B: sinθ      C: tanθ / cosθ を上限つきで（自己影を防ぐのに必要な量に合わせた式）
// θ は面の法線 N と、光へ向かう向き L のなす角。座標は左手系・Y-up。「足した」と書いた値は、このページが決めたもの。

Texture2D<float> g_shadow_map : register(t0);
SamplerComparisonState g_shadow_cmp : register(s0);

cbuffer ShadowCB : register(b0) {
  float4x4 g_shadow_matrix;     // ワールド → 光のクリップ空間（行ベクトル用）
  float g_texel_world;          // シャドウ マップの 1 テクセルのワールドでの大きさ [m]（カスケードごとに違う）
  float g_normal_offset_scale;  // ずらす量の倍率（テクセル単位。例: 1〜2）
  float g_const_bias;           // 小さな定数バイアス（NDC の z 単位。足した値の例: 0.0002）
  float g_max_tan;              // 重み C の tanθ の上限（足した値の例: 4）
};

// ================= 重み =================

float WeightA(float n_dot_l) { return 1.0 - n_dot_l; }          // 小さな傾きで効きが弱い（θ² に比例）
float WeightB(float n_dot_l) { return sqrt(max(1.0 - n_dot_l * n_dot_l, 0.0)); }   // sinθ。傾きにほぼ比例
float WeightC(float n_dot_l) {                                  // tanθ / cosθ（上限つき）
  float cos_t = max(n_dot_l, 0.05);                             // 0 割りを避ける下限（足した値）
  float sin_t = sqrt(max(1.0 - n_dot_l * n_dot_l, 0.0));
  return min(sin_t / (cos_t * cos_t), g_max_tan);               // 斜めすぎる面では上限で打ち切る（ずらしすぎて影が欠けるのを防ぐ）
}

// ================= 位置をずらす =================

// 面の法線 N（ジオメトリの法線。ノーマル マップは使わない）、光へ向かう向き L（単位ベクトル）。
float3 NormalOffsetPosition(float3 world_pos, float3 n, float3 l, int mode) {
  float n_dot_l = saturate(dot(n, l));
  float w = (mode == 0) ? WeightA(n_dot_l) : ((mode == 1) ? WeightB(n_dot_l) : WeightC(n_dot_l));
  return world_pos + n * (g_normal_offset_scale * g_texel_world * w);
}

// ================= 影を引く =================

float ShadowNormalOffset(float3 world_pos, float3 n, float3 l, int mode) {
  float3 p = NormalOffsetPosition(world_pos, n, l, mode);
  float4 clip = mul(float4(p, 1.0), g_shadow_matrix);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) return 1.0;
  return g_shadow_map.SampleCmpLevelZero(g_shadow_cmp, uv, ndc.z - g_const_bias);   // 小さな定数バイアスは併用する
}

// ================= ジオメトリの法線の選び方 =================

// 頂点法線を補間した法線は、角で滑らかに変わる。面法線（ddx/ddy の外積）は、三角形ごとに一定。
float3 GeometryNormalFromDerivatives(float3 world_pos) {
  return normalize(cross(ddx(world_pos), ddy(world_pos)));      // 面法線。向きは三角形の巻き順による（符号に注意）
}

float4 NormalOffsetPS(float4 pos : SV_Position, float3 world : TEXCOORD0, float3 normal : NORMAL, float3 light_dir : TEXCOORD1) : SV_Target {
  float3 n = normalize(normal);                                  // 補間した頂点法線
  float a = ShadowNormalOffset(world, n, light_dir, 0);
  float b = ShadowNormalOffset(world, n, light_dir, 1);
  float c = ShadowNormalOffset(world, n, light_dir, 2);
  float3 fn = GeometryNormalFromDerivatives(world);
  return float4(a, b, c, dot(fn, n) * 0.0);
}
```

`g_texel_world` はシャドウ マップの 1 テクセルのワールドでの大きさです。太陽（正射影）のカスケードなら `カスケードの幅 ÷ 解像度` です。カスケードごとに値が違います。遠いカスケードほどテクセルが大きいので、ずらす量も大きくなります。`g_normal_offset_scale` は倍率 `k` で PCF の半径 R に応じて `0.5 + R` 以上にします。たとえば 3×3 の PCF（4×4 テクセルの範囲、R = 1.5 とみなす）なら 2 以上が目安です。

`WeightB` は `sqrt(1 − (N·L)²)` で `sinθ` を出します。`NormalOffsetPosition` は `world_pos + n × (k × T × w)` です。**ずらすのはシャドウ マップを引く位置だけ**で、陰影計算の位置には使いません。使うとライティングが面の少し上で計算されます。

`ShadowNormalOffset` はずらした位置を光の空間へ変換し、比較サンプラーで引きます。最後の `ndc.z − g_const_bias` が併用する小さな定数バイアスです。法線オフセットは傾きによる量を受け持ち深度の精度の誤差（量子化）は、小さな定数で補います。

## ずらすことの副作用 {#side-effects}

法線オフセットは深度を動かさずに位置を動かすので、ピーター パンニングが出にくい方法です。ただし、副作用がないわけではありません。

**影が少しずれます。** ずらし量 `d = sinθ`（k = 1）のとき影の位置は面に沿って `d · sinθ` ずれ光の側へ `d · cosθ` 浮きます。θ = 15° で横に 0.067 T、持ち上がり 0.250 T。45° ではどちらも 0.5 T。75° で横 0.933 T、持ち上がり 0.250 T です。k が 2 なら倍になります。T が 2.4 cm なら最大でも数 cm のずれです。

**物の角で欠けることがあります。** 角で法線方向にずらすと隣の面の内側に入り影が欠けます。対策は倍率を控えめにすること（1〜2）、頂点法線を補間した滑らかな法線を使うこと定数バイアスと併用して、法線オフセットの量を減らすことです。

**法線はジオメトリの法線を使います。** ノーマル マップで細かく変わる法線を使うとずらし方がばらついて、影がちらつきます。HLSL の `GeometryNormalFromDerivatives` は画面微分で面法線を求める例です。向きは三角形の巻き順で変わるので、符号に注意してください。

## 他のバイアスとの組み合わせ {#combine}

実用的な構成は次の通りです。法線オフセットが斜めの面の自己影を抑えます（ワールド距離で指定）。小さな定数バイアスが深度の量子化誤差を補います。傾き依存のハードウェア バイアスをごく小さく足す手もあります。どれも大きくすると副作用が出るので、小さな値を組み合わせるのがコツです。傾き依存のバイアスは [Slope-Scale Bias](slope-scale-bias.md)、受け手の平面から出す方法は [Receiver Plane Bias](receiver-plane-bias.md) を見てください。

## 数字を出した C++ {#experiment}

```cpp
// 法線オフセットの効きを、2 次元の断面で数える。
// 光は +z 向き（z が大きいほど光から遠い）。シャドウ マップは 1 次元の深度列（テクセルの幅 T = 1）で、
// 平面 z = x tanθ（光に対する傾きθ）を描いて、テクセル中心の深度を保存する。
// 受け手は同じ平面の上の点。法線オフセットで点をずらし、最も近いテクセルの深度と比べる（点サンプリング、バイアスなし）。
//   [1] 自己影を防ぐのに必要なずらし量と、3 つの重みの比較
//   [2] 自己影（アクネ）の割合
//   [3] ずらしたぶんの、影の位置のずれ
//   [4] PCF の半径 R テクセルでの、必要なずらし量（導出 d = (0.5 + R) sinθ との一致）
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr double kPi = 3.14159265358979323846;

// 断面で、受け手の点を d だけ法線方向にずらして比べる。光に近い側が「小さい z」。
// 戻り値は、自己影になった点（アクネ）の割合。
static double AcneFraction(double theta, double d, double const_bias) {
  double tn = std::tan(theta);
  int n_samples = 20000, bad = 0;
  double nx = std::sin(theta), nz = -std::cos(theta);            // 法線（光の側を向く）
  for (int i = 0; i < n_samples; ++i) {
    double x = 10.0 + 80.0 * i / n_samples;                      // 受け手の位置（テクセル 10〜90）
    double z = x * tn;                                           // 平面の深度
    double px = x + d * nx, pz = z + d * nz;                     // 法線方向にずらした点
    double tx = std::floor(px) + 0.5;                            // 最も近いテクセルの中心（T = 1）
    double stored = tx * tn;                                     // そのテクセルに保存された深度（平面上）
    if (pz - const_bias > stored) ++bad;                         // 受け手が保存深度より奥 → 影（自己影）
  }
  return (double)bad / n_samples;
}

int main() {
  // ---- [1] 必要なずらし量 ----
  // 受け手の x がテクセル中心から最大 0.5 離れるとき、平面の深度差は 0.5 tanθ。
  // 法線方向 d のずらしは、深度を d cosθ だけ光側へ動かし、横を d sinθ 動かす。
  // 横ずれで最も近いテクセルが変わる影響も含めて、数値で最小の d を探す（アクネがほぼ 0 になる d）。
  std::printf("[1] required normal offset d (in texels) so that acne < 0.1 %%, vs the three weights (scale k = 1 and 2)\n");
  std::printf("theta  tan      required d   A:k(1-cos)   B:k sin     C:k tan/cos (cap 4)   [k=1 | k=2]\n");
  for (double deg : {5.0, 15.0, 30.0, 45.0, 60.0, 75.0, 85.0}) {
    double th = deg * kPi / 180;
    double lo = 0, hi = 40;
    for (int it = 0; it < 40; ++it) {
      double mid = 0.5 * (lo + hi);
      (AcneFraction(th, mid, 0) < 0.001 ? hi : lo) = mid;
    }
    double a = 1 - std::cos(th), b = std::sin(th), c = std::min(std::sin(th) / (std::cos(th) * std::cos(th)), 4.0);
    std::printf("%3.0f    %6.3f   %7.3f      %.3f|%.3f   %.3f|%.3f   %.3f|%.3f\n", deg, std::tan(th), hi, a, 2 * a, b, 2 * b, c, 2 * c);
  }

  // ---- [2] アクネの割合 ----
  std::printf("\n[2] acne fraction (%%) for each method (no constant bias)\n");
  std::printf("theta   none     A k=1    A k=2    B k=1    B k=2    C k=1    C k=2\n");
  for (double deg : {5.0, 15.0, 30.0, 45.0, 60.0, 75.0}) {
    double th = deg * kPi / 180;
    double a = 1 - std::cos(th), b = std::sin(th), c = std::min(std::sin(th) / (std::cos(th) * std::cos(th)), 4.0);
    std::printf("%3.0f    %6.2f  %6.2f   %6.2f   %6.2f   %6.2f   %6.2f   %6.2f\n", deg, 100 * AcneFraction(th, 0, 0),
                100 * AcneFraction(th, a, 0), 100 * AcneFraction(th, 2 * a, 0), 100 * AcneFraction(th, b, 0), 100 * AcneFraction(th, 2 * b, 0),
                100 * AcneFraction(th, c, 0), 100 * AcneFraction(th, 2 * c, 0));
  }

  // ---- [3] ずれ ----
  // 法線オフセットで点を d 動かすと、影の位置が面に沿って d sinθ ずれ、光の側へ d cosθ 浮く。
  std::printf("\n[3] shadow displacement along the surface for offset d = B(k=1) = sin(theta): d sin(theta)\n");
  for (double deg : {15.0, 45.0, 75.0}) {
    double th = deg * kPi / 180;
    std::printf("theta %2.0f: d = %.3f T, lateral shift %.3f T, lift %.3f T\n", deg, std::sin(th), std::sin(th) * std::sin(th),
                std::sin(th) * std::cos(th));
  }

  // ---- [4] PCF の半径 ----
  // 半径 R の PCF は、受け手から ±R テクセル離れた点でも比べる。1 つでも影になれば（最悪の場合）アクネになる。
  // 導出: ずらした点の最寄りテクセル中心とのずれ u（|u| <= 0.5 + R）で、diff = u tanθ - d / cosθ <= 0 → d >= (0.5 + R) sinθ。
  std::printf("\n[4] PCF radius R: required d (texels) found by search vs (0.5 + R) sin(theta)\n");
  std::printf("theta  R=0 found/formula    R=1 found/formula    R=2 found/formula\n");
  for (double deg : {15.0, 30.0, 45.0, 60.0}) {
    double th = deg * kPi / 180;
    std::printf("%3.0f   ", deg);
    for (int R : {0, 1, 2}) {
      double lo = 0, hi = 40;
      for (int it = 0; it < 40; ++it) {
        double mid = 0.5 * (lo + hi);
        int bad = 0, n = 4000;                                   // 受け手の x を細かく走査する
        double tn = std::tan(th), nx = std::sin(th), nz = -std::cos(th);
        for (int i = 0; i < n; ++i) {
          double x = 10.0 + 80.0 * i / n, z = x * tn;
          double px = x + mid * nx, pz = z + mid * nz;           // 法線方向にずらした点
          bool any_shadow = false;
          for (int k = -R; k <= R; ++k) {                        // PCF の 2R+1 点（整数テクセルずつ）
            double tx = std::floor(px) + 0.5 + k;
            if (pz > tx * tn) any_shadow = true;
          }
          bad += any_shadow;
        }
        ((double)bad / n < 0.001 ? hi : lo) = mid;
      }
      std::printf("   %5.3f / %5.3f   ", hi, (0.5 + R) * std::sin(th));
    }
    std::printf("\n");
  }
  return 0;
}
```

```text title="実行結果"
[1] required normal offset d (in texels) so that acne < 0.1 %, vs the three weights (scale k = 1 and 2)
theta  tan      required d   A:k(1-cos)   B:k sin     C:k tan/cos (cap 4)   [k=1 | k=2]
  5     0.087     0.044      0.004|0.008   0.087|0.174   0.088|0.176
 15     0.268     0.129      0.034|0.068   0.259|0.518   0.277|0.555
 30     0.577     0.248      0.134|0.268   0.500|1.000   0.667|1.333
 45     1.000     0.351      0.293|0.586   0.707|1.414   1.414|2.828
 60     1.732     0.430      0.500|1.000   0.866|1.732   3.464|6.928
 75     3.732     0.480      0.741|1.482   0.966|1.932   4.000|8.000
 85    11.430     0.498      0.913|1.826   0.996|1.992   4.000|8.000
```

```text title="実行結果（続き）"
[2] acne fraction (%) for each method (no constant bias)
theta   none     A k=1    A k=2    B k=1    B k=2    C k=1    C k=2
  5     49.60   45.60    41.20     0.00     0.00     0.00     0.00
 15     49.60   36.80    23.60     0.00     0.00     0.00     0.00
 30     49.60   23.20     0.00     0.00     0.00     0.00     0.00
 45     49.60    8.80     0.00     0.00     0.00     0.00     0.00
 60     49.60    0.00     0.00     0.00     0.00     0.00     0.00
 75     49.60    0.00     0.00     0.00     0.00     0.00     0.00
```

```text title="実行結果（続き）"
[3] shadow displacement along the surface for offset d = B(k=1) = sin(theta): d sin(theta)
theta 15: d = 0.259 T, lateral shift 0.067 T, lift 0.250 T
theta 45: d = 0.707 T, lateral shift 0.500 T, lift 0.500 T
theta 75: d = 0.966 T, lateral shift 0.933 T, lift 0.250 T
```

```text title="実行結果（続き）"
[4] PCF radius R: required d (texels) found by search vs (0.5 + R) sin(theta)
theta  R=0 found/formula    R=1 found/formula    R=2 found/formula
 15      0.128 / 0.129      0.386 / 0.388      0.644 / 0.647   
 30      0.240 / 0.250      0.747 / 0.750      1.240 / 1.250   
 45      0.339 / 0.354      1.047 / 1.061      1.754 / 1.768   
 60      0.416 / 0.433      1.293 / 1.299      2.148 / 2.165
```

## よくあるミス {#mistakes}

??? failure "重みを `1 − N·L` にして、緩い傾きの面にアクネが残る"
    小さな傾きで重みが小さくなりすぎる。`sinθ` にする。

??? failure "ずらしすぎて、細い物の影や角の影が欠ける"
    倍率が大きすぎるまたは `tanθ / cosθ` のような急に増える重みを使っている。倍率は PCF の半径に合わせて `0.5 + R` から 2 程度にする。

??? failure "遠いカスケードで、アクネが戻ってくる"
    テクセルの大きさをカスケードごとに計算していない。ずらす量は T に比例する。

??? failure "ノーマル マップのある面で、影がちらつく"
    ずらす向きにシェーディング用の法線を使っている。ジオメトリの法線を使う。

??? failure "ライティングまで、ずらした位置で計算している"
    ずらすのはシャドウ マップを引く位置だけ。陰影計算にはもとの位置を使う。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 法線方向に `(T / 2) · sinθ` 以上ずらせば、点サンプリングのアクネは出ない。PCF の半径 R なら `(0.5 + R) · T · sinθ`。
    - [x] 重みは `sinθ`。`1 − N·L` は小さな傾きで足りず `tanθ / cosθ` は急な角度で過大。
    - [x] テクセルの大きさはカスケードごとに計算する。
    - [x] ジオメトリの法線を使い小さな定数バイアスを併用する。

## 参考 {#references}

- Christopher Oat, John Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006. 読んでいない。
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps". 読んでいない。
- Rouslan Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007. 読んでいない。
- 必要なずらし量 `(0.5 + R) · T · sinθ` の導出と 3 つの重みの比較は、このページで行ったもの。モデルは 2 次元の断面、平行光、点サンプリング。実機のシャドウ マップの形式やバイアスの設定による違いは確かめていない。

## 関連ページ {#related}

- [Shadow Bias](index.md)
- [Constant Bias](constant-bias.md)
- [Slope-Scale Bias](slope-scale-bias.md)
- [Receiver Plane Bias](receiver-plane-bias.md)
- [Peter Panning](peter-panning.md)
