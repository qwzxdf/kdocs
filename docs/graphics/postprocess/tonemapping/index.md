---
title: Tone Mapping and Exposure
tags:
  - 描画
---

# Tone Mapping and Exposure

**現実の明るさ**は、**暗い部屋の 0.01 から、太陽の 100,000 まで**、**桁違いの幅**があります。**ディスプレイが出せる範囲**は、<strong>0〜1（LDR）</strong>です。**HDR で計算した光**を、**この狭い範囲に収める**のが**トーンマッピング**で、**その前段で「どれだけ明るく撮るか」＝露出**を決めます。このセクションでは、**露出・各トーンマップ曲線・色相の保ち方・自動露出・ガンマ**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - 流れは<strong>露出（倍率）→ トーンマップ（曲線）→ ガンマ（sRGB）</strong>。<strong>順番を変えない</strong>。
    - <strong>露出</strong> ＝ <strong>光の量への倍率</strong>。<strong>EV が 1 増えると 2 倍</strong>。
    - <strong>トーンマップ</strong> ＝ <strong>HDR → 0〜1 への単調な曲線</strong>。<strong>S 字</strong>が<strong>フィルム</strong>に近い。
    - <strong>曲線の選び方</strong>で<strong>画の性格</strong>（眠い・コントラスト強め・中立）が決まる。
    - <strong>色の保ち方</strong>（チャンネルごと / 輝度ベース）で、<strong>明るい色の見え方</strong>が変わる。
    - <strong>自動露出</strong>は、<strong>平均輝度から目標を決め、時間で滑らかに追従</strong>。

## 流れ

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="トーンマップの流れ">
<text x="20" y="26" class="fig-title">HDR のリニア画像が、画面に出るまで</text>
<defs><marker id="tm-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="60" width="140" height="80" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/>
<text x="90" y="92" text-anchor="middle" style="font-weight:700">HDR の絵</text><text x="90" y="114" text-anchor="middle" style="font-size:11px">0〜数万（リニア）</text>
<rect x="210" y="60" width="140" height="80" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="280" y="92" text-anchor="middle" style="font-weight:700">① 露出</text><text x="280" y="114" text-anchor="middle" style="font-size:11px">× 2^(−EV)</text>
<rect x="400" y="60" width="140" height="80" rx="8" fill="#e5484d" fill-opacity="0.18" stroke="#e5484d" stroke-width="2"/>
<text x="470" y="92" text-anchor="middle" style="font-weight:700">② トーンマップ</text><text x="470" y="114" text-anchor="middle" style="font-size:11px">曲線で 0〜1 へ</text>
<rect x="590" y="60" width="170" height="80" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/>
<text x="675" y="92" text-anchor="middle" style="font-weight:700">③ ガンマ（sRGB）</text><text x="675" y="114" text-anchor="middle" style="font-size:11px">画面へ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="162" y1="100" x2="208" y2="100" marker-end="url(#tm-arrow)"/><line x1="352" y1="100" x2="398" y2="100" marker-end="url(#tm-arrow)"/><line x1="542" y1="100" x2="588" y2="100" marker-end="url(#tm-arrow)"/></g>
<text x="20" y="176" style="font-size:12px">自動露出は、①の倍率を、画面の明るさから毎フレーム決める。</text>
</svg>

## なぜトーンマップが要るのか

現実の明るさは、桁違いに幅広く変化します。晴天の太陽の下は、星明かりの 10 億倍以上明るいと言われます。ゲームの内部では、このような広い明るさの範囲を、HDR のリニア値（0 から数万以上）で計算します。ところが、ディスプレイが出せる明るさは、0 から 1（SDR の場合）の狭い範囲に限られます。この差を埋める処理がトーンマップです。

最も単純な方法は、1 を超える値を 1 に切る（クランプ）ことですが、明るい部分が一様な白に潰れて、階調が失われます。トーンマップは、明るい部分を滑らかに圧縮して、白に向かって「ゆるやかに」近づけます。暗い部分はなるべくそのまま残し、明るい部分を大きく圧縮するこの特性を、カメラのフィルムが光に反応する様子（S 字の特性曲線）が参考にされました。

トーンマップには、もう 1 つ重要な役割があります。それは<strong>画作りの方向性を決める</strong>ことです。同じ HDR の絵でも、選ぶ曲線によって、コントラストの強さ、色の出方、ハイライトの白への向かい方が変わります。このセクションでは、露出（入力の明るさを揃える）から始めて、曲線の種類を順に見て、最後に自動露出と、ディスプレイへの出力を扱います。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Exposure](exposure.md) | EV・絞り／シャッター／ISO・EV100・露出補正 |
| [Reinhard](reinhard.md) | x/(1+x)・白点付き・もっとも簡単な曲線 |
| [Filmic (Hable)](filmic-hable.md) | S 字・肩とつま先・Uncharted 2 の式 |
| [ACES](aces.md) | 映画業界の標準・近似式・色の偏り |
| [AgX and Others](agx.md) | AgX・Tony McMapface・Khronos PBR Neutral |
| [Preserving Hue](hue-preservation.md) | チャンネルごと / 輝度ベース / ハイブリッド |
| [Auto Exposure](auto-exposure.md) | 平均輝度・ヒストグラム・時間追従 |
| [Gamma and HDR Output](gamma-srgb.md) | sRGB・リニア空間・HDR10 への出力 |

## 曲線を動かして比べる

**入力の明るさ x を 0 から増やしたとき、各曲線の出力がどう変わるか**を見ます。

<!-- fig:tonemap-curves:begin -->

<svg class="fig illust motion" data-fig="tonemap-curves" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-curves" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">入力の明るさ x を増やしていくと、出力がどう変わるか</text>
<rect x="50" y="70" width="420" height="250" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="155.0" y1="70" x2="155.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="132.5" x2="470" y2="132.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="260.0" y1="70" x2="260.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="195.0" x2="470" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="365.0" y1="70" x2="365.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="257.5" x2="470" y2="257.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="470" y="340" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">入力 x（HDR）</text>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">出力（0〜1）</text>
<path d="M50.0,320.0 L56.56,288.75 L63.12,257.5 L69.69,226.25 L76.25,195.0 L82.81,163.75 L89.38,132.5 L95.94,101.25 L102.5,70.0 L109.06,70.0 L115.62,70.0 L122.19,70.0 L128.75,70.0 L135.31,70.0 L141.88,70.0 L148.44,70.0 L155.0,70.0 L161.56,70.0 L168.12,70.0 L174.69,70.0 L181.25,70.0 L187.81,70.0 L194.38,70.0 L200.94,70.0 L207.5,70.0 L214.06,70.0 L220.62,70.0 L227.19,70.0 L233.75,70.0 L240.31,70.0 L246.88,70.0 L253.44,70.0 L260.0,70.0 L266.56,70.0 L273.12,70.0 L279.69,70.0 L286.25,70.0 L292.81,70.0 L299.38,70.0 L305.94,70.0 L312.5,70.0 L319.06,70.0 L325.62,70.0 L332.19,70.0 L338.75,70.0 L345.31,70.0 L351.88,70.0 L358.44,70.0 L365.0,70.0 L371.56,70.0 L378.12,70.0 L384.69,70.0 L391.25,70.0 L397.81,70.0 L404.38,70.0 L410.94,70.0 L417.5,70.0 L424.06,70.0 L430.62,70.0 L437.19,70.0 L443.75,70.0 L450.31,70.0 L456.88,70.0 L463.44,70.0 L470.0,70.0" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="5 4"/>
<path d="M50.0,320.0 L56.56,292.22 L63.12,270.0 L69.69,251.82 L76.25,236.67 L82.81,223.85 L89.38,212.86 L95.94,203.33 L102.5,195.0 L109.06,187.65 L115.62,181.11 L122.19,175.26 L128.75,170.0 L135.31,165.24 L141.88,160.91 L148.44,156.96 L155.0,153.33 L161.56,150.0 L168.12,146.92 L174.69,144.07 L181.25,141.43 L187.81,138.97 L194.38,136.67 L200.94,134.52 L207.5,132.5 L214.06,130.61 L220.62,128.82 L227.19,127.14 L233.75,125.56 L240.31,124.05 L246.88,122.63 L253.44,121.28 L260.0,120.0 L266.56,118.78 L273.12,117.62 L279.69,116.51 L286.25,115.45 L292.81,114.44 L299.38,113.48 L305.94,112.55 L312.5,111.67 L319.06,110.82 L325.62,110.0 L332.19,109.22 L338.75,108.46 L345.31,107.74 L351.88,107.04 L358.44,106.36 L365.0,105.71 L371.56,105.09 L378.12,104.48 L384.69,103.9 L391.25,103.33 L397.81,102.79 L404.38,102.26 L410.94,101.75 L417.5,101.25 L424.06,100.77 L430.62,100.3 L437.19,99.85 L443.75,99.41 L450.31,98.99 L456.88,98.57 L463.44,98.17 L470.0,97.78" fill="none" stroke="#2563eb" stroke-width="3" opacity="1"/>
<path d="M50.0,320.0 L56.56,277.32 L63.12,226.47 L69.69,190.47 L76.25,165.92 L82.81,148.66 L89.38,136.05 L95.94,126.5 L102.5,119.05 L109.06,113.1 L115.62,108.24 L122.19,104.21 L128.75,100.8 L135.31,97.9 L141.88,95.39 L148.44,93.21 L155.0,91.29 L161.56,89.58 L168.12,88.07 L174.69,86.7 L181.25,85.47 L187.81,84.36 L194.38,83.34 L200.94,82.42 L207.5,81.56 L214.06,80.78 L220.62,80.05 L227.19,79.38 L233.75,78.76 L240.31,78.18 L246.88,77.63 L253.44,77.12 L260.0,76.65 L266.56,76.2 L273.12,75.77 L279.69,75.38 L286.25,75.0 L292.81,74.64 L299.38,74.31 L305.94,73.99 L312.5,73.68 L319.06,73.39 L325.62,73.12 L332.19,72.85 L338.75,72.6 L345.31,72.36 L351.88,72.13 L358.44,71.91 L365.0,71.7 L371.56,71.5 L378.12,71.3 L384.69,71.12 L391.25,70.94 L397.81,70.76 L404.38,70.6 L410.94,70.44 L417.5,70.28 L424.06,70.13 L430.62,70.0 L437.19,70.0 L443.75,70.0 L450.31,70.0 L456.88,70.0 L463.44,70.0 L470.0,70.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="1"/>
<path d="M50.0,320.0 L56.56,308.21 L63.12,297.09 L69.69,286.71 L76.25,277.01 L82.81,267.93 L89.38,259.43 L95.94,251.44 L102.5,243.92 L109.06,236.84 L115.62,230.16 L122.19,223.83 L128.75,217.85 L135.31,212.17 L141.88,206.78 L148.44,201.65 L155.0,196.77 L161.56,192.12 L168.12,187.68 L174.69,183.44 L181.25,179.38 L187.81,175.5 L194.38,171.78 L200.94,168.22 L207.5,164.8 L214.06,161.51 L220.62,158.35 L227.19,155.31 L233.75,152.38 L240.31,149.56 L246.88,146.84 L253.44,144.22 L260.0,141.69 L266.56,139.25 L273.12,136.88 L279.69,134.6 L286.25,132.39 L292.81,130.24 L299.38,128.17 L305.94,126.16 L312.5,124.21 L319.06,122.32 L325.62,120.49 L332.19,118.71 L338.75,116.98 L345.31,115.3 L351.88,113.67 L358.44,112.08 L365.0,110.53 L371.56,109.03 L378.12,107.56 L384.69,106.14 L391.25,104.75 L397.81,103.39 L404.38,102.07 L410.94,100.79 L417.5,99.53 L424.06,98.31 L430.62,97.11 L437.19,95.94 L443.75,94.8 L450.31,93.69 L456.88,92.6 L463.44,91.53 L470.0,90.49" fill="none" stroke="#2ea043" stroke-width="3" opacity="1"/>
<text x="323.0" y="62.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">クランプは 1 で頭打ち</text>
<line x1="50.0" y1="70" x2="50.0" y2="320" stroke="#e5aa28" stroke-width="2" opacity="1"><animate attributeName="x1" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="50;50;64;78;92;106;120;134;148;162;176;190;204;218;232;246;260;274;288;302;316;330;344;358;372;386;400;414;428;442;456;470;470"/><animate attributeName="x2" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="50;50;64;78;92;106;120;134;148;162;176;190;204;218;232;246;260;274;288;302;316;330;344;358;372;386;400;414;428;442;456;470;470"/></line>
<circle cx="50.0" cy="320.0" r="6" fill="#64748b" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="50;50;64;78;92;106;120;134;148;162;176;190;204;218;232;246;260;274;288;302;316;330;344;358;372;386;400;414;428;442;456;470;470"/><animate attributeName="cy" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="320;320;253.33;186.67;120;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70"/></circle>
<text x="520" y="80" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">クランプ</text>
<rect x="620" y="58" width="110" height="44" fill="#000000" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="#000000;#000000;#8c8c8c;#c0c0c0;#e6e6e6;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff"/></rect>
<circle cx="50.0" cy="320.0" r="6" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="50;50;64;78;92;106;120;134;148;162;176;190;204;218;232;246;260;274;288;302;316;330;344;358;372;386;400;414;428;442;456;470;470"/><animate attributeName="cy" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="320;320;267.37;233.04;208.89;190.97;177.14;166.15;157.21;149.79;143.53;138.18;133.56;129.52;125.97;122.82;120;117.47;115.18;113.1;111.21;109.47;107.88;106.41;105.05;103.78;102.61;101.51;100.49;99.53;98.63;97.78;97.78"/></circle>
<text x="520" y="142" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">Reinhard</text>
<rect x="620" y="120" width="110" height="44" fill="#000000" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="#000000;#000000;#7e7e7e;#9e9e9e;#b0b0b0;#bdbdbd;#c6c6c6;#cdcdcd;#d2d2d2;#d6d6d6;#dadada;#dddddd;#dfdfdf;#e1e1e1;#e3e3e3;#e5e5e5;#e6e6e6;#e8e8e8;#e9e9e9;#eaeaea;#ebebeb;#ececec;#ededed;#ededed;#eeeeee;#efefef;#efefef;#f0f0f0;#f0f0f0;#f1f1f1;#f1f1f1;#f2f2f2;#f2f2f2"/></rect>
<circle cx="50.0" cy="320.0" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="50;50;64;78;92;106;120;134;148;162;176;190;204;218;232;246;260;274;288;302;316;330;344;358;372;386;400;414;428;442;456;470;470"/><animate attributeName="cy" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="320;320;220.83;160.74;131.92;115.72;105.47;98.45;93.34;89.48;86.45;84.01;82.01;80.34;78.92;77.7;76.65;75.72;74.9;74.18;73.52;72.94;72.41;71.93;71.48;71.08;70.71;70.37;70.05;70;70;70;70"/></circle>
<text x="520" y="204" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">ACES</text>
<rect x="620" y="182" width="110" height="44" fill="#000000" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="#000000;#000000;#a7a7a7;#d0d0d0;#e0e0e0;#e9e9e9;#eeeeee;#f1f1f1;#f4f4f4;#f6f6f6;#f7f7f7;#f8f8f8;#f9f9f9;#fafafa;#fbfbfb;#fbfbfb;#fcfcfc;#fcfcfc;#fdfdfd;#fdfdfd;#fdfdfd;#fefefe;#fefefe;#fefefe;#fefefe;#fefefe;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff"/></rect>
<circle cx="50.0" cy="320.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="50;50;64;78;92;106;120;134;148;162;176;190;204;218;232;246;260;274;288;302;316;330;344;358;372;386;400;414;428;442;456;470;470"/><animate attributeName="cy" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="320;320;295.66;274.53;256.17;240.1;225.9;213.28;201.99;191.82;182.61;174.25;166.6;159.6;153.15;147.2;141.69;136.57;131.81;127.36;123.2;119.3;115.63;112.18;108.93;105.86;102.95;100.2;97.58;95.1;92.74;90.49;90.49"/></circle>
<text x="520" y="266" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">Hable</text>
<rect x="620" y="244" width="110" height="44" fill="#000000" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0997;0.1232;0.1467;0.1702;0.1937;0.2171;0.2406;0.2641;0.2876;0.3111;0.3346;0.3581;0.3816;0.4051;0.4286;0.4521;0.4756;0.4990;0.5225;0.5460;0.5695;0.5930;0.6165;0.6400;0.6635;0.6870;0.7105;0.7340;0.7575;0.7810;1.0000" values="#000000;#000000;#585858;#767676;#898989;#989898;#a4a4a4;#adadad;#b5b5b5;#bcbcbc;#c2c2c2;#c8c8c8;#cccccc;#d0d0d0;#d4d4d4;#d8d8d8;#dbdbdb;#dedede;#e0e0e0;#e3e3e3;#e5e5e5;#e7e7e7;#e9e9e9;#eaeaea;#ececec;#eeeeee;#efefef;#f1f1f1;#f2f2f2;#f3f3f3;#f4f4f4;#f5f5f5;#f5f5f5"/></rect>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 0.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;0.0993;0.0997;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 0.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0993;0.0997;0.1228;0.1232;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 0.5<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1228;0.1232;0.1463;0.1467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 0.8<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1463;0.1467;0.1698;0.1702;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 1.1<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1698;0.1702;0.1933;0.1937;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 1.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1937;0.2168;0.2171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 1.6<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2168;0.2171;0.2403;0.2406;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 1.9<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2403;0.2406;0.2637;0.2641;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 2.1<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2637;0.2641;0.2872;0.2876;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 2.4<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2872;0.2876;0.3107;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 2.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3107;0.3111;0.3342;0.3346;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 2.9<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3342;0.3346;0.3577;0.3581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 3.2<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3577;0.3581;0.3812;0.3816;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 3.5<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3812;0.3816;0.4047;0.4051;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 3.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4047;0.4051;0.4282;0.4286;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 4.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4282;0.4286;0.4517;0.4521;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 4.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4517;0.4521;0.4752;0.4756;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 4.5<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4752;0.4756;0.4987;0.4990;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 4.8<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4987;0.4990;0.5222;0.5225;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 5.1<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5222;0.5225;0.5457;0.5460;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 5.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5457;0.5460;0.5691;0.5695;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 5.6<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5691;0.5695;0.5926;0.5930;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 5.9<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5926;0.5930;0.6161;0.6165;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 6.1<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6161;0.6165;0.6396;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 6.4<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6396;0.6400;0.6631;0.6635;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 6.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6631;0.6635;0.6866;0.6870;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 6.9<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6866;0.6870;0.7101;0.7105;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 7.2<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.7101;0.7105;0.7336;0.7340;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 7.5<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.7336;0.7340;0.7571;0.7575;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">入力 x = 7.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.7571;0.7575;0.7806;0.7810;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="360" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">右の四角が、その x を表示した色</text>
</svg>

<!-- fig:tonemap-curves:end -->

グラフの曲線を見比べてください。単純なクランプは、1 で急に頭打ちになるので、明部が真っ白に潰れます。Reinhard はなだらかですが、中間も持ち上がって低コントラストになります。Hable と ACES は、暗部を締めて、明部を滑らかにロールオフさせる S 字になります。

## どれを選ぶか

| 目的 | 選ぶ曲線 |
| --- | --- |
| **とにかく簡単に** | <strong>Reinhard（白点付き）</strong> |
| **映画のような締まった画** | **ACES 近似・Hable** |
| **色が破綻しにくい中立** | **AgX・Khronos PBR Neutral** |
| **画作りを細かく制御** | **独自の曲線を 3D LUT にする**（[カラー グレーディング](../color-grading/index.md)） |

## 関連ページ

- [Post-Processing](../index.md)
- [Bloom](../bloom/index.md)
- [Color Grading](../color-grading/index.md)
- [PBR](../../../3d/pbr.md)
