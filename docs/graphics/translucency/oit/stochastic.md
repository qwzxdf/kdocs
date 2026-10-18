---
title: Stochastic Transparency
tags:
  - 描画
---

# Stochastic Transparency

**確率的透明は、アルファ値に応じて、画素をランダムに捨て、複数フレームやサンプルで平均する**ことで、**半透明を表す手法**です。**ソート不要で、深度も書けます**が、**ノイズが出るので、TAA が前提**です。このページでは、**確率的透明の仕組み**を説明します。

!!! tip "ポイント"
    - **アルファ値の確率で、画素を残す・捨てる**。
    - **ソート不要・深度も書ける**。
    - **TAA や複数サンプルで、平均してなめらかに**。
    - **ノイズが出る**。

## 確率的透明
<strong>アルファを「そのフラグメントが残る確率」</strong>と考え、**画素ごとのランダムな値と比べて、残すか捨てるか**を決めます（[アルファ テストのハッシュド アルファ](../alpha-test/index.md)と同じ発想）。**不透明として深度に書ける**ので、**ソート不要**で、<strong>TAA（時間平均）</strong>で**滑らかな半透明**に**収束**します。

確率的透明の利点は、ソート不要で深度が書けること（DOF や SSAO などと相性が良い）、正確な期待値に収束すること、実装が簡単なことです。欠点は、ノイズが出て TAA やデノイズが必須なこと、1 フレームでは粗いこと、アルファが小さいと収束が遅いことです。

原典は、Enderton らの "Stochastic Transparency"（I3D 2010）です。

**髪・葉**など、**細かく重なる**物には**有効**です。

<!-- fig:stochastic-alpha:begin -->

<svg class="fig illust motion" data-fig="stochastic-alpha" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-stochastic-alpha" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">確率的透明: アルファを、塗るサンプルの割合に置き換える</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><rect x="190" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="244" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="298" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="352" y="100" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="406" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="460" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="514" y="100" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="568" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="170" y="130" text-anchor="end" style="font-size:14px;font-weight:700;fill:#1f2937">α = 0.25</text>
<text x="640" y="130" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">2 / 8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/><rect x="190" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="244" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="298" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="352" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="406" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="460" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="514" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="568" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="170" y="215" text-anchor="end" style="font-size:14px;font-weight:700;fill:#1f2937">α = 0.50</text>
<text x="640" y="215" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">4 / 8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/><rect x="190" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="244" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="298" y="270" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="352" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="406" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="460" y="270" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="514" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="568" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<text x="170" y="300" text-anchor="end" style="font-size:14px;font-weight:700;fill:#1f2937">α = 0.75</text>
<text x="640" y="300" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">6 / 8</text>
</g>
<text x="190" y="80" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 画素の 8 個のサンプル（青 = 描く）</text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">半透明の面を、サンプルごとに 描く / 描かない で決める<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.25: 8 個のうち 2 個だけ描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.5: 4 個<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.75: 6 個。平均すると α の割合で塗られる(並べ替え不要、代わりにノイズ)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:stochastic-alpha:end -->

## よくあるミス

??? failure "ノイズが残る"
    **TAA** や **サンプル数を増やして**、**平均**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ランダムに捨てて、平均する**
    - [x] **TAA が前提**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [Hashed Alpha](../alpha-test/hashed-alpha.md)
