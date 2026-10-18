---
title: Bloom
tags:
  - 描画
---

# Bloom

**ブルーム**は<strong>明るい光の周りに柔らかいにじみ（光のもや）</strong>を**足す**効果です。**実際のカメラでは、レンズや目の中で光が少し広がる**ために**起きる**現象で、**これを足すだけで、「眩しさ」「光の強さ」が伝わります**。このセクションでは、**原理・しきい値・ダウンサンプル・ガウスぼかし・Dual Filter・ファイアフライ対策（Karis）・合成**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - ブルーム ＝ <strong>明るい所をぼかして、元の絵に足す</strong>。
    - <strong>点光源をレンズで撮ると、光は 1 点でなく、すそ野が長く広がる</strong>（<strong>PSF</strong>）。<strong>それを再現</strong>する。
    - 作り方 ＝ <strong>① 明るい所を選ぶ → ② 縮小しながらぼかす → ③ 拡大して足し合わせる → ④ 元に足す</strong>。
    - <strong>必ず HDR（リニア）</strong>で行い、<strong>トーンマップの前</strong>に足す。
    - <strong>幅の違うぼかしを足し合わせる</strong>と、<strong>自然なすそ野</strong>になる（<strong>1 回の大きなぼかしより安く、きれい</strong>）。
    - <strong>かけすぎない</strong>。<strong>全体がぼんやりして、眠い絵</strong>になる。

## 仕組みを動かして見る

<!-- fig:bloom-stages:begin -->

<svg class="fig illust motion" data-fig="bloom-stages" viewBox="0 0 780 330" role="img"><rect x="0" y="0" width="780" height="330" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bloom-stages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<filter id="bs-blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9"/>
</filter>
<filter id="bs-blur2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/>
</filter>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ブルームの 4 段階:明るい所を抜き出し、ぼかし、足す</text>
<g opacity="1"><rect x="20" y="80" width="170" height="140" fill="#0f172a"/>
<rect x="34" y="150" width="64" height="70" fill="#334155"/>
<rect x="116" y="176" width="60" height="44" fill="#1e293b"/>
<circle cx="60" cy="122" r="8" fill="#fff7d6"/>
<circle cx="144" cy="138" r="7" fill="#fff7d6"/>
<rect x="48" y="172" width="22" height="18" fill="#fde68a"/>
<rect x="20" y="80" width="170" height="140" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="105" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">① 元の絵</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;1.0000" values="0;0;1;1"/><line x1="194" y1="150" x2="208" y2="150" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-bloom-stages)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/><rect x="210" y="80" width="170" height="140" fill="#000000"/>
<circle cx="250" cy="122" r="8" fill="#fff7d6"/>
<circle cx="334" cy="138" r="7" fill="#fff7d6"/>
<rect x="238" y="172" width="22" height="18" fill="#fde68a"/>
<rect x="210" y="80" width="170" height="140" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="295" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">② 明るい所だけ</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;1.0000" values="0;0;1;1"/><line x1="384" y1="150" x2="398" y2="150" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-bloom-stages)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000" values="0;0;1;1"/><rect x="400" y="80" width="170" height="140" fill="#000000"/>
<circle cx="440" cy="122" r="11.2" fill="#fff7d6" filter="url(#bs-blur)"/>
<circle cx="524" cy="138" r="9.799999999999999" fill="#fff7d6" filter="url(#bs-blur)"/>
<rect x="428" y="172" width="22" height="18" fill="#fde68a" filter="url(#bs-blur2)"/>
<rect x="400" y="80" width="170" height="140" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="485" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">③ ぼかす</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;1.0000" values="0;0;1;1"/><line x1="574" y1="150" x2="588" y2="150" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-bloom-stages)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000" values="0;0;1;1"/><rect x="590" y="80" width="170" height="140" fill="#0f172a"/>
<rect x="604" y="150" width="64" height="70" fill="#334155"/>
<rect x="686" y="176" width="60" height="44" fill="#1e293b"/>
<circle cx="630" cy="122" r="8" fill="#fff7d6"/>
<circle cx="714" cy="138" r="7" fill="#fff7d6"/>
<rect x="618" y="172" width="22" height="18" fill="#fde68a"/>
<circle cx="630" cy="122" r="12.8" fill="#fff7d6" filter="url(#bs-blur)" opacity="0.9"/>
<circle cx="714" cy="138" r="11.200000000000001" fill="#fff7d6" filter="url(#bs-blur)" opacity="0.9"/>
<rect x="618" y="172" width="22" height="18" fill="#fde68a" filter="url(#bs-blur2)" opacity="0.8"/>
<rect x="590" y="80" width="170" height="140" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="675" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">④ 元に足す</text>
<text x="20" y="270" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">シーンを HDR で描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="1;1;0;0"/></text>
<text x="20" y="270" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">しきい値より明るい画素だけ残す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="270" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">残したものを、大きくぼかす<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;0.5736;0.5739;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="270" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">ぼかした光を、元の絵に足す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="20" y="298" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">→ 明るい物の周りが、にじんで光って見える<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bloom-stages:end -->

## 原理：光は 1 点に集まらない

**理想のレンズなら、点光源は 1 点に写ります**。**実際のレンズや目では、光が少し広がり**（**点広がり関数 PSF**）、**明るい光ほど、周りに「にじみ」が見えます**。

<div class="formula">出力 = 元の画像 + 強さ × ( 元の画像 ⊛ PSF )　（⊛：畳み込み＝ぼかし）</div>

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="PSF の形">
<text x="20" y="26" class="fig-title">PSF：中心が強く、すそ野が長い</text>
<line x1="80" y1="180" x2="700" y2="180" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="80,178 200,176 280,170 330,155 360,120 380,70 390,50 400,70 420,120 450,155 500,170 580,176 700,178"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" stroke-dasharray="6 4" points="80,179 200,178 280,172 330,140 360,100 380,66 390,56 400,66 420,100 450,140 500,172 580,178 700,179"/>
<text x="470" y="70" style="font-size:12px;fill:#e5484d">ガウス 1 つ：すそ野が短い</text>
<text x="470" y="92" style="font-size:12px;fill:#2563eb">実際の PSF：すそ野が長い</text>
<text x="80" y="206" style="font-size:12px">中心からの距離 →</text>
</svg>

**ガウス関数 1 つ**では**すそ野が短すぎる**ため、**幅の違う複数のぼかしを重ねる**と、**実際の PSF に近づきます**。**これがミップ チェーンで作るブルームの理屈**です。

## 全体の流れ

ブルームの処理は、次の流れです。最初に、明るい所だけを取り出す<strong>しきい値</strong>の処理があります（なくてもかまいません。[Threshold](threshold.md)）。次に、半分・1/4・1/8…と縮小してミップ チェーンを作る<strong>ダウンサンプル</strong>です（[Downsampling and the Mip Chain](downsample.md)）。各段でガウスなどで<strong>ぼかし</strong>ます（[Gaussian Blur](gaussian.md)）。縮小とぼかしを同時に行う一体化した方式もあります（[Dual Filter](dual-filter.md)）。小さい明るい点がちらつく問題への<strong>対処</strong>が必要です（[Fireflies (Karis Average)](karis-average.md)）。最後に、アップサンプルして足し、元に足す<strong>合成</strong>を行い、強さやレンズ ダートも調整します（[Compositing and Intensity](composite.md)）。

## 方式の比較

方式を比べます。<strong>しきい値とガウス（昔ながら）</strong>は、明るい所を抜いて大きなガウスでぼかす方法で、簡単ですが、大きなガウスが重く、すそ野が短くなります。<strong>ミップ チェーンと加算</strong>は、縮小段ごとにぼかして足し合わせる方法で、すそ野が自然で安いですが、段数の調整が要ります。<strong>Dual Filter</strong> は、縮小・拡大のときにぼかしを兼ねる方法で、最も安く滑らかですが、カーネルの設計が要ります。<strong>しきい値なし（エネルギー保存）</strong>は、全画素をぼかしてわずかに足す方法で、しきい値の「ぱっ」がありませんが、全体がやわらかくなります。

## 関連ページ

- [Post-Processing](../index.md)
- [Tone Mapping and Exposure](../tonemapping/index.md)
- [被写界深度](../dof/index.md)
- [Lens Effects](../lens-effects/index.md)
