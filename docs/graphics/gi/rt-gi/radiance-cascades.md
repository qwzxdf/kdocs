---
title: Radiance Cascades
tags:
  - 描画
---

# Radiance Cascades

**Radiance Cascades は、「近くの光は高解像度で、遠くの光は低解像度で」持つ、階層的な方式**です。**2D の GI で特に成功しており、3D にも展開されつつあります**。このページでは、**Radiance Cascades の発想と、利点**を説明します。

!!! tip "ポイント"
    - **近くの光は、細かい空間解像度・粗い方向解像度**。
    - **遠くの光は、粗い空間解像度・細かい方向解像度**。
    - **階層ごとに結果をマージ**して、全体の光を求める。
    - **ノイズが少なく、安定している**。

## Radiance Cascades
**Radiance Cascades**（Alexander Sannikov、2023〜）は、**ノイズのない、全画素の放射照度**を**階層的な構造**で**効率よく計算する**方式です。

<!-- fig:radiance-cascades:begin -->

<svg class="fig illust motion" data-fig="radiance-cascades" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-radiance-cascades" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ラディアンス カスケード: 近くは点を細かく、遠くは方向を細かく</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">16×16 の画面を、4 段のカスケードで調べる。各段の光線の総数は同じで、届く距離が 4 倍ずつ伸びる</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/><rect x="40" y="110" width="170.0" height="170.0" fill="#ffffff" stroke="#60a5fa" stroke-width="2.5" rx="6"/>
<circle cx="45.31" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="45.31" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="55.94" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="66.56" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="77.19" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="87.81" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="98.44" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="109.06" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="119.69" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="130.31" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="140.94" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="151.56" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="162.19" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="172.81" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="183.44" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="194.06" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="115.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="125.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="136.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="147.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="157.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="168.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="179.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="189.69" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="200.31" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="210.94" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="221.56" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="232.19" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="242.81" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="253.44" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="264.06" r="1.9124999999999999" fill="#60a5fa"/>
<circle cx="204.69" cy="274.69" r="1.9124999999999999" fill="#60a5fa"/>
<line x1="125.0" y1="195.0" x2="129.14" y2="199.14" stroke="#60a5fa" stroke-width="1.3" opacity="0.8"/>
<line x1="125.0" y1="195.0" x2="120.86" y2="199.14" stroke="#60a5fa" stroke-width="1.3" opacity="0.8"/>
<line x1="125.0" y1="195.0" x2="120.86" y2="190.86" stroke="#60a5fa" stroke-width="1.3" opacity="0.8"/>
<line x1="125.0" y1="195.0" x2="129.14" y2="190.86" stroke="#60a5fa" stroke-width="1.3" opacity="0.8"/>
<text x="40" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#60a5fa">カスケード 0</text>
<text x="40" y="302.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">点 256 × 方向 4 = 1,024 本</text>
<text x="40" y="322.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">届く距離 0 〜 1</text>
<text x="40" y="340.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">点の間隔 1、方向 4 分割</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1956;0.1957;1.0000" values="0;0;1;1"/><rect x="265" y="110" width="170.0" height="170.0" fill="#ffffff" stroke="#34d399" stroke-width="2.5" rx="6"/>
<circle cx="275.62" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="275.62" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="296.88" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="318.12" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="339.38" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="360.62" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="381.88" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="403.12" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="120.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="141.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="163.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="184.38" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="205.62" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="226.88" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="248.12" r="3.8249999999999997" fill="#34d399"/>
<circle cx="424.38" cy="269.38" r="3.8249999999999997" fill="#34d399"/>
<line x1="355.74" y1="196.14" x2="372.95" y2="199.57" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="354.86" y1="198.25" x2="369.46" y2="208.0" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="353.25" y1="199.86" x2="363.0" y2="214.46" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="351.14" y1="200.74" x2="354.57" y2="217.95" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="348.86" y1="200.74" x2="345.43" y2="217.95" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="346.75" y1="199.86" x2="337.0" y2="214.46" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="345.14" y1="198.25" x2="330.54" y2="208.0" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="344.26" y1="196.14" x2="327.05" y2="199.57" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="344.26" y1="193.86" x2="327.05" y2="190.43" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="345.14" y1="191.75" x2="330.54" y2="182.0" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="346.75" y1="190.14" x2="337.0" y2="175.54" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="348.86" y1="189.26" x2="345.43" y2="172.05" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="351.14" y1="189.26" x2="354.57" y2="172.05" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="353.25" y1="190.14" x2="363.0" y2="175.54" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="354.86" y1="191.75" x2="369.46" y2="182.0" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<line x1="355.74" y1="193.86" x2="372.95" y2="190.43" stroke="#34d399" stroke-width="1.3" opacity="0.8"/>
<text x="265" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#34d399">カスケード 1</text>
<text x="265" y="302.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">点 64 × 方向 16 = 1,024 本</text>
<text x="265" y="322.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">届く距離 1 〜 4</text>
<text x="265" y="340.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">点の間隔 2、方向 16 分割</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3488;0.3489;1.0000" values="0;0;1;1"/><rect x="490" y="110" width="170.0" height="170.0" fill="#ffffff" stroke="#fbbf24" stroke-width="2.5" rx="6"/>
<circle cx="511.25" cy="131.25" r="4.5" fill="#fbbf24"/>
<circle cx="511.25" cy="173.75" r="4.5" fill="#fbbf24"/>
<circle cx="511.25" cy="216.25" r="4.5" fill="#fbbf24"/>
<circle cx="511.25" cy="258.75" r="4.5" fill="#fbbf24"/>
<circle cx="553.75" cy="131.25" r="4.5" fill="#fbbf24"/>
<circle cx="553.75" cy="173.75" r="4.5" fill="#fbbf24"/>
<circle cx="553.75" cy="216.25" r="4.5" fill="#fbbf24"/>
<circle cx="553.75" cy="258.75" r="4.5" fill="#fbbf24"/>
<circle cx="596.25" cy="131.25" r="4.5" fill="#fbbf24"/>
<circle cx="596.25" cy="173.75" r="4.5" fill="#fbbf24"/>
<circle cx="596.25" cy="216.25" r="4.5" fill="#fbbf24"/>
<circle cx="596.25" cy="258.75" r="4.5" fill="#fbbf24"/>
<circle cx="638.75" cy="131.25" r="4.5" fill="#fbbf24"/>
<circle cx="638.75" cy="173.75" r="4.5" fill="#fbbf24"/>
<circle cx="638.75" cy="216.25" r="4.5" fill="#fbbf24"/>
<circle cx="638.75" cy="258.75" r="4.5" fill="#fbbf24"/>
<line x1="598.37" y1="196.15" x2="657.9" y2="199.07" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="598.15" y1="198.43" x2="657.1" y2="207.18" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="597.7" y1="200.69" x2="655.51" y2="215.17" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="597.03" y1="202.88" x2="653.15" y2="222.96" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="596.15" y1="205.0" x2="650.03" y2="230.49" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="595.07" y1="207.03" x2="646.19" y2="237.67" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="593.8" y1="208.94" x2="641.67" y2="244.44" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="592.34" y1="210.71" x2="636.5" y2="250.74" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="590.71" y1="212.34" x2="630.74" y2="256.5" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="588.94" y1="213.8" x2="624.44" y2="261.67" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="587.03" y1="215.07" x2="617.67" y2="266.19" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="585.0" y1="216.15" x2="610.49" y2="270.03" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="582.88" y1="217.03" x2="602.96" y2="273.15" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="580.69" y1="217.7" x2="595.17" y2="275.51" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="578.43" y1="218.15" x2="587.18" y2="277.1" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="576.15" y1="218.37" x2="579.07" y2="277.9" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="573.85" y1="218.37" x2="570.93" y2="277.9" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="571.57" y1="218.15" x2="562.82" y2="277.1" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="569.31" y1="217.7" x2="554.83" y2="275.51" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="567.12" y1="217.03" x2="547.04" y2="273.15" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="565.0" y1="216.15" x2="539.51" y2="270.03" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="562.97" y1="215.07" x2="532.33" y2="266.19" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="561.06" y1="213.8" x2="525.56" y2="261.67" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="559.29" y1="212.34" x2="519.26" y2="256.5" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="557.66" y1="210.71" x2="513.5" y2="250.74" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="556.2" y1="208.94" x2="508.33" y2="244.44" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="554.93" y1="207.03" x2="503.81" y2="237.67" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="553.85" y1="205.0" x2="499.97" y2="230.49" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="552.97" y1="202.88" x2="496.85" y2="222.96" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="552.3" y1="200.69" x2="494.49" y2="215.17" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="551.85" y1="198.43" x2="492.9" y2="207.18" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="551.63" y1="196.15" x2="492.1" y2="199.07" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="551.63" y1="193.85" x2="492.1" y2="190.93" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="551.85" y1="191.57" x2="492.9" y2="182.82" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="552.3" y1="189.31" x2="494.49" y2="174.83" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="552.97" y1="187.12" x2="496.85" y2="167.04" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="553.85" y1="185.0" x2="499.97" y2="159.51" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="554.93" y1="182.97" x2="503.81" y2="152.33" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="556.2" y1="181.06" x2="508.33" y2="145.56" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="557.66" y1="179.29" x2="513.5" y2="139.26" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="559.29" y1="177.66" x2="519.26" y2="133.5" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="561.06" y1="176.2" x2="525.56" y2="128.33" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="562.97" y1="174.93" x2="532.33" y2="123.81" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="565.0" y1="173.85" x2="539.51" y2="119.97" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="567.12" y1="172.97" x2="547.04" y2="116.85" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="569.31" y1="172.3" x2="554.83" y2="114.49" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="571.57" y1="171.85" x2="562.82" y2="112.9" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="573.85" y1="171.63" x2="570.93" y2="112.1" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="576.15" y1="171.63" x2="579.07" y2="112.1" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="578.43" y1="171.85" x2="587.18" y2="112.9" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="580.69" y1="172.3" x2="595.17" y2="114.49" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="582.88" y1="172.97" x2="602.96" y2="116.85" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="585.0" y1="173.85" x2="610.49" y2="119.97" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="587.03" y1="174.93" x2="617.67" y2="123.81" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="588.94" y1="176.2" x2="624.44" y2="128.33" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="590.71" y1="177.66" x2="630.74" y2="133.5" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="592.34" y1="179.29" x2="636.5" y2="139.26" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="593.8" y1="181.06" x2="641.67" y2="145.56" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="595.07" y1="182.97" x2="646.19" y2="152.33" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="596.15" y1="185.0" x2="650.03" y2="159.51" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="597.03" y1="187.12" x2="653.15" y2="167.04" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="597.7" y1="189.31" x2="655.51" y2="174.83" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="598.15" y1="191.57" x2="657.1" y2="182.82" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<line x1="598.37" y1="193.85" x2="657.9" y2="190.93" stroke="#fbbf24" stroke-width="1.3" opacity="0.8"/>
<text x="490" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#fbbf24">カスケード 2</text>
<text x="490" y="302.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">点 16 × 方向 64 = 1,024 本</text>
<text x="490" y="322.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">届く距離 4 〜 16</text>
<text x="490" y="340.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">点の間隔 4、方向 64 分割</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5021;1.0000" values="0;0;1;1"/><rect x="715" y="110" width="170.0" height="170.0" fill="#ffffff" stroke="#f87171" stroke-width="2.5" rx="6"/>
<circle cx="757.5" cy="152.5" r="4.5" fill="#f87171"/>
<circle cx="757.5" cy="237.5" r="4.5" fill="#f87171"/>
<circle cx="842.5" cy="152.5" r="4.5" fill="#f87171"/>
<circle cx="842.5" cy="237.5" r="4.5" fill="#f87171"/>
<line x1="893.59" y1="196.15" x2="882.99" y2="196.02" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="893.54" y1="198.45" x2="882.94" y2="198.05" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="893.42" y1="200.74" x2="882.84" y2="200.09" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="893.25" y1="203.03" x2="882.69" y2="202.12" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="893.03" y1="205.32" x2="882.49" y2="204.15" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="892.75" y1="207.6" x2="882.24" y2="206.17" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="892.41" y1="209.87" x2="881.95" y2="208.19" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="892.02" y1="212.13" x2="881.6" y2="210.19" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="891.57" y1="214.39" x2="881.2" y2="212.19" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="891.07" y1="216.63" x2="880.75" y2="214.18" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="890.51" y1="218.86" x2="880.26" y2="216.15" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="889.9" y1="221.07" x2="879.72" y2="218.12" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="889.23" y1="223.27" x2="879.12" y2="220.07" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="888.51" y1="225.45" x2="878.49" y2="222.0" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="887.73" y1="227.61" x2="877.8" y2="223.92" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="886.91" y1="229.76" x2="877.07" y2="225.82" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="886.03" y1="231.88" x2="876.29" y2="227.7" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="885.1" y1="233.98" x2="875.46" y2="229.56" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="884.12" y1="236.05" x2="874.59" y2="231.41" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="883.08" y1="238.11" x2="873.67" y2="233.22" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="882.0" y1="240.13" x2="872.71" y2="235.02" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="880.87" y1="242.13" x2="871.71" y2="236.79" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="879.69" y1="244.1" x2="870.66" y2="238.54" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="878.46" y1="246.04" x2="869.57" y2="240.26" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="877.18" y1="247.95" x2="868.44" y2="241.96" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="875.86" y1="249.83" x2="867.27" y2="243.62" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="874.49" y1="251.68" x2="866.05" y2="245.26" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="873.08" y1="253.49" x2="864.8" y2="246.86" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="871.62" y1="255.26" x2="863.51" y2="248.44" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="870.12" y1="257.0" x2="862.18" y2="249.98" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="868.58" y1="258.7" x2="860.81" y2="251.49" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="866.99" y1="260.37" x2="859.41" y2="252.97" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="865.37" y1="261.99" x2="857.97" y2="254.41" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="863.7" y1="263.58" x2="856.49" y2="255.81" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="862.0" y1="265.12" x2="854.98" y2="257.18" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="860.26" y1="266.62" x2="853.44" y2="258.51" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="858.49" y1="268.08" x2="851.86" y2="259.8" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="856.68" y1="269.49" x2="850.26" y2="261.05" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="854.83" y1="270.86" x2="848.62" y2="262.27" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="852.95" y1="272.18" x2="846.96" y2="263.44" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="851.04" y1="273.46" x2="845.26" y2="264.57" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="849.1" y1="274.69" x2="843.54" y2="265.66" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="847.13" y1="275.87" x2="841.79" y2="266.71" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="845.13" y1="277.0" x2="840.02" y2="267.71" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="843.11" y1="278.08" x2="838.22" y2="268.67" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="841.05" y1="279.12" x2="836.41" y2="269.59" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="838.98" y1="280.1" x2="834.56" y2="270.46" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="836.88" y1="281.03" x2="832.7" y2="271.29" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="834.76" y1="281.91" x2="830.82" y2="272.07" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="832.61" y1="282.73" x2="828.92" y2="272.8" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="830.45" y1="283.51" x2="827.0" y2="273.49" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="828.27" y1="284.23" x2="825.07" y2="274.12" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="826.07" y1="284.9" x2="823.12" y2="274.72" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="823.86" y1="285.51" x2="821.15" y2="275.26" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="821.63" y1="286.07" x2="819.18" y2="275.75" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="819.39" y1="286.57" x2="817.19" y2="276.2" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="817.13" y1="287.02" x2="815.19" y2="276.6" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="814.87" y1="287.41" x2="813.19" y2="276.95" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="812.6" y1="287.75" x2="811.17" y2="277.24" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="810.32" y1="288.03" x2="809.15" y2="277.49" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="808.03" y1="288.25" x2="807.12" y2="277.69" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="805.74" y1="288.42" x2="805.09" y2="277.84" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="803.45" y1="288.54" x2="803.05" y2="277.94" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<line x1="801.15" y1="288.59" x2="801.02" y2="277.99" stroke="#f87171" stroke-width="1.3" opacity="0.8"/>
<text x="715" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#f87171">カスケード 3</text>
<text x="715" y="302.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">点 4 × 方向 256 = 1,024 本</text>
<text x="715" y="322.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">届く距離 16 〜 64</text>
<text x="715" y="340.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">点の間隔 8、方向 256 分割</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">光線の総数:</text>
<text x="150" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0551;0.0553;1.0000" values="1;1;0;0"/></text>
<text x="150" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1,024<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0551;0.0553;0.2083;0.2085;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">2,048<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2083;0.2085;0.3615;0.3617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3,072<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3617;0.5147;0.5149;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4,096<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5147;0.5149;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6424;0.6426;1.0000" values="0;0;1;1"/><rect x="330" y="392" width="600" height="118" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="416" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1e3a8a">カスケード 4 段: 光線 4,096 本</text>
<text x="346" y="442" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">全部の点が、全方向へ、最大距離まで調べる方法: 65,536 本(約 16 倍)</text>
<text x="346" y="466" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">近くは細かい点で、遠くは粗い点でよい。後の段の結果を、前の段に混ぜる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くの光は、細かい位置の違いが、見た目にほとんど効かない<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">段が進むごとに、点は 4 分の 1、方向は 4 倍、届く距離は 4 倍<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.6551;0.6553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">どの段も光線の数が同じなので、全体の計算量が、距離に関係なく一定になる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6551;0.6553;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:radiance-cascades:end -->

### The Idea: Trading Space for Direction {#発想空間と方向のトレードオフ}

ある点が受け取る光を正確に知りたいとします。素朴に考えれば、点（空間）を細かく取り、さらに方向も細かく取って、その積の数だけレイが要ります。画面全体に対して、画素ごとに数百本のレイは、とても払えません。

ここで、Sannikov は次の観察をしました。<strong>光の届く距離によって、必要な空間の細かさと方向の細かさが逆になる</strong>のです。

近くの光源（短いレイで届く光）を考えます。近い光源は、点の位置が少し動くと、見える方向が大きく変わります。だから、点は細かく取らなければなりません。一方、近い光源は大きく見えるので、方向は粗くても、見逃しません。逆に、遠くの光源（長いレイで届く光）では、点が少し動いても、見える方向はほとんど変わらないので、点は粗くてかまいません。ただし、遠い光源は小さく見えるので、見逃さないように、方向は細かく取らなければなりません。

つまり、「細かい点 × 粗い方向」で近距離を、「粗い点 × 細かい方向」で遠距離を担当させれば、どちらも少ないサンプルで済みます。

### Cascades {#カスケード}

この観察を、複数の<strong>カスケード</strong>という階層で実現します。カスケード 0 は、最も細かい間隔で配置したプローブで、持つ方向の数は少なく、担当するのは近距離です。カスケード 1 は、プローブの間隔が倍（数は 1/4）、方向の数は 4 倍（2D の場合）で、やや遠い距離を担当します。カスケード 2 は、さらに間隔が倍、方向が 4 倍で、さらに遠くを担当し、以下同様に続きます。

各カスケードのレイは、全距離を追うのでなく、<strong>自分の担当する距離の区間だけ</strong>を追います。区間は、カスケード n の区間を [t_n, t_(n+1)] として、距離が 4 倍ずつ伸びるように決めます。近いカスケードは短い区間を、遠いカスケードは長い区間を担当するので、全体で原点から無限遠まで、隙間なく覆えます。

プローブの数が 1/4 になり、方向の数が 4 倍になるので、<strong>カスケードごとのレイの総数は一定</strong>になります。カスケードの数は距離の対数に比例して増えるだけなので、全体の計算量は「画素数 × カスケードの数」と、とても小さく済みます。

### Merging: Passing Distant Light to the Near Side {#マージ遠い光を近い方に伝える}

各カスケードは、自分の区間の光しか知りません。全体の光を得るには、<strong>遠いカスケードの結果を、近いカスケードに伝えます</strong>（マージ）。

具体的には、カスケード n のある方向のレイが、自分の区間を進んで何にも当たらなかったとします。そのレイが見ている、さらに遠くの光は、カスケード n+1 が担当しています。そこで、カスケード n+1 の近傍の 4 つのプローブから、同じ方向をカバーしているレイの値を、補間して持ってきます。当たった場合は、当たった点の光が、そのレイの値です。この処理を、最も遠いカスケードから、順にカスケード 0 まで繰り返すと、カスケード 0 に全距離の光が集まります。

```hlsl
float3 MergeCascade(int cascade, float2 probe_pos, int dir_index) {
  float4 near = TraceInterval(cascade, probe_pos, dir_index);
  float3 radiance = near.rgb;
  float transmittance = near.a;
  if (cascade + 1 < kCascadeCount && transmittance > 0.0) {
    float3 far = SampleUpperCascade(cascade + 1, probe_pos, dir_index);
    radiance += transmittance * far;
  }
  return radiance;
}
```

`near.a` は、区間の途中で何かに遮られなかった割合（透過率）で、遮られていれば遠くの光は見えないので、0 に近づきます。補間によって、段差が出ないように、カスケード間をなめらかにつなぎます。

### Computing a Pixel's Irradiance {#画素の放射照度の求め方}

カスケード 0 のプローブは、全方向（少数の方向）の光を持っています。各画素は、近傍のカスケード 0 のプローブから、法線に沿った余弦重みで方向を足し合わせることで、放射照度を得ます。

### Properties {#性質}

Radiance Cascades は、ランダムを使わず、規則的なサンプルなので、<strong>ノイズがありません</strong>。計算量は、画素数に比例して、ほぼ一定です。2D ゲームの GI で特に成功しており、『Path of Exile 2』の GI の仕組みとして使われています。3D への拡張は、方向が球面（2 次元）に広がり、サンプル数が増えるため、研究と実装が進んでいる段階です。

原典は、Alexander Sannikov による公開資料と、Osborne らによる論文（2024 年）です。この手法は発展の途中なので、最新の情報は原典を確認してください。

## Common Mistakes {#よくあるミス}

??? failure "階層の境目に、段差が見える"
    **階層間を補間**して、なめらかにつなぐ。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **距離ごとに、解像度を変えて持つ**
    - [x] **ノイズが少なく、安定**

## References {#参考}

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## Related Pages {#関連ページ}

- [Ray-Traced GI](index.md)
- [Choosing a Method](choosing.md)
- [SSGI](../ssgi.md)
