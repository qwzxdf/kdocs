---
title: Foliage Translucency
tags:
  - 描画
---

# Foliage Translucency

草原や木々を半透明のブレンドで描こうとすると、すぐに行き詰まります。葉は数が多すぎて並べ替えられず並べ替えても、重なった葉の前後は決まりません。そこで葉は「アルファ テストで形を切り抜く」のが定番になりますが、今度は別の問題が出ます。縁がギザギザになる。遠くで葉が痩せる。さらに、逆光の葉は光を透かして明るく見えるのに、普通のライティングでは真っ黒になる。このページではこの 3 つの問題を数字で確かめながら順に直します。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。以前のページにあった「遠くのミップで 40%、10% に減る」という表は根拠のない数字だったので、実際に作ったテクスチャで数え直しました。下の参考資料は**今回は読んでいません**。ミップのアルファ補正、ハッシュ、透過の式は自分で導いて数字で確かめたもので、各資料の記述との一致は確かめていません。

!!! tip "ポイント"
    - 葉に半透明ブレンドは使えません。100 万枚の並べ替えは 1 フレームに約 1.99e7 回の比較で、そのうえ重なった葉の前後は決まりません。
    - 草のような細い物はミップが 3 段進むとアルファが 0.5 を超える画素が 1.5% から 0% になって消えます。ミップごとにアルファを倍率で補正すると、ミップ 4 でも 1.2% 残ります。
    - Alpha to Coverage のサンプル数 n に対する量子化の誤差は、最大 `1/(2n)` です。4 サンプルで 0.125、8 サンプルで 0.0625 です。
    - ハッシュド アルファはアルファ 0.3 のとき 1 フレームだと標準偏差 0.458、64 フレーム平均で 0.057 です。TAA と組み合わせて使う前提の方式です。
    - 葉は薄いので光は表で反射するか裏へ透けるかのどちらかです。向きがランダムな葉の平均では反射と透過を足した合計は、光の向きによらず 0.500 です。逆光（180 度）では反射は 0 で、透過が 0.500 を担います。

!!! info "このページを読む前に"
    - [Vegetation](index.md)（このセクション全体の地図と読む順番）
    - [Alpha Testing](../../translucency/alpha-test/index.md)（アルファ テストの基本）

## 半透明のブレンドを使えない理由 {#no-blend}

半透明のブレンドは奥から手前の順に描かないと正しい色になりません。草を 100 万本並べるとそれを毎フレーム並べ替えるだけで `n log2 n` = 1.99e7 回の比較が要ります。しかも葉は互いに交差し 1 枚の中でも前後が混じるので、並べ替えても正しい順番が決まらない場面が残ります。

もう 1 つの理由は帯域です。ブレンドは画素ごとにフレームバッファを読んで、書き戻します。RGBA8 なら 1 回あたり 8 バイトです。1080p（約 207 万画素）で平均の重なり（オーバードロー）が 2 層なら 33.2 MB/フレーム、60 fps で 1.99 GB/s です。4 層なら 3.98 GB/s、8 層なら 7.96 GB/s で、草が画面いっぱいに重なる場面ではこれが背景の描画に上乗せされます。さらに、半透明は深度バッファに書かないのが普通なので、手前の草が奥の草を隠すという前後関係も失われます。

そこで、アルファ テストを使います。アルファがしきい値より小さい画素を捨てるだけなので、深度も書け並べ替えも要りません。

## アルファ テストの縁と痩せ {#problems}

### 縁がギザギザになる {#jaggies}

アルファ テストは画素ごとに残すか捨てるかを決めるので、縁は階段状になります。MSAA は三角形の縁をサブサンプルで平均する仕組みで、シェーダーの中の `discard` による縁はサブサンプルごとには決まらないので、効果がありません。対処は 3 つです。

- Alpha to Coverage（A2C）: シェーダーが出力したアルファを、MSAA のカバレッジ（何個のサブサンプルを残すか）に変換します。
- ハッシュド アルファ: しきい値を画素ごとフレームごとにずらし、残る確率をアルファにそろえます。時間方向の平均（TAA）で半透明に見せます。
- TAA: 時間方向に平均して、ジャギーをならします。

### A2C の段階とハッシュのばらつき {#a2c-hash}

A2C はアルファをサンプル数 n で量子化します。アルファ a は `round(a × n) / n` に丸められ残るサンプルが n + 1 段階しかありません。数えた誤差は次のとおりです。

- n = 2: 3 段階、最大誤差 0.2500、平均誤差 0.1250
- n = 4: 5 段階、最大誤差 0.1250、平均誤差 0.0625
- n = 8: 9 段階、最大誤差 0.0625、平均誤差 0.0312
- n = 16: 17 段階、最大誤差 0.0312、平均誤差 0.0156

最大誤差は `1/(2n)`、平均誤差は `1/(4n)` で式と一致しました。4× MSAA ではアルファの階調が 5 段階しかなく、最大で 0.125 ずれます。

ハッシュド アルファはしきい値が一様乱数なので、1 回の判定で画素が残る確率はアルファそのものです。1 フレームだけだとただの 0/1 の乱数で、アルファ 0.3 のときの標準偏差は `sqrt(a(1 − a))` = 0.458 です。N フレーム平均すると `sqrt(a(1 − a)/N)` になり測った値は N = 4 で 0.229、N = 16 で 0.114、N = 64 で 0.057 でした。式の 0.229、0.115、0.057 に一致します。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="A2C とハッシュ"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">誤差の比較</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,75.9 78.7,81.8 87.3,87.5 96.0,93.1 104.7,98.4 113.3,103.6 122.0,108.6 130.7,113.4 139.3,118.0 148.0,122.5 156.7,126.9 165.3,131.1 174.0,135.1 182.7,139.0 191.3,142.8 200.0,146.5 208.7,150.0 217.3,153.4 226.0,156.7 234.7,159.9 243.3,162.9 252.0,165.9 260.7,168.8 269.3,171.5 278.0,174.2 286.7,176.8 295.3,179.3 304.0,181.7 312.7,184.0 321.3,186.3 330.0,188.4 338.7,190.5 347.3,192.6 356.0,194.5 364.7,196.4 373.3,198.2 382.0,200.0 390.7,201.7 399.3,203.3 408.0,204.9 416.7,206.5 425.3,207.9 434.0,209.4 442.7,210.8 451.3,212.1 460.0,213.4 468.7,214.6 477.3,215.8 486.0,217.0 494.7,218.1 503.3,219.2 512.0,220.3 520.7,221.3 529.3,222.3 538.0,223.2 546.7,224.1 555.3,225.0 564.0,225.8 572.7,226.7 581.3,227.5 590.0,228.2"/><circle cx="70.0" cy="76.0" r="4" fill="#4c8bf5"/><text x="76.0" y="67.95999999999998" text-anchor="start" style="font-size:11px;font-weight:700">0.458</text><circle cx="243.3" cy="163.0" r="4" fill="#4c8bf5"/><text x="249.33333333333334" y="154.98" text-anchor="start" style="font-size:11px;font-weight:700">0.229</text><circle cx="416.7" cy="206.3" r="4" fill="#4c8bf5"/><text x="422.6666666666667" y="198.3" text-anchor="start" style="font-size:11px;font-weight:700">0.115</text><circle cx="590.0" cy="228.3" r="4" fill="#4c8bf5"/><text x="596.0" y="220.34" text-anchor="start" style="font-size:11px;font-weight:700">0.057</text><polyline fill="none" stroke="#e5aa28" stroke-width="2.5" stroke-dasharray="6 4" points="156.7,155.0 243.3,202.5 330.0,226.2 416.7,238.1"/><circle cx="156.7" cy="155.0" r="4" fill="#e5aa28"/><circle cx="243.3" cy="202.5" r="4" fill="#e5aa28"/><circle cx="330.0" cy="226.2" r="4" fill="#e5aa28"/><circle cx="416.7" cy="238.1" r="4" fill="#e5aa28"/><text x="164.66666666666669" y="147.0" text-anchor="start" style="font-size:11px;font-weight:700">A2C の最大誤差 1/(2n)</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="156.66666666666669" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="243.33333333333334" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">4</text><text x="330.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">8</text><text x="416.6666666666667" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">16</text><text x="503.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">32</text><text x="590.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">64</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.25</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="330.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">サンプル数 n(A2C)または平均するフレーム数 N(ハッシュ、アルファ 0.3)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">誤差</text></svg>

A2C はサンプル数が増えるほど誤差が小さくなりますが、サンプル数は MSAA の設定で決まります。ハッシュドは MSAA が要らないかわりに平均するフレームが必要で、動く物では履歴が合いません。どちらも万能ではなく縁の細かさと予算で選びます。

### 遠くで葉が痩せる {#mip-thinning}

テクスチャのミップは 2×2 の平均で縮めます。アルファも平均されるのでしきい値 0.5 を超える画素が、遠くのミップで減ります。細い物ほどこの影響が大きくなります。

実際に作って確かめました。256×256 のテクスチャに幅が根元で約 6 画素、先で約 1.8 画素の草の葉と楕円を 5 枚重ねた葉の塊を描き縁は 1.5〜2 画素のなだらかな縁にしました。ミップを 2×2 の平均で作りアルファが 0.5 を超える画素の割合を数えます。

- 草の葉: ミップ 0〜2 は 1.5%、ミップ 3（32×32）で 0.0%、ミップ 4 も 0.0%
- 葉の塊: ミップ 0〜2 は 11.9%、ミップ 3 は 11.5%、ミップ 4 は 11.7%

葉の塊は広い面積を持つのでミップ 4 まででほとんど減りません。以前のページにあった「40%、10%」のような急な減り方は実際には細い物（草）でだけ起きます。草の葉はミップ 3 で全体が 0.5 を割ってしまい遠くの草が消えます。

### ミップごとにアルファを補正する {#mip-correct}

対策はミップごとにカバレッジが元と同じになるようアルファに倍率を掛けることです。ミップ 0 のカバレッジを目標に二分探索で倍率を探します。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="ミップとカバレッジ"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">草の葉のカバレッジ</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="110.0,107.5 220.0,107.5 330.0,107.5 440.0,250.0 550.0,250.0"/><circle cx="110.0" cy="107.5" r="4" fill="#e5484d"/><circle cx="220.0" cy="107.5" r="4" fill="#e5484d"/><circle cx="330.0" cy="107.5" r="4" fill="#e5484d"/><circle cx="440.0" cy="250.0" r="4" fill="#e5484d"/><circle cx="550.0" cy="250.0" r="4" fill="#e5484d"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="110.0,107.5 220.0,107.5 330.0,98.0 440.0,117.0 550.0,136.0"/><circle cx="110.0" cy="107.5" r="4" fill="#2e9e5b"/><circle cx="220.0" cy="107.5" r="4" fill="#2e9e5b"/><circle cx="330.0" cy="98.0" r="4" fill="#2e9e5b"/><circle cx="440.0" cy="117.0" r="4" fill="#2e9e5b"/><circle cx="550.0" cy="136.0" r="4" fill="#2e9e5b"/><text x="440.0" y="240.0" text-anchor="middle" style="font-size:11px;font-weight:700">補正なし: ミップ 3 で 0%</text><text x="440.0" y="107.0" text-anchor="middle" style="font-size:11px;font-weight:700">補正: 1.4%</text><text x="110.0" y="268" text-anchor="middle" style="font-size:10px;font-weight:400">ミップ 0 (256²)</text><text x="220.0" y="268" text-anchor="middle" style="font-size:10px;font-weight:400">ミップ 1 (128²)</text><text x="330.0" y="268" text-anchor="middle" style="font-size:10px;font-weight:400">ミップ 2 (64²)</text><text x="440.0" y="268" text-anchor="middle" style="font-size:10px;font-weight:400">ミップ 3 (32²)</text><text x="550.0" y="268" text-anchor="middle" style="font-size:10px;font-weight:400">ミップ 4 (16²)</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0%</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">1%</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">2%</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">アルファが 0.5 を超える画素の割合(草の葉)</text></svg>

- ミップ 1: 倍率 ×1.02、カバレッジ 1.5%
- ミップ 2: ×1.02、1.6%
- ミップ 3: ×1.59、1.4%
- ミップ 4: ×2.86、1.2%

補正なしでは 0% になるミップ 3 と 4 で、1.4% と 1.2% が残ります。目標の 1.5% には届きませんが、消えるのは避けられます。倍率が大きいほどアルファが 1 を超えて切られる画素が増えるので、細くなる限界はあります。ミップ 5（8×8）では倍率を 16 まで上げても 1 テクセルを超えられず、補正も効きません。葉の塊は倍率が 1.00〜1.18 で、補正はわずかです。

補正はミップを作るツールの段階で行います。実行時のシェーダーは普通にミップを読むだけで済みます。ツールで直せない既存のテクスチャには、シェーダーでミップが進むほどしきい値を下げる簡易版が使えます。ただし、ミップごとのアルファの分布は画像で違うので、前処理の補正より精度は劣ります。

## 葉を透かす光 {#transmission}

葉は薄く光を透かします。順光では普通の拡散面に見えますが、逆光では葉が下から光って見えます。普通のライティング（法線と光の内積を 0 で切る）だと逆光の葉は真っ黒になってしまいます。

向きがランダムな葉を 40 万枚用意し、法線を視線の側へ向けて（両面描画で裏の法線を反転）、光が表から当たる分を反射、裏から当たる分を透過として平均を取りました（反射率と透過率はどちらも 1 とした場合の割合です）。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="反射と透過"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">角度ごとの反射と透過</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="100" y="91.7" width="34" height="158.3" fill="rgba(229,170,40,0.55)" stroke="currentColor"/><text x="117" y="86.66666666666666" text-anchor="middle" style="font-size:11px;font-weight:700">0.50</text><rect x="136" y="250.0" width="34" height="0.0" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="153" y="245.0" text-anchor="middle" style="font-size:11px;font-weight:700">0.00</text><text x="135" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><rect x="198" y="114.8" width="34" height="135.2" fill="rgba(229,170,40,0.55)" stroke="currentColor"/><text x="215" y="109.78333333333333" text-anchor="middle" style="font-size:11px;font-weight:700">0.43</text><rect x="234" y="226.9" width="34" height="23.1" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="251" y="221.88333333333333" text-anchor="middle" style="font-size:11px;font-weight:700">0.07</text><text x="233" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">45°</text><rect x="296" y="170.8" width="34" height="79.2" fill="rgba(229,170,40,0.55)" stroke="currentColor"/><text x="313" y="165.83333333333331" text-anchor="middle" style="font-size:11px;font-weight:700">0.25</text><rect x="332" y="170.5" width="34" height="79.5" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="349" y="165.51666666666665" text-anchor="middle" style="font-size:11px;font-weight:700">0.25</text><text x="331" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90°</text><rect x="394" y="226.9" width="34" height="23.1" fill="rgba(229,170,40,0.55)" stroke="currentColor"/><text x="411" y="221.88333333333333" text-anchor="middle" style="font-size:11px;font-weight:700">0.07</text><rect x="430" y="114.8" width="34" height="135.2" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="447" y="109.78333333333333" text-anchor="middle" style="font-size:11px;font-weight:700">0.43</text><text x="429" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">135°</text><rect x="492" y="250.0" width="34" height="0.0" fill="rgba(229,170,40,0.55)" stroke="currentColor"/><text x="509" y="245.0" text-anchor="middle" style="font-size:11px;font-weight:700">0.00</text><rect x="528" y="91.7" width="34" height="158.3" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="545" y="86.66666666666666" text-anchor="middle" style="font-size:11px;font-weight:700">0.50</text><text x="527" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">180°</text><text x="586" y="64" text-anchor="end" style="font-size:12px;font-weight:700">黄: 反射  緑: 透過</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="174.83333333333331" text-anchor="end" style="font-size:11px;font-weight:400">0.25</text><text x="62" y="95.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="330.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">光の向きと視線のなす角(0° = 順光、180° = 逆光)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">ランダムな向きの葉の平均</text></svg>

- 光と視線のなす角 0 度（順光）: 反射 0.500、透過 0.000
- 45 度: 反射 0.427、透過 0.073
- 90 度: 反射 0.250、透過 0.251
- 135 度: 反射 0.073、透過 0.427
- 180 度（逆光）: 反射 0.000、透過 0.500

反射と透過の合計はどの角度でも 0.500 です。向きがランダムなら光が表から当たる確率と裏から当たる確率の合計が一定なためです。片面ライティング（法線を直さない）の平均は、どの角度でも約 0.250 で、逆光（180 度）では両面にして透過を足したときの 0.500 の半分でしかありません。逆光の場面で葉の塊が暗く沈むのは、この差です。

実際の葉の透過は色がつきます。葉を透かした光は緑から黄緑になるのが普通なので、透過の色 `g_leaf_transmit` は緑寄りの色にします（例では `(0.35, 0.55, 0.10)`、一例です）。透過の量は葉の厚みや裏面のテクスチャで変えられますが、このページのコードでは固定です。

## 木の葉と LOD {#trees}

木の葉は板（カード）に葉の絵を貼って描きます。アルファ テストで形を切り抜き影も切り抜きます（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)）。遠景は木全体を 1 枚の板にします（[Trees](trees.md)）。LOD を切り替えるときは 4×4 の Bayer 行列でディザをかけ 2 つの LOD を混ぜると、ポップが目立ちません。4×4 の行列は 16 段階のしきい値を持つので、`fade` を 1/16 刻みで下げると、残る画素が 1/16 ずつ減ります。

## コード：葉のピクセル シェーダー {#code}

ここからコードを数行ずつ見ます。最初は定数とテクスチャです。

```hlsl
cbuffer FoliageCB : register(b0) {
  float3 g_light_dir;        // 光が進む向き(正規化済み)。面から光へ向かう向きは -g_light_dir
  float  g_cutoff;           // アルファ テストのしきい値。例: 0.5
  float3 g_light_color;      // 光の色(放射照度)
  float  g_lod_fade;         // LOD の切り替え 0〜1(1 = 完全に見える、0 = 消える)
  float3 g_camera_pos;       // カメラのワールド位置
  float  g_frame_index;      // フレーム番号(ハッシュの種に使う)
  float3 g_leaf_transmit;    // 葉を透かした光の色。例: (0.35, 0.55, 0.10) 黄緑
  float  g_ambient;          // 環境光の強さ
};

Texture2D<float4> g_albedo : register(t0);     // rgb = 葉の色、a = 形(アルファ)
SamplerState g_linear_wrap : register(s0);

struct PSIn {
  float4 position : SV_Position;
  float2 uv : TEXCOORD0;
  float3 world_pos : TEXCOORD1;
  float3 world_normal : TEXCOORD2;
};
```

`g_cutoff` はアルファ テストのしきい値、`g_lod_fade` は LOD のフェードの度合いです。`g_leaf_transmit` が透けた光の色です。

ディザと乱数の関数です。

```hlsl
// 4×4 の Bayer 行列(0〜15)。画面の画素の位置で決まる、市松に近いしきい値の並び。
static const float kBayer4[16] = {0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5};
float Bayer4(uint2 p) { return (kBayer4[(p.y & 3) * 4 + (p.x & 3)] + 0.5) / 16.0; }   // 0〜1 のしきい値

// 画素ごとの乱数 [0, 1)。PCG ハッシュ(自作の簡易版)。時間とともに値が変わるので、TAA が平均する。
float Hash01(uint2 p, uint frame) {
  uint s = p.x * 1664525u + p.y * 1013904223u + frame * 22695477u;   // 3 つの整数を混ぜる
  s = s * 747796405u + 2891336453u;                                 // PCG の 1 ステップ
  s = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u;
  s = (s >> 22u) ^ s;
  return float(s) * (1.0 / 4294967296.0);                           // 0〜1 に正規化
}

// 縁を画素の幅でなめらかにしたアルファ(A2C 用)。fwidth は隣の画素とのアルファの差。
float SharpenAlpha(float alpha, float cutoff) {
  float w = max(fwidth(alpha), 1e-4);                               // 0 割りを避ける
  return saturate((alpha - cutoff) / w + 0.5);                      // 縁の 1 画素の幅で 0 → 1
}
```

`Bayer4` は画面の位置で決まる 0〜1 のしきい値です。画素ごとに値が違うのでフェードの途中で、細かい市松の模様になります。`Hash01` は画素とフレーム番号から 0〜1 の乱数を作ります。フレームごとに値が変わるので、TAA が平均します。ハッシュは自作の簡易版で特定の資料の関数ではありません。`SharpenAlpha` はアルファの傾き `fwidth` で割って、0.5 付近の 1 画素の幅だけアルファを段階的にします。これを A2C のアルファに使います（足した処理です）。

本体です。

```hlsl
float4 FoliagePS(PSIn i, bool front : SV_IsFrontFace) : SV_Target {
  float4 tex = g_albedo.Sample(g_linear_wrap, i.uv);
  float alpha = tex.a;

  // ① 遠くで痩せるのを、しきい値を下げて補う(ツールでミップのアルファを補正できない場合の簡易版)。
  float mip = g_albedo.CalculateLevelOfDetail(g_linear_wrap, i.uv);   // 画素あたりのテクセル数 → ミップ番号
  float cutoff = lerp(g_cutoff, 0.5 * g_cutoff, saturate(mip / 4.0));   // ミップ 4 でしきい値が半分

  // ② LOD の切り替え: 市松のディザで 2 つの LOD を混ぜる。fade が小さいほど多くの画素を捨てる。
  if (g_lod_fade < Bayer4(uint2(i.position.xy))) discard;

  // ③ アルファ テスト。画素ごとに残すか捨てるかを決める。
  if (alpha < cutoff) discard;

  // ④ 光の計算。裏面なら法線を反転して、いつも視線の側を向ける。
  float3 N = normalize(i.world_normal);
  N = front ? N : -N;                                               // 両面描画: 見えている側が表
  float3 L = -g_light_dir;                                          // 面から光へ
  float d = dot(N, L);                                              // 正なら、光が見えている側から当たる
  float3 reflected = tex.rgb * g_light_color * saturate(d);         // 反射した光
  float3 transmitted = tex.rgb * g_leaf_transmit * g_light_color * saturate(-d);   // 葉の裏から当たって透けた光
  float3 ambient = tex.rgb * g_ambient;                             // 環境光は向きに関係なく残る
  return float4(reflected + transmitted + ambient, 1.0);
}
```

最初にテクスチャを読みミップの番号を `CalculateLevelOfDetail` で得て、ミップが進むほどしきい値を下げます（ミップ 4 で半分）。これはツールで補正できないときの簡易版です。LOD のフェードは `g_lod_fade` より `Bayer4` が大きい画素を捨てます。アルファ テストはしきい値より小さいアルファを捨てます。ライティングでは `SV_IsFrontFace` で裏面を判定し、法線を反転していつも見える側を表にします。`d` が正なら光が見える側から当たるので反射、負なら裏から当たるので透過の色を掛けた光を足します。

A2C とハッシュド アルファの版です。

```hlsl
// A2C 版: 色は同じで、アルファをなめらかにしたものを SV_Target のアルファに入れる(Alpha to Coverage を ON にしておく)。
float4 FoliageA2CPS(PSIn i, bool front : SV_IsFrontFace) : SV_Target {
  float4 color = FoliagePS(i, front);
  float alpha = g_albedo.Sample(g_linear_wrap, i.uv).a;
  color.a = SharpenAlpha(alpha, g_cutoff);                          // アルファが 0.5 付近の縁だけ段階的に
  return color;
}

// ハッシュド アルファ版: しきい値を画素ごと・フレームごとに変えて、時間方向の平均で半透明に見せる。
float4 FoliageHashedPS(PSIn i, bool front : SV_IsFrontFace) : SV_Target {
  float alpha = g_albedo.Sample(g_linear_wrap, i.uv).a;
  float threshold = Hash01(uint2(i.position.xy), (uint)g_frame_index);   // 画素ごと・フレームごとに違う
  if (alpha < threshold) discard;                                   // 残る確率が alpha になる
  return FoliagePS(i, front);                                       // 色は ①〜④ と同じ(ここでのアルファ テストは通る)
}
```

A2C 版は色を本体と同じにして、アルファだけを `SharpenAlpha` の結果にし、Alpha to Coverage を有効にします。ハッシュド版はしきい値を画素とフレームで変えて、アルファが乱数より小さいときに捨てます。

## よくあるミス {#mistakes}

??? failure "遠くの草が消えてしまう"
    細い物のアルファがミップで 0.5 を割っています。草の例ではミップ 3 で 0% でした。ミップごとにアルファへ倍率を掛けるかしきい値をミップで下げます。

??? failure "逆光の葉が真っ黒になる"
    片面ライティングで裏から当たる光を捨てています。裏面の法線を反転し透過の項を足します。逆光で反射が 0 のとき透過が 0.500 を担っています。

??? failure "縁がギザギザで、MSAA を入れても変わらない"
    `discard` はサンプルごとの結果にならないためです。Alpha to Coverage にするかハッシュド アルファと TAA の組み合わせにします。

??? failure "ハッシュド アルファの葉がちらつく"
    平均するフレームが足りません。アルファ 0.3 なら 4 フレームで標準偏差 0.229 です。TAA の履歴を使えない動く物には向きません。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 葉は半透明にせずアルファ テスト系で切り抜く
    - [x] 草のような細い物は、ミップでアルファが薄まり消える。ミップごとに補正する
    - [x] 縁は A2C かハッシュド アルファ。A2C の誤差は `1/(2n)`
    - [x] 葉は薄いので、逆光では光が透ける。両面描画で法線を反転し透過の項を足す

## C++ で数えたもの {#numbers}

```cpp
// 葉の半透明（アルファ テスト・ミップのアルファ・A2C・ハッシュ・光の透過）の数字を数える。g++ -std=c++23 -Wall -Wextra
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <numeric>
#include <random>
#include <vector>

constexpr double kPi = 3.14159265358979323846;

struct Image {
  int n;                     // 一辺の画素数
  std::vector<float> a;      // アルファ(0〜1)
  explicit Image(int size) : n(size), a(static_cast<size_t>(size) * size, 0.0f) {}
  float& at(int x, int y) { return a[static_cast<size_t>(y) * n + x]; }
  float at(int x, int y) const { return a[static_cast<size_t>(y) * n + x]; }
};

float Smoothstep(float e0, float e1, float x) {            // e0 から e1 へなめらかに 0 → 1
  const float t = std::clamp((x - e0) / (e1 - e0), 0.0f, 1.0f);
  return t * t * (3.0f - 2.0f * t);
}

// 草の葉: 幅が約 6 画素の細い帯(縁は 1.5 画素のなだらかな縁)。
Image MakeBlade(int n) {
  Image img(n);
  for (int y = 0; y < n; ++y) {
    for (int x = 0; x < n; ++x) {
      const float taper = 1.0f - 0.7f * (static_cast<float>(y) / n);        // 先へ行くほど細くなる
      const float half_width = 3.0f * taper;                                 // 半幅(画素)。根元で 3、先で 0.9
      const float d = std::fabs(x + 0.5f - n * 0.5f);                        // 中心線からの距離
      img.at(x, y) = 1.0f - Smoothstep(half_width - 0.75f, half_width + 0.75f, d);
    }
  }
  return img;
}

// 葉の塊: 楕円を 5 枚重ねた絵(縁は 2 画素のなだらかな縁)。
Image MakeLeafCluster(int n) {
  Image img(n);
  const float cx[5] = {0.30f, 0.62f, 0.45f, 0.75f, 0.20f};
  const float cy[5] = {0.35f, 0.30f, 0.62f, 0.68f, 0.72f};
  const float rx[5] = {0.14f, 0.10f, 0.15f, 0.09f, 0.08f};
  const float ry[5] = {0.07f, 0.09f, 0.06f, 0.05f, 0.07f};
  for (int y = 0; y < n; ++y) {
    for (int x = 0; x < n; ++x) {
      float best = 0.0f;
      for (int k = 0; k < 5; ++k) {
        const float dx = ((x + 0.5f) / n - cx[k]) / rx[k], dy = ((y + 0.5f) / n - cy[k]) / ry[k];
        const float r = std::sqrt(dx * dx + dy * dy);                         // 楕円の半径(1 が縁)
        best = std::max(best, 1.0f - Smoothstep(1.0f - 2.0f / (rx[k] * n), 1.0f + 2.0f / (rx[k] * n), r));
      }
      img.at(x, y) = best;
    }
  }
  return img;
}

Image Downsample(const Image& src) {                       // 2×2 の平均(ふつうのミップ)
  Image dst(std::max(1, src.n / 2));
  for (int y = 0; y < dst.n; ++y)
    for (int x = 0; x < dst.n; ++x)
      dst.at(x, y) = 0.25f * (src.at(2 * x, 2 * y) + src.at(2 * x + 1, 2 * y) + src.at(2 * x, 2 * y + 1) + src.at(2 * x + 1, 2 * y + 1));
  return dst;
}

double Coverage(const Image& img, float threshold, float scale) {   // しきい値を超える画素の割合
  size_t c = 0;
  for (float v : img.a) if (v * scale > threshold) ++c;
  return static_cast<double>(c) / img.a.size();
}

float FindScale(const Image& img, float threshold, double target) {  // 二分探索: カバレッジが target になる倍率
  float lo = 0.0f, hi = 16.0f;
  for (int i = 0; i < 40; ++i) {
    const float mid = 0.5f * (lo + hi);
    if (Coverage(img, threshold, mid) < target) lo = mid; else hi = mid;
  }
  return 0.5f * (lo + hi);
}

void MipExperiment(const char* name, const Image& base) {
  std::printf("-- %s: coverage at alpha > 0.5 per mip (256 x 256 base)\n", name);
  Image cur = base;
  const double target = Coverage(base, 0.5f, 1.0f);            // ミップ 0 のカバレッジ
  for (int level = 0; level < 5; ++level) {
    const float scale = FindScale(cur, 0.5f, target);
    std::printf("mip %d (%3d x %3d): plain %5.1f%%, corrected %5.1f%% (alpha scale x%.2f), mean alpha %.3f\n", level, cur.n, cur.n,
                100 * Coverage(cur, 0.5f, 1.0f), 100 * Coverage(cur, 0.5f, scale), scale,
                std::accumulate(cur.a.begin(), cur.a.end(), 0.0) / cur.a.size());
    cur = Downsample(cur);
  }
}

int main() {
  std::printf("-- why not blend: sorting and bandwidth\n");
  const double blades = 1.0e6;
  std::printf("%.0f instances: n log2 n = %.2e comparisons per frame\n", blades, blades * std::log2(blades));
  const double px = 1920.0 * 1080.0;
  for (int overdraw : {2, 4, 8}) {
    const double bytes = px * overdraw * 8.0;                  // RGBA8 を 1 回読んで 1 回書く = 8 バイト
    std::printf("1080p, average overdraw %d: blend traffic %.1f MB/frame = %.2f GB/s at 60 fps\n", overdraw, bytes / 1.0e6, bytes * 60 / 1.0e9);
  }

  MipExperiment("grass blade", MakeBlade(256));
  MipExperiment("leaf cluster", MakeLeafCluster(256));

  std::printf("-- alpha to coverage: quantization with n samples (round to nearest)\n");
  for (int n : {2, 4, 8, 16}) {
    double max_err = 0, sum_err = 0;
    const int m = 100000;
    for (int i = 0; i <= m; ++i) {
      const double a = static_cast<double>(i) / m;
      const double q = std::round(a * n) / n;                  // 立てるサンプルの数 / n
      max_err = std::max(max_err, std::fabs(a - q));
      sum_err += std::fabs(a - q);
    }
    std::printf("n = %2d: levels %2d, max error %.4f (= 1/(2n)), mean error %.4f (= 1/(4n))\n", n, n + 1, max_err, sum_err / (m + 1));
  }

  std::printf("-- hashed alpha: coverage of alpha = 0.3 averaged over N frames (random threshold per frame)\n");
  std::mt19937 rng(12345);
  std::uniform_real_distribution<double> u(0.0, 1.0);
  for (int frames : {1, 4, 8, 16, 64}) {
    double var = 0;
    const int trials = 20000;
    for (int t = 0; t < trials; ++t) {
      int hits = 0;
      for (int f = 0; f < frames; ++f) hits += (0.3 > u(rng));  // しきい値が一様乱数 → アルファが 0.3 なら 30% の確率で残る
      const double est = static_cast<double>(hits) / frames;
      var += (est - 0.3) * (est - 0.3);
    }
    std::printf("N = %2d frames: measured sigma %.3f, formula sqrt(a(1-a)/N) = %.3f\n", frames, std::sqrt(var / trials), std::sqrt(0.3 * 0.7 / frames));
  }

  std::printf("-- leaf light: random leaf orientation, mean reflected / transmitted (rho = tau = 1)\n");
  std::mt19937 rng2(777);
  std::normal_distribution<double> g(0.0, 1.0);
  for (int deg : {0, 45, 90, 135, 180}) {
    // 視線方向 V = +z。光の向き L は V から deg だけ傾ける(deg = 180 なら逆光)。
    const double lx = std::sin(deg * kPi / 180), lz = std::cos(deg * kPi / 180);
    double refl = 0, trans = 0, refl_one_sided = 0;
    const int n = 400000;
    for (int i = 0; i < n; ++i) {
      double nx = g(rng2), ny = g(rng2), nz = g(rng2);
      const double len = std::sqrt(nx * nx + ny * ny + nz * nz);
      nx /= len; ny /= len; nz /= len;                         // 葉の法線(球面上で一様)
      refl_one_sided += std::max(nx * lx + nz * lz, 0.0);       // 向きを直さない片面ライティング
      if (nz < 0) { nx = -nx; ny = -ny; nz = -nz; }            // 視線の側へ向ける(両面描画で裏の法線を反転)
      const double d = nx * lx + nz * lz;                      // 光が表(視線の側)に当たるなら正
      refl += std::max(d, 0.0);                                // 反射する分
      trans += std::max(-d, 0.0);                              // 透過する分(光が裏から当たるとき)
    }
    std::printf("angle(L, V) = %3d deg: one-sided %.3f, two-sided reflect %.3f, transmit %.3f, total %.3f\n", deg, refl_one_sided / n, refl / n, trans / n, (refl + trans) / n);
  }
  return 0;
}
```

```text title="実行結果"
-- why not blend: sorting and bandwidth
1000000 instances: n log2 n = 1.99e+07 comparisons per frame
1080p, average overdraw 2: blend traffic 33.2 MB/frame = 1.99 GB/s at 60 fps
1080p, average overdraw 4: blend traffic 66.4 MB/frame = 3.98 GB/s at 60 fps
1080p, average overdraw 8: blend traffic 132.7 MB/frame = 7.96 GB/s at 60 fps
-- grass blade: coverage at alpha > 0.5 per mip (256 x 256 base)
mip 0 (256 x 256): plain   1.5%, corrected   1.5% (alpha scale x0.99), mean alpha 0.015
mip 1 (128 x 128): plain   1.5%, corrected   1.5% (alpha scale x1.02), mean alpha 0.015
mip 2 ( 64 x  64): plain   1.5%, corrected   1.6% (alpha scale x1.02), mean alpha 0.015
mip 3 ( 32 x  32): plain   0.0%, corrected   1.4% (alpha scale x1.59), mean alpha 0.015
mip 4 ( 16 x  16): plain   0.0%, corrected   1.2% (alpha scale x2.86), mean alpha 0.015
-- leaf cluster: coverage at alpha > 0.5 per mip (256 x 256 base)
mip 0 (256 x 256): plain  11.9%, corrected  11.9% (alpha scale x1.00), mean alpha 0.119
mip 1 (128 x 128): plain  11.9%, corrected  11.9% (alpha scale x1.03), mean alpha 0.119
mip 2 ( 64 x  64): plain  11.9%, corrected  11.9% (alpha scale x1.00), mean alpha 0.119
mip 3 ( 32 x  32): plain  11.5%, corrected  11.9% (alpha scale x1.15), mean alpha 0.119
mip 4 ( 16 x  16): plain  11.7%, corrected  12.1% (alpha scale x1.01), mean alpha 0.119
-- alpha to coverage: quantization with n samples (round to nearest)
n =  2: levels  3, max error 0.2500 (= 1/(2n)), mean error 0.1250 (= 1/(4n))
n =  4: levels  5, max error 0.1250 (= 1/(2n)), mean error 0.0625 (= 1/(4n))
n =  8: levels  9, max error 0.0625 (= 1/(2n)), mean error 0.0312 (= 1/(4n))
n = 16: levels 17, max error 0.0312 (= 1/(2n)), mean error 0.0156 (= 1/(4n))
-- hashed alpha: coverage of alpha = 0.3 averaged over N frames (random threshold per frame)
N =  1 frames: measured sigma 0.460, formula sqrt(a(1-a)/N) = 0.458
N =  4 frames: measured sigma 0.229, formula sqrt(a(1-a)/N) = 0.229
N =  8 frames: measured sigma 0.161, formula sqrt(a(1-a)/N) = 0.162
N = 16 frames: measured sigma 0.114, formula sqrt(a(1-a)/N) = 0.115
N = 64 frames: measured sigma 0.057, formula sqrt(a(1-a)/N) = 0.057
-- leaf light: random leaf orientation, mean reflected / transmitted (rho = tau = 1)
angle(L, V) =   0 deg: one-sided 0.250, two-sided reflect 0.500, transmit 0.000, total 0.500
angle(L, V) =  45 deg: one-sided 0.250, two-sided reflect 0.427, transmit 0.073, total 0.500
angle(L, V) =  90 deg: one-sided 0.250, two-sided reflect 0.250, transmit 0.251, total 0.501
angle(L, V) = 135 deg: one-sided 0.250, two-sided reflect 0.073, transmit 0.427, total 0.500
angle(L, V) = 180 deg: one-sided 0.249, two-sided reflect 0.000, transmit 0.500, total 0.500
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。

- Ignacio Castaño, "Computing Alpha Mipmaps", 2010
- Chris Wyman, Morgan McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games, 2017
- Tiago Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007
- Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`）

## 関連ページ {#related}

- [Vegetation](index.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
- [Alpha to Coverage](../../translucency/alpha-test/alpha-to-coverage.md)
- [Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)
- [Grass Shape](grass-shape.md)
