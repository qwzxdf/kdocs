---
title: Hair Anti-Aliasing
tags:
  - 描画
---

# Hair Anti-Aliasing

髪の毛 1 本は実際の太さが約 0.05〜0.1 mm と画面の 1 画素に比べて<strong>はるかに細い</strong>ことが普通です。細い物を画素の格子に当てはめて描くと ちらつき途切れジャギーといったエイリアシングが激しく出ます。髪の毛の描画ではエイリアシングが最大の敵の 1 つです。このページではなぜそれが起きるのかカバレッジを使った解決法、MSAA や TAA との付き合い方を説明します。

!!! tip "ポイント"
    - 髪は<strong>1 画素より細い</strong>。画素の中心に当たるか当たらないかで、描かれたり消えたりする。
    - 解決の基本は<strong>幅を最低 1 画素にして、足りない分をアルファで薄める</strong>（カバレッジ）。
    - 髪の毛が画素の何割を覆うか＝ アルファ。細い髪は薄く太い髪は濃く。
    - MSAA は縁に効くが、髪のような細かい物はサンプル数を超えて細い。TAA と併用。
    - 距離で髪を太くする（LOD）と遠くのちらつきが減る。

## なぜ細い物は壊れるのか

ラスタライザは三角形が<strong>画素の中心</strong>を覆うかどうかで、その画素を描くかを決めます。髪の毛のような画素より細い帯は中心を覆うか覆わないかが、位置のわずかなずれで入れ替わります。結果として、次のようなことが起きます。

* 途切れ：1 本の長い髪が、一部の画素で中心を外しちぎれて点線のように見えます。
* ちらつき：カメラやキャラクターが少し動くだけで、描かれる画素が入れ替わり髪がチカチカします。
* ジャギー：斜めに伸びる髪が、階段状のギザギザになります。

ゲームの画面では髪の毛が非常に目立つため、これらの欠点が品質を大きく損ないます。

<!-- fig:hair-coverage:begin -->

<svg class="fig illust motion" data-fig="hair-coverage" viewBox="0 0 780 430" role="img"><rect x="0" y="0" width="780" height="430" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hair-coverage" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">細い髪は、画素の中心で判定すると途切れる。覆う割合で描くと、滑らか</text>
<text x="130" y="98" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">中心で判定（ちらつく）</text>
<text x="130" y="238" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">覆う割合をアルファに（滑らか）</text>
<rect x="130" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="174" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="218" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="262" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1388;0.1391;0.1736;0.1739;1.0000" values="#ffffff;#ffffff;#2e2e2e;#2e2e2e;#ffffff;#ffffff"/></rect>
<rect x="306" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.2953;0.2957;1.0000" values="#ffffff;#ffffff;#2e2e2e;#2e2e2e;#ffffff;#ffffff"/></rect>
<rect x="350" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;0.3997;0.4000;1.0000" values="#ffffff;#ffffff;#2e2e2e;#2e2e2e;#ffffff;#ffffff"/></rect>
<rect x="394" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;0.5214;0.5217;1.0000" values="#ffffff;#ffffff;#2e2e2e;#2e2e2e;#ffffff;#ffffff"/></rect>
<rect x="438" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5910;0.5913;0.6431;0.6435;1.0000" values="#ffffff;#ffffff;#2e2e2e;#2e2e2e;#ffffff;#ffffff"/></rect>
<rect x="482" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7127;0.7130;0.7475;0.7478;1.0000" values="#ffffff;#ffffff;#2e2e2e;#2e2e2e;#ffffff;#ffffff"/></rect>
<rect x="526" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="570" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="614" y="110" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="130" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="174" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="218" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1040;0.1043;0.1214;0.1217;1.0000" values="#ffffff;#ffffff;#989898;#989898;#f0f0f0;#f0f0f0;#ffffff;#ffffff"/></rect>
<rect x="262" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1040;0.1043;0.1214;0.1217;0.1910;0.1913;0.2083;0.2087;0.2257;0.2261;1.0000" values="#ffffff;#ffffff;#989898;#989898;#404040;#404040;#323232;#323232;#5e5e5e;#5e5e5e;#b6b6b6;#b6b6b6;#ffffff;#ffffff"/></rect>
<rect x="306" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.2083;0.2087;0.2257;0.2261;0.3127;0.3130;0.3301;0.3304;0.3475;0.3478;1.0000" values="#ffffff;#ffffff;#d3d3d3;#d3d3d3;#7b7b7b;#7b7b7b;#323232;#323232;#7b7b7b;#7b7b7b;#d3d3d3;#d3d3d3;#ffffff;#ffffff"/></rect>
<rect x="350" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;0.3301;0.3304;0.3475;0.3478;0.4170;0.4174;0.4344;0.4348;0.4518;0.4522;0.4692;0.4696;1.0000" values="#ffffff;#ffffff;#b6b6b6;#b6b6b6;#5e5e5e;#5e5e5e;#323232;#323232;#404040;#404040;#989898;#989898;#f0f0f0;#f0f0f0;#ffffff;#ffffff"/></rect>
<rect x="394" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;0.4344;0.4348;0.4518;0.4522;0.4692;0.4696;0.5388;0.5391;0.5562;0.5565;0.5736;0.5739;1.0000" values="#ffffff;#ffffff;#f0f0f0;#f0f0f0;#989898;#989898;#404040;#404040;#323232;#323232;#5e5e5e;#5e5e5e;#b6b6b6;#b6b6b6;#ffffff;#ffffff"/></rect>
<rect x="438" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;0.5562;0.5565;0.5736;0.5739;0.6605;0.6609;0.6779;0.6783;0.6953;0.6957;1.0000" values="#ffffff;#ffffff;#d3d3d3;#d3d3d3;#7b7b7b;#7b7b7b;#323232;#323232;#7b7b7b;#7b7b7b;#d3d3d3;#d3d3d3;#ffffff;#ffffff"/></rect>
<rect x="482" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6605;0.6609;0.6779;0.6783;0.6953;0.6957;0.7649;0.7652;0.7823;0.7826;1.0000" values="#ffffff;#ffffff;#b6b6b6;#b6b6b6;#5e5e5e;#5e5e5e;#323232;#323232;#404040;#404040;#989898;#989898"/></rect>
<rect x="526" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7649;0.7652;0.7823;0.7826;1.0000" values="#ffffff;#ffffff;#f0f0f0;#f0f0f0;#989898;#989898"/></rect>
<rect x="570" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="614" y="250" width="44" height="44" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="130" y="102" width="3" height="56" fill="#e5484d"><animate attributeName="x" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1043;0.1217;0.1391;0.1565;0.1739;0.1913;0.2087;0.2261;0.2435;0.2609;0.2783;0.2957;0.3130;0.3304;0.3478;0.3652;0.3826;0.4000;0.4174;0.4348;0.4522;0.4696;0.4870;0.5043;0.5217;0.5391;0.5565;0.5739;0.5913;0.6087;0.6261;0.6435;0.6609;0.6783;0.6957;0.7130;0.7304;0.7478;0.7652;0.7826;1.0000" values="130;130;260.5;267.1;273.7;280.3;286.9;293.5;300.1;306.7;313.3;319.9;326.5;333.1;339.7;346.3;352.9;359.5;366.1;372.7;379.3;385.9;392.5;399.1;405.7;412.3;418.9;425.5;432.1;438.7;445.3;451.9;458.5;465.1;471.7;478.3;484.9;491.5;498.1;504.7;511.3;517.9;524.5;524.5"/></rect>
<rect x="130" y="242" width="3" height="56" fill="#e5484d"><animate attributeName="x" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1043;0.1217;0.1391;0.1565;0.1739;0.1913;0.2087;0.2261;0.2435;0.2609;0.2783;0.2957;0.3130;0.3304;0.3478;0.3652;0.3826;0.4000;0.4174;0.4348;0.4522;0.4696;0.4870;0.5043;0.5217;0.5391;0.5565;0.5739;0.5913;0.6087;0.6261;0.6435;0.6609;0.6783;0.6957;0.7130;0.7304;0.7478;0.7652;0.7826;1.0000" values="130;130;260.5;267.1;273.7;280.3;286.9;293.5;300.1;306.7;313.3;319.9;326.5;333.1;339.7;346.3;352.9;359.5;366.1;372.7;379.3;385.9;392.5;399.1;405.7;412.3;418.9;425.5;432.1;438.7;445.3;451.9;458.5;465.1;471.7;478.3;484.9;491.5;498.1;504.7;511.3;517.9;524.5;524.5"/></rect>
<text x="130" y="340" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">赤: 髪の毛（幅 0.35 画素）</text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">髪が画素の間をゆっくり動く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">上: 中心を外すと消える（途切れ・点滅）／ 下: 常に薄く描かれる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.8257;0.8261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">幅を 1 画素に広げ、足りない分をアルファで薄める<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.8257;0.8261;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:hair-coverage:end -->

## カバレッジによる解決

エイリアシングの根本的な解決は画素の「中心を覆うか」を問うのでなく、<strong>画素の面積のうち何割を覆うか</strong>（カバレッジ）を求めそれをアルファにすることです。画素の 30 % を覆う髪は 30 % の濃さで描きます。画素の中心を外れていても一部が画素にかかっていれば、薄く描かれるので途切れや点滅がなくなります。

実装は次のとおりです。ストランドの幅を画面上のピクセルの大きさに換算します。

1. 髪の実際の太さ（ワールド単位）を画面上の幅（画素数）に変換します。遠いほど小さくなります。
2. 画面上の幅が 1 画素未満なら描画する帯の幅を 1 画素に広げ足りない分を アルファで薄めます。たとえば、実際の幅が 0.3 画素なら帯を 1 画素に広げて、アルファを 0.3 にします。
3. 画面上の幅が 1 画素以上ならそのまま描きます。

```hlsl
float pixel_size = clip_w * kPixelSizeInClip;
float world_width = kHairRadius * 2.0;
float width = max(world_width, pixel_size);
float coverage = world_width / width;
```

`width` で帯を展開し `coverage` をアルファに掛けます。

この方法では幅を 1 画素に広げる分、髪の毛の総量（面積）は保たれます。細い髪を 1 画素に広げて薄く描いたものが、多数重なることで細い髪の質感が、柔らかい濃淡として表現されます。

## MSAA との組み合わせ

MSAA（マルチサンプル AA）は 1 画素に複数のサンプル（4〜8 個）を持つので、<strong>サンプル数を単位としたカバレッジ</strong>を扱えます。ストランドを幅 1 画素に広げて描き MSAA のカバレッジでアルファを表現すると、自然な濃淡になります。Alpha to Coverage（A2C）は、アルファの値をサンプルの覆う数に変換する仕組みで、髪のカードにも使えます（[Alpha to Coverage](../../translucency/alpha-test/alpha-to-coverage.md)）。

ただし、MSAA の限界があります。サンプル数が 4〜8 なので、アルファの階調が 4〜8 段階に限られます。髪の毛のようにアルファが 0.1 や 0.05 の薄い物は、サンプルを 1 つも覆わず消えてしまいます。細い髪が多数重なる部分で本来の濃さが出ない場合があります。

そのため、MSAA は 髪の太い部分やカードの縁の AA に有効ですが、細いストランドには不十分なことがあります。

## TAA との組み合わせ

TAA（時間的 AA）は毎フレームカメラを少しずつ揺らして（ジッター）、過去のフレームの結果と混ぜるので、<strong>時間方向にサンプルを増やせます</strong>。1 フレームでは画素を覆わなかった髪も別のフレームでは覆い平均すると、正しい濃さに収束します。細い髪との相性が良く髪の AA では、TAA が決定的に重要です。

髪に TAA を使うときの注意点が、いくつかあります。

ゴースト：髪は頭の動きで速く動くので、前のフレームの髪の位置と今の位置がずれ残像が出ます。髪にも頭と同じ速度ベクトルを書いて、再投影を正しくします（[Velocity Buffer](../../postprocess/motion-blur/velocity-buffer.md)）。ストランドは物理シミュレーションで動くので、各頂点の前フレームの位置を保持して、速度を計算します。

ぼけ：TAA のぼけが髪の細かい筋を甘くします。TAA の後に軽いシャープ化を足して、髪のディテールを戻します（[TAA Challenges](../../postprocess/antialiasing/taa-challenges.md)）。

薄い物の消失：履歴の妥当性を調べる近傍クランプが、細い髪を「外れ値」として履歴から除いてしまうことがあります。髪の領域ではクランプの範囲を広げる（分散クリップの γ を大きくする）ことで、細い髪を残します。

## 距離による調整

髪の毛が遠ざかると 1 本が画面上で非常に小さくなりエイリアシングが悪化します。そこで、距離に応じて髪を<strong>太く少なく</strong>します。

遠くではストランドの本数を減らし（間引き）、残った 1 本ずつを太くします。画面上の総面積（髪の量）は変わらないよう太さを本数の減少に比例して増やします。これにより遠くの髪がチカチカせずに安定します。最終的にさらに遠くではストランドをカードに置き換えます（LOD。[Hair Geometry](geometry.md)）。

## ジャギーとアルファの分離

髪の縁や毛先の AA でもう 1 つの工夫があります。アルファ テストの縁はアルファがしきい値を跨ぐ所で、輪郭がギザギザになります。<strong>アルファのしきい値を距離で調整</strong>し、遠くほどしきい値を下げる（髪が痩せない）ようにします。ハッシュド アルファを使うとしきい値がランダムになり TAA で平均すると、ジャギーが滑らかな濃淡に変わります（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。

## 品質とコストの選択

髪の AA の方式は品質とコストで並べると、次のようになります。

最も軽いのは <strong>アルファ テストのみ</strong>です。ジャギーとちらつきが出ますが、コストは最小で遠景のキャラクターには十分です。次に、A2C ＋ MSAAです。縁が滑らかになり深度順の問題も出ません。MSAA が使えるフォワード系のゲームで標準的です。さらに、ハッシュド アルファ ＋ TAAはディファード系でも使え細い髪を安定させます。TAA 必須でゴーストへの対策が要ります。最も高品質なのはストランドのカバレッジ ＋ TAA ＋ OIT（または、ビジビリティ バッファ）です。細い髪が自然に描けますがコストが大きいです。

## よくあるミス

??? failure "遠くの髪が、ちらついて点滅する"
    ストランドを<strong>最低 1 画素の幅</strong>に広げ 足りない分をアルファで薄める。距離で本数を間引いて太くする。

??? failure "TAA を入れたのに、髪の筋がぼやける"
    髪にも速度ベクトルを書く。TAA の後に軽いシャープ化。クランプの範囲を広げる。

??? failure "A2C を使っても、細い髪が消える"
    MSAA のサンプル数が足りない。髪の幅を広げてカバレッジを増やす。TAA を併用する。

??? failure "遠くで髪が痩せて、頭皮が見える"
    ミップのアルファが薄まっている。カバレッジ保存のミップを作る。遠くは髪を太くする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 髪は<strong>1 画素より細い</strong>。中心判定だと途切れ・ちらつきが出る
    - [x] 幅を最低 1 画素にし、足りない分はアルファで薄める（カバレッジ）
    - [x] MSAA は縁に TAA は細い髪に効く。速度ベクトルとシャープ化が必要
    - [x] 遠くは本数を減らして太くする（LOD）

## 参考

- Wyman, McGuire, "Hashed Alpha Testing"（I3D 2017）
- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014 Advances in Real-Time Rendering）
- AMD GPUOpen, "TressFX" ドキュメント

## 関連ページ

- [Hair Overview](index.md)
- [Hair Geometry](geometry.md)
- [Hair Transparency](transparency.md)
- [TAA](../../postprocess/antialiasing/taa.md)
- [Anti-Aliasing](../../postprocess/antialiasing/index.md)
