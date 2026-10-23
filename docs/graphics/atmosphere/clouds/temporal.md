---
title: Cloud Temporal Reprojection
tags:
  - 描画
---

# Cloud Temporal Reprojection

<strong>雲のレイマーチは重いので毎フレーム全画素を計算せず、一部だけ更新して前フレームと合成</strong>します。4×4 画素のうち毎フレーム 1 画素だけ更新する方式がよく使われます。このページでは時間蓄積による高速化を説明します。

!!! tip "ポイント"
    - 4×4 の中の 1 画素だけ、毎フレーム更新（16 フレームで全体）。
    - 他の画素は前フレームを再投影。
    - 低解像度で計算して、アップサンプル。
    - 動きが速いとゴーストに注意。

!!! info "このページを読む前に"
    - [Clouds](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 高速化：時間蓄積
<strong>雲のレイマーチは重い</strong>ので、画面全体を毎フレーム描かず、1/4 の画素だけ描いて時間をかけて埋めます。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="雲の時間蓄積">
<text x="20" y="24" class="fig-title">4×4 のうち 1 ピクセルだけ毎フレーム更新して、16 フレームで全体が埋まる</text>
<g transform="translate(40,50)">
<g stroke="currentColor" stroke-opacity="0.4" fill="none"><rect x="0" y="0" width="128" height="128"/>
<line x1="32" y1="0" x2="32" y2="128"/><line x1="64" y1="0" x2="64" y2="128"/><line x1="96" y1="0" x2="96" y2="128"/>
<line x1="0" y1="32" x2="128" y2="32"/><line x1="0" y1="64" x2="128" y2="64"/><line x1="0" y1="96" x2="128" y2="96"/></g>
<rect x="32" y="64" width="32" height="32" fill="#e5484d" fill-opacity="0.6"/>
<text x="64" y="156" text-anchor="middle" style="font-size:12px">今のフレームで描く位置</text>
</g>
<g font-size="12">
<text x="240" y="82" style="font-weight:700">手順</text>
<text x="240" y="106">① 1/4 解像度（または 4×4 に 1 画素）だけレイマーチ</text>
<text x="240" y="130">② 前フレームの結果を、カメラの動きで再投影して持ってくる</text>
<text x="240" y="154">③ 新しく描いた画素だけ置き換える</text>
<text x="240" y="178">④ 動く物の裏など、履歴が使えない所は新しい結果を優先</text>
<text x="240" y="212" style="font-weight:700">コスト：1/16 〜 1/4 に。ただしゴースト（残像）に注意</text>
</g>
</svg>

| 工夫 | 内容 |
| --- | --- |
| 低解像度で描く | 半分／1/4 の解像度でレイマーチし、アップサンプル |
| ブルー ノイズ ジッター | フレームごとに開始位置を変えて、平均で滑らか |
| 履歴の再投影 | 前フレームの雲をカメラ移動分だけ動かす（雲は遠いので回転だけで近似できる） |
| 層の距離を使う | 雲までの距離（深度）を持って、再投影の精度を上げる |
| 早期の打ち切り | 透過率が低ければ打ち切る |

### 4×4 の更新パターンの仕組み

Horizon Zero Dawn の方式は、画面を 4×4 画素のブロックに区切り、各ブロックの 16 画素のうち、毎フレーム1 画素だけをレイマーチします。更新する画素の位置はブルー ノイズや決まった順列で、フレームごとに変えます。16 フレームで全画素が一巡します。

更新しなかった 15 画素は、前フレームの結果を再投影して使います。つまり、毎フレームのレイマーチは全画素の 1/16 で済み、コストは 1/16 になります（実際には、再投影とアップサンプルのコストが加わります）。再投影はカメラの動きに合わせて、前フレームの画像を今のフレームの画素に対応づける処理です。雲は遠くにあるのでカメラの平行移動を無視し、回転だけで再投影しても見た目の破綻は小さくて済みます。

<!-- fig:cloud-bayer:begin -->

<svg class="fig illust motion" data-fig="cloud-bayer" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-bayer" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">雲の時間蓄積: 1 フレームに 16 分の 1 の画素だけ描き、残りは、前のフレームの結果を、動きに合わせて使う</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">8×8 画素。更新する画素を、Bayer の順で 1 つずつ(4×4 パターン)。画素ごとの「データの古さ」と、全画素が新しくなるまでのフレーム数を数える</text>
<rect x="30" y="96" width="326.0" height="326.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">画素の「データの古さ」(0 = 今フレームに更新)</text>
<rect x="33.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f;#1e3a8a"/></rect>
<rect x="73.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf"/></rect>
<rect x="113.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393"/></rect>
<rect x="153.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9"/></rect>
<rect x="193.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f;#1e3a8a"/></rect>
<rect x="233.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf"/></rect>
<rect x="273.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393"/></rect>
<rect x="313.0" y="99.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9"/></rect>
<rect x="33.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2"/></rect>
<rect x="73.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d"/></rect>
<rect x="113.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb"/></rect>
<rect x="153.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6"/></rect>
<rect x="193.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2"/></rect>
<rect x="233.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d"/></rect>
<rect x="273.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb"/></rect>
<rect x="313.0" y="139.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6"/></rect>
<rect x="33.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098"/></rect>
<rect x="73.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd"/></rect>
<rect x="113.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f"/></rect>
<rect x="153.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4"/></rect>
<rect x="193.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098"/></rect>
<rect x="233.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd"/></rect>
<rect x="273.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f"/></rect>
<rect x="313.0" y="179.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4"/></rect>
<rect x="33.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316"/></rect>
<rect x="73.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab"/></rect>
<rect x="113.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7"/></rect>
<rect x="153.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1"/></rect>
<rect x="193.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316"/></rect>
<rect x="233.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab"/></rect>
<rect x="273.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7"/></rect>
<rect x="313.0" y="219.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1"/></rect>
<rect x="33.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f;#1e3a8a"/></rect>
<rect x="73.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf"/></rect>
<rect x="113.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393"/></rect>
<rect x="153.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9"/></rect>
<rect x="193.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f;#1e3a8a"/></rect>
<rect x="233.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf"/></rect>
<rect x="273.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393"/></rect>
<rect x="313.0" y="259.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9"/></rect>
<rect x="33.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2"/></rect>
<rect x="73.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d"/></rect>
<rect x="113.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb"/></rect>
<rect x="153.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6"/></rect>
<rect x="193.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2"/></rect>
<rect x="233.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d"/></rect>
<rect x="273.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb"/></rect>
<rect x="313.0" y="299.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6"/></rect>
<rect x="33.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098"/></rect>
<rect x="73.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd"/></rect>
<rect x="113.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f"/></rect>
<rect x="153.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4"/></rect>
<rect x="193.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098"/></rect>
<rect x="233.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd"/></rect>
<rect x="273.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1;#486c9d;#3d6098;#335393;#28478f"/></rect>
<rect x="313.0" y="339.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4"/></rect>
<rect x="33.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316"/></rect>
<rect x="73.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab"/></rect>
<rect x="113.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7"/></rect>
<rect x="153.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1"/></rect>
<rect x="193.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316"/></rect>
<rect x="233.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab"/></rect>
<rect x="273.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7"/></rect>
<rect x="313.0" y="379.0" width="40.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1085;0.1532;0.1979;0.2426;0.2872;0.3319;0.3766;0.4213;0.4660;0.5106;0.5553;0.6000;0.6447;0.6894;0.7340" values="#e5e7eb;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#1e3a8a;#f97316;#b1eacb;#a6dec7;#9cd1c2;#91c5bd;#87b8b9;#7cabb4;#729faf;#6792ab;#5d86a6;#5279a1"/></rect>
<g opacity="0.4"><line x1="73.0" y1="99" x2="73.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="113.0" y1="99" x2="113.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="153.0" y1="99" x2="153.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="193.0" y1="99" x2="193.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="233.0" y1="99" x2="233.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="273.0" y1="99" x2="273.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="313.0" y1="99" x2="313.0" y2="419.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="139.0" x2="353.0" y2="139.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="179.0" x2="353.0" y2="179.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="219.0" x2="353.0" y2="219.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="259.0" x2="353.0" y2="259.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="299.0" x2="353.0" y2="299.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="339.0" x2="353.0" y2="339.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="33" y1="379.0" x2="353.0" y2="379.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="33" y="99" width="320.0" height="320.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="380.0" y="130" text-anchor="start" style="font-size:13px;font-weight:700;fill:#c2410c">橙 = このフレームに更新した画素(4 個)</text>
<text x="380.0" y="156" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">緑 → 青 = 前に更新してから、経ったフレーム数</text>
<text x="380.0" y="200" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">フレーム:</text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1083;0.1085;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1083;0.1085;0.1530;0.1532;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;0.1977;0.1979;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1977;0.1979;0.2424;0.2426;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2424;0.2426;0.2871;0.2872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2872;0.3317;0.3319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">7<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.3764;0.3766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3764;0.3766;0.4211;0.4213;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">9<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4211;0.4213;0.4658;0.4660;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">10<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4658;0.4660;0.5105;0.5106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">11<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5105;0.5106;0.5551;0.5553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5551;0.5553;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;0.6445;0.6447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">14<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6445;0.6447;0.6892;0.6894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;0.7339;0.7340;1.0000" values="0;0;1;1;0;0"/></text>
<text x="480.0" y="204" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7339;0.7340;1.0000" values="0;0;1;1"/></text>
<text x="380.0" y="244" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">いちばん古い画素の古さ:</text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1083;0.1085;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1083;0.1085;0.1530;0.1532;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;0.1977;0.1979;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1977;0.1979;0.2424;0.2426;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2424;0.2426;0.2871;0.2872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2872;0.3317;0.3319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.3764;0.3766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3764;0.3766;0.4211;0.4213;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4211;0.4213;0.4658;0.4660;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4658;0.4660;0.5105;0.5106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5105;0.5106;0.5551;0.5553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5551;0.5553;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;0.6445;0.6447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6445;0.6447;0.6892;0.6894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;0.7339;0.7340;1.0000" values="0;0;1;1;0;0"/></text>
<text x="580.0" y="248" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7339;0.7340;1.0000" values="0;0;1;1"/></text>
<text x="380.0" y="286" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">描いた画素の合計:</text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1083;0.1085;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1083;0.1085;0.1530;0.1532;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;0.1977;0.1979;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1977;0.1979;0.2424;0.2426;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2424;0.2426;0.2871;0.2872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2872;0.3317;0.3319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.3764;0.3766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">32<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3764;0.3766;0.4211;0.4213;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">36<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4211;0.4213;0.4658;0.4660;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">40<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4658;0.4660;0.5105;0.5106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">44<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5105;0.5106;0.5551;0.5553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">48<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5551;0.5553;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">52<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;0.6445;0.6447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">56<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6445;0.6447;0.6892;0.6894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">60<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;0.7339;0.7340;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540.0" y="290" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">64<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7339;0.7340;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7786;0.7787;1.0000" values="0;0;1;1"/><rect x="30" y="440" width="900" height="72" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="464" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">1 フレームに描く画素: 4 / 64(16 分の 1)。16 フレームで、全画素が更新される</text>
<text x="46" y="488" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">毎フレーム全部描くと 64 回 → 4×4 パターンで 4 回(16 倍安い)。残りは、再投影した、前フレームの結果を使う</text>
<text x="46" y="510" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">動くと再投影がずれて、ゴーストが出る → 近傍クランプ・履歴の重みの調整で、抑える</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲のレイマーチは重いので、全画素は、毎フレーム描けない<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">4×4 の順で、離れた画素を 1 つずつ更新する(Bayer)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.7786;0.7787;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">16 フレームで、全画素が新しくなる。コストは 1/16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7786;0.7787;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-bayer:end -->

### 破綻とその対策

この方式の弱点は動きが速いときです。カメラが急に回転したり雲が速く動いたりすると、再投影した前フレームの画素が、今のフレームの内容と合わなくなります。対策は再投影で参照した履歴が信頼できるかを調べることです。たとえば、再投影先が画面外ならそのフレームで強制的に新しく計算する、あるいは今のフレームの周囲の画素の最小値と最大値の範囲に、履歴を収める（近傍クランプ）などの方法があります。また、新しく計算した画素は前の履歴と混ぜず、すぐに置き換えるほうが残像が出にくくなります。

雲の描画を低解像度の別のターゲットに行い、最後に空と合成する構成にしておくと、この更新方式を他のパスから独立させて扱えます。

## なぜ時間方向の処理か

雲のレイマーチ（[Cloud Raymarching](raymarch.md)）は、<strong>重い</strong>です。全画素で毎フレーム、数十ステップを行うと数ミリ秒〜十数ミリ秒かかります。そこで、時間方向に計算を分散します。1 フレームで一部の画素だけを計算し残りは、前のフレームの結果を使い回します。

## 2 つの工夫

| 工夫 | 内容 | 効果 |
| --- | --- | --- |
| 低解像度で描く | 画面の、1/4（縦横、各 1/2）の解像度でレイマーチ | 画素数が、1/4 |
| 更新する画素を間引く | 1 フレームに、16 画素に 1 つ（4×4 の、1 つ）だけレイマーチ。残りの 15 は前のフレームから、再投影 | さらに 1/16 |

<strong>組み合わせる</strong>と 画面の約 1/64 の画素しか、毎フレーム、レイマーチしません。64 倍、軽くなります。

## 4×4 の更新パターン

<strong>4×4 のブロック</strong>（16 画素）の、どの 1 つを更新するかを、フレームごとに順番に変えます。16 フレームで全画素が 1 回ずつ、更新されます（[Cloud Bayer の図、参照]）。

```hlsl
// 4×4 の、更新順（Bayer 行列）。0〜15。フレーム番号 % 16 と、一致する画素が、今フレームの、更新対象。
static const int kBayer4x4[16] = { 0, 8, 2, 10,  12, 4, 14, 6,  3, 11, 1, 9,  15, 7, 13, 5 };

bool ShouldUpdate(uint2 pixel, uint frame_index) {
  uint2 p = pixel & 3;                                          // 4×4 ブロック内の位置
  return kBayer4x4[p.y * 4 + p.x] == (frame_index & 15);
}
```

ベイヤー行列の順序で 離れた画素を次々に、更新します。隣り合う画素が同じフレームで、更新されないので更新のむらが、目立ちません（[Dithered Transparency](../../translucency/alpha-test/dither.md) と同じ、順序）。

## 再投影：前のフレームを使う

<strong>更新しない画素</strong>は 前のフレームの、結果を使い回します。カメラが動いているので前のフレームの、どの画素が今の画素に対応するか（再投影）を、求めます。

```hlsl
// 今フレームの画素に対応する、前フレームの uv を求める（カメラの動きを、考慮）。
float2 ReprojectToPrevious(float2 uv, float depth_distance) {
  // 雲は、遠いので、深度は、遠景の距離として、扱う（視線方向 × 距離 → ワールド位置）。
  float3 ray_dir = ScreenToWorldDir(uv);
  float3 world_pos = g_camera_position + ray_dir * depth_distance;
  float4 prev_clip = mul(float4(world_pos, 1.0), g_prev_view_proj);
  return prev_clip.xy / prev_clip.w * float2(0.5, -0.5) + 0.5;
}
```

今の画素の位置（距離つき）から、ワールド位置を復元し前フレームの、ビュー・射影行列で前の画面の位置を、求めます。雲は遠くにあるので距離は大きな、固定値（雲の殻までの距離）で、近似できます。

```hlsl
float4 CloudTemporalPS(float2 uv : TEXCOORD0, float4 pos : SV_Position) : SV_Target {
  uint2 pixel = (uint2)pos.xy;
  float2 prev_uv = ReprojectToPrevious(uv, g_cloud_reference_distance);
  float4 history = g_cloud_history.Sample(g_linear_clamp, prev_uv);      // 前フレームの結果（色 + 透過率）

  if (ShouldUpdate(pixel, g_frame_index)) {
    float4 current = RaymarchCloud(uv);                                  // 今フレームに、更新する画素: レイマーチ
    return lerp(history, current, 0.1 + ...);                            // 履歴と、混ぜる（下記）
  }
  return history;                                                        // 更新しない画素: 履歴を、そのまま
}
```

更新する画素は レイマーチした結果を履歴に混ぜ、更新しない画素は履歴をそのまま、返します。

## 履歴のクランプ（ゴースト対策）

<strong>カメラや雲が動く</strong>と 前のフレームの結果が、今の状態と合わなくなりゴースト（残像）が、出ます。履歴の色を今フレームの周囲の色の範囲に、クランプします（Karis、2014、TAA と同じ考え方）。

```hlsl
// 周囲 3×3 の、今フレームの結果の、最小・最大の範囲に、履歴を、クランプして、ゴーストを抑える。
float4 min_c = 1e9, max_c = -1e9;
for (int y = -1; y <= 1; ++y)
  for (int x = -1; x <= 1; ++x) {
    float4 c = g_cloud_current_lowres.Load(int3(pixel / 4 + int2(x, y), 0));
    min_c = min(min_c, c); max_c = max(max_c, c);
  }
history = clamp(history, min_c, max_c);
```

履歴が今の周囲の色の範囲から、外れていたら 範囲の中に押し込みます。雲が動いたことで古い値が残る場合に、ゴーストが消えます。

| 履歴の混ぜ方 | 効果 |
| --- | --- |
| 混ぜる割合を小さく（履歴を、強く） | なめらかノイズが、少ない。ゴーストが出やすい |
| 混ぜる割合を大きく（履歴を、弱く） | ゴーストが少ない。ノイズが目立つ |
| 速い動きのときは割合を大きく | カメラの動きの速度で、混ぜる割合を変える |

```hlsl
float camera_motion = length(g_camera_position - g_prev_camera_position);
float blend = saturate(0.05 + camera_motion * g_motion_blend_scale);     // 速く動くほど、今フレームを、強く
```

## ジッターと組み合わせる

<strong>レイマーチの開始位置</strong>に フレームごとに、違うノイズを使うと 16 フレームの平均で、ノイズが均されなめらかな雲に、なります（[Cloud Raymarching](raymarch.md) の、ジッター）。

```hlsl
float jitter = InterleavedGradientNoise(pixel + g_frame_index * 5.588238);   // フレームごとに、ずらす
```

## 品質とコストのトレードオフ

| 設定 | コスト | 品質 |
| --- | --- | --- |
| フル解像度、毎フレーム、全画素 | 重い | 最高 |
| 1/4 解像度、毎フレーム、全画素 | 重い | 高 |
| 1/4 解像度、4×4 で 1/16 更新 | 軽い | 中〜高（カメラが、止まっていれば高い） |
| 1/4 解像度、2×2 で 1/4 更新 | 中 | 高 |

<strong>カメラが速く動く</strong>と ゴースト、ノイズが増えます。動きの速さに応じて更新の割合を、変える（速いときは多く更新）と品質が、保たれます。

## よくあるミス

??? failure "カメラを動かすと、雲がちらつく"
    <strong>再投影の精度</strong>を上げ、履歴の拒否をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一部の画素だけ更新して重ねる

## 参考

- Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014（Interleaved Gradient Noise）

## 関連ページ

- [Clouds](index.md)
- [Cloud Raymarching](raymarch.md)
- [TAA](../../postprocess/antialiasing/taa.md)
