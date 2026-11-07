---
title: Object Motion Blur
tags:
  - 描画
---

# Object Motion Blur

カメラが止まっていても走るキャラクターや飛んでいく弾はぶれて見えます。回るプロペラは羽根が円盤になって見えます。カメラ ブラーは画面全体を同じ規則で流せば済みますが、物体のブラーは物体ごとに速度が違うので、速度を画素ごとに持つ必要があります。このページではその速度をどう作るか（剛体、回転、スキニング）、回転が大きいとなぜ破綻するか輪郭の外の尾をどう伸ばすかどの物体をブラーの対象にするかを、数字で確かめながら説明します。最後に、速度を書く頂点・ピクセルシェーダー、シャッターとクランプ、タイルの最大速度を求めるコンピュート シェーダーを 1 本にまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`vs_5_0` / `ps_5_0` / `cs_5_0`）に通しましたが、描画した結果は確かめていません。末尾の論文・発表は今回は読んでいないので、タイルの最大速度などは自分で導いた考え方として書きます。

!!! tip "ポイント"
    - 速度は同じ頂点を前フレームの行列でもう一度変換して、その差を取ります。回転・スキニングもこの方法で頂点ごとの速度になります。
    - 位置の差は弦の長さです。1 フレームで 90° 回ると、弧の長さの 90%（1.414 / 1.571）、180° で 63.7%、360° ではちょうど 0 になります。2400 rpm のプロペラは 60 fps で 1 フレーム 240° 回り、速度バッファの向きが信用できません。
    - ブラーの長さは `1 フレームの移動 × k` です。k はシャッター（露光時間 ÷ フレーム時間）で、シャッター角 180° なら 0.5 です。
    - 横に 10 m/s で動く物体は、距離 10 m で 1 フレーム 15.59 画素動きブラーは 7.79 画素です。距離 50 m で 1.56 画素、156 m を超えると 0.5 画素を切って見えなくなります。
    - 輪郭の外の尾は近傍の最大速度（タイル）で作ります。タイルの大きさをブラーの最大半径にそろえると、読むのは 3×3 のタイルだけで済みます。

!!! info "このページを読む前に"
    - [Motion Blur](index.md)（このセクション全体の地図と読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 物体の速度 {#velocity}

### 同じ頂点を前の行列で変換する {#same-vertex}

物体の速度は各頂点について前フレームの画面位置から今の画面位置への移動です。頂点シェーダーで同じ頂点を今の行列と前フレームの行列の両方で変換し、クリップ座標を 2 つ出力します。ピクセル シェーダーで `w` で割って NDC にし、差を取って画素に直します（コードは後の節にあります）。動きの種類ごとの特徴は次のとおりです。

- 並進（移動）: 物体全体でほぼ一様です。
- 回転（プロペラ、タイヤ）: 中心から遠い点ほど速く、頂点ごとに違います。
- 変形（スキニング）: 骨ごとに違い手足の先が速くなります。

物体全体で 1 つの速度を持つ方式だと回転や変形が表現できません。頂点ごとの前フレームの位置を使いラスタライザーに補間させると、画素ごとの速度になります。

### TAA のジッターは含めない {#jitter}

TAA を使うゲームは射影行列にサブピクセルのジッターを足して、フレームごとに画面を少しずつずらします。速度を求めるときにこのジッターを含めた行列を使うと静止している物体にもジッターの差分の速度が出て、全体がぶれます。速度を出す行列はジッターを足す前のものを使います。TAA と速度バッファを共有する場合も同じで、ジッターなしの位置の差を保存し、TAA の側が必要ならジッターの差を足します（[Velocity Buffer](velocity-buffer.md)）。

## 回転する物体 {#rotation}

### 弧と弦 {#arc-chord}

プロペラやタイヤは回転軸から離れた点ほど速く動きます。頂点シェーダーで前フレームの回転を適用した位置を計算すれば、頂点ごとの速度が自動的に得られます。ところが、速度は「前の位置から今の位置への差」なので、得られるのは弦の長さです。実際に点が通った道は円弧で 1 フレームで回る角度が大きいほど弧と弦は離れます。半径 1 の点について数えました。

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

上の動く図は半径 1 から 5 の羽根について、円弧と直線のずれ（矢高）を並べたものです。矢高は `r (1 − cos(θ/2))` で半径 5、90° なら 1.46 です。図には 360° までは出ていないので、次の図で弧と弦の長さそのものを並べます。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="弧と弦"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">回転角と、弧・弦の長さ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 76.9,247.4 83.9,244.9 90.8,242.3 97.8,239.8 104.7,237.2 111.7,234.7 118.6,232.1 125.6,229.6 132.5,227.0 139.4,224.5 146.4,221.9 153.3,219.4 160.3,216.8 167.2,214.3 174.2,211.7 181.1,209.2 188.1,206.6 195.0,204.1 201.9,201.5 208.9,199.0 215.8,196.4 222.8,193.9 229.7,191.3 236.7,188.8 243.6,186.2 250.6,183.7 257.5,181.1 264.4,178.6 271.4,176.0 278.3,173.5 285.3,170.9 292.2,168.4 299.2,165.8 306.1,163.3 313.1,160.7 320.0,158.2 326.9,155.6 333.9,153.1 340.8,150.5 347.8,148.0 354.7,145.4 361.7,142.9 368.6,140.3 375.6,137.8 382.5,135.2 389.4,132.7 396.4,130.1 403.3,127.6 410.3,125.0 417.2,122.5 424.2,119.9 431.1,117.4 438.1,114.8 445.0,112.3 451.9,109.7 458.9,107.2 465.8,104.6 472.8,102.0 479.7,99.5 486.7,96.9 493.6,94.4 500.6,91.8 507.5,89.3 514.4,86.7 521.4,84.2 528.3,81.6 535.3,79.1 542.2,76.5 549.2,74.0 556.1,71.4 563.1,68.9 570.0,66.3"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,250.0 76.9,247.4 83.9,244.9 90.8,242.4 97.8,239.8 104.7,237.3 111.7,234.9 118.6,232.4 125.6,230.0 132.5,227.6 139.4,225.3 146.4,223.0 153.3,220.8 160.3,218.6 167.2,216.5 174.2,214.4 181.1,212.4 188.1,210.5 195.0,208.7 201.9,206.9 208.9,205.2 215.8,203.6 222.8,202.1 229.7,200.7 236.7,199.4 243.6,198.1 250.6,197.0 257.5,196.0 264.4,195.1 271.4,194.2 278.3,193.5 285.3,192.9 292.2,192.4 299.2,192.0 306.1,191.8 313.1,191.6 320.0,191.5 326.9,191.6 333.9,191.8 340.8,192.0 347.8,192.4 354.7,192.9 361.7,193.5 368.6,194.2 375.6,195.1 382.5,196.0 389.4,197.0 396.4,198.1 403.3,199.4 410.3,200.7 417.2,202.1 424.2,203.6 431.1,205.2 438.1,206.9 445.0,208.7 451.9,210.5 458.9,212.4 465.8,214.4 472.8,216.5 479.7,218.6 486.7,220.8 493.6,223.0 500.6,225.3 507.5,227.6 514.4,230.0 521.4,232.4 528.3,234.9 535.3,237.3 542.2,239.8 549.2,242.4 556.1,244.9 563.1,247.4 570.0,250.0"/><text x="417.22222222222223" y="101.53846153846155" text-anchor="start" style="font-size:12px;font-weight:700">弧の長さ(実際に動いた道のり)</text><text x="333.8888888888889" y="236.9230769230769" text-anchor="start" style="font-size:12px;font-weight:700">位置の差(速度バッファが見る長さ)</text><circle cx="195.0" cy="208.7" r="4" fill="#e5484d"/><text x="201.0" y="200.6676923076923" text-anchor="start" style="font-size:11px;font-weight:700">1.41</text><circle cx="320.0" cy="191.5" r="4" fill="#e5484d"/><text x="326.0" y="183.53846153846155" text-anchor="start" style="font-size:11px;font-weight:700">2.00</text><circle cx="570.0" cy="250.0" r="4" fill="#e5484d"/><text x="576.0" y="242.0" text-anchor="start" style="font-size:11px;font-weight:700">0.00</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90°</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">180°</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">270°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">360°</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="195.53846153846155" text-anchor="end" style="font-size:11px;font-weight:400">2</text><text x="62" y="137.0769230769231" text-anchor="end" style="font-size:11px;font-weight:400">4</text><text x="62" y="78.61538461538461" text-anchor="end" style="font-size:11px;font-weight:400">6</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">1 フレームで回る角度(半径 1)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">長さ(半径を 1 とする)</text></svg>

- 10°: 弧 0.175、弦 0.174（弦 ÷ 弧 = 0.999）
- 30°: 弧 0.524、弦 0.518（0.989）
- 60°: 弧 1.047、弦 1.000（0.955）
- 90°: 弧 1.571、弦 1.414（0.900）
- 120°: 弧 2.094、弦 1.732（0.827）
- 180°: 弧 3.142、弦 2.000（0.637）
- 240°: 弧 4.189、弦 1.732（0.413）
- 330°: 弧 5.760、弦 0.518（0.090）
- 360°: 弧 6.283、弦 0.000（0.000）

60° までは弦と弧の差は 5% 以内で、直線のブラーで十分です。90° で弦が 10% 短くなり 120° 以上では、速度の向きも弧の接線から大きくずれます。180° を超えると弦は短くなっていき 360° でちょうど 0 になります。1 回転した点は同じ場所に戻ってきたので、位置の差が 0 です。映画で車輪が止まって見える現象と同じ原因で、速度バッファから見ると一番速い物体の速度が 0 になります。

### 実際の回転数だと {#real-rpm}

プロペラが 2400 rpm なら 1 秒に 40 回転です。1 フレームで回る角度は 30 fps で 480°（1 回転と 120°）、60 fps で 240°、120 fps で 120° です。先端の速さは半径 0.5 m で 125.7 m/s です。60 fps でも 240° 回るので、弦は半径の 1.732 倍で、弧の 41% しかありません。時速 100 km で走る半径 0.35 m のタイヤは、60 fps で 1 フレーム 75.8° なので、弦と弧の差は 10% 程度に収まり直線で何とかなります。30 fps だと 151.6° で、差は 25% ほどに広がります。

### 対処 {#rotation-fix}

多くのゲームは回転の大きい物体のブラーを弱めるか別の処理にします。

1. 角度が大きいとき（例: 90° を超えるとき）は、速度を 0 にしてブラーを掛けません。破綻した速度でぼかすよりきれいに見えます。
2. プロペラのような決まった物は専用のメッシュ（半透明の円盤）に差し替えます。止まっている羽根と高速で回る羽根のメッシュを回転数で切り替えます。
3. ブラーの向きを弦ではなく、回転軸と半径から求めた接線にします。頂点シェーダーで物体の角速度から接線方向の速度を計算します。

どの方法でも「速度の向きが信用できない」と判定する条件を決めておくことが大切です。

## スキニング {#skinning}

### 前の骨でもう一度スキニングする {#skin-twice}

キャラクターは骨の行列で頂点を動かします（スキニング）。速度を出すには前フレームの骨の姿勢が必要です。方法は 3 つあります。

- 前フレームの骨の行列で頂点シェーダーがもう一度スキニングする。頂点処理が 2 倍になります。
- 前フレームのスキニング済みの頂点位置をバッファに保存して使う。メモリと帯域が増えます。
- コンピュート シェーダーで先にスキニングして、今と前を保存する（[スキニングとアニメーション](../../../3d/skinning-animation.md)）。1 度の計算で済みます。

### コストの見積もり {#skin-cost}

頂点 5 万のキャラクターで、スキニング済みの位置（`float3` = 12 バイト）を保存すると、1 フレーム分が 586 KiB、今と前で 1172 KiB です。骨の行列は 4×4 を 64 バイトとして、80 本で 5.00 KiB、今と前で 10.00 KiB、128 本で 16.00 KiB です。ブラーのために骨の行列を 1 フレーム分余分に残しておく（前フレームの骨の行列）のは、メモリの面では軽く頂点シェーダーが 2 回スキニングする頂点処理のほうが負担です。キャラクターが画面に多いときはこの頂点処理 2 倍が効いてきます。

## ブラーの長さ {#length}

### シャッター {#shutter}

速度は 1 フレームの移動量ですが、カメラが光を取り込むのはフレームの間のうち露光している時間だけです。露光時間を 1 フレームの割合 `k` とすると、ブラーの長さは `k × 1 フレームの移動` です。映画のシャッター角で言うと 180° が `k = 0.5` です。60 fps（1 フレーム 16.67 ms）で、シャッター角 90°、180°、270°、360° の露光時間は 4.17 ms、8.33 ms、12.50 ms、16.67 ms です。ゲームでは k をフレームレートに依存させないことが大切で、`k = 露光時間 ÷ フレーム時間` で計算すると 30 fps と 60 fps で同じ長さの「実時間のブラー」になります。

### 距離で小さくなる {#distance}

ブラーの長さは画面上の移動量なので、距離に反比例して小さくなります。縦 FOV 60°、1080p なら焦点距離は画素単位で `540 / tan 30° = 935.3` です。横に `v` m/s で動く物体が距離 `z` m にあるとき 1 フレームの移動は `935.3 × v / z / fps` 画素です。60 fps、k = 0.5 で数えました。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="距離とブラー"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">距離とブラーの長さ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="95.0,238.2 100.0,240.1 105.0,241.5 110.0,242.6 115.0,243.4 120.0,244.1 125.0,244.6 130.0,245.1 135.0,245.4 140.0,245.8 145.0,246.1 150.0,246.3 155.0,246.5 160.0,246.7 165.0,246.9 170.0,247.0 175.0,247.2 180.0,247.3 185.0,247.4 190.0,247.5 195.0,247.6 200.0,247.7 205.0,247.8 210.0,247.9 215.0,248.0 220.0,248.0 225.0,248.1 230.0,248.1 235.0,248.2 240.0,248.3 245.0,248.3 250.0,248.4 255.0,248.4 260.0,248.4 265.0,248.5 270.0,248.5 275.0,248.6 280.0,248.6 285.0,248.6 290.0,248.7 295.0,248.7 300.0,248.7 305.0,248.7 310.0,248.8 315.0,248.8 320.0,248.8 325.0,248.8 330.0,248.9 335.0,248.9 340.0,248.9 345.0,248.9 350.0,248.9 355.0,249.0 360.0,249.0 365.0,249.0 370.0,249.0 375.0,249.0 380.0,249.0 385.0,249.1 390.0,249.1 395.0,249.1 400.0,249.1 405.0,249.1 410.0,249.1 415.0,249.1 420.0,249.2 425.0,249.2 430.0,249.2 435.0,249.2 440.0,249.2 445.0,249.2 450.0,249.2 455.0,249.2 460.0,249.2 465.0,249.3 470.0,249.3 475.0,249.3 480.0,249.3 485.0,249.3 490.0,249.3 495.0,249.3 500.0,249.3 505.0,249.3 510.0,249.3 515.0,249.3 520.0,249.3 525.0,249.3 530.0,249.4 535.0,249.4 540.0,249.4 545.0,249.4 550.0,249.4 555.0,249.4 560.0,249.4 565.0,249.4 570.0,249.4"/><text x="576" y="253.40764333333334" text-anchor="start" style="font-size:11px;font-weight:700">2 m/s</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="95.0,190.8 100.0,200.6 105.0,207.7 110.0,213.0 115.0,217.1 120.0,220.4 125.0,223.1 130.0,225.3 135.0,227.2 140.0,228.8 145.0,230.3 150.0,231.5 155.0,232.6 160.0,233.5 165.0,234.4 170.0,235.2 175.0,235.9 180.0,236.5 185.0,237.1 190.0,237.7 195.0,238.2 200.0,238.6 205.0,239.0 210.0,239.4 215.0,239.8 220.0,240.1 225.0,240.4 230.0,240.7 235.0,241.0 240.0,241.3 245.0,241.5 250.0,241.8 255.0,242.0 260.0,242.2 265.0,242.4 270.0,242.6 275.0,242.8 280.0,242.9 285.0,243.1 290.0,243.3 295.0,243.4 300.0,243.6 305.0,243.7 310.0,243.8 315.0,244.0 320.0,244.1 325.0,244.2 330.0,244.3 335.0,244.4 340.0,244.5 345.0,244.6 350.0,244.7 355.0,244.8 360.0,244.9 365.0,245.0 370.0,245.1 375.0,245.1 380.0,245.2 385.0,245.3 390.0,245.4 395.0,245.4 400.0,245.5 405.0,245.6 410.0,245.6 415.0,245.7 420.0,245.8 425.0,245.8 430.0,245.9 435.0,245.9 440.0,246.0 445.0,246.1 450.0,246.1 455.0,246.2 460.0,246.2 465.0,246.3 470.0,246.3 475.0,246.3 480.0,246.4 485.0,246.4 490.0,246.5 495.0,246.5 500.0,246.6 505.0,246.6 510.0,246.6 515.0,246.7 520.0,246.7 525.0,246.7 530.0,246.8 535.0,246.8 540.0,246.8 545.0,246.9 550.0,246.9 555.0,246.9 560.0,247.0 565.0,247.0 570.0,247.0"/><text x="576" y="251.03821666666667" text-anchor="start" style="font-size:11px;font-weight:700">10 m/s</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="95.0,72.3 100.0,101.9 105.0,123.1 110.0,138.9 115.0,151.3 120.0,161.1 125.0,169.2 130.0,176.0 135.0,181.7 140.0,186.5 145.0,190.8 150.0,194.5 155.0,197.7 160.0,200.6 165.0,203.2 170.0,205.6 175.0,207.7 180.0,209.6 185.0,211.4 190.0,213.0 195.0,214.5 200.0,215.8 205.0,217.1 210.0,218.3 215.0,219.4 220.0,220.4 225.0,221.3 230.0,222.2 235.0,223.1 240.0,223.9 245.0,224.6 250.0,225.3 255.0,226.0 260.0,226.6 265.0,227.2 270.0,227.8 275.0,228.3 280.0,228.8 285.0,229.3 290.0,229.8 295.0,230.3 300.0,230.7 305.0,231.1 310.0,231.5 315.0,231.9 320.0,232.2 325.0,232.6 330.0,232.9 335.0,233.2 340.0,233.5 345.0,233.8 350.0,234.1 355.0,234.4 360.0,234.7 365.0,234.9 370.0,235.2 375.0,235.4 380.0,235.7 385.0,235.9 390.0,236.1 395.0,236.3 400.0,236.5 405.0,236.7 410.0,236.9 415.0,237.1 420.0,237.3 425.0,237.5 430.0,237.7 435.0,237.8 440.0,238.0 445.0,238.2 450.0,238.3 455.0,238.5 460.0,238.6 465.0,238.8 470.0,238.9 475.0,239.0 480.0,239.2 485.0,239.3 490.0,239.4 495.0,239.5 500.0,239.7 505.0,239.8 510.0,239.9 515.0,240.0 520.0,240.1 525.0,240.2 530.0,240.3 535.0,240.4 540.0,240.5 545.0,240.6 550.0,240.7 555.0,240.8 560.0,240.9 565.0,241.0 570.0,241.1"/><text x="576" y="245.11465" text-anchor="start" style="font-size:11px;font-weight:700">30 m/s</text><line x1="70" y1="248.1" x2="570" y2="248.1" stroke="currentColor" stroke-dasharray="5 4"/><text x="566" y="242.1" text-anchor="end" style="font-size:11px;font-weight:400">0.5 px(見えない)</text><line x1="70" y1="174.0" x2="570" y2="174.0" stroke="currentColor" stroke-dasharray="5 4" opacity="0.6"/><text x="566" y="168.0" text-anchor="end" style="font-size:11px;font-weight:400">最大半径 20 px</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">50</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">75</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">100</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="216.0" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="62" y="178.0" text-anchor="end" style="font-size:11px;font-weight:400">20</text><text x="62" y="140.0" text-anchor="end" style="font-size:11px;font-weight:400">30</text><text x="62" y="102.0" text-anchor="end" style="font-size:11px;font-weight:400">40</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">50</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">物体までの距離 z(m)。横に動く物体、縦 FOV 60°、1080p、60 fps、k = 0.5</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">ブラーの長さ(画素。上は 50 で打ち切り)</text></svg>

- 2 m/s（歩行）: 距離 5 m で 3.12 画素、10 m で 1.56、25 m で 0.62、50 m で 0.31
- 10 m/s（走る・投げる）: 5 m で 15.59 画素、10 m で 7.79、25 m で 3.12、50 m で 1.56、100 m で 0.78
- 30 m/s（乗り物）: 5 m で 46.77 画素、10 m で 23.38、25 m で 9.35、50 m で 4.68、100 m で 2.34

0.5 画素を切るとブラーは見えません。その距離は 2 m/s で 31.2 m、10 m/s で 155.9 m、30 m/s で 467.7 m です。ここを閾値にしてブラーを掛けない（速度を 0 にする）と遠くの物体にコストを掛けなくて済みます。逆に、30 m/s の乗り物が距離 5 m にいると、47 画素もぶれます。これは最大半径（例: 20 画素）を大きく超えるので、クランプします。

## 輪郭の外側に伸びる尾 {#silhouette}

### 自分の速度だけだと縁で切れる {#cut}

速い物体の輪郭の外側の背景も物体が通ったあとの尾として、ぼけるべきです。ところが、各画素が自分の速度だけでぼかすと物体の外の画素は速度が 0 で、ぼけません。物体の中だけがぼけて縁でぷつっと切れます。

<svg class="fig flow" viewBox="0 0 660 270" role="img" aria-label="輪郭の尾"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">輪郭の外のブラー</text><text x="20" y="22" text-anchor="start" style="font-size:14px;font-weight:700">右へ動く物体(青)と、その輪郭の外のブラー(黄)</text><text x="20" y="60" text-anchor="start" style="font-size:13px;font-weight:700">自分の速度だけ</text><rect x="150" y="40" width="480" height="40" fill="rgba(150,150,150,0.15)" stroke="currentColor" stroke-width="1"/><rect x="390" y="40" width="40" height="40" fill="rgba(76,139,245,0.55)" stroke="currentColor" stroke-width="1.5"/><line x1="390" y1="95" x2="300" y2="95" stroke="currentColor" stroke-width="2"/><text x="150" y="128" text-anchor="start" style="font-size:11px;font-weight:400">輪郭の外の画素は速度 0。物体の中だけがぼけ、縁でぷつっと切れる</text><text x="20" y="180" text-anchor="start" style="font-size:13px;font-weight:700">近傍の最大速度</text><rect x="150" y="160" width="480" height="40" fill="rgba(150,150,150,0.15)" stroke="currentColor" stroke-width="1"/><rect x="270" y="160" width="120" height="40" fill="rgba(229,170,40,0.30)"/><rect x="430" y="160" width="120" height="40" fill="rgba(229,170,40,0.30)"/><rect x="390" y="160" width="40" height="40" fill="rgba(76,139,245,0.55)" stroke="currentColor" stroke-width="1.5"/><line x1="390" y1="215" x2="300" y2="215" stroke="currentColor" stroke-width="2"/><text x="150" y="248" text-anchor="start" style="font-size:11px;font-weight:400">輪郭の外の画素も、近くの速い物体の速度で尾を引く</text><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="410" y1="40" x2="500" y2="40" stroke="currentColor" stroke-width="2" marker-end="url(#ar)" transform="translate(0,-8)"/></svg>

### 近傍の最大速度 {#tile-max}

輪郭の外の画素にも近くにある速い物体の速度を使います。画面をタイルに分けタイルごとに最大の速度を求めておき各画素は周りのタイルの最大速度を見て、「自分のところへ尾が伸びてくるか」を判断します。

タイルの大きさはブラーの最大半径に合わせます。半径 `R` 画素より遠い物体の速度はこの画素に影響しないので、タイルの大きさが `R` なら影響する物体は、自分のタイルと隣接する 8 個のタイル（合計 3×3）に必ず入ります。読む回数は画素あたり 9 回で、`R` によらず一定です。1080p でタイルが 20×20 ならタイルの数は 96 × 54 = 5184 個で、R16G16 なら 20.2 KiB です。

タイルの最大速度は画素の速度を 2 乗の長さで比べて、大きい方を残します。ここでは、読む側の `BlurVector` を通した後の速度（シャッターを掛けクランプした後）で比べます。ブラーの最大半径が 20 画素で、速度が大きい物体がタイルに入っていれば、そのタイルは 20 画素にクランプされた最大の速度を持ちます。

### 周りの画素を集めるときの重み {#weights}

最大速度のタイルで「尾が伸びる」と分かっても、実際にぼかすときは周りの画素のうちどれが自分に影響するかを決めます。深度と速度で重みを付けて手前の物体が奥にあるものを覆ったり奥の画素が手前に染み出したりしないようにします（[Blur Pass Implementation](blur-pass.md)）。

### ぼかす回数 {#taps}

1 画素刻みで取ると半径 `R` のブラーは `2R + 1` 点が要ります。`R = 8` で 17 点、16 で 33 点、20 で 41 点、40 で 81 点です。12 点に間引くと取る間隔は `2R / 12` 画素で、`R = 20` で 3.33 画素、`R = 40` で 6.67 画素になり間隔が広がるほど縞（バンディング）が出ます。これを避けるため取る位置を画素ごとにずらす（ジッターを入れる）か点の数を増やします。

## 速度バッファの精度 {#precision}

速度バッファの形式は読み書きの帯域と精度のトレードオフです。1080p で R8G8 は 3.96 MiB、R16G16 は 7.91 MiB です。±20 画素の範囲を 8 ビット（256 段階）で表すと刻みは 0.157 画素です。ブラーの長さの誤差としては小さいですが、向きの精度は速度が小さいときに崩れます（速度が 1 画素なら向きの角度が 8 ビットの刻みで大きくずれます）。16 ビットの SNORM なら刻みは 0.000610 画素です。

TAA と共有する場合は 0.1 画素以下の動きを区別したいので、16 ビット（`R16G16_FLOAT` か `R16G16_SNORM`）を使います。ブラーだけなら 8 ビットで足ります。クランプの範囲を狭く（16 画素など）すると、刻みが細かくなります。

## 描画順と透明物 {#order}

半透明の物体は速度バッファに書くと後ろにある不透明な物体の速度を上書きします。結果として、背景がその半透明の物体の速度でぶれて、おかしくなります。基本的な扱いは次のとおりです。

- 不透明: 速度を書きます。
- 半透明: 速度を書かないか後処理の前の別のパスで近似します。
- パーティクル: ストレッチ ビルボードなど速度を表す形そのものにして、ブラーの対象外にします。
- UI: ポストプロセスのあとに描くので、ブラーの対象外です。

## 対象を絞る {#budget}

動く物のすべてをブラーすると重く、不自然になる場合があります。対象を絞る基準は次のとおりです。

- 重要な動きだけ: プレイヤー、敵、乗り物、弾に限ります。
- 遠い物体を除外: 画面上で小さい物は、ブラーが見えません。前の節で数えたように 10 m/s なら 156 m より遠くは 0.5 画素未満です。
- 速度の閾値以下は 0: ほぼ止まっている物にコストを掛けません。
- マテリアルのフラグ: ブラーを掛けない物（武器、UI、遠景）を除外します。
- 速度の上限: 速すぎる物で画面が崩れないよう最大半径で頭打ちにします。

## 速度を書くコード {#code}

ここからコードを数行ずつ見ます。最初は定数バッファと頂点の入出力です。

```hlsl
cbuffer FrameCB : register(b0) {
  float4x4 gViewProj;         // 今フレームのビュー × 射影（TAA のジッターは含めない）
  float4x4 gPrevViewProj;     // 前フレームのビュー × 射影（同じくジッターなし）
  float2   gScreenSize;       // 画面の幅と高さ（画素）
  float    gShutter;          // シャッター k。露光時間 ÷ フレーム時間。180° シャッターなら 0.5
  float    gMaxBlurPx;        // ブラーの最大半径（画素）。タイルの大きさにも使う。例: 20
};

cbuffer ObjectCB : register(b1) {
  float4x4 gWorld;            // 今フレームのワールド行列
  float4x4 gPrevWorld;        // 前フレームのワールド行列（動かない物体は gWorld と同じ値）
};

cbuffer SkinCB : register(b2) {
  float4x4 gBones[128];       // 今フレームの骨の行列（バインド姿勢の逆行列を掛け済み）
  float4x4 gPrevBones[128];   // 前フレームの骨の行列。1 フレーム分保存しておく
};

struct VsIn {
  float3 pos     : POSITION;
  float4 weights : BLENDWEIGHT;      // 骨 4 本分の重み（合計 1）
  uint4  indices : BLENDINDICES;     // 骨の番号
};

struct VsOut {
  float4 pos      : SV_Position;
  float4 cur_clip : TEXCOORD0;       // 今フレームのクリップ座標（補間して PS で割る）
  float4 prev_clip: TEXCOORD1;       // 前フレームのクリップ座標
};
```

`gViewProj` と `gPrevViewProj` は TAA のジッターを足す前の行列です。`gShutter` が k、`gMaxBlurPx` が最大半径です。`gPrevWorld` は動かない物体では `gWorld` と同じ値を入れます。骨の行列は前フレーム分を 1 フレーム分余分に保存します。`VsOut` が今と前のクリップ座標を 2 つ持つのが、速度を出す方式の要です。

剛体（回転・並進だけの物体）の頂点シェーダーです。

```hlsl
// 剛体（回転・並進だけの物体。プロペラ、タイヤ、弾）。
VsOut VelocityRigidVS(float3 pos : POSITION) {
  VsOut o;
  float4 world = mul(float4(pos, 1.0), gWorld);              // 今のワールド位置
  float4 prev_world = mul(float4(pos, 1.0), gPrevWorld);     // 前フレームのワールド位置（同じ頂点を前の行列で）
  o.cur_clip = mul(world, gViewProj);                         // 今のクリップ座標
  o.prev_clip = mul(prev_world, gPrevViewProj);               // 前のクリップ座標
  o.pos = o.cur_clip;                                         // ラスタライズには今の位置を使う
  return o;
}
```

同じ `pos` を今の `gWorld` と前の `gPrevWorld` で変換します。回転するプロペラも前フレームの回転を持った `gPrevWorld` を渡すだけで、頂点ごとの速度になります。ラスタライズに使う `o.pos` は今の位置です。

スキニングした物体の頂点シェーダーです。

```hlsl
// スキニングした物体。今の骨と前の骨で、同じ頂点を 2 回スキニングする。
VsOut VelocitySkinnedVS(VsIn i) {
  float4x4 skin = gBones[i.indices.x] * i.weights.x + gBones[i.indices.y] * i.weights.y +
                  gBones[i.indices.z] * i.weights.z + gBones[i.indices.w] * i.weights.w;           // 今の姿勢
  float4x4 prev_skin = gPrevBones[i.indices.x] * i.weights.x + gPrevBones[i.indices.y] * i.weights.y +
                       gPrevBones[i.indices.z] * i.weights.z + gPrevBones[i.indices.w] * i.weights.w;  // 前の姿勢
  VsOut o;
  float4 world = mul(mul(float4(i.pos, 1.0), skin), gWorld);               // 今: スキニング → ワールド
  float4 prev_world = mul(mul(float4(i.pos, 1.0), prev_skin), gPrevWorld);  // 前: 前の骨 → 前のワールド
  o.cur_clip = mul(world, gViewProj);
  o.prev_clip = mul(prev_world, gPrevViewProj);
  o.pos = o.cur_clip;
  return o;
}
```

骨の行列を重みで足して今と前の 2 通りの `skin` を作ります。同じ頂点 `i.pos` を今の骨と前の骨で変換して、それぞれワールド、クリップに進めます。頂点処理が 2 倍になるのは、この 2 回の変換が原因です。

ピクセル シェーダーで速度を画素に直します。

```hlsl
// 速度の書き出し。出力は「画素単位の移動量」(x は右が正、y は下が正)。前の位置から今の位置への向き。
float2 VelocityPS(VsOut i) : SV_Target {
  float2 cur = i.cur_clip.xy / i.cur_clip.w;                     // 今の NDC（-1〜1、上が +1）
  float2 prev = i.prev_clip.xy / max(abs(i.prev_clip.w), 1e-4);  // 前の NDC。w が 0 に近いとゼロ除算（足した）
  float2 ndc_delta = cur - prev;                                 // NDC での移動
  float2 px = ndc_delta * float2(0.5, -0.5) * gScreenSize;       // 画素に直す。NDC の y は上向きなので、画面の y（下向き）に符号を反転
  return px;
}
```

`w` で割って NDC にし差を取ります。`max(abs(w), 1e-4)` は足した処理で前のカメラ位置で物体がカメラの真横にあって `w` が 0 に近いときのゼロ除算を避けます。NDC は上が +1 ですが、画面の画素は下が +1 なので、y に負の符号を掛けて `gScreenSize` を掛けると、画素単位の移動になります。NDC の範囲は 2 なので、0.5 を掛けて画面の幅と高さの半分に直しています。

読む側でシャッターとクランプ、閾値を掛けます。

```hlsl
// 読む側。速度にシャッターを掛け、最大半径でクランプし、小さければ 0 にする。
float2 BlurVector(float2 velocity_px) {
  float2 v = velocity_px * gShutter;                              // 露光中に動く量 = 1 フレームの移動 × k
  float len = length(v);                                          // 長さ（画素）
  if (len < 0.5) return 0;                                        // 0.5 画素未満はブラーが見えない。コストを掛けない
  return v * (min(len, gMaxBlurPx) / len);                        // 長さだけを最大半径で頭打ち（向きは保つ）
}
```

`gShutter` を掛けて露光中の移動量にします。0.5 画素未満は 0 にして、コストを掛けません。長さだけを `gMaxBlurPx` で頭打ちにして、向きは保ちます。

タイルの最大速度を求めるコンピュート シェーダーです。

```hlsl
// タイルの最大速度。1 グループ = 1 タイル（gMaxBlurPx 四方。ここでは 16×16 固定の例）。
Texture2D<float2> gVelocity : register(t0);
RWTexture2D<float2> gTileMax : register(u0);
groupshared float2 sMax[256];                                      // タイル内の最大の速度（長さが最大のもの）

[numthreads(16, 16, 1)]
void TileMaxCS(uint3 gid : SV_GroupID, uint3 tid : SV_GroupThreadID, uint idx : SV_GroupIndex) {
  uint2 px = gid.xy * 16 + tid.xy;                                  // この画素
  float2 v = BlurVector(gVelocity.Load(int3(min(px, uint2(gScreenSize) - 1), 0)));  // 画面外は端の値で代用（足した）
  sMax[idx] = v;                                                    // 共有メモリへ
  GroupMemoryBarrierWithGroupSync();
  [unroll] for (uint s = 128; s > 0; s >>= 1) {                     // 半分ずつ畳む(木構造の縮約)
    if (idx < s) {
      float2 a = sMax[idx], b = sMax[idx + s];
      sMax[idx] = (dot(b, b) > dot(a, a)) ? b : a;                  // 長さの 2 乗が大きい方を残す（平方根を避ける）
    }
    GroupMemoryBarrierWithGroupSync();
  }
  if (idx == 0) gTileMax[gid.xy] = sMax[0];                         // タイルの代表値を書く
}
```

1 グループが 16×16 の画素で、1 タイルです。ブラーの最大半径を 16 画素にそろえた例になります（20 画素にするなら、グループを 20×20 にするか複数のグループで 1 タイルを担当させます）。共有メモリへ `BlurVector` を通した速度を書き木構造で半分ずつ畳みます。長さの比較は平方根を避けて 2 乗で行い長い方を残します。画面の端の画素は端の値で代用しています。これは足した処理です。

## よくあるミス {#mistakes}

??? failure "物体のブラーが輪郭でぷつっと切れる"
    原因は各画素が自分の速度だけを見ていることです。近傍の最大速度（タイル）を使いサンプルに深度と速度の重みを付けます。

??? failure "プロペラのブラーがぐちゃぐちゃになるまたは止まって見える"
    原因は 1 フレームで回る角度が大きく、位置の差が弦になっていることです。2400 rpm のプロペラは 60 fps で 240° 回り弦は弧の 41% です。360° では 0 になります。大きい回転はブラーを弱めるか専用メッシュに差し替えます。

??? failure "キャラクターの手足にブラーが無い"
    原因はスキニングの前フレームの姿勢が無く、速度が 0 になっていることです。前フレームの骨の行列を保存して、頂点シェーダーでもう一度スキニングします。

??? failure "半透明の物体が背景の速度を上書きして、ブラーがおかしい"
    原因は半透明の物体が速度バッファに書いていることです。半透明は速度を書かないようにします。

??? failure "静止している物体がじわじわぶれる"
    原因は TAA のジッターを含んだ行列で速度を求めていることです。ジッターを足す前の `gViewProj` と `gPrevViewProj` を使います。

??? failure "カメラを振ると、物体のブラーが画面全体と食い違う"
    原因は物体の速度にカメラの動きが入っていないことです。前の行列に前フレームのビュー・射影を使えば、カメラの動きも含めた画面上の移動になります。物体の速度だけを別に持つ場合はカメラ ブラーとの二重掛けに注意します（[Camera Motion Blur](camera-blur.md)）。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 速度は同じ頂点を前フレームの行列で変換した位置との差。ジッターは含めない
    - [x] 位置の差は弦の長さ。90° で弧の 90%、180° で 63.7%、360° で 0。大きい回転は弱める
    - [x] ブラーの長さは `1 フレームの移動 × k`。距離に反比例して小さくなり 0.5 画素未満は掛けない
    - [x] 輪郭の外の尾は近傍の最大速度（タイル）。タイルの大きさは最大半径で読むのは 3×3
    - [x] 半透明・パーティクル・UI は速度を書かない。対象は重要な物体に絞る

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

int main() {
  // 1. 回転する物体。1 フレームで回る角度 theta のとき、先端(半径 r)の弧の長さ r*theta、弦(位置の差)の長さ 2 r sin(theta/2)、
  //    弦と弧の差(矢高) r (1 - cos(theta/2))。前フレームとの「位置の差」で速度を作ると、弦が速度になる。
  std::printf("-- rotation: arc vs chord (r = 1)\n");
  for (double deg : {10.0, 30.0, 60.0, 90.0, 120.0, 180.0, 240.0, 330.0, 360.0}) {
    const double th = deg / kDeg;
    const double arc = th;                                  // 弧の長さ
    const double chord = 2.0 * std::sin(th / 2.0);          // 位置の差の大きさ
    const double sagitta = 1.0 - std::cos(th / 2.0);        // 弦から弧までの最大のずれ
    std::printf("theta %5.1f deg: arc %6.3f, chord %6.3f, chord/arc %5.3f, sagitta %5.3f\n", deg, arc, chord, chord / arc, sagitta);
  }

  // 2. 回転数から、1 フレームで回る角度。プロペラ 2400 rpm、車輪(半径 0.35 m、時速 100 km)。
  std::printf("-- rotation per frame\n");
  for (double fps : {30.0, 60.0, 120.0}) {
    const double rev_per_sec = 2400.0 / 60.0;                     // 2400 rpm = 40 回転/秒
    const double deg_per_frame = rev_per_sec * 360.0 / fps;       // 1 フレームの角度
    std::printf("propeller 2400 rpm at %3.0f fps: %6.1f deg/frame (tip speed at r = 0.5 m: %.1f m/s)\n", fps, deg_per_frame,
                rev_per_sec * 2.0 * kPi * 0.5);
  }
  {
    const double v = 100.0 / 3.6;                                  // 時速 100 km を m/s に
    const double omega = v / 0.35;                                 // 車輪の角速度 rad/s (転がり)
    for (double fps : {30.0, 60.0}) {
      std::printf("wheel r = 0.35 m at 100 km/h, %3.0f fps: %5.1f deg/frame\n", fps, omega / fps * kDeg);
    }
  }

  // 3. シャッター。露光時間を 1 フレームの割合 k (シャッター角 180 度 = 0.5) として、ブラーの長さは k * (1 フレームの移動)。
  std::printf("-- shutter\n");
  for (double shutter_deg : {90.0, 180.0, 270.0, 360.0}) {
    const double k = shutter_deg / 360.0;
    std::printf("shutter angle %3.0f deg: k = %.3f, exposure at 60 fps = %5.2f ms, at 30 fps = %5.2f ms\n", shutter_deg, k,
                k * 1000.0 / 60.0, k * 1000.0 / 30.0);
  }

  // 4. 画面上の速さ。横に v m/s で動く物体が、距離 z m にあるとき、1 フレームで動く画素数 = f_px * v / (z * fps)。
  //    f_px = (H / 2) / tan(fov / 2)。縦 FOV 60 度、高さ 1080 画素。
  std::printf("-- screen speed of a lateral mover (fov 60, 1080p, 60 fps)\n");
  const double f_px = 540.0 / std::tan(30.0 / kDeg);              // 焦点距離を画素で
  std::printf("f_px = %.1f\n", f_px);
  for (double v : {2.0, 10.0, 30.0}) {
    for (double z : {5.0, 10.0, 25.0, 50.0, 100.0}) {
      const double px_per_frame = f_px * v / z / 60.0;
      std::printf("v = %4.1f m/s, z = %5.1f m: %6.2f px/frame, blur at k = 0.5: %5.2f px\n", v, z, px_per_frame, px_per_frame * 0.5);
    }
  }
  //    ブラーが 0.5 画素を切る距離(k = 0.5)。z = f_px * v * k / (fps * 0.5)。
  for (double v : {2.0, 10.0, 30.0}) {
    std::printf("v = %4.1f m/s: blur < 0.5 px beyond z = %.1f m\n", v, f_px * v * 0.5 / 60.0 / 0.5);
  }

  // 5. 速度バッファの精度。画素単位の速度を、最大 R 画素(クランプ)の範囲で表す。
  std::printf("-- velocity buffer precision (clamp +-R px)\n");
  for (double r : {16.0, 20.0, 40.0}) {
    const double step8 = 2.0 * r / 255.0;                           // 8 ビット(256 段階)の刻み
    const double step16 = r / 32767.0;                              // 16 ビット SNORM の刻み
    std::printf("R = %4.0f px: 8-bit step %.4f px, 16-bit snorm step %.6f px\n", r, step8, step16);
  }
  const double mpix = 1920.0 * 1080.0;
  std::printf("1080p: R8G8 = %.2f MiB, R16G16 = %.2f MiB, R16G16 (tile 20x20) = %.1f KiB\n", mpix * 2 / 1048576.0, mpix * 4 / 1048576.0,
              std::ceil(1920.0 / 20.0) * std::ceil(1080.0 / 20.0) * 4 / 1024.0);

  // 6. サンプル数。半径 R 画素のブラーを、1 画素刻みで取ると R*2+1 点(両側)。片側 R 点、全体 2R。間引くとバンディングが出る。
  std::printf("-- samples needed (1 sample per pixel along the blur)\n");
  for (double r : {8.0, 16.0, 20.0, 40.0}) {
    const double full = 2.0 * r + 1.0;
    std::printf("radius %4.0f px: full %5.0f taps/pixel, 12 taps => step %.2f px, tile max 3x3 reads = 9\n", r, full, 2.0 * r / 12.0);
  }

  // 7. スキニングのコスト。頂点 N、ボーン B、行列 4x3 (48 バイト)または 4x4 (64 バイト)。
  std::printf("-- skinning memory\n");
  for (int verts : {20000, 50000, 100000}) {
    const double pos_bytes = verts * 12.0;                           // float3 の位置
    std::printf("%6d verts: skinned positions %.0f KiB per frame, previous+current = %.0f KiB\n", verts, pos_bytes / 1024.0,
                2 * pos_bytes / 1024.0);
  }
  for (int bones : {60, 80, 128, 256}) {
    std::printf("%3d bones: palette 4x4 = %5.2f KiB, current+previous = %5.2f KiB\n", bones, bones * 64.0 / 1024.0, bones * 128.0 / 1024.0);
  }
}
```

```text title="実行結果"
-- rotation: arc vs chord (r = 1)
theta  10.0 deg: arc  0.175, chord  0.174, chord/arc 0.999, sagitta 0.004
theta  30.0 deg: arc  0.524, chord  0.518, chord/arc 0.989, sagitta 0.034
theta  60.0 deg: arc  1.047, chord  1.000, chord/arc 0.955, sagitta 0.134
theta  90.0 deg: arc  1.571, chord  1.414, chord/arc 0.900, sagitta 0.293
theta 120.0 deg: arc  2.094, chord  1.732, chord/arc 0.827, sagitta 0.500
theta 180.0 deg: arc  3.142, chord  2.000, chord/arc 0.637, sagitta 1.000
theta 240.0 deg: arc  4.189, chord  1.732, chord/arc 0.413, sagitta 1.500
theta 330.0 deg: arc  5.760, chord  0.518, chord/arc 0.090, sagitta 1.966
theta 360.0 deg: arc  6.283, chord  0.000, chord/arc 0.000, sagitta 2.000
-- rotation per frame
propeller 2400 rpm at  30 fps:  480.0 deg/frame (tip speed at r = 0.5 m: 125.7 m/s)
propeller 2400 rpm at  60 fps:  240.0 deg/frame (tip speed at r = 0.5 m: 125.7 m/s)
propeller 2400 rpm at 120 fps:  120.0 deg/frame (tip speed at r = 0.5 m: 125.7 m/s)
wheel r = 0.35 m at 100 km/h,  30 fps: 151.6 deg/frame
wheel r = 0.35 m at 100 km/h,  60 fps:  75.8 deg/frame
-- shutter
shutter angle  90 deg: k = 0.250, exposure at 60 fps =  4.17 ms, at 30 fps =  8.33 ms
shutter angle 180 deg: k = 0.500, exposure at 60 fps =  8.33 ms, at 30 fps = 16.67 ms
shutter angle 270 deg: k = 0.750, exposure at 60 fps = 12.50 ms, at 30 fps = 25.00 ms
shutter angle 360 deg: k = 1.000, exposure at 60 fps = 16.67 ms, at 30 fps = 33.33 ms
-- screen speed of a lateral mover (fov 60, 1080p, 60 fps)
f_px = 935.3
v =  2.0 m/s, z =   5.0 m:   6.24 px/frame, blur at k = 0.5:  3.12 px
v =  2.0 m/s, z =  10.0 m:   3.12 px/frame, blur at k = 0.5:  1.56 px
v =  2.0 m/s, z =  25.0 m:   1.25 px/frame, blur at k = 0.5:  0.62 px
v =  2.0 m/s, z =  50.0 m:   0.62 px/frame, blur at k = 0.5:  0.31 px
v =  2.0 m/s, z = 100.0 m:   0.31 px/frame, blur at k = 0.5:  0.16 px
v = 10.0 m/s, z =   5.0 m:  31.18 px/frame, blur at k = 0.5: 15.59 px
v = 10.0 m/s, z =  10.0 m:  15.59 px/frame, blur at k = 0.5:  7.79 px
v = 10.0 m/s, z =  25.0 m:   6.24 px/frame, blur at k = 0.5:  3.12 px
v = 10.0 m/s, z =  50.0 m:   3.12 px/frame, blur at k = 0.5:  1.56 px
v = 10.0 m/s, z = 100.0 m:   1.56 px/frame, blur at k = 0.5:  0.78 px
v = 30.0 m/s, z =   5.0 m:  93.53 px/frame, blur at k = 0.5: 46.77 px
v = 30.0 m/s, z =  10.0 m:  46.77 px/frame, blur at k = 0.5: 23.38 px
v = 30.0 m/s, z =  25.0 m:  18.71 px/frame, blur at k = 0.5:  9.35 px
v = 30.0 m/s, z =  50.0 m:   9.35 px/frame, blur at k = 0.5:  4.68 px
v = 30.0 m/s, z = 100.0 m:   4.68 px/frame, blur at k = 0.5:  2.34 px
v =  2.0 m/s: blur < 0.5 px beyond z = 31.2 m
v = 10.0 m/s: blur < 0.5 px beyond z = 155.9 m
v = 30.0 m/s: blur < 0.5 px beyond z = 467.7 m
-- velocity buffer precision (clamp +-R px)
R =   16 px: 8-bit step 0.1255 px, 16-bit snorm step 0.000488 px
R =   20 px: 8-bit step 0.1569 px, 16-bit snorm step 0.000610 px
R =   40 px: 8-bit step 0.3137 px, 16-bit snorm step 0.001221 px
1080p: R8G8 = 3.96 MiB, R16G16 = 7.91 MiB, R16G16 (tile 20x20) = 20.2 KiB
-- samples needed (1 sample per pixel along the blur)
radius    8 px: full    17 taps/pixel, 12 taps => step 1.33 px, tile max 3x3 reads = 9
radius   16 px: full    33 taps/pixel, 12 taps => step 2.67 px, tile max 3x3 reads = 9
radius   20 px: full    41 taps/pixel, 12 taps => step 3.33 px, tile max 3x3 reads = 9
radius   40 px: full    81 taps/pixel, 12 taps => step 6.67 px, tile max 3x3 reads = 9
-- skinning memory
 20000 verts: skinned positions 234 KiB per frame, previous+current = 469 KiB
 50000 verts: skinned positions 586 KiB per frame, previous+current = 1172 KiB
100000 verts: skinned positions 1172 KiB per frame, previous+current = 2344 KiB
 60 bones: palette 4x4 =  3.75 KiB, current+previous =  7.50 KiB
 80 bones: palette 4x4 =  5.00 KiB, current+previous = 10.00 KiB
128 bones: palette 4x4 =  8.00 KiB, current+previous = 16.00 KiB
256 bones: palette 4x4 = 16.00 KiB, current+previous = 32.00 KiB
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。タイルの最大速度の考え方は自分で導いたものです。論文・発表で使われている具体的な手順（サンプルの重みの式、タイルの扱い）は確かめていません。

- Morgan McGuire, Padraic Hennessy, Michael Bukowski, Brian Osman, "A Reconstruction Filter for Plausible Motion Blur", I3D 2012
- Tiago Sousa, "Graphics Gems from CryENGINE 3", SIGGRAPH 2013
- Jorge Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014

## 関連ページ {#related}

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Camera Motion Blur](camera-blur.md)
- [Tile Max Velocity](tile-max.md)
- [Blur Pass Implementation](blur-pass.md)
- [スキニングとアニメーション](../../../3d/skinning-animation.md)
