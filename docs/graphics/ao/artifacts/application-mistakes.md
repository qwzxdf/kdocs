---
title: Application Mistakes
tags:
  - 描画
---

# Application Mistakes

AO を計算するシェーダーが正しくても、できあがった絵が変になることがあります。日向まで暗い全体がどんよりする、金属の隅だけまぶしい遠くで AO の階段が見える画面の端で AO が歪む、といった症状です。原因は AO の式ではなく AO を「どこにどう掛けるか」と「どの空間の値で計算するか」にあることが大半です。このページでは AO が表している量を式から確かめたうえで、適用の間違いを症状ごとに直し、最後に正しい適用を 1 つのシェーダーにまとめます。数字は C++ で数え直しました。

このページでは AO という言葉を「見通し」（1 が遮蔽なし、0 が完全な遮蔽）の意味で使います。GTAO の論文の `A(x)` と同じ向きです。Frostbite の資料の `AO` は、これと逆向き（`1 − 見通し`）で定義されているので、資料と見比べるときは、注意してください。

!!! tip "ポイント"
    - AO は間接拡散にだけ掛けます。直接光は影が自己発光は光源そのものが担当するので、AO を掛けません。
    - アルベドの明るい面ほど隅の光は反射で戻ってきます。多重反射の補正を使うとアルベド 0.9 の面の見通し 0.25 は 0.586 まで戻り、補正なしのまま（0.25）より 2.3 倍明るくなります。
    - スペキュラには粗さと視線の向きに応じた専用の遮蔽を使います。粗さ 1 のときは AO がそのまま返ります。
    - 深度の式は標準 Z とリバース Z で別物です。間違えると 10 m の位置が 0.101 m と読まれます。

!!! info "このページを読む前に"
    - [AO Artifacts](index.md)（このセクションの地図）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（ワールド・ビュー・射影の流れ）
    - [Gamma and HDR Output](../../postprocess/tonemapping/gamma-srgb.md)（リニア空間で掛け算する理由）

## AO が表している量 {#what}

AO を「どこに掛けるか」は AO がどんな近似から出てきたかを見ると決まります。Frostbite の SIGGRAPH 2014 のコース ノート（4.10.1 節）は、McGuire の整理を引いて、次のように説明しています。環境光 `La` のもとでの反射は可視性 `V(l)`（方向 `l` に遮るものがなければ 1、あれば 0）を使って次の積分で書けます。

```text
L(v) = ∫ f(l, v) · La(l) · V(l) · ⟨n·l⟩ dl
```

粗い近似として可視性を BRDF と入射光から切り離します。

```text
L(v) = [ π ∫ f(l, v) · La(l) dl ] · [ (1/π) ∫ V(l) · ⟨n·l⟩ dl ]
         └ 遮蔽なしの環境光反射 ┘     └ 見通し（0〜1） ┘
AO（Frostbite の定義） = 1 − (1/π) ∫ V(l) · ⟨n·l⟩ dl
```

この切り離しが正しいのは BRDF `f` と環境光 `La` が定数のときつまり一様な遠い光に照らされたランバート面のときだけです。資料はどちらも球の上でなめらかなら妥当な近似になるとも書いています。ここから使い方の限界が決まります。

- 切り離せる前提が成り立つのは、間接の拡散です。そこに掛けます。
- 直接光は光の来る方向が 1 つに決まっているので、方向ごとの可視性が答えそのもので、す。その役目は影が持っているので、AO を重ねると二重に暗くなります。
- 鏡面反射は BRDF の山がとがっているので、切り離しの前提が崩れます。専用の遮蔽が必要になります（後の節）。

### 見通しと円錐の角度 {#cone}

GTAO の論文（式 17、18）は見通しを円錐で近似しています。遮蔽が法線の周りで一様なら地平線の角度 `α` と見通し `A` の間に `A = 1 − cos²α`（`cos α = √(1 − A)`）が成り立ちます。C++ で数えると `A = 1` は 90°（半球が全部見える）、`A = 0.75` は 60°、`A = 0.5` は 45°、`A = 0.25` は 30°、`A = 0` は 0° です。見通し 0.5 は半球の半分が見えているので、はなく、法線から 45° の円錐が見えている状態です。この対応はスペキュラ遮蔽やバンプの話で、AO の数字を角度に読み替えるときに、役立ちます。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="ライティングの項ごとの遮蔽"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">どの項に何を掛けるか</text><text x="330" y="40" text-anchor="middle" style="font-size:13px;font-weight:700">ライティングの項ごとに、何を掛けるか</text><rect x="20" y="60" width="150" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="95.0" y="81.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">直接光</text><line x1="170" y1="81" x2="208" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="210" y="60" width="260" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="340.0" y="81.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">影（シャドウ マップ）</text><line x1="470" y1="81" x2="508" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="510" y="60" width="130" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="575.0" y="81.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">AO は掛けない</text><rect x="20" y="118" width="150" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="95.0" y="139.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">間接拡散</text><line x1="170" y1="139" x2="208" y2="139" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="210" y="118" width="260" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="340.0" y="139.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">多重反射つき AO（見通し）</text><line x1="470" y1="139" x2="508" y2="139" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="510" y="118" width="130" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="575.0" y="139.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">掛ける</text><rect x="20" y="176" width="150" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="95.0" y="197.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">間接スペキュラ</text><line x1="170" y1="197" x2="208" y2="197" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="210" y="176" width="260" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="340.0" y="197.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">スペキュラ遮蔽（粗さ・N·V・AO）</text><line x1="470" y1="197" x2="508" y2="197" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="510" y="176" width="130" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="575.0" y="197.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">掛ける</text><rect x="20" y="234" width="150" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="95.0" y="255.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">自己発光</text><line x1="170" y1="255" x2="208" y2="255" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="210" y="234" width="260" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="340.0" y="255.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">なし</text><line x1="470" y1="255" x2="508" y2="255" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="510" y="234" width="130" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="575.0" y="255.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">掛けない</text></svg>

## 適用の間違い {#application}

### 日向まで暗くなる {#sunlit}

AO をライティングの結果の全体（直接光も含む）に掛けると、太陽が当たっている面の隅まで暗くなります。直接光の遮蔽は影が担当しているので、AO は掛けません。上の切り離しの式が示すとおり AO は「環境光が空からどれだけ届くか」を表す量だからです。

直接光の隅に暗さが欲しいときは[コンタクト シャドウ](../../shadows/contact-shadows.md)のように直接光の遮蔽を専用に近似する手法を使います。

### 全体がどんよりする {#overdark}

実際の隅は、壁どうしが光を反射し合うので、AO の値ほどは暗くなりません。AO は一様な環境光が 1 回で届く量だけを数え近くの面で反射して戻ってくる光を落としています。GTAO の論文（5 章）はこの落とした光で隅や角が暗くなりすぎると指摘しています。

対策として論文は近くの面のアルベドが等しいと仮定して、見通し `A` とアルベド `ρ` から、3 回反射までの間接光 `G` を 3 次式で近似しました。式 10 の係数はアルベド `ρ = 0.1、0.2、0.3、0.4、0.5、0.7、0.9` の 7 通りで、いくつかのシーンのシミュレーションを行い 3 次式でフィットした係数をさらにアルベドの 1 次式で表したもので、す。

```text
G(A, ρ) = a(ρ)·A³ − b(ρ)·A² + c(ρ)·A
a(ρ) = 2.0404·ρ − 0.3324
b(ρ) = 4.7951·ρ − 0.6417
c(ρ) = 2.7552·ρ + 0.6903
```

`A = 1` のときは `G ≈ 1` で遮蔽のない面は補正の前後で変わりません。`A` が小さい隅でアルベドが高いほど明るく戻ります。C++ で数えた値は次のとおりです。

- アルベド 0.1：`A = 0.75` で 0.761、`A = 0.5` で 0.507、`A = 0.25` で 0.250。暗い面はほとんど補正されません。
- アルベド 0.5：`A = 0.75` で 0.853、`A = 0.5` で 0.681、`A = 0.25` で 0.418。
- アルベド 0.9：`A = 0.75` で 0.945、`A = 0.5` で 0.855、`A = 0.25` で 0.586。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="多重反射の補正"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">アルベドごとの多重反射の補正</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="570" y2="60" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="562" y="76" text-anchor="end" style="font-size:12px;font-weight:400">補正なし（G = A）</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,250.0 75.0,248.1 80.0,246.2 85.0,244.3 90.0,242.4 95.0,240.5 100.0,238.6 105.0,236.7 110.0,234.8 115.0,232.9 120.0,231.0 125.0,229.1 130.0,227.2 135.0,225.3 140.0,223.4 145.0,221.5 150.0,219.6 155.0,217.7 160.0,215.8 165.0,213.9 170.0,212.0 175.0,210.1 180.0,208.2 185.0,206.3 190.0,204.4 195.0,202.5 200.0,200.6 205.0,198.7 210.0,196.7 215.0,194.8 220.0,192.8 225.0,190.9 230.0,188.9 235.0,187.0 240.0,185.0 245.0,183.0 250.0,181.1 255.0,179.1 260.0,177.2 265.0,175.2 270.0,173.2 275.0,171.3 280.0,169.3 285.0,167.3 290.0,165.4 295.0,163.4 300.0,161.4 305.0,159.5 310.0,157.5 315.0,155.6 320.0,153.6 325.0,151.6 330.0,149.7 335.0,147.7 340.0,145.8 345.0,143.8 350.0,141.9 355.0,139.9 360.0,138.0 365.0,136.0 370.0,134.1 375.0,132.1 380.0,130.2 385.0,128.3 390.0,126.3 395.0,124.4 400.0,122.5 405.0,120.6 410.0,118.6 415.0,116.7 420.0,114.8 425.0,112.9 430.0,111.0 435.0,109.1 440.0,107.2 445.0,105.3 450.0,103.4 455.0,101.6 460.0,99.7 465.0,97.8 470.0,96.0 475.0,94.1 480.0,92.3 485.0,90.4 490.0,88.6 495.0,86.7 500.0,84.9 505.0,83.1 510.0,81.3 515.0,79.5 520.0,77.7 525.0,75.9 530.0,74.1 535.0,72.3 540.0,70.5 545.0,68.8 550.0,67.0 555.0,65.3 560.0,63.5 565.0,61.8 570.0,60.0"/><text x="226.0" y="184.8332978" text-anchor="start" style="font-size:12px;font-weight:700">ρ = 0.1</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 75.0,246.1 80.0,242.3 85.0,238.5 90.0,234.8 95.0,231.2 100.0,227.6 105.0,224.1 110.0,220.6 115.0,217.2 120.0,213.9 125.0,210.6 130.0,207.4 135.0,204.3 140.0,201.2 145.0,198.1 150.0,195.1 155.0,192.2 160.0,189.3 165.0,186.5 170.0,183.7 175.0,181.0 180.0,178.3 185.0,175.7 190.0,173.1 195.0,170.6 200.0,168.1 205.0,165.7 210.0,163.3 215.0,160.9 220.0,158.6 225.0,156.4 230.0,154.2 235.0,152.0 240.0,149.8 245.0,147.7 250.0,145.7 255.0,143.7 260.0,141.7 265.0,139.8 270.0,137.9 275.0,136.0 280.0,134.1 285.0,132.3 290.0,130.6 295.0,128.8 300.0,127.1 305.0,125.5 310.0,123.8 315.0,122.2 320.0,120.6 325.0,119.1 330.0,117.5 335.0,116.0 340.0,114.5 345.0,113.1 350.0,111.6 355.0,110.2 360.0,108.8 365.0,107.5 370.0,106.1 375.0,104.8 380.0,103.5 385.0,102.2 390.0,100.9 395.0,99.7 400.0,98.4 405.0,97.2 410.0,96.0 415.0,94.8 420.0,93.6 425.0,92.4 430.0,91.3 435.0,90.1 440.0,89.0 445.0,87.8 450.0,86.7 455.0,85.6 460.0,84.5 465.0,83.4 470.0,82.3 475.0,81.2 480.0,80.1 485.0,79.0 490.0,77.9 495.0,76.8 500.0,75.7 505.0,74.6 510.0,73.5 515.0,72.4 520.0,71.3 525.0,70.2 530.0,69.1 535.0,68.0 540.0,66.9 545.0,65.8 550.0,64.7 555.0,63.5 560.0,62.4 565.0,61.2 570.0,60.0"/><text x="226.0" y="150.62632100000002" text-anchor="start" style="font-size:12px;font-weight:700">ρ = 0.5</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,250.0 75.0,244.0 80.0,238.2 85.0,232.6 90.0,227.0 95.0,221.6 100.0,216.3 105.0,211.2 110.0,206.1 115.0,201.2 120.0,196.5 125.0,191.8 130.0,187.3 135.0,182.9 140.0,178.6 145.0,174.4 150.0,170.3 155.0,166.4 160.0,162.5 165.0,158.8 170.0,155.2 175.0,151.7 180.0,148.2 185.0,144.9 190.0,141.7 195.0,138.6 200.0,135.6 205.0,132.6 210.0,129.8 215.0,127.1 220.0,124.4 225.0,121.9 230.0,119.4 235.0,117.0 240.0,114.7 245.0,112.5 250.0,110.3 255.0,108.2 260.0,106.2 265.0,104.3 270.0,102.5 275.0,100.7 280.0,99.0 285.0,97.4 290.0,95.8 295.0,94.3 300.0,92.8 305.0,91.4 310.0,90.1 315.0,88.9 320.0,87.6 325.0,86.5 330.0,85.4 335.0,84.3 340.0,83.3 345.0,82.4 350.0,81.4 355.0,80.6 360.0,79.7 365.0,78.9 370.0,78.2 375.0,77.5 380.0,76.8 385.0,76.2 390.0,75.5 395.0,75.0 400.0,74.4 405.0,73.9 410.0,73.4 415.0,72.9 420.0,72.4 425.0,72.0 430.0,71.6 435.0,71.1 440.0,70.8 445.0,70.4 450.0,70.0 455.0,69.6 460.0,69.3 465.0,68.9 470.0,68.6 475.0,68.3 480.0,67.9 485.0,67.6 490.0,67.2 495.0,66.9 500.0,66.5 505.0,66.2 510.0,65.8 515.0,65.4 520.0,65.0 525.0,64.6 530.0,64.2 535.0,63.8 540.0,63.3 545.0,62.8 550.0,62.3 555.0,61.8 560.0,61.2 565.0,60.6 570.0,60.0"/><text x="226.0" y="116.41934419999998" text-anchor="start" style="font-size:12px;font-weight:700">ρ = 0.9</text><text x="70" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">0.25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">0.75</text><text x="570" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="64" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">見通し A（1 = 遮蔽なし）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">補正後の明るさ G</text></svg>

暗い面では隅の光がもともと少ないので、補正がなくても大差ありません。白い面ほど反射で戻る光が多く、補正の効きが大きくなります。ゲームではこの補正を AO の値に入れてから、拡散の環境光に掛けます。論文はこの補正が AO にすでに計算された情報だけを使うので、追加の光の輸送の計算が要らないことを利点に挙げています。

### 暗部が潰れる {#gamma}

sRGB で符号化された色に AO を掛けると、掛け算の結果が物理的な意味を持ちません。アルベド 0.5（sRGB）に AO 0.5 を掛けるとき符号化された値のまま掛けてから線形にすると 0.0509 で、線形にしてから掛けた場合の 0.1070 の 0.48 倍まで暗くなります。ライティングの掛け算はリニア空間で行います。

### 鏡面反射の隅がまぶしい {#specular}

AO を拡散にだけ掛けると隅の鏡面反射（環境マップの映り込み）が暗くならず、隙間なのにまぶしい反射が出ます。Frostbite の資料はこれをスペキュラの光漏れと呼んでいます。プローブは遠くの光を取り込んだもので、その場所の遮蔽を知りません。

AO をそのままスペキュラにも掛けるのは、よい解決ではありません。AO は余弦の山（半球に広がる）の見通しですが、光沢のある面の BRDF の山は粗さが小さいほど細くなります。極端な例が完全な鏡です。見通しは 1 方向だけが問題になり結果は 0 か 1 の二択です。遮蔽されると真っ黒になります。

Frostbite は Gotanda の考えに近い経験的な式を使っています。物理に基づく式ではないと、資料自身が断っています。

```hlsl
float ComputeSpecOcclusion(float NdotV, float AO, float roughness) {
  return saturate(pow(NdotV + AO, exp2(-16.0f * roughness - 1.0f)) - 1.0f + AO);
}
```

資料は挙動を次のように説明しています。完全に粗い面では AO がそのまま返ります。滑らかな面では正面から見たときの AO の影響を弱め縁に近い角度では強めます。C++ で数えた AO（見通し）が 0.5 のときの値です。

- 粗さ 0：`N·V = 1` で 0.725、`N·V = 0.5` で 0.500、`N·V = 0.1` で 0.275
- 粗さ 0.1：0.569、0.500、0.419
- 粗さ 0.5：0.501、0.500、0.499
- 粗さ 1：0.500、0.500、0.500

粗さ 1 では `exp2(-17)` が 0 に近く、`pow(…, 0)` が 1 になって式が `AO` に戻ります。粗さ 0 の正面では `√1.5 − 1 + 0.5 = 0.725` で AO（0.5）より明るくなります。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="スペキュラ遮蔽"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">粗さごとのスペキュラ遮蔽</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="155.0" x2="570" y2="155.0" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="564" y="171.0" text-anchor="end" style="font-size:12px;font-weight:400">AO のまま（0.5）</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="75.0,209.3 80.0,208.0 85.0,206.7 90.0,205.4 95.0,204.1 100.0,202.8 105.0,201.6 110.0,200.3 115.0,199.1 120.0,197.8 125.0,196.6 130.0,195.4 135.0,194.2 140.0,193.0 145.0,191.8 150.0,190.6 155.0,189.5 160.0,188.3 165.0,187.2 170.0,186.0 175.0,184.9 180.0,183.8 185.0,182.7 190.0,181.6 195.0,180.5 200.0,179.4 205.0,178.3 210.0,177.2 215.0,176.1 220.0,175.1 225.0,174.0 230.0,172.9 235.0,171.9 240.0,170.9 245.0,169.8 250.0,168.8 255.0,167.8 260.0,166.8 265.0,165.8 270.0,164.8 275.0,163.8 280.0,162.8 285.0,161.8 290.0,160.8 295.0,159.8 300.0,158.8 305.0,157.9 310.0,156.9 315.0,156.0 320.0,155.0 325.0,154.1 330.0,153.1 335.0,152.2 340.0,151.2 345.0,150.3 350.0,149.4 355.0,148.5 360.0,147.5 365.0,146.6 370.0,145.7 375.0,144.8 380.0,143.9 385.0,143.0 390.0,142.1 395.0,141.2 400.0,140.4 405.0,139.5 410.0,138.6 415.0,137.7 420.0,136.9 425.0,136.0 430.0,135.1 435.0,134.3 440.0,133.4 445.0,132.6 450.0,131.7 455.0,130.9 460.0,130.0 465.0,129.2 470.0,128.4 475.0,127.5 480.0,126.7 485.0,125.9 490.0,125.1 495.0,124.2 500.0,123.4 505.0,122.6 510.0,121.8 515.0,121.0 520.0,120.2 525.0,119.4 530.0,118.6 535.0,117.8 540.0,117.0 545.0,116.2 550.0,115.4 555.0,114.6 560.0,113.9 565.0,113.1 570.0,112.3"/><text x="480.0" y="108.20970300294638" text-anchor="start" style="font-size:12px;font-weight:700">粗さ 0.0</text><polyline fill="none" stroke="#e5aa28" stroke-width="2.5" points="75.0,175.0 80.0,174.4 85.0,173.9 90.0,173.4 95.0,172.8 100.0,172.3 105.0,171.8 110.0,171.3 115.0,170.8 120.0,170.4 125.0,169.9 130.0,169.4 135.0,168.9 140.0,168.5 145.0,168.0 150.0,167.6 155.0,167.1 160.0,166.7 165.0,166.3 170.0,165.9 175.0,165.4 180.0,165.0 185.0,164.6 190.0,164.2 195.0,163.8 200.0,163.4 205.0,163.0 210.0,162.6 215.0,162.2 220.0,161.9 225.0,161.5 230.0,161.1 235.0,160.8 240.0,160.4 245.0,160.0 250.0,159.7 255.0,159.3 260.0,159.0 265.0,158.6 270.0,158.3 275.0,157.9 280.0,157.6 285.0,157.3 290.0,156.9 295.0,156.6 300.0,156.3 305.0,156.0 310.0,155.6 315.0,155.3 320.0,155.0 325.0,154.7 330.0,154.4 335.0,154.1 340.0,153.8 345.0,153.5 350.0,153.2 355.0,152.9 360.0,152.6 365.0,152.3 370.0,152.0 375.0,151.7 380.0,151.4 385.0,151.1 390.0,150.8 395.0,150.6 400.0,150.3 405.0,150.0 410.0,149.7 415.0,149.5 420.0,149.2 425.0,148.9 430.0,148.7 435.0,148.4 440.0,148.1 445.0,147.9 450.0,147.6 455.0,147.4 460.0,147.1 465.0,146.8 470.0,146.6 475.0,146.3 480.0,146.1 485.0,145.8 490.0,145.6 495.0,145.4 500.0,145.1 505.0,144.9 510.0,144.6 515.0,144.4 520.0,144.2 525.0,143.9 530.0,143.7 535.0,143.5 540.0,143.2 545.0,143.0 550.0,142.8 555.0,142.5 560.0,142.3 565.0,142.1 570.0,141.9"/><text x="480.0" y="134.9916155599168" text-anchor="start" style="font-size:12px;font-weight:700">粗さ 0.1</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="75.0,155.2 80.0,155.2 85.0,155.2 90.0,155.2 95.0,155.2 100.0,155.2 105.0,155.2 110.0,155.2 115.0,155.2 120.0,155.2 125.0,155.2 130.0,155.2 135.0,155.2 140.0,155.2 145.0,155.2 150.0,155.2 155.0,155.1 160.0,155.1 165.0,155.1 170.0,155.1 175.0,155.1 180.0,155.1 185.0,155.1 190.0,155.1 195.0,155.1 200.0,155.1 205.0,155.1 210.0,155.1 215.0,155.1 220.0,155.1 225.0,155.1 230.0,155.1 235.0,155.1 240.0,155.1 245.0,155.1 250.0,155.1 255.0,155.1 260.0,155.0 265.0,155.0 270.0,155.0 275.0,155.0 280.0,155.0 285.0,155.0 290.0,155.0 295.0,155.0 300.0,155.0 305.0,155.0 310.0,155.0 315.0,155.0 320.0,155.0 325.0,155.0 330.0,155.0 335.0,155.0 340.0,155.0 345.0,155.0 350.0,155.0 355.0,155.0 360.0,155.0 365.0,155.0 370.0,155.0 375.0,155.0 380.0,155.0 385.0,155.0 390.0,155.0 395.0,154.9 400.0,154.9 405.0,154.9 410.0,154.9 415.0,154.9 420.0,154.9 425.0,154.9 430.0,154.9 435.0,154.9 440.0,154.9 445.0,154.9 450.0,154.9 455.0,154.9 460.0,154.9 465.0,154.9 470.0,154.9 475.0,154.9 480.0,154.9 485.0,154.9 490.0,154.9 495.0,154.9 500.0,154.9 505.0,154.9 510.0,154.9 515.0,154.9 520.0,154.9 525.0,154.9 530.0,154.9 535.0,154.9 540.0,154.9 545.0,154.9 550.0,154.9 555.0,154.9 560.0,154.9 565.0,154.9 570.0,154.8"/><text x="480.0" y="146.86206504213976" text-anchor="start" style="font-size:12px;font-weight:700">粗さ 0.5</text><text x="70" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">0.25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">0.75</text><text x="570" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="64" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">N·V（1 = 正面、0 = 縁）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">スペキュラ遮蔽（AO = 0.5 のとき）</text></svg>

GTAO の論文（6 章）は別の方法を提案しています。見通しを円錐（法線の向きの代わりにベント ノーマルを使う）、BRDF の山も円錐で表して、2 つの円錐の重なりの立体角をスペキュラ円錐の立体角で割ったものをスペキュラ遮蔽 `S` とします。計算が重いので、論文は見通しの円錐の角度 `αv`、ベント ノーマルと反射方向の角度 `β`、粗さ法線と反射方向の角度を引数にした 4 次元の表（32⁴。法線をベント ノーマルで置き換える近似では 32³。どちらも BC4 の 8 ビット）に焼いておく方法を取りました。このページのコードはより簡単な Frostbite の式のほうを使っています。論文の表は再現していません。

### 空・半透明・UI・自己発光 {#special}

- **空。** 深度が far のピクセルには遮蔽がないので、AO は 1 とします。遮蔽の計算にも入れません。空の深度を遮蔽物として拾うと空との境目の画素に実際にはない遮蔽が出ます（私の推測で、資料の記述ではありません）。
- **半透明。** 半透明の物は深度に書かれないのが普通です。深度に書くと背後の AO が半透明の物に引きずられ書かないと、半透明の物に AO が付きません。どちらかに割り切り半透明は別扱いにします。
- **UI とパーティクル。** AO はライティングの段階で、間接光の項に適用します。ポスト プロセスで画面全体に掛けると、UI や発光する物まで暗くなります。
- **自己発光。** 光源そのものなので AO を掛けません。

## 深度と座標の取り違え {#space}

AO が「完全に変」なときは、入力の空間の取り違えであることが多いです。式が合っていても入力の深度や座標が別の空間にあれば、結果は意味を失います。

### 標準 Z とリバース Z {#reverse-z}

標準の深度は near で 0、far で 1 です。リバース Z は逆です。視点空間の距離 `z` に戻す式も違います。`near = 0.1 m`、`far = 1000 m` で数えました。

- 標準の深度バッファからリバース Z の式で戻すと `z = 1 m` が 0.111 m、`z = 10 m` が 0.101 m、`z = 100 m` が 0.100 m になります。どの距離も near の近くに潰れて、AO の半径が画素に換算できなくなります。
- リバース Z のバッファを標準の式で戻したときも同じ値になります。

症状は AO が全体に砂のようにちらつく、全面が同じ明るさになるなどです。深度を線形にして画面に出し距離に比例してなめらかに変わるかを確かめます。

### 遠くの深度の刻み {#depth-step}

24 ビットの標準の深度は遠くで刻みが荒くなります。`near = 0.1 m`、`far = 1000 m` で深度の 1 刻みに当たる距離を数えました。

- `z = 10 m`：0.0001 m（0.1 ミリ）
- `z = 100 m`：0.0060 m（6 ミリ）
- `z = 500 m`：0.1490 m（15 センチ）

500 m 先では 15 センチの階段ができるので、AO が深度の階段をそのまま拾って縞になります。リバース Z と浮動小数点の深度バッファを使うと遠くの刻みが細かくなります。この効果の大きさはこのページでは数えていません。

### 位置の復元 {#reconstruct}

画面の座標と深度から視点空間の位置を戻す式で、2 つ間違えやすい点があります。

1. **y の向きです。** テクスチャの uv は上から下へ増えますが、NDC の y は下から上へ増えます。`ndc.y = 1 − 2v` と反転します。忘れると AO が上下に反転します。
2. **画角とアスペクトです。** 距離 `z` での画面の高さの半分は `z·tan(fov/2)` で、幅の半分はその `aspect` 倍です。`tan(fov/2)` を横の画角で計算しているのに縦の式に使うあるいは `aspect` を掛け忘れると、画面の端で位置が歪みます。16:9 では横方向が 1.78 倍ずれます。

### 法線の空間 {#normal}

法線をワールド空間からビュー空間へ変換するとき変換の行列の向きや掛け順を間違えると、鏡像になります。回転と一様な拡大だけのビュー行列ならビュー行列そのもので、よく、非一様な拡大がある場合は、逆転置行列が必要です。左手系か右手系かも確かめます。このサイトは左手系・Y 上・+Z が前・行ベクトルを使います。

### デバッグの順番 {#debug}

AO が変なときは次の順に確かめます。

1. **線形深度を出します。** 距離に比例してなめらかに変わっているかを見ます。
2. **復元した位置を色で出します。** ワールドの座標の目盛り（グリッド）と見比べます。位置が正しければ AO の式の誤りに絞れます。
3. **法線を色で出します。** 空間（ビューかワールドか）と向きを確かめます。
4. **AO だけを出します。** 適用の前の AO の見た目を確かめます。

## 通して組む：AO を適用するシェーダー {#hlsl}

ここまでの内容を 1 つのライティング パスにまとめます。`fxc`（Windows SDK 10.0.26100.0、`-T ps_5_0`）でコンパイルが通ることを確かめました。実行はしていません。AO の計算そのものは別のページ（[GTAO](../gtao.md) など）にありここでは AO のテクスチャ `gAo` を受け取る側だけを書きます。

まず、定数バッファとテクスチャです。

```hlsl
// ---- AO を適用するライティング パス（左手系・Y 上・+Z が前・行ベクトル。リニア空間で計算）----

cbuffer ApplyCB : register(b0) {
  float gTanHalfFov;     // tan(縦の画角 / 2)。縦 60 度なら 0.57735
  float gAspect;         // 幅 / 高さ（例: 16 / 9 = 1.7778）
  float gNear;           // near（m）。射影行列に使った値と同じにする
  float gFar;            // far（m）。同上
  uint  gReversedZ;      // 1: リバース Z（near が 1、far が 0）。0: 標準（near が 0、far が 1）
  float gAoStrength;     // AO の強さ 0〜1（0 で無効）。見た目の調整用
  float2 gPad;           // 16 バイトの境界にそろえる詰め物
};

Texture2D<float>  gDepth      : register(t0);   // 深度バッファ（D32_FLOAT の読み取り用の見え方）
Texture2D<float>  gAo         : register(t1);   // AO（見通し。1 = 遮蔽なし、0 = 完全な遮蔽）
Texture2D<float4> gAlbedoRough: register(t2);   // rgb: アルベド（リニア）、a: 粗さ
Texture2D<float4> gNormalView : register(t3);   // xyz: 視点空間の法線（長さ 1）
Texture2D<float3> gIrradiance : register(t4);   // 間接拡散（放射照度 × 1/π を済ませた値）
Texture2D<float3> gPrefiltered: register(t5);   // 間接スペキュラ（プローブから引いた値）
Texture2D<float3> gDirect     : register(t6);   // 直接光（影を掛けた後の値。AO は掛けない）
Texture2D<float3> gEmissive   : register(t7);   // 自己発光（AO は掛けない）
SamplerState      gPoint      : register(s0);
```

`gReversedZ` で深度の向きを切り替えます。`gAoStrength` は見た目の調整で 0 にすれば AO が無効になります。

次に、深度から視点空間の位置を戻す関数です。

```hlsl
// 深度バッファの値 d から、視点空間の距離 z（m）に戻す。
float LinearizeDepth(float d) {
  // リバース Z は d を 1 - d にそろえてから、標準の式を使う（足した: 式を 1 つにまとめる）。
  float ds = gReversedZ != 0 ? 1.0 - d : d;
  return gNear * gFar / (gFar - ds * (gFar - gNear));   // 標準の射影の逆
}

// 画面の uv と深度から、視点空間の位置（m）を戻す。+Z が前、Y が上。
float3 ViewPosition(float2 uv, float d) {
  float z = LinearizeDepth(d);                           // 視点空間の距離
  // uv は左上が (0,0) で下向きが +v。NDC は上向きが +y なので、y だけ向きを反転する。
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  // 距離 z で、画面の端が見える幅は z * tan(fov/2)（縦）と、その aspect 倍（横）。
  return float3(ndc.x * gTanHalfFov * gAspect * z, ndc.y * gTanHalfFov * z, z);
}
```

`LinearizeDepth` はリバース Z のとき `1 − d` にそろえてから標準の式を使います。標準の式の `d` を `ds` に置き換えただけです。この処理は資料にない処理で私が式を 1 つにまとめるために足しました。`ViewPosition` は `uv` の y を反転して NDC にし、`z·tan(fov/2)` をかけて位置にします。

AO の適用に使う 2 つの式です。

```hlsl
// 多重反射の補正（GTAO 論文の式 10）。ao は見通し（1 = 遮蔽なし）。albedo はリニアの 0〜1。
float3 MultiBounce(float ao, float3 albedo) {
  float3 a = 2.0404 * albedo - 0.3324;                   // A^3 の係数
  float3 b = -4.7951 * albedo + 0.6417;                  // A^2 の係数（符号を含めて持つ）
  float3 c = 2.7552 * albedo + 0.6903;                   // A の係数
  return max(ao.xxx, ((ao * a + b) * ao + c) * ao);      // 補正で AO より暗くならないように max（足した）
}

// スペキュラ遮蔽（Frostbite、リスト 26）。n_dot_v は法線と視線の cos。
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  float e = exp2(-16.0 * roughness - 1.0);               // 粗いほど 0 に近い指数になる
  return saturate(pow(abs(n_dot_v + ao), e) - 1.0 + ao); // 粗さ 1 でほぼ ao、滑らかだと視線の向きで変わる
}
```

`MultiBounce` は論文の式 10 を `((A·a + b)·A + c)·A` の形にしたものです（`b` の符号を係数に含めて持ちます）。補正の後に `max(ao, …)` を使うのは補正で AO より暗くならないようにするためで、資料にない処理です。`SpecularOcclusion` は Frostbite のリスト 26 に `abs` を足したものです（`NdotV + AO` が負になって `pow` が壊れるのを防ぐための足し込みです）。

最後がライティングの本体です。

```hlsl
float4 ApplyAoPS(float4 sv_position : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  int2 texel = int2(sv_position.xy);                     // 自分のテクセル
  float depth = gDepth.Load(int3(texel, 0));             // 深度バッファの値

  // 空: 深度が far のピクセルには遮蔽がない。AO = 1 として、AO を掛けない値で返す。
  bool is_sky = gReversedZ != 0 ? depth <= 0.0 : depth >= 1.0;
  float3 direct = gDirect.Load(int3(texel, 0));          // 直接光（影で遮蔽済み）
  if (is_sky) return float4(direct, 1.0);                // 足した: 空は AO と間接光の対象外

  float4 ar = gAlbedoRough.Load(int3(texel, 0));         // アルベドと粗さ
  float3 albedo = ar.rgb;
  float roughness = ar.a;
  float3 n = normalize(gNormalView.Load(int3(texel, 0)).xyz);   // 視点空間の法線
  float3 p = ViewPosition(uv, depth);                    // 視点空間の位置（m）
  float3 v = normalize(-p);                              // 視線: ピクセルからカメラへ（カメラは原点）

  // AO は強さで線形に弱められるようにしておく（0 で無効、1 で全開）。
  float ao = lerp(1.0, gAo.SampleLevel(gPoint, uv, 0), gAoStrength);

  float3 diffuse_ambient = gIrradiance.Load(int3(texel, 0)) * albedo;   // 間接拡散（遮蔽なしの値）
  diffuse_ambient *= MultiBounce(ao, albedo);            // 多重反射つきの AO。拡散にだけ掛ける

  float n_dot_v = saturate(dot(n, v));                   // 法線と視線の cos
  float3 spec_ambient = gPrefiltered.Load(int3(texel, 0));              // 間接スペキュラ（遮蔽なしの値）
  spec_ambient *= SpecularOcclusion(n_dot_v, ao, roughness);            // スペキュラ遮蔽

  // 直接光と自己発光には AO を掛けない。直接光の遮蔽は影、自己発光は光源そのもの。
  float3 emissive = gEmissive.Load(int3(texel, 0));
  return float4(direct + diffuse_ambient + spec_ambient + emissive, 1.0);
}
```

空のピクセルは直接光だけを返します。そうでないピクセルは拡散の環境光に `MultiBounce`、スペキュラの環境光に `SpecularOcclusion` を掛けて、直接光と自己発光は掛けずに足します。

## C++ で数字を確かめる {#cpp}

このページの数字は次のプログラムの出力です。`g++ -std=c++23 -Wall -Wextra` でコンパイルして実行しました。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>

// 0〜1 に切る（HLSL の saturate と同じ）。
double Saturate(double x) { return std::clamp(x, 0.0, 1.0); }

// ---- 1. 多重反射の補正（GTAO 論文の式 10）----
// a: 見通し（1 = 遮蔽なし、0 = 完全に遮蔽）、rho: アルベド（0〜1）。
// 論文は、見通し A とアルベド rho から、3 回反射までの間接光 G を 3 次式で近似している。
double MultiBounce(double a, double rho) {
  const double ca = 2.0404 * rho - 0.3324;           // a(rho): A の 3 乗の係数
  const double cb = 4.7951 * rho - 0.6417;           // b(rho): A の 2 乗の係数（式の中で引く）
  const double cc = 2.7552 * rho + 0.6903;           // c(rho): A の 1 乗の係数
  return ca * a * a * a - cb * a * a + cc * a;       // G(A, rho) = a A^3 - b A^2 + c A
}

// ---- 2. スペキュラ遮蔽（Frostbite のリスト 26）----
// n_dot_v: 法線と視線の cos、ao: 見通し、roughness: 粗さ（GGX の roughness）。
double SpecularOcclusion(double n_dot_v, double ao, double roughness) {
  const double e = std::exp2(-16.0 * roughness - 1.0);          // 粗いほど指数が 0 に近づく
  return Saturate(std::pow(n_dot_v + ao, e) - 1.0 + ao);        // 粗さ 1 ではほぼ ao のまま
}

// ---- 3. 円錐の見通し（GTAO 論文の式 17、18）----
double ConeHalfAngleDeg(double a) {
  return std::acos(std::sqrt(1.0 - a)) * 180.0 / 3.14159265358979;   // cos(alpha) = sqrt(1 - A)
}

// ---- 4. 深度から視点空間の z を戻す ----
// n, f: near と far（m）。標準の深度は near で 0、far で 1。リバース Z は逆。
double ViewZStandard(double d, double n, double f) { return n * f / (f - d * (f - n)); }
double ViewZReversed(double d, double n, double f) { return n * f / (n + d * (f - n)); }
double DepthStandard(double z, double n, double f) { return f / (f - n) * (1.0 - n / z); }
double DepthReversed(double z, double n, double f) { return 1.0 - DepthStandard(z, n, f); }

// ---- 5. sRGB の符号化 ----
double SrgbToLinear(double c) { return c <= 0.04045 ? c / 12.92 : std::pow((c + 0.055) / 1.055, 2.4); }

int main() {
  std::printf("-- cone angle and visibility (A = 1 - cos^2 alpha)\n");
  for (double a : {1.0, 0.75, 0.5, 0.25, 0.0}) {       // 見通し（1 = 遮蔽なし）
    std::printf("A=%.2f: half angle = %5.1f deg\n", a, ConeHalfAngleDeg(a));
  }

  std::printf("-- multi-bounce G(A, rho)\n");
  for (double rho : {0.1, 0.5, 0.9}) {                 // アルベド
    std::printf("rho=%.1f:", rho);
    for (double a : {1.0, 0.75, 0.5, 0.25}) {          // 見通し
      std::printf("  A=%.2f -> %.3f", a, MultiBounce(a, rho));
    }
    std::printf("\n");
  }

  std::printf("-- specular occlusion, AO(visibility) = 0.5\n");
  for (double r : {0.0, 0.1, 0.5, 1.0}) {              // 粗さ
    std::printf("roughness=%.1f:", r);
    for (double v : {1.0, 0.5, 0.1}) {                 // N.V（1 = 正面、0.1 = ほぼ縁）
      std::printf("  N.V=%.1f -> %.3f", v, SpecularOcclusion(v, 0.5, r));
    }
    std::printf("\n");
  }

  std::printf("-- depth decode with the wrong formula (n = 0.1, f = 1000)\n");
  const double n = 0.1, f = 1000.0;
  for (double z : {1.0, 10.0, 100.0}) {                // 本当の視点空間の距離（m）
    const double d_std = DepthStandard(z, n, f);       // 標準の深度バッファに書かれる値
    const double d_rev = DepthReversed(z, n, f);       // リバース Z の深度バッファに書かれる値
    std::printf("z=%5.0f: standard d=%.6f, reversed d=%.6f | std-buffer decoded as reversed -> %.3f m | rev-buffer decoded as standard -> %.3f m\n",
                z, d_std, d_rev, ViewZReversed(d_std, n, f), ViewZStandard(d_rev, n, f));
  }

  std::printf("-- 24-bit depth step, standard Z, linear error at distance\n");
  const double step = 1.0 / 16777216.0;                // 24 ビット固定小数点の刻み
  for (double z : {10.0, 100.0, 500.0}) {
    const double d = DepthStandard(z, n, f);
    const double dz = ViewZStandard(d + step, n, f) - ViewZStandard(d, n, f);   // 1 刻み分の距離の誤差
    std::printf("z=%4.0f: one depth step = %.4f m\n", z, dz);
  }

  std::printf("-- gamma: albedo 0.5 (sRGB-coded) times AO 0.5\n");
  const double albedo_srgb = 0.5;
  const double wrong = SrgbToLinear(albedo_srgb * 0.5);               // 符号化された値に AO を掛けてから線形にした
  const double right = SrgbToLinear(albedo_srgb) * 0.5;               // 線形にしてから AO を掛けた
  std::printf("wrong (multiply in sRGB) = %.4f linear, right = %.4f linear, ratio = %.2f\n", wrong, right, wrong / right);
}
```

```text title="実行結果"
-- cone angle and visibility (A = 1 - cos^2 alpha)
A=1.00: half angle =  90.0 deg
A=0.75: half angle =  60.0 deg
A=0.50: half angle =  45.0 deg
A=0.25: half angle =  30.0 deg
A=0.00: half angle =   0.0 deg
-- multi-bounce G(A, rho)
rho=0.1:  A=1.00 -> 1.000  A=0.75 -> 0.761  A=0.50 -> 0.507  A=0.25 -> 0.250
rho=0.5:  A=1.00 -> 1.000  A=0.75 -> 0.853  A=0.50 -> 0.681  A=0.25 -> 0.418
rho=0.9:  A=1.00 -> 1.000  A=0.75 -> 0.945  A=0.50 -> 0.855  A=0.25 -> 0.586
-- specular occlusion, AO(visibility) = 0.5
roughness=0.0:  N.V=1.0 -> 0.725  N.V=0.5 -> 0.500  N.V=0.1 -> 0.275
roughness=0.1:  N.V=1.0 -> 0.569  N.V=0.5 -> 0.500  N.V=0.1 -> 0.419
roughness=0.5:  N.V=1.0 -> 0.501  N.V=0.5 -> 0.500  N.V=0.1 -> 0.499
roughness=1.0:  N.V=1.0 -> 0.500  N.V=0.5 -> 0.500  N.V=0.1 -> 0.500
-- depth decode with the wrong formula (n = 0.1, f = 1000)
z=    1: standard d=0.900090, reversed d=0.099910 | std-buffer decoded as reversed -> 0.111 m | rev-buffer decoded as standard -> 0.111 m
z=   10: standard d=0.990099, reversed d=0.009901 | std-buffer decoded as reversed -> 0.101 m | rev-buffer decoded as standard -> 0.101 m
z=  100: standard d=0.999100, reversed d=0.000900 | std-buffer decoded as reversed -> 0.100 m | rev-buffer decoded as standard -> 0.100 m
-- 24-bit depth step, standard Z, linear error at distance
z=  10: one depth step = 0.0001 m
z= 100: one depth step = 0.0060 m
z= 500: one depth step = 0.1490 m
-- gamma: albedo 0.5 (sRGB-coded) times AO 0.5
wrong (multiply in sRGB) = 0.0509 linear, right = 0.1070 linear, ratio = 0.48
```

## よくあるミス {#mistakes}

??? failure "AO が画面全体を暗くして、重い絵になる"
    直接光やスペキュラ、自己発光にまで AO を掛けていないかを確かめます。拡散の環境光にだけ多重反射の補正を入れてから掛けます。

??? failure "AO が斑模様や砂のようになる"
    深度の線形化の式が深度バッファの向き（標準 Z かリバース Z か）や、射影行列の near と far と合っていません。線形深度を画面に出して距離に比例しているかを確かめます。

??? failure "AO が上下に反転して見える"
    位置の復元で uv の y と NDC の y の向きの違いが抜けています。`ndc.y = 1 − 2v` にします。

??? failure "画面の端で AO が歪む"
    `tan(fov/2)` と `aspect` を取り違えているか掛け忘れています。縦の画角を使うなら横には `aspect` を掛けます。

??? failure "金属の隅だけまぶしく光る"
    スペキュラに遮蔽がかかっていません。粗さと `N·V` を使ったスペキュラ遮蔽を掛けます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] AO は可視性を切り離した近似で、成り立つのは一様な光とランバート面。間接拡散にだけ掛ける
    - [x] 明るいアルベドの隅は、多重反射の補正で戻す（論文の式 10）
    - [x] スペキュラ遮蔽は、粗さ 1 で AO のまま滑らかだと視線の向きで変わる
    - [x] 深度の式は標準 Z とリバース Z で別。間違えると 10 m が 0.101 m になる

## 参考 {#references}

読んだ範囲を書きます。

- Jorge Jimenez, Xian-Chun Wu, Angelo Pesce, Adrian Jarabo, "Practical Realtime Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016 Course: Physically Based Shading in Theory and Practice。コース ノートの 9 ページを読みました。4 章（見通しの扱い）、5 章（式 10 の多重反射）、6 章（GTSO、式 11〜21）、7 章（結果）です。付録 B（円錐の交差の計算）は読んでいません。
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014 Course Notes（v3.2）。4.10.1 節（拡散の遮蔽）と 4.10.2 節（スペキュラ遮蔽、リスト 26）を読みました。ほかの章は読んでいません。
- Morgan McGuire, "Ambient Occlusion Volumes", Proceedings of High Performance Graphics 2010。読んでいません。拡散の遮蔽の式は Frostbite の資料が引いたものを使いました。
- Yoshiharu Gotanda, "Real-time Physically Based Rendering", CEDEC 2013。読んでいません。スペキュラ遮蔽の考え方は Frostbite の資料の記述によります。
- Tomas Akenine-Möller ほか, "Real-Time Rendering", 4th Edition, CRC Press, 2018。読んでいません。

## 関連ページ {#related}

- [AO Artifacts](index.md)
- [Usage and Misconceptions of AO](../theory/usage-misconceptions.md)
- [GTAO](../gtao.md)
- [PBR](../../../3d/pbr.md)
