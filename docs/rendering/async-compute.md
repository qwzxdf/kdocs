---
title: 非同期コンピュート
tags:
  - 最適化
  - 3Dゲーム
---

# 非同期コンピュート

GPU は、1 つの処理の間もすべての部品が忙しいわけではありません。たとえば影マップの描画は、ピクセルシェーダーが不要なので ALU（計算ユニット）が空きます。逆に、AO やライト カリングのコンピュート シェーダーは、ALU を使いますが固定機能（ラスタライザなど）は遊んでいます。**非同期コンピュート**は、描画とコンピュートを別のキューで同時に走らせて、GPU の空きを埋める方法です。

!!! tip "ポイント"
    - 目的は<strong>GPU の稼働率を上げて、フレーム時間を短くする</strong>こと。
    - 描画（グラフィックス キュー）とコンピュート（コンピュート キュー）を<strong>並行</strong>して実行する。
    - 向く組み合わせは「ALU を使う処理」と「メモリ・固定機能を使う処理」。
    - DX12・Vulkanの機能。DX11 にはない。
    - 同期（フェンス）の設計が必要。効果は GPU と内容で変わるので、測る。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 何が改善するのか

GPU の処理は、段階ごとに使う部品が違います。1 つの処理だけでは、特定の部品が空いてしまいます。

| 処理 | 主に使う部品 | 空いている部品 |
| --- | --- | --- |
| **影マップの描画** | 頂点処理・ラスタライザ・ROP | ALU（ピクセルシェーダーが不要） |
| 深度プリパス | 同上 | ALU |
| AO・ライト カリング（コンピュート） | ALU・メモリ | ラスタライザ・ROP |
| ポストプロセス（メモリ中心） | メモリ帯域 | ALU |

影マップの描画の間に、AO のコンピュートを並行して走らせると、ALU の空きが埋まって、全体の時間が短くなります。

<svg class="fig illust" viewBox="0 0 800 220" role="img" aria-label="非同期コンピュートの時間軸">
<text x="20" y="24" class="fig-title">上：直列に実行／下：並行して実行すると、全体が短くなる</text>
<text x="20" y="70" style="font-size:12px">直列</text>
<rect x="70" y="50" width="220" height="30" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="180" y="70" text-anchor="middle" style="font-size:12px">影マップの描画</text>
<rect x="290" y="50" width="180" height="30" fill="rgba(150,100,230,0.4)" stroke="currentColor"/><text x="380" y="70" text-anchor="middle" style="font-size:12px">AO（コンピュート）</text>
<text x="490" y="70" style="font-size:12px">合計：400</text>
<text x="20" y="140" style="font-size:12px">並行</text>
<rect x="70" y="120" width="220" height="30" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="180" y="140" text-anchor="middle" style="font-size:12px">影マップの描画</text>
<rect x="70" y="154" width="180" height="30" fill="rgba(150,100,230,0.4)" stroke="currentColor"/><text x="160" y="174" text-anchor="middle" style="font-size:12px">AO（別キュー）</text>
<text x="310" y="140" style="font-size:12px">合計：約 250（短くなる）</text>
</svg>

## 仕組み

| 概念 | 説明 |
| --- | --- |
| **キュー** | GPU に命令を送る列。グラフィックス・コンピュート・コピーの 3 種類がある |
| コマンド リスト | キューごとに別々に記録し、並行して送る |
| フェンス | キュー間の依存関係を表す。AO は深度が完成してから、など |
| リソースの共有 | 同じリソースを 2 つのキューが同時に触らないように、バリアで管理する |

## 向く組み合わせ

| グラフィックス側 | コンピュート側 |
| --- | --- |
| 影マップの描画 | AO・ライト カリング |
| 深度プリパス | クラスター ライトの割り当て |
| G-Buffer の描画 | 前フレームのポストプロセス・パーティクル更新 |
| ライティング | SSR・ボリューメトリック フォグの準備 |

## 注意点

| 注意 | 説明 |
| --- | --- |
| **GPU による差** | 並行の効果はハードウェアの設計で大きく変わる。逆に遅くなる場合もある |
| キャッシュの奪い合い | 2 つの処理が同じキャッシュを使うと、お互いに遅くなる |
| 同期のコスト | フェンスが多いと待ちが増える |
| デバッグが難しい | 実行順序が非決定的になる。ツールで確認する |
| DX11 では不可 | 単一のキューで直列に実行される |

<!-- fig:async-compute-gantt:begin -->

<svg class="fig illust motion" data-fig="async-compute-gantt" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-async-compute-gantt" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">非同期コンピュート: 別の列で同時に走らせ、全体の時間を縮める</text>
<text x="40" y="85" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">ふつう（1 列で順番に）</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/><rect x="70.0" y="105" width="77.0" height="38" fill="#2563eb" opacity="0.9"/>
<text x="110.0" y="129" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">影</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1172;1.0000" values="0;0;1;1"/><rect x="150.0" y="105" width="157.0" height="38" fill="#2ea043" opacity="0.9"/>
<text x="230.0" y="129" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">G-Buffer</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;1.0000" values="0;0;1;1"/><rect x="310.0" y="105" width="117.0" height="38" fill="#e5aa28" opacity="0.9"/>
<text x="370.0" y="129" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">ライティング</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2135;0.2138;1.0000" values="0;0;1;1"/><rect x="430.0" y="105" width="37.0" height="38" fill="#64748b" opacity="0.9"/>
<text x="450.0" y="129" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">合成</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;1.0000" values="0;0;1;1"/><rect x="470.0" y="105" width="77.0" height="38" fill="#7c3aed" opacity="0.9"/>
<text x="510.0" y="129" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">パーティクル</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3101;0.3103;1.0000" values="0;0;1;1"/><rect x="550.0" y="105" width="77.0" height="38" fill="#e5484d" opacity="0.9"/>
<text x="590.0" y="129" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">SSAO</text>
</g>
<text x="630.0" y="160" text-anchor="end" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">14 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3790;0.3793;1.0000" values="0;0;1;1"/></text>
<text x="40" y="205" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">非同期（グラフィックス列 + コンピュート列）</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4480;0.4483;1.0000" values="0;0;1;1"/><rect x="70.0" y="225" width="77.0" height="38" fill="#2563eb" opacity="0.9"/>
<text x="110.0" y="249" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">影</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000" values="0;0;1;1"/><rect x="150.0" y="225" width="157.0" height="38" fill="#2ea043" opacity="0.9"/>
<text x="230.0" y="249" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">G-Buffer</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5170;0.5172;1.0000" values="0;0;1;1"/><rect x="310.0" y="225" width="117.0" height="38" fill="#e5aa28" opacity="0.9"/>
<text x="370.0" y="249" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">ライティング</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5517;1.0000" values="0;0;1;1"/><rect x="430.0" y="225" width="37.0" height="38" fill="#64748b" opacity="0.9"/>
<text x="450.0" y="249" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">合成</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5859;0.5862;1.0000" values="0;0;1;1"/><rect x="70.0" y="272" width="77.0" height="38" fill="#7c3aed" opacity="0.9"/>
<text x="110.0" y="296" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">パーティクル</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;1.0000" values="0;0;1;1"/><rect x="310.0" y="272" width="77.0" height="38" fill="#e5484d" opacity="0.9"/>
<text x="350.0" y="296" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">SSAO</text>
</g>
<text x="470.0" y="340" text-anchor="end" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">10 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6894;0.6897;1.0000" values="0;0;1;1"/></text>
<text x="40" y="252" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">GFX</text>
<text x="40" y="298" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">計算</text>
<text x="390" y="385" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">パーティクルは影と同時に、SSAO はライティングと同時に走らせる(GPU に空きがあるときだけ得をする)</text>
</svg>

<!-- fig:async-compute-gantt:end -->

## D3D12 での実装

コンピュート キューを作って、グラフィックス キューと、フェンスでつなぎます（[Command Queue](../directx/dx12/command-queue.md)、[Fence](../directx/dx12/fence.md)）。

```cpp
// コンピュート キュー（描画と並列に走る）。
D3D12_COMMAND_QUEUE_DESC desc = {};
desc.Type = D3D12_COMMAND_LIST_TYPE_COMPUTE;
device->CreateCommandQueue(&desc, IID_PPV_ARGS(&compute_queue));
// コマンド アロケーターと、コマンド リストも、COMPUTE の種類で作る。
```

流れの例です。<strong>深度を描き終えたら、AO の計算を、コンピュート キューで始め</strong>、同時に、グラフィックス キューで、影を描きます。ライティングは、AO の完了を待ちます。

```cpp
// ① グラフィックス: 深度プリパス。
graphics_queue->ExecuteCommandLists(1, depth_prepass_list);
graphics_queue->Signal(fence.Get(), ++depth_done);            // 深度が、できた目印

// ② コンピュート: 深度を待って、AO を計算（GPU 同士の待ち。CPU は止まらない）。
compute_queue->Wait(fence.Get(), depth_done);
compute_queue->ExecuteCommandLists(1, ao_list);
compute_queue->Signal(fence.Get(), ++ao_done);                // AO が、できた目印

// ③ グラフィックス: AO と並列に、影マップを描く。
graphics_queue->ExecuteCommandLists(1, shadow_list);

// ④ グラフィックス: ライティングは、AO の完了を待ってから。
graphics_queue->Wait(fence.Get(), ao_done);
graphics_queue->ExecuteCommandLists(1, lighting_list);
```

②の `Wait` は、GPU 側の待ちで、CPU は止まりません。③の影マップは、AO と並列に、実行されます。

## リソースの扱い

コンピュート キューは、グラフィックス キューと、<strong>別のキュー</strong>なので、リソースの状態の扱いに、注意が要ります。

| 注意 | 内容 |
| --- | --- |
| 状態の遷移は、リストを実行するキューで | コンピュート キューは、描画用の状態（`RENDER_TARGET` など）への遷移が、できない |
| 深度を、読む前に | 深度を、`NON_PIXEL_SHADER_RESOURCE` へ遷移するバリアを、グラフィックス キューの、リストの最後に入れて、`Signal` する |
| 結果の、受け渡し | AO の出力は、`UNORDERED_ACCESS` で書き、ライティングで読む前に、`PIXEL_SHADER_RESOURCE` へ遷移（グラフィックス キュー側） |
| 同時に、触らない | 2 つのキューが、同じリソースを、同時に読み書きしない |

## 効果が出る場面と、出ない場面

| 状況 | 結果 |
| --- | --- |
| 影マップ（ALU が空く）と AO（ALU を使う） | 重なって、全体が速くなりやすい |
| 帯域を、使い切る処理どうし | 並列にしても、帯域を、奪い合って、速くならない |
| 1 つの処理が、GPU 全体を、使い切っている | 並列にする余地がない。順番に走るだけ |
| 同期（`Wait`）が、多すぎる | 待ちが、増えて、かえって遅くなる |

効果は、GPU の世代や、処理の内容で、大きく変わります。<strong>必ず、PIX の、タイミング キャプチャで、2 つのキューが、実際に重なって走っているか</strong>を確認し、フレーム時間を、導入前後で比べます。重なっていなければ、効果は、ありません（[調査ツール](tools.md)）。

## よくあるミス

??? failure "効果を測らずに導入する"
    GPU によっては遅くなります。必ずフレーム時間を比べます。

??? failure "依存関係の同期が足りず、結果が壊れる"
    フェンスとバリアで順序を保証します。

??? failure "同じ種類の処理を並行させる"
    同じ部品を使う処理は、並行しても速くなりません。

??? failure "DX11 で使おうとする"
    DX12 や Vulkan が必要です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>GPU の空いた部品を、別の処理で埋める</strong>
    - [x] ALU 中心とメモリ中心の処理を組み合わせる
    - [x] DX12 / Vulkan の機能。DX11 にはない
    - [x] フェンス・バリアで同期する
    - [x] 測って効果を確認する

## 関連ページ

- [描画最適化](index.md)
- [影のコスト](shadows.md)
- [Tiled と Clustered](light-culling.md)
- [調査ツール](tools.md)
