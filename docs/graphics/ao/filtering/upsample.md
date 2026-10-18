---
title: Upsampling
tags:
  - 描画
---

# Upsampling

**AO は、半解像度（または 1/4）で計算する**と**コストが大きく減ります**が、**フル解像度に戻すとき、単純な拡大では、エッジがにじみます**。**フル解像度の深度を見ながら、近い深度の低解像度サンプルだけを重く混ぜる「深度を考慮したアップサンプル」**が**必要**です。このページでは、**低解像度で計算する理由・深度を見るアップサンプル・実装**を説明します。

!!! tip "ポイント"
    - **低解像度で AO を計算**し、**コストを 1/4**。
    - **拡大時に、フル解像度の深度**と**低解像度の深度**を**比べ、近いものを重く**。
    - **単純なバイリニアは、エッジで AO がにじむ**。
    - **ジョイント バイラテラル アップサンプル**と呼ばれる。

## アップサンプル：低解像度から戻す
AO は<strong>低周波（なめらか）</strong>なので**半分や 1/4 の解像度**で計算して、**拡大**すると**コストを大きく減らせます**（[低解像度のエフェクト](../../../rendering/low-res-effects.md)）。しかし、**単純なバイリニア拡大**は、**境界でにじみます**。

<!-- fig:ao-upsample:begin -->

<svg class="fig illust motion" data-fig="ao-upsample" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ao-upsample" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">AO のアップサンプル: 半分の解像度で計算した AO を、フル解像度の深度を見ながら、輪郭を守って戻す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素。左は手前(深度 1、AO 0.9)、右は奥(深度 3、AO 0.4)。AO を 24 画素で計算し、48 画素へ戻す</text>
<text x="60.0" y="98" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">深度(濃い = 手前)</text>
<rect x="60.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="77.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="94.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="111.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="128.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="145.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="162.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="179.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="196.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="213.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="230.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="247.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="264.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="281.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="298.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="315.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="332.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="349.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="366.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="383.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="400.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="417.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="434.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="451.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="468.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="485.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="502.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="519.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="536.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="553.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="570.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="587.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="604.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="621.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="638.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="655.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="672.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="689.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="706.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="723.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="740.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="757.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="774.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="791.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="808.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="825.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="842.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="859.0" y="104.0" width="17.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="60.0" y="104" width="816.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="146" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">半分の解像度で計算した AO(24 画素)</text>
<rect x="60.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="94.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="128.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="162.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="196.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="230.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="264.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="298.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="332.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="366.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="400.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="434.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="468.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="502.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="536.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="570.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="604.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="638.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="672.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="706.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="740.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="774.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="842.0" y="150.0" width="34.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="60.0" y="150" width="816.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="202" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">① そのまま 2 倍に拡大(最近傍)</text>
<rect x="60.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="77.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="94.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="111.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="128.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="145.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="162.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="179.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="196.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="213.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="230.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="247.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="264.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="281.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="298.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="315.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="332.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="349.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="366.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="383.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="400.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="417.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="434.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#e5e7eb;#666666"/></rect>
<rect x="451.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1076" values="#e5e7eb;#666666"/></rect>
<rect x="468.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#e5e7eb;#666666"/></rect>
<rect x="485.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#666666"/></rect>
<rect x="502.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1129" values="#e5e7eb;#666666"/></rect>
<rect x="519.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#e5e7eb;#666666"/></rect>
<rect x="536.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#e5e7eb;#666666"/></rect>
<rect x="553.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1182" values="#e5e7eb;#666666"/></rect>
<rect x="570.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#666666"/></rect>
<rect x="587.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1218" values="#e5e7eb;#666666"/></rect>
<rect x="604.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1236" values="#e5e7eb;#666666"/></rect>
<rect x="621.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#e5e7eb;#666666"/></rect>
<rect x="638.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#e5e7eb;#666666"/></rect>
<rect x="655.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#666666"/></rect>
<rect x="672.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#e5e7eb;#666666"/></rect>
<rect x="689.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1324" values="#e5e7eb;#666666"/></rect>
<rect x="706.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1342" values="#e5e7eb;#666666"/></rect>
<rect x="723.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#e5e7eb;#666666"/></rect>
<rect x="740.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#666666"/></rect>
<rect x="757.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1396" values="#e5e7eb;#666666"/></rect>
<rect x="774.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#e5e7eb;#666666"/></rect>
<rect x="791.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1431" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1449" values="#e5e7eb;#666666"/></rect>
<rect x="825.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#666666"/></rect>
<rect x="842.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1484" values="#e5e7eb;#666666"/></rect>
<rect x="859.0" y="206.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1502" values="#e5e7eb;#666666"/></rect>
<rect x="60.0" y="206" width="816.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><text x="884.0" y="222" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">ずれ 0.010</text>
</g>
<text x="60.0" y="258" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">② バイリニア補間</text>
<rect x="60.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2267" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="77.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2284" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="94.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2302" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="111.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2320" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="128.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2338" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="145.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2356" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="162.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2373" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="179.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="196.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2409" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="213.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2427" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="230.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2444" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="247.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2462" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="264.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2480" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="281.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2498" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="298.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2516" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="315.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2533" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="332.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2551" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="349.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2569" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="366.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2587" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="383.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2604" values="#e5e7eb;#d6d6d6"/></rect>
<rect x="400.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2622" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="417.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2640" values="#e5e7eb;#969696"/></rect>
<rect x="434.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#e5e7eb;#767676"/></rect>
<rect x="451.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2676" values="#e5e7eb;#666666"/></rect>
<rect x="468.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#666666"/></rect>
<rect x="485.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#666666"/></rect>
<rect x="502.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#666666"/></rect>
<rect x="519.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#666666"/></rect>
<rect x="536.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#666666"/></rect>
<rect x="553.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#666666"/></rect>
<rect x="570.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#666666"/></rect>
<rect x="587.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#666666"/></rect>
<rect x="604.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#666666"/></rect>
<rect x="621.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#666666"/></rect>
<rect x="638.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#666666"/></rect>
<rect x="655.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#666666"/></rect>
<rect x="672.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#666666"/></rect>
<rect x="689.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#666666"/></rect>
<rect x="706.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#666666"/></rect>
<rect x="723.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#666666"/></rect>
<rect x="740.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#666666"/></rect>
<rect x="757.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#e5e7eb;#666666"/></rect>
<rect x="774.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#e5e7eb;#666666"/></rect>
<rect x="791.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3049" values="#e5e7eb;#666666"/></rect>
<rect x="825.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#666666"/></rect>
<rect x="842.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#e5e7eb;#666666"/></rect>
<rect x="859.0" y="262.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3102" values="#e5e7eb;#666666"/></rect>
<rect x="60.0" y="262" width="816.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;1.0000" values="0;0;1;1"/><text x="884.0" y="278" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">ずれ 0.010</text>
</g>
<text x="60.0" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">③ 深度を見て、混ぜる相手を選ぶ(ジョイント バイラテラル)</text>
<rect x="60.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3867" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="77.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3884" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="94.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3902" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="111.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3920" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="128.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3938" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="145.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3956" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="162.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="179.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3991" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="196.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4009" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="213.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4027" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="230.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4044" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="247.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4062" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="264.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4080" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="281.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4098" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="298.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4116" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="315.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="332.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4151" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="349.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4169" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="366.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4187" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="383.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4204" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="400.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4222" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="417.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#e5e7eb;#676767"/></rect>
<rect x="434.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4258" values="#e5e7eb;#666666"/></rect>
<rect x="451.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4276" values="#e5e7eb;#666666"/></rect>
<rect x="468.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="#e5e7eb;#666666"/></rect>
<rect x="485.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4311" values="#e5e7eb;#666666"/></rect>
<rect x="502.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="#e5e7eb;#666666"/></rect>
<rect x="519.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4347" values="#e5e7eb;#666666"/></rect>
<rect x="536.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4364" values="#e5e7eb;#666666"/></rect>
<rect x="553.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4382" values="#e5e7eb;#666666"/></rect>
<rect x="570.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4400" values="#e5e7eb;#666666"/></rect>
<rect x="587.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4418" values="#e5e7eb;#666666"/></rect>
<rect x="604.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4436" values="#e5e7eb;#666666"/></rect>
<rect x="621.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4453" values="#e5e7eb;#666666"/></rect>
<rect x="638.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4471" values="#e5e7eb;#666666"/></rect>
<rect x="655.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4489" values="#e5e7eb;#666666"/></rect>
<rect x="672.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4507" values="#e5e7eb;#666666"/></rect>
<rect x="689.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4524" values="#e5e7eb;#666666"/></rect>
<rect x="706.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4542" values="#e5e7eb;#666666"/></rect>
<rect x="723.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4560" values="#e5e7eb;#666666"/></rect>
<rect x="740.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4578" values="#e5e7eb;#666666"/></rect>
<rect x="757.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4596" values="#e5e7eb;#666666"/></rect>
<rect x="774.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4613" values="#e5e7eb;#666666"/></rect>
<rect x="791.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4631" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4649" values="#e5e7eb;#666666"/></rect>
<rect x="825.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4667" values="#e5e7eb;#666666"/></rect>
<rect x="842.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#666666"/></rect>
<rect x="859.0" y="318.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#666666"/></rect>
<rect x="60.0" y="318" width="816.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4754;0.4756;1.0000" values="0;0;1;1"/><text x="884.0" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ずれ 0.000</text>
</g>
<text x="60.0" y="370" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">正解(フル解像度)</text>
<rect x="60.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="77.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="94.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="111.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="128.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="145.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="162.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="179.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="196.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="213.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="230.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="247.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="264.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="281.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="298.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="315.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="332.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="349.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="366.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="383.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="400.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="417.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="434.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="451.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="468.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="485.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="502.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="519.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="536.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="553.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="570.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="587.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="604.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="621.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="638.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="655.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="672.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="689.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="706.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="723.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="740.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="757.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="774.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="791.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="825.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="842.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="859.0" y="374.0" width="17.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="60.0" y="374" width="816.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5332;0.5333;1.0000" values="0;0;1;1"/><rect x="40" y="440" width="880" height="72" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="464" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">輪郭のずれ(平均): 最近傍 0.010 / バイリニア 0.010 / 深度つき 0.000</text>
<text x="56" y="488" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">バイリニアは、輪郭をまたいで混ぜる。深度が近い低解像度の画素だけを選べば、輪郭が守られる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">AO は、半分の解像度で計算して、計算量を 1/4 にする<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">フル解像度へ戻すとき、輪郭をまたいで混ぜると、にじむ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.5465;0.5467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">フル解像度の深度で、混ぜる相手を選ぶ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ao-upsample:end -->

### なぜ単純な拡大ではだめなのか

低解像度の AO 画像の 1 画素は、フル解像度の 2×2 画素（半分の解像度の場合）に対応します。単純なバイリニア補間で拡大すると、隣り合う低解像度画素の AO を、距離だけを手がかりに混ぜます。物体の輪郭では、隣り合う 2 つの低解像度画素が<strong>手前の物体と奥の背景</strong>のように別の面に乗っていることがあります。すると、背景の画素に、手前の物体の AO が混じり、物の輪郭にぼんやりした暗い縁やにじみが出ます。

AO はもともと低周波で、面の内側ではなめらかに変化するので、拡大自体は問題ありません。問題は<strong>面の境界をまたいで混ぜる</strong>ことだけです。

### ジョイント バイラテラル アップサンプル

この問題を解決するのが、「フル解像度の深度を手がかりにして、補間の重みを調整する」方法です。手がかり（深度）が、補間する対象（AO）とは別の画像から来るので、「ジョイント（共同）」バイラテラルと呼ばれます。

考え方は、次のとおりです。フル解像度の 1 画素について、その周囲の低解像度画素 4 つ（2×2）を見ます。それぞれの低解像度画素には、その場所の深度を覚えておきます（AO を計算したときの縮小した深度）。フル解像度の画素の深度に<strong>近い深度を持つ低解像度画素ほど</strong>、同じ面に乗っているはずなので、重みを大きくします。深度が大きく違う低解像度画素は、別の面なので、ほとんど無視します。

式にすると、各低解像度画素 i の重みは、普通のバイリニアの重みに、深度の近さを掛けたものになります。

<div class="formula">w_i = (バイリニアの重み) × 1 / (ε + |z_full − z_low_i|)　　AO = Σ w_i · AO_low_i / Σ w_i</div>

ε は 0 で割らないための小さな値です。深度の差が大きいほど重みが小さくなり、境界をまたいだ混ぜ方が自然に避けられます。

```hlsl
float UpsampleAO(float2 uv_full) {
  float z_full = LinearDepth(uv_full);
  float2 low_pos = uv_full * low_size - 0.5;
  float2 f = frac(low_pos);
  int2 base = int2(floor(low_pos));

  float sum = 0.0;
  float weight_sum = 0.0;
  [unroll] for (int y = 0; y < 2; ++y) {
    [unroll] for (int x = 0; x < 2; ++x) {
      int2 p = base + int2(x, y);
      float w = (x == 0 ? 1.0 - f.x : f.x) * (y == 0 ? 1.0 - f.y : f.y);
      w *= 1.0 / (0.001 + abs(z_full - low_depth_tex.Load(int3(p, 0)).r));
      sum += ao_low_tex.Load(int3(p, 0)).r * w;
      weight_sum += w;
    }
  }
  return sum / weight_sum;
}
```

### 実装で気をつけること

低解像度の深度を、<strong>AO を計算したときと同じもの</strong>で持っておく必要があります。縮小の方法（代表の 1 点を選ぶ、最小を取るなど）が違うと、重みが合わなくなります。

もう 1 つの方式として、<strong>最も深度が近い低解像度画素を 1 つだけ選ぶ</strong>方法もあります。境界のシャープさは最高ですが、面の内側でも選ばれる画素が切り替わる所で階段状の段差が出やすいです。重み付けで混ぜる方式のほうが、見た目が安定します。

### より良いやり方：法線も使う

深度が近くても向きの違う面（部屋の隅の壁と床）では、AO が急に変わります。深度に加えて<strong>法線の近さ</strong>も重みに掛ければ、隅の境界もよりきれいに守れます。また、2×2 でなく 3×3 の範囲を見ると、低解像度のサンプルが足りない場所（輪郭の細い所）を補えます。近年の実装は、アップサンプルを時間蓄積と一体にして、フル解像度のサンプルを少数だけ追加で撒く方式もあります（[Typical Pipeline](pipeline.md)）。

## よくあるミス

??? failure "バイリニアで拡大して、物の輪郭に暗いにじみが出る"
    **深度を見るアップサンプル**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **低解像度で計算 ＋ 深度を見て拡大**
    - [x] **エッジのにじみを防ぐ**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [AO Filtering](index.md)
- [Bilateral Blur](bilateral-blur.md)
- [Typical Pipeline](pipeline.md)
