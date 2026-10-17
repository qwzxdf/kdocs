---
title: Lens Effects
tags:
  - 描画
---

# Lens Effects

<strong>CG の画面は、本来「完璧すぎる」</strong>ものです。**実際のカメラは、レンズの歪み・色のずれ・周辺の暗さ・センサーのノイズ・光の反射**など、<strong>さまざまな「不完全さ」</strong>を**持ちます**。<strong>ポストプロセスでこれらを再現すると、「カメラで撮った絵」</strong>に**見え**、**リアリティや映画らしさ**が**増します**。**ただし、どれも「あれば高品質」というものではなく、表現の好みの問題**です。このセクションでは、**色収差・ビネット・フィルム グレイン・レンズ フレア**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - レンズ効果 ＝ <strong>実際のカメラの「不完全さ」を、後から足す</strong>。
    - <strong>どれも表現の好み</strong>。<strong>かけすぎると画面が見づらく、安っぽい</strong>。
    - <strong>色収差</strong>：<strong>画面の端で色がずれる</strong>。<strong>ビネット</strong>：<strong>周辺が暗い</strong>。
    - <strong>フィルム グレイン</strong>：<strong>細かいノイズ</strong>。<strong>レンズ フレア</strong>：<strong>強い光源から、光の反射が出る</strong>。
    - <strong>順序</strong>：<strong>HDR のうち（ブルーム・フレア）→ トーンマップ → LDR（ビネット・色収差・グレイン）</strong>。
    - <strong>かけすぎない</strong>。<strong>設定で切れるように</strong>する。

## 効果の一覧

| 効果 | 内容 | 向く場面 |
| --- | --- | --- |
| [Chromatic Aberration](chromatic-aberration.md) | **画面の端で赤・緑・青がずれる** | **ホラー・SF・被ダメージの演出** |
| [Vignette](vignette.md) | **周辺が暗くなる** | **視線の誘導・映画風・夜のシーン** |
| [Film Grain](film-grain.md) | <strong>細かいノイズ（粒子）</strong> | **フィルムの質感・暗部のバンディング隠し** |
| [Lens Flare](lens-flare.md) | **強い光源から、ゴーストと光芒** | **SF・日光・ヘッドライト** |

<strong>光の筋（ゴッド レイ）</strong>は、**大気の効果**なので[光の筋](../../atmosphere/god-rays/index.md)で扱います。

## 動きで見る：色収差の広がり

<!-- fig:chromatic-aberration-shift:begin -->

<svg class="fig illust motion" data-fig="chromatic-aberration-shift" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chromatic-aberration-shift" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="ca-clip"><rect x="40" y="60" width="700" height="280" rx="6"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">色収差:画面の端ほど、赤と青がずれる</text>
<rect x="40" y="60" width="700" height="280" fill="#000000" rx="6"/>
<g style="mix-blend-mode:screen" clip-path="url(#ca-clip)"><ellipse cx="390.0" cy="200.0" rx="68.0" ry="34.0" fill="none" stroke="#ff0000" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="68;68;71.06;71.06;68;68"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="34;34;35.53;35.53;34;34"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="136.0" ry="68.0" fill="none" stroke="#ff0000" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="136;136;142.12;142.12;136;136"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="68;68;71.06;71.06;68;68"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="204.0" ry="102.0" fill="none" stroke="#ff0000" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="204;204;213.18;213.18;204;204"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="102;102;106.59;106.59;102;102"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="272.0" ry="136.0" fill="none" stroke="#ff0000" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="272;272;284.24;284.24;272;272"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="136;136;142.12;142.12;136;136"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="340.0" ry="170.0" fill="none" stroke="#ff0000" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="340;340;355.3;355.3;340;340"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="170;170;177.65;177.65;170;170"/></ellipse>
<line x1="90.0" y1="74" x2="90.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="90;90;76.5;76.5;90;90"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="90;90;76.5;76.5;90;90"/></line>
<line x1="190.0" y1="74" x2="190.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="190;190;181;181;190;190"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="190;190;181;181;190;190"/></line>
<line x1="290.0" y1="74" x2="290.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="290;290;285.5;285.5;290;290"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="290;290;285.5;285.5;290;290"/></line>
<line x1="390.0" y1="74" x2="390.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"/>
<line x1="490.0" y1="74" x2="490.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="490;490;494.5;494.5;490;490"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="490;490;494.5;494.5;490;490"/></line>
<line x1="590.0" y1="74" x2="590.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="590;590;599;599;590;590"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="590;590;599;599;590;590"/></line>
<line x1="690.0" y1="74" x2="690.0" y2="326" stroke="#ff0000" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="690;690;703.5;703.5;690;690"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="690;690;703.5;703.5;690;690"/></line>
</g>
<g style="mix-blend-mode:screen" clip-path="url(#ca-clip)"><ellipse cx="390.0" cy="200.0" rx="68.0" ry="34.0" fill="none" stroke="#00ff00" stroke-width="3"/>
<ellipse cx="390.0" cy="200.0" rx="136.0" ry="68.0" fill="none" stroke="#00ff00" stroke-width="3"/>
<ellipse cx="390.0" cy="200.0" rx="204.0" ry="102.0" fill="none" stroke="#00ff00" stroke-width="3"/>
<ellipse cx="390.0" cy="200.0" rx="272.0" ry="136.0" fill="none" stroke="#00ff00" stroke-width="3"/>
<ellipse cx="390.0" cy="200.0" rx="340.0" ry="170.0" fill="none" stroke="#00ff00" stroke-width="3"/>
<line x1="90.0" y1="74" x2="90.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
<line x1="190.0" y1="74" x2="190.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
<line x1="290.0" y1="74" x2="290.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
<line x1="390.0" y1="74" x2="390.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
<line x1="490.0" y1="74" x2="490.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
<line x1="590.0" y1="74" x2="590.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
<line x1="690.0" y1="74" x2="690.0" y2="326" stroke="#00ff00" stroke-width="2" opacity="0.8"/>
</g>
<g style="mix-blend-mode:screen" clip-path="url(#ca-clip)"><ellipse cx="390.0" cy="200.0" rx="68.0" ry="34.0" fill="none" stroke="#0000ff" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="68;68;64.94;64.94;68;68"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="34;34;32.47;32.47;34;34"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="136.0" ry="68.0" fill="none" stroke="#0000ff" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="136;136;129.88;129.88;136;136"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="68;68;64.94;64.94;68;68"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="204.0" ry="102.0" fill="none" stroke="#0000ff" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="204;204;194.82;194.82;204;204"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="102;102;97.41;97.41;102;102"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="272.0" ry="136.0" fill="none" stroke="#0000ff" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="272;272;259.76;259.76;272;272"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="136;136;129.88;129.88;136;136"/></ellipse>
<ellipse cx="390.0" cy="200.0" rx="340.0" ry="170.0" fill="none" stroke="#0000ff" stroke-width="3"><animate attributeName="rx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="340;340;324.7;324.7;340;340"/><animate attributeName="ry" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="170;170;162.35;162.35;170;170"/></ellipse>
<line x1="90.0" y1="74" x2="90.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="90;90;103.5;103.5;90;90"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="90;90;103.5;103.5;90;90"/></line>
<line x1="190.0" y1="74" x2="190.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="190;190;199;199;190;190"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="190;190;199;199;190;190"/></line>
<line x1="290.0" y1="74" x2="290.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="290;290;294.5;294.5;290;290"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="290;290;294.5;294.5;290;290"/></line>
<line x1="390.0" y1="74" x2="390.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"/>
<line x1="490.0" y1="74" x2="490.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="490;490;485.5;485.5;490;490"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="490;490;485.5;485.5;490;490"/></line>
<line x1="590.0" y1="74" x2="590.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="590;590;581;581;590;590"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="590;590;581;581;590;590"/></line>
<line x1="690.0" y1="74" x2="690.0" y2="326" stroke="#0000ff" stroke-width="2" opacity="0.8"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="690;690;676.5;676.5;690;690"/><animate attributeName="x2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.3043;0.5217;0.7652;1.0000" values="690;690;676.5;676.5;690;690"/></line>
</g>
<text x="40" y="366" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">ずれなし（元の画像）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;1.0000" values="1;1;0;0"/></text>
<text x="40" y="366" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">中心は動かず、端ほど大きくずれる（赤は外へ、青は内へ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="366" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">端の白い線が、赤と青に分かれて見える<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;0.7649;0.7652;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="366" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">元に戻る<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7649;0.7652;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:chromatic-aberration-shift:end -->

## 適用の順序

| 順序 | 効果 | 理由 |
| --- | --- | --- |
| **① HDR のうち** | **ブルーム・レンズ フレア** | **明るさが 1 を超える光が必要** |
| **② トーンマップ** | **HDR → LDR** | — |
| **③ LDR で** | **色収差・ビネット・グレイン** | **見た目の色に直接かける** |
| **④ UI の前に** | **UI はこれらの影響を受けない** | **文字が歪まない・読める** |

**1 つのパスに色収差・ビネット・グレイン・トーンマップ・ガンマをまとめる**と**フル解像度のパスが 1 回で済み**、**帯域が減ります**。

## かけすぎない

| 効果 | かけすぎると |
| --- | --- |
| **色収差** | **画面が溶けて見え、目が疲れる・酔う** |
| **ビネット** | **画面の周辺が見えず、プレイしにくい** |
| **グレイン** | **ざらざらで細部が見えない** |
| **フレア** | **眩しすぎて、何も見えない** |

**これらは全部「オプションでオフ」にできる**ように**します**。<strong>アクセシビリティ（光過敏・酔いやすい人）</strong>にも**重要**です。

## 関連ページ

- [Post-Processing](../index.md)
- [Bloom](../bloom/index.md)
- [Color Grading](../color-grading/index.md)
- [光の筋](../../atmosphere/god-rays/index.md)
