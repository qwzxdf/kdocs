---
title: Ray-Traced AO (RTAO)
tags:
  - 描画
---

# Ray-Traced AO (RTAO)

<strong>レイトレース AO は、シェーディングする点から、半球にレイを何本か飛ばし、一定距離以内に当たった割合を数えて、AO を求めます</strong>。<strong>ハードウェア レイトレーシングを使えば、画面外や薄い物も含めて、正確な AO</strong> が得られます。レイ数が少ないとノイズが多いので、デノイズが必須です。このページでは、仕組み・実装・レイ数とデノイズ・コストを説明します。

!!! tip "ポイント"
    - RTAO ＝ 半球にレイを飛ばし、半径内で当たったら遮蔽。
    - レイは、コサイン重みで分布させる。
    - 1 ピクセル 1〜2 レイ ＋ デノイズが実用的。
    - 画面外・薄い物の裏側も正しい。

## レイトレース AO（RTAO）
<strong>DXR</strong>（DirectX Raytracing）などのレイトレーシングで、<strong>三角形に実際にレイを飛ばして</strong>、AO を求めます。

<!-- fig:rtao-rays:begin -->

<svg class="fig illust motion" data-fig="rtao-rays" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rtao-rays" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">レイトレース AO: 半球にレイを N 本飛ばし、近くに当たった割合を、数える。N が少ないとノイズが出る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">床と壁の角(90°)の近くの点。cos 重みで 2 次元の向きを選び、半径 1.5 以内の壁に当たったら、遮蔽。N = 1・4・16・64</text>
<rect x="30" y="96" width="440" height="260" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 点と壁(断面)</text>
<line x1="150.0" y1="330.0" x2="438.0" y2="330.0" stroke="#475569" stroke-width="4"/>
<rect x="138.0" y="138.0" width="12.0" height="192.0" fill="#94a3b8"/>
<circle cx="234.0" cy="330.0" r="7" fill="#1f2937"/>
<path d="M54.0,330.0 A180.0,180.0 0 0 1 414.0,330.0" fill="none" stroke="#93c5fd" stroke-width="2" stroke-dasharray="5 4"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2709;0.2711;1.0000" values="1;1;0;0"/><line x1="234.0" y1="330.0" x2="318.13" y2="170.87" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<text x="44" y="128" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">レイ 1 本 → 当たり 0 本 → AO 1.00(正解 0.73)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2709;0.2711;0.4754;0.4756;1.0000" values="0;0;1;1;0;0"/><line x1="234.0" y1="330.0" x2="317.71" y2="170.65" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="188.79" y2="155.77" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="312.87" y2="168.2" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="174.17" y2="160.23" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<text x="44" y="128" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">レイ 4 本 → 当たり 0 本 → AO 1.00(正解 0.73)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4754;0.4756;0.6798;0.6800;1.0000" values="0;0;1;1;0;0"/><line x1="234.0" y1="330.0" x2="316.04" y2="169.78" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="156.95" y2="167.32" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="234.93" y2="150.0" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="374.26" y2="217.19" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="282.44" y2="156.64" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="356.79" y2="198.38" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="259.14" y2="151.76" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="240.54" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="228.23" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="277.72" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="316.01" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="260.96" y2="152.03" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="247.71" y2="150.52" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="268.5" y2="153.34" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="327.19" y2="176.0" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="249.79" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<text x="44" y="128" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">レイ 16 本 → 当たり 5 本 → AO 0.69(正解 0.73)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6798;0.6800;1.0000" values="0;0;1;1"/><line x1="234.0" y1="330.0" x2="309.34" y2="166.53" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="389.59" y2="239.5" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="283.18" y2="156.85" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="261.36" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="285.9" y2="157.65" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="396.35" y2="252.26" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="370.82" y2="213.04" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="227.87" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="328.82" y2="177.0" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="168.47" y2="162.35" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="200.46" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="307.41" y2="165.65" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="287.55" y2="158.15" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="381.1" y2="226.26" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="341.71" y2="185.78" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="329.7" y2="177.55" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="305.11" y2="164.64" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="250.23" y2="150.73" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="239.62" y2="150.09" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="168.93" y2="162.17" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="298.48" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="267.25" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="268.36" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="285.05" y2="157.39" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="210.42" y2="151.55" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="212.11" y2="151.34" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="238.08" y2="150.05" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="198.96" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="182.75" y2="157.45" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="351.14" y2="193.33" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="343.72" y2="187.3" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="264.54" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="342.76" y2="186.57" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="257.35" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="406.46" y2="278.45" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.15" y2="170.72" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="274.87" y2="154.7" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="387.17" y2="235.45" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="177.26" y2="159.18" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="333.42" y2="179.95" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="231.15" y2="150.02" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="225.74" y2="150.19" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="235.15" y2="150.0" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="308.92" y2="166.33" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="328.81" y2="176.99" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="400.05" y2="260.51" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="388.54" y2="237.72" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="397.27" y2="254.22" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="308.36" y2="166.08" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="254.14" y2="151.13" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="322.03" y2="172.99" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="271.86" y2="154.03" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="409.47" y2="289.86" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="176.38" y2="159.47" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="150.0" y2="226.7" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="202.94" y2="152.7" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="231.18" y2="150.02" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="384.59" y2="231.39" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="372.07" y2="214.52" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="251.19" y2="150.82" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="273.67" y2="154.43" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="188.99" y2="155.72" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="383.04" y2="229.06" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<line x1="234.0" y1="330.0" x2="284.85" y2="157.33" stroke="#2ea043" stroke-width="1.6" opacity="0.85"/>
<text x="44" y="128" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">レイ 64 本 → 当たり 10 本 → AO 0.84(正解 0.73)</text>
</g>
<rect x="500" y="96" width="430" height="260" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="500" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">② 同じ点で 300 回やったときの、ばらつき</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0932;0.0933;1.0000" values="0;0;1;1"/><text x="520" y="158" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">1 本</text>
<rect x="590" y="140" width="280.0" height="26" fill="#e5484d" opacity="0.85"/>
<text x="878.0" y="159" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">0.442</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2976;0.2978;1.0000" values="0;0;1;1"/><text x="520" y="208" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">4 本</text>
<rect x="590" y="190" width="127.6" height="26" fill="#e5484d" opacity="0.85"/>
<text x="725.5987807296074" y="209" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">0.202</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5022;1.0000" values="0;0;1;1"/><text x="520" y="258" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">16 本</text>
<rect x="590" y="240" width="74.62" height="26" fill="#e5484d" opacity="0.85"/>
<text x="672.618842803869" y="259" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">0.118</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><text x="520" y="308" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">64 本</text>
<rect x="590" y="290" width="35.19" height="26" fill="#e5484d" opacity="0.85"/>
<text x="633.1944526748666" y="309" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">0.056</text>
</g>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">AO のレイの本数:</text>
<text x="200" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="200" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2843;0.2844;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2843;0.2844;0.4887;0.4889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4887;0.4889;0.6932;0.6933;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">64<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/></text>
<text x="40" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画面 1920×1080 での、1 フレームのレイの数:</text>
<text x="40" y="460" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="460" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">2,073,600<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2843;0.2844;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="460" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">8,294,400<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2843;0.2844;0.4887;0.4889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="460" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">33,177,600<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4887;0.4889;0.6932;0.6933;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="460" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">132,710,400<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8709;0.8711;1.0000" values="0;0;1;1"/><rect x="520" y="400" width="410" height="112" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="536" y="424" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">4 倍のレイで、ばらつきは約 半分(1/√N)</text>
<text x="536" y="448" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">1 本 0.442 → 64 本 0.056(約 8.0 分の 1)</text>
<text x="536" y="470" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">実際は 1 本で撮って、時間方向に重ねて(デノイズ)消す</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">近くに当たったレイの割合が、遮蔽<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">レイが少ないと、割合がばらつく(ノイズ)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8843;0.8844;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ノイズは、デノイズで消す。レイ自体は、画面の外の物にも当たる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8843;0.8844;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:rtao-rays:end -->

### 手順

RTAO のアルゴリズムは、とても単純です。

まず、G-Buffer から、画素のワールド位置と法線を得ます。次に、法線の側の半球に、<strong>コサイン分布</strong>でレイの方向を作ります。コサイン分布とは、法線に近い方向ほど多く選ばれる分布です。この分布で方向を選ぶと、AO の積分にある `n·ω` の重みと確率密度が打ち消し合って、<strong>AO は単に「遮られなかったレイの割合」</strong>になります（[Approximating the Integral](../theory/approximation.md)）。重みを別に掛ける必要がないので、実装が簡単です。

レイは、最大距離 R（AO の影響半径）まで飛ばします。ここで知りたいのは「当たったかどうか」だけで、どこで当たったか、何に当たったかは要りません。そのため、<strong>any-hit の最初の当たりで探索を打ち切って</strong>構いません。当たれば V = 0、当たらなければ V = 1 で、全レイの平均が AO です。

```hlsl
[shader("raygeneration")]
void RtaoRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 p = WorldPosition(pixel);
  float3 n = WorldNormal(pixel);

  float3 dir = CosineSampleHemisphere(n, Random2(pixel, frame_index));

  RayDesc ray;
  ray.Origin = p + n * kRayBias;
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = ao_radius;

  AoPayload payload;
  payload.hit = 1.0;
  TraceRay(scene, RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | RAY_FLAG_SKIP_CLOSEST_HIT_SHADER,
           0xFF, 0, 0, 0, ray, payload);

  ao_output[pixel] = payload.hit;
}
```

このコードの要点は次のとおりです。`RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH` は、最初に当たった時点で探索を終えるフラグで、最も近い交点を求める必要がない AO では、これで大きく速くなります。`RAY_FLAG_SKIP_CLOSEST_HIT_SHADER` は、当たった後のシェーダーを省略します。当たらなければ可視とするために、payload の初期値を 1 にし、ミス シェーダーで 0 ではなく可視の値を返す規約にします（ここでは当たったら 0 を書く運用です）。`ray.TMax = R` が AO の影響範囲を決めます。レイの出発点は、自己交差を避けるために、法線方向へ少し浮かせます。

### レイの方向の作り方

コサイン分布の方向は、2 つの乱数 (u1, u2) から作ります。円盤の上に一様に点を取り、それを半球に持ち上げる（Malley の方法）のが標準です。

<div class="formula">r = √u1、φ = 2π·u2　→　局所座標 (r cos φ, r sin φ, √(1 − u1))</div>

局所座標の z 軸を法線に合わせるために、法線から作った接線ベクトル 2 本で基底を組んで変換します。乱数は、画素の位置とフレーム番号から作ったブルー ノイズや低ディスクレパンシー列を使うと、同じレイ数でもノイズが小さくなり、時間蓄積の収束も速くなります（[Noise Patterns](../filtering/noise-pattern.md)）。

### コストの考え方

RTAO のコストは、レイの数と、レイの長さ R で決まります。R が短いと、レイが BVH のごく一部しか走査しないで済むので、とても軽くなります。AO の半径は 0.5〜2 m 程度が普通なので、長いレイを使う反射や GI と比べて、<strong>1 レイあたりの処理が桁違いに軽い</strong>のが RTAO の強みです。

軽さを活かして、実用的には 1 画素 1 本のレイを毎フレーム飛ばし、デノイザーで集めます。半分の解像度でレイを飛ばして、フル解像度の深度を見ながらアップサンプルする構成もあります。

### 特徴

利点は、画面外・隠れた物・薄い物も含めて、正しく遮蔽できることです。ハローなどのアーティファクトがなく、コサイン重みが自然に入り、半径の大きさにも強いです。

欠点は、1 画素 1〜2 本のレイではノイズが大きく、デノイザーが必須なことです。レイトレーシング対応の GPU が必要で、BVH の構築と更新のコストがかかります。動く物体が多いと、BVH の更新が重くなります。

### デノイズ

レイは画素あたり 1 本程度なので、そのままでは、ノイズだらけです。空間（バイラテラル ブラー）と時間（再投影した履歴との混合）で平均します（[AO Filtering](../filtering/index.md)）。AO は 1 チャンネル（スカラー）で、色を持つ反射や GI に比べて、デノイズがずっと軽く済みます。

ノイズの大きさは、実は画素ごとに違います。完全に遮られた隅や、完全に開けた場所では、全レイの結果が同じなので、ばらつきがありません。ばらつきが大きいのは、遮蔽と非遮蔽が混ざる縁です。そこで、履歴の分散を見て、ばらつきの大きい画素だけブラーを強める、分散ガイド付きのフィルタ（SVGF など）を使うと、きれいに仕上がります。

### より良いやり方：スクリーン空間との併用

RTAO の 1 本のレイは、<strong>正確ですがノイズが大きい</strong>。GTAO は、<strong>ノイズが小さいが画面外を知らない</strong>。この 2 つは相補的です。画面内の細かい接触は GTAO で安く出し、RTAO は GTAO が苦手な画面外や薄い物の影響だけを補う（画素あたり 0.25 本の低いレート）構成にすれば、品質とコストの両方を良くできます。ハードウェアの許す範囲で、「RTAO を最高画質設定、GTAO を標準設定」と切り替えるのも、現実的な選択です。

また、レイの出発点の自己交差は、ノイズやちらつきの原因になります。法線方向へ浮かせる距離を、画素の距離に応じて変える、またはレイに法線方向の TMin を設定するなどして、調整してください。アルファ テストのある葉や柵は、any-hit シェーダーでアルファを評価しないと、板が遮蔽物になってしまいます。



## DirectX 11 では動かない部分

<strong>DXR（DirectX Raytracing）は、DirectX 12 の機能です。DirectX 11 には、ありません。</strong>このページの `TraceRay`・`RayQuery` を使うコードは、D3D12 のレンダラーで動かします。D3D11 だけで、同じ効果を狙うときは、次のように、置き換えます。

| やりたいこと | D3D11 での代用 |
| --- | --- |
| レイと三角形の、交差 | 距離場（SDF）・ボクセル、またはスクリーン空間のレイマーチ（[Linear Marching](../../reflections/ssr-basics/linear-march.md)） |
| 影 | シャドウ マップ（[Shadow Map Basics](../../shadows/shadow-map-basics/index.md)） |
| 間接光 | ライトマップ・プローブ・SSGI・ボクセル GI（[Global Illumination (GI)](../../gi/index.md)） |

D3D12 側の、初期化（加速構造・ステート オブジェクト・シェーダー テーブル・`DispatchRays`）は、[DXR Host Setup](../../dxr-host.md) に、まとめています。

## よくあるミス

??? failure "レイ数が少なくて、ノイズだらけ"
    <strong>時間蓄積と空間フィルタ（デノイズ）</strong>を使う（[フィルタ](../filtering/index.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RTAO ＝ 半球レイで遮蔽を数える
    - [x] 正確だが、レイ数とデノイズが課題

## 参考

- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019
- Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017
- Pharr, Jakob, Humphreys, "Physically Based Rendering: From Theory to Implementation", 4th Edition, MIT Press, 2023（モンテカルロ積分、コサイン重みのサンプリング）

## 関連ページ

- [Ray-Traced, Distance-Field and Voxel AO](index.md)
- [Distance Field AO (DFAO)](dfao.md)
- [AO Filtering](../filtering/index.md)
