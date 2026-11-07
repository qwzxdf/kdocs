---
title: Visual Effect
tags:
  - 描画
---

# Visual Effect

直接光だけで描いた部屋は日が当たる所だけが明るく、日陰は真っ黒です。現実の部屋はそうなりません。窓から入った光が床や壁で何度も跳ね返って、日の当たらない隅まで届くからです。赤い壁の近くの白い床がうっすら赤くなるのも物の根元が暗くなるのも同じ「跳ね返った光」のせいです。このページでは間接光が見た目に出す効果を 4 つに分けそれぞれを数字で見積もります。壁の近くでどれだけ染まるか反射を重ねると何倍明るくなるか空の光だけで日陰がどれだけ明るいかを、C++ で数えます。最後に、半球の環境光と色のにじみを足すシェーダーを 1 本にまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。以前のページにあった lux の表（日向 100,000、日陰 10,000〜20,000 など）は、出典がなく確かめられないので削りました。末尾の資料は今回は読んでいません。

!!! tip "ポイント"
    - 床の点から 4 m × 3 m の赤い壁を見た割合（形状係数）は、壁まで 0.25 m で 0.445、1 m で 0.296、4 m で 0.051 です。壁から 4 m 離れるとにじみは壁際の 1/8 以下になります。
    - 反射を無限に重ねた合計は `1 / (1 − ρ)` 倍で、ρ = 0.2 なら 1.25 倍、0.8 なら 5 倍です。これは「最初の反射の何倍か」で、直接光の何倍かではありません。
    - 4 m × 5 m × 3 m の部屋に 1.8 m² の窓から太陽が 45° で差すと、間接光は日向の床の 0.5%（ρ = 0.2）から 7.1%（ρ = 0.8）です。日陰はこの光だけで見えています。
    - 空と地面を 2 つの一様な半球と見なすと環境光は法線の Y 成分の一次式になり、厳密に求まります。

!!! info "このページを読む前に"
    - [GI Theory](index.md)（このセクション全体の地図と読む順番）

## 効果は 4 つある {#effects}

間接光の効果は日陰の明るさ色のにじみ接地感、室内の明るさの 4 つです。順に見ます。

| 効果 | 何が変わるか | 節 |
| --- | --- | --- |
| 日陰の明るさ | 影の中が真っ黒でなくなる | [日陰](#shade) |
| 色のにじみ | 色のついた壁の近くが染まる | [にじみ](#bleed) |
| 接地感 | 物の根元・隅が暗くなって地面になじむ | [接地](#contact) |
| 室内の明るさ | 日の当たらない奥まで届く | [室内](#room) |

品質を上げる優先順位は影の中が真っ黒でないことが最初、次に場所による明るさの差、最後に色のにじみの順に効くことが多いです。これは経験的な目安でこのページで測ったものではありません。

## 日陰が明るくなる {#shade}

### 空は大きな光源 {#sky}

日陰に光が届くのは空全体が光っているからです。直接光は太陽 1 個の方向からだけ来ますが、空の光は上半球のすべての方向から来ます。上半球を一様な放射輝度 `Ls`、下半球（地面）を一様な `Lg` として、法線 `n` の面に当たる光を余弦で積分します。放射照度 `E(n)` を `π` で割った値は次の式になります。

```text
E(n) / π = Ls × (1 + n.y) / 2 + Lg × (1 − n.y) / 2
```

上向きの面（`n.y = 1`）は `Ls` だけ下向きの面は `Lg` だけ真横（`n.y = 0`）は 2 つの平均を受けます。余弦の積分が `n.y` の一次式になるのは、半球を 2 つ重ねた形だからで、近似ではありません（空が一様であることと遮蔽がないことが前提です）。空が 1.0、地面が 0.3 のときの値を数えました。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="半球の環境光"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">半球の環境光</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,193.0 75.0,191.7 80.0,190.3 85.0,189.0 90.0,187.7 95.0,186.4 100.0,185.0 105.0,183.7 110.0,182.4 115.0,181.0 120.0,179.7 125.0,178.4 130.0,177.0 135.0,175.7 140.0,174.4 145.0,173.1 150.0,171.7 155.0,170.4 160.0,169.1 165.0,167.7 170.0,166.4 175.0,165.1 180.0,163.7 185.0,162.4 190.0,161.1 195.0,159.8 200.0,158.4 205.0,157.1 210.0,155.8 215.0,154.4 220.0,153.1 225.0,151.8 230.0,150.4 235.0,149.1 240.0,147.8 245.0,146.5 250.0,145.1 255.0,143.8 260.0,142.5 265.0,141.1 270.0,139.8 275.0,138.5 280.0,137.1 285.0,135.8 290.0,134.5 295.0,133.2 300.0,131.8 305.0,130.5 310.0,129.2 315.0,127.8 320.0,126.5 325.0,125.2 330.0,123.8 335.0,122.5 340.0,121.2 345.0,119.8 350.0,118.5 355.0,117.2 360.0,115.9 365.0,114.5 370.0,113.2 375.0,111.9 380.0,110.5 385.0,109.2 390.0,107.9 395.0,106.6 400.0,105.2 405.0,103.9 410.0,102.6 415.0,101.2 420.0,99.9 425.0,98.6 430.0,97.2 435.0,95.9 440.0,94.6 445.0,93.2 450.0,91.9 455.0,90.6 460.0,89.3 465.0,87.9 470.0,86.6 475.0,85.3 480.0,83.9 485.0,82.6 490.0,81.3 495.0,79.9 500.0,78.6 505.0,77.3 510.0,76.0 515.0,74.6 520.0,73.3 525.0,72.0 530.0,70.6 535.0,69.3 540.0,68.0 545.0,66.7 550.0,65.3 555.0,64.0 560.0,62.7 565.0,61.3 570.0,60.0"/><circle cx="570.0" cy="60.0" r="4" fill="#4c8bf5"/><text x="578.0" y="52.0" text-anchor="start" style="font-size:11px;font-weight:700">1.0</text><circle cx="445.0" cy="93.2" r="4" fill="#4c8bf5"/><text x="453.0" y="85.25" text-anchor="start" style="font-size:11px;font-weight:700">0.825</text><circle cx="320.0" cy="126.5" r="4" fill="#4c8bf5"/><text x="328.0" y="118.5" text-anchor="start" style="font-size:11px;font-weight:700">0.65</text><circle cx="195.0" cy="159.8" r="4" fill="#4c8bf5"/><text x="203.0" y="151.75" text-anchor="start" style="font-size:11px;font-weight:700">0.475</text><circle cx="70.0" cy="193.0" r="4" fill="#4c8bf5"/><text x="78.0" y="185.0" text-anchor="start" style="font-size:11px;font-weight:700">0.3</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">-1</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">-0.5</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">法線の Y 成分 n.y（-1 = 真下、+1 = 真上）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">環境光の放射輝度（空 1.0、地面 0.3）</text></svg>

- `n.y = +1.0`（真上）: 1.000
- `+0.5`: 0.825
- `0`（真横）: 0.650
- `−0.5`: 0.475
- `−1.0`（真下）: 0.300

直線になるのは式が `n.y` の一次式だからです。`lerp` 1 回で同じ値が出ます（後のコードの `HemisphereAmbient`）。

### 一定値の環境光との違い {#flat-ambient}

環境光を一定値にすると真っ黒は避けられますが、上向きの面も下向きの面も同じ明るさになりのっぺりします。半球の環境光なら上を向いた面は空の色、下を向いた面は地面の色に寄ります。1 行増えるだけで場所による明るさの差が出ます。ただし、法線の向きだけで決まるので「屋根の下で空が見えない」といった遮蔽は表せません。遮蔽は [AO](../../ao/index.md) で暗くします。

## 色のにじみ {#bleed}

### 形状係数 {#form-factor}

赤い壁で反射した光が隣の白い床を照らす量は、床の点から壁がどれだけ広く見えるかで決まります。この割合が形状係数 `F` です。床の点を中心とする半球のうち壁が占める立体角を余弦で重みづけして `π` で割ったものです。幾何だけで決まる量で光の強さは入りません。

幅 4 m、高さ 3 m の壁に対して壁までの距離 `d` を変えて、モンテカルロで数えました（配置と数え方は末尾の `numbers.cpp` にあります）。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="距離と形状係数"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">距離と形状係数</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="101.2,80.9 132.5,101.0 195.0,137.5 320.0,189.2 570.0,230.6"/><circle cx="101.2" cy="80.9" r="4" fill="#e5484d"/><text x="109.25" y="72.9" text-anchor="start" style="font-size:11px;font-weight:700">0.445</text><circle cx="132.5" cy="101.0" r="4" fill="#e5484d"/><text x="140.5" y="93.03999999999999" text-anchor="start" style="font-size:11px;font-weight:700">0.392</text><circle cx="195.0" cy="137.5" r="4" fill="#e5484d"/><text x="203.0" y="129.52" text-anchor="start" style="font-size:11px;font-weight:700">0.296</text><circle cx="320.0" cy="189.2" r="4" fill="#e5484d"/><text x="328.0" y="181.2" text-anchor="start" style="font-size:11px;font-weight:700">0.160</text><circle cx="570.0" cy="230.6" r="4" fill="#e5484d"/><text x="578.0" y="222.62" text-anchor="start" style="font-size:11px;font-weight:700">0.051</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">3</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">4</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="216.0" text-anchor="end" style="font-size:11px;font-weight:400">0.1</text><text x="62" y="178.0" text-anchor="end" style="font-size:11px;font-weight:400">0.2</text><text x="62" y="140.0" text-anchor="end" style="font-size:11px;font-weight:400">0.3</text><text x="62" y="102.0" text-anchor="end" style="font-size:11px;font-weight:400">0.4</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">壁までの距離 d（m）。壁は幅 4 m、高さ 3 m</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">壁の形状係数 F（床の点から見た割合）</text></svg>

- `d = 0.25 m`: F = 0.445
- `0.5 m`: 0.392
- `1 m`: 0.296
- `2 m`: 0.160
- `4 m`: 0.051

壁のすぐ近くでは半球の半分近く（0.5 に近づく）を壁が占めますが、4 m 離れると 0.051 まで落ちます。壁が近いほどにじみは急に強くなります。

### 床がどれだけ染まるか {#bleed-numbers}

壁のアルベドを (0.8, 0.1, 0.1)、床のアルベドを 0.8（灰色）、壁と床の直接照度を同じ（比 1）とします。壁が床に足す放射照度は `壁のアルベド × F` を直接照度に掛けたものです。床の色（直接光 + にじみ）に直すと次のようになります。

- `d = 0.25 m`: (1.085, 0.836, 0.836)
- `1 m`: (0.989, 0.824, 0.824)
- `4 m`: (0.832, 0.804, 0.804)

壁がないときの床の色は (0.8, 0.8, 0.8) です。壁際では R が 0.8 から 1.085 に増え G と B は 0.036 しか増えません。赤い光は大きく足されるのに緑と青は壁の反射が小さいのでほとんど変わらず結果として赤みが出ます。4 m 離れると R の増分は 0.032 まで減って、見分けがつかなくなります。

この見積もりは 1 回反射だけです。壁も床から反射光を受けるので、本当はもう少し複雑ですがにじみの目立ち方を決めているのは最初の 1 回です。

## 接地感 {#contact}

物と地面が接する所や壁の隅は周りの面が近いので、空の光が届きません。そこが暗くなると物が地面に「乗っている」ように見えます。この暗さは AO が表します（[AO](../../ao/index.md)）。GI にはこの暗さが自然に含まれます。遮蔽された方向からの光はそもそも来ないからです。

AO だけでは足りない点が 1 つあります。AO は遮蔽を暗さにするだけで、遮蔽物から反射した光を足しません。白い隅は反射のおかげで AO が示すほど暗くなりません。この補正（マルチバウンスの AO）は [GTAO](../../ao/gtao.md) で扱います。

## 室内の明るさ {#room}

### 反射を重ねる {#series}

閉じた部屋で平均アルベド `ρ` の面が光を何度も反射すると、全体の明るさはどれだけ増えるでしょうか。1 回目の反射の量を 1 とします。2 回目は `ρ` 倍、3 回目は `ρ²` 倍と減っていくので、合計は等比級数です。

```text
合計 = 1 + ρ + ρ² + ρ³ + … = 1 / (1 − ρ)
```

数値で確かめた合計はρ = 0.2 で 1.250、0.5 で 2.000、0.8 で 5.000、0.9 で 10.000 で、どれも `1 / (1 − ρ)` と一致しました。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="反射の累計"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">反射の累計</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,218.3 120.0,212.0 170.0,210.7 220.0,210.5 270.0,210.4 320.0,210.4 370.0,210.4 420.0,210.4 470.0,210.4 520.0,210.4 570.0,210.4"/><line x1="70" y1="210.4" x2="570" y2="210.4" stroke="#2e9e5b" stroke-dasharray="4 4"/><text x="574" y="214.41666666666666" text-anchor="start" style="font-size:11px;font-weight:700">ρ=0.2: 1.25</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,218.3 120.0,202.5 170.0,194.6 220.0,190.6 270.0,188.6 320.0,187.7 370.0,187.2 420.0,186.9 470.0,186.8 520.0,186.7 570.0,186.7"/><line x1="70" y1="186.7" x2="570" y2="186.7" stroke="#4c8bf5" stroke-dasharray="4 4"/><text x="574" y="190.66666666666666" text-anchor="start" style="font-size:11px;font-weight:700">ρ=0.5: 2.00</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,218.3 120.0,193.0 170.0,172.7 220.0,156.5 270.0,143.5 320.0,133.2 370.0,124.9 420.0,118.2 470.0,112.9 520.0,108.7 570.0,105.3"/><line x1="70" y1="91.7" x2="570" y2="91.7" stroke="#e5484d" stroke-dasharray="4 4"/><text x="574" y="95.66666666666663" text-anchor="start" style="font-size:11px;font-weight:700">ρ=0.8: 5.00</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="170.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="270.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">4</text><text x="370.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">6</text><text x="470.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">8</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">10</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="222.33333333333334" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="62" y="190.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">2</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">3</text><text x="62" y="127.33333333333333" text-anchor="end" style="font-size:11px;font-weight:400">4</text><text x="62" y="95.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">5</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">反射の回数 k</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">最初の反射を 1 とした累計</text></svg>

3 本の線は反射を 1 項ずつ足していった累計です。ρ = 0.2 は数回でほぼ頭打ちになりρ = 0.8 は k = 10 でも 4.57 で、まだ 5 に届きません。白い部屋ほど光は長く跳ね回るので、間接光の計算で「何回まで追うか」が効きます。

以前のページには「ρ = 0.8 では間接光が直接光の 4 倍」と書いてありましたが、この読み方は誤りです。`1 / (1 − ρ)` は最初の反射を 1 としたときの合計で、2 回目以降の和は最初の反射の `ρ / (1 − ρ)` 倍（ρ = 0.8 なら 4 倍）です。直接光との比ではありません。

### 実際の部屋では桁が違う {#room-real}

では直接光との比はいくつでしょうか。4 m × 5 m × 3 m（表面積 94 m²）の部屋に 1.8 m² の窓から太陽が 45° で差し込むとします。窓を通る光の量は 1.273（太陽の照度を 1 として、窓の面積に cos 45° を掛けたもの）で、日向の床の照度は 0.707 です。

この光が部屋の面に一様に当たり平均アルベド `ρ` で反射して部屋の中を回る、と見なして日の当たらない面の間接照度を見積もりました。積分球の考え方を使った足した近似で、窓から逃げる光や光の偏りは無視しています。

- ρ = 0.2: 間接照度 0.0034（日向の床の 0.5%）
- ρ = 0.5: 0.0133（1.9%）
- ρ = 0.8: 0.0503（7.1%）

日向の床と比べると日の当たらない壁の明るさは、最大でも 7% 程度です。それでも日陰が見えるのは画面に出す段階でトーンマッピングやガンマがかかり、暗い値が持ち上がるからだと考えられます（この点は今回測っていません）。GI がなければこの値が 0 になり完全な黒になります。

見積もりは部屋の形や窓の大きさで大きく変わります。確かめたのは桁（数 % から 10 % 弱）で、特定の部屋の予測ではありません。

## 効果が大きいのはどこか {#where}

間接光が見た目を支配する場所は次のとおりです。

- 日向の屋外: 直接光が支配的です。間接光（空の光と地面の反射）は脇役です。
- 日陰の屋外: 直接光が 0 なので、見えているのはすべて間接光です。
- 室内: 日の当たらない所はすべて間接光です。
- 洞窟の奥: 入口から入った光の跳ね返りだけです。

「GI の効果が大きいか小さいか」は、場面で決まります。日向だけの絵なら半球の環境光と AO でほぼ足ります。日陰・室内・洞窟ではプローブやライトマップなど場所ごとに明るさを持つ手法が要ります。

## 簡易な近似 {#cheap}

GI を計算せずに効果の一部を得る方法は、次の 4 つです。

| 方法 | 得られる効果 | 参照 |
| --- | --- | --- |
| 半球ライト | 日陰の明るさ（方向の差は少し） | [Using the Sky for Lighting](../../atmosphere/sky-models/sky-lighting.md) |
| AO | 接地感 | [AO](../../ao/index.md) |
| マルチバウンスの AO | 白い面で AO が暗すぎない | [GTAO](../../ao/gtao.md) |
| 環境光のプローブ（SH） | 場所による明るさの差 | [Probe GI](../probes/index.md) |

## 合成するコード {#compose}

半球の環境光、色のにじみ直接光を 1 本の関数にまとめます。ここからコードを数行ずつ見ます。最初は定数です。

```hlsl
cbuffer AmbientCB : register(b0) {
  float3 gSkyRadiance;      // 空（上半球）の一様な放射輝度（リニア）。青みがかった色
  float  gBounceStrength;   // 色のにじみの強さ 0〜1。0 で無効
  float3 gGroundRadiance;   // 地面（下半球）の一様な放射輝度（リニア）。地面の色 × 日向の明るさ
  float  gPad;              // 詰め物
  float3 gSunColor;         // 太陽の色 × 強さ（リニア）
  float  gPad2;             // 詰め物
  float3 gSunDir;           // 太陽へ向かう単位ベクトル
  float  gPad3;             // 詰め物
};
```

`gSkyRadiance` は空の放射輝度（リニア）、`gGroundRadiance` は地面の放射輝度で「地面の色 × 日向の明るさ」を CPU 側で掛けた値を渡します。16 バイト境界に合わせるため、`float3` の後ろに `gBounceStrength` などの `float` を詰めています。`gPad` は詰め物で使いません。

半球の環境光です。

```hlsl
// 二つの一様な半球（空と地面）が、法線 n の面に作る環境光の放射輝度。
// 余弦で畳み込むと、n.y の一次式になる: E(n)/π = Ls (1 + n.y)/2 + Lg (1 − n.y)/2（厳密。AO やめり込みは無視）。
float3 HemisphereAmbient(float3 n) {
  float up = n.y * 0.5 + 0.5;                              // 上向き 1、下向き 0
  return lerp(gGroundRadiance, gSkyRadiance, up);          // 線形補間がそのまま厳密な式
}
```

`n.y * 0.5 + 0.5` で `n.y = 1` の上向きを 1、`−1` の下向きを 0 にそろえ `lerp` で地面と空の放射輝度を混ぜます。この線形補間は前の節の式 `Ls (1 + n.y)/2 + Lg (1 − n.y)/2` と同じです。

色のにじみです。

```hlsl
// 近くの色のついた面から受ける 1 回反射の見積もり（足した近似）。
// wall_albedo: 壁の色、form_factor: 壁が見える割合（0〜1。事前に焼くか、距離から見積もる）、wall_irradiance: 壁の直接照度の比。
float3 ColorBleed(float3 wall_albedo, float form_factor, float wall_irradiance) {
  return gBounceStrength * wall_albedo * form_factor * wall_irradiance;   // 壁が反射した光が、床の照度に足される割合
}
```

`wall_albedo × form_factor × wall_irradiance` が前の節で数えた「壁が床に足す割合」です。`form_factor` は事前に焼くか距離から見積もります（表の値は一例です）。`gBounceStrength` は 1 回反射だけの近似と実際の差を見た目で合わせる係数で、0 にすると無効になります。

最後に、全部を足します。

```hlsl
// 全部をまとめる。ao は 0〜1（1 = 遮蔽なし）。
float3 ShadeWithGi(float3 albedo, float3 n, float shadow, float ao, float3 bleed_irradiance) {
  float n_dot_l = saturate(dot(n, gSunDir));               // 直接光の当たり具合
  float3 direct = albedo * gSunColor * n_dot_l * shadow;   // 影の中では 0 になる
  float3 ambient = albedo * HemisphereAmbient(n) * ao;     // 影の中でも残る。AO で隙間を暗く
  float3 bleed = albedo * bleed_irradiance;                // 色のにじみ。アルベドを掛けるので、白い面ほど染まる
  return direct + ambient + bleed;
}
```

直接光は影の中で 0 になります。環境光は影の中でも残ります。AO は環境光にだけ掛けます。直接光は影のテストで暗くしているので、AO を重ねると二重に暗くなるからです。にじみはアルベドを掛けます。白い面ほど赤く見え赤い面は元から赤いので、にじみが目立ちません。

## よくあるミス {#mistakes}

??? failure "GI なしで、影の中が真っ黒"
    原因は環境光（アンビエント）を足していないことです。最低でも半球の環境光を足します。

??? failure "環境光を一定値にして、のっぺりする"
    原因は法線の向きを使っていないことです。上向きの面と下向きの面が同じ明るさになります。半球の環境光（`lerp` 1 回）にします。

??? failure "AO を直接光にも掛けて、昼間の絵が暗い"
    原因は影のテストで暗くした直接光に AO をさらに掛けていることです。AO は間接光（環境光）にだけ掛けます。

??? failure "「間接光は直接光の 4 倍」と読んで、環境光を明るくしすぎる"
    原因は `1 / (1 − ρ)` を直接光との比と取り違えていることです。この式は最初の反射を 1 としたときの反射の合計です。直接光との比は部屋の形と窓の大きさで決まり日の当たらない面では数 % から 10 % 弱の桁です。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 間接光の効果は日陰の明るさ色のにじみ接地感、室内の明るさの 4 つ
    - [x] 空と地面を 2 つの一様な半球と見なすと環境光は `n.y` の一次式で、`lerp` 1 回で出る
    - [x] 色のにじみは壁のアルベド × 形状係数。壁際 0.25 m で F = 0.445、4 m で 0.051
    - [x] 反射の総和は `1 / (1 − ρ)`。直接光との比ではない
    - [x] AO は環境光にだけ掛ける

## C++ で数えたもの {#numbers}

```cpp
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>
#include <random>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

// 床の点（原点、法線は +Y）から見た、壁（平面 z = d、幅 w（x 方向、中心 0）、高さ h（y 方向 0〜h））の形状係数。
// 形状係数 F = 点から出たコサイン分布の光線が、壁に当たる割合。モンテカルロで数える。
double WallFormFactor(double d, double w, double h, int samples) {
  std::mt19937 rng(777);                                         // 種を固定
  std::uniform_real_distribution<double> uni(0.0, 1.0);
  int hit = 0;
  for (int i = 0; i < samples; ++i) {
    const double u1 = uni(rng), u2 = uni(rng);
    const double r = std::sqrt(u1), phi = 2.0 * kPi * u2;        // コサイン分布の半球サンプル（円盤から持ち上げる）
    const double x = r * std::cos(phi), z = r * std::sin(phi);   // 水平成分
    const double y = std::sqrt(std::max(0.0, 1.0 - u1));         // 法線方向の成分
    if (z <= 1e-9) continue;                                     // 壁の方を向かない光線
    const double t = d / z;                                      // 壁の平面 z = d に届く距離
    const double hx = x * t, hy = y * t;                         // 当たる位置
    if (std::fabs(hx) <= 0.5 * w && hy >= 0.0 && hy <= h) ++hit;
  }
  return static_cast<double>(hit) / samples;
}

int main() {
  // 1. 赤い壁（幅 4 m、高さ 3 m）から床の点までの距離 d と、形状係数 F。
  //    壁は床と同じ直接照度で照らされているとする。壁の albedo = (0.8, 0.1, 0.1)、床の albedo = 0.8（白っぽい）。
  std::printf("-- form factor from a floor point to a red wall (4 m wide, 3 m high)\n");
  const double rw[3] = {0.8, 0.1, 0.1};
  const double floor_albedo = 0.8;
  for (double d : {0.25, 0.5, 1.0, 2.0, 4.0}) {
    const double f = WallFormFactor(d, 4.0, 3.0, 2000000);
    std::printf("d=%.2f m: F = %.3f, extra irradiance = (%.3f, %.3f, %.3f) x direct, floor color = (%.3f, %.3f, %.3f)\n", d, f,
                rw[0] * f, rw[1] * f, rw[2] * f, floor_albedo * (1.0 + rw[0] * f), floor_albedo * (1.0 + rw[1] * f),
                floor_albedo * (1.0 + rw[2] * f));
  }

  // 2. 反射の総和。k 回目の反射は rho^k 倍。1 + rho + rho^2 + ... = 1 / (1 - rho)。
  std::printf("-- geometric series of bounces\n");
  for (double rho : {0.2, 0.5, 0.8, 0.9}) {
    double sum = 0.0, term = 1.0;
    for (int k = 0; k < 200; ++k) { sum += term; term *= rho; }
    std::printf("rho=%.1f: sum = %.3f (1/(1-rho) = %.3f), bounces after the first = %.3f x the first bounce\n", rho, sum,
                1.0 / (1.0 - rho), sum - 1.0);
  }

  // 3. 部屋の間接照度（積分球のモデル）。窓から入った光量 Phi が、部屋の全表面積 A に一様に広がる。
  //    1 回目の反射で rho * Phi。窓から逃げる分を考慮して、実効の反射率 rho_eff = rho (1 - 窓の割合)。
  //    間接照度 E_ind = rho * Phi / (A (1 - rho_eff))。
  //    部屋 4 x 5 x 3 m、A = 94 m^2。窓 1.2 x 1.5 = 1.8 m^2。太陽の高さ 45 度、窓は真正面の方位。太陽の強さ I = 1。
  std::printf("-- indirect irradiance in a room (4 x 5 x 3 m, window 1.8 m2, sun 45 deg)\n");
  const double area = 2.0 * (4.0 * 5.0 + 4.0 * 3.0 + 5.0 * 3.0);    // 全表面積
  const double window = 1.8;
  const double phi_in = window * std::cos(45.0 / kDeg);              // 窓を通る光量（光線に垂直な断面積 * 1）
  const double e_dir = std::sin(45.0 / kDeg);                        // 日だまりの床の照度（水平面）
  std::printf("total surface = %.0f m2, flux through window = %.3f, direct floor patch irradiance = %.3f\n", area, phi_in, e_dir);
  for (double rho : {0.2, 0.5, 0.8}) {
    const double rho_eff = rho * (1.0 - window / area);
    const double e_ind = rho * phi_in / (area * (1.0 - rho_eff));
    std::printf("rho=%.1f: E_ind = %.4f (= %.1f%% of the patch), series factor = %.2f\n", rho, e_ind, e_ind / e_dir * 100.0,
                1.0 / (1.0 - rho_eff));
  }

  // 4. 二つの一様な半球（空 Ls、地面 Lg）が作る環境光。E(n)/pi = Ls (1 + ny)/2 + Lg (1 - ny)/2。
  std::printf("-- hemisphere ambient (sky 1.0, ground 0.3)\n");
  for (double ny : {1.0, 0.5, 0.0, -0.5, -1.0}) {
    std::printf("n.y = %+.1f: ambient radiance = %.3f\n", ny, 1.0 * (1.0 + ny) / 2.0 + 0.3 * (1.0 - ny) / 2.0);
  }
}
```

```text title="実行結果"
-- form factor from a floor point to a red wall (4 m wide, 3 m high)
d=0.25 m: F = 0.445, extra irradiance = (0.356, 0.045, 0.045) x direct, floor color = (1.085, 0.836, 0.836)
d=0.50 m: F = 0.392, extra irradiance = (0.313, 0.039, 0.039) x direct, floor color = (1.051, 0.831, 0.831)
d=1.00 m: F = 0.296, extra irradiance = (0.236, 0.030, 0.030) x direct, floor color = (0.989, 0.824, 0.824)
d=2.00 m: F = 0.160, extra irradiance = (0.128, 0.016, 0.016) x direct, floor color = (0.903, 0.813, 0.813)
d=4.00 m: F = 0.051, extra irradiance = (0.040, 0.005, 0.005) x direct, floor color = (0.832, 0.804, 0.804)
-- geometric series of bounces
rho=0.2: sum = 1.250 (1/(1-rho) = 1.250), bounces after the first = 0.250 x the first bounce
rho=0.5: sum = 2.000 (1/(1-rho) = 2.000), bounces after the first = 1.000 x the first bounce
rho=0.8: sum = 5.000 (1/(1-rho) = 5.000), bounces after the first = 4.000 x the first bounce
rho=0.9: sum = 10.000 (1/(1-rho) = 10.000), bounces after the first = 9.000 x the first bounce
-- indirect irradiance in a room (4 x 5 x 3 m, window 1.8 m2, sun 45 deg)
total surface = 94 m2, flux through window = 1.273, direct floor patch irradiance = 0.707
rho=0.2: E_ind = 0.0034 (= 0.5% of the patch), series factor = 1.24
rho=0.5: E_ind = 0.0133 (= 1.9% of the patch), series factor = 1.96
rho=0.8: E_ind = 0.0503 (= 7.1% of the patch), series factor = 4.64
-- hemisphere ambient (sky 1.0, ground 0.3)
n.y = +1.0: ambient radiance = 1.000
n.y = +0.5: ambient radiance = 0.825
n.y = +0.0: ambient radiance = 0.650
n.y = -0.5: ambient radiance = 0.475
n.y = -1.0: ambient radiance = 0.300
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。形状係数の定義、反射の等比級数、半球の環境光は標準的な形を自分で導き数字で確かめました。

- James T. Kajiya, "The Rendering Equation", SIGGRAPH 1986（レンダリング方程式の原典）
- Cindy M. Goral, Kenneth E. Torrance, Donald P. Greenberg, Bennett Battaile, "Modeling the Interaction of Light Between Diffuse Surfaces", SIGGRAPH 1984（ラジオシティの原典。形状係数）
- Ravi Ramamoorthi, Pat Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001（放射照度を 9 個の SH 係数で表す）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、放射照度の章）

## 関連ページ {#related}

- [GI Theory](index.md)
- [AO](../../ao/index.md)
- [GI Comparison](../comparison.md)
