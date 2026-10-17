---
title: 1 フレームの中身
tags:
  - 3Dゲーム
  - 描画
---

# 1 フレームの中身

**ここまで見てきた「頂点 → ピクセル → 書き込み」の流れは、1 フレームの中で何十回も繰り返されます**。**影を作るために 1 回、物体を描くために 1 回、ぼかしのために 1 回…**と、<strong>目的ごとに分けた描画のまとまりを「パス」</strong>と呼びます。このページでは、**実際のゲームの 1 フレームがどんなパスの連なりで出来ているか**を、**図で追います**。

!!! tip "ポイント"
    - 1 フレーム ＝ <strong>複数のパス</strong>の連なり。<strong>パスごとに描画先（レンダー ターゲット）と使うシェーダーが違う</strong>。
    - 典型の順序：<strong>① シャドウ → ② 不透明 → ③ 空 → ④ 半透明 → ⑤ ポスト エフェクト → ⑥ UI → ⑦ Present</strong>。
    - 前のパスの<strong>結果（画像）が、次のパスの入力（テクスチャ）</strong>になる。
    - 途中の絵は<strong>HDR（明るさに上限がない）</strong>で持ち、<strong>最後にトーンマップで 0〜1 に収める</strong>。
    - パスが多いほど、<strong>描画先の切り替え・メモリ読み書き</strong>が増える。

## パスとは

**パスは、1 つの目的で、1 つ（または複数）の画像に描くまとまり**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="パスの考え方"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">パス：入力のテクスチャ → 処理 → 出力の画像</text>
<g font-size="12">
<rect x="30" y="70" width="170" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/><text x="115" y="100" text-anchor="middle" style="font-weight:700">入力</text><text x="115" y="120" text-anchor="middle" style="font-size:11px">頂点・テクスチャ・前のパスの画像</text>
<rect x="290" y="70" width="170" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/><text x="375" y="100" text-anchor="middle" style="font-weight:700">パス</text><text x="375" y="120" text-anchor="middle" style="font-size:11px">シェーダー ＋ 描画の設定</text>
<rect x="550" y="70" width="200" height="70" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/><text x="650" y="100" text-anchor="middle" style="font-weight:700">出力</text><text x="650" y="120" text-anchor="middle" style="font-size:11px">レンダー ターゲット（画像）</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="202" y1="105" x2="288" y2="105" marker-end="url(#rfa)"/><line x1="462" y1="105" x2="548" y2="105" marker-end="url(#rfa)"/></g>
<text x="20" y="180" style="font-size:12px">出力の画像は、次のパスの入力になる（たとえば「影の画像」→ 本体の描画で読んで、影を付ける）。</text>
</svg>

**画像に描く** ＝ **レンダー ターゲットに描く**です。**レンダー ターゲットはふつうのテクスチャ**で、**描いたあとに別のパスが読めます**。

## 典型的な 1 フレーム

<svg class="fig illust" viewBox="0 0 780 520" role="img" aria-label="1 フレームのパスの連なり">
<text x="20" y="24" class="fig-title">フォワード レンダリングの 1 フレーム</text>
<g font-size="12">
<rect x="30" y="50" width="720" height="62" rx="8" fill="#8a8a8a" fill-opacity="0.18" stroke="#8a8a8a" stroke-width="2"/>
<text x="46" y="74" style="font-weight:700">① シャドウ パス</text><text x="46" y="96">光の位置から見た深度を描く → 影の画像（シャドウ マップ）</text>
<rect x="30" y="122" width="720" height="62" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/>
<text x="46" y="146" style="font-weight:700">② 不透明パス</text><text x="46" y="168">シャドウ マップを読みながら、地形・建物・キャラを描く → HDR のカラー ＋ 深度</text>
<rect x="30" y="194" width="720" height="48" rx="8" fill="#9664e6" fill-opacity="0.18" stroke="#9664e6" stroke-width="2"/>
<text x="46" y="214" style="font-weight:700">③ 空パス</text><text x="46" y="232">最奥のピクセルだけに空を描く（深度テストで）</text>
<rect x="30" y="252" width="720" height="62" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="46" y="276" style="font-weight:700">④ 半透明パス</text><text x="46" y="298">ガラス・煙・水を奥から手前へ（ブレンド。深度は書かない）</text>
<rect x="30" y="324" width="720" height="86" rx="8" fill="#e5484d" fill-opacity="0.15" stroke="#e5484d" stroke-width="2"/>
<text x="46" y="348" style="font-weight:700">⑤ ポスト エフェクト</text><text x="46" y="370">全画面の絵を入力にして加工：ブルーム → 被写界深度 → モーション ブラー → トーンマップ（HDR → 0〜1）</text><text x="46" y="392">出力：LDR（ふつうの明るさ）の画像</text>
<rect x="30" y="420" width="720" height="40" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/>
<text x="46" y="445" style="font-weight:700">⑥ UI パス</text><text x="120" y="445">HP バー・文字・メニューを、最後に上から描く（HDR 加工の影響を受けない）</text>
<rect x="30" y="470" width="720" height="36" rx="8" fill="#4c8bf5" fill-opacity="0.35" stroke="#4c8bf5" stroke-width="2"/>
<text x="46" y="493" style="font-weight:700">⑦ Present</text><text x="130" y="493">完成した絵を画面に出す（バック バッファ → 画面）</text>
</g>
</svg>

| パス | 描画先 | 目的 |
| --- | --- | --- |
| **① シャドウ** | <strong>深度だけのテクスチャ（シャドウ マップ）</strong> | **光から見えない所を調べる** |
| **② 不透明** | **HDR カラー ＋ 深度** | **物体の本体** |
| **③ 空** | **HDR カラー** | **背景** |
| **④ 半透明** | **HDR カラー** | **透ける物・光る物** |
| **⑤ ポスト** | **別の画像を経由して、最終はバック バッファ** | **見た目の仕上げ** |
| **⑥ UI** | **バック バッファ** | **文字・メニュー** |

<!-- fig:frame-build-up:begin -->

<svg class="fig illust motion" data-fig="frame-build-up" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-frame-build-up" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="fp-clip"><rect x="20" y="52" width="420" height="280"/>
</clipPath>
<linearGradient id="fp-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f9cf0"/>
<stop offset="1" stop-color="#cfe8ff"/>
</linearGradient>
<radialGradient id="fp-ball" cx="0.5" cy="0.5" r="0.5" fx="0.35" fy="0.3"><stop offset="0" stop-color="#ffffff"/>
<stop offset="1" stop-color="#e5484d"/>
</radialGradient>
<radialGradient id="fp-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff3b0" stop-opacity="0.95"/>
<stop offset="1" stop-color="#fff3b0" stop-opacity="0"/>
</radialGradient>
<radialGradient id="fp-vig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#000000" stop-opacity="0"/>
<stop offset="1" stop-color="#000000" stop-opacity="0.45"/>
</radialGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">1 フレームが、パスごとに完成していく</text>
<rect x="20" y="52" width="420" height="280" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<g clip-path="url(#fp-clip)"><g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;1.0000" values="0;0;1;1"/><rect x="20" y="52" width="420" height="170" fill="url(#fp-sky)"/>
<circle cx="350" cy="107" r="18" fill="#fff3b0"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1837;0.1840;1.0000" values="0;0;1;1"/><rect x="20" y="222" width="420" height="110" fill="#7aa874"/>
<polygon points="130,282 225,282 265,302 170,302" fill="#3f5d3a" opacity="0.55"/>
<rect x="110" y="202" width="70" height="80" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="290" cy="267" r="38" fill="url(#fp-ball)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;1.0000" values="0;0;1;1"/><rect x="320" y="60" width="110" height="70" fill="#334155" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="340" y="78" width="36" height="34" fill="#cbd5e1"/>
<rect x="385" y="92" width="28" height="20" fill="#94a3b8"/>
<text x="324" y="142" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">シャドウ マップ</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4237;0.4240;1.0000" values="0;0;1;1"/><rect x="210" y="172" width="110" height="140" fill="#7dd3fc" opacity="0.45" stroke="#0ea5e9" stroke-width="2"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5437;0.5440;1.0000" values="0;0;1;1"/><circle cx="350" cy="107" r="70" fill="url(#fp-glow)"/>
<rect x="20" y="52" width="420" height="280" fill="url(#fp-vig)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6637;0.6640;1.0000" values="0;0;1;1"/><rect x="34" y="66" width="130" height="14" fill="#1f2937" opacity="0.75"/>
<rect x="36" y="68" width="96" height="10" fill="#2ea043"/>
<text x="34" y="98" text-anchor="start" style="font-size:13px;font-weight:700;fill:#ffffff;stroke:#1f2937;stroke-width:3px;paint-order:stroke">HP 74 / 100</text>
</g>
</g>
<rect x="462" y="42" width="314" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.1837;0.1840;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="470" y="64" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">① シャドウ</text>
<text x="570" y="64" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光から見た深度を描く</text>
<text x="762" y="64" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043" opacity="0">✓<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></text>
<rect x="462" y="88" width="314" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1837;0.1840;0.3037;0.3040;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="470" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">② 不透明</text>
<text x="570" y="110" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">地面・箱・球（影を読む）</text>
<text x="762" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043" opacity="0">✓<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;1.0000" values="0;0;1;1"/></text>
<rect x="462" y="134" width="314" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.4237;0.4240;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="470" y="156" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">③ 空</text>
<text x="570" y="156" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">最奥のピクセルだけに空</text>
<text x="762" y="156" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043" opacity="0">✓<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></text>
<rect x="462" y="180" width="314" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4237;0.4240;0.5437;0.5440;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="470" y="202" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">④ 半透明</text>
<text x="570" y="202" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ガラスを奥から手前へ</text>
<text x="762" y="202" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043" opacity="0">✓<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5197;0.5200;1.0000" values="0;0;1;1"/></text>
<rect x="462" y="226" width="314" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5437;0.5440;0.6637;0.6640;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="470" y="248" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">⑤ ポスト</text>
<text x="570" y="248" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ブルーム・トーンマップ</text>
<text x="762" y="248" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043" opacity="0">✓<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;1.0000" values="0;0;1;1"/></text>
<rect x="462" y="272" width="314" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6637;0.6640;1.0000;1.0000" values="0;0;1;1;0"/></rect>
<text x="470" y="294" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">⑥ UI</text>
<text x="570" y="294" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">HP バーと文字</text>
<text x="762" y="294" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043" opacity="0">✓<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7597;0.7600;1.0000" values="0;0;1;1"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">まず白紙のフレームから<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;1.0000" values="1;1;0;0"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 光から見た深度（影の材料）を別の画像に描く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.1837;0.1840;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 影を読みながら、不透明な物を描く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1837;0.1840;0.3037;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 何も描かれていない最奥に空を描く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.4237;0.4240;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 半透明は最後に、奥から手前の順<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4237;0.4240;0.5437;0.5440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑤ 全画面を加工（光のにじみ・周辺減光・明るさ調整）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5437;0.5440;0.6637;0.6640;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑥ UI は加工の後に上から描く → Present で画面へ<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6637;0.6640;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:frame-build-up:end -->

## パスごとに変わるもの

**パスごとに次の設定が切り替わります**。

| 設定 | 例 |
| --- | --- |
| <strong>描画先（レンダー ターゲット）</strong> | **シャドウ マップ → HDR カラー → バック バッファ** |
| **ビューポート** | **シャドウ マップの大きさ・画面の大きさ** |
| <strong>カメラ（ビュー・射影）</strong> | **光から見たカメラ → プレイヤーのカメラ** |
| **シェーダー** | **深度だけのシェーダー → 本体のシェーダー** |
| **深度・ブレンド** | **不透明は深度を書く、半透明は書かない** |
| **カリング** | **シャドウは前面カリングなど** |

**切り替え自体にコストがある**ので、**同じ設定のものをまとめて描きます**（ソート）。

## シャドウ パスを詳しく

**影は、「光から見て、手前に別の物があるか」で決まります**。<strong>光の位置にカメラを置いて、深度だけを描いた画像（シャドウ マップ）</strong>を**先に作ります**。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="シャドウ マップ">
<text x="20" y="24" class="fig-title">影のしくみ：光から見た深度を、本体の描画で比べる</text>
<g transform="translate(40,50)">
<circle cx="40" cy="20" r="14" fill="#e5aa28"/><text x="64" y="26" style="font-size:12px">光</text>
<line x1="40" y1="36" x2="130" y2="150" stroke="#e5aa28" stroke-dasharray="5 4"/><line x1="40" y1="36" x2="210" y2="150" stroke="#e5aa28" stroke-dasharray="5 4"/>
<rect x="100" y="80" width="60" height="22" fill="#a0763c"/>
<line x1="0" y1="170" x2="320" y2="170" stroke="currentColor" stroke-width="3"/>
<rect x="120" y="168" width="90" height="4" fill="#222"/>
<text x="165" y="196" text-anchor="middle" style="font-size:12px">影（光が遮られた所）</text>
<circle cx="250" cy="156" r="5" fill="#e5484d"/><text x="258" y="150" style="font-size:12px">ここは光が届く</text>
</g>
<g font-size="12">
<text x="420" y="80" style="font-weight:700">手順</text>
<text x="420" y="104">① 光の位置から深度だけを描く（シャドウ マップ）</text>
<text x="420" y="128">② 本体の描画で、各ピクセルの位置を光から見た座標へ変換</text>
<text x="420" y="152">③ シャドウ マップの深度より奥にあれば「遮られている」→ 影</text>
<text x="420" y="176">④ 影なら光を当てない（暗くする）</text>
<text x="420" y="214" style="font-size:11px">詳細：影（シャドウ マップ・PCF・カスケード）</text>
</g>
</svg>

## ポスト エフェクトの連鎖

**ポスト エフェクトは、完成した絵を入力にして、全画面を覆う 1 枚の三角形を描き**、**ピクセル シェーダーで加工**します。**効果ごとにパスが分かれ、前の出力が次の入力**になります。

<svg class="fig illust" viewBox="0 0 780 180" role="img" aria-label="ポスト エフェクトの連鎖"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ポスト エフェクトの連鎖：画像 → 画像 → 画像</text>
<g font-size="12">
<rect x="20" y="60" width="110" height="60" rx="6" fill="#4c8bf5" fill-opacity="0.25" stroke="#4c8bf5"/><text x="75" y="86" text-anchor="middle">HDR の絵</text><text x="75" y="104" text-anchor="middle" style="font-size:11px">明るさ無制限</text>
<rect x="170" y="60" width="110" height="60" rx="6" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28"/><text x="225" y="86" text-anchor="middle">ブルーム</text><text x="225" y="104" text-anchor="middle" style="font-size:11px">明るい所が光る</text>
<rect x="320" y="60" width="110" height="60" rx="6" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28"/><text x="375" y="86" text-anchor="middle">被写界深度</text><text x="375" y="104" text-anchor="middle" style="font-size:11px">ピントのぼけ</text>
<rect x="470" y="60" width="130" height="60" rx="6" fill="#e5484d" fill-opacity="0.25" stroke="#e5484d"/><text x="535" y="86" text-anchor="middle">トーンマップ</text><text x="535" y="104" text-anchor="middle" style="font-size:11px">HDR → 0〜1</text>
<rect x="640" y="60" width="120" height="60" rx="6" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043"/><text x="700" y="86" text-anchor="middle">画面用の絵</text><text x="700" y="104" text-anchor="middle" style="font-size:11px">ふつうの明るさ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="132" y1="90" x2="168" y2="90" marker-end="url(#rfa)"/><line x1="282" y1="90" x2="318" y2="90" marker-end="url(#rfa)"/><line x1="432" y1="90" x2="468" y2="90" marker-end="url(#rfa)"/><line x1="602" y1="90" x2="638" y2="90" marker-end="url(#rfa)"/></g>
<text x="20" y="160" style="font-size:12px">詳細：ポストプロセス（トーンマップ・ブルーム・被写界深度・モーション ブラーなど）</text>
</svg>

## フォワードとディファード

**不透明パスの作り方は 2 通り**あります。

| 方式 | 流れ | 特徴 |
| --- | --- | --- |
| **フォワード** | **物体を描くときにピクセル シェーダーで光まで全部計算** | **単純・半透明・MSAA が楽。光が多いと重い** |
| **ディファード** | **まず材質情報（色・法線・粗さ）を G バッファへ書く → 別のパスで全画面に光を計算** | **光が多くても軽い。半透明・MSAA が苦手** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="フォワードとディファード"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">フォワード（上）とディファード（下）の違い</text>
<g font-size="12">
<text x="20" y="62" style="font-weight:700">フォワード</text>
<rect x="110" y="44" width="230" height="30" rx="5" fill="#4c8bf5" fill-opacity="0.25" stroke="#4c8bf5"/><text x="225" y="64" text-anchor="middle">物体を描く（形＋材質＋光を一度に）</text>
<rect x="370" y="44" width="150" height="30" rx="5" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043"/><text x="445" y="64" text-anchor="middle">完成した絵</text>
<text x="20" y="162" style="font-weight:700">ディファード</text>
<rect x="110" y="104" width="190" height="30" rx="5" fill="#4c8bf5" fill-opacity="0.25" stroke="#4c8bf5"/><text x="205" y="124" text-anchor="middle">① 材質を G バッファへ</text>
<rect x="110" y="144" width="190" height="30" rx="5" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28"/><text x="205" y="164" text-anchor="middle">② G バッファを読んで光計算</text>
<rect x="370" y="124" width="150" height="30" rx="5" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043"/><text x="445" y="144" text-anchor="middle">完成した絵</text>
<text x="560" y="64" style="font-size:11px">光 × 物体の数だけ計算が増える</text>
<text x="560" y="144" style="font-size:11px">光の計算は画面のピクセル数だけ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="342" y1="59" x2="368" y2="59" marker-end="url(#rfa)"/><line x1="302" y1="119" x2="340" y2="135" marker-end="url(#rfa)"/><line x1="302" y1="159" x2="340" y2="143" marker-end="url(#rfa)"/></g>
</svg>

詳しくは[フォワードとディファード](../../rendering/forward-deferred.md)で扱います。

## パスをつなぐ：画像の使い回し

**画像（レンダー ターゲット）は、一度描いたら、後のパスで何度も使えます**。

| 画像 | 作るパス | 使うパス |
| --- | --- | --- |
| **シャドウ マップ** | **シャドウ パス** | <strong>不透明パス（影の判定）</strong> |
| **深度バッファ** | **不透明パス** | **空・半透明・SSAO・フォグ・水** |
| **HDR カラー** | **不透明・空・半透明** | **ポスト エフェクト** |
| **G バッファ** | **ディファードの材質パス** | **ライティング パス** |
| **SSAO の画像** | **SSAO パス** | **ライティング／合成** |

## パスの数とコスト

**パスを増やすと見た目が良くなる代わりに、次のコストが増えます**。

| コスト | 内容 |
| --- | --- |
| **メモリ** | **中間画像（HDR・G バッファ）が増える** |
| **帯域幅** | **各パスで画像を読み書き**（[メモリ帯域](../../rendering/bandwidth.md)） |
| **切り替え** | **レンダー ターゲットやシェーダーの切り替え** |
| **オーバードロー** | **同じピクセルに何度も描く** |

**フレーム全体の予算**（60 FPS なら 16.7 ms）を**パスに割り振って、重いパスを削る**のが**最適化の基本**です（[フレーム時間の設計](../../optimize/frame-budget.md)）。

## パスを調べる道具

**実際のゲームの 1 フレームは、デバッガーで 1 コマずつ確認できます**。

| ツール | できること |
| --- | --- |
| **RenderDoc** | **1 フレームの全ドロー コールと、各パスの出力画像を見る** |
| <strong>PIX（DirectX）</strong> | **GPU の処理時間をパスごとに見る** |
| **NVIDIA Nsight** | **GPU の詳細なプロファイル** |

**ゲームの画面が出来上がる過程を、RenderDoc で 1 回観察する**と、**このシリーズの内容がすべてつながって理解できます**。

## よくあるミス

??? failure "描画先と読み込み元に同じ画像を指定して、動作が不定になる"
    **同じ画像を同時に出力と入力にできない**。**コピーするか、別の画像に描く**。

??? failure "UI にもトーンマップやブルームが掛かって、文字が光る"
    **UI はポスト エフェクトの後に描く**。

??? failure "半透明が、ポスト エフェクトの後に描かれ、ブルームが効かない"
    **半透明は、HDR のうちに描く**（ポストの前）。

??? failure "パスの順番を間違えて、影のない状態で描かれる"
    **シャドウ マップ → 不透明の順**。**依存する画像を先に作る**。

??? failure "不要なパスや画像を残して、無駄に重い"
    **使っていないパスを止める**。**画像は使い回す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 フレーム ＝ <strong>パスの連なり</strong>。<strong>前のパスの出力が次の入力</strong>
    - [x] 順序：<strong>シャドウ → 不透明 → 空 → 半透明 → ポスト → UI → Present</strong>
    - [x] <strong>HDR で持ち、最後のトーンマップで画面用に</strong>
    - [x] パスごとに<strong>描画先・シェーダー・深度・ブレンド</strong>が<strong>切り替わる</strong>
    - [x] <strong>フォワード／ディファード</strong>は<strong>不透明パスの作り方の違い</strong>
    - [x] <strong>RenderDoc</strong>で<strong>実際のフレームを観察する</strong>と<strong>理解が深まる</strong>

## 参考

- Microsoft, "Direct3D 11 Graphics Pipeline"（Microsoft Learn）
- Adrian Courrèges, "GTA V - Graphics Study"（実際のゲームの 1 フレームの解説）
- RenderDoc ドキュメント

## 関連ページ

- [描画の流れ（入門）](index.md)
- [画面に出す](present.md)
- [描画のしくみ（最適化の入口）](../../rendering/pipeline.md)
- [フォワードとディファード](../../rendering/forward-deferred.md)
- [描画（応用）](../../graphics/index.md)
