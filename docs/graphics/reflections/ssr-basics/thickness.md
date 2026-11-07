---
title: Thickness
tags:
  - 描画
---

# Thickness

床に柱が立っていてその向こうに壁があるとします。柱の横をかすめて壁へ向かう反射レイが、柱の画素の上を通るとき SSR は「このレイは柱に当たったのか柱の後ろを抜けたのか」を決めなければなりません。ところが深度バッファに入っているのは、カメラに一番近い面の深さだけです。柱がどれだけ厚いのかはどこにも書かれていません。そこで「表の面から T メートル以内に入ったら当たり」という約束（厚み）を決めて判定します。T が小さければ薄い物を見逃し、大きければ物の後ろの景色が物の色に染まります。このページでは T がどう効くかを数字で確かめ距離に応じた決め方、深度の精度による下限、裏面の深度で厚みを測る方法、偽の当たりを減らす工夫をコードにまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）で構文を確かめましたが、画面には出していません。下の参考資料は**今回は読んでいません**。厚みの考え方と式は自分で導いて数字で確かめたもので、各資料の記述との一致は確かめていません。

!!! tip "ポイント"
    - 判定は「レイの深さ − 表の面の深さ」が `0 より大きく T より小さい` のとき当たり T 以上なら裏へ抜けたです。
    - T は 2 つの失敗の綱引きです。T が d（物の本当の厚み）より小さければ、レイは物の中を通っても受理されません。T が d より大きければ物の後ろの `T − d` の帯を通るレイが、偽の当たりになります。
    - ステップの深さ方向の幅 s が T より大きいと薄い物はすり抜けます。s = 0.5 m・T = 0.25 m なら標本が受理範囲に入る確率は 50% です。
    - T を距離に比例させる根拠は、1 画素が覆う世界の大きさ `z / f`（f は焦点距離の画素数）です。垂直 FOV 60 度・1080p なら 50 m で 0.0535 m、1000 m で 1.07 m です。
    - 24 ビットの標準 Z だと深さの刻みは 100 m で 0.00596 m、500 m で 0.149 m です。T をこれより小さくすると受理がノイズになります。
    - 裏面の深度を別に描けば、`裏 − 表` が厚みそのものになり推定は要りません。

!!! info "このページを読む前に"
    - [SSR Basics](index.md)（このセクション全体の地図と読む順番）
    - [Linear Marching](linear-march.md)（レイを進めて深度と比べる手順）

## 深度バッファは面しか知らない {#only-surface}

深度バッファが持つのは各画素でカメラに最も近い面の距離だけです。その面の裏側（物の厚み）と手前の物に隠れた奥の物は書かれていません。SSR はレイ上の点の深さをこの値と比べるので、レイが面の奥に入ったとき判定に使える情報は「どれだけ奥か」という 1 つの数字だけです。

レイの深さを `ray_depth`、その画素の表の面の深さを `front` として、`diff = ray_depth − front` を作ります。

- `diff ≤ 0`: レイはまだ表の面に達していません。当たりではありません。
- `0 < diff < T`: レイは表の面の奥に入りましたが、T 以内です。当たりです。
- `diff ≥ T`: 奥に入りすぎました。物を裏へ抜けたと見なし当たりにしません。

<svg class="fig flow" viewBox="0 0 700 360" role="img" aria-label="厚みの受理範囲"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">T による当たりの範囲</text><text x="60" y="22" text-anchor="start" style="font-size:12px;font-weight:400">表の面からの深さ(m)。0 = 表の面、画素の上のレイの深さ</text><rect x="140.0" y="40" width="48.0" height="40" fill="rgba(229,72,77,0.40)" stroke="currentColor"/><text x="164.0" y="64" text-anchor="middle" style="font-size:11px;font-weight:700">柱</text><text x="140.0" y="34" text-anchor="middle" style="font-size:11px;font-weight:400">表 0</text><text x="188.0" y="34" text-anchor="start" style="font-size:11px;font-weight:400">裏 0.3</text><text x="60" y="96" text-anchor="start" style="font-size:12px;font-weight:700">T = 0.25 m</text><rect x="60" y="110" width="80.0" height="26" fill="rgba(120,120,120,0.18)" stroke="currentColor"/><text x="100.0" y="127" text-anchor="middle" style="font-size:11px;font-weight:400">手前</text><rect x="140.0" y="110" width="40.0" height="26" fill="rgba(46,158,91,0.45)" stroke="currentColor"/><text x="160.0" y="127" text-anchor="middle" style="font-size:11px;font-weight:400">当たり</text><rect x="180.0" y="110" width="440.0" height="26" fill="rgba(76,139,245,0.18)" stroke="currentColor"/><text x="400.0" y="127" text-anchor="middle" style="font-size:11px;font-weight:400">外れ(すり抜け)</text><text x="60" y="176" text-anchor="start" style="font-size:12px;font-weight:700">T = 1.0 m</text><rect x="60" y="190" width="80.0" height="26" fill="rgba(120,120,120,0.18)" stroke="currentColor"/><text x="100.0" y="207" text-anchor="middle" style="font-size:11px;font-weight:400">手前</text><rect x="140.0" y="190" width="48.0" height="26" fill="rgba(46,158,91,0.45)" stroke="currentColor"/><rect x="188.0" y="190" width="112.0" height="26" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="244.0" y="207" text-anchor="middle" style="font-size:11px;font-weight:400">偽の当たり</text><rect x="300.0" y="190" width="320.0" height="26" fill="rgba(76,139,245,0.18)" stroke="currentColor"/><text x="460.0" y="207" text-anchor="middle" style="font-size:11px;font-weight:400">外れ</text><text x="60" y="256" text-anchor="start" style="font-size:12px;font-weight:700">T = 無限大</text><rect x="60" y="270" width="80.0" height="26" fill="rgba(120,120,120,0.18)" stroke="currentColor"/><text x="100.0" y="287" text-anchor="middle" style="font-size:11px;font-weight:400">手前</text><rect x="140.0" y="270" width="48.0" height="26" fill="rgba(46,158,91,0.45)" stroke="currentColor"/><rect x="188.0" y="270" width="432.0" height="26" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="404.0" y="287" text-anchor="middle" style="font-size:11px;font-weight:400">全部当たり(偽を含む)</text><text x="140.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="220.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="300.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="380.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">1.5</text><text x="460.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="540.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">2.5</text><text x="620.0" y="322" text-anchor="middle" style="font-size:11px;font-weight:400">3</text><text x="340.0" y="342" text-anchor="middle" style="font-size:12px;font-weight:400">レイの深さ - 表の面の深さ(m)</text></svg>

図は厚み d = 0.3 m の柱の画素の上で、レイの深さを横軸に取ったものです。T = 0.25 m なら柱の中（0〜0.3 m）のうち 0〜0.25 m だけが当たりで、それより奥は外れです。T = 1.0 m にすると、柱の裏（0.3 m）を越えて 1.0 m までが当たりになり 0.3〜1.0 m の 0.7 m は偽の当たりです。T が無限大なら表の面より奥は全部当たりで、柱の向こうの壁に向かうレイもすべて柱に当たります。

## T の大小が起こすこと {#tradeoff}

### T が d より小さいとき {#small}

T が物の本当の厚み d より小さいとレイが物の中にいるのに受理されない深さの範囲ができます。d = 0.3 m の柱で T = 0.1 m なら受理されるのは表の面から 0.1 m までで、残りの 0.2 m は物の内側なのに外れです。ただし偽の当たりは出ません。柱の向こうの景色が柱の色に染まることはなく、代わりに反射が欠けます。

### T が d より大きいとき {#large}

T が d より大きいと物の後ろに `T − d` の幅の帯ができます。この帯の深さでレイが画素の上を通ると、物に当たっていないのに受理されます。数えた値は次のとおりです。

- d = 0.05 m（柵）: T = 0.25 m で帯の幅 0.20 m、T = 1.0 m で 0.95 m、T = 2.0 m で 1.95 m
- d = 0.3 m（柱）: T = 0.5 m で 0.20 m、T = 1.0 m で 0.70 m、T = 2.0 m で 1.70 m
- d = 2.0 m（壁）: T = 2.0 m まで帯は 0 m

厚い壁には大きな T を使っても害がありませんが、薄い柵では T を大きくするほど柵の後ろの広い範囲が偽の当たりになります。一定の T で全部を扱えないのは、このためです。

### 取りこぼしはステップ幅で決まる {#step}

T が d に合っていてもレイの標本がその範囲に入るとは限りません。レイを 1 標本ごとに深さ方向へ s メートル進めるなら標本が深さ `[0, T)` に入る確率は `min(T / s, 1)` です（位相は一様と見なしました）。位相を 20000 通りに振って数えた結果です。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="T と受理確率"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">T と受理確率</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,250.0 72.6,246.2 75.2,242.4 77.8,238.6 80.4,234.8 83.0,231.0 85.6,227.2 88.2,223.4 90.8,219.6 93.4,215.8 96.0,212.0 98.6,208.2 101.2,204.4 103.8,200.6 106.4,196.8 109.0,193.0 111.6,189.2 114.2,185.4 116.8,181.6 119.4,177.8 122.0,174.0 124.6,170.2 127.2,166.4 129.8,162.6 132.4,158.8 135.0,155.0 137.6,151.2 140.2,147.4 142.8,143.6 145.4,139.8 148.0,136.0 150.6,132.2 153.2,128.4 155.8,124.6 158.4,120.8 161.0,117.0 163.6,113.2 166.2,109.4 168.8,105.6 171.4,101.8 174.0,98.0 176.6,94.2 179.2,90.4 181.8,86.6 184.4,82.8 187.0,79.0 189.6,75.2 192.2,71.4 194.8,67.6 197.4,63.8 200.0,60.0 202.6,60.0 205.2,60.0 207.8,60.0 210.4,60.0 213.0,60.0 215.6,60.0 218.2,60.0 220.8,60.0 223.4,60.0 226.0,60.0 228.6,60.0 231.2,60.0 233.8,60.0 236.4,60.0 239.0,60.0 241.6,60.0 244.2,60.0 246.8,60.0 249.4,60.0 252.0,60.0 254.6,60.0 257.2,60.0 259.8,60.0 262.4,60.0 265.0,60.0 267.6,60.0 270.2,60.0 272.8,60.0 275.4,60.0 278.0,60.0 280.6,60.0 283.2,60.0 285.8,60.0 288.4,60.0 291.0,60.0 293.6,60.0 296.2,60.0 298.8,60.0 301.4,60.0 304.0,60.0 306.6,60.0 309.2,60.0 311.8,60.0 314.4,60.0 317.0,60.0 319.6,60.0 322.2,60.0 324.8,60.0 327.4,60.0 330.0,60.0 332.6,60.0 335.2,60.0 337.8,60.0 340.4,60.0 343.0,60.0 345.6,60.0 348.2,60.0 350.8,60.0 353.4,60.0 356.0,60.0 358.6,60.0 361.2,60.0 363.8,60.0 366.4,60.0 369.0,60.0 371.6,60.0 374.2,60.0 376.8,60.0 379.4,60.0 382.0,60.0 384.6,60.0 387.2,60.0 389.8,60.0 392.4,60.0 395.0,60.0 397.6,60.0 400.2,60.0 402.8,60.0 405.4,60.0 408.0,60.0 410.6,60.0 413.2,60.0 415.8,60.0 418.4,60.0 421.0,60.0 423.6,60.0 426.2,60.0 428.8,60.0 431.4,60.0 434.0,60.0 436.6,60.0 439.2,60.0 441.8,60.0 444.4,60.0 447.0,60.0 449.6,60.0 452.2,60.0 454.8,60.0 457.4,60.0 460.0,60.0 462.6,60.0 465.2,60.0 467.8,60.0 470.4,60.0 473.0,60.0 475.6,60.0 478.2,60.0 480.8,60.0 483.4,60.0 486.0,60.0 488.6,60.0 491.2,60.0 493.8,60.0 496.4,60.0 499.0,60.0 501.6,60.0 504.2,60.0 506.8,60.0 509.4,60.0 512.0,60.0 514.6,60.0 517.2,60.0 519.8,60.0 522.4,60.0 525.0,60.0 527.6,60.0 530.2,60.0 532.8,60.0 535.4,60.0 538.0,60.0 540.6,60.0 543.2,60.0 545.8,60.0 548.4,60.0 551.0,60.0 553.6,60.0 556.2,60.0 558.8,60.0 561.4,60.0 564.0,60.0 566.6,60.0 569.2,60.0 571.8,60.0 574.4,60.0 577.0,60.0 579.6,60.0 582.2,60.0 584.8,60.0 587.4,60.0 590.0,60.0"/><text x="206.0" y="76" text-anchor="start" style="font-size:11px;font-weight:700">ステップ 0.5 m</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 72.6,231.0 75.2,212.0 77.8,193.0 80.4,174.0 83.0,155.0 85.6,136.0 88.2,117.0 90.8,98.0 93.4,79.0 96.0,60.0 98.6,60.0 101.2,60.0 103.8,60.0 106.4,60.0 109.0,60.0 111.6,60.0 114.2,60.0 116.8,60.0 119.4,60.0 122.0,60.0 124.6,60.0 127.2,60.0 129.8,60.0 132.4,60.0 135.0,60.0 137.6,60.0 140.2,60.0 142.8,60.0 145.4,60.0 148.0,60.0 150.6,60.0 153.2,60.0 155.8,60.0 158.4,60.0 161.0,60.0 163.6,60.0 166.2,60.0 168.8,60.0 171.4,60.0 174.0,60.0 176.6,60.0 179.2,60.0 181.8,60.0 184.4,60.0 187.0,60.0 189.6,60.0 192.2,60.0 194.8,60.0 197.4,60.0 200.0,60.0 202.6,60.0 205.2,60.0 207.8,60.0 210.4,60.0 213.0,60.0 215.6,60.0 218.2,60.0 220.8,60.0 223.4,60.0 226.0,60.0 228.6,60.0 231.2,60.0 233.8,60.0 236.4,60.0 239.0,60.0 241.6,60.0 244.2,60.0 246.8,60.0 249.4,60.0 252.0,60.0 254.6,60.0 257.2,60.0 259.8,60.0 262.4,60.0 265.0,60.0 267.6,60.0 270.2,60.0 272.8,60.0 275.4,60.0 278.0,60.0 280.6,60.0 283.2,60.0 285.8,60.0 288.4,60.0 291.0,60.0 293.6,60.0 296.2,60.0 298.8,60.0 301.4,60.0 304.0,60.0 306.6,60.0 309.2,60.0 311.8,60.0 314.4,60.0 317.0,60.0 319.6,60.0 322.2,60.0 324.8,60.0 327.4,60.0 330.0,60.0 332.6,60.0 335.2,60.0 337.8,60.0 340.4,60.0 343.0,60.0 345.6,60.0 348.2,60.0 350.8,60.0 353.4,60.0 356.0,60.0 358.6,60.0 361.2,60.0 363.8,60.0 366.4,60.0 369.0,60.0 371.6,60.0 374.2,60.0 376.8,60.0 379.4,60.0 382.0,60.0 384.6,60.0 387.2,60.0 389.8,60.0 392.4,60.0 395.0,60.0 397.6,60.0 400.2,60.0 402.8,60.0 405.4,60.0 408.0,60.0 410.6,60.0 413.2,60.0 415.8,60.0 418.4,60.0 421.0,60.0 423.6,60.0 426.2,60.0 428.8,60.0 431.4,60.0 434.0,60.0 436.6,60.0 439.2,60.0 441.8,60.0 444.4,60.0 447.0,60.0 449.6,60.0 452.2,60.0 454.8,60.0 457.4,60.0 460.0,60.0 462.6,60.0 465.2,60.0 467.8,60.0 470.4,60.0 473.0,60.0 475.6,60.0 478.2,60.0 480.8,60.0 483.4,60.0 486.0,60.0 488.6,60.0 491.2,60.0 493.8,60.0 496.4,60.0 499.0,60.0 501.6,60.0 504.2,60.0 506.8,60.0 509.4,60.0 512.0,60.0 514.6,60.0 517.2,60.0 519.8,60.0 522.4,60.0 525.0,60.0 527.6,60.0 530.2,60.0 532.8,60.0 535.4,60.0 538.0,60.0 540.6,60.0 543.2,60.0 545.8,60.0 548.4,60.0 551.0,60.0 553.6,60.0 556.2,60.0 558.8,60.0 561.4,60.0 564.0,60.0 566.6,60.0 569.2,60.0 571.8,60.0 574.4,60.0 577.0,60.0 579.6,60.0 582.2,60.0 584.8,60.0 587.4,60.0 590.0,60.0"/><text x="102.0" y="76" text-anchor="start" style="font-size:11px;font-weight:700">ステップ 0.1 m</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" stroke-dasharray="6 4" points="70.0,250.0 72.6,250.0 75.2,250.0 77.8,250.0 80.4,250.0 83.0,250.0 85.6,250.0 88.2,250.0 90.8,250.0 93.4,250.0 96.0,250.0 98.6,250.0 101.2,250.0 103.8,250.0 106.4,250.0 109.0,250.0 111.6,250.0 114.2,250.0 116.8,250.0 119.4,250.0 122.0,250.0 124.6,250.0 127.2,250.0 129.8,250.0 132.4,250.0 135.0,250.0 137.6,250.0 140.2,250.0 142.8,250.0 145.4,250.0 148.0,250.0 150.6,249.1 153.2,248.1 155.8,247.2 158.4,246.2 161.0,245.2 163.6,244.3 166.2,243.3 168.8,242.4 171.4,241.4 174.0,240.5 176.6,239.6 179.2,238.6 181.8,237.7 184.4,236.7 187.0,235.8 189.6,234.8 192.2,233.8 194.8,232.9 197.4,231.9 200.0,231.0 202.6,230.1 205.2,229.1 207.8,228.2 210.4,227.2 213.0,226.2 215.6,225.3 218.2,224.3 220.8,223.4 223.4,222.4 226.0,221.5 228.6,220.6 231.2,219.6 233.8,218.7 236.4,217.7 239.0,216.8 241.6,215.8 244.2,214.8 246.8,213.9 249.4,212.9 252.0,212.0 254.6,211.1 257.2,210.1 259.8,209.2 262.4,208.2 265.0,207.2 267.6,206.3 270.2,205.3 272.8,204.4 275.4,203.4 278.0,202.5 280.6,201.6 283.2,200.6 285.8,199.7 288.4,198.7 291.0,197.8 293.6,196.8 296.2,195.8 298.8,194.9 301.4,193.9 304.0,193.0 306.6,192.0 309.2,191.1 311.8,190.1 314.4,189.2 317.0,188.2 319.6,187.3 322.2,186.4 324.8,185.4 327.4,184.4 330.0,183.5 332.6,182.6 335.2,181.6 337.8,180.7 340.4,179.7 343.0,178.8 345.6,177.8 348.2,176.8 350.8,175.9 353.4,174.9 356.0,174.0 358.6,173.1 361.2,172.1 363.8,171.2 366.4,170.2 369.0,169.2 371.6,168.3 374.2,167.4 376.8,166.4 379.4,165.4 382.0,164.5 384.6,163.6 387.2,162.6 389.8,161.7 392.4,160.7 395.0,159.8 397.6,158.8 400.2,157.9 402.8,156.9 405.4,155.9 408.0,155.0 410.6,154.1 413.2,153.1 415.8,152.1 418.4,151.2 421.0,150.2 423.6,149.3 426.2,148.3 428.8,147.4 431.4,146.5 434.0,145.5 436.6,144.6 439.2,143.6 441.8,142.7 444.4,141.7 447.0,140.8 449.6,139.8 452.2,138.9 454.8,137.9 457.4,136.9 460.0,136.0 462.6,135.1 465.2,134.1 467.8,133.2 470.4,132.2 473.0,131.2 475.6,130.3 478.2,129.3 480.8,128.4 483.4,127.5 486.0,126.5 488.6,125.5 491.2,124.6 493.8,123.7 496.4,122.7 499.0,121.8 501.6,120.8 504.2,119.9 506.8,118.9 509.4,118.0 512.0,117.0 514.6,116.1 517.2,115.1 519.8,114.2 522.4,113.2 525.0,112.2 527.6,111.3 530.2,110.3 532.8,109.4 535.4,108.4 538.0,107.5 540.6,106.6 543.2,105.6 545.8,104.7 548.4,103.7 551.0,102.8 553.6,101.8 556.2,100.8 558.8,99.9 561.4,99.0 564.0,98.0 566.6,97.1 569.2,96.1 571.8,95.2 574.4,94.2 577.0,93.2 579.6,92.3 582.2,91.3 584.8,90.4 587.4,89.5 590.0,88.5"/><text x="460.0" y="179.0" text-anchor="start" style="font-size:11px;font-weight:700">偽の帯の幅(d = 0.3 m)</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="200.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="330.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="460.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1.5</text><text x="590.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0.0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">1.0</text><text x="330.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">厚み T(m)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">標本が受理される確率(実線)。右軸: 偽の帯の幅(破線、2 m = 1.0)</text></svg>

- s = 0.5 m・T = 0.25 m: 受理される確率は 50.0%（d = 0.05 m の柵の中に標本が入る確率は 10.0%、d = 0.3 m の柱は 60.0%、d = 2.0 m の壁は 100.0%）
- s = 0.5 m・T = 0.5 m: 受理は 100.0%。ただし帯は柵で 0.45 m、柱で 0.20 m
- s = 0.1 m・T = 0.1 m: 受理は 100.0%（柵の中に入る確率は 50.0%）

s が T より大きいと受理される確率が `T / s` まで落ちます。ステップを細かくするか T を s 以上に取るかしないと薄い物は確率的にしか見えません。柵（d = 0.05 m）は s = 0.5 m だとレイが中に入る確率が 10.0% しかないので、T を大きくしてもステップ幅が粗いままでは見逃します。逆に、ステップ幅が細かければ（s = 0.1 m）、T = 0.1 m で受理は 100% になり柱（d = 0.3 m）は T = 0.1 m でも拾えます。

## 距離に比例させる {#scaled}

深さ方向のステップ幅 s はレイの傾きと画素の大きさで決まります。画素の中央（x = 0）でレイがカメラから遠ざかる成分 dz と画面の横へ動く成分 dx を持つなら、1 画素ぶん横へ進むあいだに深さは `(z / f) × (dz / dx)` だけ変わります。`z / f` は距離 z で 1 画素が覆う世界の長さです。傾き `dz / dx` を k、画素のステップ数を n とすれば、必要な厚みは `T = (z / f) × k × n` になります。T を `pixel_world_size × scale`（scale は k × n）で決めるのは、この式を使っているからです。

垂直 FOV 60 度・高さ 1080 では、f = 540 / tan 30° = 935.3 画素です。このとき `z / f` は次のとおりです。

- z = 2 m: 0.0021 m。傾き 4・4 画素ステップなら T = 0.034 m
- z = 10 m: 0.0107 m。T = 0.171 m
- z = 50 m: 0.0535 m。T = 0.855 m（傾き 1 なら 0.214 m、16 画素ステップなら 3.421 m）
- z = 200 m: 0.2138 m。T = 3.421 m
- z = 1000 m: 1.0692 m。T = 17.107 m

<svg class="fig flow" viewBox="0 0 700 320" role="img" aria-label="必要な厚みと距離"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">距離と必要な厚み</text><line x1="70" y1="260" x2="590" y2="260" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="260" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,210.7 78.7,208.7 87.3,206.7 96.0,204.7 104.7,202.7 113.3,200.7 122.0,198.7 130.7,196.7 139.3,194.7 148.0,192.7 156.7,190.7 165.3,188.7 174.0,186.7 182.7,184.7 191.3,182.7 200.0,180.7 208.7,178.7 217.3,176.7 226.0,174.7 234.7,172.7 243.3,170.7 252.0,168.7 260.7,166.7 269.3,164.7 278.0,162.7 286.7,160.7 295.3,158.7 304.0,156.7 312.7,154.7 321.3,152.7 330.0,150.7 338.7,148.7 347.3,146.7 356.0,144.7 364.7,142.7 373.3,140.7 382.0,138.7 390.7,136.7 399.3,134.7 408.0,132.7 416.7,130.7 425.3,128.7 434.0,126.7 442.7,124.7 451.3,122.7 460.0,120.7 468.7,118.7 477.3,116.7 486.0,114.7 494.7,112.7 503.3,110.7 512.0,108.7 520.7,106.7 529.3,104.7 538.0,102.7 546.7,100.7 555.3,98.7 564.0,96.7 572.7,94.7 581.3,92.7 590.0,90.7"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,234.8 78.7,232.8 87.3,230.8 96.0,228.8 104.7,226.8 113.3,224.8 122.0,222.8 130.7,220.8 139.3,218.8 148.0,216.8 156.7,214.8 165.3,212.8 174.0,210.8 182.7,208.8 191.3,206.8 200.0,204.8 208.7,202.8 217.3,200.8 226.0,198.8 234.7,196.8 243.3,194.8 252.0,192.8 260.7,190.8 269.3,188.8 278.0,186.8 286.7,184.8 295.3,182.8 304.0,180.8 312.7,178.8 321.3,176.8 330.0,174.8 338.7,172.8 347.3,170.8 356.0,168.8 364.7,166.8 373.3,164.8 382.0,162.8 390.7,160.8 399.3,158.8 408.0,156.8 416.7,154.8 425.3,152.8 434.0,150.8 442.7,148.8 451.3,146.8 460.0,144.8 468.7,142.8 477.3,140.8 486.0,138.8 494.7,136.8 503.3,134.8 512.0,132.8 520.7,130.8 529.3,128.8 538.0,126.8 546.7,124.8 555.3,122.8 564.0,120.8 572.7,118.8 581.3,116.8 590.0,114.8"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,186.6 78.7,184.6 87.3,182.6 96.0,180.6 104.7,178.6 113.3,176.6 122.0,174.6 130.7,172.6 139.3,170.6 148.0,168.6 156.7,166.6 165.3,164.6 174.0,162.6 182.7,160.6 191.3,158.6 200.0,156.6 208.7,154.6 217.3,152.6 226.0,150.6 234.7,148.6 243.3,146.6 252.0,144.6 260.7,142.6 269.3,140.6 278.0,138.6 286.7,136.6 295.3,134.6 304.0,132.6 312.7,130.6 321.3,128.6 330.0,126.6 338.7,124.6 347.3,122.6 356.0,120.6 364.7,118.6 373.3,116.6 382.0,114.6 390.7,112.6 399.3,110.6 408.0,108.6 416.7,106.6 425.3,104.6 434.0,102.6 442.7,100.6 451.3,98.6 460.0,96.6 468.7,94.6 477.3,92.6 486.0,90.6 494.7,88.6 503.3,86.6 512.0,84.6 520.7,82.6 529.3,80.6 538.0,78.6 546.7,76.6 555.3,74.6 564.0,72.6 572.7,70.6 581.3,68.6 590.0,66.6"/><polyline fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4" points="70.0,260.0 78.7,260.0 87.3,260.0 96.0,260.0 104.7,260.0 113.3,260.0 122.0,260.0 130.7,260.0 139.3,260.0 148.0,260.0 156.7,260.0 165.3,260.0 174.0,260.0 182.7,260.0 191.3,260.0 200.0,260.0 208.7,260.0 217.3,260.0 226.0,260.0 234.7,260.0 243.3,260.0 252.0,260.0 260.7,260.0 269.3,260.0 278.0,260.0 286.7,260.0 295.3,260.0 304.0,260.0 312.7,260.0 321.3,260.0 330.0,260.0 338.7,260.0 347.3,260.0 356.0,257.0 364.7,253.0 373.3,249.0 382.0,245.0 390.7,241.0 399.3,237.0 408.0,233.0 416.7,229.0 425.3,225.0 434.0,221.0 442.7,217.0 451.3,213.0 460.0,209.0 468.7,205.0 477.3,201.0 486.0,197.0 494.7,193.0 503.3,189.0 512.0,185.0 520.7,181.0 529.3,177.0 538.0,173.0"/><text x="499.3676841514082" y="206.8334084122892" text-anchor="end" style="font-size:11px;font-weight:700">24 ビット深度の最小の刻み</text><text x="174.35706516351348" y="174.15487857287047" text-anchor="start" style="font-size:11px;font-weight:700">傾き 4・ステップ 16 画素</text><text x="326.0343508180748" y="146.19607839942972" text-anchor="start" style="font-size:11px;font-weight:700">傾き 4・ステップ 4 画素</text><text x="447.1891515696514" y="158.23727822598897" text-anchor="start" style="font-size:11px;font-weight:700">傾き 1・ステップ 4 画素</text><text x="70.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="243.33333333333334" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">10</text><text x="416.6666666666667" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">100</text><text x="590.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">1000</text><text x="62" y="264.0" text-anchor="end" style="font-size:11px;font-weight:400">0.001</text><text x="62" y="224.0" text-anchor="end" style="font-size:11px;font-weight:400">0.01</text><text x="62" y="184.0" text-anchor="end" style="font-size:11px;font-weight:400">0.1</text><text x="62" y="144.0" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="62" y="104.0" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">100</text><text x="330.0" y="298" text-anchor="middle" style="font-size:12px;font-weight:400">視線方向の距離 z (m、対数)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">必要な厚み(m、対数)</text></svg>

傾き 4・4 画素ステップなら 50 m 先で T が 0.855 m、200 m 先で 3.4 m と遠景ほど厚みが大きくなります。1000 m では 17 m と非現実的な値になるので、上限（`gMaxThickness`）で切ります。レイがほぼ真っ直ぐ奥へ向かう場合（傾きが無限大に近づく）は、どんな有限の T でも足りません。画面の端から奥へ抜けるレイは無理に当たりを探さずフォールバックに任せます。

## 深度の精度が T の下限になる {#precision}

深度バッファの値は量子化されています。T が深さの最小の刻みより小さいと受理するかどうかが量子化の誤差で決まり、ノイズになります。near = 0.1 m・far = 1000 m で、最下位ビット 1 つぶんの深さの差を数えました。

- 標準 Z（24 ビット固定小数点）: 10 m で 0.00006 m、100 m で 0.00596 m、300 m で 0.05365 m、500 m で 0.14904 m
- 反転 Z（32 ビット浮動小数点）: 10 m で 0.0000009 m、100 m で 0.0000058 m、300 m で 0.0000131 m、500 m で 0.0000182 m

標準 Z は遠くで急に粗くなり 500 m では 0.149 m の刻みです。T を 0.1 m にすると、500 m 先では受理が運で決まります。反転 Z の float は同じ距離で刻みが 4 桁ほど細かく、T の下限は問題になりません。図 3 の破線がこの刻みで標準 Z では、距離に応じた T の曲線がこの破線より下に入るならその距離では T を持ち上げる必要があります。コードの `gMinThickness` はこの刻みより大きな値にします。

## 裏面の深度で測る {#back-depth}

推定をやめて厚みを測る方法もあります。物体の裏面だけを別の深度テクスチャへ描きます（背面を描く、前面をカリングする）。画素ごとに `厚み = 裏 − 表` が分かるので、レイが表の面と裏の面のあいだにいるあいだは、物の内側にいると言えます。

高さ 10.0 m に表、10.6 m に裏がある箱で、定数の T = 0.25 m と裏面の深度を比べました。

- レイの深さ 9.9 m: どちらも外れ（表の手前）
- 10.1 m: どちらも当たり
- 10.5 m: 定数の T は外れ裏面は当たり（箱の中なのに T が足りない）
- 10.7 m: どちらも外れ（裏の面を越えた）
- 11.5 m: どちらも外れ

定数の T は箱が 0.6 m の厚みなのに 0.25 m で打ち切るので、10.5 m で取りこぼします。裏面を使えば箱の厚みそのままに判定できます。代償は裏面を描く追加の描画パスと深度テクスチャ 1 枚ぶんの帯域です。裏面が 1 層しか取れないので、凹んだ物や重なった物では一番手前の裏面までしか分かりません。凹んだ物の奥の裏面は手前の面に隠れて描かれないからです。

## 偽の当たりを減らす {#reduce}

### 法線で裏からの当たりを外す {#normal}

当たった画素の法線がレイと同じ向き（`dot(n, ray_dir) > 0`）ならレイは面の裏側から入っています。表を向いた面にレイが当たるなら法線とレイは反対向きのはずです。これで柱の裏に回り込んだ偽の当たりを一部外せます。

### 縁の信頼度を下げる {#edge}

深度の不連続（物の縁）ではレイがどちらの面に当たったのかが決まりません。隣の画素との深さの比が `gEdgeDepthRatio` を超えたら縁と見なし、信頼度を半分にします。比で見るのは遠くほど深さの絶対値が大きく、差も大きく出るためです。

### 受理の中の位置で信頼度を付ける {#confidence}

`diff` が 0 に近いほど表の面のすぐ奥で、確実です。T に近いほど受理の端で偽の当たりかもしれません。`1 − diff / T` を信頼度にして反射の色の重みに使います。

## コード：厚みを含む当たり判定 {#code}

ここからコードを数行ずつ見ます。最初は定数とテクスチャです。

```hlsl
cbuffer ThicknessCB : register(b0) {
  float2 gScreenSize;        // 画面の幅と高さ（画素）
  float  gInvFocalPx;        // 1 / 焦点距離（画素）。垂直 FOV 60 度・高さ 1080 なら 1 / 935.3
  float  gMinThickness;      // 厚みの下限（メートル）。例: 0.05。深度の量子化より大きく取る
  float  gThicknessScale;    // 画素の大きさに掛ける倍率。例: 4〜16（ステップ幅の画素数 × 想定する傾き）
  float  gMaxThickness;      // 厚みの上限（メートル）。例: 2.0。これ以上は偽の当たりが増える
  float  gEdgeDepthRatio;    // 縁とみなす深さの比。例: 0.1（隣の画素と 10% 以上違えば縁）
  float  gUseBackDepth;      // 1 なら裏面の深度で厚みを測る。0 なら定数と距離比例の厚み
};

Texture2D<float> gFrontDepth  : register(t0);   // 表の面の線形深度（メートル）
Texture2D<float> gBackDepth   : register(t1);   // 裏の面の線形深度（メートル）。裏面だけを描いたパスの結果
Texture2D<float4> gNormal     : register(t2);   // ビュー空間の法線（xyz は -1〜1）
```

`gInvFocalPx` は画素の大きさの計算に `gMinThickness` と `gMaxThickness` は T を挟む範囲に使います。`gUseBackDepth` で裏面の深度と推定を切り替えます。

距離に比例した厚みです。

```hlsl
// 距離に比例した厚み。遠いほど 1 画素が覆う世界の大きさが増えるので、厚みも増やす。
float ScaledThickness(float scene_depth) {
  float pixel_world_size = scene_depth * gInvFocalPx;                       // その距離で 1 画素が覆う長さ（メートル）
  float t = pixel_world_size * gThicknessScale;                             // ステップ幅と傾きから決めた必要な厚み
  return clamp(t, gMinThickness, gMaxThickness);                            // 下限と上限で挟む（上限は足した）
}
```

`scene_depth * gInvFocalPx` がその距離で 1 画素が覆う世界の長さです。これにステップ幅と傾きから決めた倍率を掛け下限と上限で挟みます。上限は足した処理です。

縁の検出です。

```hlsl
// 深度の不連続（物の縁）かどうか。隣の 4 画素のどれかと深さが大きく違えば縁。
bool IsDepthEdge(int2 px, float depth) {
  const int2 offsets[4] = {int2(1, 0), int2(-1, 0), int2(0, 1), int2(0, -1)};
  [unroll] for (int i = 0; i < 4; ++i) {
    int2 q = clamp(px + offsets[i], int2(0, 0), int2(gScreenSize) - 1);     // 画面の端は端の値で代用（足した）
    float neighbor = gFrontDepth.Load(int3(q, 0));
    if (abs(neighbor - depth) > gEdgeDepthRatio * depth) return true;       // 比で見る: 遠くでは差が大きくなるため
  }
  return false;
}
```

上下左右の 4 画素のどれかと深さが `gEdgeDepthRatio` の比以上違えば縁です。画面の端は端の値で代用しています（足した処理です）。

1 つの標本点の判定です。

```hlsl
// 1 つの標本点の当たり判定。ray_depth はレイ上の点の線形深度、ray_dir_vs はビュー空間の反射方向。
bool ThicknessHit(int2 px, float ray_depth, float3 ray_dir_vs, out float confidence) {
  confidence = 0.0;
  float front = gFrontDepth.Load(int3(px, 0));                              // その画素の表の面の深さ
  float diff = ray_depth - front;                                           // 正なら、レイは表の面より奥にいる
  if (diff <= 0.0) return false;                                            // まだ表の面に達していない

  float thickness;
  if (gUseBackDepth > 0.5) {
    float back = gBackDepth.Load(int3(px, 0));                              // 裏の面の深さ
    thickness = max(back - front, gMinThickness);                           // 実測の厚み。薄すぎる板は下限で救う（足した）
  } else {
    thickness = ScaledThickness(front);                                     // 推定の厚み
  }
  if (diff >= thickness) return false;                                      // 裏へ抜けた

  float3 n = gNormal.Load(int3(px, 0)).xyz;
  if (dot(n, ray_dir_vs) > 0.0) return false;                               // 面がレイと同じ向き = 裏から当たった。無効にする

  confidence = 1.0 - diff / thickness;                                      // 表の面に近いほど 1。厚みの限界に近いほど 0 に近づく
  if (IsDepthEdge(px, front)) confidence *= 0.5;                            // 縁では、どちらの面に当たったか不定なので信頼度を下げる
  return true;
}
```

最初の 2 行は `diff` を作り表の面の手前なら外れで打ち切ります。厚みは `gUseBackDepth` で裏面から測るか推定します。`diff >= thickness` なら裏へ抜けたので外れです。法線がレイと同じ向きなら裏から当たったので外します。最後に、信頼度を `1 − diff / thickness` で作り縁なら半分にします。

呼び出し側のマーチです。

```hlsl
// 呼び出し側: レイを一定のステップで進めて、最初に当たった点を返す（線形マーチの最小形）。
bool MarchAndHit(float3 origin_vs, float3 dir_vs, float max_dist, int steps, out int2 hit_px, out float confidence) {
  hit_px = int2(0, 0);
  confidence = 0.0;
  float step_len = max_dist / steps;                                        // 世界でのステップ幅（メートル）
  for (int i = 1; i <= steps; ++i) {
    float3 p = origin_vs + dir_vs * (step_len * i);                         // レイ上の点（ビュー空間）
    if (p.z <= 0.0) break;                                                  // カメラの後ろ: 投影できない
    float2 offset_px = float2(p.x, -p.y) / (p.z * gInvFocalPx);             // 画面中心からの画素数（Y は下向きが正なので反転）
    int2 px = int2(gScreenSize * 0.5 + offset_px);                          // 画素の座標
    if (any(px < 0) || any(px >= int2(gScreenSize))) break;                 // 画面の外: 見つからない
    float c;
    if (ThicknessHit(px, p.z, dir_vs, c)) { hit_px = px; confidence = c; return true; }
  }
  return false;
}
```

ビュー空間のレイを一定の幅で進め画素に投影して `ThicknessHit` を呼びます。カメラの後ろに出たら打ち切り画面の外に出たら打ち切ります。最初に当たった点を返す最小の形です。ステップ幅は前に見たとおり T と比べて大きすぎないようにします。

## よくあるミス {#mistakes}

??? failure "柱の後ろの景色が、柱の色に染まる"
    T が柱の厚みより大きく、`T − d` の帯を通るレイが受理されています。T を下げるか裏面の深度で測ります。

??? failure "柵や手すりの反射が、点線のように欠ける"
    ステップの深さ方向の幅 s が T より大きく、標本が受理範囲を飛び越えています。s = 0.5 m・T = 0.25 m なら受理は 50% です。ステップを細かくするか T を s 以上にします。

??? failure "遠景の反射が、ざらざらにちらつく"
    標準 Z の刻みが T より大きく、500 m で 0.149 m あります。T の下限をその距離の刻みより大きく取るか反転 Z の float 深度を使います。

??? failure "近景は直るのに、遠景の薄い物だけ消える"
    T を距離に比例させず一定にしています。50 m で 0.855 m が要るところを 0.2 m に固定すると、遠景の薄い物は受理されません。

??? failure "物の縁で、反射が引き伸ばされる"
    縁の画素は深さが不連続で、レイがどちらの面に当たったか決まりません。縁の信頼度を下げ色の重みを小さくします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 深度バッファは表の面しか持たない。`0 < diff < T` を当たりにする
    - [x] T が d より小さいと取りこぼし、大きいと `T − d` の帯が偽の当たりになる
    - [x] T は距離に比例（`z / f × 傾き × ステップ`）させ深度の刻みを下限に偽の当たりの出にくい値を上限にする
    - [x] 裏面の深度を描けば、厚みを測れる。法線と縁で偽の当たりを減らす

## C++ で数えたもの {#numbers}

```cpp
// SSR の厚み（thickness）の数字を数える。g++ -std=c++23 -Wall -Wextra
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// 1 本のレイが、物体の画素の上で s メートルずつ奥へ進みながら、深さを調べる 1 次元モデル。
// 表の面の深さを 0、裏の面の深さを d とする。標本の深さは、位相 p を一様に振って p + k s (k は整数)。
// 当たりと言うのは、表の面の奥 T 以内（0 < z < T）に標本が入ったとき。
// 本当に物体の中（0 < z < d）に標本が入ったかどうかとは別に数える。
struct Rates {
  double inside;  // 標本が物体の中に入る確率（本当の当たり）。min(d / s, 1) になるはず
  double accept;  // 標本が「表の面の奥 T 以内」に入る確率。min(T / s, 1) になるはず
};

Rates Simulate(double d, double T, double s) {
  const int n = 20000;
  int in_true = 0, in_acc = 0;
  for (int i = 0; i < n; ++i) {
    const double p = s * (i + 0.5) / n;  // 位相: 0〜s を一様に（表の面からの最初の標本の深さ）
    // 表の面の奥へ入った最初の標本は z = p。次は p + s、... と進む。
    bool inside = false, accept = false;
    for (double z = p; z < 3.0 * std::max(T, d) + 3.0 * s; z += s) {
      if (z > 0.0 && z < d) inside = true;
      if (z > 0.0 && z < T) accept = true;
    }
    in_true += inside;
    in_acc += accept;
  }
  Rates r;
  r.inside = static_cast<double>(in_true) / n;
  r.accept = static_cast<double>(in_acc) / n;
  return r;
}

int main() {
  const double ds[] = {0.05, 0.3, 2.0};
  const double Ts[] = {0.05, 0.1, 0.25, 0.5, 1.0, 2.0};
  for (double s : {0.5, 0.1}) {
    std::printf("-- ray depth step s = %.1f m per sample: P(sample inside object) / P(sample accepted by T) / false band width max(T-d,0)\n", s);
    for (double d : ds) {
      for (double T : Ts) {
        const Rates r = Simulate(d, T, s);
        std::printf("d = %.2f m, T = %4.2f m: inside %5.1f%%, accepted %5.1f%%, false band %.2f m\n", d, T, 100 * r.inside, 100 * r.accept, std::max(T - d, 0.0));
      }
    }
  }

  std::printf("-- pixel world size (fov 60 deg vertical, 1080 px)\n");
  const double f = 540.0 / std::tan(30.0 * 3.14159265358979323846 / 180.0);   // 焦点距離（画素）
  std::printf("focal length = %.1f px\n", f);
  const double zs[] = {2, 10, 50, 200, 1000};
  for (double z : zs) {
    const double pws = z / f;
    std::printf("z = %6.0f m: pixel size %.4f m; T for slope 1, step 4 px = %.3f m; slope 4, step 4 px = %.3f m; slope 4, step 16 px = %.3f m\n",
                z, pws, pws * 1 * 4, pws * 4 * 4, pws * 4 * 16);
  }

  std::printf("-- depth buffer resolution (near 0.1, far 1000)\n");
  const double n = 0.1, fa = 1000.0;
  const double zq[] = {1, 10, 100, 300, 500, 800};
  for (double z : zq) {
    // 標準 Z（24 ビット固定小数点）: d = f (z - n) / (z (f - n))。最下位ビット 1 つ分の深さの差。
    const double d0 = fa * (z - n) / (z * (fa - n));
    const double step = 1.0 / 16777215.0;
    const double d1 = std::min(1.0, d0 + step);
    const double z1 = fa * n / (fa - d1 * (fa - n));          // 逆変換: z = f n / (f - d (f - n))
    // 反転 Z（32 ビット浮動小数点）: d = n (f - z) / (z (f - n))。float の次の値までの差。
    const double r0 = n * (fa - z) / (z * (fa - n));
    const float rf = static_cast<float>(r0);
    const float rf2 = std::nextafterf(rf, 0.0f);              // 小さくなる = 奥へ
    const double zr1 = n * fa / (n + rf2 * (fa - n));          // 逆変換: z = n f / (n + d (f - n))
    const double zr0 = n * fa / (n + static_cast<double>(rf) * (fa - n));
    std::printf("z = %6.0f m: standard 24-bit step %.5f m; reversed float32 step %.7f m\n", z, z1 - z, zr1 - zr0);
  }

  std::printf("-- back-face thickness of a box (front 10.0 m, back 10.6 m): hit range vs T\n");
  const double fz = 10.0, bz = 10.6;
  for (double z : {9.9, 10.1, 10.5, 10.7, 11.5}) {
    const bool constant_hit = (z > fz) && (z - fz < 0.25);
    const bool back_hit = (z > fz) && (z < bz);
    std::printf("ray depth %.1f: constant T = 0.25 -> %s, back-face -> %s\n", z, constant_hit ? "hit" : "miss", back_hit ? "hit" : "miss");
  }
  return 0;
}
```

```text title="実行結果"
-- ray depth step s = 0.5 m per sample: P(sample inside object) / P(sample accepted by T) / false band width max(T-d,0)
d = 0.05 m, T = 0.05 m: inside  10.0%, accepted  10.0%, false band 0.00 m
d = 0.05 m, T = 0.10 m: inside  10.0%, accepted  20.0%, false band 0.05 m
d = 0.05 m, T = 0.25 m: inside  10.0%, accepted  50.0%, false band 0.20 m
d = 0.05 m, T = 0.50 m: inside  10.0%, accepted 100.0%, false band 0.45 m
d = 0.05 m, T = 1.00 m: inside  10.0%, accepted 100.0%, false band 0.95 m
d = 0.05 m, T = 2.00 m: inside  10.0%, accepted 100.0%, false band 1.95 m
d = 0.30 m, T = 0.05 m: inside  60.0%, accepted  10.0%, false band 0.00 m
d = 0.30 m, T = 0.10 m: inside  60.0%, accepted  20.0%, false band 0.00 m
d = 0.30 m, T = 0.25 m: inside  60.0%, accepted  50.0%, false band 0.00 m
d = 0.30 m, T = 0.50 m: inside  60.0%, accepted 100.0%, false band 0.20 m
d = 0.30 m, T = 1.00 m: inside  60.0%, accepted 100.0%, false band 0.70 m
d = 0.30 m, T = 2.00 m: inside  60.0%, accepted 100.0%, false band 1.70 m
d = 2.00 m, T = 0.05 m: inside 100.0%, accepted  10.0%, false band 0.00 m
d = 2.00 m, T = 0.10 m: inside 100.0%, accepted  20.0%, false band 0.00 m
d = 2.00 m, T = 0.25 m: inside 100.0%, accepted  50.0%, false band 0.00 m
d = 2.00 m, T = 0.50 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 2.00 m, T = 1.00 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 2.00 m, T = 2.00 m: inside 100.0%, accepted 100.0%, false band 0.00 m
-- ray depth step s = 0.1 m per sample: P(sample inside object) / P(sample accepted by T) / false band width max(T-d,0)
d = 0.05 m, T = 0.05 m: inside  50.0%, accepted  50.0%, false band 0.00 m
d = 0.05 m, T = 0.10 m: inside  50.0%, accepted 100.0%, false band 0.05 m
d = 0.05 m, T = 0.25 m: inside  50.0%, accepted 100.0%, false band 0.20 m
d = 0.05 m, T = 0.50 m: inside  50.0%, accepted 100.0%, false band 0.45 m
d = 0.05 m, T = 1.00 m: inside  50.0%, accepted 100.0%, false band 0.95 m
d = 0.05 m, T = 2.00 m: inside  50.0%, accepted 100.0%, false band 1.95 m
d = 0.30 m, T = 0.05 m: inside 100.0%, accepted  50.0%, false band 0.00 m
d = 0.30 m, T = 0.10 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 0.30 m, T = 0.25 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 0.30 m, T = 0.50 m: inside 100.0%, accepted 100.0%, false band 0.20 m
d = 0.30 m, T = 1.00 m: inside 100.0%, accepted 100.0%, false band 0.70 m
d = 0.30 m, T = 2.00 m: inside 100.0%, accepted 100.0%, false band 1.70 m
d = 2.00 m, T = 0.05 m: inside 100.0%, accepted  50.0%, false band 0.00 m
d = 2.00 m, T = 0.10 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 2.00 m, T = 0.25 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 2.00 m, T = 0.50 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 2.00 m, T = 1.00 m: inside 100.0%, accepted 100.0%, false band 0.00 m
d = 2.00 m, T = 2.00 m: inside 100.0%, accepted 100.0%, false band 0.00 m
-- pixel world size (fov 60 deg vertical, 1080 px)
focal length = 935.3 px
z =      2 m: pixel size 0.0021 m; T for slope 1, step 4 px = 0.009 m; slope 4, step 4 px = 0.034 m; slope 4, step 16 px = 0.137 m
z =     10 m: pixel size 0.0107 m; T for slope 1, step 4 px = 0.043 m; slope 4, step 4 px = 0.171 m; slope 4, step 16 px = 0.684 m
z =     50 m: pixel size 0.0535 m; T for slope 1, step 4 px = 0.214 m; slope 4, step 4 px = 0.855 m; slope 4, step 16 px = 3.421 m
z =    200 m: pixel size 0.2138 m; T for slope 1, step 4 px = 0.855 m; slope 4, step 4 px = 3.421 m; slope 4, step 16 px = 13.685 m
z =   1000 m: pixel size 1.0692 m; T for slope 1, step 4 px = 4.277 m; slope 4, step 4 px = 17.107 m; slope 4, step 16 px = 68.427 m
-- depth buffer resolution (near 0.1, far 1000)
z =      1 m: standard 24-bit step 0.00000 m; reversed float32 step 0.0000001 m
z =     10 m: standard 24-bit step 0.00006 m; reversed float32 step 0.0000009 m
z =    100 m: standard 24-bit step 0.00596 m; reversed float32 step 0.0000058 m
z =    300 m: standard 24-bit step 0.05365 m; reversed float32 step 0.0000131 m
z =    500 m: standard 24-bit step 0.14904 m; reversed float32 step 0.0000182 m
z =    800 m: standard 24-bit step 0.38161 m; reversed float32 step 0.0000116 m
-- back-face thickness of a box (front 10.0 m, back 10.6 m): hit range vs T
ray depth 9.9: constant T = 0.25 -> miss, back-face -> miss
ray depth 10.1: constant T = 0.25 -> hit, back-face -> hit
ray depth 10.5: constant T = 0.25 -> miss, back-face -> hit
ray depth 10.7: constant T = 0.25 -> miss, back-face -> miss
ray depth 11.5: constant T = 0.25 -> miss, back-face -> miss
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。厚みの式、ステップと T の関係、深度の刻みの計算は一般的な考え方を自分で導いたものです。

- Morgan McGuire, Michael Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Tomasz Stachowiak, Yasin Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Yasin Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, 2014
- Tomas Akenine-Möller ほか, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ {#related}

- [SSR Basics](index.md)
- [Linear Marching](linear-march.md)
- [Artifacts and Evaluation](artifacts.md)
- [Hi-Z SSR](../ssr-hiz.md)
