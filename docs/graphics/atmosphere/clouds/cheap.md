---
title: Cheap Alternatives
tags:
  - 描画
---

# Cheap Alternatives

ボリューム雲のレイマーチはきれいですが重いものです。モバイルでは 1 フレームの予算に入りませんし、PC でもカメラが地面から動かないゲームなら雲の中を通れる立体感はそもそも使いません。そういう場面では板や絵で済ませるほうが速くて、制作も楽です。このページでは雲を絵として扱う安い方法を 4 つ取り上げます。空全体を 1 枚の平面に見立てる方法、その平面を重ねて視差を出す方法、個々の雲を板にする方法、板に焼いた絵を貼るインポスターです。どれも新しい論文があるわけではない古典的な手法なので、式は幾何から導き数字は C++ で数え HLSL は fxc で通しました。

このページに載せたコードは HLSL を `fxc`（`ps_5_0` / `vs_5_0`）でコンパイルして確かめたもので、実際に描画した結果は確かめていません。C++ は `g++ -std=c++23 -Wall -Wextra` で通し実行して本文に載せた数字を出しました。

!!! tip "ポイント"
    - 平面に雲を貼ると、地平線の近くで絵が縦に潰れます。仰角 5° で縦と横の縮尺は 1 対 11.5 です。異方性フィルタ 16 倍が効くのは、仰角が 3.6° より上の範囲です。
    - 視差は層の高さの差だけで決まります。100 m 動いたとき高さ 1000 m の層は 35〜73 画素、2200 m の層は 16〜33 画素ずれます。
    - UV のスクロールは `frac` で 0〜1 に折り返してから渡します。折り返さない float は 100 時間後に 1/8 テクセルの刻みになります。
    - ビルボードは雲が見える角度が小さい遠景に使います。幅 500 m の雲は 2 km で 257 画素、10 km で 52 画素です。

!!! info "このページを読む前に"
    - [Clouds](index.md)（このセクション全体の地図と読む順番）
    - [Cloud Raymarching](raymarch.md)（この安い方法が置き換える、重いほうの方法）

## 4 つの方法の位置づけ {#overview}

雲を安く描く方法はどれくらい近くから見るかで選びます。地上から空を見上げるだけなら 1 枚か数枚の平面で十分です。飛行機で雲に近づくなら板ではもたず本物のボリュームが要ります。その間にある距離を板で埋めます。

| 方式 | 立体感 | コスト | 近づけるか | 向く場面 |
| --- | --- | --- | --- | --- |
| [層の平面](#plane) | なし | 最小 | 近づけない | モバイル、遠景 |
| [重ねた層](#layers) | 視差 | 小 | 近づけない | 中程度の品質 |
| [ビルボード](#billboard) | 中 | 小〜中 | 遠景まで | 点在する積雲 |
| [インポスター](#impostor) | 中 | 中 | 中距離まで | 局所的な雲の塊 |
| ボリューム | 完全 | 重い | 中を通れる | 飛行、高品質 |

<svg class="fig flow" viewBox="0 0 660 270" role="img" aria-label="距離ごとの方式の切り替え"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">方式の切り替え</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">カメラからの距離ごとの方式（目安）</text><rect x="20" y="50" width="190" height="60" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="115.0" y="80.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">近く：ボリューム</text><rect x="225" y="50" width="210" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="330.0" y="80.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">中間：ビルボード</text><rect x="450" y="50" width="190" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="545.0" y="80.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">遠く：層の平面</text><line x1="20" y1="150" x2="640" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="330" y="176" text-anchor="middle" style="font-size:12px;font-weight:400">カメラからの距離</text><text x="20" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="212" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">〜2 km</text><text x="437" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">〜10 km</text><text x="640" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">地平線</text><text x="115" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">雲の中を通れる</text><text x="330" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">近づくと板だと分かる</text><text x="545" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">地平線へ向けて霧に溶かす</text><text x="330" y="250" text-anchor="middle" style="font-size:12px;font-weight:400">境目はアルファのフェードでつなぐ（距離は一例）</text></svg>

距離で方式を替えるハイブリッドは[末尾](#hybrid)で扱います。

## 方法 1：層の平面 {#plane}

空にスカイボックスの絵を貼る方法はカメラが動いても雲の位置が変わらないので、雲が遠くに固定された壁紙のように見えます。もう少しだけ雲らしくするには雲を「カメラの上の水平な平面」に貼ったと考えて、視線がその平面に当たる点を計算します。こうすると地平線に近い雲ほど小さく詰まって見えカメラを動かすと雲の位置も動きます。

### 視線が平面に当たる点 {#plane-math}

カメラの高さを `y_c`、雲の層の高さを `y_l` とします。カメラから単位ベクトル `d` の向きに伸ばした視線が層に届くまでの長さ `t` は、`d.y × t = y_l − y_c` から次のように決まります。

```text
t = (y_l − y_c) / d.y
当たる点 = カメラ位置.xz + d.xz × t
```

`d.y` が 0 に近づく（地平線）と `t` は発散します。視線が真上（`d.y = 1`）なら `t` は層までの高さそのもので、当たる点はカメラの真上です。この `t` の発散が地平線付近で起きる問題の原因です。

### 仰角ごとの当たる位置 {#plane-distance}

層の高さが 1500 m（カメラの上）のとき仰角 `e` の視線が当たる水平距離は `1500 / tan(e)` です。

<svg class="fig flow" viewBox="0 0 720 290" role="img" aria-label="雲の層に視線が当たる位置"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">仰角ごとの当たる位置</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">横から見た図：視線が雲の層に当たる位置（層の高さ 1500 m）</text><line x1="60" y1="145.0" x2="700" y2="145.0" stroke="#4c8bf5" stroke-width="3"/><text x="690" y="137.0" text-anchor="end" style="font-size:12px;font-weight:700">雲の層</text><line x1="60" y1="250" x2="700" y2="250" stroke="#94a3b8" stroke-width="2"/><text x="690" y="268" text-anchor="end" style="font-size:12px;font-weight:400">カメラの高さ</text><line x1="60" y1="250" x2="120.6" y2="145.0" stroke="#2e9e5b" stroke-width="2"/><circle cx="120.6" cy="145.0" r="4" fill="#2e9e5b"/><text x="120.62177826491073" y="165.0" text-anchor="middle" style="font-size:12px;font-weight:700">60° → 0.9 km</text><line x1="60" y1="250" x2="165.0" y2="145.0" stroke="#2e9e5b" stroke-width="2"/><circle cx="165.0" cy="145.0" r="4" fill="#2e9e5b"/><text x="165.00000000000003" y="165.0" text-anchor="middle" style="font-size:12px;font-weight:700">45° → 1.5 km</text><line x1="60" y1="250" x2="348.5" y2="145.0" stroke="#e5aa28" stroke-width="2"/><circle cx="348.5" cy="145.0" r="4" fill="#e5aa28"/><text x="348.4851290427354" y="165.0" text-anchor="middle" style="font-size:12px;font-weight:700">20° → 4.1 km</text><line x1="60" y1="250" x2="655.5" y2="145.0" stroke="#e5484d" stroke-width="2"/><circle cx="655.5" cy="145.0" r="4" fill="#e5484d"/><text x="655.4845910598596" y="165.0" text-anchor="middle" style="font-size:12px;font-weight:700">10° → 8.5 km</text><text x="390" y="232" text-anchor="middle" style="font-size:12px;font-weight:400">5° では 17 km、1° では 86 km 先（図の外）</text><circle cx="60" cy="250" r="5" fill="currentColor"/><text x="60" y="270" text-anchor="middle" style="font-size:12px;font-weight:400">カメラ</text></svg>

C++ で数えると仰角 45° で 1500 m、20° で 4121 m、10° で 8507 m、5° で 17145 m、1° で 85935 m です。地平線の 1° 上は 86 km 先を見ています。この距離では実際の雲は地球の丸みで見えませんし、雲のテクスチャも 1 テクセルが何十メートルにもなります。

### 地平線で絵が潰れる量 {#plane-aniso}

平面上の 1 テクセルの大きさを `s`、層の高さを `h` とします。画面上でそれが占める角度は奥行きの向きと横の向きで違います。視線の仰角が `e` のとき奥行きの向きは `s × sin²(e) / h`、横の向きは `s × sin(e) / h` です。比（奥行き ÷ 横）は `sin(e)` になります。

つまり、仰角 5° の雲は横に比べて縦が 0.087 倍、約 11.5 分の 1 に潰れて見えます。サンプリングから見れば画面の 1 画素の足跡が、縦に 11.5 倍長い楕円になるということです。等方的なミップマップでこれを読むと長いほうの軸に合わせて粗いミップが選ばれ、雲が地平線に向かってぼやけます。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="必要な異方性の倍率"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">仰角と必要な異方性</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="85.0,61.0 86.7,79.9 88.3,95.4 90.0,108.2 91.7,119.1 93.3,128.5 95.0,136.6 96.7,143.7 98.3,149.9 100.0,155.5 101.7,160.5 103.3,164.9 105.0,169.0 106.7,172.7 108.3,176.0 110.0,179.1 111.7,181.9 113.3,184.6 115.0,187.0 116.7,189.2 118.3,191.3 120.0,193.3 121.7,195.1 123.3,196.8 125.0,198.4 126.7,199.9 128.3,201.4 130.0,202.7 131.7,204.0 133.3,205.2 135.0,206.4 136.7,207.4 138.3,208.5 140.0,209.5 141.7,210.4 143.3,211.3 145.0,212.2 146.7,213.0 148.3,213.8 150.0,214.5 151.7,215.2 153.3,215.9 155.0,216.6 156.7,217.2 158.3,217.9 160.0,218.5 161.7,219.0 163.3,219.6 165.0,220.1 166.7,220.6 168.3,221.1 170.0,221.6 171.7,222.1 173.3,222.5 175.0,222.9 176.7,223.4 178.3,223.8 180.0,224.2 181.7,224.6 183.3,224.9 185.0,225.3 186.7,225.6 188.3,226.0 190.0,226.3 191.7,226.6 193.3,226.9 195.0,227.3 196.7,227.6 198.3,227.8 200.0,228.1 201.7,228.4 203.3,228.7 205.0,228.9 206.7,229.2 208.3,229.4 210.0,229.7 211.7,229.9 213.3,230.1 215.0,230.4 216.7,230.6 218.3,230.8 220.0,231.0 221.7,231.2 223.3,231.4 225.0,231.6 226.7,231.8 228.3,232.0 230.0,232.2 231.7,232.4 233.3,232.6 235.0,232.7 236.7,232.9 238.3,233.1 240.0,233.2 241.7,233.4 243.3,233.6 245.0,233.7 246.7,233.9 248.3,234.0 250.0,234.2 251.7,234.3 253.3,234.4 255.0,234.6 256.7,234.7 258.3,234.8 260.0,235.0 261.7,235.1 263.3,235.2 265.0,235.4 266.7,235.5 268.3,235.6 270.0,235.7 271.7,235.8 273.3,236.0 275.0,236.1 276.7,236.2 278.3,236.3 280.0,236.4 281.7,236.5 283.3,236.6 285.0,236.7 286.7,236.8 288.3,236.9 290.0,237.0 291.7,237.1 293.3,237.2 295.0,237.3 296.7,237.4 298.3,237.5 300.0,237.6 301.7,237.6 303.3,237.7 305.0,237.8 306.7,237.9 308.3,238.0 310.0,238.1 311.7,238.1 313.3,238.2 315.0,238.3 316.7,238.4 318.3,238.5 320.0,238.5 321.7,238.6 323.3,238.7 325.0,238.7 326.7,238.8 328.3,238.9 330.0,239.0 331.7,239.0 333.3,239.1 335.0,239.2 336.7,239.2 338.3,239.3 340.0,239.4 341.7,239.4 343.3,239.5 345.0,239.5 346.7,239.6 348.3,239.7 350.0,239.7 351.7,239.8 353.3,239.8 355.0,239.9 356.7,240.0 358.3,240.0 360.0,240.1 361.7,240.1 363.3,240.2 365.0,240.2 366.7,240.3 368.3,240.3 370.0,240.4 371.7,240.4 373.3,240.5 375.0,240.5 376.7,240.6 378.3,240.6 380.0,240.7 381.7,240.7 383.3,240.8 385.0,240.8 386.7,240.9 388.3,240.9 390.0,241.0 391.7,241.0 393.3,241.1 395.0,241.1 396.7,241.1 398.3,241.2 400.0,241.2 401.7,241.3 403.3,241.3 405.0,241.4 406.7,241.4 408.3,241.4 410.0,241.5 411.7,241.5 413.3,241.6 415.0,241.6 416.7,241.6 418.3,241.7 420.0,241.7 421.7,241.8 423.3,241.8 425.0,241.8 426.7,241.9 428.3,241.9 430.0,241.9 431.7,242.0 433.3,242.0 435.0,242.0 436.7,242.1 438.3,242.1 440.0,242.1 441.7,242.2 443.3,242.2 445.0,242.2 446.7,242.3 448.3,242.3 450.0,242.3 451.7,242.4 453.3,242.4 455.0,242.4 456.7,242.5 458.3,242.5 460.0,242.5 461.7,242.6 463.3,242.6 465.0,242.6 466.7,242.6 468.3,242.7 470.0,242.7 471.7,242.7 473.3,242.8 475.0,242.8 476.7,242.8 478.3,242.8 480.0,242.9 481.7,242.9 483.3,242.9 485.0,242.9 486.7,243.0 488.3,243.0 490.0,243.0 491.7,243.1 493.3,243.1 495.0,243.1 496.7,243.1 498.3,243.2 500.0,243.2 501.7,243.2 503.3,243.2 505.0,243.3 506.7,243.3 508.3,243.3 510.0,243.3 511.7,243.3 513.3,243.4 515.0,243.4 516.7,243.4 518.3,243.4 520.0,243.5 521.7,243.5 523.3,243.5 525.0,243.5 526.7,243.5 528.3,243.6 530.0,243.6 531.7,243.6 533.3,243.6 535.0,243.7 536.7,243.7 538.3,243.7 540.0,243.7 541.7,243.7 543.3,243.8 545.0,243.8 546.7,243.8 548.3,243.8 550.0,243.8 551.7,243.9 553.3,243.9 555.0,243.9 556.7,243.9 558.3,243.9 560.0,244.0 561.7,244.0 563.3,244.0 565.0,244.0 566.7,244.0 568.3,244.0 570.0,244.1"/><line x1="70" y1="202.5" x2="570" y2="202.5" stroke="#e5484d" stroke-dasharray="5 4"/><text x="564" y="196.5" text-anchor="end" style="font-size:12px;font-weight:400">16 倍の異方性フィルタの上限</text><circle cx="129.7" cy="202.5" r="4" fill="#e5484d"/><text x="139.66666666666666" y="220.5" text-anchor="start" style="font-size:12px;font-weight:700">3.6°</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="236.66666666666666" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">10°</text><text x="403.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">20°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30°</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">16</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">32</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">48</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">64</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">視線の仰角</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">必要な異方性の倍率 1 / sin(仰角)</text></svg>

異方性フィルタリングはこの楕円を 1 本の線に沿った複数回のサンプルで読むものです。16 倍の設定で足りるのは必要な倍率 `1 / sin(e)` が 16 以下になる仰角、つまり `e ≥ asin(1/16) = 3.58°` の範囲です。それより低い所は 16 倍でもぼやけます。

そこで、地平線に近い部分は雲を消します。消す幅の目安は必要な倍率が 16 を超える所、つまり仰角の sin が 1/16 ≈ 0.06 より小さい所です。HLSL では `dir.y`（視線の単位ベクトルの Y 成分で、sin(仰角) と同じ）に `smoothstep` を掛けます。

### 風による流れと精度 {#plane-scroll}

風で雲を流すには UV に「風の速さ × 時間」を足し引きします。ここに落とし穴が 2 つあります。

1 つ目は float の精度です。UV に直接「時間 × 風速 ÷ テクスチャの大きさ」を足し込むと時間が経つにつれて UV の値が大きくなり、float の刻みが粗くなります。風が 10 m/s でテクスチャが 2000 m 分なら 1 時間で UV は 18、10 時間で 180、100 時間で 1800 まで進みます。float で表せる隣の値との差はそれぞれ 0.002 テクセル、0.016 テクセル、0.125 テクセルです。100 時間遊ぶ人は多くありませんが、起動したままの展示端末では 10 時間は現実的です。`frac` で 0〜1 に折り返してから使えば、刻みは 1 付近の 6e-8 程度で済みます。ただし、`frac` の前の値が大きいとその手前の足し算で精度が落ちているので、時間そのものを周期で折り返す必要もあります。

2 つ目は折り返しの継ぎ目です。時間を `WrapTime` で折り返すと周期の境目で雲が飛びます。風で動いた距離がテクスチャの大きさの整数倍になる周期を選べば、継ぎ目は見えません。風速 `(8, 3)` m/s、テクスチャ 2000 m、周期 3600 s なら動く距離は 28800 m と 10800 m で、2000 m の 14.4 倍と 5.4 倍です。整数ではないので境目で飛びます。継ぎ目を消したいなら周期を「2000 m ÷ 風速」の整数倍にするか風速のほうを周期に合わせて丸めます（[Animation Tricks](../../water/waves/animation-tricks.md) の波の周期の丸めと同じ考え方です）。

### 疑似的な陰影 {#plane-shade}

雲の絵を貼っただけでは全部が同じ色で平板です。簡単な陰影として UV を太陽の方向に少しずらして、もう 1 回読む方法があります。ずらした先の濃さが今の位置より濃ければ、太陽の側に雲が続いているので、光が雲の中を長く通る分だけ暗くなります。薄ければ雲の縁にいるので明るくなります。

これは物理的な散乱の計算ではなく、「縁は明るく芯は暗い」という見た目を作る近似です。ずらす量（`gSunUvStep`）と強さ（`gShadeGain`）は見た目で調整する値で、コードの例の値は一例に過ぎません。

### 層の平面のコード {#plane-code}

ここからコードを数行ずつ見ます。最初は定数バッファとテクスチャです。

```hlsl
// ---- 安い雲（左手系・Y 上・+Z が前。リニア空間）。層の平面、疑似陰影、ビルボードの 3 本立て ----

cbuffer CloudCB : register(b0) {
  float3 gCameraPos;      // カメラの位置（m）。Y が高さ
  float  gTime;           // 経過時間（秒）。float のまま増やし続けない（下の WrapTime を参照）
  float3 gSunDir;         // 太陽へ向かう単位ベクトル（ワールド）
  float  gCloudMeters;    // テクスチャ 1 枚が覆う長さ（m）。例: 2000
  float2 gWind;           // 風の速さ（m/s）。x, z 成分。例: (8, 3)
  float  gSunUvStep;      // 疑似陰影で太陽側へずらす UV の量。例: 0.02
  float  gShadeGain;      // 疑似陰影の強さ。例: 3
  float3 gSkyColor;       // 層の後ろに見える空の色（リニア）
  float  gFogStart;       // 地平線に向けて雲を消し始める仰角の sin。例: 0.12
  float3 gLitColor;       // 日向側の雲の色（リニア）
  float  gFogEnd;         // 完全に消える仰角の sin。例: 0.02
  float3 gShadowColor;    // 日陰側の雲の色（リニア）
  float  gPad;            // 16 バイト境界にそろえる詰め物
};

Texture2D<float4> gCloudTex : register(t0);   // 雲の絵。a が濃さ
SamplerState gAniso : register(s0);           // 異方性フィルタ（Wrap, MaxAnisotropy = 16）
```

`gCloudMeters` は雲の絵 1 枚が実際に覆う長さ（m）です。この値と絵に描かれた雲の大きさで、雲が空でどれくらいの大きさに見えるかが決まります。`gFogStart` と `gFogEnd` は地平線で消し始める仰角の sin です。角度ではなく sin を使うのは、`dir.y` がそのまま sin(仰角) だからで、`asin` を呼ばずに済みます。

続く `WrapTime` と `PlaneUv` が本体です。

```hlsl
// 時間を 1 周期で折り返す（足した）。float の時間は大きくなるほど刻みが粗くなり、スクロールが階段になる。
float WrapTime(float t, float period) {
  return t - floor(t / period) * period;      // 0〜period に収める
}

// 視線 dir が、カメラの上 layer_height（m）の水平な平面に当たる点の UV を返す。
// 戻り値の z は、カメラからその点までの水平距離（m）。地平線付近の消し込みに使う。
float3 PlaneUv(float3 dir, float layer_height) {
  float rise = layer_height - gCameraPos.y;   // 層がカメラよりどれだけ上か（m）
  float t = rise / dir.y;                     // 視線を何倍に伸ばせば層に届くか（dir は単位ベクトル）
  float2 hit = gCameraPos.xz + dir.xz * t;    // 当たった点の水平位置（m）
  float2 wind = gWind * WrapTime(gTime, 3600.0);   // 風で流れた距離（m）。1 時間で折り返す
  float2 uv = (hit - wind) / gCloudMeters;    // m を UV に直す。風と逆向きに引くと、絵が風下へ動く
  uv = frac(uv);                              // 0〜1 に折り返してから渡す。大きな値のまま渡すと精度が落ちる
  return float3(uv, length(dir.xz * t));      // 水平距離 = |dir.xz| * t
}
```

`WrapTime` は時間を周期の中に収めます。これは足した処理です。`PlaneUv` は先に導いた `t = 高さの差 / d.y` で当たる点を求めそこから風で動いた距離を引きます。風で動いた分を位置から引くことで、雲の絵が風下に流れます（逆に足すと風上へ流れます）。UV はメートルをテクスチャの大きさで割って作り `frac` で折り返します。戻り値の `z` に水平距離を入れておくのは、距離による消し込みに使えるようにするためです。このページのコードでは `x`/`y` しか使っていません。

次は 1 層分を読む関数です。

```hlsl
// 疑似陰影つきの 1 層を読む。rgb が色、a が濃さ。
float4 SampleLayer(float3 dir, float layer_height) {
  float3 p = PlaneUv(dir, layer_height);      // 当たった点の UV と距離
  float2 uv = p.xy;                           // UV
  float density = gCloudTex.Sample(gAniso, uv).a;   // その場所の雲の濃さ
  // 太陽側へ UV をずらして、もう 1 回読む。太陽側に雲が続くほど、光が雲の中を長く通るので暗い。
  float2 sun_uv = normalize(gSunDir.xz + 1e-5) * gSunUvStep;   // 太陽の水平方向を UV 方向に使う（足した: 1e-5 は真上の太陽でのゼロ除算よけ）
  float toward_sun = gCloudTex.Sample(gAniso, uv + sun_uv).a;  // 太陽側の濃さ
  float shade = saturate(1.0 - (toward_sun - density) * gShadeGain);   // 1: 日向、0: 日陰
  float3 color = lerp(gShadowColor, gLitColor, shade);         // 日陰色と日向色の補間
  // 地平線に近い（仰角の sin が小さい）ほど薄くする。平面が遠くで 1 テクセルを縮めるので、そこは消す。
  float fade = smoothstep(gFogEnd, gFogStart, dir.y);          // 0: 消える、1: そのまま
  return float4(color, density * fade);       // a に消し込みを掛ける
}
```

濃さを 2 回読んでいます。1 回目は今の位置、2 回目は太陽の水平方向に `gSunUvStep` だけずらした位置です。`normalize(gSunDir.xz + 1e-5)` の `1e-5` は太陽が真上でゼロベクトルになるのを避けるために足しました。`shade` は太陽側のほうが濃いほど小さくなり小さいほど日陰色に寄ります。最後に `smoothstep(gFogEnd, gFogStart, dir.y)` で地平線に近づくほどアルファを 0 に近づけます。

## 方法 2：層を重ねて視差を出す {#layers}

1 枚の平面はカメラが動いても雲どうしの位置関係が変わりません。高さの違う層を 2〜3 枚重ねると、カメラの移動で手前の層が速くずれ奥の層はゆっくりずれます。これが視差で奥行きを感じさせる手がかりになります。

### 視差の大きさ {#layers-parallax}

カメラが横に `c` メートル動いたとき距離 `r` にある点の見える方向は、約 `c / r` ラジアン変わります。層の点までの距離は `r = 層の高さ / sin(仰角)` なので、高い層ほど `r` が大きくずれが小さくなります。縦の画角 60°、縦 1080 画素（1 度が 18 画素）で数えた結果は、次のとおりです。

- 高さ 1000 m の層: 仰角 45° で 73 画素、20° で 35 画素
- 高さ 1500 m の層: 仰角 45° で 49 画素、20° で 24 画素
- 高さ 2200 m の層: 仰角 45° で 33 画素、20° で 16 画素

同じ視線でも 1000 m の層と 2200 m の層でずれが 2 倍以上違います。この違いが奥行きとして読み取れます。層の高さは比が 1 : 1.5 : 2.2 くらいに離すとはっきり視差が出ます。近すぎると 1 枚の厚い雲にしか見えず離しすぎると層がばらばらに見えます。

### コード {#layers-code}

`SampleLayer` を高さを変えて 3 回呼べば、重ねられます。

```hlsl
// 3 層を奥から重ねる。高さが違うほど、カメラが動いたときの視差が違う。
float4 ShadeSkyPS(float4 pos : SV_Position, float3 view_dir : TEXCOORD0) : SV_Target {
  float3 dir = normalize(view_dir);           // 視線（補間で長さが崩れるので正規化する）
  if (dir.y <= 0.0) return float4(gSkyColor, 1.0);   // 足した: 地平線より下には層がない
  float3 color = gSkyColor;                   // 一番奥は空の色
  float4 c2 = SampleLayer(dir, 2200.0);       // 高い層（遠い）
  float4 c1 = SampleLayer(dir, 1500.0);       // 中間の層
  float4 c0 = SampleLayer(dir, 1000.0);       // 低い層（近い）
  color = lerp(color, c2.rgb, c2.a);          // 奥から手前へ、アルファ ブレンド
  color = lerp(color, c1.rgb, c1.a);          // 中
  color = lerp(color, c0.rgb, c0.a);          // 手前
  return float4(color, 1.0);                  // 空は不透明
}
```

奥の層から順に `lerp` で重ねるのは、アルファブレンドの順序と同じです。手前の層の濃さが 1 なら奥は完全に隠れます。`dir.y <= 0` は足した処理で地平線より下の視線は層に届かない（`t` が負になる）ので、空の色をそのまま返します。

層ごとに風の速さを変えるとさらに奥行きが出ます。このコードでは省きましたが `PlaneUv` に層ごとの風を渡す変更で足せます。

### 層の数とコスト {#layers-cost}

1 層に 2 回のテクスチャ読み込みなので、3 層で 6 回です。全画面で毎フレーム読むと負荷は空が占める面積に比例します。地面や建物で隠れる画素まで計算しないよう深度が far の画素だけに描くのが基本です。

## 方法 3：ビルボード {#billboard}

空に点在する積雲を数十個だけ置きたいときは、1 つの雲を 1 枚の板にして、カメラの方を向かせます。板に貼る絵はアルファつきの雲の画像で、ライティング済みです。

### 見える大きさ {#billboard-size}

幅 500 m の雲が占める角度は距離 `D` で `2 × atan(250 / D)` です。縦の画角 60°、縦 1080 画素で数えると、次のようになります。

- 距離 2 km: 14.25° で 257 画素
- 距離 5 km: 5.72° で 103 画素
- 距離 10 km: 2.86° で 52 画素
- 距離 20 km: 1.43° で 26 画素

2 km では 257 画素の雲が見えるので、絵は 256×256 以上が欲しくなります。10 km なら 52 画素なので、64×64 で足ります。ミップマップを使えば遠くの雲の読み込みは自然に小さくなります。

### 頂点シェーダーで板を作る {#billboard-code}

板の頂点は中心の位置からカメラの右と上の方向に半幅と半高だけ動かして作ります。

```hlsl
// ---- ビルボード（インポスター）: 中心を向く板を、頂点シェーダーで作る ----

cbuffer BillboardCB : register(b1) {
  float4x4 gViewProj;     // ビュー × 射影（行ベクトル。v * M）
  float3 gCamRight;       // カメラの右（ワールド）
  float  gHalfWidth;      // 板の半分の幅（m）。例: 250
  float3 gCamUp;          // カメラの上（ワールド）
  float  gHalfHeight;     // 板の半分の高さ（m）。例: 150
  uint   gGrid;           // インポスターの一辺の視点数 N（N x N 枚が 1 枚の絵に並ぶ）
  float3 gPad1;           // 詰め物
};

struct BillboardVSOut {
  float4 pos : SV_Position;     // クリップ空間の位置
  float2 uv  : TEXCOORD0;       // 板の中の UV（0〜1）
  nointerpolation uint frame : TEXCOORD1;  // どの視点の絵を使うか（板の中で変わらない）
};

// 視線から、焼いた視点の番号を選ぶ。方位角を N 等分、仰角を N 等分に量子化する（足した: 割り当ては一例）。
uint PickFrame(float3 to_cloud_dir) {
  float azimuth = atan2(to_cloud_dir.x, to_cloud_dir.z);     // 方位角 -π〜π
  float elevation = asin(clamp(to_cloud_dir.y, -1.0, 1.0));  // 仰角 -π/2〜π/2
  uint ix = (uint)floor((azimuth / 6.2831853 + 0.5) * gGrid) % gGrid;          // 方位の番号（0〜N-1）
  uint iy = min((uint)floor((elevation / 3.1415927 + 0.5) * gGrid), gGrid - 1); // 仰角の番号
  return iy * gGrid + ix;                                    // 行優先の通し番号
}

BillboardVSOut BillboardVS(float3 center : POSITION, float2 corner : TEXCOORD0, uint vid : SV_VertexID) {
  BillboardVSOut o;                                          // 出力
  float2 c = corner * 2.0 - 1.0;                             // 0〜1 を -1〜+1 にする（板の四隅）
  float3 world = center + gCamRight * (c.x * gHalfWidth)     // 右へ半幅
                        + gCamUp    * (c.y * gHalfHeight);   // 上へ半高
  o.pos = mul(float4(world, 1.0), gViewProj);                // 行ベクトルの掛け順
  o.uv = float2(corner.x, 1.0 - corner.y);                   // UV は下向きが +v
  o.frame = PickFrame(normalize(gCameraPos - center));       // 雲からカメラへの向きで視点を選ぶ
  return o;
}
```

`gCamRight` と `gCamUp` はビュー行列から取ります（左手系・行ベクトルなので、ビュー行列の 0 列目と 1 列目が、ワールドから見たカメラの右と上です）。板が常にカメラを向くのはこの 2 方向だけで広げているからです。`PickFrame` は後述するインポスターの視点を選ぶ関数で、板だけを使うときは不要です。

### 並べ方と描画順 {#billboard-order}

板は半透明なので奥から手前の順に並べる必要があります（[Sorting](../../translucency/blending-sorting/sorting.md)）。数十枚なら CPU で距離を並べ替えるだけで済みます。板どうしが重なる所はアルファが二重にかかって濃くなるので、絵の縁は十分に薄くしておきます。

### 近づくと板だと分かる理由 {#billboard-limit}

カメラが雲に近づくと板の平らさが見えます。理由は 2 つあります。1 つはカメラを横に動かしても板が常にこちらを向くので、雲の側面が見えないことです。もう 1 つは地面や他の物体に板が突き刺さる所で、交差の線が出ることです。後者は板のアルファを深度の差で薄める「ソフトパーティクル」と同じ方法で和らげます。

## 方法 4：インポスター {#impostor}

ボリューム雲を事前にレンダリングして、複数の方向から見た絵として焼いておきカメラの向きに近い絵を板に貼る方法です。同じ発想は木の遠景にも使われます（[Trees](../../terrain/vegetation/trees.md)）。1 つの雲に対して見る角度で絵が切り替わるので、板だけの場合より立体感が出ます。

### 容量の見積もり {#impostor-memory}

1 方向の絵が 256×256 で、一辺の視点の数が `N` の `N×N` 枚を並べたとき非圧縮の RGBA8 とブロック圧縮（BC3 / BC7、1 テクセル 1 バイト）の容量は次のとおりです。

- 4×4 枚: 非圧縮 4.0 MB、圧縮 1.0 MB
- 8×8 枚: 非圧縮 16.0 MB、圧縮 4.0 MB
- 16×16 枚: 非圧縮 64.0 MB、圧縮 16.0 MB

雲の種類を 5 つ用意して 8×8 枚にすると、圧縮しても 20 MB です。モバイルの予算ではこれが限度になるので、視点の数を減らす（4×4 にする）か解像度を下げます。

### 視点の切り替えと補間 {#impostor-blend}

上の `PickFrame` は方位角と仰角を `N` 等分して、一番近い視点を 1 つだけ選びます。この方式ではカメラが動いて視点の境目を越えるたびに絵が一瞬で切り替わる「ポップ」が出ます。目立たなくする方法は 2 つあります。1 つは隣り合う視点の絵を距離に応じて混ぜて読む方法です（サンプルが 2 回から 4 回になります）。もう 1 つは視点を増やして、1 回あたりの変化を小さくする方法です。このページのコードはどちらもしていません。

また、次の `BillboardPS` では枠の境目で隣の絵を拾わないように半テクセル内側へ寄せる処理を省いています。ブロック圧縮とミップマップを使うと境目に隣の絵が混ざって縁に線が出ることがあります。絵と絵の間に余白を空けるか UV を内側に寄せて対処してください。

```hlsl
Texture2D<float4> gImpostor : register(t1);                  // N x N 枚を並べた 1 枚の絵

float4 BillboardPS(BillboardVSOut i) : SV_Target {
  float2 cell = float2(i.frame % gGrid, i.frame / gGrid);    // 絵の中の位置（列, 行）
  float2 uv = (cell + i.uv) / gGrid;                         // 全体の UV にする
  // 枠の境界で隣の絵を拾わないよう、半テクセル内側に寄せたいが、ここでは省く（足りない所は本文で述べる）。
  return gImpostor.Sample(gAniso, uv);                       // 焼いた絵そのもの（アルファつき）
}
```

`frame` は頂点シェーダーが決めた通し番号で、`%` と `/` で絵の中の列と行に戻します。`(cell + uv) / gGrid` で全体の絵の中の UV になります。

## ハイブリッド：近くはボリューム、遠くは安く {#hybrid}

近くだけをボリュームにして遠くを安い方法にするのが現実的な使い方です。ボリュームのレイマーチは視線が雲の殻を通る距離が長い（地平線に近い）ほど重くなります。遠景を層やビルボードに替えると、重い所を避けられます。

境目はアルファのフェードでつなぎます。近い側のボリュームを境の距離に向けて徐々に薄くし、同じ位置から遠い側の平面を徐々に濃くすると、切り替えが目立ちません。ここで挙げた距離（2 km、10 km）は見た目と予算で決める一例で、根拠のある定数ではありません。

## よくあるミス {#mistakes}

??? failure "地平線に近い所の雲が縦にぼやける"
    原因は平面に貼ったテクスチャが地平線の近くで縦に強く潰れる（仰角 5° で 11.5 倍）のに、異方性フィルタが効いていないことです。サンプラーの `Filter` を `D3D11_FILTER_ANISOTROPIC` にして `MaxAnisotropy` を 16 にします。それでも仰角 3.6° より低い所はぼやけるので、`smoothstep` で雲を消します。

??? failure "雲の流れが、数時間後にガタガタになる"
    原因は時間と風速の積を float のまま UV に足し続けて精度が落ちることです。10 時間で UV が 180 に達し、刻みが 1/64 テクセルほどになります。時間を周期で折り返し UV も `frac` で折り返してから使います。

??? failure "周期の継ぎ目で雲がジャンプする"
    原因は時間を折り返す周期で雲が動く距離が、テクスチャの大きさの整数倍になっていないことです。周期を `テクスチャの大きさ ÷ 風速` の整数倍にします。

??? failure "近づくとビルボードが突き刺さって見える"
    原因は板が地面や建物と交差する所で、アルファがいきなり切れることです。板のアルファに深度の差で 0〜1 に変わる係数を掛けます（ソフトパーティクルと同じ方法）。

??? failure "インポスターの視点が変わる瞬間に絵がパッと変わる"
    原因は視点を 1 つだけ選んでいることです。隣り合う 2 つの視点を混ぜるか視点の数を増やします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 平面への投影は `t = (高さの差) / d.y` で、地平線で発散する。仰角 5° で縦が 1/11.5 に潰れる
    - [x] 16 倍の異方性は仰角 3.6° まで。それより低い所は雲を消す
    - [x] 視差は層の高さの差で決まる。比 1 : 1.5 : 2.2 くらいに離す
    - [x] float の時間は周期で折り返し、UV は `frac` で折り返してから渡す
    - [x] ビルボードは遠景用。幅 500 m の雲は 10 km で 52 画素
    - [x] インポスターは視点の数 N×N に比例して容量が増える（8×8 圧縮で 4 MB）

## C++ で数えたもの {#numbers}

このページの数字を出した C++ です。

```cpp
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

int main() {
  // 1. 高さ h の平面に雲を貼ったときの、仰角ごとの歪み。
  //    視線の仰角 e の方向は、平面の (水平距離 h / tan e) の点に当たる。
  //    平面上の 1 テクセル（大きさ s）が、画面でどれだけの角度を占めるか:
  //      放射方向（地平線に向かう向き）: s * sin(e)^2 / h
  //      接線方向（地平線に沿う向き）:   s * sin(e) / h
  //    比（放射 / 接線）= sin(e)。この逆数が、必要な異方性フィルタの倍率になる。
  std::printf("-- sky plane: elevation e, distance to the plane point (h = 1500 m), aspect, aniso needed\n");
  const double h = 1500.0;                           // 雲の層の高さ（m）。カメラの上の高さ
  for (double e_deg : {90.0, 45.0, 20.0, 10.0, 5.0, 3.0, 2.0, 1.0}) {
    const double e = e_deg / kDeg;                   // 仰角（ラジアン）
    const double ground = h / std::tan(e);           // 平面上の水平距離（m）
    const double ratio = std::sin(e);                // 放射 / 接線の比
    std::printf("e=%4.0f deg: horizontal distance = %9.0f m, radial/tangential = %.3f, aniso needed = %6.1f\n", e_deg,
                ground, ratio, 1.0 / ratio);
  }
  // 16 倍の異方性フィルタで足りる最小の仰角。
  std::printf("16x aniso covers e >= %.2f deg\n", std::asin(1.0 / 16.0) * kDeg);

  // 2. UV のスクロールを float で持ったときの精度。風 10 m/s、1 テクスチャ 2000 m、1024 テクセル。
  std::printf("-- scroll precision (wind 10 m/s, texture covers 2000 m, 1024 texels)\n");
  for (double hours : {1.0, 10.0, 100.0}) {
    const double uv = 10.0 * hours * 3600.0 / 2000.0;                  // 動いた UV 量（周回数）
    const float u = static_cast<float>(uv);                            // float に入れた値
    const double step = std::nextafter(u, 1e30f) - static_cast<double>(u);   // 次に表せる値との差
    std::printf("%5.0f h: uv = %8.0f, float step = %.6f uv = %.3f texel\n", hours, uv, step, step * 1024.0);
  }
  // fract で 0〜1 に折り返してから渡せば、刻みは 1 付近の 2^-24 程度になる。
  std::printf("fract(uv) step near 1.0 = %.9f uv\n", std::nextafter(1.0f, 0.0f) - std::nextafter(std::nextafter(1.0f, 0.0f), 0.0f));

  // 3. 視差。カメラが c m 動いたとき、高さ h の層の点が見える角度のずれ。
  //    点までの距離 r = h / sin(e)。横方向の移動 c が視線と垂直に近いとき、ずれは c / r ラジアン。
  std::printf("-- parallax: camera moves 100 m, 1080p, vertical fov 60 deg\n");
  const double px_per_deg = 1080.0 / 60.0;           // 1 度が何画素か（画面中央付近の近似）
  for (double layer_h : {1000.0, 1500.0, 2200.0}) {
    for (double e_deg : {45.0, 20.0}) {
      const double r = layer_h / std::sin(e_deg / kDeg);               // 層の点までの距離（m）
      const double shift = 100.0 / r * kDeg;                           // 角度のずれ（度）
      std::printf("layer h=%4.0f e=%2.0f deg: r = %6.0f m, shift = %.2f deg = %.0f px\n", layer_h, e_deg, r, shift,
                  shift * px_per_deg);
    }
  }

  // 4. ビルボードの大きさと、必要なテクスチャの大きさ。
  std::printf("-- billboard: cloud width 500 m\n");
  for (double dist : {2000.0, 5000.0, 10000.0, 20000.0}) {
    const double ang = 2.0 * std::atan(250.0 / dist) * kDeg;           // 雲が占める角度（度）
    std::printf("distance %6.0f m: angular size = %5.2f deg = %5.0f px\n", dist, ang, ang * px_per_deg);
  }

  // 5. インポスター（複数の角度から焼いた画像）の容量。1 方向 256x256、RGBA8 と BC3 / BC7。
  std::printf("-- impostor memory (256x256 per view)\n");
  for (int n : {4, 8, 16}) {                         // 一辺の視点の数（n x n のグリッド）
    const double views = static_cast<double>(n) * n;
    const double raw = views * 256.0 * 256.0 * 4.0 / (1024.0 * 1024.0);     // 非圧縮（MB）
    const double bc = views * 256.0 * 256.0 * 1.0 / (1024.0 * 1024.0);      // BC3 / BC7（1 バイト / テクセル）（MB）
    std::printf("%2d x %2d views: raw = %5.1f MB, block-compressed = %5.1f MB\n", n, n, raw, bc);
  }
}
```

```text title="実行結果"
-- sky plane: elevation e, distance to the plane point (h = 1500 m), aspect, aniso needed
e=  90 deg: horizontal distance =         0 m, radial/tangential = 1.000, aniso needed =    1.0
e=  45 deg: horizontal distance =      1500 m, radial/tangential = 0.707, aniso needed =    1.4
e=  20 deg: horizontal distance =      4121 m, radial/tangential = 0.342, aniso needed =    2.9
e=  10 deg: horizontal distance =      8507 m, radial/tangential = 0.174, aniso needed =    5.8
e=   5 deg: horizontal distance =     17145 m, radial/tangential = 0.087, aniso needed =   11.5
e=   3 deg: horizontal distance =     28622 m, radial/tangential = 0.052, aniso needed =   19.1
e=   2 deg: horizontal distance =     42954 m, radial/tangential = 0.035, aniso needed =   28.7
e=   1 deg: horizontal distance =     85935 m, radial/tangential = 0.017, aniso needed =   57.3
16x aniso covers e >= 3.58 deg
-- scroll precision (wind 10 m/s, texture covers 2000 m, 1024 texels)
    1 h: uv =       18, float step = 0.000002 uv = 0.002 texel
   10 h: uv =      180, float step = 0.000015 uv = 0.016 texel
  100 h: uv =     1800, float step = 0.000122 uv = 0.125 texel
fract(uv) step near 1.0 = 0.000000060 uv
-- parallax: camera moves 100 m, 1080p, vertical fov 60 deg
layer h=1000 e=45 deg: r =   1414 m, shift = 4.05 deg = 73 px
layer h=1000 e=20 deg: r =   2924 m, shift = 1.96 deg = 35 px
layer h=1500 e=45 deg: r =   2121 m, shift = 2.70 deg = 49 px
layer h=1500 e=20 deg: r =   4386 m, shift = 1.31 deg = 24 px
layer h=2200 e=45 deg: r =   3111 m, shift = 1.84 deg = 33 px
layer h=2200 e=20 deg: r =   6432 m, shift = 0.89 deg = 16 px
-- billboard: cloud width 500 m
distance   2000 m: angular size = 14.25 deg =   257 px
distance   5000 m: angular size =  5.72 deg =   103 px
distance  10000 m: angular size =  2.86 deg =    52 px
distance  20000 m: angular size =  1.43 deg =    26 px
-- impostor memory (256x256 per view)
 4 x  4 views: raw =   4.0 MB, block-compressed =   1.0 MB
 8 x  8 views: raw =  16.0 MB, block-compressed =   4.0 MB
16 x 16 views: raw =  64.0 MB, block-compressed =  16.0 MB
```

## 参考資料 {#references}

このページの式と数字は幾何から導いて C++ で確かめたもので、以下の資料の中身は**今回は読んでいません**。そのため、これらの資料の内容として書いた箇所はありません。

- Andrew Schneider, Nathan Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（ボリューム雲。このページが置き換える側の資料）
- Sébastien Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ {#related}

- [Clouds](index.md)
- [Cloud Raymarching](raymarch.md)
- [Gradient Sky](../sky-models/gradient.md)
