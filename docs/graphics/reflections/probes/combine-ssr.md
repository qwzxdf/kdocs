---
title: Combining with SSR
tags:
  - 描画
---

# Combining with SSR

SSR は画面に写っている物だけを映せて、反射プローブは画面の外も映せますが、細かさがありません。どちらか一方だけで反射を作ると、SSR は画面の端とレイが外れた場所で穴が開きプローブは足元の接地した映り込みがぼやけます。そこで、SSR が当たった所は SSR、外れた所はプローブ、という順に重ねます。このページではその重ね方を決める信頼度、色と露出のつながり 1 フレーム遅れの影響、3 段階のフォールバックを数字で確かめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。旧ページは同じ節が 2 回重なっていたので 1 つにまとめ「カメラに向かう反射」の係数の符号が逆に読める式を、`R・V` の式に直しました。下の参考資料は**今回は読んでいません**。信頼度の各係数の値（0.75、0.6 など）は自分で決めた一例で、資料の値ではありません。

!!! tip "ポイント"
    - 合成は `結果 = SSR × a + プローブ × (1 − a) × w + 空 × (1 − a) × (1 − w)` です。a は SSR の信頼度、w はローカル プローブの有効な割合です。3 つの重みの合計は a と w のどの組み合わせでも 1 です（確かめた最大の誤差は 2.2e-16）。
    - 信頼度は 4 つの要因の積です。画面の端、レイの長さカメラへ戻る向き粗さのどれかが 0 ならその画素はプローブに任せます。
    - 端のフェードは中心から 0.75 より外側で効きます。1920 画素の横幅なら左右それぞれ 240 画素（全体の 25%）がフェードの帯になります。
    - 色の差が 20% あるときフェードの幅が 1 画素だと 1 画素で 20% 変わり、240 画素だと 1 画素あたり 0.083% です。継ぎ目を目立たなくするには幅を広げます。
    - SSR が前フレームの色を再投影せずに読むとカメラが毎秒 90 度で回るとき、1 フレームで画面の中心が 24.5 画素ずれます。

!!! info "このページを読む前に"
    - [Reflection Probes](index.md)（このセクション全体の地図と、読む順番）
    - [SSR Fallback and Compositing](../ssr-fallback.md)（SSR 側から見た合成）

## 得意と不得意が正反対 {#why}

SSR とプローブは得意な所が逆です。

SSR は今のフレームの画面から色を拾うので、動く物も映ります。近くの細かい反射（足元の映り込み接地部）も画面の実際のジオメトリから拾うので正確です。ただし、画面に写っていない物は映せず画面の端では反射が欠けます。遠景はレイを長く進めなければならず重くなります。

プローブはあらかじめ撮ったキューブ マップを引くだけなので安く、画面の外も映ります。ただし、位置が 1 点なので近くの反射は視差でずれ解像度も粗くなります。ベイクしたプローブには動く物は映りません。

この対応がそのまま合成の順番になります。SSR を優先し信頼できない所をプローブで埋めて、プローブも届かない所は空で埋めます。

## 3 段階のフォールバック {#three-tier}

重みは 3 段階です。

1. SSR: 信頼度 a。画面内で近距離の最も正確な反射です。
2. ローカル プローブ: 残りの `(1 − a)` のうちプローブが有効な割合 w。
3. 空: 残りの `(1 − a)(1 − w)`。プローブの範囲外では空のキューブ マップを使います。

重みの合計は `a + (1 − a)w + (1 − a)(1 − w) = a + (1 − a) = 1` でどの組み合わせでも 1 です。a と w を 0.1 刻みで全部試した最大の誤差は、2.2e-16 でした。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="3 段階の重み"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">フォールバックの重み</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="100" y="60.0" width="60" height="190.0" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><text x="130" y="159.0" text-anchor="middle" style="font-size:11px;font-weight:700">1.00</text><text x="130" y="266" text-anchor="middle" style="font-size:11px;font-weight:400">a=1</text><text x="130" y="280" text-anchor="middle" style="font-size:11px;font-weight:400">w=1</text><rect x="198" y="155.0" width="60" height="95.0" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><text x="228" y="206.5" text-anchor="middle" style="font-size:11px;font-weight:700">0.50</text><rect x="198" y="60.0" width="60" height="95.0" fill="rgba(229,170,40,0.60)" stroke="currentColor"/><text x="228" y="111.5" text-anchor="middle" style="font-size:11px;font-weight:700">0.50</text><text x="228" y="266" text-anchor="middle" style="font-size:11px;font-weight:400">a=0.5</text><text x="228" y="280" text-anchor="middle" style="font-size:11px;font-weight:400">w=1</text><rect x="296" y="155.0" width="60" height="95.0" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><text x="326" y="206.5" text-anchor="middle" style="font-size:11px;font-weight:700">0.50</text><rect x="296" y="60.0" width="60" height="95.0" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="326" y="111.5" text-anchor="middle" style="font-size:11px;font-weight:700">0.50</text><text x="326" y="266" text-anchor="middle" style="font-size:11px;font-weight:400">a=0.5</text><text x="326" y="280" text-anchor="middle" style="font-size:11px;font-weight:400">w=0</text><rect x="394" y="60.0" width="60" height="190.0" fill="rgba(229,170,40,0.60)" stroke="currentColor"/><text x="424" y="159.0" text-anchor="middle" style="font-size:11px;font-weight:700">1.00</text><text x="424" y="266" text-anchor="middle" style="font-size:11px;font-weight:400">a=0</text><text x="424" y="280" text-anchor="middle" style="font-size:11px;font-weight:400">w=1</text><rect x="492" y="60.0" width="60" height="190.0" fill="rgba(46,158,91,0.55)" stroke="currentColor"/><text x="522" y="159.0" text-anchor="middle" style="font-size:11px;font-weight:700">1.00</text><text x="522" y="266" text-anchor="middle" style="font-size:11px;font-weight:400">a=0</text><text x="522" y="280" text-anchor="middle" style="font-size:11px;font-weight:400">w=0</text><text x="586" y="66" text-anchor="end" style="font-size:12px;font-weight:700">青: SSR  黄: プローブ  緑: 空</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">重みの合計は常に 1</text></svg>

- a = 1: SSR だけ。プローブも空も使いません。
- a = 0.5、w = 1: SSR とローカル プローブが半分ずつ。
- a = 0.5、w = 0: SSR と空が半分ずつ。プローブの範囲外なのでプローブは使いません。
- a = 0、w = 1: プローブだけ。SSR が外れた画素の最低限の反射です。
- a = 0、w = 0: 空だけ。屋内でプローブが無い場所に空が写り込むときの危険な状態です（屋内の床が空を映します）。

重みの合計が 1 でエネルギーが増えも減りもしない、という点がこの式の要です。SSR が外れた画素が黒く抜けることは、プローブと空が受け止めるので、ありません。

## 信頼度の決め方 {#confidence}

信頼度 a は SSR の苦手な条件で下がる 4 つの係数の積です。

### 画面の端 {#edge}

レイが当たった点が画面の端に近いとそのすぐ外側の情報が欠けています。当たった点の uv の中心からの距離（0〜1）を `d` として、`1 − saturate((d − 0.75) / 0.25)` で下げます。

- uv.x = 0.875 まで: 係数 1.000
- 0.900: 0.800
- 0.950: 0.400
- 0.990: 0.080
- 1.000: 0.000

フェードの帯は uv = 0.875 から端までの 0.125 で、1920 画素の横なら片側 240 画素、1080 画素の縦なら 135 画素です。左右合わせると画面の幅の 25% がフェード中ということになります。

### レイの長さ {#distance}

レイが長いほど画面の遠くを拾うことになり精度も落ちます。`1 − saturate(長さ / 最大距離)` で下げます。最大距離 50 m なら 5 m で 0.90、25 m で 0.50、45 m で 0.10 です。

### カメラへ戻る向き {#facing}

反射がカメラの方へ戻る向き（`R・V` が 1 に近い。V は面からカメラへ向かう向き）だと画面に写っていない、カメラの後ろ側を見ることになります。`R・V` が 0.6 以下なら係数は 1、0.8 で 0.50、0.9 で 0.25、1.0 で 0 です（0.6 は一例で、足した式です）。旧ページの `saturate(dot(R, -V) * 4.0 + 1.0)` は符号の取り方次第で、逆向きの反射を弱めてしまう式だったので、この式に置き換えました。

### 粗さ {#roughness}

粗い面は反射が広い方向から来るので、1 本のレイでは足りません。粗さ 0.6 以下は係数 1、0.8 で 0.50、1.0 で 0 です（これも一例です）。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="信頼度の要因"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">要因ごとの信頼度</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5"  points="70.0,60.0 75.2,60.0 80.4,60.0 85.6,60.0 90.8,60.0 96.0,60.0 101.2,60.0 106.4,60.0 111.6,60.0 116.8,60.0 122.0,60.0 127.2,60.0 132.4,60.0 137.6,60.0 142.8,60.0 148.0,60.0 153.2,60.0 158.4,60.0 163.6,60.0 168.8,60.0 174.0,60.0 179.2,60.0 184.4,60.0 189.6,60.0 194.8,60.0 200.0,60.0 205.2,60.0 210.4,60.0 215.6,60.0 220.8,60.0 226.0,60.0 231.2,60.0 236.4,60.0 241.6,60.0 246.8,60.0 252.0,60.0 257.2,60.0 262.4,60.0 267.6,60.0 272.8,60.0 278.0,60.0 283.2,60.0 288.4,60.0 293.6,60.0 298.8,60.0 304.0,60.0 309.2,60.0 314.4,60.0 319.6,60.0 324.8,60.0 330.0,60.0 335.2,60.0 340.4,60.0 345.6,60.0 350.8,60.0 356.0,60.0 361.2,60.0 366.4,60.0 371.6,60.0 376.8,60.0 382.0,60.0 387.2,60.0 392.4,60.0 397.6,60.0 402.8,60.0 408.0,60.0 413.2,60.0 418.4,60.0 423.6,60.0 428.8,60.0 434.0,60.0 439.2,60.0 444.4,60.0 449.6,60.0 454.8,60.0 460.0,60.0 465.2,67.6 470.4,75.2 475.6,82.8 480.8,90.4 486.0,98.0 491.2,105.6 496.4,113.2 501.6,120.8 506.8,128.4 512.0,136.0 517.2,143.6 522.4,151.2 527.6,158.8 532.8,166.4 538.0,174.0 543.2,181.6 548.4,189.2 553.6,196.8 558.8,204.4 564.0,212.0 569.2,219.6 574.4,227.2 579.6,234.8 584.8,242.4 590.0,250.0"/><text x="464.0" y="52" text-anchor="start" style="font-size:11px;font-weight:700">端のフェード(中心からの距離 0.75〜1)</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 4" points="70.0,60.0 75.2,61.9 80.4,63.8 85.6,65.7 90.8,67.6 96.0,69.5 101.2,71.4 106.4,73.3 111.6,75.2 116.8,77.1 122.0,79.0 127.2,80.9 132.4,82.8 137.6,84.7 142.8,86.6 148.0,88.5 153.2,90.4 158.4,92.3 163.6,94.2 168.8,96.1 174.0,98.0 179.2,99.9 184.4,101.8 189.6,103.7 194.8,105.6 200.0,107.5 205.2,109.4 210.4,111.3 215.6,113.2 220.8,115.1 226.0,117.0 231.2,118.9 236.4,120.8 241.6,122.7 246.8,124.6 252.0,126.5 257.2,128.4 262.4,130.3 267.6,132.2 272.8,134.1 278.0,136.0 283.2,137.9 288.4,139.8 293.6,141.7 298.8,143.6 304.0,145.5 309.2,147.4 314.4,149.3 319.6,151.2 324.8,153.1 330.0,155.0 335.2,156.9 340.4,158.8 345.6,160.7 350.8,162.6 356.0,164.5 361.2,166.4 366.4,168.3 371.6,170.2 376.8,172.1 382.0,174.0 387.2,175.9 392.4,177.8 397.6,179.7 402.8,181.6 408.0,183.5 413.2,185.4 418.4,187.3 423.6,189.2 428.8,191.1 434.0,193.0 439.2,194.9 444.4,196.8 449.6,198.7 454.8,200.6 460.0,202.5 465.2,204.4 470.4,206.3 475.6,208.2 480.8,210.1 486.0,212.0 491.2,213.9 496.4,215.8 501.6,217.7 506.8,219.6 512.0,221.5 517.2,223.4 522.4,225.3 527.6,227.2 532.8,229.1 538.0,231.0 543.2,232.9 548.4,234.8 553.6,236.7 558.8,238.6 564.0,240.5 569.2,242.4 574.4,244.3 579.6,246.2 584.8,248.1 590.0,250.0"/><text x="122.0" y="95.0" text-anchor="start" style="font-size:11px;font-weight:700">距離のフェード(0〜50 m)</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5"  points="70.0,60.0 75.2,60.0 80.4,60.0 85.6,60.0 90.8,60.0 96.0,60.0 101.2,60.0 106.4,60.0 111.6,60.0 116.8,60.0 122.0,60.0 127.2,60.0 132.4,60.0 137.6,60.0 142.8,60.0 148.0,60.0 153.2,60.0 158.4,60.0 163.6,60.0 168.8,60.0 174.0,60.0 179.2,60.0 184.4,60.0 189.6,60.0 194.8,60.0 200.0,60.0 205.2,60.0 210.4,60.0 215.6,60.0 220.8,60.0 226.0,60.0 231.2,60.0 236.4,60.0 241.6,60.0 246.8,60.0 252.0,60.0 257.2,60.0 262.4,60.0 267.6,60.0 272.8,60.0 278.0,60.0 283.2,60.0 288.4,60.0 293.6,60.0 298.8,60.0 304.0,60.0 309.2,60.0 314.4,60.0 319.6,60.0 324.8,60.0 330.0,60.0 335.2,60.0 340.4,60.0 345.6,60.0 350.8,60.0 356.0,60.0 361.2,60.0 366.4,60.0 371.6,60.0 376.8,60.0 382.0,60.0 387.2,64.8 392.4,69.5 397.6,74.2 402.8,79.0 408.0,83.8 413.2,88.5 418.4,93.3 423.6,98.0 428.8,102.7 434.0,107.5 439.2,112.2 444.4,117.0 449.6,121.8 454.8,126.5 460.0,131.2 465.2,136.0 470.4,140.8 475.6,145.5 480.8,150.2 486.0,155.0 491.2,159.8 496.4,164.5 501.6,169.2 506.8,174.0 512.0,178.8 517.2,183.5 522.4,188.2 527.6,193.0 532.8,197.8 538.0,202.5 543.2,207.3 548.4,212.0 553.6,216.8 558.8,221.5 564.0,226.2 569.2,231.0 574.4,235.8 579.6,240.5 584.8,245.2 590.0,250.0"/><text x="356.0" y="147.0" text-anchor="end" style="font-size:11px;font-weight:700">粗さ・R·V のフェード(0.6〜1)</text><text x="70" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="200.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="330.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="460.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="590.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="330.0" y="288" text-anchor="middle" style="font-size:11px;font-weight:400">横軸: 各要因の正規化した値(端: 中心からの距離、距離: 長さ / 50 m、粗さ・R·V: そのまま)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">信頼度</text></svg>

### 4 つの積 {#product}

4 つを掛けた例です。

- 床の鏡面（画面の中央・8 m・向き -0.4・粗さ 0.1）: 1.00 × 0.84 × 1.00 × 1.00 = 0.840
- 画面の端の濡れた床（uv.x = 0.97）: 0.24 × 0.84 = 0.202
- 遠い反射（40 m）: 0.20
- カメラへ戻る反射（R・V = 0.9）: 0.84 × 0.25 = 0.210
- 粗い金属（粗さ 0.8）: 0.84 × 0.50 = 0.420

どれも 0.2〜0.8 台で、1 つの係数が下がるだけでプローブの重みが大きく増えます。

## 継ぎ目と色のつながり {#seam}

SSR とプローブは別の方法で作った色なので、同じ物を映しても少し違います。信頼度が変わる所で反射の色が段になって見えることがあります。

フェードの幅を変えて 20% の色の差が、1 画素あたり何%の変化になるかを数えました。

- 幅 1 画素: 1 画素で 20.000%
- 8 画素: 2.500%
- 64 画素: 0.312%
- 240 画素: 0.083%

端のフェードの 240 画素は継ぎ目が見えにくい幅です。信頼度を粗さや向きで下げるときは急に落とさず広い範囲で下げます。

### 露出のずれ {#exposure}

SSR は前フレームの色を読むことが多く、その色は前フレームの露出で撮られています。プローブは今の露出で読みます。露出が自動調整で動いている最中はこの 2 つがずれます。1 段（2 倍）の露出のジャンプを毎フレーム `速度` の割合で追うとして、最初の 1 フレームで動く量を数えると、速度 0.02 で 0.020 段（比 1.014）、0.05 で 0.050 段（比 1.035）、0.10 で 0.100 段（比 1.072）でした。1 フレームの差は数%で目立ちにくいのですが、14 フレーム経ってもジャンプが 0.754 段（速度 0.02）、0.488 段（0.05）、0.229 段（0.10）残るので、遅い適応のあいだ継ぎ目に色の段が出ます。トーン マッピング前の HDR で、露出を掛ける前の値を読み今の露出に合わせる（`g_exposure_ratio`）のが確実です。

### 1 フレーム遅れ {#lag}

SSR が前フレームの色を再投影せずにそのまま読むとカメラが動くと反射がずれます。60 fps・垂直 FOV 60 度・1080p で、画面の中心のずれを数えました。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="1 フレームの遅れ"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">回転でのずれ</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="110" y="234.4" width="70" height="15.6" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="145" y="228.42000000000002" text-anchor="middle" style="font-size:12px;font-weight:700">8.2 px</text><text x="145" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30 °/s</text><rect x="230" y="203.4" width="70" height="46.6" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="265" y="197.45" text-anchor="middle" style="font-size:12px;font-weight:700">24.5 px</text><text x="265" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90 °/s</text><rect x="350" y="156.9" width="70" height="93.1" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="385" y="150.9" text-anchor="middle" style="font-size:12px;font-weight:700">49.0 px</text><text x="385" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">180 °/s</text><rect x="470" y="63.2" width="70" height="186.8" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="505" y="57.22999999999999" text-anchor="middle" style="font-size:12px;font-weight:700">98.3 px</text><text x="505" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">360 °/s</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">50</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">100</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">前フレームの色を再投影しないときのずれ(画面の中心、60 fps、1080p)</text><text x="330.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">カメラの回転の速さ</text></svg>

- 毎秒 30 度: 0.50 度/フレーム、8.2 画素
- 90 度: 1.50 度/フレーム、24.5 画素
- 180 度: 3.00 度/フレーム、49.0 画素
- 360 度: 6.00 度/フレーム、98.3 画素

当たった点の位置を速度バッファで前フレームの位置に戻して色を読めば、このずれはほぼなくなります。ただし、反射に映る物自体が動いているならその物の速度は別に必要です。

## 合成パスの帯域 {#bandwidth}

合成パスは全画面で SSR の結果（RGBA16F、8 バイト）、プローブの結果（8 バイト）、前フレームの色（8 バイト）を読み結果（8 バイト）を書きます。1 画素あたり 32 バイトで、1080p なら 66.4 MB/フレーム、60 fps で 3.98 GB/s です。ほかのポストの全画面パスと同じ規模なので、SSR のレイマーチやプローブの視差補正に比べれば小さなコストです。

## コード：合成パス {#code}

ここからコードを数行ずつ見ます。最初は定数とテクスチャです。

```hlsl
cbuffer CompositeCB : register(b0) {
  float2 g_screen_size;      // 画面の幅と高さ(画素)
  float  g_max_ssr_distance; // SSR を信頼する最大のレイの長さ(m)。例: 50
  float  g_edge_start;       // 画面の端のフェードを始める位置(中心からの距離 0〜1)。例: 0.75
  float  g_facing_start;     // カメラへ戻る反射を弱め始める R・V。例: 0.6
  float  g_rough_start;      // SSR を弱め始める粗さ。例: 0.6
  float  g_exposure_ratio;   // 今フレームの露出 / SSR が読んだ前フレームの露出(同じなら 1)
  float  g_probe_weight;     // ローカル プローブの有効な割合(範囲外へ向かって 0 に下がる)
};

Texture2D<float4> g_ssr      : register(t0);   // rgb = SSR が拾った色(前フレームの色)、a = 当たったなら 1
Texture2D<float4> g_ssr_hit  : register(t1);   // xy = 当たった点の uv、z = レイの長さ(m)、w = 使わない
Texture2D<float4> g_probe    : register(t2);   // 反射プローブを引いた結果(視差補正と粗さのミップ込み)
Texture2D<float3> g_sky      : register(t3);   // 空のキューブ マップを引いた結果(最後の砦)
Texture2D<float>  g_roughness : register(t4);  // 粗さ(知覚的な粗さ 0〜1)
```

`g_edge_start`、`g_facing_start`、`g_rough_start` は各係数が下がり始める位置で、本文の例の値（0.75、0.6、0.6）は一例です。`g_exposure_ratio` は SSR が読んだ色の露出を今の露出に合わせる倍率です。

信頼度の要因です。

```hlsl
// 画面の端で下がる信頼度。当たった点が端に近いほど、そのすぐ外側の情報が欠けている。
float EdgeFade(float2 hit_uv) {
  float d = max(abs(hit_uv.x * 2.0 - 1.0), abs(hit_uv.y * 2.0 - 1.0));    // 中心からの距離(0〜1)
  return 1.0 - saturate((d - g_edge_start) / (1.0 - g_edge_start));      // 始点まで 1、端で 0
}

// カメラの方へ戻る反射は、画面に写っていない裏側を見ることになるので弱める(R・V が 1 に近いほど)。
float FacingFade(float3 R, float3 V) {
  return 1.0 - saturate((dot(R, V) - g_facing_start) / (1.0 - g_facing_start));
}

// 4 つの要因を掛けた SSR の信頼度。どれか 1 つが 0 なら、その画素はプローブに任せる。
float SsrConfidence(float2 hit_uv, float ray_len, float3 R, float3 V, float roughness, float hit) {
  float c = hit;                                                            // 当たらなかったなら 0
  c *= EdgeFade(hit_uv);
  c *= 1.0 - saturate(ray_len / g_max_ssr_distance);                        // 遠いほど弱く(レイが長いほど精度も落ちる)
  c *= FacingFade(R, V);
  c *= 1.0 - saturate((roughness - g_rough_start) / (1.0 - g_rough_start));   // 粗いほどプローブに任せる
  return c;
}
```

`EdgeFade` は当たった点の uv から中心までの距離を使って、端で 0 になる係数を返します。`FacingFade` は `R・V` が始点を超えたら 0 へ下げます。`SsrConfidence` は当たったかどうか（`hit`）に 4 つの係数を掛けます。当たらなかった画素は最初から 0 です。

合成の本体です。

```hlsl
float4 CompositePS(float4 pos : SV_Position, float3 R : TEXCOORD0, float3 V : TEXCOORD1) : SV_Target {
  int3 p = int3(pos.xy, 0);
  float4 ssr = g_ssr.Load(p);
  float4 hit = g_ssr_hit.Load(p);
  float3 probe = g_probe.Load(p).rgb;
  float3 sky = g_sky.Load(p);
  float roughness = g_roughness.Load(p);

  float3 ssr_color = ssr.rgb * g_exposure_ratio;                            // 前フレームの色を今の露出に合わせる

  float a = SsrConfidence(hit.xy, hit.z, normalize(R), normalize(V), roughness, ssr.a);
  float w = g_probe_weight;
  // 3 段階: ① SSR、② ローカル プローブ、③ 空。重みは a + (1 - a) w + (1 - a)(1 - w) = 1。
  float3 result = ssr_color * a + probe * ((1.0 - a) * w) + sky * ((1.0 - a) * (1.0 - w));
  return float4(result, 1.0);
}
```

テクスチャを読み SSR の色に露出の倍率を掛けます。信頼度 a を作り 3 段階の式で合成します。`R` と `V` は補間で長さが変わるので、正規化して使います。

## よくあるミス {#mistakes}

??? failure "SSR が外れた所が黒くなる"
    プローブをフォールバックにしていません。信頼度 0 のときプローブか空の色が出るようにします。重みの合計が 1 なら黒く抜けることはありません。

??? failure "屋内の床が空を映してしまう"
    w = 0（プローブが無効）のとき空だけが残ります。プローブの範囲外では空ではなく、環境の平均色などに落とします。

??? failure "SSR とプローブの境目に帯が見える"
    フェードが急です。20% の色の差で幅 1 画素だと 1 画素で 20% 変わります。幅を広げます。露出の自動調整中は露出の倍率も合わせます。

??? failure "カメラを回すと反射が遅れてついてくる"
    前フレームの色を再投影していません。毎秒 90 度で 24.5 画素ずれます。速度で前フレームの位置に戻して読みます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] SSR を優先し、信頼度の低い所をプローブ、その外側を空で埋める
    - [x] 重みの合計は常に 1。黒く抜けない
    - [x] 信頼度は端・距離・向き・粗さの積。フェードは広く取る
    - [x] 前フレームの色は、再投影と露出の合わせ込みをする

## C++ で数えたもの {#numbers}

```cpp
// SSR とプローブの合成：信頼度・継ぎ目・1 フレーム遅れ・帯域の数字を数える。g++ -std=c++23 -Wall -Wextra
#include <algorithm>
#include <cmath>
#include <cstdio>

double Saturate(double x) { return std::clamp(x, 0.0, 1.0); }

// 画面の端のフェード: hit_uv の中心からの最大距離(0〜1)を 4 倍して 3 を引く。0.75 までは 1、1.0 で 0。
double EdgeFade(double u, double v) {
  const double d = std::max(std::fabs(u * 2.0 - 1.0), std::fabs(v * 2.0 - 1.0));
  return 1.0 - Saturate(d * 4.0 - 3.0);
}
double DistanceFade(double ray_len, double max_dist) { return 1.0 - Saturate(ray_len / max_dist); }
// V は「面からカメラへ向かう向き」。R がカメラの方へ戻る(R・V が 1 に近い)ほど、画面に写っていない裏側を見るので弱くする。例: 0.6 から下げ始め、1.0 で 0(足した式)。
double FacingFade(double r_dot_v) { return 1.0 - Saturate((r_dot_v - 0.6) / 0.4); }
double RoughnessFade(double rough) { return 1.0 - Saturate((rough - 0.6) / 0.4); }

int main() {
  std::printf("-- edge fade: hit uv (x, y = 0.5) -> factor, and the fade band width at 1920 px\n");
  for (double u : {0.50, 0.80, 0.875, 0.90, 0.95, 0.99, 1.00}) std::printf("u = %.3f: edge fade %.3f\n", u, EdgeFade(u, 0.5));
  std::printf("fade band: from u = 0.875 to 1.0 on each side = %.0f px of 1920, %.0f px of 1080 (vertical)\n", 0.125 * 1920, 0.125 * 1080);
  std::printf("a hit in the outer band: %.1f%% of the screen width is fading on both sides together\n", 100 * 0.25);

  std::printf("-- distance fade (max distance 50 m)\n");
  for (double len : {0.0, 5.0, 25.0, 45.0, 50.0}) std::printf("ray length %4.0f m: %.2f\n", len, DistanceFade(len, 50.0));

  std::printf("-- facing fade: dot(R, V), V = surface to camera\n");
  for (double d : {-1.0, 0.0, 0.5, 0.6, 0.8, 0.9, 1.0}) std::printf("dot(R, V) = %5.2f: factor %.2f\n", d, FacingFade(d));

  std::printf("-- roughness fade\n");
  for (double r : {0.0, 0.3, 0.6, 0.8, 1.0}) std::printf("roughness %.1f: factor %.2f\n", r, RoughnessFade(r));

  std::printf("-- combined confidence for example pixels\n");
  struct Case { const char* name; double u, v, len, rdv, rough; };
  const Case cases[] = {
      {"floor mirror, center", 0.50, 0.40, 8.0, -0.4, 0.1},
      {"wet floor near screen edge", 0.97, 0.50, 8.0, -0.4, 0.1},
      {"far reflection", 0.50, 0.40, 40.0, -0.4, 0.1},
      {"toward camera", 0.50, 0.40, 8.0, 0.9, 0.1},
      {"rough metal", 0.50, 0.40, 8.0, -0.4, 0.8},
  };
  for (const Case& c : cases) {
    const double e = EdgeFade(c.u, c.v), d = DistanceFade(c.len, 50.0), f = FacingFade(c.rdv), r = RoughnessFade(c.rough);
    std::printf("%-28s edge %.2f x dist %.2f x facing %.2f x rough %.2f = %.3f\n", c.name, e, d, f, r, e * d * f * r);
  }

  std::printf("-- three-tier blend: weights always sum to 1\n");
  double worst = 0;
  for (int i = 0; i <= 10; ++i)
    for (int j = 0; j <= 10; ++j) {
      const double a = i / 10.0, w = j / 10.0;
      worst = std::max(worst, std::fabs(a + (1 - a) * w + (1 - a) * (1 - w) - 1.0));
    }
  std::printf("max |sum - 1| over a, w in {0, 0.1, ..., 1}: %.1e\n", worst);
  for (double a : {1.0, 0.5, 0.0}) for (double w : {1.0, 0.0}) std::printf("ssr %.1f, probe weight %.1f -> weights: ssr %.2f, probe %.2f, sky %.2f\n", a, w, a, (1 - a) * w, (1 - a) * (1 - w));

  std::printf("-- seam: a color difference of 20%% between SSR and probe, fade over W pixels\n");
  for (double w : {1.0, 8.0, 64.0, 240.0}) std::printf("fade width %5.0f px: change per pixel %.4f (%.3f%% per pixel)\n", w, 0.2 / w, 20.0 / w);

  std::printf("-- exposure adaptation: SSR reads last frame's color (1 frame old)\n");
  for (double speed : {0.02, 0.05, 0.10}) {
    // 1 段(2 倍)の露出ジャンプが、毎フレーム (1 - speed) の割合で残る。1 フレームで動く量(段)と、その比。
    const double stops_first = 1.0 * speed;
    std::printf("adapt speed %.2f/frame: first frame moves %.3f stop = ratio %.3f; after 14 frames %.3f stop left\n", speed, stops_first, std::pow(2.0, stops_first), std::pow(1.0 - speed, 14));
  }

  std::printf("-- 1-frame lag of last-frame color when the camera turns (60 fps, 1080 px = 60 deg vertical)\n");
  for (double dps : {30.0, 90.0, 180.0, 360.0}) {
    const double deg_per_frame = dps / 60.0;
    const double focal = 540.0 / std::tan(30.0 * 3.14159265358979323846 / 180.0);
    const double px = focal * std::tan(deg_per_frame * 3.14159265358979323846 / 180.0);
    std::printf("turn %3.0f deg/s: %.2f deg/frame = %.1f px at the center\n", dps, deg_per_frame, px);
  }

  std::printf("-- composite pass memory traffic at 1080p, 60 fps\n");
  const double px = 1920.0 * 1080.0;
  const double bytes = px * (8.0 + 8.0 + 8.0 + 8.0);           // SSR RGBA16F 読み、プローブ RGBA16F 読み(双線形の 1 回ぶん)、前の色 RGBA16F 読み、結果 RGBA16F 書き
  std::printf("4 x 8 bytes per pixel = %.1f MB/frame = %.2f GB/s\n", bytes / 1.0e6, bytes * 60 / 1.0e9);
  return 0;
}
```

```text title="実行結果"
-- edge fade: hit uv (x, y = 0.5) -> factor, and the fade band width at 1920 px
u = 0.500: edge fade 1.000
u = 0.800: edge fade 1.000
u = 0.875: edge fade 1.000
u = 0.900: edge fade 0.800
u = 0.950: edge fade 0.400
u = 0.990: edge fade 0.080
u = 1.000: edge fade 0.000
fade band: from u = 0.875 to 1.0 on each side = 240 px of 1920, 135 px of 1080 (vertical)
a hit in the outer band: 25.0% of the screen width is fading on both sides together
-- distance fade (max distance 50 m)
ray length    0 m: 1.00
ray length    5 m: 0.90
ray length   25 m: 0.50
ray length   45 m: 0.10
ray length   50 m: 0.00
-- facing fade: dot(R, V), V = surface to camera
dot(R, V) = -1.00: factor 1.00
dot(R, V) =  0.00: factor 1.00
dot(R, V) =  0.50: factor 1.00
dot(R, V) =  0.60: factor 1.00
dot(R, V) =  0.80: factor 0.50
dot(R, V) =  0.90: factor 0.25
dot(R, V) =  1.00: factor 0.00
-- roughness fade
roughness 0.0: factor 1.00
roughness 0.3: factor 1.00
roughness 0.6: factor 1.00
roughness 0.8: factor 0.50
roughness 1.0: factor 0.00
-- combined confidence for example pixels
floor mirror, center         edge 1.00 x dist 0.84 x facing 1.00 x rough 1.00 = 0.840
wet floor near screen edge   edge 0.24 x dist 0.84 x facing 1.00 x rough 1.00 = 0.202
far reflection               edge 1.00 x dist 0.20 x facing 1.00 x rough 1.00 = 0.200
toward camera                edge 1.00 x dist 0.84 x facing 0.25 x rough 1.00 = 0.210
rough metal                  edge 1.00 x dist 0.84 x facing 1.00 x rough 0.50 = 0.420
-- three-tier blend: weights always sum to 1
max |sum - 1| over a, w in {0, 0.1, ..., 1}: 2.2e-16
ssr 1.0, probe weight 1.0 -> weights: ssr 1.00, probe 0.00, sky 0.00
ssr 1.0, probe weight 0.0 -> weights: ssr 1.00, probe 0.00, sky 0.00
ssr 0.5, probe weight 1.0 -> weights: ssr 0.50, probe 0.50, sky 0.00
ssr 0.5, probe weight 0.0 -> weights: ssr 0.50, probe 0.00, sky 0.50
ssr 0.0, probe weight 1.0 -> weights: ssr 0.00, probe 1.00, sky 0.00
ssr 0.0, probe weight 0.0 -> weights: ssr 0.00, probe 0.00, sky 1.00
-- seam: a color difference of 20% between SSR and probe, fade over W pixels
fade width     1 px: change per pixel 0.2000 (20.000% per pixel)
fade width     8 px: change per pixel 0.0250 (2.500% per pixel)
fade width    64 px: change per pixel 0.0031 (0.312% per pixel)
fade width   240 px: change per pixel 0.0008 (0.083% per pixel)
-- exposure adaptation: SSR reads last frame's color (1 frame old)
adapt speed 0.02/frame: first frame moves 0.020 stop = ratio 1.014; after 14 frames 0.754 stop left
adapt speed 0.05/frame: first frame moves 0.050 stop = ratio 1.035; after 14 frames 0.488 stop left
adapt speed 0.10/frame: first frame moves 0.100 stop = ratio 1.072; after 14 frames 0.229 stop left
-- 1-frame lag of last-frame color when the camera turns (60 fps, 1080 px = 60 deg vertical)
turn  30 deg/s: 0.50 deg/frame = 8.2 px at the center
turn  90 deg/s: 1.50 deg/frame = 24.5 px at the center
turn 180 deg/s: 3.00 deg/frame = 49.0 px at the center
turn 360 deg/s: 6.00 deg/frame = 98.3 px at the center
-- composite pass memory traffic at 1080p, 60 fps
4 x 8 bytes per pixel = 66.4 MB/frame = 3.98 GB/s
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。信頼度の式と係数の値は自分で決めた一例です。

- Tomasz Stachowiak, Yasin Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Michal Valient, "Reflections and Volumetrics of Killzone Shadow Fall", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Morgan McGuire, Michael Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014
- Tomas Akenine-Möller ほか, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ {#related}

- [Reflection Probes](index.md)
- [SSR Fallback and Compositing](../ssr-fallback.md)
- [Reflection Comparison](../comparison.md)
