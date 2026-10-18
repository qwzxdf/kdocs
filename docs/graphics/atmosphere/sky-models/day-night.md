---
title: Day-Night Cycle
tags:
  - 描画
---

# Day-Night Cycle

<strong>時間が進むと太陽が動き空の色・光の色・影の向きが変わります</strong>。<strong>これらを 1 つの「時刻」から連動させる</strong>と、管理が楽です。このページでは昼夜のサイクルを説明します。

!!! tip "ポイント"
    - 時刻 → 太陽の位置 → 空・光・影、が連動。
    - 日の出・日没は色が大きく変わる（オレンジ）。
    - 夜は月と星。
    - 時間経過のコスト（環境マップの更新）に注意。

<!-- fig:day-night:begin -->

<svg class="fig illust motion" data-fig="day-night" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-day-night" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">昼夜のサイクル:時刻から、空・太陽・光の色が、いっせいに変わる</text>
<rect x="40" y="70" width="700" height="230" fill="#0b1224"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2738;0.3238;0.4571;0.5905;0.6571;0.7071;0.7571;0.8571;1.0000" values="#0b1224;#0b1224;#0b1224;#f59e8b;#7dd3fc;#38bdf8;#7dd3fc;#fb923c;#312e81;#0b1224;#0b1224;#0b1224"/></rect>
<rect x="40" y="190" width="700" height="110" fill="#fb923c" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2738;0.3238;0.5905;0.6571;0.7071;0.8571;1.0000" values="0;0;0;0.7;0;0;0.8;0;0;0"/></rect>
<circle cx="70" cy="84" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="167" cy="137" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="264" cy="190" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="361" cy="113" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="458" cy="166" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="555" cy="89" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="652" cy="142" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="109" cy="195" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="206" cy="118" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="303" cy="171" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="400" cy="94" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="497" cy="147" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="594" cy="200" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="691" cy="123" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="148" cy="176" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="245" cy="99" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="342" cy="152" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="439" cy="205" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="536" cy="128" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="633" cy="181" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="90" cy="104" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="187" cy="157" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="284" cy="210" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="381" cy="133" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="478" cy="186" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="575" cy="109" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<rect x="40" y="300" width="700" height="70" fill="#334155"/>
<circle cx="40" cy="300" r="22" fill="#fde68a" opacity="0"><animate attributeName="cx" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.2671;0.2771;0.2871;0.2971;0.3071;0.3171;0.3271;0.3371;0.3471;0.3571;0.3671;0.3771;0.3871;0.3971;0.4071;0.4171;0.4271;0.4371;0.4471;0.4571;0.4671;0.4771;0.4871;0.4971;0.5071;0.5171;0.5271;0.5371;0.5471;0.5571;0.5671;0.5771;0.5871;0.5971;0.6071;0.6171;0.6271;0.6371;0.6471;0.6571;1.0000" values="40;40;70;86;102;118;134;150;166;182;198;214;230;246;262;278;294;310;326;342;358;374;390;406;422;438;454;470;486;502;518;534;550;566;582;598;614;630;646;662;678;694;710;710"/><animate attributeName="cy" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2571;0.2671;0.2771;0.2871;0.2971;0.3071;0.3171;0.3271;0.3371;0.3471;0.3571;0.3671;0.3771;0.3871;0.3971;0.4071;0.4171;0.4271;0.4371;0.4471;0.4571;0.4671;0.4771;0.4871;0.4971;0.5071;0.5171;0.5271;0.5371;0.5471;0.5571;0.5671;0.5771;0.5871;0.5971;0.6071;0.6171;0.6271;0.6371;0.6471;0.6571;1.0000" values="300;300;285.88;271.84;257.98;244.38;231.12;218.28;205.95;194.2;183.1;172.72;163.13;154.38;146.52;139.62;133.7;128.81;124.97;122.22;120.55;120;120.55;122.22;124.97;128.81;133.7;139.62;146.52;154.38;163.13;172.72;183.1;194.2;205.95;218.28;231.12;244.38;257.98;271.84;285.88;300;300"/><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.6569;0.6571;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="40" cy="300" r="16" fill="#e2e8f0" opacity="0"><animate attributeName="cx" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6569;0.6571;0.6671;0.6771;0.6871;0.6971;0.7071;0.7171;0.7271;0.7371;0.7471;0.7571;0.7671;0.7771;0.7871;0.7971;0.8071;0.8171;0.8271;0.8371;0.8471;0.8571;1.0000" values="40;40;70;86;102;118;134;150;166;182;198;214;230;246;262;278;294;310;326;342;358;374;390;390"/><animate attributeName="cy" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6571;0.6671;0.6771;0.6871;0.6971;0.7071;0.7171;0.7271;0.7371;0.7471;0.7571;0.7671;0.7771;0.7871;0.7971;0.8071;0.8171;0.8271;0.8371;0.8471;0.8571;1.0000" values="300;300;285.88;271.84;257.98;244.38;231.12;218.28;205.95;194.2;183.1;172.72;163.13;154.38;146.52;139.62;133.7;128.81;124.97;122.22;120.55;120;120"/><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6569;0.6571;1.0000" values="0;0;1;1"/></circle>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">夜（0〜6 時）:月と星<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.2569;0.2571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">日の出:空がオレンジに染まる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.3236;0.3238;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">昼:青い空。太陽が高い（白い光）<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3236;0.3238;0.5902;0.5905;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">夕方:再びオレンジ、影が長い<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5902;0.5905;0.7069;0.7071;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">夜:星が出る<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.7069;0.7071;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">1 つの「時刻」から、太陽の位置・空の色・光の色・星を計算する。環境光（IBL）も、時刻に合わせて更新する。</text>
</svg>

<!-- fig:day-night:end -->

## 昼夜のサイクル
<strong>時刻から太陽の方向を決める</strong>と、<strong>すべてが連動します</strong>。

```cpp
float time_of_day = std::fmod(game_hours, 24.0f) / 24.0f;
float angle = time_of_day * 2.0f * 3.14159265f - 3.14159265f * 0.5f;
Vector3 sun_direction(std::cos(angle) * 0.3f, std::sin(angle), std::cos(angle) * 0.95f);
sun_direction.Normalize();
```

| 連動する物 | 内容 |
| --- | --- |
| 空の色 | 太陽の方向から自動で |
| 太陽光の色と強さ | 高さで赤く・弱く。地平線の下で 0 |
| 環境光 | 空から更新 |
| 影の向き | 平行光源の向き |
| 月と星 | 夜に現れる |
| フォグの色 | 空の色に合わせる（[Aerial Perspective and Fog](../aerial-fog/index.md)） |

## 時間帯が変わると何が変わるか

<strong>昼から夜へ</strong>、1 日を通して変わるものを整理します。

| 時間帯 | 太陽の高さ | 空 | 光 |
| --- | --- | --- | --- |
| 昼（正午） | 高い | 明るい青 | 白〜やや黄色、強い |
| 朝・夕（日の出・日の入り前後） | 低い | 地平線付近が、橙・赤。反対側は青紫 | 橙〜赤、影が長い |
| 薄明（日没後、約 30〜60 分） | 地平線の下（0〜−18°） | 深い青〜紫。地平線付近だけわずかに明るい | ほぼ、空の光だけ（太陽の直接光は無い） |
| 夜 | −18° 以下 | 暗い。星空 | 月（あれば）、星 |

## 太陽の高さと光の色

<strong>太陽が低い</strong>ほど <strong>光が大気を長く通り</strong>、青から先に散って失われます。赤い光が残るので朝夕の太陽は赤い。

```hlsl
// 太陽の、高さ（天頂角の cos = sun_dir.y）から、地表での、太陽の光の色を求める（大気の透過率を、掛ける）。
float3 SunColorAtGround(float3 sun_dir) {
  float3 ground_pos = float3(0, g_bottom_radius + 1.0, 0);           // 地表に近い点
  return g_sun_illuminance * SunTransmittance(ground_pos, sun_dir);   // 透過率 LUT で、大気を通った、光の色
}
```

<strong>透過率</strong>は <strong>RGB ごと</strong>に、違います（青がよく散る）。太陽の高さに応じて自動的に昼は白、夕方は橙、日没は赤になります。色を手で設定する必要はありません。

## 光の強さ

<strong>太陽の光の強さ</strong>は <strong>高さとともに急に、変わります</strong>。

| 太陽の高さ | 地表の照度（目安、lux） |
| --- | --- |
| 90°（真上） | 約 100,000 |
| 30° | 約 60,000 |
| 10° | 約 10,000 |
| 0°（地平線） | 約 1,000 |
| −6°（市民薄明の終わり） | 約 3 |
| −12° | 約 0.01 |
| 夜（満月） | 約 0.1〜0.3 |
| 夜（月なし） | 約 0.001 |

<strong>対数的</strong>に <strong>桁が変わる</strong>ので、HDR と露出の自動調整（[Auto Exposure](../../postprocess/tonemapping/auto-exposure.md)）がほぼ、必須です。固定の露出では昼が白飛びするか夜が、真っ暗になります。

## 薄明（トワイライト）

<strong>太陽が地平線の下に沈んだ後</strong>も <strong>空は、しばらく明るい</strong>です。大気の高い部分（太陽の光がまだ、当たっている）が光を散乱して地上へ、届けるためです。

| 太陽の高さ | 名前 | 見え方 |
| --- | --- | --- |
| 0° 〜 −6° | 市民薄明 | 空が、明るい。屋外で活動できる |
| −6° 〜 −12° | 航海薄明 | 明るい星が、見える。地平線がぼんやり見える |
| −12° 〜 −18° | 天文薄明 | ほぼ夜。かすかな明るさ |

大気散乱の <strong>物理計算</strong>（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)）は、<strong>多重散乱</strong>とオゾンの吸収を、含めると薄明も自然に再現します（1 回散乱だけでは、足りない。[Multiple Scattering](../scattering/multiple-scattering.md)）。

## 1 日の時間を進める

ゲームでは <strong>1 日を数十分</strong>に、縮めます。<strong>時刻</strong>を一定の速さで進めます。

```cpp
// ゲーム内の時刻（時）を、進める。1 日を day_length_minutes 分に、縮める。
float AdvanceTime(float hour, float dt_seconds, float day_length_minutes) {
  const float hours_per_second = 24.0f / (day_length_minutes * 60.0f);
  hour += dt_seconds * hours_per_second;
  if (hour >= 24.0f) hour -= 24.0f;
  return hour;
}
```

| 設計 | 内容 |
| --- | --- |
| 昼夜の長さを変える | 昼を長く夜を、短く（プレイしやすい）など時間の進みを、時刻に応じて変える |
| 季節 | 日付で太陽の最大の高さ（赤緯）が、変わる（夏は高い） |
| 時刻の固定 | ある場面だけ夕方で、固定（演出） |

## 夜への移行で変えるもの

時刻が進むと <strong>複数のシステムを、連動</strong>させます。

| システム | 変化 |
| --- | --- |
| 空（大気散乱） | LUT を、太陽の位置で更新（Hillaire の方式なら、自動） |
| 太陽の光（方向光） | 向き・色・強さを、透過率から更新 |
| 月の光 | 夜は月を方向光に（太陽が、下がったら月の光に切り替え。または、足す） |
| 環境光（空のライティング） | 空の色から、再計算（[Using the Sky for Lighting](sky-lighting.md)） |
| 星 | 夜にフェード イン（[Sun, Moon and Stars](celestial.md)） |
| 霧（空気遠近法） | 空の色に、合わせて色・強さを変える（[Matching Fog Color to the Sky](../aerial-fog/color-match.md)） |
| 人工の光（街灯、窓） | 夜に点灯 |
| 影 | 太陽が低いと影が、長く（シャドウ マップの範囲、バイアスの調整が必要） |
| 露出 | 自動露出が数秒かけて、追従 |
| 色補正（カラー グレーディング） | 夜は、青みがかり彩度が下がる（人間の目の、暗所での見え方） |

## よくあるミス

??? failure "日没で、影が長くならない・向きが変わらない"
    <strong>太陽の向きを時刻から計算</strong>して、<strong>影</strong>に使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時刻から、すべてを連動させる

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Meeus, "Astronomical Algorithms", Willmann-Bell, 1991（太陽・月の位置の計算）
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Sky Models](index.md)
- [Sun, Moon and Stars](celestial.md)
