---
title: 画面に出す
tags:
  - 3Dゲーム
  - 描画
---

# 画面に出す

**1 フレーム分の絵が完成しても、まだ画面には出ていません**。**絵は「バックバッファ」という裏の画像に描かれていて、最後に「表示して」と命令して、初めて画面に出ます**。このページでは、**フロント バッファとバック バッファ・スワップチェーン・Present・垂直同期（VSync）とティアリング・フレーム レート・入力遅延**を説明します。

!!! tip "ポイント"
    - 描画は<strong>画面に直接ではなく、裏の画像（バック バッファ）</strong>に行う。<strong>途中の絵を見せないため</strong>。
    - 完成したら<strong>Present</strong>で<strong>表と裏を入れ替える</strong>（<strong>スワップ</strong>）。
    - ディスプレイは<strong>一定周期（60 Hz なら 16.7 ms）</strong>で<strong>画面を更新</strong>する。
    - <strong>VSync あり</strong> ＝ <strong>更新のタイミングまで待ってから入れ替える</strong>（<strong>ティアリングなし、遅延あり</strong>）。
    - <strong>VSync なし</strong> ＝ <strong>すぐ入れ替える</strong>（<strong>速いが画面が裂けることがある</strong>）。
    - <strong>フレーム時間</strong>が<strong>ディスプレイの周期より長い</strong>と<strong>カクつく</strong>。

## なぜバック バッファが要るのか

**もし、画面に直接描いたら**、**描いている途中の絵**（背景だけ、物の半分だけ…）が**そのまま見えてしまいます**。**チラつきの原因**です。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="ダブル バッファリング"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ダブル バッファリング：裏で描いて、完成したら入れ替える</text>
<g font-size="12">
<rect x="40" y="60" width="200" height="130" rx="8" fill="#4c8bf5" fill-opacity="0.15" stroke="#4c8bf5" stroke-width="2"/>
<text x="140" y="84" text-anchor="middle" style="font-weight:700">フロント バッファ</text><text x="140" y="102" text-anchor="middle" style="font-size:11px">今、画面に出ている絵</text>
<rect x="70" y="116" width="140" height="56" fill="#87ceeb" fill-opacity="0.5"/><rect x="100" y="140" width="40" height="32" fill="#a0763c"/>
<rect x="320" y="60" width="200" height="130" rx="8" fill="#e5aa28" fill-opacity="0.18" stroke="#e5aa28" stroke-width="2"/>
<text x="420" y="84" text-anchor="middle" style="font-weight:700">バック バッファ</text><text x="420" y="102" text-anchor="middle" style="font-size:11px">今、GPU が描いている絵</text>
<rect x="350" y="116" width="140" height="56" fill="#87ceeb" fill-opacity="0.25" stroke-dasharray="3 3" stroke="currentColor"/>
<rect x="580" y="60" width="170" height="130" rx="8" fill="#2ea043" fill-opacity="0.15" stroke="#2ea043" stroke-width="2"/>
<text x="665" y="100" text-anchor="middle" style="font-weight:700">ディスプレイ</text><text x="665" y="122" text-anchor="middle" style="font-size:11px">フロント バッファを</text><text x="665" y="140" text-anchor="middle" style="font-size:11px">繰り返し読んで表示</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="242" y1="125" x2="578" y2="125" marker-end="url(#rfa)" stroke-opacity="0"/><line x1="242" y1="100" x2="578" y2="100" marker-end="url(#rfa)"/></g>
<path d="M300,215 L270,215 M270,215 L270,200 M270,200 L270,200" stroke="none"/>
<g font-size="12"><text x="260" y="230" text-anchor="middle" style="fill:#e5484d;font-weight:700">Present：2 つを入れ替える ⇄</text></g>
<g stroke="#e5484d" stroke-width="2" fill="none"><path d="M140,192 C140,222 420,222 420,192" marker-end="url(#rfa)"/><path d="M420,192 C420,214 140,214 140,192" stroke-opacity="0"/></g>
</svg>

| 用語 | 意味 |
| --- | --- |
| **フロント バッファ** | **今、画面に表示されている画像** |
| **バック バッファ** | <strong>次に表示する画像（描画中）</strong> |
| **Present** | **完成したバック バッファを、画面に出す命令**（**入れ替え**） |
| **スワップチェーン** | **バック バッファの列**（**2 枚や 3 枚を順番に回す**） |

<!-- fig:double-buffer-swap:begin -->

<svg class="fig illust motion" data-fig="double-buffer-swap" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-double-buffer-swap" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Present:裏で描いて、完成したら表と入れ替える</text>
<rect x="40" y="90" width="200" height="130" rx="8" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="40" y="80" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">バック バッファ</text>
<rect x="300" y="90" width="200" height="130" rx="8" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="300" y="80" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">フロント バッファ</text>
<rect x="560" y="78" width="180" height="142" rx="10" fill="#0f172a"/>
<text x="560" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">ディスプレイ</text>
<text x="656" y="70" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">（フロントを読む）</text>
<rect x="570" y="90" width="160" height="114" fill="#cbd5e1"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3040;0.5920;0.8720" values="#cbd5e1;#e5aa28;#2563eb;#2ea043"/></rect>
<rect x="50" y="100" width="0" height="110" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0317;0.0320;0.5957;0.5960;1.0000" values="0;0;1;1;0;0"/><animate attributeName="width" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0320;0.2080;1.0000" values="0;0;180;180"/><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2400;0.3040;1.0000" values="50;50;310;310"/></rect>
<text x="140.0" y="161.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff" opacity="0">フレーム 1<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2077;0.2080;0.5957;0.5960;1.0000" values="0;0;1;1;0;0"/><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2400;0.3040;1.0000" values="140;140;400;400"/></text>
<rect x="50" y="100" width="0" height="110" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.8757;0.8760;1.0000" values="0;0;1;1;0;0"/><animate attributeName="width" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3200;0.4960;1.0000" values="0;0;180;180"/><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5280;0.5920;1.0000" values="50;50;310;310"/></rect>
<text x="140.0" y="161.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff" opacity="0">フレーム 2<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;0.8757;0.8760;1.0000" values="0;0;1;1;0;0"/><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5280;0.5920;1.0000" values="140;140;400;400"/></text>
<rect x="50" y="100" width="0" height="110" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6077;0.6080;0.8757;0.8760;1.0000" values="0;0;1;1;0;0"/><animate attributeName="width" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6080;0.7840;1.0000" values="0;0;180;180"/><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.8160;0.8720;1.0000" values="50;50;310;310"/></rect>
<text x="140.0" y="161.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff" opacity="0">フレーム 3<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7837;0.7840;0.8757;0.8760;1.0000" values="0;0;1;1;0;0"/><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.8160;0.8720;1.0000" values="140;140;400;400"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">GPU の描画が始まる前<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0317;0.0320;1.0000" values="1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">GPU が フレーム 1 を、見えない裏（バック）に描いている<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0317;0.0320;0.2077;0.2080;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">描き終わり<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2077;0.2080;0.2397;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">Present:バックとフロントを入れ替える<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2397;0.2400;0.3037;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ディスプレイは フレーム 1 を表示しながら、裏で フレーム 2 を描く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.4957;0.4960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">描き終わり<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;0.5277;0.5280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">Present:入れ替え<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5917;0.5920;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5917;0.5920;0.6077;0.6080;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">フレーム 2 を表示中。裏で フレーム 3 を描く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6077;0.6080;0.7837;0.7840;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">描き終わり<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7837;0.7840;0.8157;0.8160;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="272" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">Present:入れ替え → 途中の絵は一度も見えない<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.8157;0.8160;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="306" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">VSync あり:ディスプレイの更新の合間まで待ってから入れ替える（裂けない）。<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="328" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">VSync なし:すぐ入れ替わるので、更新の途中で絵が変わり、画面が裂けることがある。<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<rect x="570" y="90" width="160" height="3" fill="#ef4444" opacity="0.85"><animate attributeName="y" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0320;0.1920;0.2077;0.2080;0.3680;0.3837;0.3840;0.5440;0.5597;0.5600;0.7200;0.7357;0.7360;0.8960;1.0000" values="90;90;201;201;90;201;201;90;201;201;90;201;201;90;201;201"/></rect>
</svg>

<!-- fig:double-buffer-swap:end -->

## スワップチェーン

**DX11／DX12 では、スワップチェーンを作って、画面とバック バッファを管理します**。

```cpp
DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Width = 1280;
desc.Height = 720;
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
desc.SampleDesc.Count = 1;
desc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
desc.BufferCount = 2;
desc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;

factory->CreateSwapChainForHwnd(device.Get(), hwnd, &desc, nullptr, nullptr, swap_chain.GetAddressOf());
```

| 項目 | 内容 |
| --- | --- |
| **`Format`** | **バック バッファの形式**。**`_SRGB` にすると書き込み時に自動でガンマ補正** |
| **`BufferCount`** | **バック バッファの数**。<strong>2（ダブル）か 3（トリプル）</strong> |
| **`SwapEffect`** | **`FLIP_DISCARD`**（**最新の高速な方式**）を使う |
| **バックバッファへの書き込み** | **バック バッファから `RenderTargetView` を作って、描画先にする** |

## Present と VSync

**ディスプレイは、決まった周期（60 Hz なら 1 秒に 60 回）で画面を更新**します。<strong>Present のタイミングが、この更新の途中だと上半分は古い絵、下半分は新しい絵が見える「ティアリング」</strong>が**起きます**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="ティアリング">
<text x="20" y="24" class="fig-title">VSync なし：更新の途中で入れ替えると、画面が裂ける</text>
<g transform="translate(60,50)">
<rect x="0" y="0" width="200" height="130" fill="#4c8bf5" fill-opacity="0.35" stroke="currentColor"/>
<rect x="0" y="0" width="200" height="60" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="0" y="60" width="200" height="70" fill="#e5484d" fill-opacity="0.35"/>
<line x1="0" y1="60" x2="200" y2="60" stroke="#e5aa28" stroke-width="3"/>
<text x="100" y="40" text-anchor="middle" style="font-size:12px">前のフレーム</text>
<text x="100" y="104" text-anchor="middle" style="font-size:12px">新しいフレーム</text>
<text x="100" y="152" text-anchor="middle" style="font-size:12px;fill:#e5aa28">この線でずれる（ティアリング）</text>
</g>
<g font-size="12">
<text x="330" y="80" style="font-weight:700">VSync なし</text><text x="330" y="102">・Present したらすぐ入れ替え</text><text x="330" y="122">・FPS が高いが、画面が裂けることがある</text><text x="330" y="142">・入力から表示までの遅延が小さい</text>
<text x="330" y="178" style="font-weight:700">VSync あり</text><text x="330" y="200">・更新の合間（垂直帰線期間）まで待って入れ替え</text><text x="330" y="220">・裂けない。ただし待つ分だけ遅延が増える</text>
</g>
</svg>

```cpp
UINT sync_interval = vsync_enabled ? 1 : 0;
UINT flags = (!vsync_enabled && tearing_supported) ? DXGI_PRESENT_ALLOW_TEARING : 0;
swap_chain->Present(sync_interval, flags);
```

| `SyncInterval` | 意味 |
| --- | --- |
| **0** | **待たずに Present**（VSync なし） |
| **1** | **1 回の更新ごとに**（60 Hz なら 60 FPS 上限） |
| **2** | **2 回に 1 回**（30 FPS 上限） |

## 60 Hz のディスプレイで

**VSync ありでフレームの処理が 16.7 ms に間に合わないと、次の更新まで待つ**ので**表示は 1 つ飛ばして 33.3 ms になります**（30 FPS 相当）。

<svg class="fig illust motion" data-fig="vsync-timeline" viewBox="0 0 780 280" role="img" aria-label="VSync のタイムライン">
<text x="20" y="24" class="fig-title">VSync あり：間に合えば 60 FPS、間に合わないと 1 回飛ばす</text>
<g stroke="currentColor" stroke-opacity="0.35"><line x1="60" y1="60" x2="60" y2="230"/><line x1="200" y1="60" x2="200" y2="230"/><line x1="340" y1="60" x2="340" y2="230"/><line x1="480" y1="60" x2="480" y2="230"/><line x1="620" y1="60" x2="620" y2="230"/><line x1="760" y1="60" x2="760" y2="230"/></g>
<text x="60" y="52" text-anchor="middle" style="font-size:11px">更新</text><text x="200" y="52" text-anchor="middle" style="font-size:11px">更新</text><text x="340" y="52" text-anchor="middle" style="font-size:11px">更新</text><text x="480" y="52" text-anchor="middle" style="font-size:11px">更新</text><text x="620" y="52" text-anchor="middle" style="font-size:11px">更新</text>
<g font-size="12">
<text x="14" y="98" style="font-size:11px">GPU</text>
<rect x="60" y="80" width="110" height="28" fill="#2ea043" fill-opacity="0.4" stroke="#2ea043"/><text x="115" y="99" text-anchor="middle">フレーム A (12ms)</text>
<rect x="200" y="80" width="110" height="28" fill="#2ea043" fill-opacity="0.4" stroke="#2ea043"/><text x="255" y="99" text-anchor="middle">フレーム B (12ms)</text>
<rect x="340" y="80" width="200" height="28" fill="#e5484d" fill-opacity="0.4" stroke="#e5484d"/><text x="440" y="99" text-anchor="middle">フレーム C (22ms：間に合わない)</text>
<rect x="540" y="80" width="80" height="28" fill="#2ea043" fill-opacity="0.4" stroke="#2ea043"/><text x="580" y="99" text-anchor="middle">D</text>
<text x="14" y="168" style="font-size:11px">表示</text>
<rect x="200" y="150" width="140" height="28" fill="#4c8bf5" fill-opacity="0.4"/><text x="270" y="169" text-anchor="middle">A を表示</text>
<rect x="340" y="150" width="140" height="28" fill="#4c8bf5" fill-opacity="0.4"/><text x="410" y="169" text-anchor="middle">B を表示</text>
<rect x="480" y="150" width="140" height="28" fill="#e5aa28" fill-opacity="0.4"/><text x="550" y="169" text-anchor="middle">B をもう一度（C が間に合わず）</text>
<rect x="620" y="150" width="140" height="28" fill="#4c8bf5" fill-opacity="0.4"/><text x="690" y="169" text-anchor="middle">C を表示</text>
</g>
<text x="60" y="260" style="font-size:12px">フレーム C が遅れた分、同じ絵が 2 回表示される → 動きがカクッとして見える</text>
</svg>

| 状況 | 結果 |
| --- | --- |
| **フレームが 16.7 ms 以内** | **60 FPS で滑らか** |
| **少しでも超える** | **次の更新まで待つ → 実質 30 FPS** |
| **VSync なし** | **FPS は不規則だが遅延は小さい** |

<strong>可変リフレッシュ（G-Sync／FreeSync）</strong>に対応した**ディスプレイ**では、**ディスプレイ側が Present のタイミングに合わせて更新**するので、**ティアリングもカクつきも減ります**。

## フレーム レートとフレーム時間

| FPS | 1 フレームの時間 |
| --- | --- |
| **30** | **33.3 ms** |
| **60** | **16.7 ms** |
| **120** | **8.3 ms** |
| **144** | **6.9 ms** |

**フレーム時間が「平均が良い」だけでなく、一定であること**が**滑らかさ**には**大切**です。**時々だけ重い（スパイク）フレームは体感でカクつく**ので**最適化は平均だけでなく最悪のフレーム**を**見ます**（[フレーム時間の設計](../../optimize/frame-budget.md)）。

## 入力から表示までの遅延

**ボタンを押してから画面に反映されるまで**には、**いくつもの待ち時間**があります。

<svg class="fig illust" viewBox="0 0 780 160" role="img" aria-label="入力遅延">
<text x="20" y="24" class="fig-title">入力 → 更新 → 描画 → 表示：遅延が積み重なる</text>
<g font-size="12">
<rect x="20" y="60" width="130" height="50" fill="#4c8bf5" fill-opacity="0.25" stroke="#4c8bf5"/><text x="85" y="90" text-anchor="middle">入力を受け取る</text>
<rect x="170" y="60" width="130" height="50" fill="#4c8bf5" fill-opacity="0.25" stroke="#4c8bf5"/><text x="235" y="90" text-anchor="middle">ゲーム更新</text>
<rect x="320" y="60" width="130" height="50" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28"/><text x="385" y="90" text-anchor="middle">描画命令を作る</text>
<rect x="470" y="60" width="130" height="50" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043"/><text x="535" y="90" text-anchor="middle">GPU が描く</text>
<rect x="620" y="60" width="130" height="50" fill="#e5484d" fill-opacity="0.25" stroke="#e5484d"/><text x="685" y="90" text-anchor="middle">画面に表示</text>
</g>
<text x="20" y="145" style="font-size:12px">バッファが多い・先読みが多い・VSync がある、ほど遅延が増える。格闘ゲームなどでは重要。</text>
</svg>

| 遅延を減らす方法 | 内容 |
| --- | --- |
| **VSync を切る／可変リフレッシュ** | **待ち時間を減らす** |
| **先読みフレーム数を減らす** | **CPU が先に積むフレームを 1〜2 に** |
| **バック バッファを減らす** | **3 → 2 枚**（FPS が不安定になりやすい） |
| **入力を遅く読む** | **描画直前に入力を取る** |

## ウィンドウのリサイズと全画面

| 場面 | 処理 |
| --- | --- |
| **ウィンドウのサイズ変更** | **バック バッファを作り直す**（`ResizeBuffers`）。**深度バッファ・レンダー ターゲットも作り直す** |
| <strong>全画面（フルスクリーン）</strong> | **排他的全画面・ボーダーレス ウィンドウ**。**今は後者が主流** |
| **解像度とスケール** | **内部解像度を下げて描いて、画面の大きさに拡大**（[アップスケール](../../rendering/taa-upscaling.md)） |
| **HDR 出力** | <strong>バック バッファを HDR 形式（R10G10B10A2 など）</strong> にする |

## よくあるミス

??? failure "ウィンドウをリサイズすると、画面がぼやける／描画が崩れる"
    **`ResizeBuffers` で作り直し、ビューポートと深度バッファも更新**する。

??? failure "VSync を切ったら、画面が裂ける"
    **ティアリングは、VSync を切ったときの正常な結果**。**VSync を入れるか、可変リフレッシュに対応**する。

??? failure "60 FPS のはずが、30 FPS に落ちる"
    **VSync あり**で**16.7 ms を超えた**。**フレーム時間を詰める**。

??? failure "古い swap effect（BITBLT）で、遅く、機能が足りない"
    **`FLIP_DISCARD`** を使う。

??? failure "ガンマが二重に掛かって、画面が白っぽい"
    **バック バッファが `_SRGB` なら、シェーダーでガンマ補正をしない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 絵は<strong>バック バッファ</strong>に描き、<strong>Present で入れ替える</strong>（<strong>ダブル バッファリング</strong>）
    - [x] <strong>スワップチェーン</strong>が<strong>画面とバック バッファを管理</strong>
    - [x] <strong>VSync あり</strong> ＝ <strong>ティアリングなし・遅延あり</strong>。<strong>なし</strong> ＝ <strong>低遅延・ティアリングあり</strong>
    - [x] <strong>60 Hz で 16.7 ms</strong>。<strong>間に合わないと 30 FPS 相当に落ちる</strong>
    - [x] <strong>リサイズ時</strong>は<strong>バッファの作り直し</strong>

## 参考

- Microsoft, "DXGI Flip Model"（Microsoft Learn）
- Microsoft, "IDXGISwapChain::Present"（Microsoft Learn）
- NVIDIA, "G-SYNC 101"

## 関連ページ

- [描画の流れ（入門）](index.md)
- [深度・ブレンド](output-merger.md)
- [1 フレームの中身](frame-passes.md)
- [フレーム時間の設計](../../optimize/frame-budget.md)
