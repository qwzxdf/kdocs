---
title: Anti-Aliasing
tags:
  - 描画
---

# Anti-Aliasing

**ピクセルは四角い格子**なので、**斜めの線や細い物の縁が、階段状（ジャギー）に見えます**。これが**エイリアシング**で、<strong>アンチエイリアシング（AA）</strong>は、**これを滑らかにする技術**です。**方式が多く、画質・速さ・弱点がそれぞれ違います**。このセクションでは、**エイリアシングの原因・SSAA/MSAA・FXAA・SMAA・TAA・TAA の課題・比較と選び方**を、**1 つずつ別のページ**で説明します。

## エイリアシングの 3 つの種類

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="エイリアシングの種類">
<text x="20" y="26" class="fig-title">エイリアシングは、見え方で 3 種類</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">① ジャギー（縁）</text>
<g fill="#334155"><rect x="0" y="100" width="20" height="20"/><rect x="20" y="80" width="20" height="20"/><rect x="40" y="60" width="20" height="20"/><rect x="60" y="40" width="20" height="20"/><rect x="80" y="20" width="20" height="20"/></g>
<text x="0" y="146" style="font-size:12px">斜めの縁が階段状</text>
</g>
<g transform="translate(300,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">② 細い物の途切れ</text>
<g fill="#334155"><rect x="0" y="40" width="20" height="4"/><rect x="40" y="40" width="20" height="4"/><rect x="80" y="40" width="20" height="4"/><rect x="20" y="70" width="20" height="4"/><rect x="60" y="70" width="20" height="4"/></g>
<text x="0" y="146" style="font-size:12px">電線・フェンスが途切れる</text>
</g>
<g transform="translate(560,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">③ ちらつき・モアレ</text>
<g stroke="#334155" stroke-width="2"><line x1="0" y1="10" x2="140" y2="10"/><line x1="0" y1="26" x2="140" y2="30"/><line x1="0" y1="42" x2="140" y2="52"/><line x1="0" y1="58" x2="140" y2="74"/><line x1="0" y1="74" x2="140" y2="96"/></g>
<text x="0" y="146" style="font-size:12px">縞模様が動くとチラつく</text>
</g>
</svg>

| 種類 | 原因 | 効く方式 |
| --- | --- | --- |
| **ジオメトリの縁のジャギー** | **三角形の縁を画素の中心で判定するから** | **MSAA・FXAA・SMAA・TAA** |
| **シェーダー内のエイリアシング** | **スペキュラ・法線マップなど、1 画素内で急変する値** | **TAA・SSAA**（MSAA は効かない） |
| **時間的なちらつき** | **動くとき、サンプルの位置が変わり、出たり消えたりする** | **TAA** |

## 動きで見る：TAA のジッター

<!-- fig:taa-jitter:begin -->

<svg class="fig illust motion" data-fig="taa-jitter" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-taa-jitter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">TAA: 毎フレーム、画素の中の別の場所を測り、履歴と平均して縁をなめらかにする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">三角形の縁(斜めの線)を、12×8 画素で描く。1 フレームだけ vs 8 フレームぶん平均</text>
<rect x="30" y="100" width="288.0" height="192.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">1 フレームだけ(画素の中心で 1 回測る)</text>
<rect x="30.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="54.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="78.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="102.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="126.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="150.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="174.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="198.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="222.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="246.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="270.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="78.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="102.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="126.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="150.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="174.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="198.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="222.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="246.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="270.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="78.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="102.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="126.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="150.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="174.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="198.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="222.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="246.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="270.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="78.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="102.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="126.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="150.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="174.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="198.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="222.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="246.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="270.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="78.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="102.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="126.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="150.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="174.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="198.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="222.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="246.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="270.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="78.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="102.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="126.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="150.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="174.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="198.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="222.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="246.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="270.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="78.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="102.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="126.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="150.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="174.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="198.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="222.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="246.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="270.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="294.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="30.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="54.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="78.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="102.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="126.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="150.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="174.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="198.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="222.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="246.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="270.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="294.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0270" values="#f1f5f9;#334155"/></rect>
<rect x="345" y="100" width="288.0" height="192.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="345" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">TAA(ジッター + 履歴の平均)</text>
<rect x="345.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="369.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="393.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="417.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="441.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="465.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="489.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="513.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="537.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="561.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="585.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="609.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#727d8c;#626e7e;#596576;#535f70;#4e5b6c;#4b586a"/></rect>
<rect x="369.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#929ba7;#b2b9c2;#c2c8d0;#cbd1d8;#d1d7de;#d6dbe2;#c2c8d0"/></rect>
<rect x="393.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="417.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="441.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="465.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="489.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="513.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="537.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="561.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="585.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="609.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="369.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="393.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#727d8c;#626e7e;#596576;#535f70;#4e5b6c;#4b586a"/></rect>
<rect x="417.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#d9dee4"/></rect>
<rect x="441.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="465.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="489.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="513.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="537.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="561.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="585.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="609.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="369.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="393.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="417.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="441.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#929ba7;#b2b9c2;#929ba7;#7f8997;#929ba7;#a0a8b3;#929ba7"/></rect>
<rect x="465.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#d9dee4"/></rect>
<rect x="489.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="513.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="537.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="561.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="585.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="609.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="369.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="393.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="417.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="441.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="465.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="489.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#929ba7;#b2b9c2;#929ba7;#7f8997;#929ba7;#a0a8b3;#929ba7"/></rect>
<rect x="513.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#d9dee4"/></rect>
<rect x="537.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="561.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="585.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="609.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="369.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="393.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="417.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="441.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="465.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="489.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="513.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#727d8c;#626e7e;#596576;#535f70;#4e5b6c;#4b586a"/></rect>
<rect x="537.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#929ba7;#b2b9c2;#929ba7;#7f8997;#929ba7;#a0a8b3;#929ba7"/></rect>
<rect x="561.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#d9dee4"/></rect>
<rect x="585.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="609.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="369.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="393.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="417.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="441.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="465.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="489.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="513.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="537.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="561.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#727d8c;#626e7e;#596576;#535f70;#4e5b6c;#4b586a"/></rect>
<rect x="585.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#f1f5f9;#929ba7;#b2b9c2;#c2c8d0;#a5adb7;#b2b9c2;#bbc2ca;#aab2bc"/></rect>
<rect x="609.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="345.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="369.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="393.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="417.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="441.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="465.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="489.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="513.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="537.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="561.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="585.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#334155;#334155;#334155;#334155;#334155;#334155"/></rect>
<rect x="609.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865;0.1784;0.2703;0.3622;0.4541;0.5459;0.6378;0.7297" values="#f1f5f9;#334155;#334155;#727d8c;#626e7e;#596576;#535f70;#4e5b6c;#4b586a"/></rect>
<rect x="660" y="100" width="288.0" height="192.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="660" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">正解(1 画素あたり 64 回測る)</text>
<rect x="660.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#eef2f6"/></rect>
<rect x="684.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="708.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="732.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="756.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="780.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="804.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="828.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="852.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="876.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="900.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="924.0" y="100.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#576374"/></rect>
<rect x="684.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#bfc5cd"/></rect>
<rect x="708.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="732.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="756.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="780.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="804.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="828.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="852.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="876.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="900.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="924.0" y="124.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="684.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="708.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#657181"/></rect>
<rect x="732.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#cdd3da"/></rect>
<rect x="756.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="780.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="804.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="828.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="852.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="876.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="900.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="924.0" y="148.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="684.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="708.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="732.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#364458"/></rect>
<rect x="756.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#7a8492"/></rect>
<rect x="780.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#dce1e7"/></rect>
<rect x="804.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="828.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="852.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="876.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="900.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="924.0" y="172.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="684.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="708.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="732.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="756.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="780.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#39475a"/></rect>
<rect x="804.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#8f98a4"/></rect>
<rect x="828.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#e5eaef"/></rect>
<rect x="852.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="876.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="900.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="924.0" y="196.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="684.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="708.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="732.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="756.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="780.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="804.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="828.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#424f62"/></rect>
<rect x="852.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#a1a9b4"/></rect>
<rect x="876.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#eef2f6"/></rect>
<rect x="900.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="924.0" y="220.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="684.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="708.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="732.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="756.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="780.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="804.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="828.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="852.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="876.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#4e5a6c"/></rect>
<rect x="900.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#b3bac3"/></rect>
<rect x="924.0" y="244.0" width="24.3" height="24.3" fill="#f1f5f9"/>
<rect x="660.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="684.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="708.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="732.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="756.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="780.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="804.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="828.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="852.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="876.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="900.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#334155"/></rect>
<rect x="924.0" y="268.0" width="24.3" height="24.3" fill="#f1f5f9"><animate attributeName="fill" dur="18.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8270" values="#f1f5f9;#606b7b"/></rect>
<g opacity="0.35"><line x1="54.0" y1="100" x2="54.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="78.0" y1="100" x2="78.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="102.0" y1="100" x2="102.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="126.0" y1="100" x2="126.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="150.0" y1="100" x2="150.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="174.0" y1="100" x2="174.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="198.0" y1="100" x2="198.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="222.0" y1="100" x2="222.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="246.0" y1="100" x2="246.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="270.0" y1="100" x2="270.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="294.0" y1="100" x2="294.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="124.0" x2="318.0" y2="124.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="148.0" x2="318.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="172.0" x2="318.0" y2="172.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="196.0" x2="318.0" y2="196.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="220.0" x2="318.0" y2="220.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="244.0" x2="318.0" y2="244.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="268.0" x2="318.0" y2="268.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="30" y="100" width="288.0" height="192.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0.35"><line x1="369.0" y1="100" x2="369.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="393.0" y1="100" x2="393.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="417.0" y1="100" x2="417.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="441.0" y1="100" x2="441.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="465.0" y1="100" x2="465.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="489.0" y1="100" x2="489.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="513.0" y1="100" x2="513.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="537.0" y1="100" x2="537.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="561.0" y1="100" x2="561.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="585.0" y1="100" x2="585.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="609.0" y1="100" x2="609.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="124.0" x2="633.0" y2="124.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="148.0" x2="633.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="172.0" x2="633.0" y2="172.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="196.0" x2="633.0" y2="196.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="220.0" x2="633.0" y2="220.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="244.0" x2="633.0" y2="244.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="345" y1="268.0" x2="633.0" y2="268.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="345" y="100" width="288.0" height="192.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0.35"><line x1="684.0" y1="100" x2="684.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="708.0" y1="100" x2="708.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="732.0" y1="100" x2="732.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="756.0" y1="100" x2="756.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="780.0" y1="100" x2="780.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="804.0" y1="100" x2="804.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="828.0" y1="100" x2="828.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="852.0" y1="100" x2="852.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="876.0" y1="100" x2="876.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="900.0" y1="100" x2="900.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="924.0" y1="100" x2="924.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="124.0" x2="948.0" y2="124.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="148.0" x2="948.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="172.0" x2="948.0" y2="172.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="196.0" x2="948.0" y2="196.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="220.0" x2="948.0" y2="220.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="244.0" x2="948.0" y2="244.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660" y1="268.0" x2="948.0" y2="268.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="660" y="100" width="288.0" height="192.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<rect x="30" y="360" width="150" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">このフレームで測る場所</text>
<rect x="30" y="360" width="150" height="150" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" rx="6"/>
<line x1="105" y1="360" x2="105" y2="510" stroke="#e2e8f0" stroke-width="1"/>
<line x1="30" y1="435" x2="180" y2="435" stroke="#e2e8f0" stroke-width="1"/>
<circle cx="105.0" cy="411.67" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0646;0.0649;0.1565;0.1568;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="105.0" cy="411.67" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1565;0.1568;1.0000" values="0;0;1;1"/></circle>
<text x="113.0" y="405.67" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0646;0.0649;0.1565;0.1568;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="70.0" cy="458.33" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1565;0.1568;0.2484;0.2486;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="70.0" cy="458.33" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2484;0.2486;1.0000" values="0;0;1;1"/></circle>
<text x="78.0" y="452.33" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1565;0.1568;0.2484;0.2486;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="140.0" cy="380.56" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2484;0.2486;0.3403;0.3405;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="140.0" cy="380.56" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3403;0.3405;1.0000" values="0;0;1;1"/></circle>
<text x="148.0" y="374.56" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2484;0.2486;0.3403;0.3405;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="52.5" cy="427.22" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3403;0.3405;0.4322;0.4324;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="52.5" cy="427.22" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4322;0.4324;1.0000" values="0;0;1;1"/></circle>
<text x="60.5" y="421.22" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3403;0.3405;0.4322;0.4324;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="122.5" cy="473.89" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4322;0.4324;0.5241;0.5243;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="122.5" cy="473.89" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5241;0.5243;1.0000" values="0;0;1;1"/></circle>
<text x="130.5" y="467.89" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4322;0.4324;0.5241;0.5243;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="87.5" cy="396.11" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5241;0.5243;0.6160;0.6162;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="87.5" cy="396.11" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6160;0.6162;1.0000" values="0;0;1;1"/></circle>
<text x="95.5" y="390.11" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">6<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5241;0.5243;0.6160;0.6162;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="157.5" cy="442.78" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6160;0.6162;0.7079;0.7081;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="157.5" cy="442.78" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7079;0.7081;1.0000" values="0;0;1;1"/></circle>
<text x="165.5" y="436.78" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">7<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6160;0.6162;0.7079;0.7081;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="43.75" cy="489.44" r="6" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7079;0.7081;1.0000" values="0;0;1;1"/></circle>
<circle cx="43.75" cy="489.44" r="3" fill="#c4b5fd" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7998;0.8000;1.0000" values="0;0;1;1"/></circle>
<text x="51.75" y="483.44" text-anchor="start" style="font-size:10px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7079;0.7081;0.7998;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="210" y="360" width="340" height="150" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="210" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">正解とのずれ(小さいほど良い)</text>
<line x1="232" y1="490" x2="532" y2="490" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="232" y1="402.03" x2="532" y2="402.03" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<text x="532" y="396.03416149068323" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d">1 フレームだけ: 0.034</text>
<circle cx="232.0" cy="394.35" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0917;0.0919;1.0000" values="0;0;1;1"/></circle>
<text x="232.0" y="384.35" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.036<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0917;0.0919;1.0000" values="0;0;1;1"/></text>
<text x="232.0" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<circle cx="274.86" cy="436.2" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1836;0.1838;1.0000" values="0;0;1;1"/></circle>
<text x="274.86" y="426.2" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.021<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1836;0.1838;1.0000" values="0;0;1;1"/></text>
<text x="274.86" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<circle cx="317.71" cy="439.9" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2755;0.2757;1.0000" values="0;0;1;1"/></circle>
<text x="317.71" y="429.9" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.019<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2755;0.2757;1.0000" values="0;0;1;1"/></text>
<text x="317.71" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">3</text>
<circle cx="360.57" cy="459.25" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3674;0.3676;1.0000" values="0;0;1;1"/></circle>
<text x="360.57" y="449.25" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.012<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3674;0.3676;1.0000" values="0;0;1;1"/></text>
<text x="360.57" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<circle cx="403.43" cy="458.4" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4592;0.4595;1.0000" values="0;0;1;1"/></circle>
<text x="403.43" y="448.4" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.012<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4592;0.4595;1.0000" values="0;0;1;1"/></text>
<text x="403.43" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5</text>
<circle cx="446.29" cy="460.96" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5511;0.5514;1.0000" values="0;0;1;1"/></circle>
<text x="446.29" y="450.96" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.011<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5511;0.5514;1.0000" values="0;0;1;1"/></text>
<text x="446.29" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6</text>
<circle cx="489.14" cy="456.69" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6430;0.6432;1.0000" values="0;0;1;1"/></circle>
<text x="489.14" y="446.69" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.013<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6430;0.6432;1.0000" values="0;0;1;1"/></text>
<text x="489.14" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">7</text>
<circle cx="532.0" cy="463.52" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7349;0.7351;1.0000" values="0;0;1;1"/></circle>
<text x="532.0" y="453.52" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#2563eb" opacity="0">0.010<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7349;0.7351;1.0000" values="0;0;1;1"/></text>
<text x="532.0" y="504" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">8</text>
<text x="532" y="516" text-anchor="end" style="font-size:11px;font-weight:500;fill:#64748b">平均したフレーム数</text>
<text x="580" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">平均したフレーム数:</text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0863;0.0865;1.0000" values="1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">1<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0863;0.0865;0.1782;0.1784;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">2<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1782;0.1784;0.2701;0.2703;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">3<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2701;0.2703;0.3619;0.3622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">4<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3619;0.3622;0.4538;0.4541;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4538;0.4541;0.5457;0.5459;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5457;0.5459;0.6376;0.6378;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6376;0.6378;0.7295;0.7297;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="374" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">8<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7295;0.7297;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.8430;0.8432;1.0000" values="0;0;1;1"/><rect x="580" y="392" width="350" height="118" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="596" y="416" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">1 フレームだけ: ずれ 0.034(階段状)</text>
<text x="596" y="440" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">TAA 8 フレーム: ずれ 0.010(70% 減)</text>
<text x="596" y="464" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">1 フレームあたりの測定は、どちらも 1 回</text>
<text x="596" y="486" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">(測る場所を毎回ずらしているだけ)</text>
</g>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">斜めの縁は、画素の中心で 1 回測ると、階段状(ジャギー)になる<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0646;0.0649;1.0000" values="1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">毎フレーム、測る場所を少しずつずらして、履歴と平均する<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0646;0.0649;0.7998;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">右の「正解」は、1 画素を 64 回測った結果<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7998;0.8000;0.8971;0.8973;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">TAA は 1 フレームあたり 1 回の測定で、正解に近づく<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.8971;0.8973;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:taa-jitter:end -->

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [MSAA](msaa.md) | SSAA との違い・サンプル パターン・リゾルブ・弱点 |
| [FXAA](fxaa.md) | 輝度から縁を見つけてぼかす・1 パスの後処理 |
| [SMAA](smaa.md) | 縁検出・パターン判定・重みの計算・ブレンド |
| [TAA](taa.md) | ジッター・再投影・履歴のクランプ・合成 |
| [TAA Challenges](taa-challenges.md) | ゴースト・ぼけ・ちらつき・アップスケール |
| [Comparison and Choosing](comparison.md) | 方式の比較表・組み合わせ・目的別の選び方 |

## 関連ページ

- [Post-Processing](../index.md)
- [Motion Blur](../motion-blur/index.md)
- [TAA・アップスケーラ・VRS](../../../rendering/taa-upscaling.md)
- [ラスタライズ](../../../3d/render-flow/rasterize.md)
