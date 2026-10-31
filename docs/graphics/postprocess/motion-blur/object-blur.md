---
title: Object Motion Blur
tags:
  - 描画
---

# Object Motion Blur

<strong>動く物体（走るキャラクター・飛ぶ弾・回るプロペラ）</strong>は、カメラが静止していても、動きに沿ってぶれます。オブジェクト モーション ブラーは、物体ごとの速度を速度バッファに書き込み、その速度に沿って、物体と周りをぼかすものです。カメラ ブラーに比べて、重く、破綻しやすいので実装の工夫が必要です。このページでは、物体の速度の出し方・回転する物体・スキニング・輪郭のにじみ・描画順・対象の絞り込みを説明します。

!!! tip "ポイント"
    - オブジェクト ブラー ＝ <strong>動く物体の速度</strong>に<strong>沿って、その物体（と周りの背景）をぼかす</strong>。
    - 速度は描画時に前フレームの行列で計算して、速度バッファへ（[Velocity Buffer](velocity-buffer.md)）。
    - 回転する物体（プロペラ・タイヤ）は頂点ごとに速度が違うので、頂点シェーダーで正しく計算。
    - キャラクターは前フレームの骨の姿勢が必要。
    - 速い物体の輪郭の外側にも、尾が伸びるように周りの速度を考慮（[Tile Max Velocity](tile-max.md)）。
    - 対象を絞る（重要な物体・プレイヤー周辺）とコストが下がる。

!!! info "このページを読む前に"
    - [Motion Blur](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 物体の速度

<strong>物体の各頂点について、前フレームの位置と今の位置を計算</strong>し、その差をピクセル シェーダーで速度として出力します（[Velocity Buffer](velocity-buffer.md)）。

動きの種類ごとの速度の特徴です。並進（移動）は、物体全体でほぼ一様です。回転（プロペラ・タイヤ）は、中心から遠い点ほど速く、頂点ごとに違います。変形（スキニング）は、骨ごとに違い、手足の先が速くなります。

物体全体で 1 つの速度だと、回転や変形が表現できません。頂点ごとの前フレームの位置から、画素ごとの速度を補間します。

<!-- fig:object-blur-rotation:begin -->

<svg class="fig illust motion" data-fig="object-blur-rotation" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-object-blur-rotation" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">回転する物のブラー: 先端ほど速く動く。直線で流すと、回転が大きいとき、先端が外れる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">プロペラの羽根(半径 1〜5)。1 フレームで回る角度を 10° → 30° → 60° → 90° に変える。円弧と、直線の差を測る</text>
<rect x="30" y="96" width="560" height="340" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 回る羽根の先端が通る道(青 = 円弧、赤 = 直線で流した場合)</text>
<circle cx="300.0" cy="290.0" r="6" fill="#1f2937"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="1;1;0;0"/><path d="M334.0,290.0 L334.0,289.67 L333.99,289.34 L333.99,289.01 L333.97,288.68 L333.96,288.35 L333.94,288.02 L333.92,287.69 L333.9,287.37 L333.87,287.04 L333.84,286.71 L333.81,286.38 L333.77,286.05 L333.73,285.73 L333.69,285.4 L333.64,285.07 L333.59,284.75 L333.54,284.42 L333.48,284.1" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="334.0" y1="290.0" x2="333.48" y2="284.1" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M368.0,290.0 L368.0,289.34 L367.99,288.68 L367.97,288.02 L367.95,287.36 L367.92,286.7 L367.88,286.05 L367.84,285.39 L367.8,284.73 L367.74,284.07 L367.68,283.42 L367.61,282.76 L367.54,282.11 L367.46,281.45 L367.37,280.8 L367.28,280.14 L367.18,279.49 L367.08,278.84 L366.97,278.19" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="368.0" y1="290.0" x2="366.97" y2="278.19" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M402.0,290.0 L402.0,289.01 L401.98,288.02 L401.96,287.03 L401.92,286.04 L401.88,285.06 L401.83,284.07 L401.77,283.08 L401.69,282.1 L401.61,281.11 L401.52,280.13 L401.42,279.14 L401.31,278.16 L401.19,277.18 L401.06,276.2 L400.92,275.22 L400.77,274.24 L400.62,273.26 L400.45,272.29" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="402.0" y1="290.0" x2="400.45" y2="272.29" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M436.0,290.0 L435.99,288.68 L435.97,287.36 L435.94,286.04 L435.9,284.73 L435.84,283.41 L435.77,282.09 L435.69,280.78 L435.59,279.46 L435.48,278.15 L435.36,276.83 L435.23,275.52 L435.08,274.21 L434.92,272.9 L434.75,271.59 L434.56,270.29 L434.37,268.99 L434.16,267.68 L433.93,266.38" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="436.0" y1="290.0" x2="433.93" y2="266.38" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M470.0,290.0 L469.99,288.35 L469.97,286.7 L469.93,285.06 L469.87,283.41 L469.8,281.76 L469.71,280.12 L469.61,278.47 L469.49,276.83 L469.35,275.18 L469.2,273.54 L469.03,271.9 L468.85,270.26 L468.65,268.63 L468.44,266.99 L468.21,265.36 L467.96,263.73 L467.7,262.1 L467.42,260.48" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="470.0" y1="290.0" x2="467.42" y2="260.48" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<line x1="300.0" y1="290.0" x2="470.0" y2="290.0" stroke="#64748b" stroke-width="3"/>
<text x="50" y="128" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">1 フレームで 10° 回る</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;0.4932;0.4933;1.0000" values="0;0;1;1;0;0"/><path d="M334.0,290.0 L333.99,289.01 L333.94,288.02 L333.87,287.04 L333.77,286.05 L333.64,285.07 L333.48,284.1 L333.3,283.12 L333.08,282.16 L332.84,281.2 L332.57,280.25 L332.27,279.31 L331.95,278.37 L331.6,277.45 L331.22,276.53 L330.81,275.63 L330.38,274.74 L329.93,273.86 L329.44,273.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="334.0" y1="290.0" x2="329.44" y2="273.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M368.0,290.0 L367.97,288.02 L367.88,286.05 L367.74,284.07 L367.54,282.11 L367.28,280.14 L366.97,278.19 L366.6,276.25 L366.17,274.32 L365.68,272.4 L365.14,270.5 L364.55,268.61 L363.9,266.74 L363.2,264.89 L362.44,263.07 L361.63,261.26 L360.77,259.48 L359.85,257.73 L358.89,256.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="368.0" y1="290.0" x2="358.89" y2="256.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M402.0,290.0 L401.96,287.03 L401.83,284.07 L401.61,281.11 L401.31,278.16 L400.92,275.22 L400.45,272.29 L399.89,269.37 L399.25,266.48 L398.52,263.6 L397.71,260.75 L396.82,257.92 L395.85,255.11 L394.79,252.34 L393.66,249.6 L392.44,246.89 L391.15,244.22 L389.78,241.59 L388.33,239.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="402.0" y1="290.0" x2="388.33" y2="239.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M436.0,290.0 L435.94,286.04 L435.77,282.09 L435.48,278.15 L435.08,274.21 L434.56,270.29 L433.93,266.38 L433.19,262.5 L432.33,258.64 L431.37,254.8 L430.29,250.99 L429.1,247.22 L427.8,243.49 L426.39,239.79 L424.88,236.13 L423.26,232.52 L421.53,228.96 L419.71,225.45 L417.78,222.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="436.0" y1="290.0" x2="417.78" y2="222.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M470.0,290.0 L469.93,285.06 L469.71,280.12 L469.35,275.18 L468.85,270.26 L468.21,265.36 L467.42,260.48 L466.49,255.62 L465.42,250.8 L464.21,246.0 L462.86,241.24 L461.37,236.53 L459.75,231.86 L457.99,227.23 L456.1,222.67 L454.07,218.15 L451.92,213.7 L449.63,209.32 L447.22,205.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="470.0" y1="290.0" x2="447.22" y2="205.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<line x1="300.0" y1="290.0" x2="470.0" y2="290.0" stroke="#64748b" stroke-width="3"/>
<text x="50" y="128" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">1 フレームで 30° 回る</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/><path d="M334.0,290.0 L333.94,288.02 L333.77,286.05 L333.48,284.1 L333.08,282.16 L332.57,280.25 L331.95,278.37 L331.22,276.53 L330.38,274.74 L329.44,273.0 L328.41,271.32 L327.27,269.7 L326.05,268.15 L324.73,266.67 L323.33,265.27 L321.85,263.95 L320.3,262.73 L318.68,261.59 L317.0,260.56" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="334.0" y1="290.0" x2="317.0" y2="260.56" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M368.0,290.0 L367.88,286.05 L367.54,282.11 L366.97,278.19 L366.17,274.32 L365.14,270.5 L363.9,266.74 L362.44,263.07 L360.77,259.48 L358.89,256.0 L356.81,252.63 L354.54,249.39 L352.09,246.29 L349.46,243.34 L346.66,240.54 L343.71,237.91 L340.61,235.46 L337.37,233.19 L334.0,231.11" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="368.0" y1="290.0" x2="334.0" y2="231.11" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M402.0,290.0 L401.83,284.07 L401.31,278.16 L400.45,272.29 L399.25,266.48 L397.71,260.75 L395.85,255.11 L393.66,249.6 L391.15,244.22 L388.33,239.0 L385.22,233.95 L381.82,229.09 L378.14,224.44 L374.19,220.0 L370.0,215.81 L365.56,211.86 L360.91,208.18 L356.05,204.78 L351.0,201.67" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="402.0" y1="290.0" x2="351.0" y2="201.67" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M436.0,290.0 L435.77,282.09 L435.08,274.21 L433.93,266.38 L432.33,258.64 L430.29,250.99 L427.8,243.49 L424.88,236.13 L421.53,228.96 L417.78,222.0 L413.63,215.27 L409.09,208.79 L404.18,202.58 L398.92,196.67 L393.33,191.08 L387.42,185.82 L381.21,180.91 L374.73,176.37 L368.0,172.22" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="436.0" y1="290.0" x2="368.0" y2="172.22" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M470.0,290.0 L469.71,280.12 L468.85,270.26 L467.42,260.48 L465.42,250.8 L462.86,241.24 L459.75,231.86 L456.1,222.67 L451.92,213.7 L447.22,205.0 L442.03,196.58 L436.36,188.48 L430.23,180.73 L423.65,173.34 L416.66,166.35 L409.27,159.77 L401.52,153.64 L393.42,147.97 L385.0,142.78" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="470.0" y1="290.0" x2="385.0" y2="142.78" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<line x1="300.0" y1="290.0" x2="470.0" y2="290.0" stroke="#64748b" stroke-width="3"/>
<text x="50" y="128" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">1 フレームで 60° 回る</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><path d="M334.0,290.0 L333.87,287.04 L333.48,284.1 L332.84,281.2 L331.95,278.37 L330.81,275.63 L329.44,273.0 L327.85,270.5 L326.05,268.15 L324.04,265.96 L321.85,263.95 L319.5,262.15 L317.0,260.56 L314.37,259.19 L311.63,258.05 L308.8,257.16 L305.9,256.52 L302.96,256.13 L300.0,256.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="334.0" y1="290.0" x2="300.0" y2="256.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M368.0,290.0 L367.74,284.07 L366.97,278.19 L365.68,272.4 L363.9,266.74 L361.63,261.26 L358.89,256.0 L355.7,251.0 L352.09,246.29 L348.08,241.92 L343.71,237.91 L339.0,234.3 L334.0,231.11 L328.74,228.37 L323.26,226.1 L317.6,224.32 L311.81,223.03 L305.93,222.26 L300.0,222.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="368.0" y1="290.0" x2="300.0" y2="222.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M402.0,290.0 L401.61,281.11 L400.45,272.29 L398.52,263.6 L395.85,255.11 L392.44,246.89 L388.33,239.0 L383.55,231.5 L378.14,224.44 L372.12,217.88 L365.56,211.86 L358.5,206.45 L351.0,201.67 L343.11,197.56 L334.89,194.15 L326.4,191.48 L317.71,189.55 L308.89,188.39 L300.0,188.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="402.0" y1="290.0" x2="300.0" y2="188.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M436.0,290.0 L435.48,278.15 L433.93,266.38 L431.37,254.8 L427.8,243.49 L423.26,232.52 L417.78,222.0 L411.4,211.99 L404.18,202.58 L396.17,193.83 L387.42,185.82 L378.01,178.6 L368.0,172.22 L357.48,166.74 L346.51,162.2 L335.2,158.63 L323.62,156.07 L311.85,154.52 L300.0,154.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="436.0" y1="290.0" x2="300.0" y2="154.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<path d="M470.0,290.0 L469.35,275.18 L467.42,260.48 L464.21,246.0 L459.75,231.86 L454.07,218.15 L447.22,205.0 L439.26,192.49 L430.23,180.73 L420.21,169.79 L409.27,159.77 L397.51,150.74 L385.0,142.78 L371.85,135.93 L358.14,130.25 L344.0,125.79 L329.52,122.58 L314.82,120.65 L300.0,120.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="470.0" y1="290.0" x2="300.0" y2="120.0" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="5 4"/>
<line x1="300.0" y1="290.0" x2="470.0" y2="290.0" stroke="#64748b" stroke-width="3"/>
<text x="50" y="128" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">1 フレームで 90° 回る</text>
</g>
<rect x="620" y="96" width="310" height="340" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="620" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">② 円弧と直線のずれ(矢高)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="1;1;0;0"/><text x="636" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 1</text>
<rect x="706" y="150" width="2" height="18" fill="#e5484d" opacity="0.85"/>
<text x="712.4157476282908" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.00</text>
<text x="636" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 2</text>
<rect x="706" y="200" width="2" height="18" fill="#e5484d" opacity="0.85"/>
<text x="712.8314952565815" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.01</text>
<text x="636" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 3</text>
<rect x="706" y="250" width="2" height="18" fill="#e5484d" opacity="0.85"/>
<text x="713.2472428848723" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.01</text>
<text x="636" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 4</text>
<rect x="706" y="300" width="2" height="18" fill="#e5484d" opacity="0.85"/>
<text x="713.6629905131631" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.02</text>
<text x="636" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 5</text>
<rect x="706" y="350" width="2.08" height="18" fill="#e5484d" opacity="0.85"/>
<text x="714.0787381414539" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.02</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;0.4932;0.4933;1.0000" values="0;0;1;1;0;0"/><text x="636" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 1</text>
<rect x="706" y="150" width="3.72" height="18" fill="#e5484d" opacity="0.85"/>
<text x="715.7227681923366" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.03</text>
<text x="636" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 2</text>
<rect x="706" y="200" width="7.45" height="18" fill="#e5484d" opacity="0.85"/>
<text x="719.4455363846732" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.07</text>
<text x="636" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 3</text>
<rect x="706" y="250" width="11.17" height="18" fill="#e5484d" opacity="0.85"/>
<text x="723.1683045770098" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.10</text>
<text x="636" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 4</text>
<rect x="706" y="300" width="14.89" height="18" fill="#e5484d" opacity="0.85"/>
<text x="726.8910727693466" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.14</text>
<text x="636" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 5</text>
<rect x="706" y="350" width="18.61" height="18" fill="#e5484d" opacity="0.85"/>
<text x="730.6138409616832" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.17</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/><text x="636" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 1</text>
<rect x="706" y="150" width="14.64" height="18" fill="#e5484d" opacity="0.85"/>
<text x="726.6373722692041" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.13</text>
<text x="636" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 2</text>
<rect x="706" y="200" width="29.27" height="18" fill="#e5484d" opacity="0.85"/>
<text x="741.2747445384082" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.27</text>
<text x="636" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 3</text>
<rect x="706" y="250" width="43.91" height="18" fill="#e5484d" opacity="0.85"/>
<text x="755.9121168076124" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.40</text>
<text x="636" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 4</text>
<rect x="706" y="300" width="58.55" height="18" fill="#e5484d" opacity="0.85"/>
<text x="770.5494890768165" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.54</text>
<text x="636" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 5</text>
<rect x="706" y="350" width="73.19" height="18" fill="#e5484d" opacity="0.85"/>
<text x="785.1868613460206" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.67</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><text x="636" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 1</text>
<rect x="706" y="150" width="32.0" height="18" fill="#e5484d" opacity="0.85"/>
<text x="744.0" y="164" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.29</text>
<text x="636" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 2</text>
<rect x="706" y="200" width="64.0" height="18" fill="#e5484d" opacity="0.85"/>
<text x="776.0" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.59</text>
<text x="636" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 3</text>
<rect x="706" y="250" width="96.0" height="18" fill="#e5484d" opacity="0.85"/>
<text x="808.0" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">0.88</text>
<text x="636" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 4</text>
<rect x="706" y="300" width="128.0" height="18" fill="#e5484d" opacity="0.85"/>
<text x="840.0" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">1.17</text>
<text x="636" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">半径 5</text>
<rect x="706" y="350" width="160.0" height="18" fill="#e5484d" opacity="0.85"/>
<text x="872.0" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">1.46</text>
</g>
<text x="40" y="470" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">先端(半径 5)のずれ:</text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2932;0.2933;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">17<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2932;0.2933;0.5065;0.5067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">67<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5065;0.5067;0.7198;0.7200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">146<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7198;0.7200;1.0000" values="0;0;1;1"/></text>
<text x="250" y="474" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(×0.01)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9020;0.9022;1.0000" values="0;0;1;1"/><rect x="360" y="456" width="570" height="64" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="376" y="480" text-anchor="start" style="font-size:13px;font-weight:700;fill:#166534">回転が小さい(10°)なら、直線で近似して十分(ずれ 0.02)</text>
<text x="376" y="502" text-anchor="start" style="font-size:13px;font-weight:700;fill:#991b1b">90° では、ずれ 1.46。サンプルを回転で曲げて取る方法もある</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">回転する物の、先端は、中心より速く動く<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">角度が大きくなると、円弧が曲がり、直線との差が広がる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.9198;0.9200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">速度バッファは直線の近似。大きな回転は、フレームを分けて描くなどで補う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9198;0.9200;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:object-blur-rotation:end -->

## 回転する物体

<strong>プロペラやタイヤ</strong>は、回転軸から離れた点ほど、大きな速度です。頂点シェーダーで前フレームの回転を適用した位置を計算すれば、自動的に頂点ごとの速度が得られます。

```hlsl
float4 current_position = mul(mul(float4(local_position, 1.0), world), view_projection);
float4 previous_position = mul(mul(float4(local_position, 1.0), previous_world), previous_view_projection);
```

注意：回転が大きい（1 フレームで 90° 以上）と、前後の位置の差が実際の弧の動きを表さず、速度の向きが不正確になります。速い回転はブラーを円弧に沿わせる特別な処理が必要です（多くのゲームは、回転の大きい物体のブラーを弱める）。

## スキニング

<strong>キャラクター</strong>は、骨の行列で頂点を動かす（スキニング）ので前フレームの骨の姿勢が必要です。

| 方式 | 内容 | コスト |
| --- | --- | --- |
| 前フレームのボーン行列で、もう一度スキニング | 頂点シェーダーで今・前の 2 回 | 頂点処理が 2 倍 |
| 前フレームのスキニング済み頂点を保存 | スキニング結果をバッファに保存し、次フレームに使う | メモリ ＋ 帯域 |
| コンピュートでスキニング | スキニングを事前に行い、今・前を保存（[スキニングとアニメーション](../../../3d/skinning-animation.md)） | 一括で軽い |

## 輪郭の外側に伸びる尾

<strong>速い物体の輪郭の外側（背景）にもぼけた尾が伸びる</strong>べきです。物体の画素の速度だけを使うと、物体の縁でぼかしが急にぷつっと切れます。

物体の輪郭に関する問題と対処です。物体の周りの背景がぼけない問題には、周りの画素のうち最も速い物体の速度をその画素も使います（タイルの最大速度、近傍最大。[Tile Max Velocity](tile-max.md)）。ぼけた物体の縁がくっきりする問題には、深度と速度で重みを付けてサンプルを集めます（[Blur Pass Implementation](blur-pass.md)）。

## 描画順と透明物

<strong>半透明の物体</strong>は、速度バッファに書き込めない（背景の速度が上書きされる）ことが多いので扱いに注意します。

| 対象 | 扱い |
| --- | --- |
| 不透明 | 速度を書く |
| 半透明 | 速度を書かない、または別パスで後処理の前に近似 |
| パーティクル | ストレッチ ビルボードなど、速度を表す形そのものに。ブラーの対象外に |
| UI | ブラーの対象外（ポストプロセスの後に描く） |

## 対象を絞る

<strong>すべての動く物をブラーする</strong>と重く、不自然な場合があります。

| 工夫 | 内容 |
| --- | --- |
| 重要な動きだけ | プレイヤー・敵・乗り物・弾 |
| 遠い物体を除外 | 画面上で小さい物は、ブラーが見えない |
| 速度の閾値以下は 0 | ほぼ止まっている物にコストをかけない |
| マテリアルのフラグ | ブラーを掛けない物（武器・UI・遠景）を除外 |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| カメラ ブラー優先 | まずカメラ。オブジェクトは必要なものだけ |
| 回転の大きい物は弱める | プロペラなど、速度の向きが当てにならない物は、別途処理 |
| 前フレームの頂点位置を保存 | スキニング・変形でも正確な速度 |
| 近傍最大の速度でぼかす | 輪郭の外側にも尾が伸びる |
| TAA の速度バッファと共有 | 同じバッファを使う |
| 速度の上限を設ける | 速すぎる物で画面が崩れない |

## よくあるミス

??? failure "物体のブラーが輪郭でぷつっと切れる"
    <strong>近傍の最大速度（タイル）</strong>を使い、サンプルの重み付けをする。

??? failure "プロペラのブラーがぐちゃぐちゃになる"
    回転が大きい物体は、速度の向きが不正確。ブラーを弱める・別処理。

??? failure "キャラクターの手足にブラーが無い"
    スキニングの前フレームの姿勢が無く、速度が 0。前フレームのボーンで再計算。

??? failure "半透明の物体が背景の速度を上書きして、ブラーがおかしい"
    半透明は速度を書かない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] オブジェクト ブラー ＝ <strong>動く物体の速度に沿ってぼかす</strong>
    - [x] 頂点ごとに前フレームの位置から速度。回転・スキニングも
    - [x] 輪郭の外にも尾が伸びるよう近傍の最大速度を使う
    - [x] 半透明・パーティクル・UI は対象外が基本
    - [x] 重要な物体だけに絞ってコストと破綻を減らす

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Camera Motion Blur](camera-blur.md)
- [スキニングとアニメーション](../../../3d/skinning-animation.md)
