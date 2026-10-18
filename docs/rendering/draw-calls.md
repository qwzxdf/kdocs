---
title: ドロー コールとバッチ
tags:
  - 最適化
  - 3Dゲーム
---

# ドロー コールとバッチ

**ドロー コール**は、**CPU が GPU に出す、「これを描いて」という、1 回の命令**です。**GPU は速く描けても、CPU が命令を作るのが遅い**と、**GPU は待たされます**。特に **DirectX 11 は、ドライバが命令ごとに検査・変換**をするので**数千回を超えると、CPU が詰まりやすい**です。このページは**ドロー コールの何が重いのか**、<strong>減らす方法（バッチ・インスタンシング・状態の整理）</strong>を、**目的から**説明します（入口は [描画の最適化](pipeline.md)）。

!!! tip "ポイント"
    - ドロー コールの<strong>コストは、描く量ではなく「命令の回数」に比例</strong>（<strong>CPU 側のドライバの仕事</strong>）。
    - 重い理由：<strong>検査・状態の変換・コマンドの作成</strong>。<strong>1 回あたり、数〜数十マイクロ秒</strong>。
    - 減らす方法：<strong>① まとめる（バッチ・結合）　② 同じメッシュを、1 回で（インスタンシング）　③ 状態の切り替えを減らす（ソート）　④ 見えないものを描かない（カリング）</strong>。
    - <strong>状態の切り替え</strong>（シェーダー・テクスチャ・ブレンド）は、<strong>ドロー コール以上に重い</strong>ことがある。
    - 根本的な解決：<strong>GPU Driven</strong>（<strong>命令を、GPU 自身に作らせる</strong>）（[GPU Driven](gpu-driven.md)）。
    - <strong>測ってから</strong>。<strong>CPU がボトルネックのときだけ、効く</strong>（[何が重いのか](bottlenecks.md)）。

## なぜ、ドロー コールが重いのか

**1 回の描画命令**には、**GPU に実行させるための、準備**が、**CPU 側で必要**です。

| 処理 | 内容 |
| --- | --- |
| **状態の検査** | **シェーダー・テクスチャ・RT の組み合わせが正しいか** |
| **状態の変換** | **API の状態を、GPU のハードウェア命令に、変換** |
| **コマンドの作成** | **GPU が読む、コマンド バッファに書き込み** |
| **リソースの管理** | **使うバッファ・テクスチャの追跡**（メモリ配置・同期） |

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ドロー コールの、CPU コスト">
<text x="20" y="24" class="fig-title">1000 個の木を描く：1 本ずつ（1000 回）と、まとめて（1 回）</text>
<text x="20" y="64" style="font-weight:700">1 本ずつ</text>
<g fill="rgba(229,72,77,0.4)" stroke="currentColor" stroke-width="1">
<rect x="110" y="46" width="40" height="26"/><rect x="152" y="46" width="40" height="26"/><rect x="194" y="46" width="40" height="26"/><rect x="236" y="46" width="40" height="26"/><rect x="278" y="46" width="40" height="26"/><rect x="320" y="46" width="40" height="26"/><rect x="362" y="46" width="40" height="26"/><rect x="404" y="46" width="40" height="26"/><rect x="446" y="46" width="40" height="26"/><rect x="488" y="46" width="40" height="26"/><rect x="530" y="46" width="40" height="26"/><rect x="572" y="46" width="40" height="26"/><rect x="614" y="46" width="40" height="26"/><rect x="656" y="46" width="40" height="26"/><rect x="698" y="46" width="60" height="26"/>
</g>
<text x="110" y="92" style="font-size:12px">命令 × 1000（毎回、準備）→ CPU の時間：約 5〜15 ms（目安）</text>
<text x="20" y="146" style="font-weight:700">まとめて</text>
<rect x="110" y="128" width="40" height="26" fill="rgba(46,160,67,0.45)" stroke="currentColor" stroke-width="1"/>
<text x="160" y="146" style="font-size:12px">命令 × 1（インスタンシング）→ CPU の時間：ほぼゼロ。GPU が、1000 個を、まとめて描く</text>
<text x="20" y="206" style="font-size:12px">GPU が描く量（三角形の数）は、同じ。減るのは、CPU の「命令の回数」</text>
<text x="20" y="226" style="font-size:12px">※ 時間は、環境による目安（ドライバ・API・状態の複雑さで変わる）</text>
</svg>

**目安**：**DX11 で数千ドロー コール/フレーム**が、**CPU の限界**になりやすい（**1 回あたり 数〜数十 µs**）。**DX12・Vulkan**は、**ドライバの仕事が少なく、数倍多く出せる**。

## 減らす方法

### 1. 結合（スタティック バッチ）

**動かない物体**（建物・地形・小物）の、**メッシュを、1 つに結合**して、**1 回で描きます**。

| 利点 | 欠点 |
| --- | --- |
| **ドロー コールが減る** | **メモリが増える**（インスタンスの共有がなくなる） |
| **簡単** | **個別にカリング・移動ができない**（結合した単位） |

**同じ材質**（シェーダー・テクスチャ）の物体だけが**結合できます**。**ビルド時にまとめる**のが定番です（[ベイク](../optimize/baking.md)）。

### 2. インスタンシング

**同じメッシュを位置・色・回転だけ、変えて、多数描く**のに、**1 回の命令**で済ませます。

```cpp
context->DrawIndexedInstanced(index_count, instance_count, 0, 0, 0);
```

| 利点 | 説明 |
| --- | --- |
| **ドロー コール 1 回** | **1000 本の木が、1 回**で |
| **インスタンスごとのデータ** | **ワールド行列・色**を**インスタンス用の頂点バッファ**（`D3D11_INPUT_PER_INSTANCE_DATA`）、または**構造化バッファ**に |
| **メモリが少ない** | **メッシュは、1 つ** |

<strong>木・草・岩・弾・敵（同じ種類）</strong>に、最適です（[メッシュとテクスチャ](../3d/mesh-textures.md)）。**メッシュが違う**物は**インスタンシングできません**（→ GPU Driven）。

### 3. 状態の切り替えを、減らす

**ドロー コール以上に重い**のが**状態の切り替え**（**シェーダー・テクスチャ・ブレンド・レンダーターゲット**）です。

| 切り替え | コスト |
| --- | --- |
| <strong>シェーダー（パイプライン）</strong> | **重い** |
| **レンダーターゲット** | **重い**（**パスが変わる**） |
| **テクスチャ（SRV）の変更** | **中** |
| **定数バッファの更新** | **軽〜中** |
| **ブレンド・深度ステート** | **軽〜中** |

| 工夫 | 説明 |
| --- | --- |
| **ソートする** | **シェーダー → テクスチャ → メッシュ**の順に、**並べ替えて**、**同じ状態を連続**させる（**ソート キー**） |
| **材質をまとめる** | **シェーダーの種類を減らす**（バリアントを絞る） |
| **テクスチャ アトラス** | **小さな画像を、1 枚に**（テクスチャの切り替えを、なくす） |
| **テクスチャ配列** | **同じ大きさのテクスチャを配列に**し、**インデックスで選ぶ**（切り替え不要） |
| **バインドレス** | <strong>（DX12・新しい API）テクスチャを番号で参照</strong>（切り替え自体が不要） |

### 4. 定数バッファの更新を、減らす

**物体ごとに、`Map` / `Unmap` で、ワールド行列を書く**と、**CPU・同期が重い**です。

| 工夫 | 説明 |
| --- | --- |
| **大きな 1 つのバッファに、まとめて書く** | **全物体の行列を、1 回の `Map` で**、**構造化バッファ**に書き、**インデックスで選ぶ** |
| **`D3D11_MAP_WRITE_DISCARD`** | **前の内容を破棄**して、**同期待ちを避ける** |
| **更新頻度で分ける** | **毎フレーム・物体ごと・材質ごと・不変**で**定数バッファを分割** |

### 5. 見えないものを、描かない

**カリング**（[カリング](culling.md)）で、**そもそも命令を出さない**のが**最も効果的**です。

### 6. マルチスレッドでの、コマンド作成

| 方法 | 説明 |
| --- | --- |
| **ディファード コンテキスト**（DX11） | **複数スレッドでコマンド リストを記録**し、**メインで実行**。**効果はドライバ次第**（**限定的**） |
| **DX12 / Vulkan** | **コマンド リストの並列記録**が**本来の機能**（CPU の負担を大きく減らす） |

**DX11 のディファード コンテキストは、期待ほど、効かない**ことが多いです。

## 目安と段階

| 規模 | 対策 |
| --- | --- |
| **〜数百ドロー コール** | **気にしなくてよい** |
| **数百〜数千** | **ソート・バッチ・インスタンシング** |
| **数千〜数万** | **GPU Driven**（[GPU Driven](gpu-driven.md)） |
| **それ以上** | **GPU Driven ＋ Meshlet**（[Mesh Shader](mesh-shaders.md)） |

<!-- fig:state-sort:begin -->

<svg class="fig illust motion" data-fig="state-sort" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-state-sort" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">マテリアルでソートすると、状態の切り替え回数が減る</text>
<text x="70" y="88" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">描く順（ソートなし）</text>
<rect x="70" y="100" width="56" height="56" fill="#2563eb" opacity="0.9"/>
<text x="98.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">A</text>
<rect x="132" y="100" width="56" height="56" fill="#2ea043" opacity="0.9"/>
<text x="160.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">B</text>
<rect x="127" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0933;0.0935;1.0000" values="0;0;1;1"/></rect>
<rect x="194" y="100" width="56" height="56" fill="#2563eb" opacity="0.9"/>
<text x="222.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">A</text>
<rect x="189" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1223;0.1226;1.0000" values="0;0;1;1"/></rect>
<rect x="256" y="100" width="56" height="56" fill="#e5aa28" opacity="0.9"/>
<text x="284.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">C</text>
<rect x="251" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1516;1.0000" values="0;0;1;1"/></rect>
<rect x="318" y="100" width="56" height="56" fill="#2ea043" opacity="0.9"/>
<text x="346.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">B</text>
<rect x="313" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1806;1.0000" values="0;0;1;1"/></rect>
<rect x="380" y="100" width="56" height="56" fill="#e5aa28" opacity="0.9"/>
<text x="408.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">C</text>
<rect x="375" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2094;0.2097;1.0000" values="0;0;1;1"/></rect>
<rect x="442" y="100" width="56" height="56" fill="#2563eb" opacity="0.9"/>
<text x="470.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">A</text>
<rect x="437" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2385;0.2387;1.0000" values="0;0;1;1"/></rect>
<rect x="504" y="100" width="56" height="56" fill="#2ea043" opacity="0.9"/>
<text x="532.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">B</text>
<rect x="499" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2675;0.2677;1.0000" values="0;0;1;1"/></rect>
<rect x="566" y="100" width="56" height="56" fill="#e5aa28" opacity="0.9"/>
<text x="594.0" y="133.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">C</text>
<rect x="561" y="98" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2965;0.2968;1.0000" values="0;0;1;1"/></rect>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.0933;0.0935;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0933;0.0935;0.1223;0.1226;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1223;0.1226;0.1514;0.1516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1516;0.1804;0.1806;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1806;0.2094;0.2097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2094;0.2097;0.2385;0.2387;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2385;0.2387;0.2675;0.2677;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2675;0.2677;0.2965;0.2968;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="194" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2965;0.2968;1.0000" values="0;0;1;1"/></text>
<text x="98" y="194" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">回、マテリアルを切り替えた（赤い線）</text>
<text x="70" y="238" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">マテリアルで並べ替えた順</text>
<rect x="70" y="250" width="56" height="56" fill="#2563eb" opacity="0.9"/>
<text x="98.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">A</text>
<rect x="132" y="250" width="56" height="56" fill="#2563eb" opacity="0.9"/>
<text x="160.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">A</text>
<rect x="194" y="250" width="56" height="56" fill="#2563eb" opacity="0.9"/>
<text x="222.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">A</text>
<rect x="256" y="250" width="56" height="56" fill="#2ea043" opacity="0.9"/>
<text x="284.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">B</text>
<rect x="251" y="248" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1516;1.0000" values="0;0;1;1"/></rect>
<rect x="318" y="250" width="56" height="56" fill="#2ea043" opacity="0.9"/>
<text x="346.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">B</text>
<rect x="380" y="250" width="56" height="56" fill="#2ea043" opacity="0.9"/>
<text x="408.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">B</text>
<rect x="442" y="250" width="56" height="56" fill="#e5aa28" opacity="0.9"/>
<text x="470.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">C</text>
<rect x="437" y="248" width="4" height="60" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2385;0.2387;1.0000" values="0;0;1;1"/></rect>
<rect x="504" y="250" width="56" height="56" fill="#e5aa28" opacity="0.9"/>
<text x="532.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">C</text>
<rect x="566" y="250" width="56" height="56" fill="#e5aa28" opacity="0.9"/>
<text x="594.0" y="283.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#ffffff">C</text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.0933;0.0935;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0933;0.0935;0.1223;0.1226;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1223;0.1226;0.1514;0.1516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1516;0.1804;0.1806;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1806;0.2094;0.2097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2094;0.2097;0.2385;0.2387;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2385;0.2387;0.2675;0.2677;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2675;0.2677;0.2965;0.2968;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="344" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2965;0.2968;1.0000" values="0;0;1;1"/></text>
<text x="98" y="344" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">回、マテリアルを切り替えた（赤い線）</text>
</svg>

<!-- fig:state-sort:end -->

## よくあるミス

??? failure "GPU が、ボトルネックなのにドロー コールを減らす"
    **効果がありません**（[何が重いのか](bottlenecks.md)）。

??? failure "全部を、1 つのメッシュに結合して、カリングできなくなる"
    **結合の単位**を**カリングの粒度**に合わせます。

??? failure "物体ごとに、定数バッファを `Map` して、CPU が重い"
    **まとめて、1 回の書き込み**にします。

??? failure "同じメッシュを、1 つずつ、描いている"
    **インスタンシング**にします。

??? failure "ソートせず、状態を頻繁に切り替える"
    **シェーダー・テクスチャでソート**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ドロー コールの重さは<strong>CPU の「命令の回数」</strong>。<strong>DX11 は特にドライバの仕事が多い</strong>
    - [x] 減らす：<strong>結合・インスタンシング・状態のソート・カリング</strong>
    - [x] <strong>状態の切り替え（シェーダー・RT）は、ドロー コール以上に重い</strong>
    - [x] 定数バッファは<strong>まとめて 1 回で書く</strong>
    - [x] 数千を超えたら<strong>GPU Driven</strong>。<strong>CPU がボトルネックのときだけ、効く</strong>

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [何が重いのか](bottlenecks.md)
- [カリング](culling.md)
- [GPU Driven Rendering](gpu-driven.md)
- [描画の最適化（入口）](pipeline.md)
