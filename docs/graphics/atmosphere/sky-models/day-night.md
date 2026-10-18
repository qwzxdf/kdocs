---
title: Day-Night Cycle
tags:
  - 描画
---

# Day-Night Cycle

**時間が進むと、太陽が動き、空の色・光の色・影の向きが変わります**。**これらを 1 つの「時刻」から連動させる**と、**管理が楽**です。このページでは、**昼夜のサイクル**を説明します。

!!! tip "ポイント"
    - **時刻 → 太陽の位置 → 空・光・影、が連動**。
    - **日の出・日没は、色が大きく変わる**（オレンジ）。
    - **夜は、月と星**。
    - **時間経過のコスト（環境マップの更新）に注意**。

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
**時刻から太陽の方向を決める**と、**すべてが連動します**。

```cpp
float time_of_day = std::fmod(game_hours, 24.0f) / 24.0f;
float angle = time_of_day * 2.0f * 3.14159265f - 3.14159265f * 0.5f;
Vector3 sun_direction(std::cos(angle) * 0.3f, std::sin(angle), std::cos(angle) * 0.95f);
sun_direction.Normalize();
```

| 連動する物 | 内容 |
| --- | --- |
| **空の色** | **太陽の方向から自動で** |
| **太陽光の色と強さ** | **高さで赤く・弱く**。**地平線の下で 0** |
| **環境光** | **空から更新** |
| **影の向き** | **平行光源の向き** |
| **月と星** | **夜に現れる** |
| **フォグの色** | **空の色に合わせる**（[距離フォグ](../aerial-fog/index.md)） |

## よくあるミス

??? failure "日没で、影が長くならない・向きが変わらない"
    **太陽の向きを、時刻から計算**して、**影**に使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **時刻から、すべてを連動させる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky Models](index.md)
- [Sun, Moon and Stars](celestial.md)
