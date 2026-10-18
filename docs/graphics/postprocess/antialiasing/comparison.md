---
title: Comparison and Choosing
tags:
  - 描画
---

# Comparison and Choosing

**AA の方式は、どれも「何をどれだけ、どんなコストで消せるか」が違います**。**1 つで全部を解決する方式はなく**、**ゲームの描画方式・ターゲット機・見た目の好み**で**選び**、**組み合わせます**。このページでは、**方式の総合比較・消せるエイリアシングの種類・コストと副作用・描画方式との相性・目的別の選び方・組み合わせの例**を説明します。

!!! tip "ポイント"
    - <strong>ジオメトリの縁</strong>は<strong>MSAA・SMAA・TAA</strong>が<strong>効く</strong>。<strong>FXAA は粗い</strong>。
    - <strong>シェーダー内のエイリアシング・時間のちらつき</strong>は<strong>TAA 系だけ</strong>が<strong>本格的に消せる</strong>。
    - <strong>ディファード</strong>は<strong>MSAA が重い</strong>ので<strong>後処理・TAA</strong>。<strong>フォワード・VR・モバイル</strong>は<strong>MSAA が現役</strong>。
    - <strong>現代の主流</strong>は<strong>TAA ＋ アップスケール（DLSS・FSR・TSR）</strong>。
    - <strong>低スペック・簡易</strong>は<strong>FXAA・SMAA</strong>。
    - <strong>組み合わせ</strong>：<strong>MSAA ＋ 後処理</strong>、<strong>TAA ＋ シャープ化</strong>。

## 総合比較

| 方式 | ジオメトリの縁 | シェーダー内 | 時間的ちらつき | コスト | 副作用 | 必要なもの |
| --- | --- | --- | --- | --- | --- | --- |
| **SSAA** | **◎** | **◎** | **○** | **非常に重い** | **なし** | **なし** |
| **MSAA** | **◎** | **×** | **△** | <strong>中（メモリ・帯域）</strong> | **ディファードで重い** | **MSAA 対応の描画** |
| **FXAA** | **△** | **△** | **×** | **最小** | **全体が少しぼける** | **最終画像のみ** |
| **SMAA 1x** | **○** | **△** | **×** | **小** | **わずかにぼける** | **最終画像のみ** |
| **SMAA T2x** | **○** | **○** | **○** | **小〜中** | **わずかにぼける・ゴースト** | **速度バッファ** |
| **TAA** | **◎** | **◎** | **◎** | **小〜中** | **ゴースト・ぼけ** | **速度バッファ・ジッター** |
| **TAAU・DLSS・FSR** | **◎** | **◎** | **◎** | <strong>小〜中（解像度を下げるので総コストは減る）</strong> | **ゴースト・調整が必要** | **速度・深度・ジッター** |

## 消せるエイリアシングの種類

| エイリアシング | MSAA | FXAA | SMAA | TAA |
| --- | --- | --- | --- | --- |
| **三角形の縁のジャギー** | **◎** | **○** | **◎** | **◎** |
| **アルファ テストの縁** | **A2C で ○** | **○** | **○** | **◎** |
| **スペキュラのちらつき** | **×** | **△** | **△** | **◎** |
| **法線マップのちらつき** | **×** | **△** | **△** | **◎** |
| **細い線・電線** | **○** | **△** | **△** | **○** |
| **動くときのちらつき** | **△** | **×** | **×** | **◎** |

<!-- fig:aa-compare:begin -->

<svg class="fig illust motion" data-fig="aa-compare" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-aa-compare" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">アンチエイリアスの比較: 縁はなめらかに、細かい模様はぼかさずに</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">左半分は斜めの縁、右半分は 1 画素ごとの縞(細かい模様)。5 つの方法で、縁のずれと、縞の残り方を比べる</text>
<rect x="30" y="100" width="288.0" height="120.0" fill="#ffffff" stroke="#64748b" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">なし(1 回測る)</text>
<rect x="30.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="42.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="54.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="66.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="78.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="90.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="54.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="66.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="78.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="90.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="78.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="90.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="162.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="174.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="162.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="174.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="162.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="174.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<text x="30" y="238.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">1 画素あたり測る回数: 1<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></text>
<line x1="174.0" y1="100" x2="174.0" y2="220.0" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<rect x="335" y="100" width="288.0" height="120.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">FXAA(後から、ぼかす)</text>
<rect x="335.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="347.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="359.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="371.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="383.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="395.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="407.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#454545"/></rect>
<rect x="347.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="359.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="371.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="383.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="395.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="407.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#363636"/></rect>
<rect x="359.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#454545"/></rect>
<rect x="371.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="383.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="395.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="407.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#363636"/></rect>
<rect x="383.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#454545"/></rect>
<rect x="395.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="407.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="419.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#363636"/></rect>
<rect x="407.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#454545"/></rect>
<rect x="419.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="431.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="443.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#363636"/></rect>
<rect x="431.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#454545"/></rect>
<rect x="443.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="455.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#454545"/></rect>
<rect x="455.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="467.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="479.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="491.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="455.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#363636"/></rect>
<rect x="467.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#434343"/></rect>
<rect x="479.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#c0c0c0"/></rect>
<rect x="491.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="455.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="467.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#343434"/></rect>
<rect x="479.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#c0c0c0"/></rect>
<rect x="491.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="335.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="455.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="467.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#343434"/></rect>
<rect x="479.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#c0c0c0"/></rect>
<rect x="491.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#575757"/></rect>
<rect x="503.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="515.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#575757"/></rect>
<rect x="527.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="539.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#575757"/></rect>
<rect x="551.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="563.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#575757"/></rect>
<rect x="575.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="587.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#575757"/></rect>
<rect x="599.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="611.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#4b4b4b"/></rect>
<text x="335" y="238.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">1 画素あたり測る回数: 1<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></text>
<line x1="479.0" y1="100" x2="479.0" y2="220.0" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<rect x="640" y="100" width="288.0" height="120.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">MSAA 4x(縁だけ 4 回)</text>
<rect x="640.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="652.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="664.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="676.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="688.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="700.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="712.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="724.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="736.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="748.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="760.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="772.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="100.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="664.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="676.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="688.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="700.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="712.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="724.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="736.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="748.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="760.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="772.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="112.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#595959"/></rect>
<rect x="676.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="688.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="700.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="712.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="724.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="736.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="748.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="760.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="772.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="124.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="700.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="712.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="724.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="736.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="748.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="760.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="772.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="136.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="712.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="724.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="736.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="748.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="760.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="772.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="148.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="712.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="724.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="736.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="748.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="760.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="772.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="160.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="712.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="724.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="736.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="748.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="760.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="772.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="784.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="172.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="712.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="724.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="736.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="748.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="760.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="772.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="784.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="184.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="712.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="724.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="736.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="748.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="760.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="772.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="784.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="196.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="640.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="652.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="664.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="676.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="688.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="712.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="724.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="736.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="748.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="760.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="772.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="784.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="796.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="808.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="820.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="832.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="844.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="856.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="868.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="880.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="892.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="904.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="916.0" y="208.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<text x="640" y="238.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">1 画素あたり測る回数: 4<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></text>
<line x1="784.0" y1="100" x2="784.0" y2="220.0" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<rect x="30" y="262" width="288.0" height="120.0" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="252" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">TAA(8 フレーム平均)</text>
<rect x="30.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="42.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="54.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="66.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="78.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="90.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#404040"/></rect>
<rect x="42.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="54.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="66.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="78.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="90.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#404040"/></rect>
<rect x="66.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="78.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="90.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="102.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#404040"/></rect>
<rect x="90.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="102.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="114.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="114.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="126.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="138.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="150.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="138.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="150.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="162.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="162.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="174.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="162.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#404040"/></rect>
<rect x="174.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="162.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="174.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="30.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="42.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="54.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="66.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="78.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="90.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="102.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="114.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="126.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="138.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="150.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="162.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="174.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="186.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="198.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="210.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="222.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="234.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="246.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="258.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="270.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="282.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="294.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="306.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<text x="30" y="400.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">1 画素あたり測る回数: 1<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></text>
<line x1="174.0" y1="262" x2="174.0" y2="382.0" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<rect x="335" y="262" width="288.0" height="120.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="335" y="252" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">正解(1 画素を 64 回測る)</text>
<rect x="335.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#ececec"/></rect>
<rect x="347.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="359.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="371.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="383.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="395.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="407.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="262.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#3d3d3d"/></rect>
<rect x="347.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="359.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#efefef"/></rect>
<rect x="371.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="383.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="395.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="407.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="274.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#4c4c4c"/></rect>
<rect x="371.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#bcbcbc"/></rect>
<rect x="383.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="395.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="407.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="286.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#5c5c5c"/></rect>
<rect x="395.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#cccccc"/></rect>
<rect x="407.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="419.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="431.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="298.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#292929"/></rect>
<rect x="407.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#737373"/></rect>
<rect x="419.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="431.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="443.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="455.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="310.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#2d2d2d"/></rect>
<rect x="431.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#898989"/></rect>
<rect x="443.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="455.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="467.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="479.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="322.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#363636"/></rect>
<rect x="455.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="467.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#efefef"/></rect>
<rect x="479.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="334.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="455.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="467.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#434343"/></rect>
<rect x="479.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="346.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="455.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="467.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="479.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="358.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<rect x="335.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0488" values="#e5e7eb;#262626"/></rect>
<rect x="347.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0576" values="#e5e7eb;#262626"/></rect>
<rect x="359.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#262626"/></rect>
<rect x="371.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0751" values="#e5e7eb;#262626"/></rect>
<rect x="383.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0839" values="#e5e7eb;#262626"/></rect>
<rect x="395.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#262626"/></rect>
<rect x="407.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1015" values="#e5e7eb;#262626"/></rect>
<rect x="419.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#262626"/></rect>
<rect x="431.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1190" values="#e5e7eb;#262626"/></rect>
<rect x="443.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1278" values="#e5e7eb;#262626"/></rect>
<rect x="455.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#262626"/></rect>
<rect x="467.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1454" values="#e5e7eb;#262626"/></rect>
<rect x="479.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1541" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="491.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1629" values="#e5e7eb;#404040"/></rect>
<rect x="503.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1717" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="515.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1805" values="#e5e7eb;#404040"/></rect>
<rect x="527.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1893" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="539.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1980" values="#e5e7eb;#404040"/></rect>
<rect x="551.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2068" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="563.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2156" values="#e5e7eb;#404040"/></rect>
<rect x="575.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="587.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2332" values="#e5e7eb;#404040"/></rect>
<rect x="599.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2420" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="611.0" y="370.0" width="12.3" height="12.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#404040"/></rect>
<text x="335" y="400.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">1 画素あたり測る回数: 64<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></text>
<line x1="479.0" y1="262" x2="479.0" y2="382.0" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="30" y="392" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">左半分 = 斜めの縁 / 右半分 = 1 画素ごとの縞</text>
<rect x="640" y="262" width="290" height="140" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="640" y="252" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">縁のずれ(小さいほど良い)</text>
<text x="650" y="300" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">なし</text>
<rect x="700" y="286" width="0.5" height="18" fill="#64748b" opacity="0.85"><animate attributeName="width" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2985;0.3473;1.0000" values="0.5;0.5;150;150"/></rect>
<text x="856.0" y="300" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b" opacity="0">0.021<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3471;0.3473;1.0000" values="0;0;1;1"/></text>
<text x="650" y="328" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">FXAA</text>
<rect x="700" y="314" width="0.5" height="18" fill="#e5484d" opacity="0.85"><animate attributeName="width" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2985;0.3473;1.0000" values="0.5;0.5;116.31;116.31"/></rect>
<text x="822.3054187192118" y="328" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d" opacity="0">0.016<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3471;0.3473;1.0000" values="0;0;1;1"/></text>
<text x="650" y="356" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">MSAA</text>
<rect x="700" y="342" width="0.5" height="18" fill="#2563eb" opacity="0.85"><animate attributeName="width" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2985;0.3473;1.0000" values="0.5;0.5;73.15;73.15"/></rect>
<text x="779.1527093596059" y="356" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb" opacity="0">0.010<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3471;0.3473;1.0000" values="0;0;1;1"/></text>
<text x="650" y="384" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">TAA</text>
<rect x="700" y="370" width="0.5" height="18" fill="#7c3aed" opacity="0.85"><animate attributeName="width" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2985;0.3473;1.0000" values="0.5;0.5;43.6;43.6"/></rect>
<text x="749.5960591133005" y="384" text-anchor="start" style="font-size:11px;font-weight:700;fill:#7c3aed" opacity="0">0.006<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3471;0.3473;1.0000" values="0;0;1;1"/></text>
<rect x="30" y="420" width="900" height="96" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="410" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">細かい模様(縞)の、くっきり度(「なし」を 100% とする)</text>
<text x="50" y="462" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">なし</text>
<text x="110" y="466" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043" opacity="0">100%<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="50" y="490" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">そのまま<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="270" y="462" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">FXAA</text>
<text x="330" y="466" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">71%<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="270" y="490" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">縞がつぶれる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="490" y="462" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">MSAA</text>
<text x="550" y="466" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043" opacity="0">100%<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="490" y="490" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">模様は 1 回測る<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="710" y="462" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">TAA</text>
<text x="770" y="466" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043" opacity="0">100%<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="710" y="490" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">ぶれなければ残る<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3717;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ絵を、5 通りの方法で処理する<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">左から右へ、画面をなぞる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.2593;0.2595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">FXAA は縁を直すが、模様もぼかす。MSAA は縁だけ直す。TAA は縁も模様も、フレームを重ねて直す<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:aa-compare:end -->

## 描画方式との相性

| 描画方式 | 向く AA | 理由 |
| --- | --- | --- |
| **フォワード** | **MSAA・TAA** | **MSAA が素直に使える** |
| **ディファード** | **TAA・SMAA・FXAA** | **G バッファの MSAA は重い** |
| **ビジビリティ バッファ** | <strong>TAA・MSAA（比較的軽い）</strong> | **ID だけ MSAA** |
| **VR** | **MSAA ＋ 軽い後処理** | **TAA のぼけ・遅延が苦手**（**左右の目でずれる**） |
| <strong>モバイル（タイルベース）</strong> | **MSAA** | **タイル内で解決、ほぼ無料** |

## 目的別の選び方

| 目的 | おすすめ |
| --- | --- |
| **とにかく簡単に・最小コスト** | **FXAA** |
| **簡単で、FXAA より綺麗に** | **SMAA 1x** |
| **現代的でちらつきも消したい** | <strong>TAA（＋シャープ化）</strong> |
| **解像度を下げて、軽くしたい** | **TAAU・DLSS・FSR** |
| **VR・フォワード** | **MSAA ＋ 軽い後処理** |
| **モバイル** | **MSAA 4x** |
| <strong>最高品質（オフライン・スクリーンショット）</strong> | **SSAA ＋ TAA** |

## 組み合わせの例

| 組み合わせ | 内容 |
| --- | --- |
| **MSAA ＋ FXAA/SMAA** | **縁は MSAA、残りの粗さを後処理** |
| **TAA ＋ シャープ化** | **ぼけを戻す**（**CAS など**） |
| **TAA ＋ 低解像度レンダリング** | **TAAU・DLSS・FSR**（**総コストが下がる**） |
| **TAA が使えない物だけ別 AA** | **半透明・UI は、TAA の後に別途**（MSAA/FXAA） |

## 選ぶときの考え方

| 問い | 判断 |
| --- | --- |
| **描画はフォワードか、ディファードか** | **ディファードなら、MSAA は避ける** |
| **速度バッファを作れるか** | **作れれば TAA が使える** |
| **ちらつきが気になるか** | **気になるなら TAA 系** |
| **ぼけが許せるか** | **許せなければ MSAA・SMAA・シャープ化付き TAA** |
| **ターゲット機の性能** | **低ければ FXAA** |
| **VR か** | **TAA は避けるか、慎重に** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **設定で選べるように** | **FXAA / SMAA / TAA / TAAU を、ユーザーが切り替え** |
| **TAA を基本にして、補助を併用** | **現代の標準的な構成** |
| **UI は AA の外で描く** | **文字がぼけない** |
| **アップスケールで総コストを下げる** | **AA とアップスケールを同時に** |
| **画質の評価を動画で行う** | **静止画では分からない、ちらつき・ゴースト** |

## よくあるミス

??? failure "ディファードで MSAA を使い、重くなりすぎる"
    **TAA・SMAA に切り替える**。

??? failure "TAA だけに頼って、VR で酔う・ぼける"
    **VR は MSAA を基本**にする。

??? failure "FXAA だけで、動くちらつきが残る"
    **時間方向の AA（TAA）が必要**。

??? failure "静止画でだけ AA を評価して、動いたときに失敗"
    **動画で確認する**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>縁のジャギー</strong>は多くの方式が効く。<strong>シェーダー内・ちらつきは TAA 系のみ</strong>
    - [x] <strong>ディファードは MSAA が重い</strong>。<strong>VR・モバイルは MSAA が現役</strong>
    - [x] <strong>現代の主流は TAA ＋ アップスケール</strong>
    - [x] <strong>簡易は FXAA・SMAA</strong>
    - [x] <strong>組み合わせて</strong>使い、<strong>動画で評価</strong>する

## 参考

- Jimenez et al., "Filtering Approaches for Real-Time Anti-Aliasing"（SIGGRAPH 2011 Course）
- Yang et al., "A Survey of Temporal Antialiasing Techniques"（Eurographics 2020）
- Pettineo, "Anti-Aliasing Comparison"（The Danger Zone）

## 関連ページ

- [Anti-Aliasing](index.md)
- [MSAA](msaa.md)
- [FXAA](fxaa.md)
- [SMAA](smaa.md)
- [TAA](taa.md)
- [フォワードとディファード](../../../rendering/forward-deferred.md)
