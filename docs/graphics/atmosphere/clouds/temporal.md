---
title: Cloud Temporal Reprojection
tags:
  - 描画
---

# Cloud Temporal Reprojection

**雲のレイマーチは重いので、毎フレーム全画素を計算せず、一部だけ更新して、前フレームと合成**します。**4×4 画素のうち、毎フレーム 1 画素だけ更新**する**方式**が**よく使われます**。このページでは、**時間蓄積による高速化**を説明します。

!!! tip "ポイント"
    - **4×4 の中の 1 画素だけ、毎フレーム更新**（16 フレームで全体）。
    - **他の画素は、前フレームを再投影**。
    - **低解像度で計算して、アップサンプル**。
    - **動きが速いと、ゴーストに注意**。

## 高速化：時間蓄積
**雲のレイマーチは重い**ので、**画面全体を毎フレーム描かず、1/4 の画素だけ描いて、時間をかけて埋めます**。

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
| **低解像度で描く** | **半分／1/4 の解像度**で**レイマーチ**し、**アップサンプル** |
| **ブルー ノイズ ジッター** | **フレームごとに開始位置を変えて、平均で滑らか** |
| **履歴の再投影** | **前フレームの雲をカメラ移動分だけ動かす**（雲は遠いので回転だけで近似できる） |
| **層の距離を使う** | **雲までの距離（深度）を持って、再投影の精度を上げる** |
| **早期の打ち切り** | **透過率が低ければ打ち切る** |

### 4×4 の更新パターンの仕組み

Horizon Zero Dawn の方式は、画面を 4×4 画素のブロックに区切り、各ブロックの 16 画素のうち、毎フレーム<strong>1 画素だけ</strong>をレイマーチします。更新する画素の位置は、ブルー ノイズや決まった順列で、フレームごとに変えます。16 フレームで、全画素が一巡します。

更新しなかった 15 画素は、前フレームの結果を再投影して使います。つまり、毎フレームのレイマーチは全画素の 1/16 で済み、コストは 1/16 になります（実際には、再投影とアップサンプルのコストが加わります）。再投影は、カメラの動きに合わせて、前フレームの画像を今のフレームの画素に対応づける処理です。雲は遠くにあるので、カメラの平行移動を無視し、回転だけで再投影しても、見た目の破綻は小さくて済みます。

<!-- fig:cloud-bayer:begin -->

<svg class="fig illust motion" data-fig="cloud-bayer" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-bayer" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">4×4 の更新: 1 フレームに 1/16 だけ描き、16 フレームで全部そろう</text>
<rect x="150" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="90" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0965;0.0968;1.0000" values="0;0;1;1"/></rect>
<rect x="150" y="90" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.1126;0.1129;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="179.0" y="125.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">1</text>
<rect x="212" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="90" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5804;0.5806;1.0000" values="0;0;1;1"/></rect>
<rect x="212" y="90" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5481;0.5484;0.5965;0.5968;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="241.0" y="125.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">11</text>
<rect x="274" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="90" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;1.0000" values="0;0;1;1"/></rect>
<rect x="274" y="90" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1610;0.1613;0.2094;0.2097;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="303.0" y="125.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">3</text>
<rect x="336" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="90" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4836;0.4839;1.0000" values="0;0;1;1"/></rect>
<rect x="336" y="90" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;0.4997;0.5000;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="365.0" y="125.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">9</text>
<rect x="150" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="152" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3385;0.3387;1.0000" values="0;0;1;1"/></rect>
<rect x="150" y="152" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3062;0.3065;0.3546;0.3548;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="179.0" y="187.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">6</text>
<rect x="212" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="152" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.8223;0.8226;1.0000" values="0;0;1;1"/></rect>
<rect x="212" y="152" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7901;0.7903;0.8385;0.8387;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="241.0" y="187.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">16</text>
<rect x="274" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="152" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4352;0.4355;1.0000" values="0;0;1;1"/></rect>
<rect x="274" y="152" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4030;0.4032;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="303.0" y="187.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">8</text>
<rect x="336" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="152" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7255;0.7258;1.0000" values="0;0;1;1"/></rect>
<rect x="336" y="152" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6933;0.6935;0.7417;0.7419;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="365.0" y="187.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">14</text>
<rect x="150" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="214" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1449;0.1452;1.0000" values="0;0;1;1"/></rect>
<rect x="150" y="214" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1126;0.1129;0.1610;0.1613;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="179.0" y="249.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">2</text>
<rect x="212" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="214" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6288;0.6290;1.0000" values="0;0;1;1"/></rect>
<rect x="212" y="214" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5965;0.5968;0.6449;0.6452;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="241.0" y="249.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">12</text>
<rect x="274" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="214" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2417;0.2419;1.0000" values="0;0;1;1"/></rect>
<rect x="274" y="214" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2094;0.2097;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="303.0" y="249.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">4</text>
<rect x="336" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="214" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5320;0.5323;1.0000" values="0;0;1;1"/></rect>
<rect x="336" y="214" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4997;0.5000;0.5481;0.5484;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="365.0" y="249.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">10</text>
<rect x="150" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="276" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2903;1.0000" values="0;0;1;1"/></rect>
<rect x="150" y="276" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.3062;0.3065;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="179.0" y="311.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">5</text>
<rect x="212" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="276" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7739;0.7742;1.0000" values="0;0;1;1"/></rect>
<rect x="212" y="276" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7417;0.7419;0.7901;0.7903;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="241.0" y="311.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">15</text>
<rect x="274" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="276" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;1.0000" values="0;0;1;1"/></rect>
<rect x="274" y="276" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3546;0.3548;0.4030;0.4032;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="303.0" y="311.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">7</text>
<rect x="336" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="276" width="58" height="58" fill="#7daefa" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6772;0.6774;1.0000" values="0;0;1;1"/></rect>
<rect x="336" y="276" width="58" height="58" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6449;0.6452;0.6933;0.6935;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="365.0" y="311.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">13</text>
<text x="150" y="78" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">画面を 4×4 のブロックに分け、番号の順に 1 つずつ更新</text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">各ブロックの数字は、更新される順番<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1〜4 フレーム目: 離れた位置から順に描く<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3223;0.3226;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">5〜8 フレーム目: 隙間が埋まっていく<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3223;0.3226;0.5804;0.5806;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9〜16 フレーム目: 全ブロックが更新される<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5804;0.5806;0.8385;0.8387;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">残りは前フレームの結果を再投影して使う(= 時間蓄積)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.8385;0.8387;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-bayer:end -->

### 破綻とその対策

この方式の弱点は、動きが速いときです。カメラが急に回転したり、雲が速く動いたりすると、再投影した前フレームの画素が、今のフレームの内容と合わなくなります。対策は、再投影で参照した履歴が信頼できるかを調べることです。たとえば、再投影先が画面外ならそのフレームで強制的に新しく計算する、あるいは、今のフレームの周囲の画素の最小値と最大値の範囲に、履歴を収める（近傍クランプ）などの方法があります。また、新しく計算した画素は、前の履歴と混ぜず、すぐに置き換えるほうが、残像が出にくくなります。

雲の描画を低解像度の別のターゲットに行い、最後に空と合成する構成にしておくと、この更新方式を他のパスから独立させて扱えます。

## よくあるミス

??? failure "カメラを動かすと、雲がちらつく"
    **再投影の精度**を**上げ**、**履歴の拒否**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **一部の画素だけ更新して、重ねる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Clouds](index.md)
- [レイマーチ](raymarch.md)
- [TAA](../../postprocess/antialiasing/taa.md)
