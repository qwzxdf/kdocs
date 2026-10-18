---
title: Gradient Sky
tags:
  - 描画
---

# Gradient Sky

<strong>空の色を上と地平線で変えるだけの、最も簡単な方法</strong>です。<strong>軽く制御しやすい</strong>のでスタイライズされた作品や、モバイルで多用されます。このページではグラデーションの空を説明します。

!!! tip "ポイント"
    - 天頂の色と地平線の色を、視線の高さで補間。
    - 太陽の周りを明るくする。
    - とても軽い。
    - 物理的には正確でない。

## グラデーションの空
<strong>もっとも簡単</strong>なのは <strong>視線の仰角（上下の角度）で、地平線の色と天頂の色を混ぜる</strong>方法です。

```hlsl
float3 GradientSky(float3 view_dir) {
  float elevation = saturate(view_dir.y);
  float t = pow(elevation, 0.5);
  float3 sky = lerp(horizon_color, zenith_color, t);

  float below = saturate(-view_dir.y * 4.0);
  return lerp(sky, ground_color, below);
}
```

| 点 | 説明 |
| --- | --- |
| `pow(elevation, 0.5)` | 地平線付近で色が急に変わる（天頂は広く青い）。空の見た目に近づく |
| 地面の色 | <strong>地平線より下は、地面（暗い色）</strong>で塞ぐ（実際の地面が見えない場合） |
| 太陽の方向で色を寄せる | 太陽のそばを明るく暖色にする（下の「太陽」） |
| 時間帯のプリセット | 朝・昼・夕・夜の色セットを補間 |

<strong>グラデーションは安く・調整しやすい</strong>ですが<strong>太陽の位置で色が変わる</strong>（夕焼けで太陽の側だけ赤い）といった表現は、手作業になります。

<!-- fig:sky-gradient-day:begin -->

<svg class="fig illust motion" data-fig="sky-gradient-day" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sky-gradient-day" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">太陽の高さに合わせて、天頂と地平線の 2 色を入れ替える</text>
<rect x="140" y="70.0" width="500" height="27.0" fill="#2563eb"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#2563eb;#2563eb;#1e3a8a;#1e3a8a;#1e1b4b;#1e1b4b;#020617;#020617"/></rect>
<rect x="140" y="96.0" width="500" height="27.0" fill="#2b67ec"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#2b67ec;#2b67ec;#263d87;#263d87;#231d51;#231d51;#030718;#030718"/></rect>
<rect x="140" y="122.0" width="500" height="27.0" fill="#3570ed"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#3570ed;#3570ed;#354382;#354382;#2c215d;#2c215d;#050a1b;#050a1b"/></rect>
<rect x="140" y="148.0" width="500" height="27.0" fill="#437aef"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#437aef;#437aef;#494b7b;#494b7b;#39266c;#39266c;#070d1e;#070d1e"/></rect>
<rect x="140" y="174.0" width="500" height="27.0" fill="#5387f1"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#5387f1;#5387f1;#5f5473;#5f5473;#472c7e;#472c7e;#0a1022;#0a1022"/></rect>
<rect x="140" y="200.0" width="500" height="27.0" fill="#6595f3"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#6595f3;#6595f3;#7a5e6a;#7a5e6a;#573392;#573392;#0e1426;#0e1426"/></rect>
<rect x="140" y="226.0" width="500" height="27.0" fill="#79a4f5"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#79a4f5;#79a4f5;#966a60;#966a60;#693ba9;#693ba9;#11192b;#11192b"/></rect>
<rect x="140" y="252.0" width="500" height="27.0" fill="#8fb5f8"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#8fb5f8;#8fb5f8;#b67654;#b67654;#7d43c1;#7d43c1;#151e30;#151e30"/></rect>
<rect x="140" y="278.0" width="500" height="27.0" fill="#a6c8fb"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#a6c8fb;#a6c8fb;#d78449;#d78449;#924cdb;#924cdb;#192335;#192335"/></rect>
<rect x="140" y="304.0" width="500" height="27.0" fill="#bfdbfe"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#bfdbfe;#bfdbfe;#fb923c;#fb923c;#a855f7;#a855f7;#1e293b;#1e293b"/></rect>
<rect x="140" y="70" width="500" height="260" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="652" y="84" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">天頂</text>
<text x="652" y="330" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">地平線</text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">空は、天頂色と地平線色の 2 色を混ぜるだけ<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">昼: 天頂は濃い青、地平線は薄い水色<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.2894;0.2897;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">夕方: 地平線がオレンジに<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2894;0.2897;0.5101;0.5103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">夕暮れ: 紫を経て暗くなる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5101;0.5103;0.7308;0.7310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">夜: 天頂も地平線もほぼ黒<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7308;0.7310;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sky-gradient-day:end -->

## 最も単純な空

<strong>グラデーション スカイ</strong>は、<strong>天頂の色</strong>から地平線の色へ、補間するだけの空です。物理計算はありません。非常に軽く自由に色を決められるので、スタイライズされたゲームやモバイルで、よく使われます。

## 実装

視線の <strong>高さ</strong>（上向きか水平か）に応じて、<strong>天頂の色と地平線の色を混ぜます</strong>。

```hlsl
// 視線の向き（正規化）から、空の色を求める。
float3 GradientSky(float3 view_dir) {
  float t = saturate(view_dir.y);                       // 0 = 水平、1 = 真上
```

`view_dir.y` は <strong>視線がどれだけ上を向いているか</strong>（−1〜1）です。<strong>地平線より下</strong>（負）は 0 に、切ります（`saturate`）。

```hlsl
  // 地平線に近いところで、急に色が変わるように、べき乗で曲げる。
  t = pow(t, 0.5);
  return lerp(g_horizon_color, g_zenith_color, t);
}
```

<strong>べき乗</strong>（`pow(t, 0.5)` = 平方根）で、<strong>地平線の近くを広く</strong>取ります。そうしないと地平線の色が狭い帯に、押し込まれ不自然に見えます。現実の空でも地平線の明るい帯は、幅が広いです。

```hlsl
// 地面の方向（view_dir.y < 0）は、別の色で。
float3 sky = GradientSky(view_dir);
float3 ground = g_ground_color;
float3 color = (view_dir.y >= 0.0) ? sky : lerp(g_horizon_color, ground, saturate(-view_dir.y * 4.0));
```

<strong>水平線より下</strong>は <strong>地面の色</strong>へ、移ります。地面が描かれていない（水平線の、下が見える）ならここで補う必要があります。

## 3 色以上のグラデーション

<strong>2 色だけ</strong>では <strong>夕焼けの、複雑な色</strong>を表せません。複数の色を高さの段階で補間します。

```hlsl
// 4 つの色（地平線の下、地平線、中間、天頂）を、高さで、区分線形に、補間する。
float3 MultiGradientSky(float y) {                      // y: −1（真下）〜 1（真上）
  float3 colors[4] = { g_below_horizon, g_horizon, g_mid, g_zenith };
  float stops[4] = { -0.1, 0.0, 0.3, 1.0 };
  for (int i = 0; i < 3; ++i) {
    if (y < stops[i + 1]) {
      float t = saturate((y - stops[i]) / (stops[i + 1] - stops[i]));
      return lerp(colors[i], colors[i + 1], t);
    }
  }
  return colors[3];
}
```

<strong>色と境目の高さ</strong>を <strong>配列</strong>に並べ、該当する区間を探してその区間の、2 色を補間します。色の数を増やすほど自由なグラデーションが、描けます。グラデーションを 1 次元のテクスチャに描いて `SampleLevel` で、引く方法もあります（アーティストが画像で、編集できる）。

## 太陽の方向への変化

空は <strong>太陽の近くが明るく</strong>、<strong>反対側が暗い</strong>ので太陽の方向を、反映するとぐっとそれらしくなります。

```hlsl
// 太陽の方向に近いほど、地平線の色を、太陽の色の方へ、寄せる。
float sun_amount = saturate(dot(view_dir, g_sun_dir));
float3 horizon = lerp(g_horizon_color, g_sun_glow_color, pow(sun_amount, 8.0));
```

`dot(view_dir, g_sun_dir)` は <strong>視線と太陽の近さ</strong>です。<strong>べき乗で太陽の近くだけ</strong>に、絞ります（`pow(…, 8.0)`）。これで太陽の周りのぼんやりした、明るさ（グロー）が出ます。

## 時間帯で色を変える

<strong>1 日の時間</strong>に応じて <strong>色を、補間</strong>します。朝、昼、夕方、夜の色のセット（天頂、地平線、太陽のグロー）を用意して時間で、混ぜます。

```cpp
// 時間帯のキーフレーム（時刻、天頂の色、地平線の色）。
struct SkyKey { float time; float3 zenith; float3 horizon; };
std::vector<SkyKey> keys = {
    {0.0f,  {0.01f, 0.01f, 0.05f}, {0.02f, 0.02f, 0.08f}},     // 深夜
    {6.0f,  {0.20f, 0.30f, 0.60f}, {0.90f, 0.50f, 0.30f}},     // 朝焼け
    {12.0f, {0.10f, 0.30f, 0.80f}, {0.60f, 0.75f, 0.90f}},     // 昼
    {18.0f, {0.20f, 0.25f, 0.50f}, {1.00f, 0.40f, 0.20f}},     // 夕焼け
    {24.0f, {0.01f, 0.01f, 0.05f}, {0.02f, 0.02f, 0.08f}},     // 深夜（0 時と同じ）
};
// 現在の時刻が、どの 2 つの、キーの間にあるかを探し、線形補間する（時間帯の補間）。
```

<strong>時刻</strong>をキーフレームの <strong>間で、補間</strong>するとなめらかに色が変わる空が、できます。キーフレームをアーティストが、編集できるデータにしておくと調整が、楽です（[Day-Night Cycle](day-night.md)）。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 最も軽い（数命令）。アーティストが完全に制御できる。スタイライズに最適 |
| 短所 | 物理的に正しくない。夕焼けの太陽の周りの複雑な色、地平線の霞が出ない |
| 短所 | 太陽の高さに応じた色の変化を手で、設計する必要 |
| 短所 | 空気遠近法（遠景の霞）と色が、合わないことがある（空の色と、霧の色を合わせる。[Matching Fog Color to the Sky](../aerial-fog/color-match.md)） |

## よくあるミス

??? failure "地平線に、色の帯（バンディング）が出る"
    <strong>ディザ</strong>を<strong>加える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高さで色を補間するだけ

## 参考

- Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Sky Models](index.md)
- [Analytic Sky Models](analytic.md)
