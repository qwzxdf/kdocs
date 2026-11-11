---
title: Aliasing and Stabilization
tags:
  - 描画
---

# Aliasing and Stabilization

シャドウ マップを使うと影の縁がギザギザになります。それだけでなくカメラを動かすと影の縁がちらちらと這うように動くことがあります。前者は解像度の問題で後者はシャドウ マップの格子が、世界に対して動くことが原因です。

<strong>エイリアシングには 2 種類あり解像度不足（遠近と射影）とテクセルの揺れ（カメラや光が動くと縁が這う）です</strong>。後者はシャドウ マップの範囲を固定の大きさにして、テクセルの整数倍の位置にそろえる「スナップ」で防げます。このページでは問題の整理、2 種類のエイリアシング、スイミングの原因、バウンディング スフィアとスナップ（実測つき）、光が動くとき縁のフィルタ、深度の精度を説明します。

!!! tip "ポイント"
    - エイリアシングは画面の 1 画素がマップの複数テクセルにまたがる（解像度不足）か、逆に過剰な場合です。
    - 遠近エイリアシング（近くで足りない）は、[Cascaded Shadow Maps (CSM)](../cascaded.md) で解決します。
    - 揺れはカメラが動くたびにマップの格子と世界の対応がずれて起きます。スナップで固定します。
    - 視錐台にぴったり合う箱は、カメラの回転で大きさが変わります。実測で約 2 倍変わりました。球にすれば一定です。
    - スナップは半径を固定したうえで、箱の位置をテクセルの整数倍に丸めます。

!!! info "このページを読む前に"
    - [Shadow Map Basics](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## 問題の整理 {#problems}

シャドウ マップの問題は見た目で分けると、次の 6 つです。

- シャドウ アクネは面に縞や斑点が出ます。深度の離散化で自分自身を遮蔽物と誤判定するのが原因です（[Shadow Bias](../bias/index.md)）。
- ピーター パンニングは影が物体から浮きます。バイアスが大きすぎるのが原因です。
- エイリアシングは影の縁がギザギザになります。解像度が足りないのが原因です（[Cascaded Shadow Maps (CSM)](../cascaded.md)、高解像度、フィルタ）。
- 縁がハードなのは点での比較（0 か 1）だけだからです（[PCF](../pcf.md)、[PCSS](../pcss.md)）。
- 範囲外では画面の端で影が途切れます。範囲の設計やカスケードで対処します。
- 透明部分では葉やフェンスの影が板状になります。深度だけを描いているからです（[Special Cases](../special-cases/index.md)）。

<!-- fig:perspective-aliasing:begin -->

<svg class="fig illust motion" data-fig="perspective-aliasing" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-perspective-aliasing" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">透視エイリアシング: 近くでは、シャドウ マップの 1 マスが画面で大きく見える</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。カメラから床を見て、シャドウ マップの 1 マス(床の上で一定の幅)が画面の何画素ぶんになるか</text>
<rect x="30" y="96" width="900" height="230" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 断面(床にシャドウ マップの 1 マスが一定の幅で並ぶ)</text>
<line x1="70.0" y1="280.0" x2="920.0" y2="280.0" stroke="#475569" stroke-width="3"/>
<circle cx="70.0" cy="200.0" r="8" fill="#1f2937"/>
<text x="80.0" y="192.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ(高さ 2 m)</text>
<line x1="70.0" y1="280.0" x2="70.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="72.12" y1="280.0" x2="72.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="74.25" y1="280.0" x2="74.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="76.38" y1="280.0" x2="76.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="78.5" y1="280.0" x2="78.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="80.62" y1="280.0" x2="80.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="82.75" y1="280.0" x2="82.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="84.88" y1="280.0" x2="84.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="87.0" y1="280.0" x2="87.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="89.12" y1="280.0" x2="89.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="91.25" y1="280.0" x2="91.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="93.38" y1="280.0" x2="93.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="95.5" y1="280.0" x2="95.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="97.62" y1="280.0" x2="97.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="99.75" y1="280.0" x2="99.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="101.88" y1="280.0" x2="101.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="104.0" y1="280.0" x2="104.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="106.12" y1="280.0" x2="106.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="108.25" y1="280.0" x2="108.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="110.38" y1="280.0" x2="110.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="112.5" y1="280.0" x2="112.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="114.62" y1="280.0" x2="114.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="116.75" y1="280.0" x2="116.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="118.88" y1="280.0" x2="118.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="121.0" y1="280.0" x2="121.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="123.12" y1="280.0" x2="123.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="125.25" y1="280.0" x2="125.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="127.38" y1="280.0" x2="127.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="129.5" y1="280.0" x2="129.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="131.62" y1="280.0" x2="131.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="133.75" y1="280.0" x2="133.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="135.88" y1="280.0" x2="135.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="138.0" y1="280.0" x2="138.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="140.12" y1="280.0" x2="140.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="142.25" y1="280.0" x2="142.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="144.38" y1="280.0" x2="144.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="146.5" y1="280.0" x2="146.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="148.62" y1="280.0" x2="148.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="150.75" y1="280.0" x2="150.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="152.88" y1="280.0" x2="152.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="155.0" y1="280.0" x2="155.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="157.12" y1="280.0" x2="157.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="159.25" y1="280.0" x2="159.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="161.38" y1="280.0" x2="161.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="163.5" y1="280.0" x2="163.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="165.62" y1="280.0" x2="165.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="167.75" y1="280.0" x2="167.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="169.88" y1="280.0" x2="169.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="172.0" y1="280.0" x2="172.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="174.12" y1="280.0" x2="174.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="176.25" y1="280.0" x2="176.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="178.38" y1="280.0" x2="178.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="180.5" y1="280.0" x2="180.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="182.62" y1="280.0" x2="182.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="184.75" y1="280.0" x2="184.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="186.88" y1="280.0" x2="186.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="189.0" y1="280.0" x2="189.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="191.12" y1="280.0" x2="191.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="193.25" y1="280.0" x2="193.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="195.38" y1="280.0" x2="195.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="197.5" y1="280.0" x2="197.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="199.62" y1="280.0" x2="199.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="201.75" y1="280.0" x2="201.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="203.88" y1="280.0" x2="203.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="206.0" y1="280.0" x2="206.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="208.12" y1="280.0" x2="208.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="210.25" y1="280.0" x2="210.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="212.38" y1="280.0" x2="212.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="214.5" y1="280.0" x2="214.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="216.62" y1="280.0" x2="216.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="218.75" y1="280.0" x2="218.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="220.88" y1="280.0" x2="220.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="223.0" y1="280.0" x2="223.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="225.12" y1="280.0" x2="225.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="227.25" y1="280.0" x2="227.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="229.38" y1="280.0" x2="229.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="231.5" y1="280.0" x2="231.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="233.62" y1="280.0" x2="233.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="235.75" y1="280.0" x2="235.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="237.88" y1="280.0" x2="237.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="240.0" y1="280.0" x2="240.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="242.12" y1="280.0" x2="242.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="244.25" y1="280.0" x2="244.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="246.38" y1="280.0" x2="246.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="248.5" y1="280.0" x2="248.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="250.62" y1="280.0" x2="250.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="252.75" y1="280.0" x2="252.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="254.88" y1="280.0" x2="254.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="257.0" y1="280.0" x2="257.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="259.12" y1="280.0" x2="259.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="261.25" y1="280.0" x2="261.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="263.38" y1="280.0" x2="263.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="265.5" y1="280.0" x2="265.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="267.62" y1="280.0" x2="267.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="269.75" y1="280.0" x2="269.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="271.88" y1="280.0" x2="271.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="274.0" y1="280.0" x2="274.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="276.12" y1="280.0" x2="276.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="278.25" y1="280.0" x2="278.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="280.38" y1="280.0" x2="280.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="282.5" y1="280.0" x2="282.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="284.62" y1="280.0" x2="284.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="286.75" y1="280.0" x2="286.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="288.88" y1="280.0" x2="288.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="291.0" y1="280.0" x2="291.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="293.12" y1="280.0" x2="293.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="295.25" y1="280.0" x2="295.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="297.38" y1="280.0" x2="297.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="299.5" y1="280.0" x2="299.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="301.62" y1="280.0" x2="301.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="303.75" y1="280.0" x2="303.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="305.88" y1="280.0" x2="305.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="308.0" y1="280.0" x2="308.0" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="310.12" y1="280.0" x2="310.12" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="312.25" y1="280.0" x2="312.25" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="314.38" y1="280.0" x2="314.38" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="316.5" y1="280.0" x2="316.5" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="318.62" y1="280.0" x2="318.62" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="320.75" y1="280.0" x2="320.75" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="322.88" y1="280.0" x2="322.88" y2="288.0" stroke="#e5aa28" stroke-width="1.5"/>
<text x="40" y="120" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">オレンジの短い線 = 影のマスの境目(0.25 m ごと)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2265;0.2267;1.0000" values="0;0;1;1;0;0"/><line x1="70.0" y1="200.0" x2="95.5" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<line x1="70.0" y1="200.0" x2="97.62" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<rect x="95.5" y="275.0" width="3" height="10" fill="#e5484d"/>
<text x="95.5" y="314.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">距離 3 m</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2265;0.2267;0.3865;0.3867;1.0000" values="0;0;1;1;0;0"/><line x1="70.0" y1="200.0" x2="121.0" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<line x1="70.0" y1="200.0" x2="123.12" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<rect x="121.0" y="275.0" width="3" height="10" fill="#e5484d"/>
<text x="121.0" y="314.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">距離 6 m</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3865;0.3867;0.5465;0.5467;1.0000" values="0;0;1;1;0;0"/><line x1="70.0" y1="200.0" x2="172.0" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<line x1="70.0" y1="200.0" x2="174.12" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<rect x="172.0" y="275.0" width="3" height="10" fill="#e5484d"/>
<text x="172.0" y="314.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">距離 12 m</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/><line x1="70.0" y1="200.0" x2="274.0" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<line x1="70.0" y1="200.0" x2="276.12" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<rect x="274.0" y="275.0" width="3" height="10" fill="#e5484d"/>
<text x="274.0" y="314.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">距離 24 m</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><line x1="70.0" y1="200.0" x2="478.0" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<line x1="70.0" y1="200.0" x2="480.12" y2="280.0" stroke="#e5484d" stroke-width="2"/>
<rect x="478.0" y="275.0" width="3" height="10" fill="#e5484d"/>
<text x="478.0" y="314.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">距離 48 m</text>
</g>
<rect x="30" y="346" width="900" height="100" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="336" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② その 1 マスが画面でどれだけの画素になるか</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><rect x="50" y="382" width="150.0" height="26" fill="#e5484d" opacity="0.85"/>
<text x="50" y="376" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">距離 3 m</text>
<text x="54" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">30.8 画素 / マス</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2265;0.2267;1.0000" values="0;0;1;1"/><rect x="225" y="382" width="48.0" height="26" fill="#e5484d" opacity="0.85"/>
<text x="225" y="376" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">距離 6 m</text>
<text x="229" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">8.0 画素 / マス</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3865;0.3867;1.0000" values="0;0;1;1"/><rect x="400" y="382" width="12.24" height="26" fill="#2ea043" opacity="0.85"/>
<text x="400" y="376" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">距離 12 m</text>
<text x="404" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">2.0 画素 / マス</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;1.0000" values="0;0;1;1"/><rect x="575" y="382" width="3.09" height="26" fill="#2ea043" opacity="0.85"/>
<text x="575" y="376" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">距離 24 m</text>
<text x="579" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">0.5 画素 / マス</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><rect x="750" y="382" width="2" height="26" fill="#2ea043" opacity="0.85"/>
<text x="750" y="376" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">距離 48 m</text>
<text x="754" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">0.1 画素 / マス</text>
</g>
<text x="40" y="478" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">1 マスの画素数(×10):</text>
<text x="220" y="482" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0754;0.0756;1.0000" values="1;1;0;0"/></text>
<text x="220" y="482" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">308<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0754;0.0756;0.2354;0.2356;1.0000" values="0;0;1;1;0;0"/></text>
<text x="220" y="482" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">80<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2354;0.2356;0.3954;0.3956;1.0000" values="0;0;1;1;0;0"/></text>
<text x="220" y="482" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3954;0.3956;0.5554;0.5556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="220" y="482" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5554;0.5556;0.7154;0.7156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="220" y="482" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7154;0.7156;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000" values="0;0;1;1"/><rect x="480" y="460" width="450" height="60" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="496" y="484" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">近く(3 m)は 30.8 画素 / マス → ギザギザが目立つ</text>
<text x="496" y="507" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">遠く(48 m)は 0.13 画素 / マス → ほぼ見えない</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">シャドウ マップのマスは、光の側から見て、均等に並ぶ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラから見ると、近いほど 1 マスが大きく見える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8665;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">だから、カスケードで、近くほど細かい影の表を使う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:perspective-aliasing:end -->

## エイリアシングの 2 つの種類 {#two}

シャドウ マップは解像度が有限なので、縁がギザギザになります。原因は 2 つに分けられます。

透視エイリアシングはシャドウ マップの 1 テクセルが、画面上で大きく拡大されることで起きます。カメラの近くで画素が粗くなって、影の縁が階段状になります。解像度を上げるカスケードを使うフィルタリングする（[PCF](../pcf.md)）ことで軽減します。

射影エイリアシングは光に対して面が斜め（光とほぼ平行）だと 1 テクセルが面の上で細長く引き伸ばされることで起きます。斜面の影が縞模様になります。バイアスで隠すか（[Shadow Bias](../bias/index.md)）、法線オフセットで軽減します。

カメラの近くで細かい影が必要なのに、マップが全体を均等に覆っているので、近くが粗く遠くが無駄になります。距離に応じて解像度を配分する方式（カスケード）が、これを解決します。

## シャドウのちらつき（スイミング） {#swimming}

カメラが動くと影の縁がちらちらと動く（泳ぐ）ことがあります。原因はシャドウ マップの画素の位置が、カメラの動きにつれてフレームごとに世界に対してずれることです。

```text
フレーム N:    シャドウ マップの画素:  | | | | | |     ← 影の縁は、この画素のどれかに落ちる
フレーム N+1:  カメラが少し動くと、画素がずれる: |  |  |  |  ← 縁が別の画素に落ちて、影がぴくぴく動く
```

太陽のシャドウ マップの範囲をカメラの視錐台に合わせて、毎フレーム作り直すと範囲の位置と大きさが連続的に変わって、画素の境界が世界の上で動きます。影がそのたびにわずかにずれて見えます。

## 対策 1: 範囲の大きさを固定する {#sphere}

視錐台にぴったり合う箱はカメラが回転すると、大きさが変わります。視錐台を囲む球（バウンディング スフィア）に合わせて箱を作ると、カメラが回転しても大きさが変わりません。

測りました。FOV 60°、アスペクト 16:9 で近い面 0.5 m、遠い面 60 m の視錐台をカメラを水平に 360° 回しながら、光の空間に変換しました。光の空間の箱（AABB）の横幅は最小 60.9 m から最大 123.1 m まで変わって、約 2.02 倍の差がありました。バウンディング スフィアの半径はどの向きでも 76.67 m で一定でした。

箱の大きさが変わると 1 テクセルのワールドでの大きさが変わるので、影が拡大縮小して見えます。球ならどの向きでも同じ大きさなので、安定します。代償は箱が視錐台より大きくなって、解像度が無駄になることです（Valient、2008）。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="カメラを 360 度回したときの、光空間の箱の幅とバウンディング スフィアの直径。箱は 2 倍変わり、球は一定"><text x="14" y="22" class="fig-title">カメラを回したときの大きさ（実測）</text>
<line x1="60" y1="190" x2="680" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="120" y="140" width="80" height="50" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="230" y="40" width="80" height="150" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="430" y="40" width="80" height="150" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/><rect x="540" y="40" width="80" height="150" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="160" y="134">最小 60.9 m</text><text x="270" y="34">最大 123.1 m</text><text x="470" y="34">153.3 m</text><text x="580" y="34">153.3 m</text>
<text x="215" y="212">光空間の箱の幅（約 2.02 倍変わる）</text><text x="525" y="212">球の直径 2 × 76.67 m（一定）</text></g>
<text x="360" y="234" text-anchor="middle" style="font-size:12px">箱が変わると、1 テクセルの大きさも変わり、影が拡大縮小する。球なら変わらない</text></svg>

## 対策 2: テクセル スナップ {#snap}

箱の位置をシャドウ マップの画素の整数倍にそろえます。カメラが少し動いても箱は画素の整数倍ずつしか動かないので、画素の境界がワールド上で動かず影の縁がちらつきません。

次の関数はバウンディング スフィアとスナップを一体にしたものです。MSVC（`/W4`）でコンパイルして確かめました。

```cpp
#include <DirectXMath.h>
#include <algorithm>
#include <cmath>
#include <vector>

using namespace DirectX;

// 視錐台の 8 頂点（ワールド）から、回転しても大きさが変わらず、動いてもテクセルの境界が動かない
// 正射影行列を作る。light_view はワールド → 光のビュー空間の行列。
XMMATRIX StableLightProjection(const std::vector<XMVECTOR>& corners, FXMMATRIX light_view,
                               int resolution, float near_z, float far_z) {
  // ① バウンディング スフィア: 中心は 8 頂点の平均、半径は中心から最も遠い頂点までの距離
  XMVECTOR center = XMVectorZero();
  for (const XMVECTOR& c : corners) center += c;
  center /= float(corners.size());
  float radius = 0.0f;
  for (const XMVECTOR& c : corners) radius = std::max(radius, XMVectorGetX(XMVector3Length(c - center)));
  // 半径を 1/16 m 単位に切り上げる。わずかな変化で大きさが揺れないようにする
  radius = std::ceil(radius * 16.0f) / 16.0f;

  // ② 1 テクセルが、ワールドで何メートルか（球の直径を解像度で割る）
  const float texel_size = (2.0f * radius) / float(resolution);

  // ③ 球の中心を光のビュー空間へ移して、x, y を 1 テクセルの整数倍に丸める（z は動かしてよい）
  XMFLOAT3 c_ls;
  XMStoreFloat3(&c_ls, XMVector3TransformCoord(center, light_view));
  c_ls.x = std::floor(c_ls.x / texel_size) * texel_size;
  c_ls.y = std::floor(c_ls.y / texel_size) * texel_size;

  // ④ 丸めた中心から、正射影の箱を作る
  return XMMatrixOrthographicOffCenterLH(c_ls.x - radius, c_ls.x + radius,
                                         c_ls.y - radius, c_ls.y + radius, near_z, far_z);
}
```

テクセル スナップは半径を固定（対策 1）したうえで、初めて意味を持ちます。半径が揺れると画素の大きさが変わって、スナップしてもずれるからです。

効果を数字で確かめました。ワールドの固定した 1 点が、シャドウ マップ上でテクセルのどこに落ちるか（テクセル内の位置）をカメラを 1.3 cm ずつ、200 回（合計 2.6 m）前進させながら調べました。半径は 40 m に固定して、解像度 2048 なら 1 テクセルが 3.9 cm です。スナップなしでは固定点のテクセル内の位置が、最大 0.59 テクセル動きました。縁がテクセルの半分以上、這っています。スナップありでは変動は 0.000 でした。

| 手法 | 効果 | 代償 |
| --- | --- | --- |
| バウンディング スフィア | カメラの回転で影が拡大縮小しない | 箱が大きく、解像度がやや無駄になる |
| テクセル スナップ | カメラの移動で影がちらつかない | 箱の位置が画素単位で飛ぶ（影の範囲が少しずつ不連続に動く） |

!!! note "確かめた範囲"
    C++ は MSVC（`/W4`、DirectXMath）でコンパイルして、箱の幅と半径の比較、固定点のテクセル内位置の変動を実行して確かめました。実際のシャドウ マップを GPU で描いたものではありません。

## 光の方向が動くとき {#light}

太陽が動く（時間の経過）と光の向きが変わって、シャドウ マップの座標軸が回転します。ゆっくり動かすなら問題ありませんが、毎フレーム少しずつ動くと影がちらつくことがあります。

- 光の向きの更新を間引きます。数フレームに 1 回だけ更新すると、影が少し段階的に動きます。
- フィルタを強くします。PCF の範囲を広げてちらつきをぼかして隠します。

## 影の縁のフィルタ {#filter}

ちらつきを完全になくすのは難しいので、フィルタで縁をぼかして目立たなくします。

- 2×2（比較サンプラー）はわずかななめらかさで、ちらつきは残ります。
- 3×3〜5×5 の PCF はちらつきがかなり減ります。
- 回転するポアソン円盤はちらつきをノイズに変えて、減らします（[PCF](../pcf.md)）。
- TAA は時間方向に平均して、ちらつきを消します。フレームごとにサンプルをずらします。

## 深度の精度 {#depth}

シャドウ マップの深度の精度も重要です。近い面と遠い面の範囲（ニアとファー）が広いと精度が落ちて、シャドウ アクネが出ます。

- ニアとファーを影を落とす物の範囲にぴったり合わせます（光の視点の奥行き）。
- `D32_FLOAT` を使って 16 ビットを避けます。
- 正射影を使うと深度が線形なので、精度が均一です。

## よくあるミス {#mistakes}

??? failure "カメラを動かすと影の縁が泳ぐ（ちらつく）"
    原因はシャドウ マップの範囲の位置が、テクセルの整数倍になっていないことです。光の空間の中心をテクセルの大きさの整数倍に丸めます。実測で丸めないと 0.59 テクセル動きました。

??? failure "カメラを回すと影が拡大縮小する"
    原因は視錐台にぴったり合う箱を使っていて、回転で大きさが変わることです。バウンディング スフィアを使います。実測で箱の幅が約 2 倍変わりました。

??? failure "スナップしたのに、まだ揺れる"
    原因は半径が揺れていることです。半径が変わるとテクセルの大きさも変わるので、スナップしても境界がずれます。半径は 1/16 m のように切り上げて、固定します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] エイリアシングは、解像度不足と揺れの 2 種類です。
    - [x] 箱はバウンディング スフィアで大きさを固定します。
    - [x] 箱の位置をテクセルの整数倍に丸める（スナップ）と縁が這いません。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は自分で書いた C++ の実測です。

- Valient, "Stable Rendering of Cascaded Shadow Maps", ShaderX6, 2008（テクセル スナップによる安定化）
- Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007
- Brabec, Annen, Seidel, "Practical Shadow Mapping", Journal of Graphics Tools, Vol. 7, No. 4, 2002
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [PCF](../pcf.md)
