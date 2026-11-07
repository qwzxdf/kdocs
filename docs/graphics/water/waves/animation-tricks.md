---
title: Wave Animation Tricks
tags:
  - 描画
---

# Wave Animation Tricks

波を動かすいちばん簡単な方法は sin の中の時間を毎フレーム増やすことです。ところが、そのまま動かすと 4 つの問題が出ます。すべての波が同じ速さで滑るので、機械的に見え同じ形が繰り返されて見え遠くで細かい波がちらつき、何時間も遊ぶと時間の値が大きくなって動きがカクつきます。このページではこの 4 つを数字で確かめながら直していきます。最後に、風の強さから波の大きさを決める式を載せます。

旧版のこのページには数字の誤りがいくつかありました。float の時間の刻み最も強い波の波長、風速ごとの波高の表です。このページでは数え直した値に置き換えてあります。どの値を直したかは各節に書きました。

!!! tip "ポイント"
    - 水の波は長い波ほど速く進みます（分散）。この関係を使うと波の模様が時間とともに変わり続けて、海らしくなります。
    - 浅い水では速さが水深で決まります。岸に近づくと周期は同じまま波長が縮んで波が切り立ちます。
    - 遠くの波は 1 波長が数画素より細かくなるとちらつきます。波長ごとに見える距離を決めて、振幅を連続的に 0 へ近づけます。
    - `float` の経過時間は 100 時間で 31 ミリ秒の刻みになります。周期で折り返すと精度が保てます。

!!! info "このページを読む前に"
    - [Water Waves](index.md)（このセクションの地図）
    - [Summing Sine Waves](sine-waves.md)（サイン波を足し合わせる基本。このページはその改良）

## 分散関係：長い波ほど速い {#dispersion}

水の波は波長によって進む速さが違います。長いうねりは速く短いさざ波は遅く進みます。これを分散といい波の模様が時間とともに崩れて変わり続ける原因になります。

水深 `d` の水の重力で動く波には次の関係があります（線形波動論）。

```text
ω² = g · k · tanh(k · d)        ω: 角周波数（rad/s）、k: 波数（2π / λ）、d: 水深
c  = ω / k                       位相速度（山が進む速さ）
```

深い水（`d > λ/2`）では `tanh` が 1 になるので `ω² = g·k` で、速さは `c = √(g·λ / 2π)` です。波長が 100 m なら約 12.5 m/s、1 m なら約 1.25 m/s で、波長が 100 倍になると速さは 10 倍になります。浅い水（`d < λ/20`）では `tanh(kd)` が `kd` に近づくので `c = √(g·d)` となり波長によらず水深だけで決まります。この境目の値は Wikipedia の Dispersion (water waves) の記事に載っているもので、す。

| 水深と波長 | `tanh(kd)` | 速さ c | 呼び方 |
| --- | --- | --- | --- |
| `d > λ/2` | 約 1 | `√(g·λ / 2π)` | 深水波 |
| `d < λ/20` | 約 `kd` | `√(g·d)` | 浅水波 |
| その間 | 1 と `kd` の間 | 元の式で計算 | 中間 |

群速度（波のエネルギーが進む速さ）は、深い水では位相速度のちょうど半分、浅い水では位相速度と同じになります。船の航跡の角度が 19.47° になる導出で使った関係です（[Wakes and Collisions](../shore-foam/wake.md)）。

### 全部の波を同じ速さにすると {#dispersion-same}

分散関係を使わずに全部の波を同じ速さで進ませると、波の形が変わらないまま滑るだけです。分散関係を使えば長い波が短い波を追い越していき山と谷の重なり方が毎フレーム変わります。同じ形が現れない（ように見える）ことが、海の不規則さの正体です。

### 水深と速さを数える {#dispersion-depth}

波長 50 m の波で水深を変えたときの位相速度を数えます。全行の数字は後に載せる C++ の出力から取りました。

- 水深 50 m と 25 m では、速さは 8.84 m/s と 8.82 m/s で、深い水の値（8.84 m/s）とほとんど同じです。
- 水深 10 m では 8.15 m/s と少し遅くなります。浅い水の式 `√(g·d)` は 9.90 m/s で、まだ合いません。`d = λ/5` は深い水とも浅い水とも言えない中間にあたります。
- 水深 5 m では 6.59 m/s で、浅い水の式（7.00 m/s）に近づきます。
- 水深 2 m では 4.38 m/s で、浅い水の式（4.43 m/s）とほぼ一致します。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="水深と波の速さ"><defs><marker id="a1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">水深と位相速度（波長 50 m）</text><line x1="70" y1="250" x2="610" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="72.7,220.3 75.4,207.9 78.1,198.5 80.8,190.6 83.5,183.7 86.2,177.5 88.9,171.9 91.6,166.7 94.3,161.9 97.0,157.4 99.7,153.2 102.4,149.3 105.1,145.6 107.8,142.1 110.5,138.7 113.2,135.6 115.9,132.7 118.6,129.9 121.3,127.2 124.0,124.7 126.7,122.4 129.4,120.1 132.1,118.0 134.8,116.0 137.5,114.1 140.2,112.2 142.9,110.5 145.6,108.9 148.3,107.4 151.0,105.9 153.7,104.6 156.4,103.3 159.1,102.1 161.8,100.9 164.5,99.8 167.2,98.8 169.9,97.8 172.6,96.9 175.3,96.0 178.0,95.2 180.7,94.4 183.4,93.7 186.1,93.0 188.8,92.4 191.5,91.8 194.2,91.2 196.9,90.7 199.6,90.2 202.3,89.7 205.0,89.2 207.7,88.8 210.4,88.4 213.1,88.0 215.8,87.7 218.5,87.3 221.2,87.0 223.9,86.7 226.6,86.5 229.3,86.2 232.0,86.0 234.7,85.7 237.4,85.5 240.1,85.3 242.8,85.1 245.5,84.9 248.2,84.8 250.9,84.6 253.6,84.5 256.3,84.3 259.0,84.2 261.7,84.1 264.4,83.9 267.1,83.8 269.8,83.7 272.5,83.6 275.2,83.5 277.9,83.5 280.6,83.4 283.3,83.3 286.0,83.2 288.7,83.2 291.4,83.1 294.1,83.0 296.8,83.0 299.5,82.9 302.2,82.9 304.9,82.8 307.6,82.8 310.3,82.8 313.0,82.7 315.7,82.7 318.4,82.6 321.1,82.6 323.8,82.6 326.5,82.6 329.2,82.5 331.9,82.5 334.6,82.5 337.3,82.5 340.0,82.4 342.7,82.4 345.4,82.4 348.1,82.4 350.8,82.4 353.5,82.4 356.2,82.3 358.9,82.3 361.6,82.3 364.3,82.3 367.0,82.3 369.7,82.3 372.4,82.3 375.1,82.3 377.8,82.3 380.5,82.2 383.2,82.2 385.9,82.2 388.6,82.2 391.3,82.2 394.0,82.2 396.7,82.2 399.4,82.2 402.1,82.2 404.8,82.2 407.5,82.2 410.2,82.2 412.9,82.2 415.6,82.2 418.3,82.2 421.0,82.2 423.7,82.2 426.4,82.2 429.1,82.2 431.8,82.2 434.5,82.2 437.2,82.2 439.9,82.2 442.6,82.2 445.3,82.2 448.0,82.2 450.7,82.1 453.4,82.1 456.1,82.1 458.8,82.1 461.5,82.1 464.2,82.1 466.9,82.1 469.6,82.1 472.3,82.1 475.0,82.1 477.7,82.1 480.4,82.1 483.1,82.1 485.8,82.1 488.5,82.1 491.2,82.1 493.9,82.1 496.6,82.1 499.3,82.1 502.0,82.1 504.7,82.1 507.4,82.1 510.1,82.1 512.8,82.1 515.5,82.1 518.2,82.1 520.9,82.1 523.6,82.1 526.3,82.1 529.0,82.1 531.7,82.1 534.4,82.1 537.1,82.1 539.8,82.1 542.5,82.1 545.2,82.1 547.9,82.1 550.6,82.1 553.3,82.1 556.0,82.1 558.7,82.1 561.4,82.1 564.1,82.1 566.8,82.1 569.5,82.1 572.2,82.1 574.9,82.1 577.6,82.1 580.3,82.1 583.0,82.1 585.7,82.1 588.4,82.1 591.1,82.1 593.8,82.1 596.5,82.1 599.2,82.1 601.9,82.1 604.6,82.1 607.3,82.1 610.0,82.1"/><polyline fill="none" stroke="#e5aa28" stroke-width="2" stroke-dasharray="6 4" points="72.7,220.2 75.4,207.9 78.1,198.5 80.8,190.5 83.5,183.5 86.2,177.1 88.9,171.3 91.6,165.8 94.3,160.7 97.0,155.9 99.7,151.3 102.4,146.9 105.1,142.7 107.8,138.7 110.5,134.8 113.2,131.0 115.9,127.3 118.6,123.8 121.3,120.3 124.0,116.9 126.7,113.6 129.4,110.4 132.1,107.3 134.8,104.2 137.5,101.2 140.2,98.3 142.9,95.4 145.6,92.6 148.3,89.8 151.0,87.0 153.7,84.3 156.4,81.7 159.1,79.1 161.8,76.5 164.5,74.0 167.2,71.5 169.9,69.0 172.6,66.6 175.3,64.2 178.0,61.8 180.7,60.0 183.4,60.0 186.1,60.0 188.8,60.0 191.5,60.0 194.2,60.0 196.9,60.0 199.6,60.0 202.3,60.0 205.0,60.0 207.7,60.0 210.4,60.0 213.1,60.0 215.8,60.0 218.5,60.0 221.2,60.0 223.9,60.0 226.6,60.0 229.3,60.0 232.0,60.0 234.7,60.0 237.4,60.0 240.1,60.0 242.8,60.0 245.5,60.0 248.2,60.0 250.9,60.0 253.6,60.0 256.3,60.0 259.0,60.0 261.7,60.0 264.4,60.0 267.1,60.0 269.8,60.0 272.5,60.0 275.2,60.0 277.9,60.0 280.6,60.0 283.3,60.0 286.0,60.0 288.7,60.0 291.4,60.0 294.1,60.0 296.8,60.0 299.5,60.0 302.2,60.0 304.9,60.0 307.6,60.0 310.3,60.0 313.0,60.0 315.7,60.0 318.4,60.0 321.1,60.0 323.8,60.0 326.5,60.0 329.2,60.0 331.9,60.0 334.6,60.0 337.3,60.0 340.0,60.0 342.7,60.0 345.4,60.0 348.1,60.0 350.8,60.0 353.5,60.0 356.2,60.0 358.9,60.0 361.6,60.0 364.3,60.0 367.0,60.0 369.7,60.0 372.4,60.0 375.1,60.0 377.8,60.0 380.5,60.0 383.2,60.0 385.9,60.0 388.6,60.0 391.3,60.0 394.0,60.0 396.7,60.0 399.4,60.0 402.1,60.0 404.8,60.0 407.5,60.0 410.2,60.0 412.9,60.0 415.6,60.0 418.3,60.0 421.0,60.0 423.7,60.0 426.4,60.0 429.1,60.0 431.8,60.0 434.5,60.0 437.2,60.0 439.9,60.0 442.6,60.0 445.3,60.0 448.0,60.0 450.7,60.0 453.4,60.0 456.1,60.0 458.8,60.0 461.5,60.0 464.2,60.0 466.9,60.0 469.6,60.0 472.3,60.0 475.0,60.0 477.7,60.0 480.4,60.0 483.1,60.0 485.8,60.0 488.5,60.0 491.2,60.0 493.9,60.0 496.6,60.0 499.3,60.0 502.0,60.0 504.7,60.0 507.4,60.0 510.1,60.0 512.8,60.0 515.5,60.0 518.2,60.0 520.9,60.0 523.6,60.0 526.3,60.0 529.0,60.0 531.7,60.0 534.4,60.0 537.1,60.0 539.8,60.0 542.5,60.0 545.2,60.0 547.9,60.0 550.6,60.0 553.3,60.0 556.0,60.0 558.7,60.0 561.4,60.0 564.1,60.0 566.8,60.0 569.5,60.0 572.2,60.0 574.9,60.0 577.6,60.0 580.3,60.0 583.0,60.0 585.7,60.0 588.4,60.0 591.1,60.0 593.8,60.0 596.5,60.0 599.2,60.0 601.9,60.0 604.6,60.0 607.3,60.0 610.0,60.0"/><line x1="70" y1="82.1261028308646" x2="610" y2="82.1261028308646" stroke="#94a3b8" stroke-dasharray="4 4"/><text x="604" y="76.1261028308646" text-anchor="end" style="font-size:12px;font-weight:400">深い水 8.84 m/s</text><text x="144.8" y="94.2314848809936" text-anchor="start" style="font-size:12px;font-weight:400">√(g d)（浅い水の式）</text><text x="286.0" y="113.19999999999999" text-anchor="start" style="font-size:12px;font-weight:700">tanh を含む式（波長 50 m）</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="178.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">10</text><text x="286.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">20</text><text x="394.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30</text><text x="502.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">40</text><text x="610.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">50</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">5</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="340.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">水深 d（m）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">位相速度 c（m/s）</text></svg>

### 岸に近づくと波長が縮む {#shoaling}

岸に向かって波が進むとき波の周期は変わらず（波を作った風や沖の波が決めています）、水深が浅くなって速さが落ちる分、波長が縮みます。周期が 8 秒の波で角周波数を保ったまま水深を変えたときの波長をニュートン法で解いた結果は次のとおりです。

- 水深 200 m と 50 m では、波長は 99.9 m と 99.6 m で、ほとんど変わりません。
- 水深 20 m で 88.8 m、10 m で 70.9 m、5 m で 53.1 m、2 m で 34.7 m まで縮みます。速さは 12.49 m/s から 4.34 m/s に落ちます。

波長が縮むと波頭の間隔が詰まり高さは（エネルギーが保たれるため）増して、波が切り立ちます。このページで数えたのは波長と速さだけで、高さの増え方は計算していません。

### 水深を読んで速さを変えるときの注意 {#shoaling-twist}

地形の水深マップを読んで場所ごとに `ω` を変えると、波が岸へ向かって曲がる様子（屈折）も出せます。ところが、位相 `k·x − ω·t` の `ω` が場所ごとに違うと時間がたつほど場所ごとの位相の差が開き、波がねじれて崩れます。実際のゲームでは波の向きを水深の勾配に少し寄せる程度の簡易な方法にとどめることが多いと思います。この「多い」は私の印象で数字ではありません。

## 風から波の大きさを決める {#wind}

波の振幅や波長は風の強さから決められます。十分長い時間と広い海で風が吹き続けて、波がこれ以上発達しなくなった状態（完全に発達した海）なら波の高さは風速の 2 乗に比例します。

使うのは Pierson と Moskowitz が 1964 年に提案したスペクトルです。このページでは原論文を読めていないので、スペクトルの定数（`α = 8.1×10⁻³`、`β = 0.74`）は私の記憶によるもので、す。Wikipedia の関連記事はこの定数を載せていませんでした。確認できたのは旧版の `0.21·U²/g` とこの定数の整合です。次のスペクトルから有義波高を求めると、`0.209·U²/g` になり旧版の 0.21 と合います。

```text
S(ω) = α g² / ω⁵ · exp( −β (g / (U ω))⁴ )      U: 風速（m/s）
有義波高 Hs = 4 √m0，m0 = S の積分 = α U⁴ / (4 β g²)
ピークの角周波数 ωp = (4β / 5)^(1/4) · g / U ≈ 0.877 g / U
```

`Hs` を式に直すと `4·√(α / 4β) · U²/g ≈ 0.209 U²/g` です。別の資料（Wikipedia の Wind wave model）は、深い水の発達した波の関係として `g·Hs / u² = 0.283` を載せています。これは風速をどの高さで測るかなどの定義が違う別の値で、0.21 と 0.283 のどちらが正しいという話ではありません。ゲームで使う風速の意味に合わせて、定数を選びます。

### 旧版の誤り：最も強い波の波長 {#wind-wavelength}

最も強い波の波長はピークの位相速度 `cp = g / ωp = 1.14·U` から `λp = 2π·cp² / g` で出します。風速 10 m/s なら約 83 m です。旧版は `λp ≈ 2π·U² / (1.13²·g) ≈ 0.5·U²`（10 m/s で 50 m）と書いていて、`1.14` を割り算の側に入れていたため、実際の約 6 割になっていました。この ページでは直してあります。

風速ごとの値を後に載せる C++ で数えました。

- U = 3 m/s：Hs 0.19 m、λp 7.5 m（旧版は Hs 0.1 m）
- U = 6 m/s：Hs 0.77 m、λp 30.0 m（旧版は Hs 0.5 m）
- U = 10 m/s：Hs 2.13 m、λp 83.2 m
- U = 15 m/s：Hs 4.80 m、λp 187.3 m
- U = 20 m/s：Hs 8.53 m、λp 333.0 m

これらは完全に発達した海の値です。吹き始めて間もないと、きや陸に近く風が吹き渡る距離が短いときは、波はこれより小さく波長も短くなります。ゲームの天候に使うなら嵐の波を表すこの値を上限にして、弱い風の設定では小さい値を手で決めるほうが安全です。

天候が変わるとき振幅を急に変えると水面がぱっと動きます。風速のほうを時間をかけて補間して、そこから振幅と波長を計算します。

## 遠くをちらつかせない（LOD） {#lod}

遠くの水面で波の 1 波長が数画素より細かくなると、ちらつきます。画素の間隔より細かい模様は標本化定理により正しく表せません。そこで、波長ごとに「どの距離まで描くか」を決めて、振幅を連続的に 0 へ近づけます。

距離 `d` での 1 画素の大きさは `d · 2·tan(fov/2) / H`（`fov` は縦の画角、`H` は縦の画素数）です。縦の画角 60°、縦 1080 画素なら距離 `d` の 1 画素は `0.001069·d` m で、`1 m` あたり 935 画素です。1 波長を `N` 画素で描きたいなら見える距離は波長の `935 / N` 倍になります。

<svg class="fig flow" viewBox="0 0 660 296" role="img" aria-label="LOD の距離"><defs><marker id="a3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">波の見える距離</text><line x1="90" y1="240" x2="610" y2="240" stroke="currentColor" stroke-width="1.5"/><rect x="120" y="80.88" width="60" height="159.12" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="150" y="72.88" text-anchor="middle" style="font-size:13px;font-weight:700">468 倍</text><text x="150" y="258" text-anchor="middle" style="font-size:12px;font-weight:400">2 画素</text><rect x="245" y="160.44" width="60" height="79.56" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="275" y="152.44" text-anchor="middle" style="font-size:13px;font-weight:700">234 倍</text><text x="275" y="258" text-anchor="middle" style="font-size:12px;font-weight:400">4 画素</text><rect x="370" y="200.22" width="60" height="39.78" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="400" y="192.22" text-anchor="middle" style="font-size:13px;font-weight:700">117 倍</text><text x="400" y="258" text-anchor="middle" style="font-size:12px;font-weight:400">8 画素</text><rect x="495" y="226.06" width="60" height="13.94" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="525" y="218.06" text-anchor="middle" style="font-size:13px;font-weight:700">41 倍</text><text x="525" y="258" text-anchor="middle" style="font-size:12px;font-weight:400">23 画素</text><text x="350.0" y="280" text-anchor="middle" style="font-size:12px;font-weight:400">1 波長を何画素で描くか（縦 1080 画素、縦の画角 60°）</text><text x="94" y="62" text-anchor="start" style="font-size:12px;font-weight:400">見える距離（波長の何倍か）</text><text x="606" y="180.5" text-anchor="end" style="font-size:12px;font-weight:400">黄色: 旧版の「波長の 40 倍」</text></svg>

`N = 2`（標本化の下限）で 468 倍、`N = 4` で 234 倍、`N = 8` で 117 倍、旧版の「波長の 40 倍」は `N = 23` 画素に当たります。旧版の値は安全側に倒した値です。ただし、ちらつかない距離と模様が美しく見える距離は別の話で実際は、見た目で `N` を決めて調整します。

LOD では波の本数を切り替えるより振幅を距離で連続的に減らすほうが、切り替えのポップが出ません。次の `LodFade` は波長の `gCameraDistanceScale` 倍で振幅が 0 になる 1 次の減衰です。

```hlsl
// 距離による振幅の薄れ。波長の gCameraDistanceScale 倍で 0 になる（短い波ほど近くで消える）。
float LodFade(float wavelength, float dist) {
  float visible = wavelength * gCameraDistanceScale;   // この距離を超えると 1 波長が細かすぎる
  return saturate(1.0 - dist / visible);               // 近いと 1、visible で 0
}
```

`wavelength * gCameraDistanceScale` がその波の見える距離です。距離が 0 なら 1、見える距離で 0 になります。

## 規則性を崩す {#irregular}

波が同じ形で同じ向きに進み続けると、機械的に見えます。崩し方は 5 つあります。

- **向きをばらす。** 波ごとの向きを風向きの周りに ±30° くらいばらつかせます。
- **波長を不規則にする。** 波長を等比数列にせず少し乱数でずらします。
- **位相にノイズを足す。** 位置に依存する低周波のノイズを位相に足すと波頭がまっすぐに並びません。
- **振幅を場所で変える。** 低周波のノイズで波の強い所と弱い所を作ります。
- **振幅を時間で変える。** 突風や静けさをゆっくり変わる振幅で表します。

位相にノイズを足すときの副作用に注意します。位相が `k·x + noise·s`（`s` はゆらぎの大きさ）なら場所によって実効の波数が `k + s·∂noise/∂x` になります。たとえば `s = 2 rad` でノイズが 50 m の間に 0 から 1 まで変わると仮定すると、勾配は `0.04 rad/m` です。波長 1 m の波（`k = 6.28 rad/m`）では 0.6% の変化で目立ちませんが、波長 100 m の波（`k = 0.063 rad/m`）では 64% も変わり元の波が崩れます。位相へのノイズは短い波にだけ足すのが無難です。この見積もりの前提（ノイズの変化の速さ）は、私が置いた仮定です。

## 時間の精度 {#precision}

経過時間を `float` で増やし続けると、数時間後に精度が足りなくなります。`float` は大きな値ほど次に表せる値との差が広がります。C++ で次に表せる値との差を数えました。

- 60 秒：差は 0.0000038 秒（3.8 マイクロ秒）
- 1 時間（3600 秒）：0.000244 秒
- 10 時間（36000 秒）：0.0039 秒
- 100 時間（360000 秒）：0.0313 秒

旧版の表は 10 時間を 0.002 秒、100 時間を 0.015 秒と書いていて、半分でした。直しました。

<svg class="fig flow" viewBox="0 0 660 296" role="img" aria-label="経過時間の刻み"><defs><marker id="a2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">float の時間の刻み</text><line x1="90" y1="240" x2="610" y2="240" stroke="currentColor" stroke-width="1.5"/><rect x="120" y="219.12779052179485" width="60" height="20.87220947820515" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="150" y="211.12779052179485" text-anchor="middle" style="font-size:12px;font-weight:400">0.0038 ms</text><text x="150" y="258" text-anchor="middle" style="font-size:12px;font-weight:700">1 分</text><rect x="245" y="154.05396625180575" width="60" height="85.94603374819425" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="275" y="146.05396625180575" text-anchor="middle" style="font-size:12px;font-weight:400">0.244 ms</text><text x="275" y="258" text-anchor="middle" style="font-size:12px;font-weight:700">1 時間</text><rect x="370" y="110.69763939773392" width="60" height="129.30236060226608" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="400" y="102.69763939773392" text-anchor="middle" style="font-size:12px;font-weight:400">3.906 ms</text><text x="400" y="258" text-anchor="middle" style="font-size:12px;font-weight:700">10 時間</text><rect x="495" y="78.18539921951663" width="60" height="161.81460078048337" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="525" y="70.18539921951663" text-anchor="middle" style="font-size:12px;font-weight:400">31.25 ms</text><text x="525" y="258" text-anchor="middle" style="font-size:12px;font-weight:700">100 時間</text><line x1="90" y1="88.01344501381118" x2="610" y2="88.01344501381118" stroke="#e5aa28" stroke-width="2" stroke-dasharray="6 4"/><text x="606" y="82.01344501381118" text-anchor="end" style="font-size:12px;font-weight:400">1 フレーム = 16.7 ms</text><text x="350.0" y="280" text-anchor="middle" style="font-size:12px;font-weight:400">float の経過時間（対数の縦軸。値は次に表せる時間との差）</text></svg>

時間の刻みが問題になるのは位相 `ω·t` が大きいときです。波長 1 m の波は `ω = 7.85 rad/s` なので、時間が 10 時間（刻み 3.9 ms）で位相が 0.031 rad、100 時間（刻み 31 ms）で 0.245 rad ずつしか動けなくなります。位相が 0.245 rad ずつ飛ぶと 60 fps のフレーム（16.7 ms）の間隔より粗くなり、動きがカクカクします。波長が短いほど `ω` が大きく、同じ刻みでも位相の飛びが大きくなります。

### 周期で折り返す {#wrap}

対策は時間を周期で折り返すことです。すべての波の角周波数を基本の角周波数 `ω_base = 2π / T0` の整数倍にそろえておくと `sin(n·ω_base·t)` は周期 `T0` で完全に繰り返すので、時間を `fmod(t, T0)` に置き換えても継ぎ目が出ません。

整数倍に丸めると波の速さがわずかに変わります。基本の周期 `T0` で変化量を比べました。

- `T0 = 60 s`：波長 1 m は +0.04%、10 m は +1.23%、50 m は +3.75%、200 m は −5.68% です。長い波ほど角周波数が基本に近く、丸めの影響が大きくなります。
- `T0 = 600 s`：波長 1 m は +0.04%、10 m は −0.03%、50 m は −0.02%、200 m は −0.02% です。

旧版は「速さはわずかに変わるが気づかない」と書いていました。60 秒の周期では長い波の 5.7% の変化が見えることがあります。周期を 600 秒（10 分）まで伸ばすと変化はほぼ消えます。そのかわり 10 分ごとに同じ動きが繰り返されますが、複数の波の位相が重なる様子は 10 分では気づかれにくいと思います（これも私の印象です）。

折り返した時間は最大でも 600 秒です。そのときの `float` の刻みは 600 秒付近で約 0.00006 秒（60 マイクロ秒）で、100 時間の 31 ミリ秒に比べて桁が違います。

```hlsl
// 時間を周期で折り返す。fmod は負の値を負で返すので、足した: 負の時間でも 0〜周期に入れる。
float WrapTime(float t, float period) {
  float r = fmod(t, period);
  return r < 0.0 ? r + period : r;
}
```

HLSL の `fmod` は負の値を負のまま返すので、負の時間が入ることがあるなら周期を足して 0 以上に戻します。この処理は資料にない処理で私が足しました。

```hlsl
// 時間の折り返しに合わせて、角周波数を基本の整数倍に丸める（C++ 側で波を作るときに使う）。
// omega_base = 2 pi / period。周期 600 秒なら速さの変化は 0.04% 以下（本文の数字）。
float SnapOmega(float omega, float period) {
  float w_base = kTwoPi / period;                      // 基本の角周波数
  return max(1.0, round(omega / w_base)) * w_base;     // 足した: 最低でも基本の 1 倍（0 にならないように）
}
```

`SnapOmega` は波を作るときに（または毎ピクセルで）角周波数を基本の整数倍に丸めます。0 倍にならないように最低でも 1 倍にします。この処理も私が足しました。

水深で角周波数が変わる波にも同じように `SnapOmega` をかけます。丸めない場合、折り返しの瞬間に位相が跳びます。丸めても水深の違う場所の位相が時間とともにずれていく問題は残ります（先の「水深を読んで速さを変えるときの注意」）。丸めの誤差は最大で `ω_base/2` ですから、`T0` の間にずれる位相は最大でも π ですが、継ぎ目では 0 に戻ります。

## 通して組む：水面の高さを求める {#hlsl}

ここまでの部品を 1 つの水面のシェーダーにまとめます。`fxc`（Windows SDK 10.0.26100.0、`-T ps_5_0`）でコンパイルが通ることを確かめました。実行はしていません。

まず、波の定義と定数バッファです。

```hlsl
// ---- 波の合成: 分散関係・距離による LOD・位相のゆらぎ・時間の折り返し ----

static const int   kWaveCount = 8;      // 合成する波の数（一例）
static const float kGravity   = 9.81;   // 重力加速度（m/s^2）
static const float kTwoPi     = 6.28318530718;

struct Wave {
  float2 dir;          // 進む向き（XZ、長さ 1）。風向きの周りにばらした値
  float  wavelength;   // 波長（m）
  float  amplitude;    // 振幅（m）。波長の 1/50 前後までにしておく（急になりすぎない）
  float  phase0;       // 初めの位相（rad）。波ごとにずらして、山がそろわないようにする
};

cbuffer WaveCB : register(b0) {
  Wave   gWaves[kWaveCount];   // 波の一覧
  float  gTime;                // 秒。折り返し済みの値を渡す（下の gWrapPeriod で折り返す）
  float  gWrapPeriod;          // 全体が一巡する周期（秒）。波の角周波数をこの整数倍にしてある
  float  gCameraDistanceScale; // LOD の見える距離の係数。波長のこの倍まで見える（例: 40）
  float  gNoiseStrength;       // 位相のゆらぎの大きさ（rad）。例: 2.0
};

Texture2D<float> gPhaseNoise : register(t0);   // 低周波の連続したノイズ（0〜1）
SamplerState     gLinearWrap : register(s0);
```

波は `Wave` の配列で向き・波長・振幅・初めの位相を持ちます。向きと波長と位相はあらかじめばらして、C++ 側で作っておきます。`gTime` は折り返しの前の時間でシェーダー側で `WrapTime` にかけます（時間を `float` のまま渡すと、折り返す前の時点で精度が落ちるので、実際には C++ 側で `double` のまま折り返してから渡すほうが安全です）。

分散関係の角周波数です。

```hlsl
// 水深 depth（m）での、波数 k（rad/m）の波の角周波数。分散関係 omega^2 = g k tanh(k d)。
float WaveOmega(float k, float depth) {
  return sqrt(kGravity * k * tanh(k * depth));
}
```

そして、波を足し合わせる本体です。

```hlsl
// 1 点の水面の高さ（m）。p は水面の XZ 位置（m）、depth はその場所の水深（m）、dist はカメラからの距離（m）。
float WaterHeight(float2 p, float depth, float dist) {
  float t = WrapTime(gTime, gWrapPeriod);              // 長時間でも精度が落ちない時間
  // 低周波のノイズ。0.01 は 1 / 100 m で、100 m で 1 周期の連続変化（一例）。
  float noise = gPhaseNoise.SampleLevel(gLinearWrap, p * 0.01, 0);
  float height = 0.0;                                  // 合成した高さ

  [unroll]
  for (int i = 0; i < kWaveCount; ++i) {
    Wave w = gWaves[i];                                // i 番目の波
    float k = kTwoPi / w.wavelength;                   // 波数（rad/m）
    // 水深を考えた角周波数を、基本の整数倍に丸める。丸めないと、折り返しの継ぎ目で位相が跳ぶ。
    float omega = SnapOmega(WaveOmega(k, depth), gWrapPeriod);
    // 位相 = 位置の進み + 時間の進み + 初めの位相 + 場所ごとのゆらぎ。
    // 時間の進みを引くので、波は dir の向きに進む。
    float phase = k * dot(w.dir, p) - omega * t + w.phase0 + noise * gNoiseStrength;
    height += w.amplitude * LodFade(w.wavelength, dist) * sin(phase);   // 距離で薄めて足す
  }
  return height;
}
```

ループは 8 本の波を足します。`noise` はループの外で 1 回だけ読み全部の波に同じノイズを足すので、場所ごとの位相のずれが全部の波でそろって、ねじれません。波ごとに違うノイズが欲しいなら波ごとに読む場所をずらします。位相の式で `omega * t` を引いているのは、波を `dir` の向きに進めるためです。足すと逆向きに進みます。

法線は高さの中心差分から求めます。

```hlsl
// 水面の高さを、法線ごと求める簡単な版: 中心差分。h は差分の幅（m）。
float3 WaterNormal(float2 p, float depth, float dist) {
  const float h = 0.25;                                // 差分の幅（一例）。波長の最小に比べて十分小さく
  float hx = WaterHeight(p + float2(h, 0), depth, dist) - WaterHeight(p - float2(h, 0), depth, dist);
  float hz = WaterHeight(p + float2(0, h), depth, dist) - WaterHeight(p - float2(0, h), depth, dist);
  return normalize(float3(-hx, 2.0 * h, -hz));         // 勾配から法線へ（Y が上）
}
```

差分の幅 `h` はいちばん短い波長に比べて十分に小さくします。大きいと細かい波が差分の間に落ちて見えなくなります。

```hlsl
float4 WaterPS(float4 sv_position : SV_Position, float3 world : TEXCOORD0, float depth : TEXCOORD1) : SV_Target {
  float dist = length(world);                          // 足した: カメラが原点にある前提の簡易な距離
  float3 n = WaterNormal(world.xz, depth, dist);       // 水面の法線
  float diffuse = saturate(dot(n, normalize(float3(0.3, 1.0, 0.2))));   // 動作確認用の簡単な照明
  return float4(diffuse.xxx, 1.0);
}
```

ピクセル シェーダーは動作の確認用に簡単な拡散だけを返します。カメラが原点にあるという前提の距離の求め方は、私が足した簡易なものです。本番ではカメラの位置を定数バッファで渡して、`world - camera` の長さを使います。

## C++ で数字を確かめる {#cpp}

この節のほとんどの数字は次のプログラムの出力です。`g++ -std=c++23 -Wall -Wextra` でコンパイルして実行しました。

```cpp
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;   // 円周率
const double kG = 9.81;                // 重力加速度（m/s^2）

// 水深 d（m）で、波数 k の波の角周波数 omega（rad/s）。線形波動論の分散関係 omega^2 = g k tanh(k d)。
double Omega(double k, double d) { return std::sqrt(kG * k * std::tanh(k * d)); }

// 角周波数 omega の波が、水深 d で持つ波数 k を、ニュートン法で求める。
// omega は水深が変わっても（岸に近づいても）保たれる量なので、波長の変化を調べるのに使う。
double WaveNumber(double omega, double d) {
  double k = omega * omega / kG;                       // 深い水の解を初期値にする
  for (int i = 0; i < 50; ++i) {
    const double f = kG * k * std::tanh(k * d) - omega * omega;   // 解きたい式 f(k) = 0
    const double c = std::cosh(k * d);
    const double df = kG * (std::tanh(k * d) + k * d / (c * c));  // f の k による微分
    k -= f / df;                                       // ニュートン法の 1 歩
  }
  return k;
}

int main() {
  // 1. 水深と位相速度。波長 50 m の波。
  std::printf("-- phase speed, wavelength 50 m\n");
  const double k50 = 2.0 * kPi / 50.0;                 // 波数（rad/m）
  const double c_deep = std::sqrt(kG / k50);           // 深い水の速さ sqrt(g / k)
  for (double d : {2.0, 5.0, 10.0, 25.0, 50.0}) {      // 水深（m）
    const double c = Omega(k50, d) / k50;              // 位相速度 omega / k
    std::printf("depth %4.0f m: c = %.2f m/s (deep %.2f, shallow sqrt(g d) = %.2f)\n", d, c, c_deep,
                std::sqrt(kG * d));
  }

  // 2. 岸に近づくと波長が縮む。周期 8 秒の波。
  std::printf("-- shoaling, period 8 s\n");
  const double omega = 2.0 * kPi / 8.0;                // 周期 8 秒の角周波数（rad/s）
  for (double d : {200.0, 50.0, 20.0, 10.0, 5.0, 2.0}) {
    const double k = WaveNumber(omega, d);             // この水深での波数
    std::printf("depth %5.0f m: wavelength = %6.1f m, c = %.2f m/s\n", d, 2.0 * kPi / k, omega / k);
  }

  // 3. Pierson-Moskowitz スペクトル（S = alpha g^2 / w^5 * exp(-beta (g / (U w))^4)）から。
  //    定数 alpha と beta は、記憶による値で、原論文では確かめていない。
  std::printf("-- Pierson-Moskowitz (alpha = 8.1e-3, beta = 0.74)\n");
  const double alpha = 8.1e-3;
  const double beta = 0.74;
  for (double u : {3.0, 6.0, 10.0, 15.0, 20.0}) {      // 風速（m/s）
    const double m0 = alpha * u * u * u * u / (4.0 * beta * kG * kG);       // スペクトルの面積（分散）
    const double hs = 4.0 * std::sqrt(m0);                                   // 有義波高 4 sqrt(m0)
    const double wp = std::pow(4.0 * beta / 5.0, 0.25) * kG / u;             // ピークの角周波数
    const double cp = kG / wp;                                               // ピークの位相速度
    const double lp = 2.0 * kPi * cp * cp / kG;                              // ピークの波長
    std::printf("U=%2.0f m/s: Hs = %5.2f m (0.21 U^2/g = %5.2f), wp = %.3f rad/s, cp = %.1f m/s, lambda_p = %6.1f m (0.5 U^2 = %5.1f)\n",
                u, hs, 0.21 * u * u / kG, wp, cp, lp, 0.5 * u * u);
  }

  // 4. 時間を float で持ったときの刻み（ulp）。
  std::printf("-- float time resolution\n");
  const double lambda1 = 1.0;                          // 波長 1 m の細かい波
  const double w1 = std::sqrt(kG * 2.0 * kPi / lambda1);   // その角周波数（rad/s）
  for (double hours : {0.0167, 1.0, 10.0, 100.0}) {
    const float t = static_cast<float>(hours * 3600.0);                 // 経過時間（秒）
    const double ulp = std::nextafter(t, 1e30f) - static_cast<double>(t);   // t の次に表せる値との差
    std::printf("t = %8.0f s (%.3g h): step = %.7f s, phase step (lambda 1 m) = %.5f rad\n", static_cast<double>(t),
                hours, ulp, ulp * w1);
  }

  // 5. 波の角周波数を基本の整数倍に丸めたときの速さの変化。基本の周期を 60 秒と 600 秒で比べる。
  std::printf("-- snap omega to n * omega_base\n");
  for (double period : {60.0, 600.0}) {                // 全体が一巡する周期（秒）
    const double w_base = 2.0 * kPi / period;          // 基本の角周波数（rad/s）
    for (double lambda : {1.0, 10.0, 50.0, 200.0}) {
      const double w = std::sqrt(kG * 2.0 * kPi / lambda);             // 元の角周波数
      const double w_snap = std::round(w / w_base) * w_base;           // 整数倍に丸めた値
      std::printf("period %3.0f s, lambda %5.0f m: omega %.4f -> %.4f, change %+.2f%%\n", period, lambda, w, w_snap,
                  100.0 * (w_snap - w) / w);
    }
  }

  // 6. 波が画面で何画素になるか。縦の画角 60 度、縦 1080 画素。
  std::printf("-- LOD distance\n");
  const double px_per_m_at_1m = 1080.0 / (2.0 * std::tan(30.0 * kPi / 180.0));   // 距離 1 m で 1 m が何画素か
  for (double n : {2.0, 4.0, 8.0, 23.0}) {             // 1 波長を何画素で描きたいか
    std::printf("%4.0f px per wavelength: visible up to %.0f x wavelength\n", n, px_per_m_at_1m / n);
  }
}
```

```text title="実行結果"
-- phase speed, wavelength 50 m
depth    2 m: c = 4.38 m/s (deep 8.84, shallow sqrt(g d) = 4.43)
depth    5 m: c = 6.59 m/s (deep 8.84, shallow sqrt(g d) = 7.00)
depth   10 m: c = 8.15 m/s (deep 8.84, shallow sqrt(g d) = 9.90)
depth   25 m: c = 8.82 m/s (deep 8.84, shallow sqrt(g d) = 15.66)
depth   50 m: c = 8.84 m/s (deep 8.84, shallow sqrt(g d) = 22.15)
-- shoaling, period 8 s
depth   200 m: wavelength =   99.9 m, c = 12.49 m/s
depth    50 m: wavelength =   99.6 m, c = 12.45 m/s
depth    20 m: wavelength =   88.8 m, c = 11.10 m/s
depth    10 m: wavelength =   70.9 m, c = 8.86 m/s
depth     5 m: wavelength =   53.1 m, c = 6.64 m/s
depth     2 m: wavelength =   34.7 m, c = 4.34 m/s
-- Pierson-Moskowitz (alpha = 8.1e-3, beta = 0.74)
U= 3 m/s: Hs =  0.19 m (0.21 U^2/g =  0.19), wp = 2.868 rad/s, cp = 3.4 m/s, lambda_p =    7.5 m (0.5 U^2 =   4.5)
U= 6 m/s: Hs =  0.77 m (0.21 U^2/g =  0.77), wp = 1.434 rad/s, cp = 6.8 m/s, lambda_p =   30.0 m (0.5 U^2 =  18.0)
U=10 m/s: Hs =  2.13 m (0.21 U^2/g =  2.14), wp = 0.860 rad/s, cp = 11.4 m/s, lambda_p =   83.2 m (0.5 U^2 =  50.0)
U=15 m/s: Hs =  4.80 m (0.21 U^2/g =  4.82), wp = 0.574 rad/s, cp = 17.1 m/s, lambda_p =  187.3 m (0.5 U^2 = 112.5)
U=20 m/s: Hs =  8.53 m (0.21 U^2/g =  8.56), wp = 0.430 rad/s, cp = 22.8 m/s, lambda_p =  333.0 m (0.5 U^2 = 200.0)
-- float time resolution
t =       60 s (0.0167 h): step = 0.0000038 s, phase step (lambda 1 m) = 0.00003 rad
t =     3600 s (1 h): step = 0.0002441 s, phase step (lambda 1 m) = 0.00192 rad
t =    36000 s (10 h): step = 0.0039062 s, phase step (lambda 1 m) = 0.03067 rad
t =   360000 s (100 h): step = 0.0312500 s, phase step (lambda 1 m) = 0.24534 rad
-- snap omega to n * omega_base
period  60 s, lambda     1 m: omega 7.8510 -> 7.8540, change +0.04%
period  60 s, lambda    10 m: omega 2.4827 -> 2.5133, change +1.23%
period  60 s, lambda    50 m: omega 1.1103 -> 1.1519, change +3.75%
period  60 s, lambda   200 m: omega 0.5551 -> 0.5236, change -5.68%
period 600 s, lambda     1 m: omega 7.8510 -> 7.8540, change +0.04%
period 600 s, lambda    10 m: omega 2.4827 -> 2.4819, change -0.03%
period 600 s, lambda    50 m: omega 1.1103 -> 1.1100, change -0.02%
period 600 s, lambda   200 m: omega 0.5551 -> 0.5550, change -0.02%
-- LOD distance
   2 px per wavelength: visible up to 468 x wavelength
   4 px per wavelength: visible up to 234 x wavelength
   8 px per wavelength: visible up to 117 x wavelength
  23 px per wavelength: visible up to 41 x wavelength
```

出力の 3 つ目の節（Pierson-Moskowitz）の最後の 2 つの値は、旧版の `0.5·U²` と比べるために並べました。10 m/s で 83.2 m と 50.0 m で、旧版が小さすぎたことが数字で確かめられます。

## よくあるミス {#mistakes}

??? failure "長時間プレイすると、波がカクつく"
    経過時間を `float` で足し続けると、100 時間で刻みが 31 ミリ秒になり位相の変化が粗くなります。時間を周期で折り返し角周波数を基本の整数倍にそろえておきます。折り返す前の時間は `double` で持ちます。

??? failure "折り返しの瞬間に波がぴくっと跳ぶ"
    角周波数が基本の整数倍になっていないと `ω·T0` が 2π の整数倍にならず、折り返しの瞬間に位相が跳びます。水深で角周波数が変わる波でも丸めを忘れると同じことが起きます。

??? failure "水深を考えたら、波がねじれて崩れた"
    場所ごとに `ω` が違うと時間がたつほど位相の差が開いていきます。水深で速さを変えるのはごく浅い部分にとどめるか波の向きだけを水深の勾配に寄せます。

??? failure "遠くの水面がちらつく"
    1 波長が 2 画素より細かい波が描かれています。波長ごとに見える距離を決めて、`LodFade` で振幅を 0 に近づけます。法線のほうも細かい波を同じ距離で薄めないと法線だけがちらつきます。

??? failure "位相のノイズで、長い波が崩れた"
    位相にノイズを足すと実効の波数が変わります。長い波ほど変化の割合が大きくなるので、ノイズは短い波にだけ足します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 波の速さは分散関係 `ω² = g·k·tanh(kd)` で決まる。深い水は `√(gλ/2π)`、浅い水は `√(gd)`
    - [x] 見える距離は `935 / N` 倍（縦 1080 画素・縦画角 60°・1 波長を N 画素で描く）
    - [x] `float` の時間は 100 時間で刻み 31 ミリ秒。周期 600 秒で折り返す
    - [x] 風速 10 m/s の完全に発達した海は、Hs 約 2.1 m、ピークの波長約 83 m

## 参考 {#references}

読んだ範囲を書きます。

- Wikipedia, "Dispersion (water waves)"。線形の分散関係、位相速度、群速度、深い水（`h > λ/2`）と浅い水（`h < λ/20`）の境目を確かめました。
- Wikipedia, "Wind wave model"。深い水の発達した波の関係 `g·Hs / u² = 0.283` を確かめました。Pierson と Moskowitz のスペクトルの式と定数は載っていませんでした。
- Willard J. Pierson, Lionel Moskowitz, "A Proposed Spectral Form for Fully Developed Wind Seas Based on the Similarity Theory of S. A. Kitaigorodskii", Journal of Geophysical Research, Vol. 69, No. 24, 1964。読んでいません。スペクトルの定数は私の記憶によるもので、有義波高の係数が旧版の 0.21 と整合することだけを確かめました。
- Mark Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004。読んでいません。
- Jerry Tessendorf, "Simulating Ocean Water", SIGGRAPH Course Notes, 2001。読んでいません。
- K. Hasselmann ほか, "Measurements of Wind-Wave Growth and Swell Decay during the Joint North Sea Wave Project (JONSWAP)", Deutsche Hydrographische Zeitschrift, Reihe A, Vol. 8, No. 12, 1973。読んでいません。

## 関連ページ {#related}

- [Water Waves](index.md)
- [Summing Sine Waves](sine-waves.md)
- [Wakes and Collisions](../shore-foam/wake.md)
