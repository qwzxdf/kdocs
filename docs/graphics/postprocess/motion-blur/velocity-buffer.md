---
title: Velocity Buffer
tags:
  - 描画
---

# Velocity Buffer

<strong>モーション ブラーは、「各画素が前フレームからどう動いたか」</strong>という情報に頼ります。これを画素ごとに保存した画像が速度バッファ（Velocity Buffer）です。TAA・モーション ブラー・時間的なノイズ除去・アップスケールなど、時間方向の処理すべてが使う、現代の描画の共通インフラです。このページでは、速度の定義・書き込み方法・精度と形式・ジッターの扱い・動かない物の扱いを説明します。

!!! tip "ポイント"
    - 速度 ＝ <strong>この画素の点が前フレームでは画面のどこにいたか、との差</strong>（<strong>`現在位置 − 前フレームの位置`</strong>）。
    - 動く物体は、描画時に速度を書く。静止した物はカメラ移動分だけ（深度から計算できる）。
    - 保存は `R16G16_FLOAT`（UV 単位または画素単位）。
    - 前フレームのワールド行列が必要（物体ごとに保存）。
    - TAA のジッターを速度に混ぜない。
    - アニメーション・スキニングは前フレームの姿勢で頂点位置を計算する。

!!! info "このページを読む前に"
    - [Motion Blur](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:velocity-buffer:begin -->

<svg class="fig illust motion" data-fig="velocity-buffer" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-velocity-buffer" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">速度バッファ: 画素ごとに「前のフレームでは、どこにいたか」を書いておき、前の色を引き当てる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素。物 A は右へ 8、物 B は左へ 4 動いた。速度から前の位置を求めて、前のフレームの画像を読む</text>
<text x="60.0" y="106" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">前のフレーム</text>
<rect x="60.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="77.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="94.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="111.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="128.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="145.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="162.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="179.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="196.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="213.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="230.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="247.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="264.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="281.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="298.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="315.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="332.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="349.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="366.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="383.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="400.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="417.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="434.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="451.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="468.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="485.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="502.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="519.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="536.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="553.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="570.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="587.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="604.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="621.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="638.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="655.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="672.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="689.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="706.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="723.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="740.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="757.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="774.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="791.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="808.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="825.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="842.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="859.0" y="110.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="60.0" y="110" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="164" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">いまのフレーム(物が動いた)</text>
<rect x="60.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="77.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="94.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="111.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="128.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="145.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="162.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="179.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="196.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="213.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="230.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="247.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="264.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="281.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="298.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="315.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="332.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="349.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="366.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="383.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="400.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="417.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2594c"/></rect>
<rect x="434.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="451.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="468.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="485.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="502.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="519.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="536.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="553.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="570.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="587.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="604.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="621.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="638.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="655.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4080f2"/></rect>
<rect x="672.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="689.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="706.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="723.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="740.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="757.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="774.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="791.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="808.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="825.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="842.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="859.0" y="168.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="60.0" y="168" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="238" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">速度バッファ(画素ごとの動き。右 = 赤、左 = 青)</text>
<rect x="60.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="77.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="94.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="111.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="128.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="145.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="162.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="179.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="196.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="213.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="230.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="247.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="264.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="281.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="298.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="315.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="332.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="349.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="366.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="383.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="400.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="417.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="434.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="451.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="468.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="485.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="502.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="519.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="536.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="553.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="570.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="587.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="604.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="621.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="638.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="655.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="672.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="689.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="706.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="723.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="740.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="757.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="774.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="791.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="808.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="825.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="842.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="859.0" y="244.0" width="17.3" height="26.3" fill="#e5e7eb"/>
<rect x="60.0" y="244" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="340.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">+8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1092;0.1093;1.0000" values="0;0;1;1"/></text>
<text x="357.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">+8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1118;0.1120;1.0000" values="0;0;1;1"/></text>
<text x="374.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">+8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1147;1.0000" values="0;0;1;1"/></text>
<text x="391.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">+8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1172;0.1173;1.0000" values="0;0;1;1"/></text>
<text x="408.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">+8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1198;0.1200;1.0000" values="0;0;1;1"/></text>
<text x="425.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">+8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1225;0.1227;1.0000" values="0;0;1;1"/></text>
<text x="578.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">-4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1465;0.1467;1.0000" values="0;0;1;1"/></text>
<text x="595.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">-4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1493;1.0000" values="0;0;1;1"/></text>
<text x="612.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">-4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1518;0.1520;1.0000" values="0;0;1;1"/></text>
<text x="629.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">-4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1545;0.1547;1.0000" values="0;0;1;1"/></text>
<text x="646.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">-4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1572;0.1573;1.0000" values="0;0;1;1"/></text>
<text x="663.5" y="262" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff" opacity="0">-4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1598;0.1600;1.0000" values="0;0;1;1"/></text>
<text x="60.0" y="306" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">速度で前の位置を引き当てた画像(各画素: 前のフレームの「自分の位置 − 速度」の色)</text>
<rect x="60.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2213" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="77.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2240" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="94.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2267" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="111.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2293" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="128.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2320" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="145.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2347" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="162.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2373" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="179.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="196.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2427" values="#e5e7eb;#f2594c"/></rect>
<rect x="213.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2453" values="#e5e7eb;#f2594c"/></rect>
<rect x="230.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2480" values="#e5e7eb;#f2594c"/></rect>
<rect x="247.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#f2594c"/></rect>
<rect x="264.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2533" values="#e5e7eb;#f2594c"/></rect>
<rect x="281.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2560" values="#e5e7eb;#f2594c"/></rect>
<rect x="298.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2587" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="315.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2613" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="332.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2640" values="#e5e7eb;#f2594c"/></rect>
<rect x="349.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2667" values="#e5e7eb;#f2594c"/></rect>
<rect x="366.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#f2594c"/></rect>
<rect x="383.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#f2594c"/></rect>
<rect x="400.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#f2594c"/></rect>
<rect x="417.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#f2594c"/></rect>
<rect x="434.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="451.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="468.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="485.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="502.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="519.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="536.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="553.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="570.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#e5e7eb;#4080f2"/></rect>
<rect x="587.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3040" values="#e5e7eb;#4080f2"/></rect>
<rect x="604.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#4080f2"/></rect>
<rect x="621.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#4080f2"/></rect>
<rect x="638.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3120" values="#e5e7eb;#4080f2"/></rect>
<rect x="655.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3147" values="#e5e7eb;#4080f2"/></rect>
<rect x="672.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3173" values="#e5e7eb;#4080f2"/></rect>
<rect x="689.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#e5e7eb;#4080f2"/></rect>
<rect x="706.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3227" values="#e5e7eb;#4080f2"/></rect>
<rect x="723.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3253" values="#e5e7eb;#4080f2"/></rect>
<rect x="740.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3280" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="757.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3307" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="774.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="791.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3360" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="808.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3387" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="825.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="842.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3440" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="859.0" y="312.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="60.0" y="312" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="370" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">速度を使わず、同じ位置を読んだ画像</text>
<rect x="60.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3724" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="77.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3751" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="94.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="111.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3804" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="128.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3831" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="145.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3858" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="162.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3884" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="179.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3911" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="196.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3938" values="#e5e7eb;#f2594c"/></rect>
<rect x="213.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3964" values="#e5e7eb;#f2594c"/></rect>
<rect x="230.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3991" values="#e5e7eb;#f2594c"/></rect>
<rect x="247.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4018" values="#e5e7eb;#f2594c"/></rect>
<rect x="264.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4044" values="#e5e7eb;#f2594c"/></rect>
<rect x="281.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4071" values="#e5e7eb;#f2594c"/></rect>
<rect x="298.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4098" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="315.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4124" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="332.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4151" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="349.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4178" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="366.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4204" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="383.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4231" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="400.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4258" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="417.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4284" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="434.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4311" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="451.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4338" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="468.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4364" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="485.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4391" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="502.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4418" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="519.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4444" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="536.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4471" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="553.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="570.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4524" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="587.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4551" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="604.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4578" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="621.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4604" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="638.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4631" values="#e5e7eb;#4080f2"/></rect>
<rect x="655.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4658" values="#e5e7eb;#4080f2"/></rect>
<rect x="672.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#4080f2"/></rect>
<rect x="689.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#4080f2"/></rect>
<rect x="706.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#4080f2"/></rect>
<rect x="723.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#4080f2"/></rect>
<rect x="740.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="757.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="774.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="791.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="808.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="825.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="842.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="859.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#e5e7eb;#e0e6eb"/></rect>
<rect x="60.0" y="376" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5269;0.5271;1.0000" values="0;0;1;1"/><rect x="60" y="424" width="860" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="76" y="448" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">いまのフレームと食い違う画素: 速度あり 10 個 / 速度なし 20 個</text>
<text x="76" y="472" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">残る 10 個は、物が離れて、隠れていた所が見えた画素(ディスオクルージョン)。前の色が無いので、履歴を捨てる</text>
<text x="76" y="494" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">速度バッファは、TAA・モーション ブラーの土台。物の動きから、頂点シェーダーで計算して書く</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">動く物の前の位置は、画素だけからは分からない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">描くとき、前のフレームとの位置の差を速度バッファに書く<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2212;0.2213;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">速度を引いて、前のフレームの色を引き当てる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2212;0.2213;0.5269;0.5271;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">速度なしだと、物の色が前の位置のまま、ずれる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5269;0.5271;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:velocity-buffer:end -->

## 速度とは

<strong>画素 P が表す 3D の点が前フレームでは画面のどこにいたか</strong>を求め、現在位置との差を速度とします。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="速度の定義">
<text x="20" y="26" class="fig-title">速度 ＝ 今のフレームの画面位置 − 前のフレームの画面位置</text>
<g transform="translate(40,56)">
<rect x="0" y="0" width="320" height="150" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="90" cy="95" r="10" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="70" y="124" style="font-size:12px">前フレームの位置</text>
<circle cx="220" cy="60" r="10" fill="#2563eb"/><text x="190" y="40" style="font-size:12px">今フレームの位置</text>
<line x1="100" y1="90" x2="208" y2="64" stroke="#e5484d" stroke-width="3" marker-end="url(#vb-arrow)"/>
<defs><marker id="vb-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#e5484d"/></marker></defs>
<text x="130" y="68" style="font-size:12px;fill:#e5484d;font-weight:700">速度</text>
</g>
<g font-size="13"><text x="400" y="90" style="font-weight:700">速度バッファの中身</text>
<text x="400" y="116">各画素に(vx, vy)（2 要素）を保存</text>
<text x="400" y="140">動く物体 → 大きな値、静止した物 → カメラの動き分だけ</text>
<text x="400" y="164">この画像をブラー・TAA・アップスケールが読む</text></g>
</svg>

## 書き込み（動く物体）

<strong>物体を描くときに、「今の位置」と「前フレームの位置」を両方計算</strong>して、差を出力します。

```hlsl
cbuffer PerObject : register(b0) {
  float4x4 world;
  float4x4 previous_world;
  float4x4 view_projection;
  float4x4 previous_view_projection;
  float2 jitter_current;
  float2 jitter_previous;
};
```

オブジェクトごとの、定数です。今フレームと、前フレームの、ワールド行列と、ビュー射影行列を持ちます。`jitter_*` は、TAA が、画面をずらす量で、速度から、取り除くために、必要です。

```hlsl
struct VSOutput {
  float4 position : SV_POSITION;
  float4 current_clip : TEXCOORD0;
  float4 previous_clip : TEXCOORD1;
};
```

頂点シェーダーから、ピクセル シェーダーへ渡すものです。今の位置と、前の位置をクリップ空間のまま、渡します。

```hlsl
VSOutput VSMain(VSInput input) {
  VSOutput output;
  float4 world_position = mul(float4(input.position, 1.0), world);
  float4 previous_world_position = mul(float4(input.position, 1.0), previous_world);
  output.current_clip = mul(world_position, view_projection);
  output.previous_clip = mul(previous_world_position, previous_view_projection);
  output.position = output.current_clip;
  return output;
}
```

頂点を今の行列と、前の行列で、それぞれ、変換します。前の位置は、「同じ頂点が前のフレームで、どこにあったか」で、スキニングなど、頂点が変形する物は、前のフレームの、変形後の位置を使います。

```hlsl
float2 PSMain(VSOutput input) : SV_Target {
  float2 current_ndc = input.current_clip.xy / input.current_clip.w;
  float2 previous_ndc = input.previous_clip.xy / input.previous_clip.w;
  current_ndc -= jitter_current;
  previous_ndc -= jitter_previous;
  float2 velocity = (current_ndc - previous_ndc) * float2(0.5, -0.5);
  return velocity;
}
```

| 点 | 説明 |
| --- | --- |
| `previous_world` | 前フレームのワールド行列（物体ごとに、1 フレーム前を覚えておく） |
| `previous_view_projection` | 前フレームのカメラ（ジッターなしのもの） |
| NDC → UV の差 | `× (0.5, −0.5)`（NDC の Y 向きと、UV の Y 向きは逆） |
| ジッターを引く | TAA のサブピクセル ジッターを差し引いてから比較 |

## カメラの動き（静止した物）

<strong>静止している物体は、カメラが動いたぶんだけ、画面で動く</strong>ので描画時に書かなくても深度から計算できます（[Camera Motion Blur](camera-blur.md)）。動く物体だけが速度バッファに書き込み、書かれていない画素は、カメラの速度を使います。

画素ごとの速度の出どころです。動く物体は、速度バッファに書き込んだ値を使います。静止した物（書かれていない画素）は、深度から再構成したカメラの速度を使います。

## 精度と形式

| 項目 | 内容 |
| --- | --- |
| 形式 | `R16G16_FLOAT`（2 要素・半精度） |
| 単位 | UV（0〜1）または画素。UV 単位が解像度に依らない |
| 精度 | 0.5 画素以下の速度が区別できることが重要（TAA のため） |
| 範囲 | 画面を横切る速度（±1 UV）まで |

<strong>8 ビットは不十分</strong>です（小さな速度が量子化で消える）。

## ジッターの扱い

<strong>TAA は毎フレーム、サブピクセル単位でカメラを揺らします（ジッター）</strong>。速度を揺らした位置どうしで比べると、ジッターの差がすべての画素の速度に混ざり、静止した物がブレます。

ジッターの対処は 2 つです。現在と前フレームの NDC のそれぞれから、そのフレームのジッターを引きます。あるいは、速度計算用の `view_projection` をジッターなしで別に持ちます。

## スキニング・アニメーション

<strong>キャラクターの手足</strong>などは、前フレームの姿勢で頂点位置を再計算する必要があります。

スキニング済みの頂点の速度は、3 通りで求めます。前フレームのボーン行列を保存して、スキニングを今と前の 2 回行う方法。前フレームの頂点位置をバッファに保存し、スキニング後の頂点位置をスワップして使う方法。メッシュ シェーダーで、頂点位置を今と前の両方計算する方法です。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 動く物体だけ書く | 静止した物は深度から計算（帯域節約） |
| フラグで書き込みを切る | 動かない物体は、速度の書き込みを省略 |
| 前フレームの行列をバッファで管理 | 物体ごとに前の行列を保持して、更新 |
| R16G16 ＋ UV 単位 | 精度と解像度非依存 |
| TAA・ブラー・アップスケールで共有 | 1 枚を作り、複数の効果が読む |
| 新しく現れた物体は速度 0 | 初出のフレームで前の行列がないと速度が壊れるので現在 = 前にする |

## よくあるミス

??? failure "静止している物がブラーやゴーストでぼける"
    <strong>ジッターを速度に混ぜている</strong>。ジッターを引く。

??? failure "動く物体にだけブラーがかかって、カメラを動かしても背景が流れない"
    静止した物の速度（カメラ分）が入っていない。深度から再構成。

??? failure "出現したばかりの物体が画面を横切る大きな速度で、ひどくぼける"
    前フレームの行列が無い。初出は前の行列 ＝ 現在の行列にする。

??? failure "速度を 8 ビットで保存して、小さな動きが 0 になる"
    `R16G16_FLOAT` にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 速度 ＝ <strong>今の画面位置 − 前フレームの画面位置</strong>
    - [x] 動く物体は描画時に書き込み、静止した物は深度から計算
    - [x] `R16G16_FLOAT`。TAA・ブラーで共有
    - [x] ジッターは引く。前フレームの行列を保持
    - [x] スキニングは前フレームの姿勢で

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）

## 関連ページ

- [Motion Blur](index.md)
- [Camera Motion Blur](camera-blur.md)
- [Object Motion Blur](object-blur.md)
- [TAA](../antialiasing/taa.md)
