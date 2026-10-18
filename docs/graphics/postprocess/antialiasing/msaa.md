---
title: MSAA
tags:
  - 描画
---

# MSAA

<strong>MSAA（マルチサンプル アンチエイリアス）</strong>は、<strong>三角形の縁だけを、1 画素に複数のサンプル点で判定して、滑らかにする</strong>方式です。<strong>ピクセル シェーダーは 1 画素につき 1 回だけ</strong>走るので、画素を全部 4 倍や 8 倍に増やす SSAA より、はるかに安いのにジオメトリの縁のジャギーはしっかり消せます。ただし、シェーダー内のエイリアシングには効かず、ディファード レンダリングとは相性が悪いという弱点があります。このページでは、SSAA との違い・サンプル パターン・カバレッジとリゾルブ・DX11 の設定・弱点と対処を説明します。

!!! tip "ポイント"
    - MSAA ＝ <strong>1 画素に複数のサンプル点（2・4・8）</strong>。<strong>三角形が各サンプルを覆うかを判定</strong>。
    - <strong>ピクセル シェーダーは 1 画素 1 回</strong>。<strong>覆ったサンプルすべてに同じ色を書く</strong>。
    - 縁の画素だけ<strong>サンプルごとに色が違う</strong>→ <strong>リゾルブ（平均）</strong>で<strong>滑らかな縁</strong>。
    - <strong>効く</strong>のは<strong>ジオメトリの縁</strong>。<strong>効かない</strong>のは<strong>シェーダー内・テクスチャ内</strong>のエイリアシング。
    - <strong>メモリと帯域が サンプル数 倍</strong>。<strong>ディファードの G バッファは特に重い</strong>。
    - <strong>VR・モバイル（タイルベース）</strong>では<strong>今も現役</strong>。

<!-- fig:msaa-samples:begin -->

<svg class="fig illust motion" data-fig="msaa-samples" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-msaa-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">MSAA: 縁の判定(カバレッジ)だけ 4 倍に増やし、色の計算は、画素に 1 回で済ませる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">三角形の縁。1 画素に 4 つのサンプル点。何個が三角形の中かを数えて、その割合で色を混ぜる</text>
<rect x="30" y="100" width="259.2" height="172.8" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">① MSAA なし(中心で 1 回判定)</text>
<rect x="335" y="100" width="259.2" height="172.8" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">② MSAA 4x(4 サンプルで判定)</text>
<rect x="640" y="100" width="259.2" height="172.8" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">③ 正解(1 画素 64 サンプル)</text>
<rect x="30.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="51.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="73.2" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="94.8" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="116.4" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="138.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="159.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="181.2" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="202.8" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="224.4" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="73.2" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="94.8" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="116.4" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="138.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="159.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="181.2" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="202.8" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="224.4" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="73.2" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="94.8" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="116.4" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="138.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="159.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="181.2" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="202.8" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="224.4" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="73.2" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="94.8" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="116.4" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="138.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="159.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="181.2" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="202.8" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="224.4" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="73.2" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="94.8" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="116.4" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="138.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="159.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="181.2" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="202.8" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="224.4" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="73.2" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="94.8" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="116.4" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="138.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="159.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="181.2" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="202.8" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="224.4" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="73.2" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="94.8" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="116.4" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="138.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="159.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="181.2" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#2673d9"/></rect>
<rect x="202.8" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#2673d9"/></rect>
<rect x="224.4" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="246.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="267.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="30.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="51.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="73.2" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="94.8" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="116.4" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="138.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="159.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="181.2" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#2673d9"/></rect>
<rect x="202.8" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#2673d9"/></rect>
<rect x="224.4" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#2673d9"/></rect>
<rect x="246.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#2673d9"/></rect>
<rect x="267.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="356.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="378.2" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="399.8" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="421.4" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="443.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="464.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="486.2" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="507.8" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="529.4" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="551.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="356.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#c1d4ee"/></rect>
<rect x="378.2" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="399.8" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="421.4" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="443.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="464.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="486.2" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="507.8" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="529.4" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="551.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="356.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="378.2" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="399.8" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="421.4" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="443.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="464.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="486.2" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="507.8" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="529.4" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="551.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="356.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="378.2" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="399.8" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="421.4" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="443.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="464.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="486.2" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="507.8" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="529.4" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="551.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="356.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="378.2" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="399.8" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="421.4" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="443.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="464.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="486.2" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="507.8" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="529.4" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="551.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="356.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="378.2" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="399.8" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="421.4" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="443.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="464.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="486.2" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="507.8" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="529.4" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="551.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="356.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="378.2" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="399.8" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="421.4" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="443.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="464.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="486.2" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#2673d9"/></rect>
<rect x="507.8" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#5a93e0"/></rect>
<rect x="529.4" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="551.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="572.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="335.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="356.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="378.2" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="399.8" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="421.4" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="443.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="464.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="486.2" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#2673d9"/></rect>
<rect x="507.8" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#2673d9"/></rect>
<rect x="529.4" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#2673d9"/></rect>
<rect x="551.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#8eb4e7"/></rect>
<rect x="572.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="661.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="683.2" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="704.8" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="726.4" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="748.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="769.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="791.2" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="812.8" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="834.4" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="856.0" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="100.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#538fdf"/></rect>
<rect x="661.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#cedcf0"/></rect>
<rect x="683.2" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="704.8" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="726.4" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="748.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="769.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="791.2" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="812.8" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="834.4" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="856.0" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="121.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="661.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2975d9"/></rect>
<rect x="683.2" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#84aee5"/></rect>
<rect x="704.8" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#ebeff3"/></rect>
<rect x="726.4" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="748.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="769.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="791.2" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="812.8" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="834.4" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="856.0" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="143.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="661.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="683.2" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="704.8" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#3d81dc"/></rect>
<rect x="726.4" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#b4ccec"/></rect>
<rect x="748.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="769.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="791.2" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="812.8" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="834.4" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="856.0" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="164.8" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="661.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="683.2" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="704.8" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="726.4" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="748.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#679be2"/></rect>
<rect x="769.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#dee7f2"/></rect>
<rect x="791.2" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="812.8" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="834.4" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="856.0" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="186.4" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="661.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="683.2" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="704.8" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="726.4" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="748.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="769.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#3079da"/></rect>
<rect x="791.2" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#97bae8"/></rect>
<rect x="812.8" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#f2f3f4"/></rect>
<rect x="834.4" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="856.0" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="208.0" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="661.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="683.2" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="704.8" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="726.4" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="748.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="769.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="791.2" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#2673d9"/></rect>
<rect x="812.8" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#4d8bde"/></rect>
<rect x="834.4" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#c8d8ef"/></rect>
<rect x="856.0" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="877.6" y="229.6" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="640.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#2673d9"/></rect>
<rect x="661.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#2673d9"/></rect>
<rect x="683.2" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#2673d9"/></rect>
<rect x="704.8" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#2673d9"/></rect>
<rect x="726.4" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#2673d9"/></rect>
<rect x="748.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#2673d9"/></rect>
<rect x="769.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2673d9"/></rect>
<rect x="791.2" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#2673d9"/></rect>
<rect x="812.8" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#2673d9"/></rect>
<rect x="834.4" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#2673d9"/></rect>
<rect x="856.0" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#7aa8e4"/></rect>
<rect x="877.6" y="251.2" width="21.9" height="21.9" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#e8edf3"/></rect>
<rect x="335.0" y="121.6" width="21.6" height="21.6" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1628;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1628;1.0000" values="0;0;1;1"/><rect x="600" y="330" width="130.0" height="130.0" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<polygon points="0,0" fill="none"/>
<line x1="626.0" y1="333.12" x2="730.0" y2="397.6" stroke="#1f2937" stroke-width="3"/>
<circle cx="616.25" cy="411.25" r="9" fill="#2563eb" stroke="#334155" stroke-width="2"/>
<circle cx="648.75" cy="346.25" r="9" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
<circle cx="681.25" cy="443.75" r="9" fill="#2563eb" stroke="#334155" stroke-width="2"/>
<circle cx="713.75" cy="378.75" r="9" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
<text x="600" y="320" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">赤枠の画素を拡大: 4 サンプル</text>
<text x="742.0" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">三角形の中: 2 / 4 個</text>
<text x="742.0" y="386" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">色 = 三角形 0.50 + 背景 0.50</text>
<text x="742.0" y="406" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(色の計算は 1 回)</text>
</g>
<text x="40" y="336" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">色を計算した回数(画素シェーダー):</text>
<text x="40" y="366" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">MSAA 4x:</text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.0742;0.0744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">14<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0742;0.0744;0.0789;0.0791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">20<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0789;0.0791;0.0835;0.0837;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">25<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0835;0.0837;0.0882;0.0884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">30<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;0.0928;0.0930;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">34<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0928;0.0930;0.0975;0.0977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">37<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0975;0.0977;0.1021;0.1023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">40<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1021;0.1023;0.1068;0.1070;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">42<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1068;0.1070;0.1114;0.1116;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">44<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1114;0.1116;0.1161;0.1163;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">45<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1161;0.1163;0.1207;0.1209;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="369" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">45<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1207;0.1209;1.0000" values="0;0;1;1"/></text>
<text x="40" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">解像度を 4 倍にして描く(SSAA):</text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.0742;0.0744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">56<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0742;0.0744;0.0789;0.0791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">80<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0789;0.0791;0.0835;0.0837;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">100<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0835;0.0837;0.0882;0.0884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">120<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;0.0928;0.0930;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">136<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0928;0.0930;0.0975;0.0977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">148<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0975;0.0977;0.1021;0.1023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">160<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1021;0.1023;0.1068;0.1070;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">168<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1068;0.1070;0.1114;0.1116;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">176<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1114;0.1116;0.1161;0.1163;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">180<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1161;0.1163;0.1207;0.1209;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="403" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">180<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1207;0.1209;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2556;0.2558;1.0000" values="0;0;1;1"/><rect x="30" y="430" width="560" height="88" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="454" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">正解とのずれ: なし 0.016 → MSAA 0.008</text>
<text x="46" y="478" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">色の計算 45 回 vs SSAA 180 回(4 倍)。判定とメモリだけ 4 倍</text>
<text x="46" y="501" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">内側の画素は、4 サンプルとも同じ → 色は 1 回で足りる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縁の画素は、三角形に半分だけかかっている<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">4 つのサンプル点が、三角形の中か外かを、画素ごとに数える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.1626;0.1628;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">中の数の割合で、三角形の色と背景を混ぜる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1628;0.2556;0.2558;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">色の計算は 1 画素 1 回のまま。解像度を上げるより、ずっと安い<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2556;0.2558;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:msaa-samples:end -->

## SSAA との違い

<strong>SSAA（スーパー サンプリング）</strong>は、<strong>画面全体を縦横 2 倍（面積 4 倍）で描いて縮小</strong>する方式です。<strong>最も高品質</strong>ですがピクセル シェーダーも 4 倍回るので、非常に重いです。

SSAA 4x と MSAA 4x を比べます。SSAA 4x は、ピクセル シェーダーが 4 倍、メモリも 4 倍で、縁もシェーダー内も滑らかになります。MSAA 4x は、ピクセル シェーダーは 1 倍で済み、メモリ（カラーと深度）は 4 倍ですが、縁は滑らかになるものの、シェーダー内のエイリアシングには効きません。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="MSAA のサンプル">
<text x="20" y="26" class="fig-title">MSAA：縁をまたぐ画素だけ、サンプルごとに「覆っているか」を判定</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">1 サンプル（通常）</text>
<rect x="0" y="0" width="160" height="160" fill="#f8fafc" stroke="#94a3b8"/>
<polygon points="0,160 160,160 160,0" fill="#2563eb" fill-opacity="0.25"/>
<g fill="#334155"><rect x="80" y="80" width="80" height="80" opacity="0.6"/></g>
<circle cx="120" cy="120" r="4" fill="#fff"/>
<text x="0" y="182" style="font-size:12px">画素の中心だけで判定 → 全部か、ゼロ</text>
</g>
<g transform="translate(300,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">4 サンプル（MSAA 4x）</text>
<rect x="0" y="0" width="160" height="160" fill="#f8fafc" stroke="#94a3b8"/>
<polygon points="0,160 160,160 160,0" fill="#2563eb" fill-opacity="0.25"/>
<g stroke="#94a3b8"><line x1="80" y1="0" x2="80" y2="160"/><line x1="0" y1="80" x2="160" y2="80"/></g>
<circle cx="50" cy="50" r="5" fill="#94a3b8"/><circle cx="110" cy="40" r="5" fill="#94a3b8"/><circle cx="40" cy="110" r="5" fill="#2563eb"/><circle cx="110" cy="115" r="5" fill="#2563eb"/>
<text x="0" y="182" style="font-size:12px">4 点のうち 2 点が内側 → 50 % の色</text>
</g>
<g font-size="13"><text x="520" y="100" style="font-weight:700">リゾルブ（解像）</text>
<text x="520" y="124">各画素のサンプルを平均して</text>
<text x="520" y="146">最終的な 1 画素の色にする</text></g>
</svg>

## 仕組み

| 手順 | 内容 |
| --- | --- |
| ① 各サンプルのカバレッジ | 三角形が画素内の複数のサンプル点を、それぞれ覆うかを判定（ラスタライザ） |
| ② ピクセル シェーダーは 1 回 | 画素ごとに 1 回、色を計算（画素の中心付近） |
| ③ 覆ったサンプルに書く | その色を覆ったサンプルすべてに書く（深度はサンプルごとに別） |
| ④ リゾルブ | 各画素のサンプルを平均して、1 つの色に |

<strong>内側の画素</strong>は<strong>全サンプルが同じ色</strong>なので、平均しても変わりません。縁の画素だけ、<strong>サンプルごとに色が違い（三角形の色と背景の色）</strong>、平均すると中間色になり、滑らかになります。

## サンプル パターン

<strong>サンプル点の位置</strong>は、<strong>規則格子ではなく、回転した（ずらした）配置</strong>が使われます。

サンプル点の位置は、規則格子でなく、回転した（ずらした）配置が使われます。2x は斜めに 2 点です。4x は回転した格子（RGSS）で、水平や垂直の縁で異なる段階を作れます。8x はさらに多様な位置を取ります。

<strong>規則格子</strong>（<strong>縦横にそろう</strong>）だと水平・垂直に近い縁でサンプルの高さが同じになり、段階が減ります。回転・ずらした配置にするとどの傾きの縁でも多くの段階が得られます。

## DX11 での設定

```cpp
DXGI_SAMPLE_DESC sample_desc = {4, 0};

D3D11_TEXTURE2D_DESC color_desc = {};
color_desc.Width = width;
color_desc.Height = height;
color_desc.MipLevels = 1;
color_desc.ArraySize = 1;
color_desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
color_desc.SampleDesc = sample_desc;
color_desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&color_desc, nullptr, msaa_color.GetAddressOf());

context->ResolveSubresource(resolved.Get(), 0, msaa_color.Get(), 0, DXGI_FORMAT_R16G16B16A16_FLOAT);
```

設定の要点です。`SampleDesc = {4, 0}` で 4x MSAA になり、カラーも深度も同じサンプル数です。`ResolveSubresource` は、ハードウェアがサンプルを平均して 1 サンプルの画像にします。HDR では、リゾルブが単純平均なので、明るい点が混ざってトーンマップ後の見た目が悪化することがあります（次の節）。

### HDR でのリゾルブの注意

<strong>HDR（値が 1 を超える）</strong>を<strong>そのまま平均</strong>すると<strong>明るい点が支配的になり、トーンマップ後に縁がジャギーのまま見えます</strong>。対策：

HDR（値が 1 を超える）をそのまま平均すると、明るい点が支配的になり、トーンマップ後に縁がジャギーのまま見えます。対策は 2 つです。サンプルごとにトーンマップ（またはその近似）してから平均して戻す方法。コンピュート シェーダーのカスタム リゾルブで、サンプルを読み、輝度で重み付けして平均する方法です（ファイアフライ対策と同様です）。

## 弱点

| 弱点 | 理由 | 対処 |
| --- | --- | --- |
| シェーダー内のエイリアシングに効かない | シェーダーは 1 画素 1 回 | TAA・スペキュラ AA |
| アルファ テストの縁に効かない | テクスチャのアルファ判定は、画素単位 | <strong>A2C（アルファ トゥ カバレッジ）</strong> |
| ディファードで重い | G バッファがサンプル数 倍 | フォワード系・MSAA を諦める |
| メモリと帯域が サンプル数 倍 | 深度・カラーのサンプルが増える | サンプル数を下げる・圧縮に頼る |
| ポストプロセスと相性が悪い | リゾルブ前のサンプルは、画面全体の加工に使いにくい | リゾルブしてから加工 |

### アルファ トゥ カバレッジ（A2C）

<strong>葉・フェンスのアルファ テスト</strong>の縁は、<strong>MSAA で滑らかになりません</strong>。A2C を有効にすると、ピクセル シェーダーが出力したアルファを、カバレッジ マスクに変換し、サンプルごとに覆う・覆わないを決めます。

```cpp
D3D11_BLEND_DESC blend = {};
blend.AlphaToCoverageEnable = TRUE;
```

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| <strong>フォワード ＋ MSAA（VR・モバイル）</strong> | <strong>タイルベース GPU は、MSAA がほぼ無料（タイル内で解決）</strong> |
| MSAA ＋ TAA | 縁は MSAA、残りは TAA で（重くなる） |
| A2C で葉・フェンス | アルファ テストの縁も滑らかに |
| HDR はトーンマップ後の見た目でリゾルブ | 明るい点でジャギーが復活しないよう |
| スペキュラ AA を併用 | シェーダー内のちらつきは、別に対策（法線の分散を粗さに足す） |

## よくあるミス

??? failure "MSAA を有効にしたのに、スペキュラのちらつきが消えない"
    <strong>MSAA はジオメトリの縁だけ</strong>。<strong>TAA・スペキュラ AA</strong> を使う。

??? failure "HDR でリゾルブして、明るい縁がジャギーに見える"
    <strong>トーンマップしてからリゾルブ</strong>、または<strong>重み付きリゾルブ</strong>。

??? failure "ディファードで MSAA を有効にして、極端に重くなる"
    <strong>G バッファが全サンプル分</strong>。<strong>フォワード系にするか、TAA に切り替える</strong>。

??? failure "葉のアルファ テストの縁が、ジャギーのまま"
    <strong>A2C（`AlphaToCoverageEnable`）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] MSAA ＝ <strong>1 画素に複数サンプル</strong>。<strong>縁だけサンプルごとに判定</strong>。<strong>シェーダーは 1 回</strong>
    - [x] <strong>ジオメトリの縁に効く</strong>が、<strong>シェーダー内には効かない</strong>
    - [x] <strong>リゾルブ（平均）</strong>で<strong>滑らかな縁</strong>。<strong>HDR ではリゾルブの順序に注意</strong>
    - [x] <strong>メモリ・帯域が サンプル数 倍</strong>。<strong>ディファードとは相性が悪い</strong>
    - [x] <strong>A2C</strong> で<strong>アルファ テストの縁</strong>も

## 参考

- Akeley, "RealityEngine Graphics"（SIGGRAPH 1993）
- Microsoft, "Multisampling Anti-Aliasing"（Microsoft Learn）
- Pettineo, "A Quick Overview of MSAA"（The Danger Zone）

## 関連ページ

- [Anti-Aliasing](index.md)
- [FXAA](fxaa.md)
- [TAA](taa.md)
- [Comparison and Choosing](comparison.md)
- [ラスタライズ](../../../3d/render-flow/rasterize.md)
