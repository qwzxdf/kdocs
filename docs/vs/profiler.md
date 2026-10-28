---
title: パフォーマンス プロファイラー
tags:
  - Visual Studio
---

# パフォーマンス プロファイラー

プログラムが遅いとき、**勘で直す**のではなく、どこで時間を使っているかをプロファイラーで測ります。Visual Studio には、パフォーマンス プロファイラーが入っていて、CPU の使用率、メモリの使用量、GPU の使用率などをグラフと表で見られます。このページは使い方（起動・測り方・結果の読み方）と、測る前の準備、ほかのツール（PIX、Tracy など）をまとめます。最適化の考え方は、[計測（プロファイリング）](../optimize/measure.md)にあります。

!!! tip "ポイント"
    - <strong>Release 構成で測る</strong>（Debug は別物）。<strong>ただし、デバッグ情報（`.pdb`）は付けておく</strong>（関数名が見えるように）。
    - 起動は 「デバッグ」→「パフォーマンス プロファイラー」（Alt + F2）。デバッガーなしで実行して測る。
    - まず CPU 使用率。「ホット パス」（一番時間を使っている呼び出しの流れ）を見る。
    - 「合計 CPU」（その関数と呼んだ先の合計）と、「自己 CPU」（その関数自身だけ）を区別して読む。
    - 測る時間は、遅い場面だけ。同じ場面を何度も測って、比べる。
    - GPU が遅いなら、Visual Studio のツールより、PIX・RenderDoc が向く。

!!! info "このページを読む前に"
    - [vs/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [インストールとプロジェクトの作成](setup.md)（Visual Studio の準備）

## 測る前の準備

### 構成は Release

| 構成 | 速さ | プロファイルに向くか |
| --- | --- | --- |
| **Debug** | 何倍も遅い（最適化なし、検査あり） | 向かない。本番と違う場所が遅く見える |
| Release | 本番に近い | 向く |

### デバッグ情報を付ける

Release では、既定でデバッグ情報（`.pdb`）が作られますが関数名の解決に必要です。

| 設定 | 場所 | 値 |
| --- | --- | --- |
| デバッグ情報の形式 | C/C++ → 全般 | プログラム データベース（/Zi）（Release でも付ける） |
| デバッグ情報の生成 | リンカー → デバッグ | デバッグ情報を生成する：はい（/DEBUG） |
| 参照されない関数を除去 | リンカー → 最適化 | `/OPT:REF`、`/OPT:ICF`（Release の既定）。関数名がまとめられて見えることがある |
| フレーム ポインターの省略 | C/C++ → 最適化 | 呼び出し履歴がうまくたどれないときは、`/Oy-`（省略しない）で測る |

!!! note "ICF（同一の関数をまとめる最適化）"
    `/OPT:ICF` は中身が同じ関数を 1 つにまとめます。プロファイラーで別の関数名で表示されることがあります。気になるときは、`/OPT:NOICF` で測ります。

### 測りやすい構成を作る

Debug / Release のほかに、「Profile」構成を作る方法があります（Release をコピーして、デバッグ情報つき、プロファイラー用のマクロを有効にする）。

```text
Debug：    最適化なし、デバッグ検査あり
Profile：  Release と同じ最適化 + デバッグ情報 + ENABLE_PROFILER
Release：  最適化 + 製品用（プロファイラーなし）
```

（[プリプロセッサマクロ](preprocessor.md)）

### 測る環境

| 注意 | 説明 |
| --- | --- |
| ほかのアプリを閉じる | ブラウザー・ウイルス対策などが、CPU を使うとぶれる |
| 電源プラン | 高パフォーマンス。ノート PC は、電源につなぐ |
| VSync を切る | VSync がフレーム時間を一定にしてしまう |
| 同じ場面を測る | リプレイや固定シードの再現ができると、比べやすい |
| ウォームアップ | 起動直後はキャッシュやロードの影響が出る。少し待ってから測る |

## プロファイラーを使う

### 起動する

1. **デバッグ → パフォーマンス プロファイラー**（Alt + F2）を開く
2. ターゲット（開始するプロジェクト）を選ぶ
3. 使うツール（CPU の使用率など）にチェックを入れる
4. 開始を押す
5. ゲームが起動するので、測りたい場面を実行する
6. 終了（ゲームを閉じる、または収集の停止を押す）
7. レポート（`.diagsession`）が開く

デバッガーをつけずに実行されるので、Release に近い速さで測れます。

メニューは「デバッグ」の中にあります。

![デバッグ メニュー。パフォーマンス プロファイラー（Alt + F2）がある](img/debug-menu.jpg)

開いたタブが次の画面です。上の「分析ターゲット」が測る対象で、既定は「スタートアップ プロジェクト」です。その下の「フレキシブル」に使えるツールがチェックボックスで並びます。下のほうにある「開始」ボタンで、測定を始めます。ここでは、まだ何もチェックしていないので、「開始」が灰色になっています。

![パフォーマンス プロファイラーの開始画面。CPU 使用率、GPU 使用率、イベント ビューアー、ファイル IO、メモリ使用量が選べる](img/profiler-start.jpg)

上の説明に「ソリューション構成が［リリース］に設定されていることを確認してください」とあるとおり、構成を Release にしてから開きます。

### 使えるツール

| ツール | 内容 |
| --- | --- |
| CPU 使用率 | どの関数が CPU 時間を使っているか。まず、これ |
| メモリ使用量 | ヒープの使用量・確保をスナップショットで調べる |
| GPU 使用率 | GPU の使用率・フレーム時間（DirectX） |
| ファイル IO | ファイルの読み書きの回数と時間 |
| イベント ビューアー | ETW イベントの表示 |
| インストルメンテーション | 関数の呼び出し回数と正確な時間（遅い。対象を絞って使う）。「すべてのツールの表示」を押すと出る |

C++ のゲームで最初に開くのは、「CPU 使用率」です。右上の「すべてのツールの表示」を押すと、ここに出ていないツールも並びます。

!!! note "ツールの名前や位置は、バージョンで変わります"
    ここでの名前は、Visual Studio 2026 の例です。一部のツールは、デバッガーの「診断ツール」ウィンドウ（デバッグ中に出る）でも使えます。

### 診断ツール（デバッグ中）

F5 でデバッグ実行すると、診断ツールが画面に出ます（表示 → 診断ツール、Ctrl + Alt + F2）。

| 機能 | 内容 |
| --- | --- |
| イベント | ブレークポイント、例外、出力 |
| プロセス メモリ | メモリ使用量の推移。リークの発見の入口 |
| CPU 使用率 | CPU の使用率の推移 |

デバッガーがついているので、速さの測定には向きません。メモリの傾向をざっと見る用途です。

## CPU 使用率の読み方

### ホット パス

レポートを開くと、**CPU 使用率のグラフ**と、関数の一覧が出ます。

| ビュー | 内容 |
| --- | --- |
| ホット パス | 一番、時間を使っている呼び出しの流れ（炎のアイコン）をツリーで表示。まず、ここを見る |
| 関数 | 関数ごとの合計 CPU と自己 CPU の一覧 |
| 呼び出し元/呼び出し先 | ある関数を誰が呼び、何を呼んでいるか |
| 呼び出しツリー | 呼び出しの階層（展開して辿る） |
| フレーム グラフ（炎グラフ） | 幅が時間。広い所が重い |
| モジュール | DLL ごとの時間 |
| スレッド | スレッドごとの時間 |

### 合計 CPU と自己 CPU

<svg class="fig flow" viewBox="0 0 885 364" role="img" aria-label="呼び出しツリー：自己 CPU が大きい関数が、直す対象"><defs><marker id="fl76825" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">呼び出しツリー：自己 CPU が大きい関数が直す対象</text><line x1="207.1" y1="87.0" x2="339.4" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76825)"/><line x1="505.9" y1="171.0" x2="648.6" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76825)"/><line x1="153.7" y1="87.0" x2="392.8" y2="293.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76825)"/><rect x="28.0" y="44.0" width="198" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="127.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Update() 合計40% 自己2%</text><rect x="294.0" y="128.0" width="251" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="419.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">UpdateEnemies() 合計30% 自己5%</text><rect x="613.0" y="212.0" width="244" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="735.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FindNearest() 合計25% 自己25%</text><rect x="290.0" y="296.0" width="259" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="419.5" y="316.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">UpdateParticles() 合計8% 自己8%</text></svg>

| 指標 | 意味 |
| --- | --- |
| 合計 CPU（Total） | その関数 + 呼んだ先の、合計時間 |
| 自己 CPU（Self） | その関数自身のコードだけの時間 |

自己 CPU が大きい関数が直す候補です。合計だけ大きい関数は、呼んだ先に原因があります。

### 見るべきもの

| 発見 | 次にすること |
| --- | --- |
| 自己 CPU が大きい関数 | その関数のアルゴリズム・メモリの並びを見直す（[アルゴリズム](../optimize/algorithms.md)、[メモリとキャッシュ](../optimize/memory-cache.md)） |
| `operator new` / `malloc` / `free` が上位 | ヒープ確保が多い（[毎フレームのヒープ確保を避ける](../optimize/frame-allocation.md)） |
| `memcpy` / コンストラクタ / コピー | 無駄なコピー（[コピーとムーブ](../optimize/copy-move.md)） |
| ロックの待ち（`WaitForSingleObject` など） | スレッドの競合（[マルチスレッド化](../optimize/multithreading.md)） |
| ログ・文字列の関数 | 文字列の作成（[文字列とハッシュ](../optimize/strings-hash.md)） |
| STL の内部関数 | どの呼び出し元から来ているかを呼び出し元ビューで確認 |
| 描画のドライバー（D3D・`dxgi`）の関数 | 描画命令の数が多い（[描画の最適化](../rendering/index.md)） |

### ソースコードの行を見る

関数名をダブルクリックすると、ソースコードの各行の時間が見えます（デバッグ情報があれば）。どの行が重いかが分かります。

最適化されたコードは、インライン展開で関数が見えなくなることがあります。呼び出し元の行にまとめられて表示されます。

## メモリ使用量

| 機能 | 内容 |
| --- | --- |
| **スナップショット** | ある時点のヒープの内容を保存。2 つのスナップショットを比べる |
| 差分 | 2 つの間で増えたオブジェクト・確保の場所を表示 |
| ヒープのプロファイリング | 確保の呼び出し元を追跡（有効にして、実行する） |

リークを調べるには、開始後と数分後の、2 回スナップショットを撮って、差分を見ます。確保の呼び出し元が分かれば、原因を特定できます（[デバッグ](debugging.md)、[AddressSanitizer](asan.md)）。

## GPU 使用量

<strong>DirectX（11 / 12）</strong>のアプリで、GPU の使用率、フレーム時間を見られます。

| 内容 | 説明 |
| --- | --- |
| フレーム時間 | 各フレームに GPU がかかった時間 |
| GPU の使用率 | GPU が飽和しているか |
| CPU 待ち | GPU が、CPU を待っていないか |

GPU の細かい調査（どの描画命令・シェーダーが重いか）は、PIXやRenderDocが向いています。

## ほかのツール

| ツール | 特徴 | 使いどころ |
| --- | --- | --- |
| **PIX on Windows** | DirectX の、GPU・CPU のタイミングをキャプチャ。Microsoft 製・無料 | DX11 / DX12 の描画の最適化。描画命令ごとの時間、ステート、シェーダーのデバッグ |
| RenderDoc | グラフィックスのフレームキャプチャ。無料。多くの API に対応 | 描画の不具合の調査、命令の確認 |
| Tracy Profiler | フレームごとの CPU/GPU のゾーンをリアルタイムで表示。ソースにマクロを入れる | ゲーム用に定番。スパイクの調査 |
| Superluminal | 見やすい CPU プロファイラー（有料・評価版あり） | 日常的な CPU の最適化 |
| Windows Performance Analyzer（WPA）+ ETW | OS 全体のトレース | スレッドの待ち、ファイル I/O、システムの影響 |
| Intel VTune / AMD uProf | CPU のカウンター（キャッシュミス、分岐予測ミス） | 低レベルの最適化 |
| Very Sleepy | 軽量で手軽（無料）。サンプリング型 | 簡単に試したいとき |
| 自作のタイマー | `std::chrono` で区間を測る | 画面に表示して、常に監視（[計測](../optimize/measure.md)） |

### サンプリングと計装

| 方式 | 説明 | 長所 | 短所 |
| --- | --- | --- | --- |
| サンプリング | 一定間隔で今、どの関数が動いているかを記録 | 軽い（実行速度に影響が小さい）。コードを変えない | 短い関数は見逃す。正確な回数は不明 |
| 計装（インストルメンテーション） | 関数の入口・出口に計測コードを入れる | 正確な回数・時間 | 遅くなる。計測が結果をゆがめる |

Visual Studio の「CPU 使用率」は、サンプリングです。Tracy などは、自分でマクロを入れる計装です。まずサンプリングで全体を見て、気になる所を計装する、という使い分けです。

## Tracy のようなゲーム向けプロファイラー

**ゲームはフレームごとの動きが重要**です。Visual Studio のプロファイラーは全体の平均を見ますが、Tracy のようなツールは、フレームごとの内訳が見えます。

```cpp
#include <tracy/Tracy.hpp>

void Update() {
  ZoneScoped;
  UpdateEnemies();
  UpdateParticles();
}

void MainLoop() {
  while (running) {
    Update();
    Render();
    FrameMark;
  }
}
```

| 機能 | 説明 |
| --- | --- |
| `ZoneScoped` | 関数のスコープの時間を記録 |
| `FrameMark` | フレームの区切り。フレームごとの時間が分かる |
| メモリの確保の記録 | `operator new` をフックして記録できる |
| GPU のゾーン | DX11 / DX12 に対応 |
| ネットワークで接続 | 別のウィンドウ（プロファイラーの UI）にリアルタイム表示 |

`ENABLE_PROFILER` マクロで、製品ビルドでは、消せるようにしておきます（[プリプロセッサマクロ](preprocessor.md)）。

## 結果の読み方の注意

| 注意 | 説明 |
| --- | --- |
| **1 回の結果を信用しない** | ぶれる。複数回測って、中央値を見る |
| 変更は、1 つずつ | 何が効いたか、分からなくなる |
| 速度は割合で見る | 絶対時間は、PC で変わる。「全体の何 % か」で、優先度を決める |
| サンプリングの偏り | 短い関数は見えにくい |
| 測定が結果を変える | 計装は遅くなる。サンプリングが基本 |
| ボトルネックは移動する | 1 つ直すと次の場所が一番重くなる。また測る |
| 最悪のフレームを見る | 平均でなく、カクつくフレームの内訳（[フレーム時間の設計](../optimize/frame-budget.md)） |

<!-- fig:flame-graph:begin -->

<svg class="fig illust motion" data-fig="flame-graph" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-flame-graph" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">フレーム グラフ: 幅 = かかった時間。幅の広い所が直す候補</text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="70.0" y="290" width="638.0" height="54" fill="#64748b" opacity="0.9"/>
<text x="390.0" y="322" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">Frame 16.0 ms</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2903;1.0000" values="0;0;1;1"/><rect x="70.0" y="228" width="238.0" height="54" fill="#2563eb" opacity="0.9"/>
<text x="190.0" y="260" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">Update 6.0</text>
<rect x="310.0" y="228" width="318.0" height="54" fill="#2ea043" opacity="0.9"/>
<text x="470.0" y="260" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">Render 8.0</text>
<rect x="630.0" y="228" width="78.0" height="54" fill="#cbd5e1" opacity="0.9"/>
<text x="670.0" y="260" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">待ち 2.0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5159;0.5161;1.0000" values="0;0;1;1"/><rect x="70.0" y="166" width="138.0" height="54" fill="#2563eb" opacity="0.9"/>
<text x="140.0" y="198" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">AI 3.5</text>
<rect x="210.0" y="166" width="78.0" height="54" fill="#2563eb" opacity="0.9"/>
<text x="250.0" y="198" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">Physics 2.0</text>
<rect x="290.0" y="166" width="18.0" height="54" fill="#2563eb" opacity="0.9"/>
<text x="300.0" y="198" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff">他 0.5</text>
<rect x="310.0" y="166" width="58.0" height="54" fill="#2ea043" opacity="0.9"/>
<text x="340.0" y="198" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff">Culling 1.5</text>
<rect x="370.0" y="166" width="198.0" height="54" fill="#e5484d" opacity="0.9"/>
<text x="470.0" y="198" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">Draw 5.0</text>
<rect x="570.0" y="166" width="58.0" height="54" fill="#2ea043" opacity="0.9"/>
<text x="600.0" y="198" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#ffffff">UI 1.5</text>
</g>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 フレーム(16 ms)の、関数ごとの時間を積み上げる<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">一番下: フレーム全体<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2901;0.2903;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 段上: Update / Render / 待ち に分ける<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2903;0.5159;0.5161;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">さらに内訳。Draw が 5.0 ms で最大 → まずここを調べる<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5159;0.5161;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:flame-graph:end -->

## よくあるミス

??? failure "Debug で測って、本番と違う場所を直してしまう"
    **Release 構成**で測ります。

??? failure "関数名がアドレスの数字（`0x00007ff6...`）で表示される"
    デバッグ情報（`.pdb`）がありません。`/Zi` と `/DEBUG` を設定して、ビルドし直します。

??? failure "デバッガーをつけたまま、速さを測る"
    F5 ではなく、プロファイラーから起動します（デバッガーなし）。

??? failure "合計 CPU だけを見て、呼び出し先を直す"
    自己 CPU が大きい関数が直す対象です。合計が大きいだけの関数は、呼び出し先に原因があります。

??? failure "VSync が有効のまま測って、GPU の余裕が分からない"
    VSync を切って測ります。

??? failure "遅い場面だけでなく、全体を長時間測って、結果が薄まる"
    遅い場面だけを測ります。

??? failure "プロファイラーのマクロを製品ビルドに残す"
    製品では無効にします（`ENABLE_PROFILER` を定義しない）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Release 構成で測る。`/Zi`・`/DEBUG` でデバッグ情報は付ける
    - [x] 起動は Alt + F2。デバッガーなしで遅い場面だけ測る
    - [x] ホット パスから見る。自己 CPU が大きい関数が直す対象
    - [x] `operator new`・`memcpy`・ロック待ちが上位なら、確保・コピー・競合を疑う
    - [x] GPU は PIX・RenderDoc、フレームごとのスパイクは Tracy など、用途で使い分ける
    - [x] 変更は1 つずつ。直したら、また測る

## 関連ページ

- [Visual Studio（目次）](index.md)
- [計測（プロファイリング）](../optimize/measure.md)
- [フレーム時間の設計](../optimize/frame-budget.md)
- [毎フレームのヒープ確保を避ける](../optimize/frame-allocation.md)
- [デバッグのやり方](debugging.md)
- [AddressSanitizer](asan.md)
- [プリプロセッサマクロ](preprocessor.md)
- [C++23 を使えるようにする設定](settings.md)
