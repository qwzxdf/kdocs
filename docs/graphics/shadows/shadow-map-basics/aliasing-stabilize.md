---
title: Aliasing and Stabilization
tags:
  - 描画
---

# Aliasing and Stabilization

**シャドウ マップの絵は、画面より低い解像度**であることが多く、**影の縁がギザギザ（エイリアシング）**になります。**エイリアシングには 2 種類**あり、**解像度不足（遠近）**と**テクセルの揺れ（カメラや光が動くと、縁が這う）**です。**後者は、光の行列をテクセルの単位に揃える「スナップ」**で**防げます**。このページでは、**2 種類の整理・テクセルのスナップ**を説明します。

!!! tip "ポイント"
    - **エイリアシング ＝ 画面の 1 画素が、マップの複数テクセルにまたがる / 逆**。
    - **遠近エイリアシング**：**近くで足りない**。**[カスケード](../cascaded.md)**で解決。
    - **揺れ**：**カメラが動くたびに、マップの格子と画面の対応が変わる**。**スナップ**で固定。
    - **スナップ ＝ 光の位置をテクセルの大きさの倍数に丸める**。

## 問題の整理
| 問題 | 症状 | 原因 | 対策 |
| --- | --- | --- | --- |
| **シャドウ アクネ** | 面に縞・斑点 | 深度の離散化で**自分自身を遮蔽物と誤判定** | [バイアス](../bias/index.md) |
| **ピーター パンニング** | 影が物体から**浮く** | バイアスが大きすぎる | バイアスの調整・法線オフセット |
| **エイリアシング** | 影の縁が**ギザギザ** | シャドウ マップの解像度が足りない | [カスケード](../cascaded.md)・高解像度・フィルタ |
| **縁がハード** | 影の縁がくっきりしすぎ | 点での比較（0/1）だけ | [PCF](../pcf.md)・[PCSS](../pcss.md) |
| **範囲外** | 画面の端で影が途切れる | シャドウ マップの範囲不足 | 範囲の設計・カスケード |
| **透明部分** | 葉・フェンスの影が板状 | 深度だけを描いている | [特殊なケース](../special-cases/index.md) |

<!-- fig:perspective-aliasing:begin -->

<svg class="fig illust motion" data-fig="perspective-aliasing" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-perspective-aliasing" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">透視エイリアシング: 近くでは、シャドウ マップの 1 マスが、画面で大きく見える</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。カメラから床を見て、シャドウ マップの 1 マス(床の上で一定の幅)が、画面の何画素ぶんになるか</text>
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
<text x="30" y="336" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② その 1 マスが、画面でどれだけの画素になるか</text>
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

## エイリアシングの 2 種類
シャドウ マップは、**解像度が有限**なので**縁がギザギザ**になります。その原因は 2 つに分けられます。

エイリアシングの原因は、2 種類に分けられます。<strong>投影エイリアシング</strong>は、光の向きと面の向きが近い（斜め）と、1 テクセルが面の上で細長く伸びることで起きます。スロープ バイアスや、面の向きに応じた処理で対処します。<strong>遠近エイリアシング</strong>は、カメラの近くでは画面上の 1 ピクセルがシャドウ マップの 1 テクセルより小さく（粗く見え）、遠くでは逆に過剰になることで起きます。距離ごとに分割するカスケードや、射影の工夫（LiSPSM・TSM など）で対処します。

**カメラの近くで細かい影が必要**なのに**マップは全体を均等に**覆っているので、**近くが粗く**、**遠くが無駄**になります。**距離に応じて、解像度を配分**する方式（**カスケード**）が、これを解決します。

## 安定させる：テクセルのスナップ
カメラや光が動くと**シャドウ マップの範囲**が動き、**影の縁がちらつきます**（テクセルの境界がずれるため）。**範囲の位置をテクセル単位に揃える**と、ちらつきが止まります（[カスケード](../cascaded.md)）。

## よくあるミス

??? failure "カメラを動かすと、影の縁が泳ぐ（ちらつく）"
    **光の行列を、テクセル単位にスナップ**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **エイリアシングは、解像度不足と揺れの 2 種類**
    - [x] **テクセルのスナップで、揺れを防ぐ**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [PCF](../pcf.md)
