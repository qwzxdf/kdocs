---
title: Premultiplied Alpha
tags:
  - 描画
---

# Premultiplied Alpha

**乗算済みアルファは、色にあらかじめアルファを掛けておく形式**です。**ブレンド式が単純になり、縁の黒いにじみ（フリンジ）も防げます**。**通常ブレンドと加算ブレンドを、1 つのシェーダーで両立できる**のも**利点**です。このページでは、**乗算済みアルファの意味と使い方**を説明します。

!!! tip "ポイント"
    - **乗算済み ＝ 色 × α を、先に計算して保存**。
    - **ブレンド式：手前 ＋ 奥 × (1 − α)**（One / InvSrcAlpha）。
    - **テクスチャの縁の、黒や白のにじみが出ない**。
    - **α = 0 で加算、α = 1 で通常**として、**1 つの式で両立**できる。

<!-- fig:premult-fringe:begin -->

<svg class="fig illust motion" data-fig="premult-fringe" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-premult-fringe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">縁の黒い線:ストレート アルファは、補間で「透明部分の色」が混ざる</text>
<rect x="60" y="100" width="300" height="70" fill="#e5484d" stroke="#94a3b8" stroke-width="1.5"/>
<text x="210" y="90" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">テクセル A:赤・不透明（α = 1）</text>
<rect x="360" y="100" width="300" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="360" y="100" width="300" height="70" fill="#f1f5f9"/>
<text x="510" y="140" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">（透明。中の RGB は黒）</text>
<text x="510" y="90" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">テクセル B:透明（α = 0）、色は黒</text>
<text x="60" y="214" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ストレート（補間 → その後でブレンド）</text>
<rect x="60" y="230" width="25" height="40" fill="#e14a4f"/>
<rect x="85" y="230" width="25" height="40" fill="#d94f54"/>
<rect x="110" y="230" width="25" height="40" fill="#d25458"/>
<rect x="135" y="230" width="25" height="40" fill="#cc5a5d"/>
<rect x="160" y="230" width="25" height="40" fill="#c75f63"/>
<rect x="185" y="230" width="25" height="40" fill="#c36568"/>
<rect x="210" y="230" width="25" height="40" fill="#bf6b6e"/>
<rect x="235" y="230" width="25" height="40" fill="#bc7274"/>
<rect x="260" y="230" width="25" height="40" fill="#ba787a"/>
<rect x="285" y="230" width="25" height="40" fill="#b97f81"/>
<rect x="310" y="230" width="25" height="40" fill="#b88688"/>
<rect x="335" y="230" width="25" height="40" fill="#b88e8f"/>
<rect x="360" y="230" width="25" height="40" fill="#b99596"/>
<rect x="385" y="230" width="25" height="40" fill="#bb9d9e"/>
<rect x="410" y="230" width="25" height="40" fill="#bea5a6"/>
<rect x="435" y="230" width="25" height="40" fill="#c1aeae"/>
<rect x="460" y="230" width="25" height="40" fill="#c6b6b7"/>
<rect x="485" y="230" width="25" height="40" fill="#cbbfc0"/>
<rect x="510" y="230" width="25" height="40" fill="#d1c8c9"/>
<rect x="535" y="230" width="25" height="40" fill="#d7d2d2"/>
<rect x="560" y="230" width="25" height="40" fill="#dfdbdb"/>
<rect x="585" y="230" width="25" height="40" fill="#e7e5e5"/>
<rect x="610" y="230" width="25" height="40" fill="#f0efef"/>
<rect x="635" y="230" width="25" height="40" fill="#fafafa"/>
<rect x="60" y="230" width="600" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="314" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">乗算済み（先に α を掛けて保存 → 補間）</text>
<rect x="60" y="330" width="25" height="40" fill="#e64c51"/>
<rect x="85" y="330" width="25" height="40" fill="#e75358"/>
<rect x="110" y="330" width="25" height="40" fill="#e85b60"/>
<rect x="135" y="330" width="25" height="40" fill="#e96367"/>
<rect x="160" y="330" width="25" height="40" fill="#ea6a6e"/>
<rect x="185" y="330" width="25" height="40" fill="#eb7276"/>
<rect x="210" y="330" width="25" height="40" fill="#ec7a7d"/>
<rect x="235" y="330" width="25" height="40" fill="#ed8185"/>
<rect x="260" y="330" width="25" height="40" fill="#ee898c"/>
<rect x="285" y="330" width="25" height="40" fill="#ef9093"/>
<rect x="310" y="330" width="25" height="40" fill="#f0989b"/>
<rect x="335" y="330" width="25" height="40" fill="#f1a0a2"/>
<rect x="360" y="330" width="25" height="40" fill="#f3a7aa"/>
<rect x="385" y="330" width="25" height="40" fill="#f4afb1"/>
<rect x="410" y="330" width="25" height="40" fill="#f5b7b9"/>
<rect x="435" y="330" width="25" height="40" fill="#f6bec0"/>
<rect x="460" y="330" width="25" height="40" fill="#f7c6c7"/>
<rect x="485" y="330" width="25" height="40" fill="#f8cdcf"/>
<rect x="510" y="330" width="25" height="40" fill="#f9d5d6"/>
<rect x="535" y="330" width="25" height="40" fill="#faddde"/>
<rect x="560" y="330" width="25" height="40" fill="#fbe4e5"/>
<rect x="585" y="330" width="25" height="40" fill="#fcecec"/>
<rect x="610" y="330" width="25" height="40" fill="#fdf4f4"/>
<rect x="635" y="330" width="25" height="40" fill="#fefbfb"/>
<rect x="60" y="330" width="600" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60" y="222" width="25" height="156" fill="none" stroke="#e5aa28" stroke-width="3"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1037;0.1333;0.1630;0.1926;0.2222;0.2519;0.2815;0.3111;0.3407;0.3704;0.4000;0.4296;0.4593;0.4889;0.5185;0.5481;0.5778;0.6074;0.6370;0.6667;0.6963;0.7259;0.7556" values="60;60;85;110;135;160;185;210;235;260;285;310;335;360;385;410;435;460;485;510;535;560;585;610;635"/></rect>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A と B の境界を、バイリニア補間で読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ストレートは、中間で「黒」が混ざって暗い縁（フリンジ）。乗算済みは、混ざらない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8145;0.8148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">→ 乗算済みアルファなら、縁が自然に薄くなるだけ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8145;0.8148;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:premult-fringe:end -->

## 乗算済みアルファ
**色にあらかじめアルファを掛けて保存**しておく方式です（**Premultiplied Alpha**）。

<div class="formula">C_s' = C_s · α_s　（保存する色）　、　C_out = C_s' + C_d · (1 − α_s)</div>

乗算済みアルファの利点は 4 つです。式が簡単で、ソースに掛け算が不要です（`ONE`）。加算と通常を 1 つのブレンドで表せて、α を 0 にすれば加算（`C_s' + C_d`）になります。縁のにじみが少なく、テクスチャの縁で背景の色（黒や白）が混ざる問題が起きにくくなります。ミップとフィルタが正しく働き、縮小や補間をしても、透明な部分の色に引きずられません。

**ストレート アルファ**（通常の画像）は、**完全に透明な画素の RGB が不定**で、**縮小・補間時に、縁に、白や黒の線（ハロー）が出ます**。**乗算済みアルファのテクスチャ**を使うと、**これが起きません**。

## よくあるミス

??? failure "半透明テクスチャの縁に、黒い線が出る"
    **乗算済みアルファ**にする（または縁の色を広げる）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **色にアルファを先に掛ける**
    - [x] **縁のにじみを防ぎ、式も単純**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Blend State](blend-state.md)
