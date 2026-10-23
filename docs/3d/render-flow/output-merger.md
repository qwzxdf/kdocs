---
title: 深度・ブレンド
tags:
  - 3Dゲーム
  - 描画
---

# 深度・ブレンド

<strong>ピクセル シェーダーが色を決めても、すぐ画面に書かれるわけではありません</strong>。書き込む前に「その色を書いてよいか」「すでにある色とどう混ぜるか」を決める最後の工程があります。出力マージャー（Output Merger）と呼ばれ、深度テスト・ステンシルテスト・ブレンドを行います。手前にある物が奥の物を隠すのも、半透明の物が透けて見えるのもこの工程です。

!!! tip "ポイント"
    - 出力マージャー ＝ <strong>書き込む前の最後の関門</strong>：<strong>① 深度テスト → ② ステンシル → ③ ブレンド → ④ 書き込み</strong>。
    - 深度テスト ＝ 今のピクセルが、すでに描かれた物より手前か。手前なら書く、奥なら捨てる。
    - 深度バッファはピクセルごとの「一番手前の距離」を覚える画像。
    - ステンシル ＝ ピクセルごとの整数マスク。描く範囲を限定する。
    - ブレンド ＝ 新しい色と既存の色を、式で混ぜる。半透明・加算など。
    - 描く順番が重要：不透明は手前から（高速）、半透明は奥から。

## 全体の位置

<svg class="fig illust" viewBox="0 0 780 180" role="img" aria-label="出力マージャーの流れ"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ピクセル シェーダーの後：深度 → ステンシル → ブレンド → 書き込み</text>
<g font-size="12">
<rect x="20" y="60" width="150" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/><text x="95" y="90" text-anchor="middle" style="font-weight:700">ピクセル</text><text x="95" y="110" text-anchor="middle" style="font-weight:700">シェーダー</text>
<rect x="210" y="60" width="130" height="70" rx="8" fill="#e5484d" fill-opacity="0.2" stroke="#e5484d" stroke-width="2"/><text x="275" y="90" text-anchor="middle" style="font-weight:700">深度テスト</text><text x="275" y="110" text-anchor="middle" style="font-size:11px">手前か？</text>
<rect x="380" y="60" width="130" height="70" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="445" y="90" text-anchor="middle" style="font-weight:700">ステンシル</text><text x="445" y="110" text-anchor="middle" style="font-size:11px">許可された範囲か？</text>
<rect x="550" y="60" width="100" height="70" rx="8" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043" stroke-width="2"/><text x="600" y="90" text-anchor="middle" style="font-weight:700">ブレンド</text><text x="600" y="110" text-anchor="middle" style="font-size:11px">混ぜる</text>
<rect x="690" y="60" width="70" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/><text x="725" y="90" text-anchor="middle" style="font-weight:700">書込</text><text x="725" y="110" text-anchor="middle" style="font-size:11px">画像へ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="172" y1="95" x2="208" y2="95" marker-end="url(#rfa)"/><line x1="342" y1="95" x2="378" y2="95" marker-end="url(#rfa)"/><line x1="512" y1="95" x2="548" y2="95" marker-end="url(#rfa)"/><line x1="652" y1="95" x2="688" y2="95" marker-end="url(#rfa)"/></g>
<text x="275" y="160" text-anchor="middle" style="font-size:11px;fill:#e5484d">奥なら捨てる</text>
<text x="445" y="160" text-anchor="middle" style="font-size:11px;fill:#e5aa28">範囲外なら捨てる</text>
</svg>

## 深度テスト

<strong>3D では手前の物が奥の物を隠します</strong>。描く順番に関係なく、手前が勝つようにピクセルごとの「今までで一番手前の距離」を深度バッファに記録します。

<svg class="fig illust motion" data-fig="depth-test" viewBox="0 0 780 300" role="img" aria-label="深度テスト">
<text x="20" y="24" class="fig-title">深度テスト：描く順番が逆でも、手前の物が勝つ</text>
<g transform="translate(40,50)">
<text x="0" y="-6" style="font-size:12px;font-weight:700">① 先に奥の青い四角を描く</text>
<rect x="0" y="0" width="150" height="120" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<rect x="30" y="20" width="90" height="80" fill="#4c8bf5" fill-opacity="0.8"/>
<text x="75" y="64" text-anchor="middle" style="font-size:12px;fill:#fff">奥(0.8)</text>
<text x="0" y="146" style="font-size:11px">深度バッファ：</text><text x="0" y="162" style="font-size:11px">この範囲は 0.8 を記録</text>
</g>
<g transform="translate(270,50)">
<text x="0" y="-6" style="font-size:12px;font-weight:700">② 後から手前の赤い四角を描く</text>
<rect x="0" y="0" width="150" height="120" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<rect x="30" y="20" width="90" height="80" fill="#4c8bf5" fill-opacity="0.8"/>
<rect x="60" y="40" width="70" height="70" fill="#e5484d" fill-opacity="0.9"/>
<text x="95" y="80" text-anchor="middle" style="font-size:12px;fill:#fff">手前(0.3)</text>
<text x="0" y="146" style="font-size:11px">0.3 は 0.8 より手前 → 書く</text><text x="0" y="162" style="font-size:11px">深度を 0.3 に更新</text>
</g>
<g transform="translate(500,50)">
<text x="0" y="-6" style="font-size:12px;font-weight:700">③ 逆順でも結果は同じ</text>
<rect x="0" y="0" width="150" height="120" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<rect x="60" y="40" width="70" height="70" fill="#e5484d" fill-opacity="0.9"/>
<rect x="30" y="20" width="90" height="80" fill="#4c8bf5" fill-opacity="0.8"/>
<rect x="60" y="40" width="70" height="70" fill="#e5484d" fill-opacity="0.95"/>
<text x="0" y="146" style="font-size:11px">先に赤(0.3)を描き、青(0.8)は</text><text x="0" y="162" style="font-size:11px">0.8 は 0.3 より奥 → 重なる所は捨てる</text>
</g>
<text x="40" y="270" style="font-size:13px">深度が小さい（手前）ほうが勝つ。描画の順番に関係なく、手前が必ず見える。</text>
</svg>

| 設定 | 意味 |
| --- | --- |
| `DepthEnable` | 深度テストを使う |
| `DepthFunc = LESS` | 今の深度 < 記録された深度 のとき通す（手前なら通す） |
| `DepthWriteMask = ALL` | 通ったら深度バッファを更新（半透明では `ZERO`＝更新しない） |
| `LESS_EQUAL` | 同じ深度も通す（空・多パスの重ね描きで使う） |

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
desc.DepthFunc = D3D11_COMPARISON_LESS;
device->CreateDepthStencilState(&desc, depth_state.GetAddressOf());
context->OMSetDepthStencilState(depth_state.Get(), 0);
```

<!-- fig:depth-test-order:begin -->

<svg class="fig illust motion" data-fig="depth-test-order" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-depth-test-order" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">深度テスト:描く順番を変えても、手前の物が勝つ</text>
<text x="20" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">① A → B の順に描く</text>
<text x="20" y="118" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">色</text>
<text x="20" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">深度</text>
<rect x="56" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>
<rect x="56" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="86" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1174" values="#f1f5f9;#e5484d"/></rect>
<rect x="86" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="116" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1417" values="#f1f5f9;#e5484d"/></rect>
<rect x="116" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="146" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1661" values="#f1f5f9;#e5484d"/></rect>
<rect x="146" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="176" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1904;0.3548" values="#f1f5f9;#e5484d;#2563eb"/></rect>
<rect x="176" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="206" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2148;0.3791" values="#f1f5f9;#e5484d;#2563eb"/></rect>
<rect x="206" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="236" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391;0.4035" values="#f1f5f9;#e5484d;#2563eb"/></rect>
<rect x="236" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="266" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4278" values="#f1f5f9;#2563eb"/></rect>
<rect x="266" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="296" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="#f1f5f9;#2563eb"/></rect>
<rect x="296" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="326" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4765" values="#f1f5f9;#2563eb"/></rect>
<rect x="326" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<text x="70.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="100.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;1.0000" values="1;1;0;0"/></text>
<text x="100.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="130.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1414;0.1417;1.0000" values="1;1;0;0"/></text>
<text x="130.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1414;0.1417;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="160.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1661;1.0000" values="1;1;0;0"/></text>
<text x="160.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1661;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="190.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1904;1.0000" values="1;1;0;0"/></text>
<text x="190.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1904;0.3544;0.3548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3544;0.3548;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="220.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2144;0.2148;1.0000" values="1;1;0;0"/></text>
<text x="220.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2144;0.2148;0.3788;0.3791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="220.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3788;0.3791;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="250.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2388;0.2391;1.0000" values="1;1;0;0"/></text>
<text x="250.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2388;0.2391;0.4031;0.4035;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4031;0.4035;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="280.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4275;0.4278;1.0000" values="1;1;0;0"/></text>
<text x="280.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4275;0.4278;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="310.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="1;1;0;0"/></text>
<text x="310.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="340.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4762;0.4765;1.0000" values="1;1;0;0"/></text>
<text x="340.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4762;0.4765;1.0000;1.0000" values="0;0;1;1;0"/></text>
<polygon points="0,0 -7,-12 7,-12" fill="#e5aa28" opacity="0"><animate attributeName="points" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1174;0.1417;0.1661;0.1904;0.2148;0.2391;0.3548;0.3791;0.4035;0.4278;0.4522;0.4765" values="0,0 -7,-12 7,-12;100.0,94 93.0,82 107.0,82;130.0,94 123.0,82 137.0,82;160.0,94 153.0,82 167.0,82;190.0,94 183.0,82 197.0,82;220.0,94 213.0,82 227.0,82;250.0,94 243.0,82 257.0,82;190.0,94 183.0,82 197.0,82;220.0,94 213.0,82 227.0,82;250.0,94 243.0,82 257.0,82;280.0,94 273.0,82 287.0,82;310.0,94 303.0,82 317.0,82;340.0,94 333.0,82 347.0,82"/><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;0.5179;0.5183;1.0000" values="0;0;1;1;0;0"/></polygon>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;0.1414;0.1417;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1414;0.1417;0.1657;0.1661;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1661;0.1901;0.1904;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1904;0.2144;0.2148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2144;0.2148;0.2388;0.2391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2388;0.2391;0.2631;0.2635;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 0.8 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3544;0.3548;0.3788;0.3791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 0.8 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3788;0.3791;0.4031;0.4035;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 0.8 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4031;0.4035;0.4275;0.4278;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4275;0.4278;0.4518;0.4522;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;0.4762;0.4765;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4762;0.4765;0.5005;0.5009;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="268" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">結果:重なった所（4〜6）は、手前の B が残る<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5440;0.5443;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="400" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">② B → A の順に描く</text>
<text x="400" y="118" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">色</text>
<text x="400" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">深度</text>
<rect x="436" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>
<rect x="436" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="466" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3548" values="#f1f5f9;#e5484d"/></rect>
<rect x="466" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="496" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3791" values="#f1f5f9;#e5484d"/></rect>
<rect x="496" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="526" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4035" values="#f1f5f9;#e5484d"/></rect>
<rect x="526" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="556" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1174" values="#f1f5f9;#2563eb"/></rect>
<rect x="556" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="586" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1417" values="#f1f5f9;#2563eb"/></rect>
<rect x="586" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="616" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1661" values="#f1f5f9;#2563eb"/></rect>
<rect x="616" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="646" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1904" values="#f1f5f9;#2563eb"/></rect>
<rect x="646" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="676" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2148" values="#f1f5f9;#2563eb"/></rect>
<rect x="676" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<rect x="706" y="96" width="28" height="34" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391" values="#f1f5f9;#2563eb"/></rect>
<rect x="706" y="166" width="28" height="34" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
<text x="450.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="480.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3544;0.3548;1.0000" values="1;1;0;0"/></text>
<text x="480.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3544;0.3548;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="510.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3788;0.3791;1.0000" values="1;1;0;0"/></text>
<text x="510.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3788;0.3791;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="540.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4031;0.4035;1.0000" values="1;1;0;0"/></text>
<text x="540.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4031;0.4035;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="570.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;1.0000" values="1;1;0;0"/></text>
<text x="570.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="600.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1414;0.1417;1.0000" values="1;1;0;0"/></text>
<text x="600.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1414;0.1417;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="630.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1661;1.0000" values="1;1;0;0"/></text>
<text x="630.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1661;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="660.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1904;1.0000" values="1;1;0;0"/></text>
<text x="660.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1904;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="690.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2144;0.2148;1.0000" values="1;1;0;0"/></text>
<text x="690.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2144;0.2148;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="720.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">1.0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2388;0.2391;1.0000" values="1;1;0;0"/></text>
<text x="720.0" y="189" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">0.3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2388;0.2391;1.0000;1.0000" values="0;0;1;1;0"/></text>
<polygon points="0,0 -7,-12 7,-12" fill="#e5aa28" opacity="0"><animate attributeName="points" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1174;0.1417;0.1661;0.1904;0.2148;0.2391;0.3548;0.3791;0.4035;0.4278;0.4522;0.4765" values="0,0 -7,-12 7,-12;570.0,94 563.0,82 577.0,82;600.0,94 593.0,82 607.0,82;630.0,94 623.0,82 637.0,82;660.0,94 653.0,82 667.0,82;690.0,94 683.0,82 697.0,82;720.0,94 713.0,82 727.0,82;480.0,94 473.0,82 487.0,82;510.0,94 503.0,82 517.0,82;540.0,94 533.0,82 547.0,82;570.0,94 563.0,82 577.0,82;600.0,94 593.0,82 607.0,82;630.0,94 623.0,82 637.0,82"/><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;0.5179;0.5183;1.0000" values="0;0;1;1;0;0"/></polygon>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1174;0.1414;0.1417;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1414;0.1417;0.1657;0.1661;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1661;0.1901;0.1904;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1904;0.2144;0.2148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2144;0.2148;0.2388;0.2391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">B:0.3 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2388;0.2391;0.2631;0.2635;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3544;0.3548;0.3788;0.3791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3788;0.3791;0.4031;0.4035;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 &lt; 1.0 → 書く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4031;0.4035;0.4275;0.4278;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 ≧ 0.3 → 捨てる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4275;0.4278;0.4518;0.4522;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 ≧ 0.3 → 捨てる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;0.4762;0.4765;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="240" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">A:0.8 ≧ 0.3 → 捨てる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4762;0.4765;0.5005;0.5009;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400" y="268" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">結果:重なった所（4〜6）は、手前の B が残る<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5440;0.5443;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="30" y="330" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">各ピクセルで「今の深度 &lt; 記録された深度」なら書く。奥の物は、すでに手前が描かれていれば捨てられる。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="30" y="354" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">→ どちらの順でも、最終的な絵は同じ。ただし ② は A の計算が無駄になる（手前から描くと速い理由）。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:depth-test-order:end -->

### 深度バッファの中身

深度バッファは、描画先と同じ大きさの 2D の画像で、各ピクセルに 0〜1 の深度値を持ちます。フレームの始めに 1（一番奥）で初期化します（クリア）。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="深度バッファ">
<text x="20" y="24" class="fig-title">カラー バッファと深度バッファ：同じ大きさの 2 枚の画像</text>
<g transform="translate(60,50)">
<rect x="0" y="0" width="240" height="150" fill="#87ceeb" fill-opacity="0.35" stroke="currentColor"/>
<rect x="60" y="50" width="70" height="100" fill="#a0763c" fill-opacity="0.8"/>
<circle cx="180" cy="90" r="36" fill="#e5484d" fill-opacity="0.8"/>
<text x="120" y="176" text-anchor="middle" style="font-size:12px;font-weight:700">カラー バッファ（見える絵）</text>
</g>
<g transform="translate(400,50)">
<defs><linearGradient id="dpg" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#222"/></linearGradient></defs>
<rect x="0" y="0" width="240" height="150" fill="#f4f4f4" stroke="currentColor"/>
<rect x="60" y="50" width="70" height="100" fill="#777"/>
<circle cx="180" cy="90" r="36" fill="#bbb"/>
<text x="120" y="176" text-anchor="middle" style="font-size:12px;font-weight:700">深度バッファ（白＝遠い、黒＝近い）</text>
</g>
<text x="400" y="228" style="font-size:12px">近い物ほど暗く（小さい値）。空は一番奥の 1.0（白）。</text>
</svg>

深度バッファは、描画の仕組み以外にも使われます。ライティング（ピクセルの位置の再構築）・SSAO・フォグ・水の深度差など、後の工程が深度を読みます。

## ステンシル

<strong>ステンシル</strong>はピクセルごとに 8 ビットの整数を持つバッファで、「描く範囲」を絞るのに使います（深度バッファと 1 枚にまとめる、24 ビット深度 + 8 ビットステンシルが一般的）。

| 用途 | 内容 |
| --- | --- |
| マスク | 窓や鏡の枠の中だけに描く |
| アウトライン | キャラクター本体のあるピクセルを 1 にして、その外側だけ輪郭色で描く |
| シルエット表示 | 壁の向こうの味方を隠れた部分だけ別の色で描く |
| 影のボリューム | 古い影の方式 |
| デカール・ライト ボリューム | ライトが影響するピクセルだけを計算する |

テスト条件と更新方法を、表側・裏側で別々に設定できます。

## ブレンド

<strong>色を書くとき、すでにある色とどう混ぜるか</strong>を決めるのがブレンドです。半透明（ガラス・煙）・加算（光・炎）などを実現します**。

<div class="formula">結果 = 新しい色 × 係数 A　⊕　既存の色 × 係数 B　（⊕：足す・引くなど）</div>

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="ブレンド">
<text x="20" y="24" class="fig-title">ブレンドの種類：同じ赤い円を、青い背景に描く</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#e5484d"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">不透明（上書き）</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × 1 ＋ 既存 × 0</text>
</g>
<g transform="translate(230,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#e5484d" fill-opacity="0.5"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">アルファ ブレンド</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × α ＋ 既存 × (1−α)</text>
</g>
<g transform="translate(420,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#e5484d" style="mix-blend-mode:screen" opacity="0.9"/>
<circle cx="75" cy="60" r="40" fill="#ffd0a0" fill-opacity="0.35"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">加算</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × 1 ＋ 既存 × 1（明るくなる）</text>
</g>
<g transform="translate(610,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#1a2c55" fill-opacity="0.75"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">乗算</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × 既存（暗くなる）</text>
</g>
</svg>

| ブレンド | 式（係数） | 使い道 |
| --- | --- | --- |
| 不透明 | 1, 0 | ふつうの物体 |
| アルファ ブレンド | α, 1 − α | ガラス・半透明の物・UI |
| 加算 | 1, 1 | 光る物・炎・魔法の粒子 |
| 乗算 | 0, 元の色 | 影・色付きガラス（暗くする） |
| プリマルチプライド アルファ | 1, 1 − α | 粒子で加算と半透明を混ぜたいとき |

```cpp
D3D11_BLEND_DESC desc = {};
auto& rt = desc.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&desc, blend_state.GetAddressOf());
```

## 描く順番が大事

<strong>不透明な物</strong>は深度テストがあるので順番に関係なく正しく描かれます。でも手前から描くほうが速いです。半透明な物は深度に頼れないので奥から手前の順に描きます。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="描画順"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">描画の順番：不透明 → 半透明</text>
<g font-size="12">
<rect x="30" y="60" width="200" height="110" rx="8" fill="#4c8bf5" fill-opacity="0.15" stroke="#4c8bf5" stroke-width="2"/>
<text x="130" y="84" text-anchor="middle" style="font-weight:700">① 不透明</text>
<text x="46" y="110">・手前から奥へ（高速）</text><text x="46" y="130">・深度を書く</text><text x="46" y="150">・ブレンドなし</text>
<rect x="290" y="60" width="200" height="110" rx="8" fill="#9664e6" fill-opacity="0.15" stroke="#9664e6" stroke-width="2"/>
<text x="390" y="84" text-anchor="middle" style="font-weight:700">② 空</text>
<text x="306" y="110">・最奥のピクセルだけ</text><text x="306" y="130">・深度テストあり</text><text x="306" y="150">・深度は書かない</text>
<rect x="550" y="60" width="200" height="110" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="650" y="84" text-anchor="middle" style="font-weight:700">③ 半透明</text>
<text x="566" y="110">・奥から手前へ（ソート）</text><text x="566" y="130">・深度テストのみ（書かない）</text><text x="566" y="150">・ブレンドあり</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="232" y1="115" x2="288" y2="115" marker-end="url(#rfa)"/><line x1="492" y1="115" x2="548" y2="115" marker-end="url(#rfa)"/></g>
<text x="20" y="215" style="font-size:13px">半透明を奥から手前へ描くのは、「手前の物の下に奥の物が透けて見える」ように混ぜるため。</text>
<text x="20" y="240" style="font-size:13px">順番を間違えると、透けるはずの物が消えたり、不自然に見える（詳細：半透明のソート）。</text>
</svg>

## 複数の描画先（MRT）

<strong>1 回のドロー コールで、複数の画像に同時に書き込む</strong>ことができます（Multiple Render Targets）。ディファード レンダリングで、色・法線・材質を別々の画像に書くときに使います。

```hlsl
struct PSOutput {
  float4 albedo : SV_Target0;
  float4 normal : SV_Target1;
  float4 material : SV_Target2;
};
```

G バッファなど、この仕組みを使う方式は[フォワードとディファード](../../rendering/forward-deferred.md)で扱います。

## 早期深度テスト（Early-Z）

<strong>深度テストはピクセル シェーダーの後</strong>ですが、GPU は結果が同じなら、ピクセル シェーダーの前に深度テストを行います（Early-Z）。隠れているピクセルのシェーダー計算を省略できます。

| 条件 | 効果 |
| --- | --- |
| ピクセル シェーダーが深度を変更しない | Early-Z が有効 |
| `discard`（クリップ）を使う | Early-Z が使えない場合がある（アルファ テストの物は遅くなる） |
| 手前から描く | 隠れるピクセルが前もって捨てられる |
| 深度プリパス | 先に深度だけ描いて、後で色を描く（オーバードローを完全に省く） |

詳しくは[オーバードロー](../../rendering/overdraw.md)で扱います。

## よくあるミス

??? failure "半透明の物が、奥の物を消してしまう"
    <strong>半透明は深度の書き込みを切る</strong>（`DepthWriteMask = ZERO`）。奥から手前の順に描く。

??? failure "深度バッファをクリアし忘れて、前フレームの絵が残る／消える"
    毎フレーム、深度を 1.0 でクリアする。

??? failure "近い面と遠い面を極端に設定して、遠くで Z ファイティング（ちらつき）"
    近い面を遠ざける、リバース Z（1 が近い）と 32 ビット浮動小数の深度を使う。

??? failure "深度とカラーの描画先の大きさが違い、描画されない"
    深度ステンシルとレンダー ターゲットは同じ大きさにする。

??? failure "ブレンドの順序で、パーティクルの明るさが変わる"
    加算は順序に依らないが、アルファ ブレンドは順序で変わる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力マージャー ＝ <strong>深度テスト → ステンシル → ブレンド → 書き込み</strong>
    - [x] 深度テスト ＝ 手前なら書く。描く順番に依らず、手前が勝つ
    - [x] ステンシルは描く範囲を絞るマスク
    - [x] ブレンドで半透明・加算・乗算。半透明は奥から手前、深度は書かない
    - [x] Early-Zで隠れたピクセルのシェーダーを省く。手前から描くと効く

## 参考

- Microsoft, "Output-Merger Stage"（Microsoft Learn）
- Microsoft, "Depth-Stencil State"・"Blend State"（Microsoft Learn）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"（Part 9）

## 関連ページ

- [描画の流れ（入門）](index.md)
- [ピクセルの色](pixel-shader.md)
- [画面に出す](present.md)
- [深度とカリング](../depth-culling.md)
- [ブレンドとソート](../../graphics/translucency/blending-sorting/index.md)
