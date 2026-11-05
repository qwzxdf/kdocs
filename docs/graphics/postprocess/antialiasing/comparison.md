---
title: Comparison and Choosing
tags:
  - 描画
---

# Comparison and Choosing

アンチエイリアスは「どれを入れればいいか」で必ず迷います。MSAA は縁がきれいですが、遅延シェーディングでは重くなります。FXAA は一番軽いのに細い線が消えたりぼけたりします。TAA は動いても静かですが、ゴーストと戦うことになります。このページでは論文の数字を拠り所にして、方式ごとに「何を消せて何を消せないか」「何バイトと何ミリ秒かかるか」を並べます。最後に、自分のゲームに合わせた選び方を HLSL と C++ の完成形つきで説明します。

!!! tip "ポイント"
    - ジオメトリの縁には MSAA・SMAA・TAA が効く。シェーダーの中のちらつきと時間方向の揺れは、実質 TAA の領域である。
    - 後処理（FXAA・SMAA 1x）は、1 枚の絵しか見ないので情報が足りない所は直せない。
    - TAA は履歴を持つ。履歴が合っているかの検証（棄却と補正）が品質のすべてを決める。
    - コストの桁は後処理が約 1 ms、TAA が 1080p で 0.2 ms 前後、MSAA 8x が 5 ms 前後（いずれも論文の測定で、GPU がそれぞれ違う）。
    - 組み合わせるなら「MSAA か SMAA で空間の縁、TAA で時間」が定番の形である。

!!! info "このページを読む前に"
    - [Anti-Aliasing](index.md)（このセクション全体の地図と読む順番）
    - [MSAA](msaa.md)・[FXAA](fxaa.md)・[SMAA](smaa.md)・[TAA](taa.md)（各方式の仕組み）

## 読んだ資料 {#sources}

このページの数字と手順は次の 2 本の論文を全文読んで書いています。

- Jimenez, Echevarria, Sousa, Gutierrez, "SMAA: Enhanced Subpixel Morphological Antialiasing", Computer Graphics Forum (Eurographics 2012) 31(2)。補足資料の本文も読みましたが、補足の動画と図、性能の比較表は読めていません。
- Yang, Liu, Salvi, "A Survey of Temporal Antialiasing Techniques", Computer Graphics Forum (Eurographics 2020) 39(2)。本文 12 ページと参考文献を読みました。

FXAA と MSAA の原典（Lottes の白書、Akeley の RealityEngine）は読んでいません。この 2 本の中でそれらが述べられている範囲だけを書きます。両方の論文に載っていない一般的な実装の知識は、そう分かるように書き分けます。

## 全体の見取り図 {#overview}

AA の方式はフレームのどこで効くかで、性質がほぼ決まります。

<svg class="fig flow" viewBox="0 0 740 184" role="img" aria-label="1 フレームの中で各アンチエイリアスが効く場所"><defs><marker id="aa-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">1 フレームの中で、各方式が効く場所</text><rect x="10" y="40" width="110" height="56" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="65.0" y="58.0" text-anchor="middle" font-size="11" fill="currentColor">ラスタライズ</text><text x="65.0" y="72.0" text-anchor="middle" font-size="11" fill="currentColor">(MSAA: サンプルを</text><text x="65.0" y="86.0" text-anchor="middle" font-size="11" fill="currentColor">複数取る)</text><rect x="130" y="40" width="110" height="56" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="185.0" y="65.0" text-anchor="middle" font-size="11" fill="currentColor">ライティング</text><text x="185.0" y="79.0" text-anchor="middle" font-size="11" fill="currentColor">(線形 HDR)</text><rect x="250" y="40" width="110" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="305.0" y="65.0" text-anchor="middle" font-size="11" fill="currentColor">TAA</text><text x="305.0" y="79.0" text-anchor="middle" font-size="11" fill="currentColor">(履歴と混ぜる)</text><rect x="370" y="40" width="110" height="56" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="425.0" y="65.0" text-anchor="middle" font-size="11" fill="currentColor">ブルームなど</text><text x="425.0" y="79.0" text-anchor="middle" font-size="11" fill="currentColor">後処理</text><rect x="490" y="40" width="110" height="56" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="545.0" y="65.0" text-anchor="middle" font-size="11" fill="currentColor">トーンマップ</text><text x="545.0" y="79.0" text-anchor="middle" font-size="11" fill="currentColor">(LDR)</text><rect x="610" y="40" width="110" height="56" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="665.0" y="65.0" text-anchor="middle" font-size="11" fill="currentColor">FXAA / SMAA 1x</text><text x="665.0" y="79.0" text-anchor="middle" font-size="11" fill="currentColor">(1 枚の絵だけ)</text><line x1="120" y1="68" x2="130" y2="68" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#aa-a)"/><line x1="240" y1="68" x2="250" y2="68" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#aa-a)"/><line x1="360" y1="68" x2="370" y2="68" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#aa-a)"/><line x1="480" y1="68" x2="490" y2="68" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#aa-a)"/><line x1="600" y1="68" x2="610" y2="68" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#aa-a)"/><path d="M305,96 L305,128 L305,128" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="235" y="128" width="140" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="305.0" y="145.0" text-anchor="middle" font-size="11" fill="currentColor">履歴(前フレームの出力)</text><text x="305.0" y="159.0" text-anchor="middle" font-size="11" fill="currentColor">+ 動きベクトル</text><path d="M375,148 C 430,148 430,68 365,68" fill="none" stroke="#4c8bf5" stroke-width="1.2" stroke-dasharray="4 3"/><text x="10" y="130" text-anchor="start" font-size="10" fill="currentColor">黄: 1 画素の中を細かく見る / 絵だけで直す</text><text x="10" y="146" text-anchor="start" font-size="10" fill="currentColor">青: 前のフレームのサンプルを足す</text></svg>

MSAA はラスタライズの段階でカバレッジを複数のサンプルで取ります。シェーディングは画素に 1 回で、深度と色のストレージだけがサンプル数に比例して増えます。SMAA の論文は MSAA が本質的に「サンプル数を増やすとスケールしにくい」と書き、遅延シェーディングに入れるのが簡単でないことを動機の 1 つにしています。

FXAA と SMAA 1x は完成した 1 枚の絵に境界を探してぼかすフィルターをかけます。入力が 1 サンプル/画素の絵だけなので、画素の中にあったはずの細部は復元できません。SMAA の論文は細い線の途切れや点の消えを「サブピクセル特徴」と呼び 1x の入力ではどれも正しく復元できないと述べます。

TAA は前のフレームの出力（履歴）を動きベクトルで今のフレームに合わせて、ジッターで少しずつずらしたサンプルと混ぜます。サーベイはこれを「時間方向に償却したスーパーサンプリング」と定義しています。画面に出る前の線形 HDR の段階に置くのは、エイリアスが残ったまま明るい点がブルームなどで増幅されるのを避けるためです。

## 消せるものと消せないもの {#coverage}

エイリアシングには種類があります。三角形の縁、アルファ テストの縁、スペキュラのちらつき細い線、動いたときのちらつきです。どの方式がどれに効くかを論文の記述から整理します。

| エイリアシング | MSAA | FXAA | SMAA 1x | TAA |
| --- | --- | --- | --- | --- |
| 三角形の縁 | ○ | △ | ○ | ○ |
| アルファ テストの縁 | A2C で ○ | △ | △ | ○ |
| スペキュラ・法線の細かい模様 | × | △ | △ | ○ |
| 細い線・サブピクセルの点 | △ | × | × | ○ |
| 動いたときのちらつき | △ | × | × | ○ |

この表は論文の記述と一般的な知識からの私の整理です。FXAA の列は SMAA の論文が「サブピクセルの特徴を弱める形で扱う」と書いていることと、品質が MSAA に届かないと書いていることに基づきます。MSAA のスペキュラへの弱さは MSAA がシェーディングを画素に 1 回しか行わない（SMAA 論文・サーベイの説明）ことから導いたものです。

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
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ絵を 5 通りの方法で処理する<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">左から右へ画面をなぞる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.2593;0.2595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">FXAA は縁を直すが、模様もぼかす。MSAA は縁だけ直す。TAA は縁も模様も、フレームを重ねて直す<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:aa-compare:end -->

### 後処理にできないこと {#postprocess-limit}

SMAA 論文の図 10 は黒い背景に白い格子を遠くから見た例です。距離が長くなると格子の線が 1 画素より細くなり 1 サンプル/画素の絵では線の連続性が切れます。1x の SMAA でも MLAA でも直りません。サンプルを足した S2x（空間 2 サンプル）や 4x では、MSAA 4x の参照に近づきます。

論文はもう 1 つ MSAA の各サンプルに別々に MLAA（または FXAA）をかけて平均する素朴な組み合わせを試しています。結果はぼけて光る縁取りが出ます。理由は 2 つ書かれています。MLAA は物体のシルエットを前提にしていて細い線に弱いことと各サンプルが画素の中心にあるという前提で面積を計算するため、サンプルの位置がずれるとグラデーションが合わなくなることです。SMAA はこの 2 点を鋭い角の検出とサンプル位置ごとの面積テクスチャで直しています。

つまり、「MSAA の上にFXAAをかければ両方の良いところ取り」とはなりません。位置の補正をしない後処理は MSAA の解像結果と整合しません。

## 方式ごとの要点 {#methods}

### MSAA {#msaa}

MSAA はカバレッジの判定をサンプルごとにシェーディングを画素に 1 回だけ行います。SMAA 論文は GTX 470 の 1080p で、8x が平均 5.4 ms（帯域が重いゲームでは 7.7 ms）かかると書きます。メモリは前方で最大 126 MB、遅延で 316 MB に達します。

自分で計算すると 1920×1080 で前方の HDR 色（RGBA16F の 8 バイト）と深度（4 バイト）なら 1 サンプル 12 バイトで、8x は 189.8 MiB です。遅延の G バッファを RGBA8 を 4 枚と深度で 20 バイトとすれば、8x は 316.4 MiB になります。論文の 316 MB に近い値です。この計算は下の C++ で出しています。

サーベイは遅延シェーディングでは MSAA のカバレッジとシェーディングの対応が失われて、実質的にコストの高いスーパーサンプリングになると書きます。対応を取り戻す方法があっても、マルチサンプルの G バッファの容量と帯域が、シェーダーを回す回数が減る利得を打ち消すことが多いとも述べています。一方で、サーベイは「低性能なプラットフォーム（特にタイル型のモバイル GPU）では MSAA のほうが TAA より安いことがある」とも書いています。前方レンダリングの選択肢として残る理由です。

### FXAA {#fxaa}

FXAA は完成した絵だけを入力にします。SMAA 論文の評価ではプリセット 39（最高品質）を比べています。論文の言い方ではサブピクセルの特徴を「単に弱める」ので、時間的な安定は増しますが画質は MSAA の水準に届きません。SMAA の論文は SMAA 1x と T2x の実行時間は他の手法と同じ 1 ms 前後の範囲にあると書いています（比較の表は補足資料の表 1 で、その中身は読めていません）。

SMAA 論文は FXAA のような「現在の画素と 4 近傍の輝度の範囲を見る」やり方では、辺どうしの知覚的なマスキングを扱えない、と書いています。

### SMAA {#smaa}

SMAA は MLAA の流れで、辺の検出、パターンの分類、面積に応じた近傍とのブレンドの 3 パスです。論文が MLAA に足した改善は 5 点あります。局所コントラストによる辺検出、鋭い角の保存（丸め係数 r）、斜めのパターン、距離探索での交差辺の確認、サブピクセルの扱い（S2x・T2x・4x）です。

GTX 470 の 1080p での測定は次のとおりです。1x が 1.02 ms、T2x が 1.32 ms、S2x が 2.04 ms、4x が 2.34 ms です。個別の部品は局所コントラストが 0.08 ms、斜めの処理が 0.12 ms、時間方向の処理が 0.3 ms、鋭い角と正確な探索が 0.01 ms 未満です。S2x・4x が高いのは空間の 2 サンプルを描くコストが、平均 1.57 ms 乗るためです。前方レンダリングでは MSAA 8x に比べて、SMAA 4x が約 1.46 倍、T2x が約 4.09 倍速いと論文は書いています。メモリは最も重い構成でも MSAA 8x の前方で 43 %、遅延で 17 % です。

T2x は MSAA を使わず時間方向でサブピクセルを取ります。履歴を混ぜる重みは速度の差で決めます。

### TAA {#taa}

TAA の中身は 3 つの部品に分かれます。ジッターを入れて描くこと動きベクトルで履歴を再投影することと履歴を検証して混ぜることです。サーベイは UE4 が Halton(2, 3) の 8 サンプル、INSIDE が同じ列の 16 サンプル、SMAA T2x が Quincunx、Quantum Break が回転グリッドを使うと書いています。

履歴を混ぜるときの式は論文の式 2 です。新しい色の重みを α として、`出力 = α × 今 + (1 − α) × 履歴` です。α が小さいほど溜まるサンプルは多いのですが、古い情報が残りやすくなります。固定 α のとき均等な重みに換算した「等価サンプル数」は、サーベイの図 4 にあります。α = 0.1 では 5 フレームで 2.2、10 フレームで 5.1、15 フレームで 9.8、定常で 19 です。下の C++ はこの値を自分で計算して再現します。

<svg class="fig flow" viewBox="0 0 700 240" role="img" aria-label="固定 α の等価サンプル数の増え方"><defs><marker id="aa-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">固定 α の指数平滑で、n フレーム溜めたときの等価サンプル数</text><line x1="50" y1="200" x2="570" y2="200" stroke="#94a3b8"/><line x1="50" y1="30" x2="50" y2="200" stroke="#94a3b8"/><line x1="50" y1="157.5" x2="570" y2="157.5" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="44" y="161.5" text-anchor="end" font-size="10" fill="currentColor">10</text><line x1="50" y1="115.0" x2="570" y2="115.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="44" y="119.0" text-anchor="end" font-size="10" fill="currentColor">20</text><line x1="50" y1="72.5" x2="570" y2="72.5" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="44" y="76.5" text-anchor="end" font-size="10" fill="currentColor">30</text><line x1="50" y1="30.0" x2="570" y2="30.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="44" y="34.0" text-anchor="end" font-size="10" fill="currentColor">40</text><text x="50.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="121.72413793103448" y="216" text-anchor="middle" font-size="10" fill="currentColor">5</text><text x="211.3793103448276" y="216" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="301.0344827586207" y="216" text-anchor="middle" font-size="10" fill="currentColor">15</text><text x="390.6896551724138" y="216" text-anchor="middle" font-size="10" fill="currentColor">20</text><text x="480.3448275862069" y="216" text-anchor="middle" font-size="10" fill="currentColor">25</text><text x="570.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="310.0" y="232" text-anchor="middle" font-size="10" fill="currentColor">溜めたフレーム数 n</text><polyline points="50.0,195.8 67.9,195.3 85.9,194.8 103.8,194.3 121.7,193.7 139.7,193.0 157.6,192.3 175.5,191.5 193.4,190.6 211.4,189.7 229.3,188.7 247.2,187.5 265.2,186.3 283.1,185.0 301.0,183.5 319.0,181.9 336.9,180.2 354.8,178.3 372.8,176.3 390.7,174.1 408.6,171.8 426.6,169.3 444.5,166.7 462.4,163.9 480.3,160.9 498.3,157.8 516.2,154.4 534.1,151.0 552.1,147.4 570.0,143.6" fill="none" stroke="#94a3b8" stroke-width="2.5"/><line x1="570" y1="34.25" x2="580" y2="34.25" stroke="#94a3b8" stroke-width="2"/><text x="584" y="38.25" text-anchor="start" font-size="10" fill="currentColor">α=0.05: 39</text><polyline points="50.0,195.8 67.9,194.8 85.9,193.7 103.8,192.4 121.7,190.8 139.7,188.9 157.6,186.7 175.5,184.2 193.4,181.4 211.4,178.2 229.3,174.7 247.2,170.9 265.2,166.8 283.1,162.7 301.0,158.4 319.0,154.2 336.9,150.1 354.8,146.2 372.8,142.5 390.7,139.2 408.6,136.2 426.6,133.6 444.5,131.3 462.4,129.3 480.3,127.5 498.3,126.1 516.2,124.9 534.1,123.9 552.1,123.0 570.0,122.4" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><line x1="570" y1="119.25000000000001" x2="580" y2="119.25000000000001" stroke="#4c8bf5" stroke-width="2"/><text x="584" y="123.25000000000001" text-anchor="start" font-size="10" fill="currentColor">α=0.1: 19</text><polyline points="50.0,195.8 67.9,193.8 85.9,191.1 103.8,187.6 121.7,183.7 139.7,179.4 157.6,175.3 175.5,171.7 193.4,168.8 211.4,166.6 229.3,165.0 247.2,163.9 265.2,163.1 283.1,162.7 301.0,162.3 319.0,162.1 336.9,162.0 354.8,161.9 372.8,161.8 390.7,161.8 408.6,161.8 426.6,161.8 444.5,161.8 462.4,161.8 480.3,161.8 498.3,161.8 516.2,161.8 534.1,161.8 552.1,161.8 570.0,161.8" fill="none" stroke="#e5aa28" stroke-width="2.5"/><line x1="570" y1="161.75" x2="580" y2="161.75" stroke="#e5aa28" stroke-width="2"/><text x="584" y="165.75" text-anchor="start" font-size="10" fill="currentColor">α=0.2: 9</text><circle cx="121.72413793103448" cy="190.65" r="3.5" fill="#4c8bf5"/><text x="127.72413793103448" y="184.65" text-anchor="start" font-size="10" fill="currentColor">2.2</text><circle cx="211.3793103448276" cy="178.325" r="3.5" fill="#4c8bf5"/><text x="217.3793103448276" y="172.325" text-anchor="start" font-size="10" fill="currentColor">5.1</text><circle cx="301.0344827586207" cy="158.35" r="3.5" fill="#4c8bf5"/><text x="307.0344827586207" y="152.35" text-anchor="start" font-size="10" fill="currentColor">9.8</text><text x="70" y="44" text-anchor="start" font-size="10" fill="currentColor">青の丸: サーベイの図 4 の値(α = 0.1)</text></svg>

履歴のぼけと棄却の精度が TAA の画質を左右します。サーベイはぼけの原因を 2 つ挙げます。履歴をバイリニアで再サンプルするときのぼけと履歴の補正（クリップ）で細い線が消えるぼけです。前者には Catmull-Rom などの再サンプルが効き後者は、クリップ範囲の推定が細い特徴を取りこぼす場合に起きます。

## コストを並べる {#cost}

いくつかのコストを並べますが、測定条件がそろっていない点に注意が必要です。SMAA の数字は GTX 470 の 1080p で、TAA の数字は RTX 2080 Ti の UE4 です。GPU の世代がちがうので ms の大小を直接比べることはできません。桁をつかむ目安にとどめてください。

<svg class="fig flow" viewBox="0 0 760 256" role="img" aria-label="SMAA・MSAA と TAA のコスト"><defs><marker id="aa-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">論文の測定値(GPU がちがうので、左右の ms は比べない)</text><text x="10" y="38" text-anchor="start" font-size="11" fill="currentColor">GTX 470, 1080p (SMAA 論文)</text><rect x="20" y="190.875" width="44" height="19.125" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="42" y="184.875" text-anchor="middle" font-size="10" fill="currentColor">1.02</text><text x="42" y="226" text-anchor="middle" font-size="10" fill="currentColor">SMAA 1x</text><rect x="82" y="185.25" width="44" height="24.75" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="104" y="179.25" text-anchor="middle" font-size="10" fill="currentColor">1.32</text><text x="104" y="226" text-anchor="middle" font-size="10" fill="currentColor">T2x</text><rect x="144" y="171.75" width="44" height="38.25" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="166" y="165.75" text-anchor="middle" font-size="10" fill="currentColor">2.04</text><text x="166" y="226" text-anchor="middle" font-size="10" fill="currentColor">S2x</text><rect x="206" y="166.125" width="44" height="43.875" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="228" y="160.125" text-anchor="middle" font-size="10" fill="currentColor">2.34</text><text x="228" y="226" text-anchor="middle" font-size="10" fill="currentColor">4x</text><rect x="268" y="108.75" width="44" height="101.25" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="290" y="102.75" text-anchor="middle" font-size="10" fill="currentColor">5.4</text><text x="290" y="226" text-anchor="middle" font-size="10" fill="currentColor">MSAA 8x</text><text x="290" y="238" text-anchor="middle" font-size="10" fill="currentColor">(平均)</text><rect x="330" y="65.625" width="44" height="144.375" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="352" y="59.625" text-anchor="middle" font-size="10" fill="currentColor">7.7</text><text x="352" y="226" text-anchor="middle" font-size="10" fill="currentColor">MSAA 8x</text><text x="352" y="238" text-anchor="middle" font-size="10" fill="currentColor">(重いとき)</text><line x1="14" y1="210" x2="396" y2="210" stroke="#94a3b8"/><text x="430" y="38" text-anchor="start" font-size="11" fill="currentColor">RTX 2080 Ti, UE4 (サーベイ表 1)</text><rect x="440" y="175.0" width="30" height="35.00000000000001" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="455" y="169.0" text-anchor="middle" font-size="10" fill="currentColor">0.14</text><text x="455" y="226" text-anchor="middle" font-size="9" fill="currentColor">TAA</text><rect x="474" y="172.5" width="30" height="37.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="489" y="166.5" text-anchor="middle" font-size="10" fill="currentColor">0.15</text><text x="489" y="226" text-anchor="middle" font-size="9" fill="currentColor">TAAU</text><text x="472" y="242" text-anchor="middle" font-size="10" fill="currentColor">1080p</text><rect x="540" y="150.0" width="30" height="60.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="555" y="144.0" text-anchor="middle" font-size="10" fill="currentColor">0.24</text><text x="555" y="226" text-anchor="middle" font-size="9" fill="currentColor">TAA</text><rect x="574" y="150.0" width="30" height="60.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="589" y="144.0" text-anchor="middle" font-size="10" fill="currentColor">0.24</text><text x="589" y="226" text-anchor="middle" font-size="9" fill="currentColor">TAAU</text><text x="572" y="242" text-anchor="middle" font-size="10" fill="currentColor">1440p</text><rect x="640" y="80.0" width="30" height="130.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="655" y="74.0" text-anchor="middle" font-size="10" fill="currentColor">0.52</text><text x="655" y="226" text-anchor="middle" font-size="9" fill="currentColor">TAA</text><rect x="674" y="85.0" width="30" height="125.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="689" y="79.0" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><text x="689" y="226" text-anchor="middle" font-size="9" fill="currentColor">TAAU</text><text x="672" y="242" text-anchor="middle" font-size="10" fill="currentColor">2160p</text><line x1="430" y1="210" x2="745" y2="210" stroke="#94a3b8"/></svg>

TAA の UE4 での測定は 1080p で 0.14 ms、1440p で 0.24 ms、2160p で 0.52 ms です。TAAU（2 倍アップサンプル）では 0.15 / 0.24 / 0.50 ms で、ほぼ同じです。サーベイは TAA の費用は出力解像度にだけ比例し、シーンの複雑さに依存しないので、安定していると述べます。MSAA はジオメトリの密度や深度の複雑さハードウェアの実装で変わります。

アップサンプルでは別のコストが出ます。サーベイは時間方向のアップサンプルが、後処理より前に置かれることがありその結果、後処理の費用がアップサンプル後の解像度で決まる場合があると述べます。

メモリ転送は TAA の 1 パスを 1080p で見積もると、読みが現在色 8、履歴 8、速度 4、深度 4 の 24 バイトで、書きが 8 バイトです。1 フレーム 63.3 MiB で、60 fps なら約 3.7 GiB/s です。近傍の 3×3 の再読み込みはキャッシュに載ると仮定した私の見積もりです。

## 選び方 {#choosing}

選ぶ順番はレンダリング方式、速度バッファの有無、ゴーストの許容、ターゲットの性能の順に決めると迷いにくくなります。

最初にレンダリング方式を見ます。遅延シェーディングなら MSAA は容量と帯域の面でほぼ候補から外れます。前方でサンプル数が小さくてよいなら MSAA が最も単純で安定します。次に、動きベクトルを出せるかを見ます。出せるなら TAA を使えゲーム全体の時間的なちらつきを同時に消せます。出せない構成（たとえば動きベクトルを書けない古いエンジン）では、SMAA 1x か FXAA が残ります。

TAA を入れるならゴーストの許容を決めます。半透明やパーティクルは動きベクトルが正しくなく、サーベイは「透明、パーティクル、反射」が TAA の苦手な例だと書いています。UE4 は半透明のマテリアルに「応答の速い AA」のフラグを立てて、そこだけ α を上げる方法を使うと書かれています。

最後に、ターゲットの性能を見ます。低スペックで 1 ms も惜しいなら FXAA か SMAA 1x です。モバイルのタイル型の GPU ならサーベイの記述では MSAA が有利になることがあります。

サーベイの結論は TAA が現状の主流で、アップサンプルと組み合わせる方向に進んでいるが、履歴の検証の信頼性にはまだ改善の余地がある、というものです。

## 組み合わせの例 {#combos}

### MSAA + 後処理 {#msaa-post}

MSAA で縁を処理し残りの粗い所を後処理で補う構成です。ただし、先に述べたとおりサンプルごとに位置を補正せずに MLAA/FXAA を重ねると、ぼけが出ます。SMAA 論文の S2x が、この組み合わせを位置補正つきで行う方法です。

### TAA + 空間の AA {#taa-spatial}

サーベイは TAA の履歴が少ない領域（カメラのカット直後、遮蔽が解けた所）ではエイリアスが目立つので、現在のフレームに SMAA のような空間の AA をかける実装があると書いています。CryEngine 3 の SMAA T2x、Decima などが例に挙がっています。

### TAA + シャープ化 {#taa-sharpen}

TAA の出力にはわずかなぼけが残ります。サーベイは離散ラプラシアンなどのシャープ化フィルターを TAA の後ろにかける実装（Hybrid Reconstruction AA、Uncharted 4 など）があると書き色域をはみ出さない適応型のシャープ化も紹介しています。

### TAA + アップサンプル {#taa-upsample}

入力を 1 画素より疎にして、時間方向でアップサンプルします。サーベイの枠組みでは出力画素ごとに「新しいサンプルの信頼度 β」を掛けて混ぜます。2 倍アップサンプルでは 4 画素のうち 1 画素だけが各フレームで更新されます。

## 実装してみる {#code}

TAA を構成する HLSL を順に見ます。SMAA 1x の辺の検出、TAA の解像、SMAA T2x の時間方向のまとめです。どれも論文の式と記述からの私の書き下ろしで、論文のコードそのものではありません。`fxc`（ps_5_0）でコンパイルして確かめました。実行して絵は確かめていません。

### SMAA の辺検出（局所コントラスト適応）{#edge}

SMAA の辺検出は輝度の差を調べて、周りの辺の強さと比べるのが特徴です。論文は人間の視覚が強い辺の近くにある弱い辺を見ない（マスキング）ことを利用して、見えない辺を消すと書きます。

```hlsl
Texture2D<float4> g_color : register(t0);   // 最終に近い色（トーンマップ後の LDR を推奨）
SamplerState g_point_clamp : register(s0);

cbuffer EdgeCB : register(b0) {
  float2 g_inv_size;     // 1 / (幅, 高さ)
  float g_threshold;     // 辺と見なす輝度差（一例: 0.1。論文は 0.05〜0.2 が普通と書く）
  float g_local_ratio;   // 局所コントラストの比（論文は 0.5）
};

// 輝度（Rec.709 の係数）。
float Luma(float3 rgb) {
  return dot(rgb, float3(0.2126, 0.7152, 0.0722));
}

// 画素 (x, y) の輝度を整数座標で読む。画面外は端にクランプされる。
float L(int2 p) {
  return Luma(g_color.Load(int3(p, 0)).rgb);
}

// 出力: x = 左の辺、y = 上の辺。1 なら辺がある。
// 辺は各画素の「左」と「上」だけを持つ。右と下は隣の画素の辺として取れる。
```

`Luma` は Rec.709 の係数で輝度を出します。論文は深度や法線ではなく輝度を選んだ理由に色の情報は必ず使えることシェーディングのエイリアスにも効くこと、RGB より速いことを挙げます。

```hlsl
float2 main(float4 pos : SV_Position) : SV_Target {
  int2 p = int2(pos.xy);

  float l = L(p);
  float l_left = L(p + int2(-1, 0));
  float l_top = L(p + int2(0, -1));

  // 1. 単純な辺の判定（論文の e_l）。輝度差がしきい値を超えたら辺。
  float c_left = abs(l - l_left);
  float c_top = abs(l - l_top);
  float2 edges = float2(c_left > g_threshold, c_top > g_threshold);
  if (all(edges == 0.0)) {
    discard;  // どちらも辺でなければ、ここで終える（0 のまま）
  }
```

辺は各画素の左と上だけを持ちます。右と下は隣の画素の辺として取れるためです。しきい値を超えなければそこで終わりです。

```hlsl
  // 2. 局所コントラスト適応（論文の式 1）。
  //    周りに、もっと強い平行な辺があれば、この辺は目に見えないとして捨てる。
  //    近傍に何を選ぶかは、論文の図 5 を見ずに、ここで決めた一例:
  //    右隣の辺 / 下隣の辺 / 左隣のさらに左の辺 / 上隣のさらに上の辺 / 隣の画素の同じ向きの辺
  float c_right = abs(l - L(p + int2(1, 0)));   // 右隣との差
  float c_bottom = abs(l - L(p + int2(0, 1)));   // 下隣との差
  float c_left_2 = abs(l_left - L(p + int2(-2, 0)));   // 左隣とその左の差（左の辺と一直線上の辺）
  float c_top_2 = abs(l_top - L(p + int2(0, -2)));   // 上隣とその上の差（上の辺と一直線上の辺）

  // 左の辺に平行な辺: 上と下の画素の「左の辺」。
  float c_left_up = abs(L(p + int2(0, -1)) - L(p + int2(-1, -1)));   // 上の画素の左の辺
  float c_left_down = abs(L(p + int2(0, 1)) - L(p + int2(-1, 1)));   // 下の画素の左の辺
  // 上の辺に平行な辺: 左と右の画素の「上の辺」。
  float c_top_left = abs(L(p + int2(-1, 0)) - L(p + int2(-1, -1)));   // 左の画素の上の辺
  float c_top_right = abs(L(p + int2(1, 0)) - L(p + int2(1, -1)));   // 右の画素の上の辺

  float max_left = max(max(c_left_up, c_left_down), max(c_right, c_left_2));   // 左の辺の周りで最も強いコントラスト
  float max_top = max(max(c_top_left, c_top_right), max(c_bottom, c_top_2));   // 上の辺の周りで最も強いコントラスト

  // 自分の辺が、周りの最大の g_local_ratio 倍より小さければ、見えない辺として消す。
  edges.x *= (c_left >= g_local_ratio * max_left);   // 弱ければ 0（辺なし）にする
  edges.y *= (c_top >= g_local_ratio * max_top);   // 上の辺も同じ

  return edges;   // x = 左の辺、y = 上の辺
}
```

論文の式 1 は `c_max = max(c_t, c_r, c_b, c_l, c_2l)` で `c_l > 0.5 × c_max` のときだけ辺を残します。近傍の取り方は論文の図 5 に描かれていますが、図を見ていないので平行な辺と自分の隣の辺を取る形を一例として決めました。係数 0.5 は論文の値です。

### TAA の解像パス {#taa-resolve}

次が TAA の解像パスです。サーベイの構成（再投影、検証、混合）に沿って書いています。

```hlsl
Texture2D<float4> g_current : register(t0);    // 今のフレーム。ジッターを入れて描いた色
Texture2D<float4> g_history : register(t1);    // 前のフレームの出力
Texture2D<float2> g_velocity : register(t2);   // 動きベクトル（UV の差。前フレームの位置 = 今の UV - 速度）
Texture2D<float> g_depth : register(t3);
SamplerState g_linear_clamp : register(s0);
SamplerState g_point_clamp : register(s1);

cbuffer TaaCB : register(b0) {
  float2 g_size;        // (幅, 高さ)
  float2 g_inv_size;
  float g_alpha;        // 新しい色の重み（固定 alpha。一例: 0.1）
  float g_gamma;        // 分散クリップの幅 γ（Salvi は 0.75〜1.25 と書く。一例: 1.0）
  float2 g_pad;
};

// 色空間。YCoCg は輝度と色味を分けるので、近傍の箱が輝度の方向に細くなる（Karis）。
float3 ToYCoCg(float3 c) {
  return float3(0.25 * c.r + 0.5 * c.g + 0.25 * c.b,
                0.5 * c.r - 0.5 * c.b,
                -0.25 * c.r + 0.5 * c.g - 0.25 * c.b);
}
float3 FromYCoCg(float3 c) {
  return float3(c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z);
}
```

YCoCg 変換は Karis が近傍の箱を細くするために使ったとサーベイが書く色空間です。輝度（Y）と色味（Co, Cg）が分かれ局所コントラストが主に輝度に出るので、箱が輝度の方向に細くなります。

```hlsl
// 5 回のバイリニア読みで近似した Catmull-Rom。履歴の再サンプルで、ぼけが溜まるのを抑える。
// （サーベイが、UE4 や SMAA T2x が同じ種類の近似を使うと書いている。コードはよく知られた形で、論文のものではない）
float4 SampleCatmullRom(Texture2D<float4> tex, float2 uv) {
  float2 pos = uv * g_size;   // テクセル単位の位置
  float2 center = floor(pos - 0.5) + 0.5;   // サンプル位置を含むテクセルの中心
  float2 f = pos - center;   // そのテクセル中心からの小数のずれ（0〜1）
  float2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f));   // Catmull-Rom の重み。左の端のテクセル
  float2 w1 = 1.0 + f * f * (-2.5 + 1.5 * f);   // 左の真ん中のテクセル
  float2 w2 = f * (0.5 + f * (2.0 - 1.5 * f));   // 右の真ん中のテクセル
  float2 w3 = f * f * (-0.5 + 0.5 * f);   // 右の端のテクセル
  float2 w12 = w1 + w2;   // 真ん中の 2 つは 1 回のバイリニアで読むので、重みを足す
  float2 offset12 = w2 / w12;   // バイリニアの読み位置を、2 つの重みの比にずらす

  float2 p0 = (center - 1.0) * g_inv_size;   // 左（上）の端のテクセルの UV
  float2 p3 = (center + 2.0) * g_inv_size;   // 右（下）の端のテクセルの UV
  float2 p12 = (center + offset12) * g_inv_size;   // 真ん中 2 つをまとめて読む UV

  float4 result = tex.SampleLevel(g_linear_clamp, float2(p12.x, p0.y), 0) * (w12.x * w0.y)   // 上の端 × 真ん中
                + tex.SampleLevel(g_linear_clamp, float2(p0.x, p12.y), 0) * (w0.x * w12.y)   // 左の端 × 真ん中
                + tex.SampleLevel(g_linear_clamp, float2(p12.x, p12.y), 0) * (w12.x * w12.y)   // 真ん中 × 真ん中
                + tex.SampleLevel(g_linear_clamp, float2(p3.x, p12.y), 0) * (w3.x * w12.y)   // 右の端 × 真ん中
                + tex.SampleLevel(g_linear_clamp, float2(p12.x, p3.y), 0) * (w12.x * w3.y);   // 真ん中 × 下の端
  // 角の 4 タップを省いたので、残りの重みの合計で割る。
  float weight = w12.x * w0.y + w0.x * w12.y + w12.x * w12.y + w3.x * w12.y + w12.x * w3.y;   // 使った 5 回分の重みの合計
  return result / weight;   // 角の 4 回を省いた分を正規化する
}
```

履歴の再サンプルはバイリニアだとぼけが毎フレーム溜まります。サーベイは UE4 と SMAA T2x が、バイリニアを 5 回使った Catmull-Rom の近似を使うと書き 100 フレーム繰り返した後でも、バイリニアよりぼけが少ないと述べます。コードはよく知られた 5 タップの形で、論文からの引用ではありません。

```hlsl
// 箱の中心から履歴へ向かう線を、箱の表面で止める。
// （サーベイは「履歴と今のサンプルを結ぶ線分を箱で切る」と書く。ここは中心へ向かう簡易版）
float3 ClipToBox(float3 history, float3 box_min, float3 box_max) {
  float3 center = 0.5 * (box_max + box_min);   // 箱の中心
  float3 extent = 0.5 * (box_max - box_min) + 1e-5;   // 0 割りを避ける。足した処理
  float3 v = history - center;   // 中心から履歴へのベクトル
  float3 a = abs(v / extent);   // 箱の大きさで割った大きさ（1 を超えれば箱の外）
  float m = max(a.x, max(a.y, a.z));   // 3 軸のうち最も外へはみ出した比
  return (m > 1.0) ? center + v / m : history;   // はみ出しているなら、箱の表面まで縮める
}
```

箱で履歴を切る処理です。サーベイは履歴と現在のサンプルを結ぶ線分を箱で切ると書いていますが、ここでは中心へ向かう簡易版にしています。

```hlsl
float4 main(float4 pos : SV_Position) : SV_Target {
  int2 p = int2(pos.xy);   // 整数の画素座標（Load 用）
  float2 uv = (pos.xy) * g_inv_size;   // 画素の中心の UV（pos.xy は +0.5 済み）

  // 1. 3x3 の近傍を読んで、平均と標準偏差を求める。同時に、いちばん手前の画素を探す。
  float3 current = 0;   // 真ん中の画素の色（YCoCg）
  float3 m1 = 0, m2 = 0;   // 色の 1 乗和と 2 乗和（平均と分散のため）
  float closest_depth = 1.0;   // 3x3 の中で最も手前の深度（小さいほど手前）
  int2 closest = int2(0, 0);   // その画素の位置（中心からのずれ）
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      float3 c = ToYCoCg(g_current.Load(int3(p + int2(x, y), 0)).rgb);
      m1 += c;   // 平均用に足す
      m2 += c * c;   // 分散用に 2 乗を足す
      if (x == 0 && y == 0) current = c;   // 真ん中だけ取っておく
      float d = g_depth.Load(int3(p + int2(x, y), 0));   // 深度も同じ 3x3 で読む
      if (d < closest_depth) { closest_depth = d; closest = int2(x, y); }
    }
  }
  float3 mean = m1 / 9.0;   // 9 画素の平均
  float3 sigma = sqrt(max(m2 / 9.0 - mean * mean, 0.0));   // 分散 = E[x^2] - E[x]^2。誤差で負にならないよう max
```

3×3 の近傍を読んで平均と標準偏差を求めます。いちばん手前の深度の画素も同時に探します。動きベクトルを輪郭でそのまま使うと輪郭の外側の背景の速度を拾ってしまうためです。サーベイは小さな 4 タップ程度の膨張で前景の速度を拾う方法を紹介しています。

```hlsl
  // 2. 分散クリップの箱（サーベイの式 6）。外れ値の暗い点や明るい点に引っ張られにくい。
  float3 box_min = mean - g_gamma * sigma;   // 箱の下限（YCoCg）
  float3 box_max = mean + g_gamma * sigma;   // 箱の上限（YCoCg）

  // 3. 動きベクトルは、いちばん手前の画素のものを使う（輪郭の外側を拾わない。Karis の方法）。
  float2 velocity = g_velocity.Load(int3(p + closest, 0));   // 最も手前の画素の速度（UV の差）
  float2 history_uv = uv - velocity;   // 前のフレームで同じ点があった UV

  // 4. 履歴を再サンプルして、箱で切る。画面の外なら、履歴を使わない。
  float3 history = ToYCoCg(SampleCatmullRom(g_history, history_uv).rgb);   // Catmull-Rom で再サンプルした履歴
  history = ClipToBox(history, box_min, box_max);   // 箱の外なら箱の表面へ寄せる
  bool offscreen = any(history_uv < 0.0) || any(history_uv > 1.0);   // 前のフレームの画面外から来た履歴かどうか

  // 5. 明るさで重みを変えて混ぜる（Karis の w(c) = 1 / (1 + L(c))）。
  //    眩しい点が、履歴に長く残って「蛍」になるのを抑える。Y が輝度。
  float alpha = offscreen ? 1.0 : g_alpha;   // 画面外なら今の色だけ（alpha = 1）
  float w_current = alpha / (1.0 + current.x);   // 今の色の重み。明るいほど小さい
  float w_history = (1.0 - alpha) / (1.0 + history.x);   // 履歴の重み。同じく明るいほど小さい
  float3 result = (current * w_current + history * w_history) / (w_current + w_history);   // 重みで正規化した平均

  return float4(max(FromYCoCg(result), 0.0), 1.0);   // RGB へ戻す。負の値は 0 にする
}
```

箱は平均 ± γ × 標準偏差です。γ はサーベイが 0.75〜1.25 くらいと書く値です。AABB（最小・最大）より外れ値に強いとされます。最後に、Karis の輝度の重み `1 / (1 + L)` をかけて混ぜます。眩しい点が履歴に長く残るのを抑えるためです。

### SMAA T2x の時間方向 {#t2x}

SMAA T2x は速度の差で前のフレームの重みを下げる式を持ちます。

```hlsl
Texture2D<float4> g_current : register(t0);        // SMAA 1x をかけた今のフレーム。アルファに速度の大きさ
Texture2D<float4> g_previous : register(t1);       // 前のフレームの出力。アルファに速度の大きさ
Texture2D<float2> g_velocity : register(t2);       // 動きベクトル（UV の差）
SamplerState g_linear_clamp : register(s0);

cbuffer T2xCB : register(b0) {
  float2 g_inv_size;
  float g_k;       // 速度の違いにどれだけ敏感か。論文は 30 を使う（単位は論文に書かれていない）
  float g_pad;
};

// SMAA T2x の時間方向のまとめ（論文の式 6, 7）。
//   w = 0.5 * max(0, 1 - K * sqrt(| |v_cur| - |v_prev| |))
//   c = (1 - w) * c_cur + w * c_prev
// 速度が変わった所（遮蔽が解けた所）では w が 0 に近づき、前のフレームを使わない。
// 論文は、速度の大きさをカラーのアルファに粗く入れておくと、SMAA が速度も一緒に
// なめらかにしてくれて、輪郭の「引きずり」が出ないと書いている。
float4 main(float4 pos : SV_Position) : SV_Target {
  float2 uv = pos.xy * g_inv_size;

  float4 current = g_current.Load(int3(pos.xy, 0));
  float2 velocity = g_velocity.Load(int3(pos.xy, 0));
  float2 previous_uv = uv - velocity;
  float4 previous = g_previous.SampleLevel(g_linear_clamp, previous_uv, 0);

  float speed_current = current.a;     // 今の速度の大きさ
  float speed_previous = previous.a;   // 前の位置にあった速度の大きさ
  float w = 0.5 * max(0.0, 1.0 - g_k * sqrt(abs(speed_current - speed_previous)));

  // 画面の外から来た履歴は使わない。足した処理。
  if (any(previous_uv < 0.0) || any(previous_uv > 1.0)) w = 0.0;

  float3 color = lerp(current.rgb, previous.rgb, w);
  return float4(color, current.a);
}
```

式 6 の `K = 30` は論文の値です。速度の単位が論文に書かれていないので、ここでの単位は一例です。速度が変わった画素は遮蔽が解けた所だと見なし、前のフレームを使いません。そのかわりその画素は時間方向の AA が効かなくなりますが、論文は SMAA の空間の部品が代わりに効くと述べています。

### 数字を出す C++ {#cpp}

ここまで出てきた数字を 1 本の C++ で計算します。固定 α の等価サンプル数、Halton(2, 3) の 8 サンプル、ミップ バイアス、メモリ、TAA のメモリ転送です。

```cpp
// 指数平滑（固定 alpha）で n フレーム溜めたときの「重みを均等にした場合の等価サンプル数」。
// 重み w_i = alpha (1-alpha)^i（新しい順）。最初のフレームの重みは残り (1-alpha)^(n-1)。
// 等価サンプル数 = (Σw)^2 / Σw^2 = 1 / Σw^2（Σw = 1 なので）。
double EffectiveSamples(double alpha, int frames) {
  double sum_sq = 0.0;
  double w = alpha;  // 新しい順に alpha, alpha(1-alpha), ...
  for (int i = 0; i < frames - 1; ++i) {
    sum_sq += w * w;
    w *= 1.0 - alpha;
  }
  const double first = std::pow(1.0 - alpha, frames - 1);  // 最初のフレームは、残りの重みを全部持つ
  sum_sq += first * first;
  return 1.0 / sum_sq;
}
```

等価サンプル数は重みの 2 乗和の逆数です。新しい順に α、α(1−α)、…と重みが付き最初のフレームだけは残りの重み (1−α)^(n−1) をすべて持ちます。α = 0.1 の 5 フレームでは、重みが 0.1、0.09、0.081、0.0729、0.6561 で 2 乗和が約 0.4604、逆数が約 2.2 です。サーベイの値と一致しました。

ミップ バイアスはサーベイの式に従い等価サンプル数 N に対して `−0.5 × log2(N)` です。N = 4 なら −1.0 です。サーベイは実際にはこの値と 0 の間の弱いバイアスが、時間の安定とテクスチャ キャッシュのために好まれることがあると付け加えています。

```cpp
// AA の方式を比べる数字を出す。サンプル数・メモリ・ジッター・ミップ バイアス。
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

namespace {
constexpr int kWidth = 1920;
constexpr int kHeight = 1080;
constexpr double kMiB = 1024.0 * 1024.0;

// 指数平滑（固定 alpha）で n フレーム溜めたときの「重みを均等にした場合の等価サンプル数」。
// 重み w_i = alpha (1-alpha)^i（新しい順）。最初のフレームの重みは残り (1-alpha)^(n-1)。
// 等価サンプル数 = (Σw)^2 / Σw^2 = 1 / Σw^2（Σw = 1 なので）。
double EffectiveSamples(double alpha, int frames) {
  double sum_sq = 0.0;
  double w = alpha;  // 新しい順に alpha, alpha(1-alpha), ...
  for (int i = 0; i < frames - 1; ++i) {
    sum_sq += w * w;
    w *= 1.0 - alpha;
  }
  const double first = std::pow(1.0 - alpha, frames - 1);  // 最初のフレームは、残りの重みを全部持つ
  sum_sq += first * first;
  return 1.0 / sum_sq;
}

// 無限に溜めた定常状態の等価サンプル数。Σ alpha^2 (1-alpha)^(2i) = alpha / (2 - alpha)。
double SteadyState(double alpha) { return (2.0 - alpha) / alpha; }

// Halton 列（index 1 始まり）。
double Halton(int index, int base) {
  double f = 1.0, r = 0.0;
  for (int i = index; i > 0; i /= base) {
    f /= base;
    r += f * (i % base);
  }
  return r;
}

// 解像度 × 1 画素あたりのバイト数 → MiB。
double Mib(int64_t pixels, double bytes_per_pixel) { return pixels * bytes_per_pixel / kMiB; }
}  // namespace

int main() {
  const int64_t pixels = static_cast<int64_t>(kWidth) * kHeight;

  std::printf("== 固定 alpha の等価サンプル数 ==\n");
  std::printf("alpha   5 枚   10 枚   15 枚   定常\n");
  for (double a : {0.05, 0.1, 0.2}) {
    std::printf("%.2f  %5.1f  %5.1f  %5.1f  %5.1f\n", a, EffectiveSamples(a, 5),
                EffectiveSamples(a, 10), EffectiveSamples(a, 15), SteadyState(a));
  }

  std::printf("\n== Halton(2,3) の 8 サンプル（画素の中心からのずれ、画素単位）==\n");
  for (int i = 1; i <= 8; ++i) {
    std::printf("%d: (%+.3f, %+.3f)\n", i, Halton(i, 2) - 0.5, Halton(i, 3) - 0.5);
  }

  std::printf("\n== ミップ バイアス = -0.5 * log2(等価サンプル数) ==\n");
  for (double n : {1.0, 2.0, 4.0, 8.0, 16.0}) {
    std::printf("N=%4.0f  bias=%+.2f\n", n, -0.5 * std::log2(n));
  }

  std::printf("\n== 1920x1080 のメモリ（MiB）==\n");
  // 前方: HDR 色 RGBA16F (8 B) + 深度 D32 (4 B) = 12 B / サンプル。
  // 遅延: G バッファ RGBA8 x4 (16 B) + 深度 4 B = 20 B / サンプル。
  std::printf("samples  forward(12 B)  deferred(20 B)\n");
  for (int s : {1, 2, 4, 8}) {
    std::printf("%5dx  %10.1f  %12.1f\n", s, Mib(pixels * s, 12), Mib(pixels * s, 20));
  }
  // TAA の追加: 履歴 RGBA16F (8 B) + 速度 RG16F (4 B)。
  std::printf("TAA 追加: 履歴 %.1f + 速度 %.1f = %.1f\n", Mib(pixels, 8), Mib(pixels, 4),
              Mib(pixels, 12));
  // TAA の 1 フレームあたりのメモリ転送（近傍 3x3 はキャッシュに載ると仮定）。
  // 読み: 現在色 8 + 履歴 8 + 速度 4 + 深度 4 = 24 B、書き: 8 B。
  const double traffic = Mib(pixels, 24 + 8);
  std::printf("TAA 転送: %.1f MiB / フレーム, 60 fps で %.2f GiB/s\n", traffic,
              traffic * 60 / 1024.0);
  return 0;
}
```

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。

```text title="実行結果"
== 固定 alpha の等価サンプル数 ==
alpha   5 枚   10 枚   15 枚   定常
0.05    1.5    2.4    3.9   39.0
0.10    2.2    5.1    9.8   19.0
0.20    3.8    7.9    8.9    9.0
```

```text title="実行結果（続き）"
== Halton(2,3) の 8 サンプル（画素の中心からのずれ、画素単位）==
1: (+0.000, -0.167)
2: (-0.250, +0.167)
3: (+0.250, -0.389)
4: (-0.375, -0.056)
5: (+0.125, +0.278)
6: (-0.125, -0.278)
7: (+0.375, +0.056)
8: (-0.438, +0.389)
```

```text title="実行結果（続き）"
== ミップ バイアス = -0.5 * log2(等価サンプル数) ==
N=   1  bias=-0.00
N=   2  bias=-0.50
N=   4  bias=-1.00
N=   8  bias=-1.50
N=  16  bias=-2.00
```

```text title="実行結果（続き）"
== 1920x1080 のメモリ（MiB）==
samples  forward(12 B)  deferred(20 B)
    1x        23.7          39.6
    2x        47.5          79.1
    4x        94.9         158.2
    8x       189.8         316.4
TAA 追加: 履歴 15.8 + 速度 7.9 = 23.7
TAA 転送: 63.3 MiB / フレーム, 60 fps で 3.71 GiB/s
```

## よくあるミス

??? failure "遅延シェーディングで MSAA を入れて、フレーム時間が大きく伸びる"
    G バッファがサンプル数ぶん増えて、容量と帯域が支配的になる。SMAA 1x か T2x、TAA に切り替える。論文の測定では遅延での 8x は 300 MB を超えた。

??? failure "MSAA の結果にあとから FXAA を重ねて、ぼける"
    サンプル位置を考えずにサンプルごとに後処理をかけると、グラデーションが合わなくなる。SMAA 論文の図 10 でも同じぼけが出ている。重ねるなら SMAA S2x のように位置を補正する方式にする。

??? failure "TAA で、動くものの後ろに尾が引く"
    履歴の棄却が足りない。動きベクトルが正しくない物（半透明やパーティクル）は、応答の速い AA のフラグで α を上げる。深度の一致を調べ遮蔽が解けた所では履歴を捨てる。

??? failure "TAA で、細い線がちらちら消える"
    クリップの箱が今のフレームだけを根拠に細い特徴を切っている。サーベイの図 9 のとおり 1 サンプル/画素の入力では、細い線が欠けるフレームがある。クリップを弱めるか分散クリップの γ を大きくして試す。

??? failure "固定 α を小さくしたらぼけて、動きでかえってちらつく"
    再サンプルのぼけが溜まっている。α に下限を設けるか Catmull-Rom で再サンプルする。サーベイは動きの小数部に応じた α の下限を理論から導いた研究（Yang 他 2009）を紹介している。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 縁は MSAA・SMAA・TAA、時間のちらつきは TAA だけが本格的に消す。
    - [x] 後処理は 1 サンプル/画素の絵しか見ないので、サブピクセルの特徴は復元できない。
    - [x] 遅延シェーディングの MSAA は、容量と帯域で重い。
    - [x] TAA の画質は、履歴の検証で決まる。ぼけとゴーストは両立しにくい。
    - [x] コストの桁は後処理が約 1 ms、TAA が 0.2 ms 前後（別の GPU の測定）。

## 参考

- Jorge Jimenez, Jose I. Echevarria, Tiago Sousa, Diego Gutierrez, "SMAA: Enhanced Subpixel Morphological Antialiasing", Computer Graphics Forum (Proc. Eurographics 2012) 31(2), 2012. <http://www.iryoku.com/smaa/>（全文と補足資料の本文を読んだ。補足の動画と図は見ていない。「消せるものと消せないもの」「SMAA」「コストを並べる」「SMAA の辺検出」「SMAA T2x の時間方向」で参照）
- Lei Yang, Shiqiu Liu, Marco Salvi, "A Survey of Temporal Antialiasing Techniques", Computer Graphics Forum (Proc. Eurographics 2020, STAR) 39(2), pp. 607–621, 2020. DOI: 10.1111/cgf.14018（全文を読んだ。図は見ていない。「TAA」「コストを並べる」「選び方」「組み合わせの例」「TAA の解像パス」で参照）
- 読んでいない資料: Jimenez 他 "Filtering Approaches for Real-Time Anti-Aliasing"（SIGGRAPH 2011 Course）、Lottes の FXAA 白書、Akeley の RealityEngine。以前のこのページの参考にあった Pettineo の記事は、今回は読んでいない。

## 関連ページ

- [Anti-Aliasing](index.md)
- [MSAA](msaa.md)
- [FXAA](fxaa.md)
- [SMAA](smaa.md)
- [TAA](taa.md)
- [TAA Challenges](taa-challenges.md)
- [Forward and Deferred](../../pipeline/forward-deferred.md)
