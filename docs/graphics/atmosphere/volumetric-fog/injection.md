---
title: Step 2: Light Injection
tags:
  - 描画
---

# Step 2: Light Injection

**各 froxel に、太陽やライトの光を計算して、足します**。**シャドウ マップを参照**して、**影の中は光を入れない**ので、**光の筋ができます**。このページでは、**光の注入**を説明します。

!!! tip "ポイント"
    - **各セルで、ライトの光 × 位相関数 × 影**。
    - **太陽・点光源・スポットライトのすべてに対応**。
    - **シャドウ マップを参照**して、**光の筋**を作る。
    - **ライトの数が多いと、重い**（クラスタ化で軽く）。

<!-- fig:light-injection:begin -->

<svg class="fig illust motion" data-fig="light-injection" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-light-injection" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">光の注入:各セルに、ライトの光 × 影を、書き込む</text>
<rect x="60" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#f0db85;#c7b877;#938c65"/></rect>
<rect x="94" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#fde68a;#c9ba77;#948d65"/></rect>
<rect x="128" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#f0db85;#c7b877;#938c65"/></rect>
<rect x="162" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#e3d081;#c2b475;#918a64"/></rect>
<rect x="196" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#d6c57c;#bbae73;#8d8762"/></rect>
<rect x="230" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c9ba77;#b3a770;#888360"/></rect>
<rect x="264" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#bbae73;#a99f6c;#817d5e"/></rect>
<rect x="298" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#aea36e;#9e9668;#7a775c"/></rect>
<rect x="332" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a19869;#938c65;#727059"/></rect>
<rect x="366" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#948d65;#888360;#696855"/></rect>
<rect x="400" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#878260;#7c795c;#5f6052"/></rect>
<rect x="434" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#7a775c;#706e58;#55584e"/></rect>
<rect x="468" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#6d6c57;#636454;#4b4f4b"/></rect>
<rect x="502" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#606152;#57594f;#334155"/></rect>
<rect x="536" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#52554e;#4b4f4b;#334155"/></rect>
<rect x="570" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#454a49;#3e4446;#334155"/></rect>
<rect x="604" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#383f44;#313942;#334155"/></rect>
<rect x="638" y="80" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#2b3440;#252f3d;#334155"/></rect>
<rect x="60" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#ead683;#d4c37b;#a09769"/></rect>
<rect x="94" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#f0db85;#d6c57c;#a19869"/></rect>
<rect x="128" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#ead683;#d4c37b;#a09769"/></rect>
<rect x="162" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#e0cd80;#cebe79;#9e9568"/></rect>
<rect x="196" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#d4c37b;#c5b776;#999167"/></rect>
<rect x="230" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c7b877;#bbae73;#938c65"/></rect>
<rect x="264" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#baad72;#b1a56f;#8c8662"/></rect>
<rect x="298" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#ada26e;#a59b6b;#84805f"/></rect>
<rect x="332" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a09769;#999167;#7b785c"/></rect>
<rect x="366" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#938c65;#8d8762;#727059"/></rect>
<rect x="400" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#868160;#817d5e;#676755"/></rect>
<rect x="434" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#79765b;#747259;#5d5e51"/></rect>
<rect x="468" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#6c6b57;#676755;#334155"/></rect>
<rect x="502" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#5f6052;#5b5c51;#334155"/></rect>
<rect x="536" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#52554d;#4e524c;#334155"/></rect>
<rect x="570" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#454a49;#414747;#334155"/></rect>
<rect x="604" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#383f44;#343c43;#242e3d"/></rect>
<rect x="638" y="114" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#2b3440;#27313e;#334155"/></rect>
<rect x="60" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#e0cd80;#e0cd80;#ada26e"/></rect>
<rect x="94" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#e3d081;#e3d081;#aea36e"/></rect>
<rect x="128" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#e0cd80;#e0cd80;#ada26e"/></rect>
<rect x="162" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#d8c77d;#d8c77d;#aaa06d"/></rect>
<rect x="196" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#cebe79;#cebe79;#a59b6b"/></rect>
<rect x="230" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c2b475;#c2b475;#9e9668"/></rect>
<rect x="264" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#b6aa71;#b6aa71;#978f66"/></rect>
<rect x="298" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#aaa06d;#aaa06d;#8e8863"/></rect>
<rect x="332" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#9e9568;#9e9568;#84805f"/></rect>
<rect x="366" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#918a64;#918a64;#7a775c"/></rect>
<rect x="400" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#84805f;#84805f;#334155"/></rect>
<rect x="434" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#77755b;#77755b;#334155"/></rect>
<rect x="468" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#6a6a56;#6a6a56;#334155"/></rect>
<rect x="502" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#5d5f51;#5d5f51;#334155"/></rect>
<rect x="536" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#50544d;#50544d;#414747"/></rect>
<rect x="570" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#434948;#434948;#353d43"/></rect>
<rect x="604" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#363e44;#363e44;#29323f"/></rect>
<rect x="638" y="148" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#29333f;#29333f;#334155"/></rect>
<rect x="60" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#d4c37b;#ead683;#baad72"/></rect>
<rect x="94" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#d6c57c;#f0db85;#bbae73"/></rect>
<rect x="128" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#d4c37b;#ead683;#baad72"/></rect>
<rect x="162" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#cebe79;#e0cd80;#b6aa71"/></rect>
<rect x="196" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c5b776;#d4c37b;#b1a56f"/></rect>
<rect x="230" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#bbae73;#c7b877;#a99f6c"/></rect>
<rect x="264" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#b1a56f;#baad72;#a09769"/></rect>
<rect x="298" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a59b6b;#ada26e;#978f66"/></rect>
<rect x="332" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#999167;#a09769;#8c8662"/></rect>
<rect x="366" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#8d8762;#938c65;#334155"/></rect>
<rect x="400" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#817d5e;#868160;#334155"/></rect>
<rect x="434" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#747259;#79765b;#334155"/></rect>
<rect x="468" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#676755;#6c6b57;#5e6052"/></rect>
<rect x="502" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#5b5c51;#5f6052;#52554e"/></rect>
<rect x="536" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#4e524c;#334155;#464b49"/></rect>
<rect x="570" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#414747;#334155;#3a4145"/></rect>
<rect x="604" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#343c43;#334155;#2e3641"/></rect>
<rect x="638" y="182" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#27313e;#334155;#212c3c"/></rect>
<rect x="60" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c7b877;#f0db85;#c7b877"/></rect>
<rect x="94" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c9ba77;#fde68a;#c9ba77"/></rect>
<rect x="128" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c7b877;#f0db85;#c7b877"/></rect>
<rect x="162" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#c2b475;#e3d081;#c2b475"/></rect>
<rect x="196" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#bbae73;#d6c57c;#bbae73"/></rect>
<rect x="230" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#b3a770;#c9ba77;#b3a770"/></rect>
<rect x="264" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a99f6c;#bbae73;#a99f6c"/></rect>
<rect x="298" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#9e9668;#aea36e;#9e9668"/></rect>
<rect x="332" y="216" width="33" height="33" fill="#f1f5f9"/>
<rect x="366" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#334155;#334155"/></rect>
<rect x="400" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#7c795c;#334155;#7c795c"/></rect>
<rect x="434" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#706e58;#334155;#706e58"/></rect>
<rect x="468" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#636454;#334155;#636454"/></rect>
<rect x="502" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#57594f;#334155;#57594f"/></rect>
<rect x="536" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#4b4f4b;#334155;#4b4f4b"/></rect>
<rect x="570" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#3e4446;#334155;#3e4446"/></rect>
<rect x="604" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#313942;#334155;#313942"/></rect>
<rect x="638" y="216" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#252f3d;#334155;#252f3d"/></rect>
<rect x="60" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#baad72;#ead683;#d4c37b"/></rect>
<rect x="94" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#bbae73;#f0db85;#d6c57c"/></rect>
<rect x="128" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#baad72;#ead683;#d4c37b"/></rect>
<rect x="162" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#b6aa71;#e0cd80;#cebe79"/></rect>
<rect x="196" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#b1a56f;#d4c37b;#c5b776"/></rect>
<rect x="230" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a99f6c;#c7b877;#bbae73"/></rect>
<rect x="264" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a09769;#baad72;#b1a56f"/></rect>
<rect x="298" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#978f66;#ada26e;#a59b6b"/></rect>
<rect x="332" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#8c8662;#a09769;#999167"/></rect>
<rect x="366" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#938c65;#8d8762"/></rect>
<rect x="400" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#868160;#817d5e"/></rect>
<rect x="434" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#79765b;#747259"/></rect>
<rect x="468" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#5e6052;#6c6b57;#676755"/></rect>
<rect x="502" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#52554e;#5f6052;#5b5c51"/></rect>
<rect x="536" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#464b49;#52554d;#4e524c"/></rect>
<rect x="570" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#3a4145;#334155;#414747"/></rect>
<rect x="604" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#2e3641;#334155;#343c43"/></rect>
<rect x="638" y="250" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#212c3c;#334155;#27313e"/></rect>
<rect x="60" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#ada26e;#e0cd80;#e0cd80"/></rect>
<rect x="94" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#aea36e;#e3d081;#e3d081"/></rect>
<rect x="128" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#ada26e;#e0cd80;#e0cd80"/></rect>
<rect x="162" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#aaa06d;#d8c77d;#d8c77d"/></rect>
<rect x="196" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a59b6b;#cebe79;#cebe79"/></rect>
<rect x="230" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#9e9668;#c2b475;#c2b475"/></rect>
<rect x="264" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#978f66;#b6aa71;#b6aa71"/></rect>
<rect x="298" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#8e8863;#aaa06d;#aaa06d"/></rect>
<rect x="332" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#84805f;#9e9568;#9e9568"/></rect>
<rect x="366" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#7a775c;#918a64;#918a64"/></rect>
<rect x="400" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#84805f;#84805f"/></rect>
<rect x="434" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#77755b;#77755b"/></rect>
<rect x="468" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#6a6a56;#6a6a56"/></rect>
<rect x="502" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#5d5f51;#5d5f51"/></rect>
<rect x="536" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#414747;#50544d;#50544d"/></rect>
<rect x="570" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#353d43;#434948;#434948"/></rect>
<rect x="604" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#29323f;#363e44;#363e44"/></rect>
<rect x="638" y="284" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#29333f;#29333f"/></rect>
<rect x="60" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a09769;#d4c37b;#ead683"/></rect>
<rect x="94" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a19869;#d6c57c;#f0db85"/></rect>
<rect x="128" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#a09769;#d4c37b;#ead683"/></rect>
<rect x="162" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#9e9568;#cebe79;#e0cd80"/></rect>
<rect x="196" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#999167;#c5b776;#d4c37b"/></rect>
<rect x="230" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#938c65;#bbae73;#c7b877"/></rect>
<rect x="264" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#8c8662;#b1a56f;#baad72"/></rect>
<rect x="298" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#84805f;#a59b6b;#ada26e"/></rect>
<rect x="332" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#7b785c;#999167;#a09769"/></rect>
<rect x="366" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#727059;#8d8762;#938c65"/></rect>
<rect x="400" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#676755;#817d5e;#868160"/></rect>
<rect x="434" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#5d5e51;#747259;#79765b"/></rect>
<rect x="468" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#676755;#6c6b57"/></rect>
<rect x="502" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#5b5c51;#5f6052"/></rect>
<rect x="536" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#4e524c;#52554d"/></rect>
<rect x="570" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#414747;#454a49"/></rect>
<rect x="604" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#242e3d;#343c43;#383f44"/></rect>
<rect x="638" y="318" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#27313e;#2b3440"/></rect>
<rect x="60" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#938c65;#c7b877;#f0db85"/></rect>
<rect x="94" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#948d65;#c9ba77;#fde68a"/></rect>
<rect x="128" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#938c65;#c7b877;#f0db85"/></rect>
<rect x="162" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#918a64;#c2b475;#e3d081"/></rect>
<rect x="196" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#8d8762;#bbae73;#d6c57c"/></rect>
<rect x="230" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#888360;#b3a770;#c9ba77"/></rect>
<rect x="264" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#817d5e;#a99f6c;#bbae73"/></rect>
<rect x="298" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#7a775c;#9e9668;#aea36e"/></rect>
<rect x="332" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#727059;#938c65;#a19869"/></rect>
<rect x="366" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#696855;#888360;#948d65"/></rect>
<rect x="400" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#5f6052;#7c795c;#878260"/></rect>
<rect x="434" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#55584e;#706e58;#7a775c"/></rect>
<rect x="468" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#4b4f4b;#636454;#6d6c57"/></rect>
<rect x="502" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#57594f;#606152"/></rect>
<rect x="536" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#4b4f4b;#52554e"/></rect>
<rect x="570" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#3e4446;#454a49"/></rect>
<rect x="604" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#313942;#383f44"/></rect>
<rect x="638" y="352" width="33" height="33" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="#f1f5f9;#334155;#252f3d;#2b3440"/></rect>
<rect x="332" y="216" width="33" height="33" fill="#78716c"/>
<text x="349.0" y="237" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">物</text>
<circle cx="111.0" cy="97.0" r="11" fill="#e5aa28" stroke="#ffffff" stroke-width="2"><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.3333;0.5926" values="97;97;233;369"/></circle>
<text x="60" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ライトを動かすと、セルの明るさ・影が、書き換わる（光の柱ができる）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3330;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ライトを動かすと、セルの明るさ・影が、書き換わる（光の柱ができる）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;0.5923;0.5926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ライトを動かすと、セルの明るさ・影が、書き換わる（光の柱ができる）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5923;0.5926;0.8516;0.8519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">明るい黄 = ライトの光が届くセル（距離で減衰）。濃い灰 = 物の影になっているセル。影は、シャドウ マップで調べる。</text>
</svg>

<!-- fig:light-injection:end -->

## ② 光の注入
**各 froxel が受けている光を計算します**。<strong>太陽光とローカル ライト（点光源・スポットライト）</strong>が**対象**です。

<div class="formula">散乱光 = 密度 × アルベド × Σ ( 光の色 × 影 × 位相関数(θ) )</div>

```hlsl
float3 inscattered = 0;

float shadow = SampleCascadeShadow(world_position);
float phase = HenyeyGreenstein(dot(view_dir, -sun_direction), g);
inscattered += sun_color * shadow * phase;

for (uint i = 0; i < light_count; ++i) {
  float3 to_light = lights[i].position - world_position;
  float distance_to_light = length(to_light);
  float3 light_dir = to_light / distance_to_light;
  float attenuation = LightAttenuation(lights[i], distance_to_light);
  float light_shadow = SampleLocalShadow(lights[i], world_position);
  float p = HenyeyGreenstein(dot(view_dir, -light_dir), g);
  inscattered += lights[i].color * attenuation * light_shadow * p;
}

inscattered += ambient_fog_color;
float3 scattering = inscattered * density * albedo;
```

| 点 | 説明 |
| --- | --- |
| **シャドウ マップを引く** | **影の中の霧は光らない**。**この結果、物の影が光の筋として見える** |
| **位相関数** | <strong>前方に強く散る（g ≈ 0.6〜0.8）</strong>。**太陽の方を見ると霧が明るい**（[大気散乱](../scattering/index.md)） |
| **環境光** | **全体にうっすら足す**（暗すぎる霧の防止） |
| **ライトの数が多い場合** | **froxel ごとにライトをカリング**（[ライト カリング](../../../rendering/light-culling.md)） |
| **解像度が低くても綺麗** | **霧は低周波**（細かい構造がない）ので低解像度で十分 |

## よくあるミス

??? failure "光の筋が出ない"
    **シャドウ マップを参照**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **セルごとに、ライトと影を計算**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [密度](density.md)
- [積分](integration.md)
