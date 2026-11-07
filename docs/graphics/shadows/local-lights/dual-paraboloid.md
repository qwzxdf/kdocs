---
title: Dual Paraboloid
tags:
  - 描画
---

# Dual Paraboloid

点光源の影をキューブマップで作ると、シャドウパスが 6 回になります。光の周りの全方向を覆うだけなのに、6 枚も描くのはもったいない、と考えた人たちがいました。そこで、お椀の形をした放物面の鏡で光を反射させ半球ぶんを丸ごと 1 枚の円盤に写す方法が使われました。前半球と後半球で円盤は 2 枚、描画は 2 回です。これがデュアル パラボロイドです。かつてのモバイルや古い世代の機種で使われましたが、歪みの扱いが難しく今はキューブマップが主流です。このページでは投影の式を導き解像度の偏りと三角形の歪みを数字で見て、なぜ使われなくなったのかを確かめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc` で `vs_5_0` と `ps_5_0` に通しましたが、描画した結果は確かめていません。この手法の原論文は今回は読んでいないので、式は幾何から自分で導き論文の内容として書いた箇所はありません。

!!! tip "ポイント"
    - 式は `xy = dir.xy / (1 + dir.z)` の 1 行です。前半球は半径 1 の円盤に収まります。
    - 解像度は一様ではありません。円盤の縁（半球の端）は中心の 4 倍の面積を受け持ちます。旧版にあった「中心で高く縁で低い」は逆でした。
    - 同じ最悪密度ならキューブマップ（一辺 1024）に対して、放物面は直径 898 で足ります。メモリは約 3.9 分の 1 です。
    - 頂点だけを変換すると、三角形の辺が曲線にならず直線になります。光から見て 38.7° 張る辺は中点が 10.7 画素ずれます。

!!! info "このページを読む前に"
    - [Point and Spot Light Shadows](index.md)（このセクション全体の地図と、読む順番）
    - [Point Lights: Cube Maps](point-cubemap.md)（比べる相手の、キューブマップによる方法）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（頂点シェーダーの後で何が補間されるか）

<!-- fig:dual-paraboloid:begin -->

<svg class="fig illust motion" data-fig="dual-paraboloid" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dual-paraboloid" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">デュアル パラボロイド:放物面の鏡で、半球を 1 枚の画像に集める</text>
<path d="M110.0,270.0 L113.54,265.05 L117.08,260.21 L120.62,255.47 L124.17,250.83 L127.71,246.3 L131.25,241.88 L134.79,237.55 L138.33,233.33 L141.88,229.22 L145.42,225.21 L148.96,221.3 L152.5,217.5 L156.04,213.8 L159.58,210.21 L163.12,206.72 L166.67,203.33 L170.21,200.05 L173.75,196.88 L177.29,193.8 L180.83,190.83 L184.38,187.97 L187.92,185.21 L191.46,182.55 L195.0,180.0 L198.54,177.55 L202.08,175.21 L205.62,172.97 L209.17,170.83 L212.71,168.8 L216.25,166.88 L219.79,165.05 L223.33,163.33 L226.88,161.72 L230.42,160.21 L233.96,158.8 L237.5,157.5 L241.04,156.3 L244.58,155.21 L248.12,154.22 L251.67,153.33 L255.21,152.55 L258.75,151.88 L262.29,151.3 L265.83,150.83 L269.38,150.47 L272.92,150.21 L276.46,150.05 L280.0,150.0 L283.54,150.05 L287.08,150.21 L290.62,150.47 L294.17,150.83 L297.71,151.3 L301.25,151.88 L304.79,152.55 L308.33,153.33 L311.88,154.22 L315.42,155.21 L318.96,156.3 L322.5,157.5 L326.04,158.8 L329.58,160.21 L333.12,161.72 L336.67,163.33 L340.21,165.05 L343.75,166.88 L347.29,168.8 L350.83,170.83 L354.38,172.97 L357.92,175.21 L361.46,177.55 L365.0,180.0 L368.54,182.55 L372.08,185.21 L375.62,187.97 L379.17,190.83 L382.71,193.8 L386.25,196.88 L389.79,200.05 L393.33,203.33 L396.88,206.72 L400.42,210.21 L403.96,213.8 L407.5,217.5 L411.04,221.3 L414.58,225.21 L418.12,229.22 L421.67,233.33 L425.21,237.55 L428.75,241.88 L432.29,246.3 L435.83,250.83 L439.38,255.47 L442.92,260.21 L446.46,265.05 L450.0,270.0" fill="none" stroke="#1f2937" stroke-width="4"/>
<text x="280" y="125" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">放物面（鏡）</text>
<circle cx="280" cy="310" r="8" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="294" y="318" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">光（焦点）</text>
<line x1="80" y1="88" x2="480" y2="88" stroke="#2563eb" stroke-width="3"/>
<text x="80" y="78" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">1 枚の画像（-1 〜 1）</text>
<line x1="280" y1="310" x2="280" y2="310" stroke="#e5aa28" stroke-width="3"><animate attributeName="x2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="280;280;460.62;449.8;439.48;429.17;419.44;408.73;398.55;387.43;376.24;364.18;351.91;338.55;324.72;310.27;295.26;280;264.74;249.73;235.28;221.45;208.09;195.82;183.76;172.57;161.45;151.27;140.56;130.83;120.52;110.2;99.38;99.38"/><animate attributeName="y2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="310;310;284.61;269.34;255.29;242.33;229.92;218.74;207.67;197.71;187.99;179.38;170.88;164.11;158.04;153.3;150.53;149.8;150.53;153.3;158.04;164.11;170.88;179.38;187.99;197.71;207.67;218.74;229.92;242.33;255.29;269.34;284.61;284.61"/></line>
<line x1="280" y1="310" x2="280" y2="88" stroke="#2ea043" stroke-width="3"><animate attributeName="x1" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="280;280;460.62;449.8;439.48;429.17;419.44;408.73;398.55;387.43;376.24;364.18;351.91;338.55;324.72;310.27;295.26;280;264.74;249.73;235.28;221.45;208.09;195.82;183.76;172.57;161.45;151.27;140.56;130.83;120.52;110.2;99.38;99.38"/><animate attributeName="y1" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="310;310;284.61;269.34;255.29;242.33;229.92;218.74;207.67;197.71;187.99;179.38;170.88;164.11;158.04;153.3;150.53;149.8;150.53;153.3;158.04;164.11;170.88;179.38;187.99;197.71;207.67;218.74;229.92;242.33;255.29;269.34;284.61;284.61"/><animate attributeName="x2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="280;280;460.62;449.8;439.48;429.17;419.44;408.73;398.55;387.43;376.24;364.18;351.91;338.55;324.72;310.27;295.26;280;264.74;249.73;235.28;221.45;208.09;195.82;183.76;172.57;161.45;151.27;140.56;130.83;120.52;110.2;99.38;99.38"/></line>
<circle cx="280" cy="310" r="6" fill="#e5484d"><animate attributeName="cx" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="280;280;460.62;449.8;439.48;429.17;419.44;408.73;398.55;387.43;376.24;364.18;351.91;338.55;324.72;310.27;295.26;280;264.74;249.73;235.28;221.45;208.09;195.82;183.76;172.57;161.45;151.27;140.56;130.83;120.52;110.2;99.38;99.38"/><animate attributeName="cy" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0950;0.1233;0.1517;0.1800;0.2083;0.2367;0.2650;0.2933;0.3217;0.3500;0.3783;0.4067;0.4350;0.4633;0.4917;0.5200;0.5483;0.5767;0.6050;0.6333;0.6617;0.6900;0.7183;0.7467;0.7750;0.8033;0.8317;0.8600;0.8883;0.9167;1.0000" values="310;310;284.61;269.34;255.29;242.33;229.92;218.74;207.67;197.71;187.99;179.38;170.88;164.11;158.04;153.3;150.53;149.8;150.53;153.3;158.04;164.11;170.88;179.38;187.99;197.71;207.67;218.74;229.92;242.33;255.29;269.34;284.61;284.61"/></circle>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光から出る光線（橙）が放物面で反射して、まっすぐ上（緑）へ → 画像の座標になる<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">半球（180°）を 1 枚に。もう 1 枚で反対側の半球 → 2 枚で全方向。キューブマップ（6 枚）より少ないが、継ぎ目で歪みやすい。</text>
</svg>

<!-- fig:dual-paraboloid:end -->

## 放物面で半球を写す {#projection}

### 式の導出 {#derivation}

光を原点に置き前向きを +Z とします。放物面の鏡を `z = (1 − x² − y²) / 2` とします。原点（焦点）から出た光がこの鏡で反射すると、全部が +Z の向きにそろうという性質があります。つまり、方向 `d = (dx, dy, dz)` の光は鏡で反射した後、`(0, 0, 1)` の向きに進みます。

反射の法則から入射方向と反射方向の中間（ハーフベクトル）が、鏡の法線の向きです。ハーフベクトルは `(dx, dy, dz + 1)` に比例します。一方、鏡の点 `(x, y, z)` での法線は `(x, y, 1)` に比例します。両者を比べて `z` 成分を 1 にそろえると、鏡の上で光が当たる位置の `x`、`y` は次のとおりです。

```text
x = dx / (1 + dz)
y = dy / (1 + dz)
```

この `(x, y)` が円盤の上の座標、つまりシャドウマップの座標です。真正面（`dz = 1`）は `xy = (dx, dy) / 2 = 0` で中心、真横（`dz = 0`）は `xy = (dx, dy)` で長さが 1 の円周になります。後ろ（`dz` が −1 に近づく）は分母が 0 に近づいて円盤の外へ飛びます。前半球だけが半径 1 の円盤に収まるのはこのためで、後半球は別の円盤に分けます。

逆写像も簡単です。円盤の座標 `(u, v)` から `r² = u² + v²` として、方向は次のとおりです。

```text
d = (2u, 2v, 1 − r²) / (1 + r²)
```

前半球の 1000 方向を往復（方向 → 円盤 → 方向）で確かめると、誤差は最大 5e-16 でした。式に間違いはありません。

### 軸からの角と円盤の半径 {#radius}

軸（+Z）からの角を `φ` とすると、`dir.xy` の長さは `sin φ`、`dir.z` は `cos φ` なので円盤の半径は次のとおりです。

```text
r = sin φ / (1 + cos φ) = tan(φ / 2)
```

`φ` が 45° なら `r = 0.4142`、60° なら 0.5774、90° なら 1 です。半径が `tan(φ/2)` で決まるため半球の端に近い角度ほど円盤の上では大きく動きます。これが次の解像度の偏りの原因です。

## 解像度の偏り {#density}

### 面積の倍率 {#density-math}

円盤の面積が半球の立体角に対してどれだけ増えるかを見ます。半径方向の伸びは `dr/dφ = 1 / (2cos²(φ/2))`、円周方向の伸びは `r / sin φ = 1 / (2cos²(φ/2))` で両方が同じです。かけると面積の倍率は次のとおりです。

```text
dA / dΩ = 1 / (4 cos⁴(φ/2))
```

中心（`φ = 0`）で 0.25、半球の縁（`φ = 90°`）で 1 です。縁は中心の 4 倍になります。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="放物面マップの密度"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">放物面マップの密度</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,204.8 75.0,204.8 80.0,204.7 85.0,204.7 90.0,204.7 95.0,204.6 100.0,204.6 105.0,204.5 110.0,204.4 115.0,204.3 120.0,204.2 125.0,204.1 130.0,203.9 135.0,203.8 140.0,203.7 145.0,203.5 150.0,203.3 155.0,203.1 160.0,202.9 165.0,202.7 170.0,202.5 175.0,202.2 180.0,202.0 185.0,201.7 190.0,201.4 195.0,201.1 200.0,200.8 205.0,200.5 210.0,200.1 215.0,199.8 220.0,199.4 225.0,199.0 230.0,198.6 235.0,198.2 240.0,197.7 245.0,197.3 250.0,196.8 255.0,196.3 260.0,195.8 265.0,195.3 270.0,194.7 275.0,194.1 280.0,193.5 285.0,192.9 290.0,192.3 295.0,191.6 300.0,190.9 305.0,190.2 310.0,189.5 315.0,188.7 320.0,187.9 325.0,187.1 330.0,186.2 335.0,185.4 340.0,184.4 345.0,183.5 350.0,182.5 355.0,181.5 360.0,180.4 365.0,179.4 370.0,178.2 375.0,177.1 380.0,175.8 385.0,174.6 390.0,173.3 395.0,171.9 400.0,170.5 405.0,169.1 410.0,167.6 415.0,166.0 420.0,164.4 425.0,162.7 430.0,161.0 435.0,159.2 440.0,157.3 445.0,155.4 450.0,153.3 455.0,151.2 460.0,149.0 465.0,146.8 470.0,144.4 475.0,141.9 480.0,139.4 485.0,136.7 490.0,133.9 495.0,131.1 500.0,128.1 505.0,124.9 510.0,121.7 515.0,118.2 520.0,114.7 525.0,111.0 530.0,107.1 535.0,103.1 540.0,98.8 545.0,94.4 550.0,89.8 555.0,85.0 560.0,79.9 565.0,74.6 570.0,69.0"/><circle cx="70.0" cy="204.8" r="4" fill="#4c8bf5"/><text x="64.0" y="194.76190476190476" text-anchor="start" style="font-size:11px;font-weight:700">×1.00</text><circle cx="320.0" cy="188.0" r="4" fill="#4c8bf5"/><text x="314.0" y="178.02380952380952" text-anchor="end" style="font-size:11px;font-weight:700">×1.37</text><circle cx="403.3" cy="169.5" r="4" fill="#4c8bf5"/><text x="397.3333333333333" y="159.47619047619048" text-anchor="end" style="font-size:11px;font-weight:700">×1.78</text><circle cx="486.7" cy="136.0" r="4" fill="#4c8bf5"/><text x="480.6666666666667" y="126.0" text-anchor="end" style="font-size:11px;font-weight:700">×2.52</text><circle cx="570.0" cy="69.0" r="4" fill="#4c8bf5"/><text x="564.0" y="59.047619047619065" text-anchor="end" style="font-size:11px;font-weight:700">×4.00</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="236.66666666666666" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30°</text><text x="403.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90°</text><text x="62" y="208.76190476190476" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="62" y="163.52380952380952" text-anchor="end" style="font-size:11px;font-weight:400">2</text><text x="62" y="118.28571428571428" text-anchor="end" style="font-size:11px;font-weight:400">3</text><text x="62" y="73.04761904761907" text-anchor="end" style="font-size:11px;font-weight:400">4</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">軸からの角 φ（0° が真正面、90° が半球の縁）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">円盤の面積 / 立体角（中心を 1 とした倍率）</text></svg>

C++ で数えると `φ` が 30° で中心の 1.15 倍、45° で 1.37 倍、60° で 1.78 倍、75° で 2.52 倍、90° で 4.00 倍です。旧版の「中心で高く縁で低い」は逆で、縁のほうが細かく中心のほうが粗いのが正しい向きです。

縁のほうが細かく中心が粗いという偏りは、光の真正面の方向に向かう影ほど荒くなるということです。どの方向の精度が足りなくなるかはシーンの配置で決まります。

### キューブマップとの比べ方 {#density-cube}

キューブマップの 1 面は中心の 1 テクセルが占める立体角を 1 とすると、面の辺の中央で 0.3536、隅で 0.1925（`3^(−1.5)`）になります。中心と隅の比は 5.196 です。放物面の 4 倍より少し偏りが大きい値です。

最悪の場所（もっとも粗い場所）を同じにそろえて比べます。キューブの一辺が 1024 のとき最悪の密度（隅）は 1 ステラジアンあたり約 50450 テクセルです。放物面の最悪の密度は円盤の中心で、直径を `M` とすると `M² / 16` なので、同じにするには `M = 898.4`、つまり 0.877 倍の大きさで足ります。

- キューブマップ（一辺 1024）: 6 面で 6.29M テクセル
- 放物面（直径 898）: 2 枚で 1.61M テクセル
- 比は 3.90

旧版は「メモリが 1/3」と書いていましたが、それは同じ一辺で比べた場合（6 対 2）です。最悪の密度を同じにするなら約 1/3.9 になります。どちらの比べ方でもメモリは放物面のほうが小さいです。ただし、メモリが小さくても使われなくなった理由は、次の歪みにあります。

## 三角形の辺の歪み {#distortion}

### 直線が曲がる {#curve}

放物面の写像は非線形です。3D の直線（三角形の辺）は円盤の上では曲線になります。ところが、ラスタライザーは頂点シェーダーが出力した頂点を画面の上で直線でつないで塗ります。頂点だけを写像すると辺の途中の点は本当の位置から外れた場所に描かれます。

どれくらい外れるかを数えます。軸からの角 60° で方位角が 0° から `a` まで開く辺を考えます。端点を円盤に写して直線でつないだ中点と辺の本当の中点（方向の中点）を写した点の差を、直径 1024 画素の円盤の画素で表します。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="辺の中点のずれ"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">辺の中点のずれ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,250.0 80.8,249.9 97.1,249.3 124.1,247.0 178.1,238.3 311.9,193.6 542.0,71.0"/><circle cx="80.8" cy="249.9" r="4" fill="#e5484d"/><circle cx="97.1" cy="249.3" r="4" fill="#e5484d"/><circle cx="124.1" cy="247.0" r="4" fill="#e5484d"/><circle cx="178.1" cy="238.3" r="4" fill="#e5484d"/><circle cx="311.9" cy="193.6" r="4" fill="#e5484d"/><circle cx="542.0" cy="71.0" r="4" fill="#e5484d"/><text x="170.125" y="228.26222222222222" text-anchor="end" style="font-size:11px;font-weight:700">2.2 画素</text><text x="303.9375" y="183.57" text-anchor="end" style="font-size:11px;font-weight:700">10.7 画素</text><text x="534.0" y="60.97777777777776" text-anchor="end" style="font-size:11px;font-weight:700">33.9 画素</text><line x1="70" y1="244.72222222222223" x2="570" y2="244.72222222222223" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="564" y="238.72222222222223" text-anchor="end" style="font-size:12px;font-weight:400">1 画素</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">20°</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">40°</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">80°</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="201.22222222222223" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="62" y="148.44444444444446" text-anchor="end" style="font-size:11px;font-weight:400">20</text><text x="62" y="95.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">30</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">三角形の辺が光から見て張る角度</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">辺の中点のずれ（画素。直径 1024 画素の円盤）</text></svg>

辺が光から見て 1.73° 張るとき 0.023 画素、4.33° で 0.141 画素、8.66° で 0.561 画素、17.30° で 2.224 画素、38.71° で 10.692 画素、75.52° で 33.920 画素です。ずれは辺の長さの 2 乗に比例して増えます。

実用上の目安はずれが 1 画素以下になる 8° 程度までです。地面のように大きな三角形は光から見ると 90° 近くも張るので、ずれが 30 画素を超えます。影の位置が数十画素ずれ影が壊れます。

### 深度も同じ理由で狂う {#depth}

頂点シェーダーが出す `z`（光からの距離）も頂点の間を画面上で線形に補間されます。本当の距離は辺の上で線形には変わりません。そのため、大きな三角形では距離もずれます。影の判定は保存した距離との比較なので、距離がずれると自己影が出たり影が抜けたりします。

### 対処と限界 {#fix}

- メッシュを細かく切る。影を落とす物だけを細分化しますが、切るにはテッセレーションかジオメトリシェーダーが要り頂点数も増えます。
- 地面のような大きな面は影を落とさず受けるだけにします。受けるだけなら投影するのは頂点ではなく、画素ごとの座標なので歪みません。
- 影を落とす物を小さなメッシュに限ります。

いずれも、使える範囲が限られます。大きな建物や地形が影を落とす場面では、歪みの対処が重く制作側の負担になります。

## 半球の境目 {#seam}

前半球の式を後半球の頂点に使うと半径が 1 を超えます。`dir.z` が −0.1 なら半径 1.106、−0.5 なら 1.732、−0.9 なら 4.359、−0.99 なら 14.107 です。後ろへ行くほど円盤の外へ急に飛びます。そのため、各パスでは反対側の半球の頂点を取り除く必要があります。

<svg class="fig flow" viewBox="0 0 660 350" role="img" aria-label="2 枚の円盤の並べ方"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">円盤の並べ方</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">2 枚の円盤を 1 枚の画像に並べる</text><rect x="50" y="50" width="240" height="240" rx="6" fill="none" stroke="#94a3b8" stroke-width="2"/><circle cx="170" cy="170" r="110" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><circle cx="170" cy="170" r="115" fill="none" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 3"/><text x="170" y="174" text-anchor="middle" style="font-size:13px;font-weight:700">前半球（+Z）</text><text x="170" y="312" text-anchor="middle" style="font-size:11px;font-weight:400">r = 1 が境界（dir.z = 0）</text><rect x="370" y="50" width="240" height="240" rx="6" fill="none" stroke="#94a3b8" stroke-width="2"/><circle cx="490" cy="170" r="110" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><circle cx="490" cy="170" r="115" fill="none" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 3"/><text x="490" y="174" text-anchor="middle" style="font-size:13px;font-weight:700">後半球（-Z）</text><text x="490" y="312" text-anchor="middle" style="font-size:11px;font-weight:400">r = 1 が境界（dir.z = 0）</text><text x="330" y="338" text-anchor="middle" style="font-size:12px;font-weight:400">赤い破線: 境界を少し越えて描く余白（dir.z &gt; -0.05 まで。r は 1.05 まで）</text></svg>

取り除く方法は `SV_ClipDistance` に `dir.z` を出して、負の頂点を含む三角形を切り落とすものです。ただし、半球の境目をまたぐ三角形はそのままだと片方のパスにしか残らず境目に隙間ができます。隙間を避けるため境目を少し越えた分まで描きます（上のコードの `dir.z + 0.05`）。この 0.05 は足した処理で、根拠のある値ではありません。大きな三角形では頂点が境目から遠いとこの余白では足りません。

## シャドウパスと読み取り {#code}

ここからコードです。まず定数と出力です。

```hlsl
// ---- デュアル パラボロイド シャドウ（左手系・Y 上・+Z が前。光の座標系で、前半球は +Z、後半球は -Z）----

cbuffer ParaboloidCB : register(b0) {
  float4x4 gWorldToLight;  // ワールド → 光の座標系（位置を引いて、向きを合わせる。行ベクトルで v * M）
  float    gRange;         // 光の届く距離（m）。深度の正規化に使う
  float    gSide;          // +1: 前半球を描くパス、-1: 後半球を描くパス
  float    gBias;          // 判定のずらし量（正規化した距離）。例: 0.002
  float    gPad;           // 16 バイト境界にそろえる詰め物
};

struct ShadowVSOut {
  float4 pos  : SV_Position;       // 円盤の座標（-1〜1）と、正規化した距離
  float  clip : SV_ClipDistance0;  // 負の頂点は、反対側の半球としてクリップされる
};
```

`gSide` は前半球のパスで +1、後半球のパスで −1 を渡します。後半球は `z` を反転して前半球と同じ式を使います。`SV_ClipDistance0` は負の頂点を含む三角形を切り落とします。

頂点シェーダーです。

```hlsl
// 位置を放物面の円盤へ。戻りの xy が円盤の座標、z が 0〜1 に正規化した距離。w は 1。
ShadowVSOut ShadowVS(float3 position : POSITION) {
  ShadowVSOut o;                                            // 出力
  float3 p = mul(float4(position, 1.0), gWorldToLight).xyz; // 光の座標系の位置
  float dist = max(length(p), 1e-4);                        // 光からの距離（足した: 光の位置の頂点でゼロ除算しない）
  float3 dir = p / dist;                                    // 光から頂点への単位方向
  dir.z *= gSide;                                           // 後半球は z を反転して、前半球と同じ式を使う
  float2 xy = dir.xy / (1.0 + dir.z);                       // 放物面の鏡で反射した位置（前半球で r が 0〜1）
  o.pos = float4(xy, dist / gRange, 1.0);                   // z は距離。w = 1 なので透視除算は何もしない
  o.clip = dir.z + 0.05;                                    // 足した: 境界を少し越えた分も残す（継ぎ目の隙間を埋める）
  return o;
}
```

距離を `gRange` で割って 0〜1 にして `z` に入れます。`w` は 1 なので透視除算で何も変わりません。ここで放物面の式を使っているので、頂点シェーダーが出す `xy` はすでに円盤の座標です。ラスタライザーが行う補間は画面上の線形なので、前節の歪みが出ます。

読み取り側です。

```hlsl
// 影の読み取り側。world_pos の点が、光から見えているか（1: 見える、0: 影）。
Texture2D<float> gFront : register(t0);   // 前半球の距離マップ（正規化した距離を保存）
Texture2D<float> gBack  : register(t1);   // 後半球の距離マップ
SamplerState gPoint : register(s0);       // 点サンプラー（比較サンプラーは使えない）

float ParaboloidShadow(float3 world_pos) {
  float3 p = mul(float4(world_pos, 1.0), gWorldToLight).xyz;   // 光の座標系の位置
  float dist = max(length(p), 1e-4);                           // 光からの距離
  float3 dir = p / dist;                                       // 単位方向
  bool front = dir.z >= 0.0;                                   // どちらの半球に入るか
  float3 d = front ? dir : float3(dir.xy, -dir.z);             // 後半球は z を反転して同じ式へ
  float2 uv = d.xy / (1.0 + d.z);                              // 円盤の座標（-1〜1）
  uv = float2(uv.x * 0.5 + 0.5, 0.5 - uv.y * 0.5);             // テクスチャ座標へ。v は下向きが正
  float stored = front ? gFront.SampleLevel(gPoint, uv, 0)     // 光から最も近い面までの距離
                       : gBack.SampleLevel(gPoint, uv, 0);
  float d_norm = dist / gRange;                                // 今の点の距離
  return d_norm - gBias <= stored ? 1.0 : 0.0;                 // 手前（以下）なら見える。バイアスで自己遮蔽をよける
}
```

読み取りでは頂点ではなく受ける点の位置から画素ごとに座標を求めるので、受ける面の歪みはありません。点が前半球か後半球かを `dir.z` の符号で決め後半球は `z` を反転して同じ式を使います。保存した距離と比べるのでハードウェアの比較サンプラー（PCF）は使えません。点サンプラーで読んで自分で比べます。`gBias` は自己影をよけるずらし量です。値は正規化した距離の単位なので、`gRange` で決まります。

## キューブマップとの比較 {#compare}

| 項目 | キューブマップ | デュアル パラボロイド |
| --- | --- | --- |
| 描画回数 | 6（面ごとのカリングで減らせる） | 2 |
| 歪み | なし | 頂点を写すので辺が歪む |
| 解像度の偏り | 中心と隅で 5.2 倍 | 中心と縁で 4 倍 |
| PCF | 使える | 使えない |
| 同じ最悪密度のメモリ | 6.29M テクセル | 1.61M テクセル |

現在のゲームではキューブマップが標準です。理由は 3 つあります。1 つはキューブマップの 6 面を 1 回のインスタンス描画で描けること（`SV_RenderTargetArrayIndex` で面を選ぶ）で、描画回数の差が小さくなりました（これはこのページでは確かめていない、一般的な知識です）。もう 1 つはキューブマップは歪みがなく、ハードウェアの PCF が使えることです。最後に、面ごとの視錐台カリングで光に近い面だけを描けば、6 回より少なくなります。

## よくあるミス {#mistakes}

??? failure "大きな地面の影が数十画素ずれる"
    原因は頂点だけを写して、辺の途中が曲がらず直線になることです。辺が光から 38° 張ると中点が 10.7 画素ずれます。影を落とす物を細分化するか大きな面は影を受けるだけにします。

??? failure "半球の境目に影の抜けた線が出る"
    原因は境目をまたぐ三角形が、どちらのパスにも十分に残らないことです。`SV_ClipDistance` の閾値を境目より少し後ろ（`dir.z > −0.05` など）にして、余白を取ります。

??? failure "光の位置にある頂点で画面が壊れる"
    原因は頂点が光の位置と一致して、距離が 0 になり方向を求めるときにゼロ除算が起きることです。距離に下限（`max(length(p), 1e-4)`）を入れます。


## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 式は `xy = dir.xy / (1 + dir.z)`。前半球が半径 1 の円盤に収まる
    - [x] 解像度は縁が中心の 4 倍（旧版の向きの記述は逆だった）
    - [x] 同じ最悪密度ならメモリはキューブの約 1/3.9
    - [x] 頂点だけ写すので、大きな三角形で歪む。光から 38° 張る辺で 10.7 画素ずれる
    - [x] 現代ではキューブマップが標準。PCF が使え歪みもない

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

struct V3 { double x, y, z; };             // 3 次元ベクトル

V3 Normalize(V3 v) {                       // 長さ 1 にする
  const double l = std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
  return {v.x / l, v.y / l, v.z / l};
}

// 前半球（dir.z > -1）の放物面投影。戻り値は円盤の座標 (u, v)。
void Project(V3 d, double& u, double& v) {
  u = d.x / (1.0 + d.z);                   // 放物面の鏡で反射させた位置
  v = d.y / (1.0 + d.z);
}

// 逆写像。円盤の座標から方向を戻す。r2 = u^2 + v^2 のとき z = (1 - r2) / (1 + r2)。
V3 Unproject(double u, double v) {
  const double r2 = u * u + v * v;
  const double inv = 1.0 / (1.0 + r2);
  return {2.0 * u * inv, 2.0 * v * inv, (1.0 - r2) * inv};
}

int main() {
  // 1. 往復して元の方向に戻るか（式の確認）。
  std::printf("-- round trip error\n");
  double worst = 0.0;                      // 最大の誤差
  for (int i = 0; i < 1000; ++i) {
    const double az = 2.0 * kPi * i / 1000.0;                 // 方位角
    const double polar = (kPi * 0.5) * (i % 97) / 96.0;       // 軸からの角（0〜90 度）
    const V3 d = {std::sin(polar) * std::cos(az), std::sin(polar) * std::sin(az), std::cos(polar)};
    double u, v;
    Project(d, u, v);
    const V3 e = Unproject(u, v);
    worst = std::max(worst, std::fabs(d.x - e.x) + std::fabs(d.y - e.y) + std::fabs(d.z - e.z));
  }
  std::printf("worst component error = %.2e\n", worst);

  // 2. 半径 r = tan(phi / 2)。軸からの角 phi ごとの、円盤の半径と、立体角あたりの面積の倍率。
  //    dA/dOmega = 1 / (4 cos^4(phi/2))。中心 0.25、縁 (phi = 90 度) 1.0。
  std::printf("-- paraboloid: radius and area density by angle from the axis\n");
  for (double phi_deg : {0.0, 30.0, 45.0, 60.0, 75.0, 90.0}) {
    const double phi = phi_deg / kDeg;
    const double r = std::tan(phi / 2.0);                                   // 円盤の半径
    const double density = 1.0 / (4.0 * std::pow(std::cos(phi / 2.0), 4));  // 面積の倍率
    std::printf("phi=%4.0f deg: r = %.4f, dA/dOmega = %.4f (x%.2f of center)\n", phi_deg, r, density, density / 0.25);
  }

  // 3. キューブマップの 1 面での、立体角あたりの面積の倍率。面の中心 1、隅 3^(-1.5)。
  std::printf("-- cube face: texel solid angle by position on the face (half width 1)\n");
  const double corner = std::pow(3.0, -1.5);
  std::printf("center = 1.0000, edge middle (1, 0) = %.4f, corner (1, 1) = %.4f, center/corner = %.3f\n",
              std::pow(2.0, -1.5), corner, 1.0 / corner);

  // 4. 同じ最悪密度にするための解像度とメモリ。
  //    キューブ（一辺 N）の最悪密度 = N^2 / 4 * 3^(-1.5)（隅）。
  //    放物面（直径 M）の最悪密度 = (M / 2)^2 * 0.25（中心）。
  std::printf("-- same worst-case density: cube N vs paraboloid M\n");
  const double n_cube = 1024.0;                                // キューブの一辺
  const double worst_cube = n_cube * n_cube / 4.0 * corner;    // 最悪密度（texel / sr）
  const double m = std::sqrt(worst_cube * 16.0);               // (M/2)^2 * 0.25 = M^2 / 16
  std::printf("cube N=%.0f: worst density = %.0f texel/sr\n", n_cube, worst_cube);
  std::printf("paraboloid needs M = %.1f (= %.3f N)\n", m, m / n_cube);
  std::printf("memory cube = %.2f M texels, dual paraboloid = %.2f M texels (ratio %.2f)\n",
              6.0 * n_cube * n_cube / 1e6, 2.0 * m * m / 1e6, 6.0 * n_cube * n_cube / (2.0 * m * m));
  std::printf("same size (M = N): cube = %.2f M texels, dual = %.2f M texels (ratio 3)\n", 6.0 * n_cube * n_cube / 1e6,
              2.0 * n_cube * n_cube / 1e6);

  // 5. 三角形の辺の歪み。辺の両端を投影して直線でつないだ中点と、本当の中点（方向の中点）を投影した点の差。
  //    軸からの角 60 度で、方位角が 0 から a まで開く辺。M = 1024 の円盤（直径 1024 画素 = 2 単位）。
  std::printf("-- edge midpoint error (polar 60 deg, map diameter 1024 px)\n");
  const double polar = 60.0 / kDeg;
  for (double a_deg : {2.0, 5.0, 10.0, 20.0, 45.0, 90.0}) {
    const double a = a_deg / kDeg;
    const V3 p = {std::sin(polar), 0.0, std::cos(polar)};                       // 端点 1
    const V3 q = {std::sin(polar) * std::cos(a), std::sin(polar) * std::sin(a), std::cos(polar)};   // 端点 2
    double pu, pv, qu, qv, mu, mv;
    Project(p, pu, pv);
    Project(q, qu, qv);
    const V3 mid = Normalize({p.x + q.x, p.y + q.y, p.z + q.z});               // 辺の本当の中点の方向
    Project(mid, mu, mv);
    const double lu = 0.5 * (pu + qu), lv = 0.5 * (pv + qv);                    // 投影後の端点をつないだ中点
    const double err = std::hypot(mu - lu, mv - lv) * 512.0;                    // 画素に直す（1 単位 = 512 画素）
    // 辺が張る角度（光から見て）。
    const double span = std::acos(p.x * q.x + p.y * q.y + p.z * q.z) * kDeg;
    std::printf("azimuth span %4.0f deg (edge angle %5.2f deg): midpoint error = %7.3f px\n", a_deg, span, err);
  }

  // 6. 境界（dir.z = 0）の外側の頂点。前半球の式を後半球の頂点に使うと、半径が 1 を超える。
  std::printf("-- radius of vertices behind the boundary when using the front formula\n");
  for (double z : {0.0, -0.1, -0.3, -0.5, -0.9, -0.99}) {
    const double s = std::sqrt(1.0 - z * z);                 // 水平成分の長さ
    std::printf("dir.z = %5.2f: r = %7.3f\n", z, s / (1.0 + z));
  }
}
```

```text title="実行結果"
-- round trip error
worst component error = 5.00e-16
-- paraboloid: radius and area density by angle from the axis
phi=   0 deg: r = 0.0000, dA/dOmega = 0.2500 (x1.00 of center)
phi=  30 deg: r = 0.2679, dA/dOmega = 0.2872 (x1.15 of center)
phi=  45 deg: r = 0.4142, dA/dOmega = 0.3431 (x1.37 of center)
phi=  60 deg: r = 0.5774, dA/dOmega = 0.4444 (x1.78 of center)
phi=  75 deg: r = 0.7673, dA/dOmega = 0.6311 (x2.52 of center)
phi=  90 deg: r = 1.0000, dA/dOmega = 1.0000 (x4.00 of center)
-- cube face: texel solid angle by position on the face (half width 1)
center = 1.0000, edge middle (1, 0) = 0.3536, corner (1, 1) = 0.1925, center/corner = 5.196
-- same worst-case density: cube N vs paraboloid M
cube N=1024: worst density = 50450 texel/sr
paraboloid needs M = 898.4 (= 0.877 N)
memory cube = 6.29 M texels, dual paraboloid = 1.61 M texels (ratio 3.90)
same size (M = N): cube = 6.29 M texels, dual = 2.10 M texels (ratio 3)
-- edge midpoint error (polar 60 deg, map diameter 1024 px)
azimuth span    2 deg (edge angle  1.73 deg): midpoint error =   0.023 px
azimuth span    5 deg (edge angle  4.33 deg): midpoint error =   0.141 px
azimuth span   10 deg (edge angle  8.66 deg): midpoint error =   0.561 px
azimuth span   20 deg (edge angle 17.30 deg): midpoint error =   2.224 px
azimuth span   45 deg (edge angle 38.71 deg): midpoint error =  10.692 px
azimuth span   90 deg (edge angle 75.52 deg): midpoint error =  33.920 px
-- radius of vertices behind the boundary when using the front formula
dir.z =  0.00: r =   1.000
dir.z = -0.10: r =   1.106
dir.z = -0.30: r =   1.363
dir.z = -0.50: r =   1.732
dir.z = -0.90: r =   4.359
dir.z = -0.99: r =  14.107
```

## 参考資料 {#references}

このページの式と数字は幾何から導いて C++ で確かめたものです。以下の資料の中身は**今回は読んでいません**。

- Stefan Brabec, Thomas Annen, Hans-Peter Seidel, "Shadow Mapping for Hemispherical and Omnidirectional Light Sources", Advances in Modelling, Animation and Rendering (Computer Graphics International 2002)
- Wolfgang Heidrich, Hans-Peter Seidel, "View-Independent Environment Maps", Eurographics/SIGGRAPH Graphics Hardware Workshop 1998
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

旧版にあった Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading" は、このページの内容と関係がないので、参考資料から外しました。

## 関連ページ {#related}

- [Point and Spot Light Shadows](index.md)
- [Point Lights: Cube Maps](point-cubemap.md)
