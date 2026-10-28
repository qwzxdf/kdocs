---
title: Hi-Z とスクリーン空間トレース
tags:
  - 最適化
  - 3Dゲーム
---

# Hi-Z とスクリーン空間トレース

<strong>Hi-Z（階層的な深度、HZB）</strong> は、深度バッファをミップマップのように縮小していった、階層構造です。縮小するときに、「4 画素のうち、最も奥（最大）の深度」を取るので「この範囲の中にこれより手前の物は、ない」ことが、1 回の読み込みで分かります。この性質が 2 つの用途を支えます。① オクルージョン カリング（物体が隠れているか）、② スクリーン空間レイトレース（SSR・AO の高速な、光線の進行）。このページは、Hi-Z の作り方、カリングでの使い方、トレースでの使い方を説明します。

!!! tip "ポイント"
    - <strong>Hi-Z</strong> ＝ <strong>深度の、ミップ チェーン</strong>。各レベルが「その範囲で最も奥の深度」（最大）。
    - カリング：物体の境界を画面に投影し、適切なミップを 1〜4 回読むだけで、「完全に隠れているか」が分かる。
    - トレース：光線が深度のどこにも当たらない範囲を一気に飛ばせる（大きなミップで大股に進み、近づいたら、細かいミップに降りる）。
    - 目的：1 ピクセルずつ、細かく歩く（リニア マーチ）の、サンプル数を激減。
    - 注意：前フレームの深度を使うと、遅れる（2 パスで解決）。画面外・隠れた物は分からない（スクリーン空間の限界）。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## Hi-Z の作り方

**深度バッファから、コンピュート シェーダーで、ミップを 1 段ずつ、作ります**。各ミップの 1 ピクセルは、下の段の、2×2 の最大深度です。

<svg class="fig illust" viewBox="0 0 800 250" role="img" aria-label="Hi-Z の階層">
<defs><marker id="hz1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">2×2 の、最も奥の深度を取って、縮小していく</text>
<g stroke="currentColor" stroke-width="1.5">
<rect x="30" y="60" width="40" height="40" fill="rgba(76,139,245,0.2)"/><rect x="70" y="60" width="40" height="40" fill="rgba(76,139,245,0.5)"/>
<rect x="30" y="100" width="40" height="40" fill="rgba(76,139,245,0.35)"/><rect x="70" y="100" width="40" height="40" fill="rgba(76,139,245,0.8)"/>
</g>
<text x="40" y="82" style="font-size:11px">0.2</text><text x="80" y="82" style="font-size:11px">0.5</text><text x="40" y="122" style="font-size:11px">0.35</text><text x="80" y="122" style="font-size:11px">0.8</text>
<text x="30" y="166" style="font-size:12px">元の深度（4 画素）</text>
<line x1="124" y1="100" x2="190" y2="100" stroke="currentColor" stroke-width="3" marker-end="url(#hz1)"/><text x="130" y="90" style="font-size:11px">最大</text>
<rect x="200" y="70" width="60" height="60" fill="rgba(76,139,245,0.8)" stroke="currentColor" stroke-width="2"/><text x="215" y="106" style="font-size:12px">0.8</text>
<text x="196" y="166" style="font-size:12px">次のミップ（1 画素）</text>
<text x="330" y="70" style="font-weight:700">意味</text>
<text x="330" y="94" style="font-size:12px">「この 4 画素の範囲で、最も奥は 0.8」</text>
<text x="330" y="114" style="font-size:12px">→ 深度 0.8 より、手前にある物が </text>
<text x="330" y="134" style="font-size:12px">　 この範囲の、どこかに、必ず映っている</text>
<text x="330" y="170" style="font-size:12px">逆に、物体の最も手前が 0.8 より奥なら、その範囲では、完全に隠れている</text>
<text x="20" y="226" style="font-size:12px">※ 深度の向き（0 が手前・1 が奥）で、最大・最小は、逆になる（リバース Z では、最小を取る）</text>
</svg>

| 点 | 説明 |
| --- | --- |
| 最大（最も奥）を取る | 「隠れている」判定を保守的（安全）にするため |
| リバース Z の場合 | 深度の向きが逆なので最小を取る |
| 作成コスト | 全ミップで約 0.1〜0.3 ms（1080p・目安） |
| 非 2 のべき乗 | 奇数サイズの端に注意（縁の画素を取りこぼさない） |

## オクルージョン カリングでの使い方

**物体の境界（球・箱）を画面に投影**し、画面上の大きさを求め、それに見合うミップを読みます。

| 手順 | 内容 |
| --- | --- |
| ① 投影 | 境界箱の 8 頂点を画面に投影し、画面上の矩形と最も手前の深度を得る |
| ② ミップを選ぶ | 矩形が 1〜2 画素に収まるミップを選ぶ（`log2(矩形の大きさ)`） |
| ③ 読む | 矩形の、4 隅（最大 4 回）のサンプルの最大深度を得る |
| ④ 比較 | 物体の最も手前の深度 ＞ Hi-Z の最大深度 なら、完全に隠れている → 除外 |

境界箱 1 つの判定が数回のテクスチャ読み込みで済みます。GPU Driven で、数万個を並列に判定できます（[GPU Driven](gpu-driven.md)・[カリング](culling.md)）。

前フレームの深度を使うときは、カメラの動きによる遅れに、注意（2 パスで解決）。

## スクリーン空間トレースでの使い方

**SSR（画面内の反射）・SSAO・SSGI・コンタクト シャドウ**などは、画面の深度バッファの上で、光線を進めて、当たりを探します。

| 方法 | 説明 |
| --- | --- |
| リニア マーチ | 一定の歩幅で少しずつ進める。歩幅が大きいと薄い物をすり抜ける。小さいとサンプル数が爆発 |
| Hi-Z トレース | 大きなミップで大股に進み、障害物に近づいたら、細かいミップに降りる |

<svg class="fig flow" viewBox="0 0 960 112" role="img" aria-label="Hi-Z トレースの流れ"><defs><marker id="fl13796" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Hi-Z トレースの流れ</text><line x1="127.0" y1="64.0" x2="185.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl13796)"/><line x1="343.0" y1="64.0" x2="401.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl13796)"/><text x="372.0" y="58.0" text-anchor="middle" style="font-size:12px">空いた範囲を飛ばす</text><line x1="545.0" y1="64.0" x2="603.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl13796)"/><line x1="775.0" y1="64.0" x2="833.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl13796)"/><rect x="28.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="76.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">光線を開始</text><rect x="188.0" y="44.0" width="152" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="264.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">大きなミップで大股</text><rect x="404.0" y="44.0" width="138" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="473.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">当たる可能性あり</text><rect x="606.0" y="44.0" width="166" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="689.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">細かいミップへ降りる</text><rect x="836.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="884.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">交点を確定</text></svg>

| 点 | 説明 |
| --- | --- |
| 空いた空間は飛ばす | 「この範囲に障害物はない」と、1 回で分かる |
| 障害物の近くだけ、細かく | サンプル数が画面の複雑さに比例（距離に比例しない） |
| 効果 | SSR の光線あたりの、サンプル数が数十 → 数回 |

### スクリーン空間の限界

| 限界 | 説明 |
| --- | --- |
| 画面外の情報は、ない | 画面の端で反射・AO が消える |
| 隠れた物の情報はない | 柱の裏側など、見えない面は分からない（厚みの仮定が必要） |
| 深度の薄い物 | すり抜けやすい |

足りない部分は、環境マップ（キューブマップ）・レイトレーシングで補います。

## 縮小バッファと組み合わせる

**SSR・AO は半分解像度**で、Hi-Z トレースを行い、深度を考慮して拡大すれば、さらに安くなります（[縮小バッファの効果](low-res-effects.md)）。

<!-- fig:hiz-pyramid:begin -->

<svg class="fig illust motion" data-fig="hiz-pyramid" viewBox="0 0 780 460" role="img"><rect x="0" y="0" width="780" height="460" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hiz-pyramid" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Hi-Z: 4 マスの最も奥の深度を取って、半分の大きさに縮める</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="70" y="100.0" width="53" height="53" fill="#c3cbd5" stroke="#94a3b8" stroke-width="1.5"/>
<text x="96.5" y="132.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.20</text>
<rect x="126" y="100.0" width="53" height="53" fill="#b4bcc8" stroke="#94a3b8" stroke-width="1.5"/>
<text x="152.5" y="132.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.30</text>
<rect x="182" y="100.0" width="53" height="53" fill="#667284" stroke="#94a3b8" stroke-width="1.5"/>
<text x="208.5" y="132.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.80</text>
<rect x="238" y="100.0" width="53" height="53" fill="#566476" stroke="#94a3b8" stroke-width="1.5"/>
<text x="264.5" y="132.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.90</text>
<rect x="70" y="156.0" width="53" height="53" fill="#bbc3ce" stroke="#94a3b8" stroke-width="1.5"/>
<text x="96.5" y="188.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.25</text>
<rect x="126" y="156.0" width="53" height="53" fill="#acb5c1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="152.5" y="188.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.35</text>
<rect x="182" y="156.0" width="53" height="53" fill="#768192" stroke="#94a3b8" stroke-width="1.5"/>
<text x="208.5" y="188.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.70</text>
<rect x="238" y="156.0" width="53" height="53" fill="#4f5c70" stroke="#94a3b8" stroke-width="1.5"/>
<text x="264.5" y="188.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.95</text>
<rect x="70" y="212.0" width="53" height="53" fill="#949eac" stroke="#94a3b8" stroke-width="1.5"/>
<text x="96.5" y="244.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.50</text>
<rect x="126" y="212.0" width="53" height="53" fill="#a4adba" stroke="#94a3b8" stroke-width="1.5"/>
<text x="152.5" y="244.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.40</text>
<rect x="182" y="212.0" width="53" height="53" fill="#85909f" stroke="#94a3b8" stroke-width="1.5"/>
<text x="208.5" y="244.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.60</text>
<rect x="238" y="212.0" width="53" height="53" fill="#7d8898" stroke="#94a3b8" stroke-width="1.5"/>
<text x="264.5" y="244.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.65</text>
<rect x="70" y="268.0" width="53" height="53" fill="#8d97a6" stroke="#94a3b8" stroke-width="1.5"/>
<text x="96.5" y="300.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.55</text>
<rect x="126" y="268.0" width="53" height="53" fill="#9ca6b3" stroke="#94a3b8" stroke-width="1.5"/>
<text x="152.5" y="300.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.45</text>
<rect x="182" y="268.0" width="53" height="53" fill="#949eac" stroke="#94a3b8" stroke-width="1.5"/>
<text x="208.5" y="300.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.50</text>
<rect x="238" y="268.0" width="53" height="53" fill="#6e7a8b" stroke="#94a3b8" stroke-width="1.5"/>
<text x="264.5" y="300.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.75</text>
<text x="70" y="85" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">元の深度（4×4）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="380" y="122.0" width="87" height="87" fill="#acb5c1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="423.5" y="171.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">0.35</text>
<rect x="470" y="122.0" width="87" height="87" fill="#4f5c70" stroke="#94a3b8" stroke-width="1.5"/>
<text x="513.5" y="171.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.95</text>
<rect x="380" y="212.0" width="87" height="87" fill="#8d97a6" stroke="#94a3b8" stroke-width="1.5"/>
<text x="423.5" y="261.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.55</text>
<rect x="470" y="212.0" width="87" height="87" fill="#6e7a8b" stroke="#94a3b8" stroke-width="1.5"/>
<text x="513.5" y="261.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0.75</text>
<text x="380" y="85" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">2×2（各 4 マスの最大）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.4240;0.4242;1.0000" values="0;0;1;1"/><rect x="600" y="152.0" width="117" height="117" fill="#4f5c70" stroke="#94a3b8" stroke-width="1.5"/>
<text x="658.5" y="216.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">0.95</text>
<text x="600" y="85" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">1×1（全体の最大）</text>
</g>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度の値: 小さいほど手前、大きいほど奥<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">元の深度バッファ（一部）<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;0.2422;0.2424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4 マスずつ、最も大きい(奥の)値を残す<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;0.4240;0.4242;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">もう一度縮めると、画面全体で最も奥の値 0.95<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.4240;0.4242;0.6058;0.6061;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">物体の最も手前の深度が 0.97 → 0.95 より奥 → 完全に隠れている → 捨てる<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.6058;0.6061;0.8482;0.8485;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.8482;0.8485;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.6058;0.6061;1.0000" values="1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">物体の最も手前が 0.50 なら、0.95 より手前 → 隠れていない可能性 → 描く<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.6058;0.6061;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:hiz-pyramid:end -->

## よくあるミス

??? failure "Hi-Z に、最小を取って（向きを間違えて）、カリングが不正確になる"
    **深度の向き**（通常 Z / リバース Z）に合わせます。

??? failure "前フレームの Hi-Z で、急な動きにポップインする"
    2 パス方式にします（[GPU Driven](gpu-driven.md)）。

??? failure "SSR で、画面端に不自然な、欠けがある"
    画面端でフェードさせ、環境マップへ切り替えます。

??? failure "リニア マーチの歩幅が大きく、薄い物をすり抜ける"
    Hi-Z トレース、または厚みの仮定を入れます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Hi-Z ＝ <strong>深度のミップ。各段が「範囲内の最も奥の深度」</strong>
    - [x] カリング：境界を投影し、数回の読み込みで隠れているか判定
    - [x] トレース：空いた範囲を大股で飛ばす。リニア マーチより、サンプルが激減
    - [x] 注意：深度の向き・前フレームの遅れ・スクリーン空間の限界
    - [x] 縮小バッファと、組み合わせて、さらに安く

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [カリング](culling.md)
- [GPU Driven Rendering](gpu-driven.md)
- [縮小バッファの効果](low-res-effects.md)
- [深度とカリング](../3d/depth-culling.md)
- [Hi-Z SSR](../graphics/reflections/ssr-hiz.md)
- [Ambient Occlusion (AO)](../graphics/ao/index.md)
