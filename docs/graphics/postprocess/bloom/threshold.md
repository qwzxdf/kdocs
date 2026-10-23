---
title: Threshold
tags:
  - 描画
---

# Threshold

<strong>ブルームの最初の工程</strong>は、「どこを光らせるか」を決めることです。画面のうち、一定より明るい部分だけを取り出すのがしきい値（スレッショルド）方式です。暗い物がにじんで画面全体がぼんやりするのを防げます。このページでは、単純なしきい値・ソフト ニー（滑らかな立ち上がり）・しきい値なしの方式・HDR だからできること・より良いやり方を説明します。

!!! tip "ポイント"
    - しきい値 ＝ <strong>一定の明るさ以上だけを取り出す</strong>。<strong>それ以下は 0（黒）</strong>。
    - 単純な切り捨て（ハード）は境で「ぱっ」と出入りし、ちらつく。ソフト ニーで滑らかに立ち上げる。
    - HDR だから、「1 を超えた部分」を光らせるという物理的な基準が使える。
    - 取り出す量は「超過分」（元の値 − しきい値）にすると自然。
    - しきい値なしの方式はぱっと出ないが、全体が柔らかくなる。
    - しきい値は、露出の後（露出済みの明るさで判断）。

!!! info "このページを読む前に"
    - [Bloom](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:bloom-threshold:begin -->

<svg class="fig illust motion" data-fig="bloom-threshold" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bloom-threshold" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ブルームのしきい値: どこから光らせるか。硬く切ると縁が目立ち、ソフト ニーでなめらかにつなぐ</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素の HDR。明るさ 0.12(暗い面)・1.6(明るい面)・5 と 14(光源)。しきい値を 0.5 → 1.0 → 2.0 に上げる</text>
<text x="60.0" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">入力(HDR)</text>
<rect x="60.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="77.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="94.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="111.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="128.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="145.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="162.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="230.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="247.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="264.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="281.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="298.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="315.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="332.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="349.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="366.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="383.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="400.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="434.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="451.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="468.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="485.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="502.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="519.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="536.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="553.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="570.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fbf1b6"/></rect>
<rect x="587.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fbf1b6"/></rect>
<rect x="604.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fbf1b6"/></rect>
<rect x="621.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fbf1b6"/></rect>
<rect x="638.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fbf1b6"/></rect>
<rect x="655.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fbf1b6"/></rect>
<rect x="672.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="689.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="706.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="723.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="740.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="757.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="774.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="791.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="808.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="825.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="842.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="859.0" y="106.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#383d42"/></rect>
<rect x="60.0" y="106" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;1.0000" values="1;1;0;0"/><text x="60.0" y="156" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">しきい値 0.5</text>
<text x="60.0" y="186" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">② 硬く切る: max(0, 明るさ − しきい値)</text>
<rect x="60.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="77.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="94.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="111.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="128.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="145.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="162.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0938" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="230.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="247.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="264.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="281.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="298.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="315.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="332.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="349.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="366.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="383.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="400.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="434.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="451.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="468.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="485.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="502.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="519.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="536.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="553.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#0f172a;#d8d0a1"/></rect>
<rect x="587.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1258" values="#0f172a;#d8d0a1"/></rect>
<rect x="604.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#0f172a;#d8d0a1"/></rect>
<rect x="621.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#d8d0a1"/></rect>
<rect x="638.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#0f172a;#d8d0a1"/></rect>
<rect x="655.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#0f172a;#d8d0a1"/></rect>
<rect x="672.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="190" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="240" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">③ ソフト ニー(切り口をなめらかに)</text>
<rect x="60.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="77.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="94.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="111.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="128.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="145.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="162.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0938" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="230.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="247.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="264.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="281.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="298.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="315.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="332.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="349.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="366.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="383.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="400.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="434.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="451.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="468.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="485.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="502.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="519.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="536.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="553.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#0f172a;#d8d0a1"/></rect>
<rect x="587.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1258" values="#0f172a;#d8d0a1"/></rect>
<rect x="604.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#0f172a;#d8d0a1"/></rect>
<rect x="621.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#d8d0a1"/></rect>
<rect x="638.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#0f172a;#d8d0a1"/></rect>
<rect x="655.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#0f172a;#d8d0a1"/></rect>
<rect x="672.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="244" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="294" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">④ ② をぼかした、にじむ光</text>
<rect x="60.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#0f172a;#3d4245"/></rect>
<rect x="77.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0858" values="#0f172a;#61625a"/></rect>
<rect x="94.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#0f172a;#8b8973"/></rect>
<rect x="111.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#0f172a;#b5b08c"/></rect>
<rect x="128.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#0f172a;#d7cfa0"/></rect>
<rect x="145.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911" values="#0f172a;#f0e6af"/></rect>
<rect x="162.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#0f172a;#fef3b7"/></rect>
<rect x="179.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0938" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#0f172a;#fef3b7"/></rect>
<rect x="213.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0964" values="#0f172a;#f0e6af"/></rect>
<rect x="230.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#0f172a;#d7cfa0"/></rect>
<rect x="247.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0991" values="#0f172a;#b7b28e"/></rect>
<rect x="264.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#0f172a;#949179"/></rect>
<rect x="281.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1018" values="#0f172a;#7a7a6a"/></rect>
<rect x="298.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1031" values="#0f172a;#797969"/></rect>
<rect x="315.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044" values="#0f172a;#918f77"/></rect>
<rect x="332.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#0f172a;#b5b08c"/></rect>
<rect x="349.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1071" values="#0f172a;#d8d0a1"/></rect>
<rect x="366.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1084" values="#0f172a;#f2e8b0"/></rect>
<rect x="383.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1098" values="#0f172a;#fff4b8"/></rect>
<rect x="400.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1124" values="#0f172a;#fff4b8"/></rect>
<rect x="434.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1138" values="#0f172a;#f2e8b0"/></rect>
<rect x="451.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1151" values="#0f172a;#d9d1a1"/></rect>
<rect x="468.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#0f172a;#b7b18d"/></rect>
<rect x="485.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1178" values="#0f172a;#929078"/></rect>
<rect x="502.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1191" values="#0f172a;#787768"/></rect>
<rect x="519.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1204" values="#0f172a;#707063"/></rect>
<rect x="536.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1218" values="#0f172a;#797969"/></rect>
<rect x="553.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1231" values="#0f172a;#8c8a74"/></rect>
<rect x="570.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#0f172a;#9d9a7e"/></rect>
<rect x="587.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1258" values="#0f172a;#aca787"/></rect>
<rect x="604.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#0f172a;#b3ae8b"/></rect>
<rect x="621.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#b3ae8b"/></rect>
<rect x="638.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#0f172a;#aca787"/></rect>
<rect x="655.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#0f172a;#9d9a7e"/></rect>
<rect x="672.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1324" values="#0f172a;#888772"/></rect>
<rect x="689.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1338" values="#0f172a;#6f6f63"/></rect>
<rect x="706.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1351" values="#0f172a;#545753"/></rect>
<rect x="723.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1364" values="#0f172a;#3c4044"/></rect>
<rect x="740.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#0f172a;#292f39"/></rect>
<rect x="757.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1391" values="#0f172a;#1c2332"/></rect>
<rect x="774.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1404" values="#0f172a;#151c2d"/></rect>
<rect x="791.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1418" values="#0f172a;#11192b"/></rect>
<rect x="808.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1431" values="#0f172a;#10182a"/></rect>
<rect x="825.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="298" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">取り出した光の量(合計): 硬い 33.6 / ソフト 33.6 / ぼかした後 33.5</text>
<text x="60.0" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">暗い面(0.12)は光らない。1.6 の面は、光る側に入る → 画面全体がにじむ</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;0.5820;0.5822;1.0000" values="0;0;1;1;0;0"/><text x="60.0" y="156" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">しきい値 1.0</text>
<text x="60.0" y="186" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">② 硬く切る: max(0, 明るさ − しきい値)</text>
<rect x="60.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="77.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="94.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="111.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="128.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="145.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="162.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3502" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3516" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3529" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="230.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="247.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="264.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="281.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="298.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="315.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="332.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="349.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="366.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="383.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="400.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="434.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="451.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="468.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="485.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="502.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="519.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="536.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="553.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#0f172a;#9f9c7f"/></rect>
<rect x="587.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3836" values="#0f172a;#9f9c7f"/></rect>
<rect x="604.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3849" values="#0f172a;#9f9c7f"/></rect>
<rect x="621.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3862" values="#0f172a;#9f9c7f"/></rect>
<rect x="638.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3876" values="#0f172a;#9f9c7f"/></rect>
<rect x="655.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3889" values="#0f172a;#9f9c7f"/></rect>
<rect x="672.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="190" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="240" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">③ ソフト ニー(切り口をなめらかに)</text>
<rect x="60.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="77.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="94.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="111.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="128.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="145.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="162.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3502" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3516" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3529" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="230.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="247.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="264.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="281.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="298.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="315.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="332.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="349.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="366.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="383.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="400.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="434.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="451.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="468.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="485.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="502.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="519.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="536.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="553.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#0f172a;#9f9c7f"/></rect>
<rect x="587.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3836" values="#0f172a;#9f9c7f"/></rect>
<rect x="604.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3849" values="#0f172a;#9f9c7f"/></rect>
<rect x="621.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3862" values="#0f172a;#9f9c7f"/></rect>
<rect x="638.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3876" values="#0f172a;#9f9c7f"/></rect>
<rect x="655.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3889" values="#0f172a;#9f9c7f"/></rect>
<rect x="672.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="244" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="294" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">④ ② をぼかした、にじむ光</text>
<rect x="60.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3422" values="#0f172a;#393e43"/></rect>
<rect x="77.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3436" values="#0f172a;#595b56"/></rect>
<rect x="94.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3449" values="#0f172a;#81806e"/></rect>
<rect x="111.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3462" values="#0f172a;#aaa586"/></rect>
<rect x="128.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3476" values="#0f172a;#ccc59a"/></rect>
<rect x="145.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3489" values="#0f172a;#e5dca8"/></rect>
<rect x="162.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3502" values="#0f172a;#f3e9b1"/></rect>
<rect x="179.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3516" values="#0f172a;#f8edb4"/></rect>
<rect x="196.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3529" values="#0f172a;#f3e9b1"/></rect>
<rect x="213.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3542" values="#0f172a;#e5dca8"/></rect>
<rect x="230.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556" values="#0f172a;#ccc59a"/></rect>
<rect x="247.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3569" values="#0f172a;#aca887"/></rect>
<rect x="264.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3582" values="#0f172a;#8a8973"/></rect>
<rect x="281.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3596" values="#0f172a;#737365"/></rect>
<rect x="298.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3609" values="#0f172a;#747466"/></rect>
<rect x="315.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622" values="#0f172a;#8d8b74"/></rect>
<rect x="332.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3636" values="#0f172a;#b1ad8a"/></rect>
<rect x="349.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3649" values="#0f172a;#d4cd9f"/></rect>
<rect x="366.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3662" values="#0f172a;#eee4ae"/></rect>
<rect x="383.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3676" values="#0f172a;#fdf3b7"/></rect>
<rect x="400.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3702" values="#0f172a;#fdf3b7"/></rect>
<rect x="434.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3716" values="#0f172a;#eee5ae"/></rect>
<rect x="451.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3729" values="#0f172a;#d4cd9f"/></rect>
<rect x="468.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3742" values="#0f172a;#b1ac8a"/></rect>
<rect x="485.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756" values="#0f172a;#8a8873"/></rect>
<rect x="502.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3769" values="#0f172a;#696a5f"/></rect>
<rect x="519.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3782" values="#0f172a;#585a55"/></rect>
<rect x="536.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3796" values="#0f172a;#575955"/></rect>
<rect x="553.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3809" values="#0f172a;#61625a"/></rect>
<rect x="570.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#0f172a;#6c6d61"/></rect>
<rect x="587.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3836" values="#0f172a;#787868"/></rect>
<rect x="604.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3849" values="#0f172a;#7e7d6c"/></rect>
<rect x="621.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3862" values="#0f172a;#7e7d6c"/></rect>
<rect x="638.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3876" values="#0f172a;#787868"/></rect>
<rect x="655.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3889" values="#0f172a;#6c6d61"/></rect>
<rect x="672.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3902" values="#0f172a;#5c5e58"/></rect>
<rect x="689.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3916" values="#0f172a;#4a4d4d"/></rect>
<rect x="706.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3929" values="#0f172a;#383d42"/></rect>
<rect x="723.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3942" values="#0f172a;#292f39"/></rect>
<rect x="740.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3956" values="#0f172a;#1d2433"/></rect>
<rect x="757.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3969" values="#0f172a;#161e2e"/></rect>
<rect x="774.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3982" values="#0f172a;#121a2c"/></rect>
<rect x="791.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3996" values="#0f172a;#10182b"/></rect>
<rect x="808.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="298" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">取り出した光の量(合計): 硬い 28.6 / ソフト 28.6 / ぼかした後 28.5</text>
<text x="60.0" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1.6 の面が少し光る。光源だけが、強く光る</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5820;0.5822;1.0000" values="0;0;1;1"/><text x="60.0" y="156" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">しきい値 2.0</text>
<text x="60.0" y="186" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">② 硬く切る: max(0, 明るさ − しきい値)</text>
<rect x="60.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="77.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="94.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="111.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="128.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="145.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="162.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6080" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6093" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6107" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="230.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="247.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="264.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="281.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="298.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="315.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="332.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="349.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="366.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="383.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="400.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="434.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="451.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="468.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="485.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="502.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="519.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="536.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="553.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="587.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="604.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="621.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="638.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="655.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="672.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="190.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="190" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="240" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">③ ソフト ニー(切り口をなめらかに)</text>
<rect x="60.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="77.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="94.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="111.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="128.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="145.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="162.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6080" values="#0f172a;#fff4b8"/></rect>
<rect x="179.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6093" values="#0f172a;#fff4b8"/></rect>
<rect x="196.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6107" values="#0f172a;#fff4b8"/></rect>
<rect x="213.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="230.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="247.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="264.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="281.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="298.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="315.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="332.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="349.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="366.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="383.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="400.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267" values="#0f172a;#fff4b8"/></rect>
<rect x="417.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="434.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="451.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="468.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="485.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="502.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="519.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="536.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="553.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400" values="#0f172a;#2f343d"/></rect>
<rect x="587.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6413" values="#0f172a;#2f343d"/></rect>
<rect x="604.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6427" values="#0f172a;#2f343d"/></rect>
<rect x="621.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6440" values="#0f172a;#2f343d"/></rect>
<rect x="638.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6453" values="#0f172a;#2f343d"/></rect>
<rect x="655.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6467" values="#0f172a;#2f343d"/></rect>
<rect x="672.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="244.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="244" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="294" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">④ ② をぼかした、にじむ光</text>
<rect x="60.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6000" values="#0f172a;#2f353d"/></rect>
<rect x="77.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6013" values="#0f172a;#4a4d4d"/></rect>
<rect x="94.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6027" values="#0f172a;#6c6c61"/></rect>
<rect x="111.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6040" values="#0f172a;#908e76"/></rect>
<rect x="128.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6053" values="#0f172a;#b1ac8a"/></rect>
<rect x="145.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6067" values="#0f172a;#c9c298"/></rect>
<rect x="162.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6080" values="#0f172a;#d8d0a1"/></rect>
<rect x="179.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6093" values="#0f172a;#ddd5a4"/></rect>
<rect x="196.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6107" values="#0f172a;#d8d0a1"/></rect>
<rect x="213.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6120" values="#0f172a;#c9c298"/></rect>
<rect x="230.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6133" values="#0f172a;#b1ac8a"/></rect>
<rect x="247.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6147" values="#0f172a;#939178"/></rect>
<rect x="264.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6160" values="#0f172a;#757567"/></rect>
<rect x="281.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6173" values="#0f172a;#64655c"/></rect>
<rect x="298.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6187" values="#0f172a;#696a60"/></rect>
<rect x="315.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6200" values="#0f172a;#84836f"/></rect>
<rect x="332.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6213" values="#0f172a;#a9a585"/></rect>
<rect x="349.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6227" values="#0f172a;#ccc59a"/></rect>
<rect x="366.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6240" values="#0f172a;#e7ddaa"/></rect>
<rect x="383.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6253" values="#0f172a;#f6ecb3"/></rect>
<rect x="400.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267" values="#0f172a;#fbf1b6"/></rect>
<rect x="417.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6280" values="#0f172a;#f6ecb3"/></rect>
<rect x="434.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6293" values="#0f172a;#e7ddaa"/></rect>
<rect x="451.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6307" values="#0f172a;#ccc59a"/></rect>
<rect x="468.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6320" values="#0f172a;#a7a384"/></rect>
<rect x="485.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6333" values="#0f172a;#7c7c6b"/></rect>
<rect x="502.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6347" values="#0f172a;#535652"/></rect>
<rect x="519.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6360" values="#0f172a;#343940"/></rect>
<rect x="536.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6373" values="#0f172a;#202634"/></rect>
<rect x="553.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6387" values="#0f172a;#161d2e"/></rect>
<rect x="570.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="587.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="604.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="621.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="638.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="655.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="672.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="689.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="706.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="723.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="740.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="757.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="774.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="791.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="808.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="825.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="842.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="859.0" y="298.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="60.0" y="298" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">取り出した光の量(合計): 硬い 21.0 / ソフト 21.5 / ぼかした後 20.9</text>
<text x="60.0" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">光源(5 と 14)だけが光る</text>
</g>
<text x="60.0" y="430" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">取り出した光の量:</text>
<text x="240" y="434" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0843;0.0844;1.0000" values="1;1;0;0"/></text>
<text x="240" y="434" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">34<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0843;0.0844;0.3420;0.3422;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="434" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">29<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3420;0.3422;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="434" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">21<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8176;0.8178;1.0000" values="0;0;1;1"/><rect x="480" y="410" width="450" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">しきい値を上げると、光る範囲と量が減る(34 → 29 → 21)</text>
<text x="496" y="457" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">硬く切ると、しきい値付近で、明るさが急に変わって、ちらつく</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">明るい所だけを取り出して、ぼかし、足す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">しきい値が低いほど、たくさんの光がにじむ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8398;0.8400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ソフト ニーを使うと、しきい値の前後で、なめらかにつながる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8398;0.8400;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bloom-threshold:end -->

## 明るい所だけ取り出す

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="しきい値の曲線">
<text x="20" y="26" class="fig-title">入力の明るさ → 取り出す量</text>
<line x1="80" y1="200" x2="720" y2="200" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="200" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" stroke-dasharray="6 4" points="80,200 400,200 400,120 720,50"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,200 340,200 370,198 400,190 430,170 470,140 560,100 720,50"/>
<line x1="400" y1="200" x2="400" y2="212" stroke="currentColor"/><text x="400" y="226" text-anchor="middle" style="font-size:12px">しきい値</text>
<text x="500" y="76" style="font-size:12px;fill:#e5484d">ハード：境で急に立ち上がる（ちらつく）</text>
<text x="500" y="98" style="font-size:12px;fill:#2563eb">ソフト ニー：滑らかに立ち上がる</text>
<text x="40" y="130" style="font-size:12px">出力</text>
</svg>

しきい値の方式は 2 つあります。<strong>ハード</strong>は、しきい値未満を 0、以上をそのまま通す方法で、境がくっきりして、動くと「ぱっ」と光ります。ソフト ニーは、しきい値の周りを滑らかな曲線でつなぐ方法で、自然に光り始めます。

## ハードなしきい値

```hlsl
float3 ThresholdHard(float3 color, float threshold) {
  float brightness = max(color.r, max(color.g, color.b));
  float contribution = max(brightness - threshold, 0.0) / max(brightness, 1e-4);
  return color * contribution;
}
```

コードの要点です。`brightness` は明るさの目安で、最大成分か輝度を使います。`brightness − threshold` は、しきい値を超えた分（超過分）だけを光らせます。`/ brightness` で割るのは、色の比率を保つためで、色相が変わりません。

## ソフト ニー

<strong>しきい値の周り</strong>で滑らかに立ち上げる方法です（Unity・Unreal などの標準）。

```hlsl
float3 ThresholdSoft(float3 color, float threshold, float knee) {
  float brightness = max(color.r, max(color.g, color.b));
  float soft = clamp(brightness - threshold + knee, 0.0, 2.0 * knee);
  soft = soft * soft / (4.0 * knee + 1e-4);
  float contribution = max(soft, brightness - threshold) / max(brightness, 1e-4);
  return color * contribution;
}
```

パラメータの意味です。`threshold` は光り始める明るさ（例：1.0）です。`knee` は立ち上がりの滑らかさの幅で、0〜1 の値を取り、0 ならハードになります。

`knee` を大きくすると、しきい値より少し暗い所から、じわっと光り始め、動いてもちらつきません。

## HDR だからできること

<strong>LDR（0〜1）の時代</strong>は、「0.8 以上」のような、見た目の明るさでしきい値を決めていました。HDR では、「1.0 を超えた」＝「ディスプレイで表現できる以上に明るい」という物理的な意味を持たせられます。

しきい値の基準の考え方です。LDR（0〜1）の時代は、「0.8 以上」のような見た目の明るさでしきい値を決めていました。HDR では、1.0 を超えるとディスプレイの白を超えます。露出後の値でしきい値を 1.0 にすれば、白を超えた光だけが光ります（直接見える光源や反射のハイライト）。しきい値を 0.5 にすれば、中間より明るい所も光り、柔らかい光る絵になります。

露出を掛けた後の値で比べることが大切です（露出が変わると光る範囲も変わる）。

## しきい値なし

<strong>しきい値を使わず、全画素をぼかして、少しだけ足す</strong>方式です（エネルギー保存型）。

| 長所 | 短所 |
| --- | --- |
| 「ぱっ」と出ない | 暗い所もにじむので全体が柔らかい・霞む |
| パラメータが少ない | 光る部分を細かく制御できない |
| 物理的に自然（レンズは全部の光を広げる） | 強さを小さくしないと眠くなる |

現代のゲームでは、しきい値なしに少ない強さ（0.04〜0.1 程度）で足す方式が増えています。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| ソフト ニーを使う | ちらつきを防ぐ（`knee` は 0.5 程度） |
| 色の比率を保つ | `/ brightness` で色相を保つ |
| 露出後の値で判定 | 露出を変えても見た目が一貫 |
| しきい値なし ＋ 弱く足す | 自然でパラメータが少ない（ただし眠くなる） |
| ミップの最初の段で一緒に | しきい値を最初のダウンサンプルと同時に行い、パスを減らす |
| エミッシブ・光源だけ光らせる | マスクで光らせたい物だけにする（ゲームごとの演出） |

## よくあるミス

??? failure "動くと、光がぱっと点いたり消えたりする"
    <strong>ハードなしきい値</strong>。ソフト ニーにする。

??? failure "露出を変えると、光る範囲が変わりすぎる"
    しきい値の基準を露出後の値にそろえる。

??? failure "光る色が、白っぽく変わる"
    色の比率を保つ（`/ brightness`）。

??? failure "しきい値なしにしたら、全体が霞んで眠い"
    足す強さを下げる（0.05 前後）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] しきい値 ＝ <strong>明るい所だけを取り出す</strong>。超過分を光らせる
    - [x] ハードは、ちらつく。ソフト ニーで滑らかに
    - [x] HDR なら「1.0 を超えた」を基準にできる。露出後の値で判断
    - [x] 色の比率を保つ（`/ brightness`）
    - [x] しきい値なし ＋ 弱く足すも定番

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Unity, "Post-processing: Bloom"（ソフト ニーの実装）
- Epic Games, "Unreal Engine: Bloom"

## 関連ページ

- [Bloom](index.md)
- [Downsampling and the Mip Chain](downsample.md)
- [Compositing and Intensity](composite.md)
- [Exposure](../tonemapping/exposure.md)
