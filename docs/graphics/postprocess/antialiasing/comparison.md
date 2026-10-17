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

<svg class="fig illust motion" data-fig="aa-compare" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-aa-compare" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">縁のなめらかさを並べて比べる（同じ斜めの縁）</text>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;1.0000" values="0;0;1;1"/><rect x="18" y="90" width="20" height="20" fill="#191919"/>
<rect x="38" y="90" width="20" height="20" fill="#191919"/>
<rect x="58" y="90" width="20" height="20" fill="#191919"/>
<rect x="78" y="90" width="20" height="20" fill="#191919"/>
<rect x="98" y="90" width="20" height="20" fill="#191919"/>
<rect x="118" y="90" width="20" height="20" fill="#191919"/>
<rect x="138" y="90" width="20" height="20" fill="#191919"/>
<rect x="18" y="110" width="20" height="20" fill="#f2f2f2"/>
<rect x="38" y="110" width="20" height="20" fill="#191919"/>
<rect x="58" y="110" width="20" height="20" fill="#191919"/>
<rect x="78" y="110" width="20" height="20" fill="#191919"/>
<rect x="98" y="110" width="20" height="20" fill="#191919"/>
<rect x="118" y="110" width="20" height="20" fill="#191919"/>
<rect x="138" y="110" width="20" height="20" fill="#191919"/>
<rect x="18" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="38" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="58" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="78" y="130" width="20" height="20" fill="#191919"/>
<rect x="98" y="130" width="20" height="20" fill="#191919"/>
<rect x="118" y="130" width="20" height="20" fill="#191919"/>
<rect x="138" y="130" width="20" height="20" fill="#191919"/>
<rect x="18" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="38" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="58" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="78" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="98" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="118" y="150" width="20" height="20" fill="#191919"/>
<rect x="138" y="150" width="20" height="20" fill="#191919"/>
<rect x="18" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="38" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="58" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="78" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="98" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="118" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="138" y="170" width="20" height="20" fill="#191919"/>
<rect x="18" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="38" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="58" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="78" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="98" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="118" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="138" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="18" y="90" width="140" height="120" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="88.0" y="78" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">なし</text>
<text x="88.0" y="232" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">ギザギザ</text>
<text x="88.0" y="250" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">0 ms</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2157;0.2160;1.0000" values="0;0;1;1"/><rect x="168" y="90" width="20" height="20" fill="#353535"/>
<rect x="188" y="90" width="20" height="20" fill="#191919"/>
<rect x="208" y="90" width="20" height="20" fill="#191919"/>
<rect x="228" y="90" width="20" height="20" fill="#191919"/>
<rect x="248" y="90" width="20" height="20" fill="#191919"/>
<rect x="268" y="90" width="20" height="20" fill="#191919"/>
<rect x="288" y="90" width="20" height="20" fill="#191919"/>
<rect x="168" y="110" width="20" height="20" fill="#bcbcbc"/>
<rect x="188" y="110" width="20" height="20" fill="#505050"/>
<rect x="208" y="110" width="20" height="20" fill="#353535"/>
<rect x="228" y="110" width="20" height="20" fill="#191919"/>
<rect x="248" y="110" width="20" height="20" fill="#191919"/>
<rect x="268" y="110" width="20" height="20" fill="#191919"/>
<rect x="288" y="110" width="20" height="20" fill="#191919"/>
<rect x="168" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="188" y="130" width="20" height="20" fill="#d7d7d7"/>
<rect x="208" y="130" width="20" height="20" fill="#bcbcbc"/>
<rect x="228" y="130" width="20" height="20" fill="#505050"/>
<rect x="248" y="130" width="20" height="20" fill="#353535"/>
<rect x="268" y="130" width="20" height="20" fill="#191919"/>
<rect x="288" y="130" width="20" height="20" fill="#191919"/>
<rect x="168" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="188" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="208" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="228" y="150" width="20" height="20" fill="#d7d7d7"/>
<rect x="248" y="150" width="20" height="20" fill="#bcbcbc"/>
<rect x="268" y="150" width="20" height="20" fill="#505050"/>
<rect x="288" y="150" width="20" height="20" fill="#191919"/>
<rect x="168" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="188" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="208" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="228" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="248" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="268" y="170" width="20" height="20" fill="#bcbcbc"/>
<rect x="288" y="170" width="20" height="20" fill="#505050"/>
<rect x="168" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="188" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="208" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="228" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="248" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="268" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="288" y="190" width="20" height="20" fill="#d7d7d7"/>
<rect x="168" y="90" width="140" height="120" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="238.0" y="78" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">FXAA</text>
<text x="238.0" y="232" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">少しぼけて、なめらか</text>
<text x="238.0" y="250" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">とても軽い</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;1.0000" values="0;0;1;1"/><rect x="318" y="90" width="20" height="20" fill="#202020"/>
<rect x="338" y="90" width="20" height="20" fill="#191919"/>
<rect x="358" y="90" width="20" height="20" fill="#191919"/>
<rect x="378" y="90" width="20" height="20" fill="#191919"/>
<rect x="398" y="90" width="20" height="20" fill="#191919"/>
<rect x="418" y="90" width="20" height="20" fill="#191919"/>
<rect x="438" y="90" width="20" height="20" fill="#191919"/>
<rect x="318" y="110" width="20" height="20" fill="#d7d7d7"/>
<rect x="338" y="110" width="20" height="20" fill="#5d5d5d"/>
<rect x="358" y="110" width="20" height="20" fill="#191919"/>
<rect x="378" y="110" width="20" height="20" fill="#191919"/>
<rect x="398" y="110" width="20" height="20" fill="#191919"/>
<rect x="418" y="110" width="20" height="20" fill="#191919"/>
<rect x="438" y="110" width="20" height="20" fill="#191919"/>
<rect x="318" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="338" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="358" y="130" width="20" height="20" fill="#b5b5b5"/>
<rect x="378" y="130" width="20" height="20" fill="#383838"/>
<rect x="398" y="130" width="20" height="20" fill="#191919"/>
<rect x="418" y="130" width="20" height="20" fill="#191919"/>
<rect x="438" y="130" width="20" height="20" fill="#191919"/>
<rect x="318" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="338" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="358" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="378" y="150" width="20" height="20" fill="#ebebeb"/>
<rect x="398" y="150" width="20" height="20" fill="#898989"/>
<rect x="418" y="150" width="20" height="20" fill="#202020"/>
<rect x="438" y="150" width="20" height="20" fill="#191919"/>
<rect x="318" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="338" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="358" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="378" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="398" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="418" y="170" width="20" height="20" fill="#d7d7d7"/>
<rect x="438" y="170" width="20" height="20" fill="#5d5d5d"/>
<rect x="318" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="338" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="358" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="378" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="398" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="418" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="438" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="318" y="90" width="140" height="120" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="388.0" y="78" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">SMAA</text>
<text x="388.0" y="232" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">縁に忠実</text>
<text x="388.0" y="250" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">軽い</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5197;0.5200;1.0000" values="0;0;1;1"/><rect x="468" y="90" width="20" height="20" fill="#191919"/>
<rect x="488" y="90" width="20" height="20" fill="#191919"/>
<rect x="508" y="90" width="20" height="20" fill="#191919"/>
<rect x="528" y="90" width="20" height="20" fill="#191919"/>
<rect x="548" y="90" width="20" height="20" fill="#191919"/>
<rect x="568" y="90" width="20" height="20" fill="#191919"/>
<rect x="588" y="90" width="20" height="20" fill="#191919"/>
<rect x="468" y="110" width="20" height="20" fill="#f2f2f2"/>
<rect x="488" y="110" width="20" height="20" fill="#868686"/>
<rect x="508" y="110" width="20" height="20" fill="#191919"/>
<rect x="528" y="110" width="20" height="20" fill="#191919"/>
<rect x="548" y="110" width="20" height="20" fill="#191919"/>
<rect x="568" y="110" width="20" height="20" fill="#191919"/>
<rect x="588" y="110" width="20" height="20" fill="#191919"/>
<rect x="468" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="488" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="508" y="130" width="20" height="20" fill="#868686"/>
<rect x="528" y="130" width="20" height="20" fill="#191919"/>
<rect x="548" y="130" width="20" height="20" fill="#191919"/>
<rect x="568" y="130" width="20" height="20" fill="#191919"/>
<rect x="588" y="130" width="20" height="20" fill="#191919"/>
<rect x="468" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="488" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="508" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="528" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="548" y="150" width="20" height="20" fill="#868686"/>
<rect x="568" y="150" width="20" height="20" fill="#191919"/>
<rect x="588" y="150" width="20" height="20" fill="#191919"/>
<rect x="468" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="488" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="508" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="528" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="548" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="568" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="588" y="170" width="20" height="20" fill="#868686"/>
<rect x="468" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="488" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="508" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="528" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="548" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="568" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="588" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="468" y="90" width="140" height="120" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="538.0" y="78" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">MSAA 4x</text>
<text x="538.0" y="232" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">4 段階</text>
<text x="538.0" y="250" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">重い</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6717;0.6720;1.0000" values="0;0;1;1"/><rect x="618" y="90" width="20" height="20" fill="#353535"/>
<rect x="638" y="90" width="20" height="20" fill="#191919"/>
<rect x="658" y="90" width="20" height="20" fill="#191919"/>
<rect x="678" y="90" width="20" height="20" fill="#191919"/>
<rect x="698" y="90" width="20" height="20" fill="#191919"/>
<rect x="718" y="90" width="20" height="20" fill="#191919"/>
<rect x="738" y="90" width="20" height="20" fill="#191919"/>
<rect x="618" y="110" width="20" height="20" fill="#d7d7d7"/>
<rect x="638" y="110" width="20" height="20" fill="#6b6b6b"/>
<rect x="658" y="110" width="20" height="20" fill="#191919"/>
<rect x="678" y="110" width="20" height="20" fill="#191919"/>
<rect x="698" y="110" width="20" height="20" fill="#191919"/>
<rect x="718" y="110" width="20" height="20" fill="#191919"/>
<rect x="738" y="110" width="20" height="20" fill="#191919"/>
<rect x="618" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="638" y="130" width="20" height="20" fill="#f2f2f2"/>
<rect x="658" y="130" width="20" height="20" fill="#bcbcbc"/>
<rect x="678" y="130" width="20" height="20" fill="#353535"/>
<rect x="698" y="130" width="20" height="20" fill="#191919"/>
<rect x="718" y="130" width="20" height="20" fill="#191919"/>
<rect x="738" y="130" width="20" height="20" fill="#191919"/>
<rect x="618" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="638" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="658" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="678" y="150" width="20" height="20" fill="#f2f2f2"/>
<rect x="698" y="150" width="20" height="20" fill="#868686"/>
<rect x="718" y="150" width="20" height="20" fill="#353535"/>
<rect x="738" y="150" width="20" height="20" fill="#191919"/>
<rect x="618" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="638" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="658" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="678" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="698" y="170" width="20" height="20" fill="#f2f2f2"/>
<rect x="718" y="170" width="20" height="20" fill="#d7d7d7"/>
<rect x="738" y="170" width="20" height="20" fill="#6b6b6b"/>
<rect x="618" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="638" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="658" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="678" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="698" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="718" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="738" y="190" width="20" height="20" fill="#f2f2f2"/>
<rect x="618" y="90" width="140" height="120" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="688.0" y="78" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">TAA</text>
<text x="688.0" y="232" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">最もなめらか</text>
<text x="688.0" y="250" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">軽い（履歴）</text>
</g>
<text x="20" y="330" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">どれも同じ縁。左から、なし・FXAA・SMAA・MSAA・TAA（TAA は 8 フレーム分の平均）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
