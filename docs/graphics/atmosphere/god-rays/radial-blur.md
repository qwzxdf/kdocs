---
title: Screen-Space Radial Blur
tags:
  - 描画
---

# Screen-Space Radial Blur

<strong>太陽の画面上の位置から外側へ、画像を放射状にぼかして光の筋を作る</strong>のが<strong>最も手軽</strong>な方法です。太陽が画面内にある時だけ使え、遮蔽物の形が筋に反映されます。このページでは放射ぼかしを説明します。

!!! tip "ポイント"
    - 明るい部分を抽出し、太陽の位置から放射状にぼかす。
    - 遮蔽物の影が筋として現れる。
    - 太陽が画面外にあると、使えない。
    - サンプル数が少ないと、縞が出る。

<!-- fig:radial-streak:begin -->

<svg class="fig illust motion" data-fig="radial-streak" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-radial-streak" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">放射ぼかし: 光源から画素へ向かう線の上で、何回か読んで足す。読む回数が少ないと、筋が途切れる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">光源から 1 本の線(48 画素)。途中に細い遮蔽物が 3 本。各画素が、光源の方向へ N 回読んで、明るさを足す</text>
<text x="60.0" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">遮る物(黒)と、光(白)。左端が光源に近い</text>
<rect x="60.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="77.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="94.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="111.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="128.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="145.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="162.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="179.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="196.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="213.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="230.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#111827"/></rect>
<rect x="247.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#111827"/></rect>
<rect x="264.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="281.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="298.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="315.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="332.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="349.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="366.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="383.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="400.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="417.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="434.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#111827"/></rect>
<rect x="451.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#111827"/></rect>
<rect x="468.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#111827"/></rect>
<rect x="485.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="502.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="519.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="536.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="553.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="570.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="587.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="604.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="621.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="638.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="655.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="672.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#111827"/></rect>
<rect x="689.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="706.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="723.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="740.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="757.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="774.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="791.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="808.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="825.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="842.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="859.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#fef3c7"/></rect>
<rect x="60.0" y="106" width="816.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="156" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">N = 4</text>
<rect x="60.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#535353"/></rect>
<rect x="77.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#535353"/></rect>
<rect x="94.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#535353"/></rect>
<rect x="111.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#535353"/></rect>
<rect x="128.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#535353"/></rect>
<rect x="145.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#535353"/></rect>
<rect x="162.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#535353"/></rect>
<rect x="179.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#535353"/></rect>
<rect x="196.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#535353"/></rect>
<rect x="213.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#535353"/></rect>
<rect x="230.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#535353"/></rect>
<rect x="247.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#535353"/></rect>
<rect x="264.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#898989"/></rect>
<rect x="281.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#898989"/></rect>
<rect x="298.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#535353"/></rect>
<rect x="315.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#818181"/></rect>
<rect x="332.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#818181"/></rect>
<rect x="349.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#818181"/></rect>
<rect x="366.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#535353"/></rect>
<rect x="383.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#535353"/></rect>
<rect x="400.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="417.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="434.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="451.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1076" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="468.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#e5e7eb;#535353"/></rect>
<rect x="485.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#898989"/></rect>
<rect x="502.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1129" values="#e5e7eb;#898989"/></rect>
<rect x="519.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#e5e7eb;#898989"/></rect>
<rect x="536.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#e5e7eb;#535353"/></rect>
<rect x="553.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1182" values="#e5e7eb;#535353"/></rect>
<rect x="570.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#535353"/></rect>
<rect x="587.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1218" values="#e5e7eb;#535353"/></rect>
<rect x="604.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1236" values="#e5e7eb;#818181"/></rect>
<rect x="621.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#e5e7eb;#818181"/></rect>
<rect x="638.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="655.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="672.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#e5e7eb;#737373"/></rect>
<rect x="689.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1324" values="#e5e7eb;#737373"/></rect>
<rect x="706.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1342" values="#e5e7eb;#737373"/></rect>
<rect x="723.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#e5e7eb;#737373"/></rect>
<rect x="740.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#a9a9a9"/></rect>
<rect x="757.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1396" values="#e5e7eb;#898989"/></rect>
<rect x="774.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#e5e7eb;#535353"/></rect>
<rect x="791.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1431" values="#e5e7eb;#535353"/></rect>
<rect x="808.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1449" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="825.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="842.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1484" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="859.0" y="160.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1502" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="60.0" y="160" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><text x="884.0" y="178" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">ずれ 0.072</text>
</g>
<text x="60.0" y="210" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">N = 8</text>
<rect x="60.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2178" values="#e5e7eb;#535353"/></rect>
<rect x="77.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2196" values="#e5e7eb;#535353"/></rect>
<rect x="94.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2213" values="#e5e7eb;#535353"/></rect>
<rect x="111.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2231" values="#e5e7eb;#535353"/></rect>
<rect x="128.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2249" values="#e5e7eb;#535353"/></rect>
<rect x="145.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2267" values="#e5e7eb;#535353"/></rect>
<rect x="162.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2284" values="#e5e7eb;#535353"/></rect>
<rect x="179.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2302" values="#e5e7eb;#535353"/></rect>
<rect x="196.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2320" values="#e5e7eb;#535353"/></rect>
<rect x="213.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2338" values="#e5e7eb;#535353"/></rect>
<rect x="230.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2356" values="#e5e7eb;#535353"/></rect>
<rect x="247.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2373" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="264.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391" values="#e5e7eb;#898989"/></rect>
<rect x="281.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2409" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="298.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2427" values="#e5e7eb;#858585"/></rect>
<rect x="315.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2444" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="332.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2462" values="#e5e7eb;#696969"/></rect>
<rect x="349.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2480" values="#e5e7eb;#696969"/></rect>
<rect x="366.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2498" values="#e5e7eb;#696969"/></rect>
<rect x="383.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2516" values="#e5e7eb;#676767"/></rect>
<rect x="400.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2533" values="#e5e7eb;#676767"/></rect>
<rect x="417.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2551" values="#e5e7eb;#676767"/></rect>
<rect x="434.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2569" values="#e5e7eb;#535353"/></rect>
<rect x="451.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2587" values="#e5e7eb;#666666"/></rect>
<rect x="468.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2604" values="#e5e7eb;#818181"/></rect>
<rect x="485.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2622" values="#e5e7eb;#818181"/></rect>
<rect x="502.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2640" values="#e5e7eb;#9b9b9b"/></rect>
<rect x="519.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="536.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2676" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="553.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="570.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="587.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="604.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="621.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="638.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="655.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#696969"/></rect>
<rect x="672.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#696969"/></rect>
<rect x="689.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#696969"/></rect>
<rect x="706.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#858585"/></rect>
<rect x="723.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#535353"/></rect>
<rect x="740.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#777777"/></rect>
<rect x="757.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#777777"/></rect>
<rect x="774.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#777777"/></rect>
<rect x="791.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#919191"/></rect>
<rect x="808.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#777777"/></rect>
<rect x="825.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#777777"/></rect>
<rect x="842.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#e5e7eb;#626262"/></rect>
<rect x="859.0" y="214.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#e5e7eb;#626262"/></rect>
<rect x="60.0" y="214" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3065;0.3067;1.0000" values="0;0;1;1"/><text x="884.0" y="232" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">ずれ 0.033</text>
</g>
<text x="60.0" y="264" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">N = 16</text>
<rect x="60.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#e5e7eb;#535353"/></rect>
<rect x="77.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3707" values="#e5e7eb;#535353"/></rect>
<rect x="94.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3724" values="#e5e7eb;#535353"/></rect>
<rect x="111.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3742" values="#e5e7eb;#535353"/></rect>
<rect x="128.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3760" values="#e5e7eb;#535353"/></rect>
<rect x="145.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778" values="#e5e7eb;#535353"/></rect>
<rect x="162.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3796" values="#e5e7eb;#535353"/></rect>
<rect x="179.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#535353"/></rect>
<rect x="196.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3831" values="#e5e7eb;#535353"/></rect>
<rect x="213.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3849" values="#e5e7eb;#535353"/></rect>
<rect x="230.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3867" values="#e5e7eb;#535353"/></rect>
<rect x="247.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3884" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="264.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3902" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="281.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3920" values="#e5e7eb;#797979"/></rect>
<rect x="298.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3938" values="#e5e7eb;#787878"/></rect>
<rect x="315.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3956" values="#e5e7eb;#777777"/></rect>
<rect x="332.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#757575"/></rect>
<rect x="349.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3991" values="#e5e7eb;#696969"/></rect>
<rect x="366.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4009" values="#e5e7eb;#686868"/></rect>
<rect x="383.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4027" values="#e5e7eb;#686868"/></rect>
<rect x="400.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4044" values="#e5e7eb;#676767"/></rect>
<rect x="417.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4062" values="#e5e7eb;#5d5d5d"/></rect>
<rect x="434.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4080" values="#e5e7eb;#676767"/></rect>
<rect x="451.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4098" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="468.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4116" values="#e5e7eb;#818181"/></rect>
<rect x="485.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#818181"/></rect>
<rect x="502.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4151" values="#e5e7eb;#777777"/></rect>
<rect x="519.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4169" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="536.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4187" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="553.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4204" values="#e5e7eb;#757575"/></rect>
<rect x="570.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4222" values="#e5e7eb;#757575"/></rect>
<rect x="587.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="604.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4258" values="#e5e7eb;#737373"/></rect>
<rect x="621.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4276" values="#e5e7eb;#727272"/></rect>
<rect x="638.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="#e5e7eb;#727272"/></rect>
<rect x="655.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4311" values="#e5e7eb;#676767"/></rect>
<rect x="672.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="#e5e7eb;#727272"/></rect>
<rect x="689.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4347" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="706.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4364" values="#e5e7eb;#666666"/></rect>
<rect x="723.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4382" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="740.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4400" values="#e5e7eb;#656565"/></rect>
<rect x="757.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4418" values="#e5e7eb;#656565"/></rect>
<rect x="774.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4436" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="791.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4453" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="808.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4471" values="#e5e7eb;#6a6a6a"/></rect>
<rect x="825.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4489" values="#e5e7eb;#646464"/></rect>
<rect x="842.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4507" values="#e5e7eb;#646464"/></rect>
<rect x="859.0" y="268.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4524" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="60.0" y="268" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4576;0.4578;1.0000" values="0;0;1;1"/><text x="884.0" y="286" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ずれ 0.020</text>
</g>
<text x="60.0" y="318" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">N = 64</text>
<rect x="60.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5200" values="#e5e7eb;#535353"/></rect>
<rect x="77.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5218" values="#e5e7eb;#535353"/></rect>
<rect x="94.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5236" values="#e5e7eb;#535353"/></rect>
<rect x="111.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5253" values="#e5e7eb;#535353"/></rect>
<rect x="128.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5271" values="#e5e7eb;#535353"/></rect>
<rect x="145.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5289" values="#e5e7eb;#535353"/></rect>
<rect x="162.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5307" values="#e5e7eb;#535353"/></rect>
<rect x="179.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5324" values="#e5e7eb;#535353"/></rect>
<rect x="196.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5342" values="#e5e7eb;#535353"/></rect>
<rect x="213.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5360" values="#e5e7eb;#535353"/></rect>
<rect x="230.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5378" values="#e5e7eb;#535353"/></rect>
<rect x="247.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5396" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="264.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5413" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="281.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5431" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="298.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5449" values="#e5e7eb;#787878"/></rect>
<rect x="315.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5467" values="#e5e7eb;#747474"/></rect>
<rect x="332.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5484" values="#e5e7eb;#707070"/></rect>
<rect x="349.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5502" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="366.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5520" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="383.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5538" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="400.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5556" values="#e5e7eb;#676767"/></rect>
<rect x="417.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5573" values="#e5e7eb;#676767"/></rect>
<rect x="434.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5591" values="#e5e7eb;#676767"/></rect>
<rect x="451.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5609" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="468.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5627" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="485.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5644" values="#e5e7eb;#838383"/></rect>
<rect x="502.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5662" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="519.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5680" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="536.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5698" values="#e5e7eb;#787878"/></rect>
<rect x="553.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5716" values="#e5e7eb;#777777"/></rect>
<rect x="570.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5733" values="#e5e7eb;#777777"/></rect>
<rect x="587.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5751" values="#e5e7eb;#767676"/></rect>
<rect x="604.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5769" values="#e5e7eb;#727272"/></rect>
<rect x="621.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5787" values="#e5e7eb;#757575"/></rect>
<rect x="638.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5804" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="655.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5822" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="672.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5840" values="#e5e7eb;#717171"/></rect>
<rect x="689.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5858" values="#e5e7eb;#737373"/></rect>
<rect x="706.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5876" values="#e5e7eb;#757575"/></rect>
<rect x="723.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5893" values="#e5e7eb;#727272"/></rect>
<rect x="740.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5911" values="#e5e7eb;#717171"/></rect>
<rect x="757.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5929" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="774.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5947" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="791.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5964" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="808.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5982" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="825.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6000" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="842.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6018" values="#e5e7eb;#6a6a6a"/></rect>
<rect x="859.0" y="322.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6036" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="60.0" y="322" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6087;0.6089;1.0000" values="0;0;1;1"/><text x="884.0" y="340" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">ずれ 0.004</text>
</g>
<text x="60.0" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">正解(N = 512)</text>
<rect x="60.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="77.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="94.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="111.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="128.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="145.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="162.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="179.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="196.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="213.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="230.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="247.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="264.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#808080"/></rect>
<rect x="281.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="298.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#777777"/></rect>
<rect x="315.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#737373"/></rect>
<rect x="332.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#707070"/></rect>
<rect x="349.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="366.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="383.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#696969"/></rect>
<rect x="400.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#676767"/></rect>
<rect x="417.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="434.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#656565"/></rect>
<rect x="451.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#707070"/></rect>
<rect x="468.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="485.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#838383"/></rect>
<rect x="502.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#808080"/></rect>
<rect x="519.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="536.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="553.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#797979"/></rect>
<rect x="570.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#777777"/></rect>
<rect x="587.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#767676"/></rect>
<rect x="604.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#747474"/></rect>
<rect x="621.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#727272"/></rect>
<rect x="638.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#717171"/></rect>
<rect x="655.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#707070"/></rect>
<rect x="672.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="689.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#757575"/></rect>
<rect x="706.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#747474"/></rect>
<rect x="723.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#727272"/></rect>
<rect x="740.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#717171"/></rect>
<rect x="757.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#717171"/></rect>
<rect x="774.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="791.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="808.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="825.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="842.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="859.0" y="376.0" width="17.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="60.0" y="376" width="816.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="440" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込み(1 画素あたり):</text>
<text x="240" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="240" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2176;0.2178;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2176;0.2178;0.3687;0.3689;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3687;0.3689;0.5198;0.5200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">64<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5198;0.5200;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6576;0.6578;1.0000" values="0;0;1;1"/><rect x="330" y="424" width="600" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="448" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">N が少ないと、筋が、飛び飛びの点線のようになる(ずれ 0.072)。N = 64 で、ほぼなめらか(0.004)</text>
<text x="346" y="471" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ふつうは N = 32〜64。読み込みは、画面全体 × N なので、重い。ジッターで、帯を、ノイズに変える手もある</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光源に向かう線の上を、少しずつ読んで、明るさを足す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">読む回数が少ないと、遮蔽物の影が、飛び飛びになる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.6709;0.6711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">回数を増やすと、筋がなめらかになる(コストも増える)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6709;0.6711;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:radial-streak:end -->

## 画面空間の放射ぼかし
<strong>画面上の太陽の位置を中心に、各ピクセルから太陽へ向かう直線上の明るさを、何度かサンプルして足し合わせる</strong>方法です。<strong>簡単・安価で古くから使われています</strong>。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="放射ぼかし">
<text x="20" y="24" class="fig-title">放射ぼかし：各ピクセルから太陽に向かって、明るさを平均する</text>
<rect x="60" y="50" width="360" height="160" fill="#87ceeb" fill-opacity="0.2" stroke="currentColor" stroke-opacity="0.5"/>
<circle cx="360" cy="80" r="14" fill="#e5aa28"/>
<polygon points="120,210 160,100 190,210" fill="#333"/><polygon points="220,210 240,120 270,210" fill="#333"/>
<g stroke="#e5aa28" stroke-dasharray="4 3"><line x1="150" y1="180" x2="360" y2="80"/><line x1="250" y1="190" x2="360" y2="80"/></g>
<circle cx="150" cy="180" r="4" fill="#e5484d"/><circle cx="250" cy="190" r="4" fill="#e5484d"/>
<g font-size="12">
<text x="450" y="80" style="font-weight:700">手順</text>
<text x="450" y="104">① 太陽の画面上の位置を求める</text>
<text x="450" y="126">② 明るい所（空）を別の画像に抜き出す（物は黒）</text>
<text x="450" y="148">③ 各ピクセルから太陽へ向かう線上を、</text><text x="450" y="166">　 数十回サンプルして足す（減衰しながら）</text>
<text x="450" y="188">④ 元の絵に加算</text>
</g>
</svg>

```hlsl
float3 GodRays(float2 uv, float2 sun_uv) {
  float2 delta = (uv - sun_uv) * (density / kSampleCount);
  float2 sample_uv = uv;
  float illumination_decay = 1.0;
  float3 accumulated = 0;

  for (int i = 0; i < kSampleCount; ++i) {
    sample_uv -= delta;
    float3 sample_color = occlusion_texture.Sample(linear_clamp, sample_uv).rgb;
    sample_color *= illumination_decay * weight;
    accumulated += sample_color;
    illumination_decay *= decay;
  }
  return accumulated * exposure;
}
```

| 点 | 説明 |
| --- | --- |
| `occlusion_texture` | 空の明るい部分だけが残り、物は黒の画像（深度から作る） |
| `decay` | 0.95〜0.99。光源から遠いほど弱くする |
| `density` | ぼかしの長さ（0.5〜1.0） |
| サンプル数 | 32〜100。半解像度で描くと軽い |
| 欠点 | 太陽が画面の外だと使えない。太陽の向きを見ていないと筋が消える。空気の濃さ・影の奥行きは表現できない |

### 原理

この方式は Mitchell の GPU Gems 3 の記事 "Volumetric Light Scattering as a Post-Process"（2007）で広まりました。考え方は「画面上で太陽に近い位置の明るさが、そこから伸びる光の筋の源である」ことです。まず、シーンを「太陽の明るさだけが残り、物体は黒いシルエット」になる画像（オクルージョン画像）に直します。次に、各ピクセルから太陽の画面位置へ向かう直線に沿って、この画像をサンプルして足します。太陽に近い方向の明るい部分（空）が、直線上にあればそのピクセルは明るくなります。物体のシルエットが直線上にあれば、その分は暗いままです。結果として、シルエットの背後から放射状に伸びる光の筋が出ます。

直線に沿ったサンプルは太陽から遠ざかるほど弱める減衰（`decay`）を掛けて足します。この減衰が光が遠くへ届くほど弱まる様子を表します。

### 制約の理由

この方式はあくまで「画面の絵」を加工しているだけで、3D の空間を解いていません。そのため、太陽が画面外にあるとそもそも太陽の画面位置が定義できず、ぼかしの中心がなくなります。また、手前の物体と奥の物体は区別できず、すべてが同じ平面のシルエットとして扱われます。「霧の奥行き」も存在しません。これらの制約は後の節で説明するシャドウ マップによる方式で解決されます。

<strong>太陽が画面外のときにも自然にするため</strong>、<strong>太陽が画面に近いほど強く離れると弱くする</strong>フェードを付けます。

## 画面空間の放射状ブラー

<strong>放射状ブラー</strong>（Mitchell、2007）は <strong>画面に描かれた、画像</strong>を太陽の画面上の位置から、放射状にぼかして（引き伸ばして）、光の筋を作ります。3D のシーンを再計算せず画面の、画像だけで行うので非常に軽いです。

```text
 画面:  太陽（画面上の点）●
         ╲   ╲   ╲
          ╲   ╲   ╲        各画素から、太陽に向かって、何回か読んで、明るさを足す
           ・   ・   ・
```

## 手順

| 手順 | 内容 |
| --- | --- |
| ① 光のマスクを作る | 太陽の円盤と、明るい空を白、遮蔽物（木、建物）を黒にした画像（低解像度） |
| ② 放射状にぼかす | 各画素から、太陽の画面位置へ向かって数十回、読んで足す。明るい部分が太陽から放射状に、伸びる |
| ③ 合成 | ぼかした結果を、加算ブレンドでシーンに足す |

## ① 光のマスク

<strong>シーンを白黒に</strong>します。<strong>空（太陽）は明るく</strong>、物体は黒にします。物体の隙間から空が見える所だけが、明るく残ります。

```hlsl
// 光のマスク: 深度が最大（空）の画素は、シーンの色を、そのまま。物体の画素は、黒。
float3 LightMaskPS(float2 uv : TEXCOORD0) : SV_Target {
  float depth = g_scene_depth.Sample(g_point_clamp, uv).r;
  float3 color = g_scene_color.Sample(g_linear_clamp, uv).rgb;
  float is_sky = step(0.9999, depth);                    // 深度が、ほぼ最大 = 空
  // 太陽の円盤、明るい空だけを、取り出す。しきい値で、明るい部分に、絞ってもよい。
  return color * is_sky;
}
```

`step(0.9999, depth)` で <strong>空の画素だけ</strong>を  3<strong>4 、物体の画素を 0 にします。空の色（太陽の周りの明るさ）が、マスクの明るさになります。画面の半分または 1/4 の解像度で描くと後の、ぼかしが軽くなります。

## ② 放射状にぼかす

```hlsl
// 太陽の画面上の位置（0〜1 の uv）から、各画素に向かって、何度か読んで、足す。
float4 RadialBlurPS(float2 uv : TEXCOORD0) : SV_Target {
  const int kSamples = 48;
  float2 delta = (uv - g_sun_screen_uv) * (g_density / kSamples);   // 太陽から、この画素への、向きと、1 歩の長さ
```

`delta` は <strong>この画素から太陽へ向かう、1 歩</strong>です（<strong>逆向き</strong>に進むので符号は `uv − sun`）。`g_density` が筋の長さ（大きいほど遠くまで、読む）を決めます。

```hlsl
  float2 sample_uv = uv;
  float illumination_decay = 1.0;                                    // 減衰（遠くを、読んだ分ほど、弱く）
  float3 sum = 0.0;
  for (int i = 0; i < kSamples; ++i) {
    sample_uv -= delta;                                              // 太陽に向かって、1 歩進む
    float3 s = g_light_mask.SampleLevel(g_linear_clamp, sample_uv, 0).rgb;
    sum += s * illumination_decay * g_weight;
    illumination_decay *= g_decay;                                   // 1 回ごとに、弱める（0.95〜0.99）
  }
  return float4(sum, 1.0);
}
```

<strong>太陽に向かって</strong>、<strong>48 回</strong>、マスクを読み明るさを足し合わせます。途中に遮蔽物（黒）があればその分、暗くなり空が見える方向は明るいので、光の筋と影が放射状に現れます。`g_decay`（減衰）は遠くを読むほど弱くする、重みです。1 に近いほど筋が長く伸びます（[Tuning the Look](tuning.md)）。

## ③ 合成

```hlsl
// 放射状ブラーの結果を、太陽の色で着色して、シーンに加算する。
float3 rays = g_radial_blur.Sample(g_linear_clamp, uv).rgb * g_sun_color * g_intensity;
float3 final_color = scene_color + rays;
```

<strong>加算ブレンド</strong>で <strong>シーンに、足す</strong>だけです。HDR で足すとブルーム（[Bloom](../../postprocess/bloom/index.md)）と、組み合わさってまぶしい筋になります。

## 太陽が画面の外にある

<strong>太陽が画面の外</strong>（背後、または画面の端の外）にあるとき、<strong>放射状ブラー</strong>の起点が画面の外になり計算が、不安定になります。

| 状況 | 対策 |
| --- | --- |
| 太陽がカメラの背後 | 筋を、消す（太陽の方向と視線の内積が負なら、強さ 0） |
| 太陽が画面の外（横） | 画面の、端の外まで計算する（起点は uv の範囲外でも、よい）。太陽に近いほど強く離れるほど、フェード |
| 太陽が真上や地平線の下 | 太陽が、地平線の下なら筋を消す |

```hlsl
// 太陽の方向に応じた、フェード。視線が、太陽の方を、向いているほど、強い。
float facing = saturate(dot(g_camera_forward, g_sun_dir));
float intensity = g_intensity * pow(facing, 3.0);
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 軽い（低解像度の、後処理。数十回のテクスチャ読み込み） |
| 長所 | 実装が簡単 |
| 短所 | 画面の中に太陽（または、明るい空）が映っていないと出ない（光が、画面の外から差し込む場合は不正確） |
| 短所 | 影の正確さが無い（画面に映った、明るい空しか使えない） |
| 短所 | 視点（カメラの向き）に依存し視線を、動かすと筋がずれる |
| 短所 | 読み込みの回数が、少ないと縞が出る |

## よくあるミス

??? failure "太陽が画面外に出ると、光の筋が消える"
    <strong>他の方式</strong>に<strong>切り替える</strong>、またはフェードさせる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 太陽から放射状にぼかす。手軽だが制約あり

## 参考

- Mitchell, "Volumetric Light Scattering as a Post-Process", GPU Gems 3, Chapter 13, 2007（放射状ブラーによる、光の筋）
- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [God Rays](index.md)
- [Gaussian Blur](../../postprocess/bloom/gaussian.md)
