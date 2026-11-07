---
title: Bottlenecks
tags:
  - 最適化
  - 3Dゲーム
---

# Bottlenecks

フレームが 20 ms かかっていて、16.7 ms に収めたいとします。ドロー コールを減らすべきかシェーダーを軽くすべきかテクスチャを小さくすべきか。どれも効く場面がありどれも効かない場面があります。ボトルネックでない所を直しても、フレーム時間はほとんど変わりません。そこで最初にやるのは直すことではなく、何が足を引っ張っているかを見分けることです。このページでは CPU と GPU の関係、GPU の中の段階、見分ける実験を数字で確かめながら整理します。最後に、GPU の区間時間を測る D3D11 のタイマーとピクセル側を軽くして切り分けるデバッグ用シェーダーを載せます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。フレーム時間のモデル（CPU と GPU の時間の組み合わせ）は、考え方を示すために自分で置いた値で、実機の測定値ではありません。D3D11 のコードは `g++ -fsyntax-only`（mingw の `<d3d11.h>`）で構文を確かめただけで、実行していません。HLSL は `fxc`（`ps_5_0`）に通しました。末尾の資料は今回は読んでいません。

!!! tip "ポイント"
    - CPU と GPU は並列に動くので、フレーム時間は `max(CPU, GPU)` です。CPU が 14 ms、GPU が 8 ms なら GPU を 2 倍速くしてもフレームは 14 ms のままです。直列に待ち合うと `CPU + GPU` になり同じ 8 ms ずつでも 16 ms（62 fps）に落ちます。
    - 解像度を縦横 0.5 倍にしたときピクセル側が重い GPU は 15.44 ms から 6.11 ms に縮みますが、頂点側が重い GPU は 15.11 ms から 12.78 ms、CPU が重いなら 15.00 ms のままです。
    - 三角形の脚が 1 ピクセルだと 2×2 のクアッドの単位で計算するので、有効に使われるのは 25% です。脚 32 ピクセルで 88.9% です。
    - 1080p の G-Buffer（4 バイトの RT が 4 枚 + 深度）は 39.6 MiB で、書き 1 回と読み 1 回を 60 fps で続けると 4.63 GiB/s の帯域を使います。4K では 4 倍の 18.54 GiB/s です。

!!! info "このページを読む前に"
    - [Optimization](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## CPU が重いか GPU が重いか {#cpu-gpu}

### 並列に動くから遅い方が決める {#parallel}

CPU は次のフレームの命令を作り GPU は前のフレームの命令を実行します。この 2 つは別のプロセッサーで同時に進みます。定常状態ではフレームの間隔は遅い方の時間になります。

<svg class="fig flow" viewBox="0 0 640 225" role="img" aria-label="CPU と GPU の並列"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">CPU 14 ms と GPU 8 ms の並列動作</text><text x="70" y="22" text-anchor="start" style="font-size:13px;font-weight:700">CPU 14 ms、GPU 8 ms。フレームは 14 ms ごと(遅い CPU が決める)</text><text x="30" y="80" text-anchor="middle" style="font-size:13px;font-weight:700">CPU</text><text x="30" y="150" text-anchor="middle" style="font-size:13px;font-weight:700">GPU</text><rect x="70.0" y="60" width="532.0" height="30" fill="rgba(229,72,77,0.35)" stroke="currentColor" stroke-width="1.5"/><text x="336.0" y="80" text-anchor="middle" style="font-size:11px;font-weight:400">フレーム 1 の更新・命令作成 14</text><rect x="602.0" y="130" width="304.0" height="30" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-width="1.5"/><text x="754.0" y="150" text-anchor="middle" style="font-size:11px;font-weight:400">描画 8</text><rect x="906.0" y="130" width="228.0" height="30" fill="rgba(150,150,150,0.18)" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/><text x="1020.0" y="150" text-anchor="middle" style="font-size:11px;font-weight:400">待ち 6</text><rect x="602.0" y="60" width="532.0" height="30" fill="rgba(229,72,77,0.35)" stroke="currentColor" stroke-width="1.5"/><text x="868.0" y="80" text-anchor="middle" style="font-size:11px;font-weight:400">フレーム 2 の更新・命令作成 14</text><rect x="1134.0" y="130" width="304.0" height="30" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-width="1.5"/><text x="1286.0" y="150" text-anchor="middle" style="font-size:11px;font-weight:400">描画 8</text><rect x="1438.0" y="130" width="228.0" height="30" fill="rgba(150,150,150,0.18)" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/><text x="1552.0" y="150" text-anchor="middle" style="font-size:11px;font-weight:400">待ち 6</text><rect x="1134.0" y="60" width="532.0" height="30" fill="rgba(229,72,77,0.35)" stroke="currentColor" stroke-width="1.5"/><text x="1400.0" y="80" text-anchor="middle" style="font-size:11px;font-weight:400">フレーム 3 の更新・命令作成 14</text><rect x="1666.0" y="130" width="304.0" height="30" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-width="1.5"/><text x="1818.0" y="150" text-anchor="middle" style="font-size:11px;font-weight:400">描画 8</text><rect x="1970.0" y="130" width="228.0" height="30" fill="rgba(150,150,150,0.18)" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/><text x="2084.0" y="150" text-anchor="middle" style="font-size:11px;font-weight:400">待ち 6</text><line x1="602.0" y1="45" x2="602.0" y2="175" stroke="currentColor" stroke-dasharray="5 4" opacity="0.5"/><line x1="1134.0" y1="45" x2="1134.0" y2="175" stroke="currentColor" stroke-dasharray="5 4" opacity="0.5"/><line x1="1666.0" y1="45" x2="1666.0" y2="175" stroke="currentColor" stroke-dasharray="5 4" opacity="0.5"/><text x="70" y="205" text-anchor="start" style="font-size:12px;font-weight:400">GPU を 2 倍速くしても、待ちが増えるだけでフレーム時間は 14 ms のまま</text></svg>

CPU が 14 ms、GPU が 8 ms のとき GPU は 8 ms 描いたあと 6 ms 遊びます。GPU の使用率は 8 / 14 = 57% です。このとき GPU のシェーダーを最適化して 8 ms を 4 ms にしても、フレームは 14 ms のままです。直す対象は CPU 側のコード（ドロー コールの発行、カリング、定数バッファの書き込み）です。

CPU と GPU の時間を組み合わせて数えました。

- CPU 4 ms、GPU 8 ms: パイプラインで 8.00 ms（125 fps）、直列なら 12.00 ms（83 fps）
- CPU 8 ms、GPU 8 ms: 8.00 ms（125 fps）、直列なら 16.00 ms（62 fps）
- CPU 12 ms、GPU 8 ms: 12.00 ms（83 fps）、直列なら 20.00 ms（50 fps）

パイプラインがうまく回ればフレーム時間は遅い方 1 つで決まります。直列の欄は CPU が GPU の結果を待つ処理（`Map` でのリードバックなど）が入ったときの姿です。8 ms ずつ使うのにフレームが 16 ms になるのは、片方が必ずもう片方を待っているからです。

### 先行するフレームの数 {#queue}

CPU が GPU より先に進める量をフレームのキューと呼びます。キューが深いほど CPU と GPU の時間のばらつきを吸収できます。その代わり入力から画面に出るまでの遅れが、1 フレーム分ずつ増えます。16.7 ms のフレームでキューが 1、2、3 フレームなら増える遅れは最大でそれぞれ 16.7 ms、33.3 ms、50.0 ms です。測るときはキューの深さも記録します。

### 見分け方 {#detect}

- CPU が重い: 解像度を下げても速くならない。GPU の使用率が低い。CPU のスレッドが描画の関数で時間を使っている
- GPU が重い: 解像度を下げると速くなる。GPU のタイムスタンプの合計がフレーム時間に近い
- 同期待ち: どちらの使用率も低いのに遅い。CPU が GPU の結果を待っている

最も手軽な実験は解像度を下げることです。次の節でどの結果が何を意味するかを数えます。

## 解像度で切り分ける {#resolution}

GPU の時間は解像度に依存しない部分（頂点、シャドウ、計算）とピクセル数に比例する部分（ピクセルシェーダー、ROP）の和でモデル化できます。`GPU = 固定費 + 1 Mpx あたりの時間 × Mpx` です。3 つの場合を置いて縦横の解像度を 1.00、0.75、0.50 倍にしたときのフレーム時間を数えました（値は説明用の仮定です）。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="解像度を下げたときの反応"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">解像度を下げたときのフレーム時間</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="141.4,185.5 320.0,144.4 498.6,87.0"/><circle cx="141.4" cy="185.5" r="4" fill="#e5484d"/><circle cx="320.0" cy="144.4" r="4" fill="#e5484d"/><circle cx="498.6" cy="87.0" r="4" fill="#e5484d"/><rect x="370" y="30" width="14" height="4" fill="#e5484d"/><text x="390" y="36" text-anchor="start" style="font-size:11px;font-weight:400">ピクセル側が重い GPU</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="141.4,115.1 320.0,104.9 498.6,90.5"/><circle cx="141.4" cy="115.1" r="4" fill="#4c8bf5"/><circle cx="320.0" cy="104.9" r="4" fill="#4c8bf5"/><circle cx="498.6" cy="90.5" r="4" fill="#4c8bf5"/><rect x="370" y="48" width="14" height="4" fill="#4c8bf5"/><text x="390" y="54" text-anchor="start" style="font-size:11px;font-weight:400">頂点・固定費が重い GPU</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="141.4,91.7 320.0,91.7 498.6,91.7"/><circle cx="141.4" cy="91.7" r="4" fill="#2e9e5b"/><circle cx="320.0" cy="91.7" r="4" fill="#2e9e5b"/><circle cx="498.6" cy="91.7" r="4" fill="#2e9e5b"/><rect x="370" y="66" width="14" height="4" fill="#2e9e5b"/><text x="390" y="72" text-anchor="start" style="font-size:11px;font-weight:400">CPU が重い</text><text x="141.42857142857142" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.50</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="498.5714285714286" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1.00</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="201.22222222222223" text-anchor="end" style="font-size:11px;font-weight:400">5</text><text x="62" y="148.44444444444446" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="62" y="95.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">15</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">縦横の解像度の倍率(1.00 = 1080p、0.50 = 960×540)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">フレーム時間(ms)</text></svg>

- ピクセル側が重い GPU（CPU 6 ms、固定費 3 ms + 6 ms/Mpx）: 15.44、10.00、6.11 ms
- 頂点・固定費が重い GPU（CPU 6 ms、固定費 12 ms + 1.5 ms/Mpx）: 15.11、13.75、12.78 ms
- CPU が重い（CPU 15 ms、GPU は 9.22、6.50、4.56 ms）: 15.00 ms のまま

1 つ目は解像度に応じてほぼ比例して縮みます。2 つ目は縮みはしますが固定費の 12 ms が残ります。3 つ目は GPU 時間が縮んでも CPU の 15 ms が下限になるので、まったく変わりません。この 3 つの反応の違いでどちら側を直すかを決められます。

ピクセル数は解像度の縦横の積です。1280×720 は 0.922 Mpx（1080p の 0.444 倍）、1600×900 は 1.440 Mpx（0.694 倍）、1920×1080 は 2.074 Mpx（1 倍）、2560×1440 は 3.686 Mpx（1.778 倍）、3840×2160 は 8.294 Mpx（4.000 倍）です。縦横を 0.5 倍にするとピクセル数は 0.25 倍なので、ピクセル側のコストは 1/4 になります。同じピクセルを何度も塗る（オーバードロー）とこの倍率にさらに回数が掛かります（[Overdraw](overdraw.md)）。

## CPU 側が重い理由 {#cpu}

### ドロー コール {#draw-calls}

1 回の描画命令ごとにドライバーが状態を検査し、GPU 用のコマンドに変換します。この処理は CPU で動くので、数千から数万の描画命令になると CPU が詰まります。対策はバッチ、インスタンシング、GPU Driven です（[Draw Calls](../draw-call/draw-calls.md)・[GPU Driven](../draw-call/gpu-driven.md)）。

### 状態の切り替え {#state}

シェーダー、テクスチャ、ブレンド設定を変えるたびにドライバー側の検査とコマンドの生成が走ります。描画の順番を状態ごとにそろえる（ソートする）と切り替えの回数が減ります。

### カリングと定数バッファ {#culling}

物体 1 つずつ「見えるか」を CPU で調べると、物体の数に比例して時間がかかります。階層構造を使うか GPU に任せます（[Culling](../draw-call/culling.md)）。定数バッファは物体ごとに別々に書くと更新が増えるので、まとめて 1 つのバッファに書きます。

### ドライバーの検証 {#driver}

DX11 はドライバーが多くの検証をします。DX12 ではその仕事の多くをアプリ側に任せるので、CPU の負担を減らしやすい代わりにアプリ側の責任が増えます。

## GPU 側が重い理由 {#gpu}

GPU の処理はいくつかの段階に分かれていて、どれかが詰まると全体が遅くなります。

| 段階 | 仕事 | 参照 |
| --- | --- | --- |
| 頂点処理 | 頂点の位置を計算 | [Level of Detail](../draw-call/lod.md) |
| ラスタライズ | 三角形をピクセルに分解 | [Overdraw](overdraw.md) |
| ピクセル処理 | 色を計算 | [Shader Cost](shader-cost.md) |
| 出力（ROP） | 深度テスト・ブレンド・書き込み | [Overdraw](overdraw.md) |
| メモリ帯域 | テクスチャ・バッファの読み書き | [Memory Bandwidth](bandwidth.md) |

### 頂点処理 {#vertex}

頂点処理は頂点の数に比例します。画面外や隠れている物の頂点も計算されるので、カリングと LOD で減らします。解像度を下げても速くならないのが、頂点側の特徴です。

### ラスタライズと小さい三角形 {#raster}

GPU はピクセルを 2×2 のクアッド単位で計算します。三角形が覆うピクセルを 1 つでも含むクアッドは、4 ピクセル分が計算されます（隣のピクセルとの差分を取る微分の計算のためです）。三角形が小さいと計算されたのに使われないピクセルが増えます。

直角二等辺三角形をサブピクセルの位置を 64 通りずらして置き覆われるピクセルと、触れるクアッドの数を数えました。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="小さい三角形の効率"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">2×2 クアッドの効率</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,202.5 170.0,184.3 228.5,166.8 270.0,153.7 370.0,122.7 470.0,97.8 570.0,81.1"/><circle cx="70.0" cy="202.5" r="4" fill="#e5484d"/><text x="76.0" y="194.5" text-anchor="start" style="font-size:11px;font-weight:700">25%</text><circle cx="170.0" cy="184.3" r="4" fill="#e5484d"/><text x="176.0" y="176.26" text-anchor="start" style="font-size:11px;font-weight:700">35%</text><circle cx="228.5" cy="166.8" r="4" fill="#e5484d"/><text x="234.49625007211563" y="158.78" text-anchor="start" style="font-size:11px;font-weight:700">44%</text><circle cx="270.0" cy="153.7" r="4" fill="#e5484d"/><text x="276.0" y="145.67000000000002" text-anchor="start" style="font-size:11px;font-weight:700">51%</text><circle cx="370.0" cy="122.7" r="4" fill="#e5484d"/><text x="376.0" y="114.7" text-anchor="start" style="font-size:11px;font-weight:700">67%</text><circle cx="470.0" cy="97.8" r="4" fill="#e5484d"/><text x="476.0" y="89.81000000000003" text-anchor="start" style="font-size:11px;font-weight:700">80%</text><circle cx="570.0" cy="81.1" r="4" fill="#e5484d"/><text x="576.0" y="73.09" text-anchor="start" style="font-size:11px;font-weight:700">89%</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="170.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="270.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">4</text><text x="370.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">8</text><text x="470.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">16</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">32</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0%</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">25%</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">50%</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">75%</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">100%</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">三角形の脚の長さ(ピクセル。直角二等辺三角形)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">有効に使われたピクセルの割合</text></svg>

- 脚 1 ピクセル: 覆われる 0.62 px に対して、計算される 2.50 px（有効 25.0%）
- 2 ピクセル: 2.25 px に対して 6.50 px（34.6%）
- 4 ピクセル: 8.50 px に対して 16.75 px（50.7%）
- 8 ピクセル: 33.00 px に対して 49.25 px（67.0%）
- 16 ピクセル: 130.00 px に対して 162.25 px（80.1%）
- 32 ピクセル: 516.00 px に対して 580.25 px（88.9%）

脚が 4 ピクセル以下の三角形では計算の半分以上が捨てられます。遠くのメッシュを LOD で減らすのは、頂点を減らすだけでなくこの無駄を減らす効果もあります。これは直角二等辺三角形での数字で、実際のメッシュの三角形は形も向きもばらばらです。傾向としての目安です。

### ピクセル処理と ROP {#pixel}

ピクセル処理はピクセル数 × シェーダーの計算量です。ライトが多いブレンドが重なる MSAA、高解像度、のいずれかで増えます。解像度に比例するので解像度の実験でそのまま現れます。

### メモリ帯域 {#bandwidth}

GPU の計算能力は大きく伸びていますが、メモリとのやりとりの速さは伸びが遅いので、計算を減らすよりメモリアクセスを減らすほうが効く場面が増えています。見積もりの例として 1080p の G-Buffer を数えました。4 バイトの RT が 4 枚と 4 バイトの深度で、1 ピクセル 20 バイトです。

- 1080p: 1 フレームの G-Buffer は 39.6 MiB。書き 1 回 + 読み 1 回で 79.1 MiB、60 fps で 4.63 GiB/s
- 4K: 158.2 MiB、書き + 読みを 60 fps で続けると 18.54 GiB/s

これは G-Buffer だけの数字です。シャドウ マップ、ポストエフェクト、テクスチャの読み込みが加わります。Deferred でライティングを軽くしても、G-Buffer の書き読みで帯域が増えるというトレードオフが現れます（[Memory Bandwidth](bandwidth.md)）。

## 見分ける実験 {#experiments}

実験は 1 つだけ変えてフレーム時間を比べます。

1. 解像度を下げます。速くなればピクセル側（シェーダー・帯域・フィルレート）です。変わらなければ頂点側か CPU です。
2. ピクセルシェーダーを定数の色にします。速くなればピクセルシェーダーが重いです。
3. テクスチャを 1×1 に差し替えます。速くなればテクスチャの帯域かキャッシュが足りません。
4. ライトの数を減らします。速くなればライティングが重いです。
5. ドロー コールを半分にします。速くなれば CPU（命令）か頂点です。
6. ポストエフェクトを切ります。速くなれば画面全体の効果が重いです。

実験 2、3、4 はシェーダーに切り替えを入れておくと再コンパイルなしで試せます。

```hlsl
cbuffer DebugCB : register(b0) {
  uint  gDebugMode;   // 0 = 通常、1 = 定数色、2 = 1x1 テクスチャで読む、3 = ライティングを飛ばす
  float3 gPad;        // 16 バイト境界の詰め物
};
```

`gDebugMode` で実験を切り替えます。CPU から定数バッファに書くだけなので、ゲーム中に数字キーで切り替えられます。`gPad` は `uint` の後ろを 16 バイトの境界に合わせる詰め物です。

```hlsl
Texture2D    gAlbedo : register(t0);   // 通常のテクスチャ
Texture2D    gTiny   : register(t1);   // 1x1 の白いテクスチャ(キャッシュに必ず載る)
SamplerState gSamp   : register(s0);

struct PsIn {
  float4 pos    : SV_Position;
  float2 uv     : TEXCOORD0;
  float3 normal : NORMAL;
};
```

`gTiny` は 1×1 の白いテクスチャです。必ずキャッシュに載るのでこれに差し替えて速くなれば、本来のテクスチャの読み込みが帯域かキャッシュのミスで遅かった、と分かります。

```hlsl
float3 HeavyLighting(float3 albedo, float3 n) {      // 本来の重いシェーディング(ここでは代わりの計算)
  float3 sum = 0;
  [loop] for (int i = 0; i < 16; ++i)               // ライト 16 個分の計算
    sum += albedo * saturate(dot(n, normalize(float3(i - 8, 4, 2))));
  return sum / 16.0;
}
```

`HeavyLighting` は本来のシェーディングの代わりに置いた計算です。ライト 16 個分を `[loop]` で回しています。実際のゲームではここが本物のライティングです。

```hlsl
float4 ExperimentPS(PsIn i) : SV_Target {
  if (gDebugMode == 1) return float4(0.5, 0.5, 0.5, 1);                  // 速くなる => ピクセルシェーダー全体が重い
  float3 albedo = (gDebugMode == 2) ? gTiny.Sample(gSamp, float2(0.5, 0.5)).rgb  // 速くなる => テクスチャの帯域・キャッシュ
                                    : gAlbedo.Sample(gSamp, i.uv).rgb;
  if (gDebugMode == 3) return float4(albedo, 1);                          // 速くなる => ライティングの計算が重い
  return float4(HeavyLighting(albedo, normalize(i.normal)), 1);
}
```

モード 1 はテクスチャも計算も飛ばして定数の色を返します。これで速くなればピクセルシェーダー全体が重いと分かります。モード 2 は 1×1 のテクスチャを読むので、帯域だけを外した状態です。モード 3 はライティングの計算だけを外した状態です。3 つの結果を比べると重いのが計算かテクスチャかそれ以外かが絞れます。

## 測る道具 {#tools}

- PIX on Windows: DX のフレームをキャプチャして、各描画命令の GPU 時間と状態を見ます。
- RenderDoc: フレームのキャプチャ。描画命令、テクスチャ、シェーダーを確認します。
- GPU ベンダーのツール（NVIDIA Nsight、AMD Radeon GPU Profiler、Intel GPA）: 帯域、占有率、キャッシュなど GPU 内部のカウンターを見ます。
- Visual Studio のプロファイラー: CPU 側の時間を見ます（[プロファイラー](../../vs/profiler.md)）。

自分のコードに区間の GPU 時間を出したいときは、タイムスタンプのクエリを使います。次のクラスは `D3D11_QUERY_TIMESTAMP_DISJOINT` で周波数を取り開始と終了のタイムスタンプの差を ms に直します。構文は確かめましたが実行はしていません。ここからコードを数行ずつ見ます。

```cpp
  bool Init(ID3D11Device* device) {
    D3D11_QUERY_DESC disjoint_desc = {D3D11_QUERY_TIMESTAMP_DISJOINT, 0};  // 周波数と「測定が壊れたか」を返す
    D3D11_QUERY_DESC stamp_desc = {D3D11_QUERY_TIMESTAMP, 0};              // GPU 内部の時刻(tick)を返す
```

クエリは 2 種類です。`TIMESTAMP` は GPU の時刻を tick で返しますが、その tick が 1 秒に何回かは別の問い合わせです。それが `TIMESTAMP_DISJOINT` で周波数 `Frequency` と測定中にクロックが変わったかどうかの `Disjoint` を返します。

```cpp
  void Begin(ID3D11DeviceContext* ctx) {
    Slot& s = slots_[write_];
    ctx->Begin(s.disjoint.Get());  // Disjoint は Begin / End で区間を囲む
    ctx->End(s.begin.Get());       // タイムスタンプは End だけを呼ぶ(Begin は不要)
  }
```

`TIMESTAMP` のクエリは `Begin` を呼ばず `End` だけを呼びます。`End` を呼んだ時点の GPU の時刻が記録されます。一方 `DISJOINT` は `Begin` と `End` で区間を囲みます。この囲みの中に 2 つのタイムスタンプが入る必要があります。

```cpp
    if (ctx->GetData(s.disjoint.Get(), &dj, sizeof(dj), D3D11_ASYNC_GETDATA_DONOTFLUSH) != S_OK) return false;
```

結果は GPU が処理し終えるまで取れません。`GetData` が `S_OK` 以外ならまだ終わっていないので、待たずに諦めます。待つと CPU が止まって測っているのに測定が遅さを作ってしまいます。そのため、クエリは 4 フレーム分のリング バッファに置き数フレーム前の組を読みます。

```cpp
    if (dj.Disjoint) return false;  // クロックが途中で変わった(省電力など)。この測定は捨てる
    *out_ms = static_cast<double>(t1 - t0) / static_cast<double>(dj.Frequency) * 1000.0;  // tick を ms に直す
```

`Disjoint` が真なら測定の途中で GPU のクロックが変わっているので、その値は信用できません。捨てます。正常なら `(t1 − t0) / Frequency` が秒で 1000 を掛けて ms にします。区間の全体を末尾に載せました。

## 優先順位の考え方 {#priority}

1. CPU が重いか GPU が重いかを決めます。
2. GPU なら最も重い段階（頂点、ピクセル、帯域）を絞ります。
3. 効果が大きく簡単なものから直します（カリング、LOD、解像度、フォーマット）。
4. それでも足りなければ大きな構造の変更（Deferred、Clustered、GPU Driven）を検討します。手間も大きいです。
5. 直したらもう一度測ります。1 つ直すとボトルネックは次の場所に移ります。

## よくあるミス {#mistakes}

??? failure "GPU が遅いのに、ドロー コールを減らす"
    原因は CPU がボトルネックでないのに CPU 側を直していることです。GPU が 15 ms で CPU が 6 ms なら CPU を 3 ms にしても、フレームは変わりません。

??? failure "使用率が高いから、GPU が限界だと思う"
    「忙しい」と「無駄がない」は別です。待っている時間も使用率に含まれることがあります。小さい三角形のクアッドの無駄のように忙しくても成果が少ない状態があります。

??? failure "Debug ビルドで測る"
    Debug は最適化がなく、標準ライブラリも遅いので CPU の時間が何倍にもなります。必ず Release で測ります（[コンパイラとビルド](../../basics/compiler.md)）。

??? failure "VSync をつけたまま測る"
    フレームが 60 fps に固定されて、余裕が分かりません。GPU の時間が 10 ms でも 16 ms でもどちらも 16.7 ms と出ます。切って測るか GPU の時間そのものを測ります。

??? failure "平均だけ見て、スパイクを見逃す"
    平均が 10 ms でも数フレームに 1 回 40 ms のスパイクがあれば、見た目はカクつきます。最悪のフレームを見ます（[フレーム時間の設計](../../optimize/frame-budget.md)）。

??? failure "GPU タイマーが毎回 `S_FALSE` で、値が取れない"
    原因は `GetData` をクエリを発行した直後のフレームで呼んでいることです。GPU は CPU より数フレーム遅れているので、3〜4 フレーム前のクエリを読みます。待つ（フラグを付けずに `S_OK` が返るまで回す）と CPU が止まって測定自体がフレームを遅くします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] フレーム時間は `max(CPU, GPU)`。まず、どちらが遅いかを見極める
    - [x] 解像度を 0.5 倍にして比例して縮めばピクセル側、固定費が残れば頂点側、変わらなければ CPU
    - [x] 小さい三角形は 2×2 のクアッドで無駄が出る。脚 1 ピクセルで有効 25%、32 ピクセルで 88.9%
    - [x] 帯域は計算より伸びが遅い。1080p の G-Buffer は 4.63 GiB/s(60 fps)
    - [x] 実験は 1 つずつ変えて測る。GPU タイマーは `Disjoint` を確かめ数フレーム遅れで読む

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>

struct Res { const char* name; int w, h; };

// 1 フレームの時間(ms)のモデル。CPU と GPU がパイプラインで並列に動くとき、定常状態のフレーム時間は遅い方で決まる。
double FrameMs(double cpu_ms, double gpu_ms) { return std::max(cpu_ms, gpu_ms); }

// GPU 時間のモデル。解像度に依存しない部分(頂点・シャドウ・計算)と、ピクセル数に比例する部分(ピクセルシェーダー・ROP)の和。
double GpuMs(double fixed_ms, double per_mpix_ms, double mpix) { return fixed_ms + per_mpix_ms * mpix; }

int main() {
  // 1. 解像度ごとのピクセル数と、1080p に対する倍率。
  std::printf("-- pixel counts\n");
  const Res res[] = {{"720p", 1280, 720}, {"900p", 1600, 900}, {"1080p", 1920, 1080}, {"1440p", 2560, 1440}, {"4K", 3840, 2160}};
  const double p1080 = 1920.0 * 1080.0;                  // 基準
  for (const Res& r : res) {
    const double px = static_cast<double>(r.w) * r.h;    // ピクセル数
    std::printf("%-5s %4dx%4d = %8.0f px (%.3f Mpx), x%.3f of 1080p\n", r.name, r.w, r.h, px, px / 1e6, px / p1080);
  }

  // 2. 解像度を半分(縦横それぞれ 1/2 ではなく、ピクセル数 1/4)にしたときのフレーム時間。
  //    CPU 側が重い場合と GPU 側が重い場合で、反応が違う。
  std::printf("-- resolution experiment (frame ms at scale of each axis)\n");
  struct Case { const char* name; double cpu, fixed, per_mpix; };
  const Case cases[] = {
      {"pixel-bound GPU", 6.0, 3.0, 6.0},   // GPU 3 + 6*2.07 = 15.4 ms (CPU は余裕)
      {"vertex-bound GPU", 6.0, 12.0, 1.5},  // GPU 12 + 1.5*2.07 = 15.1 ms
      {"CPU-bound", 15.0, 3.0, 3.0},         // GPU 3 + 3*2.07 = 9.2 ms
  };
  for (const Case& c : cases) {
    std::printf("%s (cpu %.1f ms, gpu fixed %.1f ms + %.1f ms/Mpx)\n", c.name, c.cpu, c.fixed, c.per_mpix);
    for (double s : {1.0, 0.75, 0.5}) {
      const double mpix = p1080 * s * s / 1e6;                       // 縦横を s 倍
      const double gpu = GpuMs(c.fixed, c.per_mpix, mpix);
      std::printf("  scale %.2f: %.2f Mpx, gpu %5.2f ms, frame %5.2f ms (%s)\n", s, mpix, gpu, FrameMs(c.cpu, gpu),
                  c.cpu > gpu ? "CPU limits" : "GPU limits");
    }
  }

  // 3. CPU と GPU がどちらも 8 ms ずつ使うとき、直列(同期待ち)なら 16 ms、パイプラインなら 8 ms。
  std::printf("-- serial vs pipelined\n");
  for (double a : {4.0, 8.0, 12.0}) {
    const double b = 8.0;
    std::printf("cpu %4.1f gpu %4.1f: pipelined %5.2f ms (%.0f fps), serial %5.2f ms (%.0f fps)\n", a, b, FrameMs(a, b),
                1000.0 / FrameMs(a, b), a + b, 1000.0 / (a + b));
  }

  // 4. 先行レンダリングのキュー(CPU が GPU より何フレーム先に進めるか)と入力遅延。
  std::printf("-- queued frames and latency\n");
  for (int q : {1, 2, 3}) {
    std::printf("queue %d frames at 16.7 ms: up to %.1f ms extra latency\n", q, q * 16.667);
  }

  // 5. G-Buffer の帯域の見積もり。1080p、RT 4 枚(各 4 バイト/px) + 深度 4 バイト/px。書き 1 回 + ライティングで読み 1 回。
  std::printf("-- g-buffer traffic at 1080p, 60 fps\n");
  const double bytes_px = 4 * 4 + 4;                                        // RT 4 枚 + 深度
  const double write_mb = p1080 * bytes_px / (1024.0 * 1024.0);            // 1 フレームの書き込み
  std::printf("g-buffer = %.1f MiB per frame, write+read = %.1f MiB, at 60 fps = %.2f GiB/s\n", write_mb, write_mb * 2,
              write_mb * 2 * 60 / 1024.0);
  const double p4k = 3840.0 * 2160.0;
  const double w4k = p4k * bytes_px / (1024.0 * 1024.0);
  std::printf("4K: g-buffer = %.1f MiB, write+read at 60 fps = %.2f GiB/s\n", w4k, w4k * 2 * 60 / 1024.0);

  // 6. 小さい三角形のコスト。GPU はピクセルを 2x2 のクアッドの単位で計算する。三角形が覆うピクセルを 1 つでも含むクアッドは、4 ピクセル分すべて計算される。
  //    直角二等辺三角形(直角の頂点が (ox, oy)、脚の長さ leg)を、サブピクセルの位置をずらして何通りも置き、
  //    覆われるピクセル(中心が三角形の内側)と、触れるクアッドの数を数える。
  std::printf("-- quad overshading (right isosceles triangle, averaged over 64 x 64 sub-pixel offsets)\n");
  for (double leg : {1.0, 2.0, 3.0, 4.0, 8.0, 16.0, 32.0}) {
    double covered_sum = 0.0, worked_sum = 0.0;
    const int kSteps = 8;                                                   // 8 x 8 のずらし。ずらしを 2 倍の細かさで 2 回試す代わりに 64 通り
    int trials = 0;
    for (int ix = 0; ix < kSteps; ++ix) {
      for (int iy = 0; iy < kSteps; ++iy) {
        const double ox = 10.0 + (ix + 0.5) / kSteps * 2.0;                // クアッドの格子に対するずれ(0〜2 ピクセル)
        const double oy = 10.0 + (iy + 0.5) / kSteps * 2.0;
        int covered = 0;
        bool quad_hit[64][64] = {};                                         // 触れたクアッド
        for (int py = 0; py < 128; ++py) {
          for (int px = 0; px < 128; ++px) {
            const double cx = px + 0.5 - ox, cy = py + 0.5 - oy;          // ピクセル中心の、三角形の直角の頂点からの位置
            if (cx >= 0.0 && cy >= 0.0 && cx + cy <= leg) {                 // 三角形の内側
              ++covered;
              quad_hit[py / 2][px / 2] = true;
            }
          }
        }
        int quads = 0;
        for (auto& row : quad_hit) for (bool b : row) quads += b ? 1 : 0;
        covered_sum += covered;
        worked_sum += quads * 4.0;
        ++trials;
      }
    }
    const double covered = covered_sum / trials, worked = worked_sum / trials;
    std::printf("leg %5.1f px: area %7.1f px, covered %7.2f px, worked %7.2f px, efficiency %5.1f%%\n", leg, leg * leg / 2.0, covered,
                worked, covered > 0.0 ? covered / worked * 100.0 : 0.0);
  }
}
```

```text title="実行結果"
-- pixel counts
720p  1280x 720 =   921600 px (0.922 Mpx), x0.444 of 1080p
900p  1600x 900 =  1440000 px (1.440 Mpx), x0.694 of 1080p
1080p 1920x1080 =  2073600 px (2.074 Mpx), x1.000 of 1080p
1440p 2560x1440 =  3686400 px (3.686 Mpx), x1.778 of 1080p
4K    3840x2160 =  8294400 px (8.294 Mpx), x4.000 of 1080p
-- resolution experiment (frame ms at scale of each axis)
pixel-bound GPU (cpu 6.0 ms, gpu fixed 3.0 ms + 6.0 ms/Mpx)
  scale 1.00: 2.07 Mpx, gpu 15.44 ms, frame 15.44 ms (GPU limits)
  scale 0.75: 1.17 Mpx, gpu 10.00 ms, frame 10.00 ms (GPU limits)
  scale 0.50: 0.52 Mpx, gpu  6.11 ms, frame  6.11 ms (GPU limits)
vertex-bound GPU (cpu 6.0 ms, gpu fixed 12.0 ms + 1.5 ms/Mpx)
  scale 1.00: 2.07 Mpx, gpu 15.11 ms, frame 15.11 ms (GPU limits)
  scale 0.75: 1.17 Mpx, gpu 13.75 ms, frame 13.75 ms (GPU limits)
  scale 0.50: 0.52 Mpx, gpu 12.78 ms, frame 12.78 ms (GPU limits)
CPU-bound (cpu 15.0 ms, gpu fixed 3.0 ms + 3.0 ms/Mpx)
  scale 1.00: 2.07 Mpx, gpu  9.22 ms, frame 15.00 ms (CPU limits)
  scale 0.75: 1.17 Mpx, gpu  6.50 ms, frame 15.00 ms (CPU limits)
  scale 0.50: 0.52 Mpx, gpu  4.56 ms, frame 15.00 ms (CPU limits)
-- serial vs pipelined
cpu  4.0 gpu  8.0: pipelined  8.00 ms (125 fps), serial 12.00 ms (83 fps)
cpu  8.0 gpu  8.0: pipelined  8.00 ms (125 fps), serial 16.00 ms (62 fps)
cpu 12.0 gpu  8.0: pipelined 12.00 ms (83 fps), serial 20.00 ms (50 fps)
-- queued frames and latency
queue 1 frames at 16.7 ms: up to 16.7 ms extra latency
queue 2 frames at 16.7 ms: up to 33.3 ms extra latency
queue 3 frames at 16.7 ms: up to 50.0 ms extra latency
-- g-buffer traffic at 1080p, 60 fps
g-buffer = 39.6 MiB per frame, write+read = 79.1 MiB, at 60 fps = 4.63 GiB/s
4K: g-buffer = 158.2 MiB, write+read at 60 fps = 18.54 GiB/s
-- quad overshading (right isosceles triangle, averaged over 64 x 64 sub-pixel offsets)
leg   1.0 px: area     0.5 px, covered    0.62 px, worked    2.50 px, efficiency  25.0%
leg   2.0 px: area     2.0 px, covered    2.25 px, worked    6.50 px, efficiency  34.6%
leg   3.0 px: area     4.5 px, covered    4.88 px, worked   11.12 px, efficiency  43.8%
leg   4.0 px: area     8.0 px, covered    8.50 px, worked   16.75 px, efficiency  50.7%
leg   8.0 px: area    32.0 px, covered   33.00 px, worked   49.25 px, efficiency  67.0%
leg  16.0 px: area   128.0 px, covered  130.00 px, worked  162.25 px, efficiency  80.1%
leg  32.0 px: area   512.0 px, covered  516.00 px, worked  580.25 px, efficiency  88.9%
```

GPU タイマーの全体です（構文のみ確認。実行していません）。

```cpp
#include <array>
#include <cstdint>

#include <d3d11.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

// 区間の GPU 時間を測るタイマー。1 区間につき、開始・終了のタイムスタンプと、周波数用の Disjoint クエリを 1 組持つ。
// 結果は GPU が処理し終えてから取れるので、数フレーム分のリングバッファを用意し、古い組から読む。
class GpuTimer {
 public:
  static constexpr int kFrames = 4;  // 結果が出るまで待てるフレーム数。2〜4 が一般的

  bool Init(ID3D11Device* device) {
    D3D11_QUERY_DESC disjoint_desc = {D3D11_QUERY_TIMESTAMP_DISJOINT, 0};  // 周波数と「測定が壊れたか」を返す
    D3D11_QUERY_DESC stamp_desc = {D3D11_QUERY_TIMESTAMP, 0};              // GPU 内部の時刻(tick)を返す
    for (Slot& s : slots_) {
      if (FAILED(device->CreateQuery(&disjoint_desc, &s.disjoint))) return false;  // 失敗したら測れない
      if (FAILED(device->CreateQuery(&stamp_desc, &s.begin))) return false;
      if (FAILED(device->CreateQuery(&stamp_desc, &s.end))) return false;
    }
    return true;
  }

  // 計測の開始。Disjoint クエリの Begin の後に、開始のタイムスタンプを打つ。
  void Begin(ID3D11DeviceContext* ctx) {
    Slot& s = slots_[write_];
    ctx->Begin(s.disjoint.Get());  // Disjoint は Begin / End で区間を囲む
    ctx->End(s.begin.Get());       // タイムスタンプは End だけを呼ぶ(Begin は不要)
  }

  // 計測の終了。終了のタイムスタンプを打ってから Disjoint を閉じる。
  void End(ID3D11DeviceContext* ctx) {
    Slot& s = slots_[write_];
    ctx->End(s.end.Get());
    ctx->End(s.disjoint.Get());
    s.pending = true;                // 結果待ち
    write_ = (write_ + 1) % kFrames;  // 次のフレームは次の組を使う
  }

  // 結果の回収。まだ終わっていなければ false を返し、待たない(待つと CPU が止まる)。
  bool Collect(ID3D11DeviceContext* ctx, double* out_ms) {
    Slot& s = slots_[read_];
    if (!s.pending) return false;  // この組はまだ使われていない
    D3D11_QUERY_DATA_TIMESTAMP_DISJOINT dj = {};
    // D3D11_ASYNC_GETDATA_DONOTFLUSH: コマンドをここで GPU に押し出さない。S_FALSE ならまだ終わっていない。
    if (ctx->GetData(s.disjoint.Get(), &dj, sizeof(dj), D3D11_ASYNC_GETDATA_DONOTFLUSH) != S_OK) return false;
    uint64_t t0 = 0, t1 = 0;
    if (ctx->GetData(s.begin.Get(), &t0, sizeof(t0), D3D11_ASYNC_GETDATA_DONOTFLUSH) != S_OK) return false;
    if (ctx->GetData(s.end.Get(), &t1, sizeof(t1), D3D11_ASYNC_GETDATA_DONOTFLUSH) != S_OK) return false;
    s.pending = false;
    read_ = (read_ + 1) % kFrames;
    if (dj.Disjoint) return false;  // クロックが途中で変わった(省電力など)。この測定は捨てる
    *out_ms = static_cast<double>(t1 - t0) / static_cast<double>(dj.Frequency) * 1000.0;  // tick を ms に直す
    return true;
  }

 private:
  struct Slot {
    ComPtr<ID3D11Query> disjoint, begin, end;
    bool pending = false;
  };
  std::array<Slot, kFrames> slots_;
  int write_ = 0, read_ = 0;
};
```

## 参考資料 {#references}

このページの数字は自分で置いたモデルを C++ で数えたもので、実機の測定ではありません。以下の資料は**今回は読んでいません**。

- Microsoft Learn, "Timestamp Queries"（`D3D11_QUERY_TIMESTAMP` と `D3D11_QUERY_TIMESTAMP_DISJOINT` の使い方）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（パイプラインのボトルネック、性能の章）
- PIX on Windows, RenderDoc, NVIDIA Nsight Graphics の各ドキュメント（ツールの使い方）

## 関連ページ {#related}

- [Optimization](index.md)
- [Memory Bandwidth](bandwidth.md)
- [Draw Calls](../draw-call/draw-calls.md)
- [Overdraw](overdraw.md)
- [計測（プロファイリング）](../../optimize/measure.md)
- [描画の最適化（入口）](../draw-call/overview.md)
