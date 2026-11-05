---
title: World-Space AO Comparison
tags:
  - 描画
---

# World-Space AO Comparison

画面の外にある壁や画面には写っていない天井の影響を AO に入れたいことがあります。スクリーン空間の AO は画面に写っている深度だけで遮蔽を推定するので、写っていない物は見えません。そこで、世界のジオメトリを何かの形で持っておきそこへ向けてレイや円錐を飛ばす方式が出てきました。RTAO は三角形（BVH）にレイを飛ばし、DFAO は符号付き距離場（SDF）を円錐で辿り VXAO はボクセルのミップを円錐で辿ります。このページでは 3 方式の違いを論文の数字と自分で出した数字で並べます。最後に、円錐トレースの HLSL とレイトレースの DXR コードをコメント付きの完成形で載せます。

!!! tip "ポイント"
    - 3 方式の違いは「トレース 1 回で何が分かるか」から決まる。RTAO は交差の有無、DFAO は距離つきの可視性、VXAO は占有度（遮蔽の割合）。
    - RTAO はレイが少ないとノイズが出る。N 本の平均の標準偏差は sqrt(p(1−p)/N) で、デノイズが前提になる。
    - 円錐は 1 本で広がりを扱えるので滑らかだが、円錐を太くすると遠くの遮蔽を過大に見積もる。
    - DFAO は剛体のメッシュ向きで、動く物は行列の更新で済む。VXAO は動く物を毎フレーム再ボクセル化する。
    - 実際に品質を左右するのは、方式の名前より解像度・円錐の本数・フィルターである。

!!! info "このページを読む前に"
    - [Ray-Traced, Distance-Field and Voxel AO](index.md)（このセクション全体の地図と、読む順番）
    - [RTAO](rtao.md)・[DFAO](dfao.md)・[VXAO](vxao.md)（各方式の仕組み）

## 読んだ資料 {#sources}

数字と手順は次の資料を読んで書いています。

- Daniel Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015 Advances in Real-Time Rendering in Games（スライド 60 枚と、ページ下のノートを全部読みました）。
- Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Pacific Graphics 2011（著者版の全文を読みました。このページで使うのは構造・円錐トレース・AO の節と結果の表です。間接光の節は詳しくは取り上げません）。
- Barré-Brisebois ほか, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems 第 25 章。読んだのは AO の節（25.2.3）とその前後です。章の全体は読んでいません。

RTAO の ms の数字は読んだ範囲に載っていません。BVH の更新コストも同じです。この 2 点は数字を書かずに載っていないと書きます。

## 3 方式の見取り図 {#overview}

<svg class="fig flow" viewBox="0 0 730 210" role="img" aria-label="3 方式の見取り図"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">同じ点から、3 方式は何を見るか</text><rect x="10" y="30" width="230" height="170" rx="8" fill="none" stroke="#94a3b8"/><text x="125" y="48" text-anchor="middle" font-size="13" fill="currentColor">RTAO</text><line x1="30" y1="170" x2="220" y2="170" stroke="#94a3b8" stroke-width="3"/><polygon points="160,170 160,90 185,90 185,170" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><line x1="90" y1="170" x2="0.7" y2="137.5" stroke="#4c8bf5" stroke-width="1.5"/><line x1="90" y1="170" x2="22.8" y2="102.8" stroke="#4c8bf5" stroke-width="1.5"/><line x1="90" y1="170" x2="57.5" y2="80.7" stroke="#4c8bf5" stroke-width="1.5"/><line x1="90" y1="170" x2="98.3" y2="75.4" stroke="#e5aa28" stroke-width="1.5"/><line x1="90" y1="170" x2="137.5" y2="87.7" stroke="#e5aa28" stroke-width="1.5"/><line x1="90" y1="170" x2="160.0" y2="115.5" stroke="#e5aa28" stroke-width="1.5"/><line x1="90" y1="170" x2="183.6" y2="153.5" stroke="#4c8bf5" stroke-width="1.5"/><line x1="90" y1="170" x2="183.6" y2="186.5" stroke="#4c8bf5" stroke-width="1.5"/><text x="125" y="190" text-anchor="middle" font-size="10" fill="currentColor">三角形(BVH)にレイを飛ばす</text><rect x="250" y="30" width="230" height="170" rx="8" fill="none" stroke="#94a3b8"/><text x="365" y="48" text-anchor="middle" font-size="13" fill="currentColor">DFAO</text><line x1="270" y1="170" x2="460" y2="170" stroke="#94a3b8" stroke-width="3"/><polygon points="400,170 400,100 425,100 425,170" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><line x1="310" y1="170" x2="395" y2="105" stroke="#4c8bf5" stroke-width="1.5"/><circle cx="322" cy="159" r="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="1"/><circle cx="340" cy="146" r="26" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="1"/><circle cx="362" cy="128" r="22" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="1"/><circle cx="385" cy="112" r="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="1"/><text x="365" y="190" text-anchor="middle" font-size="10" fill="currentColor">距離ぶんだけ飛ばして進む</text><rect x="490" y="30" width="230" height="170" rx="8" fill="none" stroke="#94a3b8"/><text x="605" y="48" text-anchor="middle" font-size="13" fill="currentColor">VXAO</text><rect x="510" y="110" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="510" y="130" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="510" y="150" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="540" y="110" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="540" y="130" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="540" y="150" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="570" y="110" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="570" y="130" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="570" y="150" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="600" y="110" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="600" y="130" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="600" y="150" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="630" y="110" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="630" y="130" width="30" height="20" fill="rgba(229,170,40,0.28)" stroke="#94a3b8" stroke-width="0.6"/><rect x="630" y="150" width="30" height="20" fill="rgba(229,170,40,0.28)" stroke="#94a3b8" stroke-width="0.6"/><rect x="660" y="110" width="30" height="20" fill="none" stroke="#94a3b8" stroke-width="0.6"/><rect x="660" y="130" width="30" height="20" fill="rgba(229,170,40,0.28)" stroke="#94a3b8" stroke-width="0.6"/><rect x="660" y="150" width="30" height="20" fill="rgba(229,170,40,0.28)" stroke="#94a3b8" stroke-width="0.6"/><polygon points="530,150 695,118 695,162" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="605" y="190" text-anchor="middle" font-size="10" fill="currentColor">円錐の太さに合うミップを読む</text></svg>

3 方式は世界を何で表すかが違います。RTAO は三角形を BVH に入れて、ハードウェアのレイトレースで当たりを調べます。DFAO はメッシュごとに SDF を持ちそれを 1 枚の大域 SDF にまとめて、距離で空間を飛ばしながら進みます。VXAO はシーンをボクセル化して、ミップ（子の平均を親に入れた階層）にしておき円錐の太さに合うミップを読みます。

トレース 1 回で分かることが、それぞれ違います。Wright のスライドは SDF は「表面の位置と法線しか持たない」ので、トレースから得られるのは可視性だけだと書いています。対してボクセルの円錐トレースは照明など任意の性質を集められます。AO だけなら可視性で足りるので SDF で足りますが、間接光まで同じデータで出したいならボクセルが有利です。

SDF が有利な点も書かれています。SDF は面の向きによらず同じように表せて、表面の近くでは線形に補間されるので、ボクセルより「各軸で約 4 倍高い解像度に相当する」と述べています。空の空間はまとめて飛ばせるので、固定の歩幅で進むボクセルより少ないステップで済みます。ボクセルは円錐に合わせた前フィルター（ミップ）が要りシーンが変わるたびに更新するコストが乗ります。

## 精度 {#accuracy}

### 薄い壁 {#thin}

Wright はボクセルの円錐トレースを「解像度が低く、建築に使われる壁を実用的なボクセルの大きさでは表せない」と評しています。SDF のほうも薄い面は負の値のテクセルを 1 つ内側に置けたときだけ表せる、と書いています。ただし、表面から離れた所の遮蔽は正確に出るので、空の遮蔽ではあまり目立たない、とも書いています。

自分で計算すると 512³ のボクセルで一辺 50 m のシーンを覆うと 1 ボクセルは約 0.098 m です。厚さ 10 cm の壁は 1 ボクセルにやっと収まる程度で、薄い壁はほぼ表せません。RTAO は三角形そのものにレイを当てるので、この制約がありません。

### 円錐が太いと過大になる {#wide-cone}

円錐を太くすると円錐の中心線から外れた小さな遮蔽物でも円錐全体が遮られたことになります。Crassin の AO の比較は 3 本の可視性の円錐だけを使った設定で、参照（OptiX のパス トレース）との差は主にその設定のせいだと書きます。広い円錐は遠くの可視性の精度が落ちて、遮蔽を過大に見積もる傾向がある、とも述べています。

Wright も同じ理由で 9 本の円錐を最小としています。大きな円錐では円錐中心近くの小さな特徴と同じ円錐上の複数の遮蔽物から、過大な遮蔽が出るからです。円錐を法線の半球に向けることで、平らな面が常に半分遮られてしまう問題を避けています。

### RTAO の精度 {#rtao-accuracy}

RTAO はレイが当たったかどうかだけを見るので、ボクセルの大きさや SDF の解像度に縛られません。Ray Tracing Gems の図 25-17 は、最大のレイ長 0.6 m で、参照（1 画素 1000 本）、1 本、フィルター後、GTAO を並べています。本文はフィルター後の 1 本/画素の結果が、参照とよく合うが少しシャープさに欠けると述べ GTAO との比較も示しています。

## ノイズ {#noise}

RTAO の見積もりは乱数で選んだレイの当たり外れの平均です。当たる確率を p として N 本の平均の標準偏差は sqrt(p(1−p)/N) です。壁のそばの床の点（壁は x = 0.3 m、高さ 0.6 m、レイ長 0.6 m）で実際にモンテカルロを回しました。100 万本で求めた参照の AO は 0.8039 です。

<svg class="fig flow" viewBox="0 0 640 240" role="img" aria-label="RTAO のレイ数とノイズ"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">RTAO: 画素あたりのレイ数と、AO の標準偏差(壁のそばの点、参照 AO = 0.8039)</text><line x1="60" y1="194" x2="560" y2="194" stroke="#94a3b8"/><line x1="60" y1="34" x2="60" y2="194" stroke="#94a3b8"/><line x1="60" y1="158.44444444444446" x2="560" y2="158.44444444444446" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="162.44444444444446" text-anchor="end" font-size="10" fill="currentColor">0.1</text><line x1="60" y1="122.88888888888889" x2="560" y2="122.88888888888889" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="126.88888888888889" text-anchor="end" font-size="10" fill="currentColor">0.2</text><line x1="60" y1="87.33333333333334" x2="560" y2="87.33333333333334" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="91.33333333333334" text-anchor="end" font-size="10" fill="currentColor">0.3</text><line x1="60" y1="51.77777777777777" x2="560" y2="51.77777777777777" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="55.77777777777777" text-anchor="end" font-size="10" fill="currentColor">0.4</text><polyline points="60.0,52.8 143.3,94.2 226.7,123.4 310.0,144.1 393.3,158.7 476.7,169.0 560.0,176.4" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 3"/><circle cx="60.0" cy="52.8" r="4" fill="#4c8bf5"/><text x="66.0" y="44.844444444444434" text-anchor="start" font-size="10" fill="currentColor">0.397</text><text x="60.0" y="210" text-anchor="middle" font-size="10" fill="currentColor">1</text><circle cx="143.3" cy="94.2" r="4" fill="#4c8bf5"/><text x="149.33333333333331" y="86.23111111111112" text-anchor="start" font-size="10" fill="currentColor">0.281</text><text x="143.33333333333331" y="210" text-anchor="middle" font-size="10" fill="currentColor">2</text><circle cx="226.7" cy="123.9" r="4" fill="#4c8bf5"/><text x="232.66666666666666" y="115.88444444444445" text-anchor="start" font-size="10" fill="currentColor">0.197</text><text x="226.66666666666666" y="210" text-anchor="middle" font-size="10" fill="currentColor">4</text><circle cx="393.3" cy="158.8" r="4" fill="#4c8bf5"/><text x="399.3333333333333" y="150.83555555555557" text-anchor="start" font-size="10" fill="currentColor">0.099</text><text x="393.3333333333333" y="210" text-anchor="middle" font-size="10" fill="currentColor">16</text><circle cx="560.0" cy="176.4" r="4" fill="#4c8bf5"/><text x="566.0" y="168.4" text-anchor="start" font-size="10" fill="currentColor">0.050</text><text x="560.0" y="210" text-anchor="middle" font-size="10" fill="currentColor">64</text><text x="310.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">画素あたりのレイ数 N</text><text x="556" y="48" text-anchor="end" font-size="10" fill="currentColor">破線: 理論 sqrt(p(1-p)/N)</text></svg>

1 本/画素の標準偏差は約 0.40 で、AO の値（0.80）の半分です。これは画面ではほぼ白黒の砂嵐になります。4 本でも 0.20、16 本でも 0.10 で標準偏差を 10 分の 1（0.04）にするには 100 本近く必要です。理論の値と測定値が 3 桁目まで合うので、ノイズは本数の平方根に反比例すると見てよいことが分かります。そのため、RTAO は 1〜2 本とデノイズの組み合わせが前提になります。Ray Tracing Gems の章も 1 画素 1〜2 本で、影と同じ種類のフィルターをかけると書いています。

円錐の方式はこの種のノイズが出ません。ただし、滑らかなわけではありません。Wright は円錐トレースを縦横 1/8 の解像度で回すと「強いエイリアシング」が出るので、1/2 解像度でフィルターし、ジオメトリを意識したアップサンプルを重ねています。さらに、4 つのジッター位置で 4 倍の時間方向のスーパーサンプリングをし、深度の棄却で不安定になった画素は安定した周りの画素で埋めています。ノイズは出ない代わりに解像度を落とした分のフィルターが要るということです。

## 動的なシーン {#dynamic}

DFAO（Wright の方式）はメッシュごとの SDF をオフラインで全方向にレイを飛ばして作っています。そのため、剛体のメッシュだけが使えます。インスタンスは同じ SDF に別の変換を掛けるだけですが、一様スケールだけで非一様スケールとスキンメッシュは対象外と書かれています。物体の移動は行列の更新だけで済みます。大域 SDF はカメラを中心にしたクリップマップで、カメラが動いて新しい層が見えたときか物体が動いたときだけ更新します。更新が最悪になるのはテレポートで、GCN で約 7 ms と書かれています。

VXAO（Crassin の方式）は、動く物体を毎フレーム、同じラスタライズベースの手順でボクセル化します。静的な環境の八分木を作るのに約 280 ms かかりますが、一度だけです。動く物体（1.6 万三角形の手）の更新は、1 フレーム約 5.5 ms で、動く部分の大きさと数で増えます。

RTAO の BVH の更新コストは、読んだ範囲に書かれていません。

## メモリ {#memory}

<svg class="fig flow" viewBox="0 0 740 242" role="img" aria-label="データ構造のメモリの比較"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">データ構造のメモリ(MiB、対数軸。青: DFAO、黄: VXAO)</text><text x="242" y="48" text-anchor="end" font-size="11" fill="currentColor">メッシュ 1 個の SDF (50³ fp16)</text><rect x="250" y="34" width="37.8" height="20" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="293.8290147304933" y="48" text-anchor="start" font-size="10" fill="currentColor">0.244 MiB</text><text x="242" y="78" text-anchor="end" font-size="11" fill="currentColor">大域 SDF の 4 クリップマップ (128³ fp16)</text><rect x="250" y="64" width="215.2" height="20" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="471.23458186730846" y="78" text-anchor="start" font-size="10" fill="currentColor">16 MiB</text><text x="242" y="108" text-anchor="end" font-size="11" fill="currentColor">SDF アトラス 典型(スライドの値)</text><rect x="250" y="94" width="339.5" height="20" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="595.5444645711677" y="108" text-anchor="start" font-size="10" fill="currentColor">300 Mb</text><text x="242" y="138" text-anchor="end" font-size="11" fill="currentColor">512³ 密なボクセル 1 B</text><rect x="250" y="124" width="303.4" height="20" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="559.4222473611552" y="138" text-anchor="start" font-size="10" fill="currentColor">128 MiB</text><text x="242" y="168" text-anchor="end" font-size="11" fill="currentColor">512³ 密なボクセル 4 B</text><rect x="250" y="154" width="362.2" height="20" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="618.214024357053" y="168" text-anchor="start" font-size="10" fill="currentColor">512 MiB</text><text x="242" y="198" text-anchor="end" font-size="11" fill="currentColor">Crassin の実装の確保量</text><rect x="250" y="184" width="391.6" height="20" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="647.609912855002" y="198" text-anchor="start" font-size="10" fill="currentColor">1024 MiB</text><line x1="250" y1="30" x2="250" y2="214" stroke="#94a3b8"/><text x="250.0" y="230" text-anchor="middle" font-size="10" fill="currentColor">0.1</text><text x="347.6510278755128" y="230" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="445.3020557510256" y="230" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="542.9530836265383" y="230" text-anchor="middle" font-size="10" fill="currentColor">100</text><text x="640.6041115020512" y="230" text-anchor="middle" font-size="10" fill="currentColor">1000</text></svg>

DFAO はメッシュ 1 個の SDF が 50³ の fp16 で約 240 KB と書かれています。計算すると 50×50×50×2 バイトで 244 KiB です。大域 SDF は 128³ のクリップマップを 4 枚使うと書かれていて、fp16 とすると 16 MiB です（フォーマットはスライドに書かれていないので、これは私の仮定です）。スライドは物体の SDF を詰めたアトラス（512³）が、典型的なレベルで 300 Mb と書いています。

VXAO は 512³ の密なボクセルだと 1 ボクセル 1 バイトで 128 MiB、4 バイトで 512 MiB です。Crassin の八分木は空のノードを畳む疎な構造で、3×3×3 の小さなブリックを使い頂点中心のボクセルで境界の重複を減らすと書いています。それでも著者の実装は間接の鏡面反射を含めて、約 1024 MB のビデオ メモリを確保しています。AO だけに絞ればこれより小さくできるはずですが、数字は書かれていません。

RTAO は BVH とデノイザーの履歴が主なメモリです。この 2 つの大きさは読んだ範囲に載っていません。

## コスト {#cost}

### DFAO {#cost-dfao}

Wright は 1080p の空の遮蔽（スカイ オクルージョン）のコストを、Radeon 7870 で 3.44 ms（実際の PS4 では 3.7 ms）と書いています。内訳を図にします。

<svg class="fig flow" viewBox="0 0 700 256" role="img" aria-label="DFAO の処理時間の内訳"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">DFAO スカイ オクルージョンの内訳(Radeon 7870、1080p、合計 3.44 ms)</text><text x="202" y="46" text-anchor="end" font-size="11" fill="currentColor">ConeTraceObjects</text><rect x="210" y="32" width="392.0" height="18" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="608.0" y="46" text-anchor="start" font-size="10" fill="currentColor">1.68 ms</text><text x="202" y="70" text-anchor="end" font-size="11" fill="currentColor">UpsampleAO</text><rect x="210" y="56" width="72.3" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="288.3333333333333" y="70" text-anchor="start" font-size="10" fill="currentColor">0.31 ms</text><text x="202" y="94" text-anchor="end" font-size="11" fill="currentColor">UpdateHistory</text><rect x="210" y="80" width="72.3" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="288.3333333333333" y="94" text-anchor="start" font-size="10" fill="currentColor">0.31 ms</text><text x="202" y="118" text-anchor="end" font-size="11" fill="currentColor">BuildTileList</text><rect x="210" y="104" width="67.7" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="283.66666666666663" y="118" text-anchor="start" font-size="10" fill="currentColor">0.29 ms</text><text x="202" y="142" text-anchor="end" font-size="11" fill="currentColor">ConeTraceGlobal</text><rect x="210" y="128" width="67.7" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="283.66666666666663" y="142" text-anchor="start" font-size="10" fill="currentColor">0.29 ms</text><text x="202" y="166" text-anchor="end" font-size="11" fill="currentColor">ComputeNormal</text><rect x="210" y="152" width="53.7" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="269.6666666666667" y="166" text-anchor="start" font-size="10" fill="currentColor">0.23 ms</text><text x="202" y="190" text-anchor="end" font-size="11" fill="currentColor">GeometryAwareUpsample</text><rect x="210" y="176" width="39.7" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="255.66666666666666" y="190" text-anchor="start" font-size="10" fill="currentColor">0.17 ms</text><text x="202" y="214" text-anchor="end" font-size="11" fill="currentColor">CombineCones</text><rect x="210" y="200" width="32.7" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="248.66666666666666" y="214" text-anchor="start" font-size="10" fill="currentColor">0.14 ms</text><text x="202" y="238" text-anchor="end" font-size="11" fill="currentColor">ObjectFrustumCulling</text><rect x="210" y="224" width="7.0" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="223.0" y="238" text-anchor="start" font-size="10" fill="currentColor">0.03 ms</text></svg>

いちばん重いのは物体ごとの SDF での円錐トレース（1.68 ms）です。これを軽くするために大域 SDF を足して、円錐の始めの部分だけ物体 SDF を残りは大域 SDF を読んでいます。スライドはこれで物体の影響範囲が大きく減りスカイ オクルージョンが約 5 倍速くなったと書いています。ただし、大域 SDF は表面の近くが不正確なので、円錐の始めに物体 SDF を使い分ける必要があります。

### VXAO {#cost-vxao}

Crassin の表 2 は Sponza（28 万三角形）で、3 本の円錐を使った AO の時間を円錐の開き角ごとに示しています（GTX 480 の構成、画面 512²）。10 度で 16.6 ms、20 度で 9.0 ms、30 度で 6.5 ms、60 度で 3.9 ms です。広い円錐ほど速くなるのはミップを粗く読んで、歩幅が早く広がりサンプル数が減るからです。

その仮説を自分で確かめました。ボクセル 0.1 m、最大距離 10 m で円錐の直径ごとに 1 サンプルずつ取ると、10 度で 23 歩、20 度で 14 歩、30 度で 11 歩、60 度で 6 歩です。60 度を 1 とした比が歩数では 3.83、2.33、1.83、1.00、論文の時間では 4.26、2.31、1.67、1.00 でよく合います。つまり、円錐 AO のコストはほぼサンプル数に比例するということです。

<svg class="fig flow" viewBox="0 0 620 214" role="img" aria-label="円錐の開き角と歩数・時間の比"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">円錐の開き角ごとの比(60 度を 1 とする)。青: 自分で数えた歩数、黄: Crassin の AO 時間</text><rect x="60" y="62.3" width="44" height="127.7" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><rect x="108" y="48.0" width="44" height="142.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="82" y="58.33333333333333" text-anchor="middle" font-size="10" fill="currentColor">3.83</text><text x="130" y="44.0" text-anchor="middle" font-size="10" fill="currentColor">4.26</text><text x="106" y="206" text-anchor="middle" font-size="11" fill="currentColor">10 度</text><rect x="190" y="112.3" width="44" height="77.7" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><rect x="238" y="113.0" width="44" height="77.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="212" y="108.33333333333333" text-anchor="middle" font-size="10" fill="currentColor">2.33</text><text x="260" y="109.0" text-anchor="middle" font-size="10" fill="currentColor">2.31</text><text x="236" y="206" text-anchor="middle" font-size="11" fill="currentColor">20 度</text><rect x="320" y="129.0" width="44" height="61.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><rect x="368" y="134.3" width="44" height="55.7" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="342" y="125.0" text-anchor="middle" font-size="10" fill="currentColor">1.83</text><text x="390" y="130.33333333333334" text-anchor="middle" font-size="10" fill="currentColor">1.67</text><text x="366" y="206" text-anchor="middle" font-size="11" fill="currentColor">30 度</text><rect x="450" y="156.7" width="44" height="33.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><rect x="498" y="156.7" width="44" height="33.3" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="472" y="152.66666666666669" text-anchor="middle" font-size="10" fill="currentColor">1.00</text><text x="520" y="152.66666666666669" text-anchor="middle" font-size="10" fill="currentColor">1.00</text><text x="496" y="206" text-anchor="middle" font-size="11" fill="currentColor">60 度</text><line x1="50" y1="190" x2="580" y2="190" stroke="#94a3b8"/></svg>

### RTAO {#cost-rtao}

RTAO のコストはレイの数に比例します。1 本/画素で 1080p は約 207 万本、2160p は約 829 万本です。ms の値は読んだ範囲になく、GPU と BVH で大きく変わるので、ここでは書きません。

## 選び方 {#choosing}

画面の外の遮蔽が要る点が前提ならまず「ハードウェア レイトレースが使えるか」で分かれます。使えるなら RTAO は精度でいちばん素直で、薄い壁も表せます。そのかわり 1〜2 本/画素のノイズをデノイザーで消す設計が必要です。

使えないなら静的な屋外の広い範囲には DFAO が向きます。Wright は建築の薄い壁を扱いたかったことが、ボクセルの円錐トレースを選ばなかった理由の 1 つだと書いています。Fortnite（動的な時刻とプレイヤーの建築）も PS4 級のハードウェアで動かす想定だと書いています。ただし、スキンメッシュや非一様スケールは対象外で、メッシュごとの SDF を作る手順が要ります。

動く物体が多く AO だけでなく間接光まで同じデータで出したいなら VXAO です。薄い壁と大きなメモリに注意が必要です。

スクリーン空間の AO と併用する構成が、多くのゲームで現実的です。大きな遮蔽は世界空間の方式で、細かい接触はスクリーン空間で、と得意な範囲を分担します。Ray Tracing Gems の章も GTAO と HBAO が画面外の情報を持たないことを欠点として挙げていて、画面内の遮蔽に隠れて見えなくなった物も含めて、レイが正しく扱えると書いています。

## 実装してみる {#code}

3 方式の核になる HLSL を順に見ます。どれも資料の式と手順からの私の書き下ろしで、資料のコードそのものではありません。DFAO と VXAO は `fxc`（ps_5_0）で、RTAO は `dxc`（lib_6_3）でコンパイルして確かめました。実行して絵は確かめていません。「足した処理」と書いた所は資料にない処理です。定数は一例です。

### 円錐の並べ方（DFAO と VXAO で共通）{#cones}

```hlsl
// 円錐 AO（DFAO と VXAO で共通）の、円錐の並べ方と重み。
// 9 本は Wright (2015) が「良い品質を保てる最小の本数」と書いた数。並べ方と重みはここで決めた一例。

static const int kConeCount = 9;
static const float kConeHalfAngle = 0.4712;   // 27 度。9 本で半球 (2π sr) を覆うための半角
                                              // 2π(1 - cos h) × 9 = 2π になる h = acos(8/9) ≒ 27.3 度

// 法線から 2 本の接線を作る（法線が (0,0,±1) に近くても壊れない形）。
void MakeBasis(float3 n, out float3 t, out float3 b) {
  float sign_z = (n.z >= 0.0) ? 1.0 : -1.0;
  float a = -1.0 / (sign_z + n.z);
  float c = n.x * n.y * a;
  t = float3(1.0 + sign_z * n.x * n.x * a, sign_z * c, -sign_z * n.x);
  b = float3(c, sign_z + n.y * n.y * a, -n.y);
}

// i = 0 は法線方向。i = 1〜8 は、法線から 60 度傾けた方向を、法線のまわりに 45 度ずつ回したもの。
// frame_rotation は、フレームごとに変える回転（ラジアン）。時間方向の積み重ねで縞を消すのに使う。足した処理。
float3 ConeDirection(int i, float3 n, float3 t, float3 b, float frame_rotation) {
  if (i == 0) return n;
  float phi = (i - 1) * 0.7853982 + frame_rotation;        // 45 度刻み
  const float sin_tilt = 0.8660254, cos_tilt = 0.5;        // 傾き 60 度
  return normalize(cos(phi) * sin_tilt * t + sin(phi) * sin_tilt * b + cos_tilt * n);
}

// 法線とのコサイン（ランバートの重み）。i = 0 は 1、それ以外は cos 60 度 = 0.5。
float ConeWeight(int i) {
  return (i == 0) ? 1.0 : 0.5;
}
static const float kWeightSum = 1.0 + 8.0 * 0.5;     // 5.0
```

Wright は 9 本の円錐を使い法線の半球に向けています。9 本で半球（2π sr）を覆うには、1 本あたり 2π(1−cos h) × 9 = 2π になればよく、h = acos(8/9) ≒ 27.3 度です。並べ方（法線に 1 本と 60 度傾けた 8 本）とコサインの重み（1 と 0.5）は、ここで決めた一例です。

### DFAO：距離場の円錐トレース {#dfao}

```hlsl
Texture2D<float> g_depth : register(t0);
Texture2D<float4> g_normal : register(t1);       // xyz = ワールド空間の法線
Texture3D<float> g_global_sdf : register(t2);    // 4 枚のクリップマップを z 方向に積んだ SDF（単位 m）
SamplerState g_linear_clamp : register(s0);

cbuffer DfaoCB : register(b0) {
  float4x4 g_inv_view_proj;
  float3 g_camera_pos;
  float g_max_occlusion_distance;     // 一例: 10 m（Wright の既定値）
  float3 g_clip_extent;               // 一番細かいクリップマップの一辺の長さ [m]（x, y, z 共通でよい）
  float g_frame_rotation;
  float2 g_inv_size;
  float g_start_offset;               // 表面から離れて始める距離 [m]（自己遮蔽を避ける。一例: 0.1）
  float g_pad;
};

#include "ao_cones.hlsl"

static const int kMaxSteps = 24;      // 1 本の円錐の最大ステップ数（一例）
static const int kClipCount = 4;
static const float kClipDepth = 128.0;   // 1 枚のクリップマップの奥行き（ボクセル数）

// ワールドの位置から SDF を読む。いちばん細かいクリップマップから順に探し、点を含む最初のものを使う。
// 各クリップマップはカメラを中心にして、一辺が g_clip_extent × 2^i [m]。
float SampleGlobalSdf(float3 p) {
  float3 rel = p - g_camera_pos;
  float result = 1e3;      // どのクリップマップにも入らない所は、何もないとして扱う
  bool found = false;
  [unroll] for (int i = 0; i < kClipCount; ++i) {
    float3 half_extent = 0.5 * g_clip_extent * exp2(i);
    float3 uvw = rel / (2.0 * half_extent) + 0.5;
    if (!found && all(uvw > 0.0) && all(uvw < 1.0)) {
      // z 方向に積んだテクスチャの中の、自分の層だけを読む。層の端の半ボクセルは隣の層を混ぜないよう避ける。
      float z_in = clamp(uvw.z * kClipDepth, 0.5, kClipDepth - 0.5);
      float3 coord = float3(uvw.xy, (i * kClipDepth + z_in) / (kClipDepth * kClipCount));
      result = g_global_sdf.SampleLevel(g_linear_clamp, coord, 0);
      found = true;
    }
  }
  return result;
}
```

大域 SDF は 4 枚のクリップマップを z 方向に積んだ 1 つの 3D テクスチャにしています。クリップマップを選ぶとき点を含む最初のものを使います。層の端の半ボクセルを避けて隣の層を混ぜないようにしています。

```hlsl
// 1 本の円錐の可視性。Wright のループ:
//   DistanceToSurface = SDF を読む
//   最小の可視性 = min(最小の可視性, DistanceToSurface / ConeRadius)
//   光線に沿って abs(DistanceToSurface) だけ進む。内側に入るか最大ステップを超えたら終わり。
float ConeVisibility(float3 origin, float3 dir, float tan_half) {
  float vis = 1.0;
  float t = g_start_offset;
  [loop] for (int i = 0; i < kMaxSteps; ++i) {
    float dist = SampleGlobalSdf(origin + dir * t);
    float cone_radius = max(t * tan_half, 1e-3);       // t = 0 での 0 割りを避ける。足した処理
    float v = saturate(dist / cone_radius);            // 1 = 開けている、0 = 円錐の軸が遮られている
    // 遠い遮蔽ほど弱める。論文に式はなく、ここで決めた一例（2 次で 0 になる）。
    float fade = saturate(1.0 - (t * t) / (g_max_occlusion_distance * g_max_occlusion_distance));
    vis = min(vis, lerp(1.0, v, fade));
    if (dist < 0.0 || t > g_max_occlusion_distance) break;   // 表面の内側に入った、または最大距離
    t += max(abs(dist), 0.02);                          // 進まなくなるのを防ぐ最小の歩幅。足した処理
  }
  return vis;
}
```

Wright のループをそのまま写しています。距離を読んで距離を円錐の半径で割った値の最小を取り距離の絶対値だけ進みます。内側に入るか最大距離を超えたら終わります。円錐の半径は `t × tan(半角)` で t が 0 のときに 0 で割らないよう下限を設けています。

```hlsl
// 出力: xyz = 曲がった法線（最も開けた方向）、w = AO。
float4 main(float4 pos : SV_Position) : SV_Target {
  float2 uv = pos.xy * g_inv_size;   // 画素の中心の UV
  float depth = g_depth.Load(int3(pos.xy, 0));   // 深度（1 が奥）
  if (depth >= 1.0) return float4(0, 0, 1, 1);          // 空

  float4 clip = float4(uv * float2(2, -2) + float2(-1, 1), depth, 1);   // UV と深度から、クリップ空間の位置を作る（y は反転）
  float4 world = mul(clip, g_inv_view_proj);   // ワールド空間へ戻す（同次座標）
  float3 position = world.xyz / world.w;   // 同次座標の除算でワールド位置になる
  float3 n = normalize(g_normal.Load(int3(pos.xy, 0)).xyz);   // ワールド空間の法線

  float3 t, b;
  MakeBasis(n, t, b);   // 法線を z とする座標系を作る

  float tan_half = tan(kConeHalfAngle);   // 円錐の半角の tan（半径 = 距離 × tan）
  float ao = 0.0;   // 9 本の可視性の重み付き和
  float3 bent = 0.0;   // 曲がった法線の素になるベクトル
  [unroll] for (int i = 0; i < kConeCount; ++i) {
    float3 dir = ConeDirection(i, n, t, b, g_frame_rotation);   // この円錐の向き
    float vis = ConeVisibility(position, dir, tan_half);   // 0 = 軸が遮られた、1 = 開けている
    ao += ConeWeight(i) * vis;   // コサインの重みを掛けて足す
    bent += dir * vis;                                   // 円錐の向き × 可視性 = 最も開けた方向
  }
  ao /= kWeightSum;   // 重みの合計で割って 0〜1 に戻す
  float3 bent_normal = (dot(bent, bent) > 1e-6) ? normalize(bent) : n;   // 全部遮られたときの 0 ベクトルは法線に戻す
  return float4(bent_normal, ao);   // xyz = 曲がった法線、w = AO
}
```

9 本の可視性をコサインで重み付けして平均したものが AO です。円錐の向き × 可視性の和が、最も開けた方向（曲がった法線）になります。これは Wright が「最も遮蔽の少ない円錐」と呼んで、スカイライトの SH 拡散に適用するものです。

### VXAO：ボクセルの円錐トレース {#vxao}

```hlsl
// 1 本の円錐の遮蔽。
//  - 円錐の直径に合うミップを読む（近くは細かく、遠くは粗く）。
//  - 前から順に、alpha := alpha + (1 - alpha) * alpha2 で合成する（Crassin の式。手前の遮蔽が奥を隠す）。
//  - 距離の重み f(r) を掛けて、遠い遮蔽を弱める。
float ConeOcclusion(float3 origin, float3 dir, float tan_half) {
  float occlusion = 0.0;
  float d = g_voxel_size * 2.0;      // 表面のボクセルを避けて始める（足した処理。一例）
  [loop] for (int i = 0; i < 64; ++i) {
    if (d >= g_max_distance || occlusion >= 0.99) break;

    float diameter = max(2.0 * d * tan_half, g_voxel_size);
    float mip = clamp(log2(diameter / g_voxel_size), 0.0, g_mip_count - 1.0);

    float3 p = origin + dir * d;
    float3 uvw = (p - g_grid_origin) * g_inv_grid_size;
    if (any(uvw < 0.0) || any(uvw > 1.0)) break;          // グリッドの外は、遮蔽なしとして打ち切る

    float alpha2 = g_voxel_occupancy.SampleLevel(g_linear_clamp, uvw, mip);

    // 歩幅が直径より短いと、同じ遮蔽を何度も足してしまう。占有度を歩幅に合わせて補正する
    // （Crassin の α' = 1 - (1 - α)^(d'/d)。d' が歩幅、d が直径）。
    float step_len = diameter * g_step_scale;
    alpha2 = 1.0 - pow(saturate(1.0 - alpha2), g_step_scale);

    float weight = 1.0 / (1.0 + g_decay * d);              // f(r)。論文の AO の重み
    occlusion += (1.0 - occlusion) * alpha2 * weight;

    d += max(step_len, g_voxel_size);      // ボクセルより細かくは進まない。足した処理
  }
  return saturate(occlusion);
}
```

円錐の直径に合うミップを読む部分が要点です。ミップは `log2(直径 / ボクセルの大きさ)` で距離が離れるほど粗いミップを読みます。合成は Crassin の式で、手前の遮蔽が奥を隠します。論文は AO の距離の重みに `1 / (1 + λr)` を使っています。歩幅が円錐の直径と違うとき占有度を補正する式 `α' = 1 − (1 − α)^(d'/d)` も入れています。

```hlsl
float4 main(float4 pos : SV_Position) : SV_Target {
  float2 uv = pos.xy * g_inv_size;   // 画素の中心の UV
  float depth = g_depth.Load(int3(pos.xy, 0));   // 深度（1 が奥）
  if (depth >= 1.0) return float4(0, 0, 1, 1);   // 空は遮蔽なし。法線は上向きの仮の値

  float4 clip = float4(uv * float2(2, -2) + float2(-1, 1), depth, 1);   // UV と深度から、クリップ空間の位置を作る（y は反転）
  float4 world = mul(clip, g_inv_view_proj);   // ワールド空間へ戻す（同次座標）
  float3 position = world.xyz / world.w;   // 同次座標の除算でワールド位置になる
  float3 n = normalize(g_normal.Load(int3(pos.xy, 0)).xyz);   // ワールド空間の法線

  float3 t, b;
  MakeBasis(n, t, b);   // 法線を z とする座標系を作る

  float tan_half = tan(kConeHalfAngle);   // 円錐の半角の tan（直径の計算に使う）
  float visibility = 0.0;   // 9 本の可視性の重み付き和
  float3 bent = 0.0;   // 曲がった法線の素になるベクトル
  [unroll] for (int i = 0; i < kConeCount; ++i) {
    float3 dir = ConeDirection(i, n, t, b, g_frame_rotation);   // この円錐の向き
    // 自己遮蔽を避けるため、法線の向きに 1 ボクセルぶん持ち上げた点から始める。足した処理。
    float vis = 1.0 - ConeOcclusion(position + n * g_voxel_size, dir, tan_half);
    visibility += ConeWeight(i) * vis;   // コサインの重みを掛けて足す
    bent += dir * vis;   // 開けている円錐の向きほど強く効く
  }
  visibility /= kWeightSum;   // 重みの合計で割って 0〜1 に戻す
  float3 bent_normal = (dot(bent, bent) > 1e-6) ? normalize(bent) : n;   // 全部遮られたときの 0 ベクトルは法線に戻す
  return float4(bent_normal, visibility);   // xyz = 曲がった法線、w = 可視性
}
```

### RTAO：DXR のレイ生成 {#rtao}

```hlsl
// DXR: レイトレース AO のレイ生成シェーダー（Shader Model 6.3 の lib）。
// 構造は Ray Tracing Gems 第 25 章（PICA PICA）の影のレイ生成と同じ。コードは書き直したもの。

RaytracingAccelerationStructure g_scene : register(t0);
Texture2D<float> g_depth : register(t1);
Texture2D<float4> g_normal : register(t2);           // xyz = ワールド空間の法線
RWTexture2D<float> g_ao_out : register(u0);          // 1 = 遮蔽なし

cbuffer RtaoCB : register(b0) {
  float4x4 g_inv_view_proj;
  float2 g_inv_size;
  uint g_frame_index;
  uint g_num_rays;           // 1 画素あたりのレイ数（1〜2 が普通）
  float g_min_ray_length;    // 自己交差を避ける（一例: 0.01 m）
  float g_max_ray_length;    // AO の届く距離（Ray Tracing Gems の図 25-17 は 0.6 m）
  float2 g_pad;
};

struct AoPayload {
  bool miss;                 // 初期値は false。ミス シェーダーだけが true にする
};

// PCG のハッシュ（画素と、フレームと、レイの番号から乱数を作る）。
uint Hash(uint v) {
  v = v * 747796405u + 2891336453u;
  uint w = ((v >> ((v >> 28u) + 4u)) ^ v) * 277803737u;
  return (w >> 22u) ^ w;
}
float Random01(inout uint state) {
  state = Hash(state);
  return (state >> 8) * (1.0 / 16777216.0);
}

// コサイン重みで半球（z が上）を選ぶ。pdf = cos / π なので、重みを掛けずに平均するだけで AO になる。
float3 CosineSampleHemisphere(float u1, float u2) {
  float r = sqrt(u1);
  float phi = 6.2831853 * u2;
  return float3(r * cos(phi), r * sin(phi), sqrt(max(0.0, 1.0 - u1)));
}

void MakeBasis(float3 n, out float3 t, out float3 b) {
  float s = (n.z >= 0.0) ? 1.0 : -1.0;
  float a = -1.0 / (s + n.z);
  float c = n.x * n.y * a;
  t = float3(1.0 + s * n.x * n.x * a, s * c, -s * n.x);
  b = float3(c, s + n.y * n.y * a, -n.y);
}
```

乱数は PCG のハッシュで作ります。コサイン重みの半球サンプルは確率密度が cos/π なので、重みを掛けずに平均するだけで AO になります。

```hlsl
[shader("raygeneration")]
void RtaoRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float depth = g_depth.Load(int3(pixel, 0));
  if (depth >= 1.0) { g_ao_out[pixel] = 1.0; return; }       // 空

  float2 uv = (pixel + 0.5) * g_inv_size;
  float4 clip = float4(uv * float2(2, -2) + float2(-1, 1), depth, 1);
  float4 world = mul(clip, g_inv_view_proj);
  float3 position = world.xyz / world.w;
  float3 n = normalize(g_normal.Load(int3(pixel, 0)).xyz);

  float3 t, b;
  MakeBasis(n, t, b);

  uint seed = Hash(pixel.x + Hash(pixel.y + Hash(g_frame_index)));
  float visible = 0.0;
  for (uint i = 0; i < g_num_rays; ++i) {
    float3 local = CosineSampleHemisphere(Random01(seed), Random01(seed));
    float3 dir = local.x * t + local.y * b + local.z * n;     // 法線の向きの半球に回す

    RayDesc ray;
    ray.Origin = position;
    ray.Direction = dir;
    ray.TMin = g_min_ray_length;
    ray.TMax = g_max_ray_length;

    AoPayload payload;
    payload.miss = false;
    // 当たったかどうかだけが要る。最も近い交点は不要なので、最初の交点で終える。
    // ヒット シェーダーも使わない（miss が true のままなら、何にも当たらなかった）。
    TraceRay(g_scene,
             RAY_FLAG_SKIP_CLOSEST_HIT_SHADER | RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH,
             0xFF, 0, 0, 0, ray, payload);
    visible += payload.miss ? 1.0 : 0.0;
  }
  g_ao_out[pixel] = visible / g_num_rays;
}

[shader("miss")]
void RtaoMiss(inout AoPayload payload) {
  payload.miss = true;
}
```

Ray Tracing Gems のコードと同じ形です。当たったかどうかだけが要るので、ヒット シェーダーを省き（`SKIP_CLOSEST_HIT_SHADER`）、最初の交点で終える（`ACCEPT_FIRST_HIT_AND_END_SEARCH`）ようにしています。ミス シェーダーだけが `miss` を true にします。レイの長さの上限が AO の届く距離です。

### 数字を出す C++ {#cpp}

円錐のサンプル数、メモリ、RTAO のモンテカルロを 1 本の C++ で出します。

```cpp
// 世界空間 AO の 3 方式を比べる数字を出す。
//  1. 円錐の開き角と、トレースのサンプル数（VXAO / DFAO のコストの目安）
//  2. データ構造のメモリ
//  3. RTAO: レイ数とノイズ（壁の影響を受ける点で、モンテカルロを実際に回す）
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <random>
#include <vector>

namespace {
constexpr double kPi = 3.14159265358979323846;
constexpr double kMiB = 1024.0 * 1024.0;

// 円錐に沿って進むときのサンプル数。
// 距離 d での円錐の直径は 2 d tan(theta/2)。1 サンプルを直径の spacing 倍ごとに取り、
// ボクセルの大きさ voxel を下回る歩幅にはしない（それより細かく取っても同じボクセルを読むだけ）。
int ConeSteps(double voxel, double aperture_deg, double max_dist, double spacing) {
  const double t = std::tan(aperture_deg * kPi / 180.0 * 0.5);
  double d = voxel;  // 表面のボクセル自身を読まないよう、1 ボクセル離れた所から始める
  int steps = 0;
  while (d < max_dist) {
    const double diameter = 2.0 * d * t;
    d += std::max(voxel, diameter * spacing);
    ++steps;
  }
  return steps;
}

// ---- RTAO のモンテカルロ ----
struct Vec3 { double x, y, z; };

// コサイン重みで半球（z が上）を選ぶ。pdf = cos / pi。
Vec3 CosineSample(std::mt19937_64& rng) {
  std::uniform_real_distribution<double> u(0.0, 1.0);
  const double r = std::sqrt(u(rng));
  const double phi = 2.0 * kPi * u(rng);
  return {r * std::cos(phi), r * std::sin(phi), std::sqrt(std::max(0.0, 1.0 - r * r))};
}

// 遮蔽物: 平面 x = wall_x に立つ壁（高さ 0 〜 wall_h、y 方向には無限）。
// 原点から d 方向のレイが、max_dist 以内に壁に当たれば遮蔽。
bool Occluded(const Vec3& d, double wall_x, double wall_h, double max_dist) {
  if (d.x <= 1e-9) return false;
  const double t = wall_x / d.x;
  return t <= max_dist && t * d.z <= wall_h;
}
}  // namespace

int main() {
  std::printf("== 円錐のサンプル数（ボクセル 0.1 m、最大距離 10 m）==\n");
  std::printf("開き角   1 直径ごと  0.5 直径ごと  Crassin の AO 時間 [ms]\n");
  const double apertures[] = {10, 20, 30, 60};
  const double crassin_ms[] = {16.6, 9.0, 6.5, 3.9};  // 論文 Table 2 の値（3 円錐、512^2）
  for (int i = 0; i < 4; ++i) {
    std::printf("%4.0f 度  %8d  %10d  %8.1f\n", apertures[i],
                ConeSteps(0.1, apertures[i], 10.0, 1.0), ConeSteps(0.1, apertures[i], 10.0, 0.5),
                crassin_ms[i]);
  }
  std::printf("60 度を 1 としたときの比: ");
  for (int i = 0; i < 4; ++i) {
    std::printf("%.2f(歩数) / %.2f(論文の時間)  ",
                static_cast<double>(ConeSteps(0.1, apertures[i], 10.0, 1.0)) /
                    ConeSteps(0.1, 60, 10.0, 1.0),
                crassin_ms[i] / crassin_ms[3]);
  }
  std::printf("\n");

  std::printf("\n== メモリ（MiB）==\n");
  const double dense512 = 512.0 * 512.0 * 512.0;
  for (int bytes : {1, 2, 4, 8}) {
    std::printf("512^3 の密なボクセル %d バイト/ボクセル: %.0f MiB\n", bytes, dense512 * bytes / kMiB);
  }
  std::printf("メッシュ 1 個の SDF 50^3 fp16: %.0f KiB\n", 50.0 * 50 * 50 * 2 / 1024.0);
  std::printf("全体 SDF のクリップマップ 4 枚 x 128^3 fp16: %.0f MiB\n",
              4.0 * 128 * 128 * 128 * 2 / kMiB);

  std::printf("\n== RTAO: 壁（x = 0.3 m、高さ 0.6 m）のそばの床の点 ==\n");
  std::mt19937_64 rng(12345);
  const double wall_x = 0.3, wall_h = 0.6, max_dist = 0.6;
  // 正解（100 万本）。
  int blocked = 0;
  const int kRef = 1000000;
  for (int i = 0; i < kRef; ++i) blocked += Occluded(CosineSample(rng), wall_x, wall_h, max_dist);
  const double ao_ref = 1.0 - static_cast<double>(blocked) / kRef;  // 1 = 遮蔽なし
  std::printf("参照 (100 万本): AO = %.4f\n", ao_ref);
  std::printf("rays/pixel  平均    標準偏差(測定)  標準偏差(理論 sqrt(p(1-p)/N))\n");
  const int kPixels = 20000;
  for (int n : {1, 2, 4, 16, 64}) {
    double sum = 0, sum_sq = 0;
    for (int p = 0; p < kPixels; ++p) {
      int hit = 0;
      for (int i = 0; i < n; ++i) hit += Occluded(CosineSample(rng), wall_x, wall_h, max_dist);
      const double ao = 1.0 - static_cast<double>(hit) / n;
      sum += ao;
      sum_sq += ao * ao;
    }
    const double mean = sum / kPixels;
    const double sd = std::sqrt(std::max(0.0, sum_sq / kPixels - mean * mean));
    std::printf("%6d      %.4f  %.4f          %.4f\n", n, mean, sd,
                std::sqrt(ao_ref * (1.0 - ao_ref) / n));
  }
  std::printf("\n1 本/画素のレイ数: 1080p %.2f M, 2160p %.2f M\n", 1920.0 * 1080 / 1e6,
              3840.0 * 2160 / 1e6);
  return 0;
}
```

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。

```text title="実行結果"
== 円錐のサンプル数（ボクセル 0.1 m、最大距離 10 m）==
開き角   1 直径ごと  0.5 直径ごと  Crassin の AO 時間 [ms]
  10 度        23          37      16.6
  20 度        14          23       9.0
  30 度        11          17       6.5
  60 度         6          10       3.9
60 度を 1 としたときの比: 3.83(歩数) / 4.26(論文の時間)  2.33(歩数) / 2.31(論文の時間)  1.83(歩数) / 1.67(論文の時間)  1.00(歩数) / 1.00(論文の時間)
```

```text title="実行結果（続き）"
== メモリ（MiB）==
512^3 の密なボクセル 1 バイト/ボクセル: 128 MiB
512^3 の密なボクセル 2 バイト/ボクセル: 256 MiB
512^3 の密なボクセル 4 バイト/ボクセル: 512 MiB
512^3 の密なボクセル 8 バイト/ボクセル: 1024 MiB
メッシュ 1 個の SDF 50^3 fp16: 244 KiB
全体 SDF のクリップマップ 4 枚 x 128^3 fp16: 16 MiB
```

```text title="実行結果（続き）"
== RTAO: 壁（x = 0.3 m、高さ 0.6 m）のそばの床の点 ==
参照 (100 万本): AO = 0.8039
rays/pixel  平均    標準偏差(測定)  標準偏差(理論 sqrt(p(1-p)/N))
     1      0.8039  0.3970          0.3971
     2      0.8048  0.2806          0.2808
     4      0.8069  0.1972          0.1985
    16      0.8043  0.0989          0.0993
    64      0.8047  0.0495          0.0496
```

```text title="実行結果（続き）"
1 本/画素のレイ数: 1080p 2.07 M, 2160p 8.29 M
```

## よくあるミス

??? failure "世界空間 AO だけにして、接地感が足りない"
    世界空間の方式は解像度が粗い。スクリーン空間の AO（GTAO など）も併用して、細部を補う。

??? failure "SDF やボクセルで、平らな面が自分自身を暗くする"
    自己遮蔽。円錐の始点を表面から離す（DFAO は 0.1 m ほど VXAO は 1 ボクセルほど。一例）。Wright は SDF のほうがボクセルより必要なバイアスが少ないと書いている。

??? failure "円錐 AO が全体に暗すぎる"
    円錐が太すぎるか本数が少なすぎる。Crassin も Wright も太い円錐が遠くの遮蔽を過大に見積もると述べている。円錐を細くするか本数を増やす。距離の重みで遠い遮蔽を弱めるのも手である。

??? failure "RTAO が砂嵐のままデノイズしても消えない"
    1 本/画素の標準偏差は約 0.4 で、AO の値と同じ桁になる。デノイザーに履歴の蓄積と法線・深度に応じたフィルターが入っているかを確かめる。レイ長を短くすると当たる確率が下がって分散が減る。

??? failure "円錐トレースの結果に縞やブロックが出る"
    解像度を落として回している。Wright のようにフィルターとジオメトリを意識したアップサンプルを入れ、ジッターを変えて時間方向に積む。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RTAO は交差の有無、DFAO は距離つきの可視性、VXAO は占有度。トレース 1 回で分かることが違う。
    - [x] RTAO のノイズは sqrt(p(1−p)/N)。1 本/画素の標準偏差は約 0.4 で、デノイザーが前提になる。
    - [x] 円錐 AO のコストは、ほぼサンプル数に比例する。太い円錐は速いが遠くの遮蔽を過大に見積もる。
    - [x] DFAO は剛体向き VXAO は動く物を毎フレーム再ボクセル化する。
    - [x] 画面内の細部はスクリーン空間で、大きな遮蔽は世界空間で分担する。

## 参考

- Daniel Wright, "Dynamic Occlusion with Signed Distance Fields", ACM SIGGRAPH 2015 Courses, Advances in Real-Time Rendering in Games, 2015. <https://advances.realtimerendering.com/s2015/DynamicOcclusionWithSignedDistanceFields.pdf>（全文を読んだ。「3 方式の見取り図」「精度」「ノイズ」「動的なシーン」「メモリ」「コスト」「DFAO」で参照）
- Cyril Crassin, Fabrice Neyret, Miguel Sainz, Simon Green, Elmar Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Proc. Pacific Graphics 2011) 30(7), 2011.（著者版の全文を読んだ。図は見ていない。「精度」「動的なシーン」「メモリ」「コスト」「VXAO」で参照）
- Colin Barré-Brisebois, Henrik Halén, Graham Wihlidal, Andrew Lauritzen, Jasper Bekkers, Tomasz Stachowiak, Johan Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, Apress, 2019. DOI: 10.1007/978-1-4842-4427-2_25（25.2.3 の AO の節と前後だけを読んだ。ほかの節は読んでいない。「ノイズ」「RTAO」で参照）
- Akenine-Möller ほか "Real-Time Rendering" 第 4 版は、今回は読み直していない。

## 関連ページ

- [Ray-Traced, Distance-Field and Voxel AO](index.md)
- [RTAO](rtao.md)
- [DFAO](dfao.md)
- [VXAO](vxao.md)
- [GTAO](../gtao.md)
- [AO Comparison](../comparison.md)
