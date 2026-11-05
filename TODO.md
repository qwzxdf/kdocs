# kdocs TODO

docs の外（リポジトリ直下）に置いているので、サイトにはビルドされない。2026-10-28 に、全体を調べ直して書き直した（2026-10-29 に C# 連携の項目を更新）。

## 0. `/todo` の使い方

`/todo` で、この TODO を実行する（`.claude/skills/todo/SKILL.md`）。

- `/todo` … 「2. 直す」の未完了（`- [ ]`）を上から 1 つ選び、実行する。1 つ終えるたびに、検証・commit・push・TODO の更新まで進めて、次へ続ける
- `/todo 2-3` … 項目の番号を指定して実行する（番号は「2. 直す」の `2-1`〜、「3. 追加したいページ」の `3-1-1`〜）
- `/todo io` … 名前に合う未完了の項目を実行する（`io`、`utilities`、`DX ガイド` など）
- `/todo list` … 未完了の項目を一覧するだけで、実行はしない

終わった項目は、`- [x]` にして、日付を書く。新しく見つけたやり残しは、該当する節に `- [ ]` で足す。

## 1. 全体レビュー（2026-10-28 時点）

2356 ページの統計を取り、今回の作業で書いたページ（約 700 ページ）を読み返した結果。実際の日本語記事との並べ読みや、Compiler Explorer での実行はしていない。

### 1-1. 規模と濃さ

本文の長さ（コードと表を除く）の中央値と、1300 字未満の薄いページの数。

| 場所 | ページ数 | 中央値 | 薄いページ |
| --- | --- | --- | --- |
| STL `support` | 412 | 1449 字 | 126 |
| STL `numeric` | 285 | 1609 字 | 31 |
| STL `io` | 283 | 980 字 | 236 |
| STL `utilities` | 222 | 1173 字 | 138 |
| STL `algorithms` | 140 | 1546 字 | 56 |
| STL `memory` | 80 | 1145 字 | 62 |
| STL `concurrency` | 72 | 1148 字 | 43 |
| STL `containers` | 63 | 1416 字 | 26 |
| `graphics` | 290 | 12487 字 | 1 |
| `3d`・`gamemath` | 39 | 12000〜15000 字 | 0 |
| `rendering`・`optimize` | 62 | 5400〜5800 字 | 0 |
| `directx`・`libs`・`csharp`・`vs`・`design`・`engine` ほか | 約 340 | 2900〜5200 字 | 7 |

- STL は 1560 ページで、サイト全体の約 3 分の 2。そのうち約 720 ページが 1300 字未満で、ここが一番の弱点。`io` と `utilities` が、まだ手つかず
- `numeric` は一通り書き直した。`support` も、type_traits・concepts・exceptions・比較・ranges・エラーコードを書き直した
- 書き直したページの本文は 1200〜2500 字。`gcd.md` の濃さには届くが、`vector.md`（約 15000 字）や `graphics` の水準には遠い

### 1-2. 今回の作業の品質で、気になる所

- **同じ型の文章が並ぶ。** 同じ種類のページ（`cctype`、`ratio` の接頭辞、`cstdint`、`type_traits` の `is_xxx`、`functional` の演算子）は、生成スクリプトで、同じ構成の文章を作った。1 ページずつ読むと自然だが、続けて読むと、言い回しが同じで、人が書いた感じが薄い。特に「ゲームでの使いどころ」が、型どおりのページがある
- **実行結果は、スクリプトで検証した（2026-10-28）。** 手元の Visual Studio 18（MSVC 14.51、`/std:c++latest`）で、サンプルをビルド・実行して「実行結果」と照合する `tools/verify_samples.py` を作った。今回の作業で変わった 1854 ページの 1362 サンプルのうち、1275 が一致、30 が標準以外のヘッダー等でスキップ、57 が不一致だった
    - 不一致のうち、自分のページの原因は 2 種類だけ。特殊関数 21 ページで出力の見出しを書き忘れた（数値は全部合っていた）。`is_error_code_enum` / `is_error_condition_enum` の期待値の取り違え。いずれも直して再検証済み
    - 検証で、元からあったページの間違いも見つかり、直した: `io/left.md`（`'|
'` の文字定数）、`algorithms/views/reverse.md`（`take(2)` の結果）、`algorithms/views/lazy_split.md`（`string(begin, end)` でビルドできない）、`utilities/random/ranlux48.md`（10000 回目の値が規格と違った）、`support/concepts/sortable.md`（ランダムアクセスは要求しない）
    - 使い方: `python tools/verify_samples.py docs/stl/numeric`、`--since <版>`（その版からの変更分）、`--jobs 8`（並列）。MSVC で確認できる範囲の照合で、GCC / Clang との差は見えない
- **「このページを読む前に」を機械的に入れた。** 約 690 ページに、フォルダーごとの対応表で前提ページを入れた。リンク先は実在するが、そのページに本当に必要な前提かは、1 ページずつ見ていない（例: `graphics` の全ページに、MVP 変換と GPU パイプラインを入れた）
- **「非常に」を地の文から削った。** 201 か所。「影が非常に、長く」→「影が、長く」のように、読点だけ残った所がある
- **検査スクリプトが無い。** CLAUDE.md が push 前に要求する `.handoff/scripts/check_anchors.py` と `check_docs.py` が、このチェックアウトに無く、一度も実行できていない。`mkdocs build --strict` だけで push している
- **ビルドが遅い。** 全体のビルドに 6〜60 分かかる（機械の状況で変わる）。ページを足すたびの確認が重い
- `k-cpperr/`（VS 拡張）を、誤って自分のコミットに含めた。その後、本人のコミットも載っているので、扱いは問題ないはずだが、確認はしていない

### 1-3. 文体の違和感・わかりにくさ（サイト全体）

- 「このページでは〜／このページは〜」を含むページが 427 ページ（436 か所）。多くは導入の最後の「このページは〜をまとめます」で、先頭にあるのは数ページだけ。一括の書き換えは見送った
- 「必要があります」256 か所（213 ページ）、「つまり」66 か所（58 ページ）、「効率的」12 か所、「具体的には」6 か所
- 読点: 「に、」が 1827 か所、「が、」が 1828 か所、「を、」が 96 か所。**読点を整える `tools/fix_commas.py` が既にある**（`--survey` で密度の一覧、`--apply 6.0` で直す）。まだ全体には適用していない
- 太字の多いページ 29 ページ（STL で 7 か所以上）。`stl/containers/vector.md` が 41 か所、`stl/utilities/hash.md` が 37 か所、`stl/index.md` が 34 か所。`tools/fix_bold.py` がある
- 実行結果が続かないコード: `int main` があるのに、直後に「実行結果」が無いコード ブロックが 47 か所
- `TODO` の下書きが残るページ: `design/foundations/naming.md`、`design/practice/coding-style.md`、`libs/index.md`

### 1-4. 良い点（維持する）

- `graphics`・`3d`・`gamemath` は、どのページも濃く、動く図もある。構成が一定
- `csharp/04-player.md`、`stl/containers/vector.md`、`graphics/terrain/lod/cdlod.md` の流れ（動機 → 例 → 構造、コード → すぐ解説）は、そのまま読み物として通る
- 新しく足した `vs/git.md`、`engine/ai/` などは、導入が動機から入っていて、見本のページに近い

## 2. 直す

番号の順が優先順位。**実行の決まり**: STL のページを書き直したら、`python tools/verify_samples.py <ファイル>` で照合してから `mkdocs build --strict` を通し、`main` に push する（CLAUDE.md の作業の進め方に従う）。

### 2-2. 検証で残った不一致

- 環境で出力が変わる（直さなくてよい）: `source_location`・`predefined-macros`（パス）、`vs/terms/platform`（アドレス）、`hexfloat`、`cerr`・`wcerr`・`wclog`（標準エラー）、`file_clock`、`create_symlink`

### 2-8. 表の規則への移行（CLAUDE.md の「表の規則」）

STL（`docs/stl/`）は対象外。STL 以外の表（約 3600 個）のうち、案内・比較・引く用の一覧（約 300 個）を除く約 3300 個（約 1000 ページ）を、番号つきリスト・文章・小見出し・コメントに直す。新しく書くページは、最初から守る。

- [ ] 2-8-1. 見本の 4 ページ（`graphics/shadows/contact-shadows.md`、`graphics/gi/ssgi.md`、`design/foundations/error-handling.md`）で、手順・長所短所・コストと限界・記号の説明を直した。この形で広げる
- [x] 2-8-2. （2026-11-04）`tools/check_docs.py` に、STL 以外の警告を足した（`--report` で一覧。現在 746 ページ。直したページから、エラーに切り替える）。残り: 体言止めが続く「ポイント」、案内の表で 1 列目にリンクがないもの
    - セルが 40 字を超える表（40 字は、セルの長さの分布を調べて決める）
    - 案内の表で、1 列目にリンクがない
    - 「説明」「理由」「手順」「長所」などの列がある表
    - 体言止めが続く「ポイント」
- [ ] 2-8-3. 手順・段階（約 90 個）と長所・短所（約 50 個）を、番号つきリストと 2 段落に直す（形が決まっているので、スクリプトで下書きして、1 ページずつ読んで直す）
    - `tools/tables_to_lists.py` で、2 列の「見出し語 | 長い文」の表を箇条書き・番号つきリストに機械変換できる。`graphics/` は 894 個（271 ページ）を変換済み（2026-11-04）。ほかのフォルダも変換済み（2026-11-04、1,022 個）。読点も STL 以外を一括で削減した。変換後は、1 項目ごとに段落へ深める作業（2-8-6）が残る
- [ ] 2-8-4. 「場面 | 書き方」（約 300 個）を、小見出しとコードの交互に直す。コードの記号の説明（「点 | 説明」「項目 | 内容」、約 380 個）を、コードのコメントに直す（各行に意味・単位・理由を書く。言い換えだけのコメントにしない。コードが断片しかないなら、動かせる形に直す）
- [ ] 2-8-5. フラグ・値・引数・メンバーの表（STL 以外、約 300 個）を、項目ごとの本文に直す。表は索引にとどめる（`libs/imgui/reference/flags.md` の 152 行など）
- [ ] 2-8-6. 説明が長いセルの表（「要素 | 内容」「設定 | 意味」「使いどころ | 説明」など、約 1800 個）を、項目ごとの段落に直す（「何をするか・なぜか・間違えるとどうなるか」を書く。表の文をつなぐだけにしない）。優先順位は `graphics` → `libs` → `optimize` → `directx` → `gamemath` → `rendering` → `design` → `vs` → `csharp` → `3d` → `encoding` → `basics`
- [ ] 2-8-7. 見出し的な表（1 列目があとの見出しと対応するもの、約 110 個）のうち、リンクがないもの（約 84 個）は、リンクを付けるか文章に直す。リンクには `{#id}` を使って、`check_anchors.py` で確かめる
- [ ] 2-8-8. `docs/_template.md` を、「STL は表、STL 以外は本文」の形に分けて書き直す

### 2-9. 全ページを見本の水準に寄せる（CLAUDE.md の「ページの質の基準」）

見本は `graphics/shadows/contact-shadows.md`（約 200 文、図 2 枚以上、コード 90 行前後、1 文あたりの読点 0.67）。全 2380 ページを一度には直せないので、指標で薄いページを見つけて、低い順に進める。**1 ページ終えたと言えるのは、次の「完了の条件」を全部満たしたとき。** 資料を読んで文章を書き直しただけでは、終わりにしない（2026-11-04 に、そのように終えた 4 ページが、見本に届いていなかった）。

完了の条件（1 ページごと）

- 表が、「表の規則」の 3 つ以外にない
- 解説するアルゴリズム・API に、通して読める完成形のコードが 100 行以上あり、全行に意味・単位・理由のコメントがある（式だけ、数行の断片の寄せ集めで終えていない）。資料にない処理は「足した」と書いてある。手元で確かめられるもの（`dxc`・`fxc`・C++ のコンパイル）は確かめてあり、確かめたかどうかをページに書いてある
- 図が 2 枚以上ある（配置・流れ・値の変化。文章と式だけで済ませていない）
- 資料の主要な節を 1 つずつ並べて、ページにあるかを確かめた。読んでいない範囲は、参考資料の節に書いてある
- 資料の数字・比較の言葉（「同程度」「速い」など）を、表の行ごとに照らした。単位の換算が資料にない所は、断定していない
- 同じ種類のページ（並ぶ手法）で繰り返される共通の概念は、親の `index.md` か比較ページに集めた
- 読点が 1 文あたり 0.7 以下（本文の読点の数 ÷ 句点の数。コードと SVG を除く）
- 文章量が見本の下限（約 200 文）に届いている。増やした分は、なぜ・数字・失敗の症状・境界・比較・過程・資料の抜けた節のどれかで、水増し（言い換え、中身のない文、要約の繰り返し）ではない
- 4 つの自己レビュー（コードの抜けとコメント、重複、規則違反、出典と主張の区別）をした。見本と並べて、量が極端に少なくない

- [x] 2-9-1. （2026-11-04）`tools/survey_depth.py` に統合した（`survey_graphics.py` は削除。`python tools/survey_depth.py docs/graphics 40`）。薄いページを見つける指標を作る（`tools/survey_depth.py` と `tools/survey_graphics.py` を統合）。完了の条件に対応させる: 図の数、コードの行数とコメント率、表の割合、1 文あたりの読点、文の数、参考文献の中身（著者・URL・ページ）。点数で並べる
- [x] 2-9-2. （2026-11-04、参考文献の中身の警告は未実装）`check_docs.py` に警告を足す: 1 文あたりの読点が 1 を超える、図が 0 枚の解説ページ、コードがあるのにコメントが少ない、参考文献に著者・URL・ページがない、同じ段落が 1 ページに 2 回ある、同じ節に並ぶページで同じ見出しが繰り返される
- [ ] 2-9-3. `graphics/`（約 320 ページ）を、指標の点数が低いものから 1 ページずつ、完了の条件を満たすまで直す。資料は実際に読む（PDF は pypdf で本文を取り出す）。必要なら、ページを増やしてよい
    - 手直し済み（2026-11-04）: `shadows/comparison.md`（19 文 → 約 100 文、図 2 枚、カスケードの分割・テクセル・メモリを出す C++ を MSVC で実行、HLSL を `fxc` で確認）、`gi/probes/compare.md`（24 文 → 約 100 文、図 2 枚、SH の誤差とメモリを確かめる C++ を MSVC で実行、HLSL を `fxc` で確認。旧版の「反射プローブ約 400 KB」は誤りで約 1 MiB だった）、`terrain/generation/timing.md`（24 文 → 約 100 文、図 2 枚、継ぎ目・侵食の余白・予算・キャッシュのキーを確かめる C++ を MSVC で実行）、`reflections/ssr-basics/artifacts.md`（30 文 → 約 100 文、図 2 枚、デバッグ表示つき SSR の HLSL を `fxc` で確認）、`postprocess/upscaling/` の index・comparison（新規）・xess・fsr・dlss、`ao/mssao.md`。図・コード・コメント・読点（1 文あたり 0.7 前後）・重複の整理・数字の照合は済み。**完了の条件に、まだ届いていない点**
        - 文章量: xess 128 文、fsr 123 文、dlss 190 文（目安 200）。図は xess・fsr・dlss が 1 枚ずつ（目安 2 枚以上）
        - 読んでいない資料: DLSS の 5 章以降、FSR 2 の README の後半（約 2.6 万字）、MSSAO の CGI 2011 版と VRST 版。読んで、足りない点（なぜ・数字・失敗の症状・境界）を足す
        - コードを豊富にする（完成形を 100 行以上）。FSR は、初期化 → 毎フレームのジッター・ディスパッチ → 終了まで通して書く。XeSS と DLSS も、コンテキスト作成から評価までを通して書く（API の引数は、資料で確かめられる範囲だけ。確かめられない所はダミーの名前にして注記する）。MSSAO の HLSL は、フィルター・16 点のポアソン ディスク・層を回す全体の流れ（Table 1）まで書き、`dxc` / `fxc` で通るかを確かめる
        - コンパイル確認: MSSAO の HLSL、DLSS・FSR・XeSS の呼び出し（HLSL は `dxc` / `fxc`、C++ は SDK のヘッダーがあるときだけ）
    - 手直し済み（2026-11-04）: `translucency/alpha-test/comparison.md`（7 文 → 132 文、図 2 枚、HLSL を `fxc` で確認）、`gi/rt-gi/choosing.md`（24 文 → 130 文、図 2 枚、C++ を MSVC `/W4` で確認）、`reflections/comparison.md`（20 文 → 約 120 文、図 2 枚、HLSL を `fxc` で確認）、`gi/restir.md`（33 文 → 176 文、図 3 枚、コース ノート（A Gentle Introduction to ReSTIR）を読んで書いた。C++ を MSVC で実行、HLSL を `fxc` で確認。ReSTIR GI・PT の論文は未読）、`gi/comparison.md`（35 文 → 約 120 文、図 2 枚、HLSL を `fxc` で確認。`reflections/comparison.md` の pow の警告も直した）、`translucency/oit/hybrid.md`（14 文 → 102 文、図 2 枚、C++ を MSVC `/W4` でコンパイルして実行）。次の候補（点数の低い順）: `reflections/ssr-basics/artifacts.md`、`gi/restir.md`、`ao/xegtao.md`、`ao/assao-cacao.md`、`gi/lumen.md`
- [x] 2-9-4. 描画の統合: `rendering/` を `graphics/` に移した（2026-11-03）。`graphics/pipeline/` と各分野の `cost.md`、`redirects.yml`、`hooks/redirects.py`。重複している内容の整理は 2-9-3 で進める
- [ ] 2-9-5. 見本の既知の不足: `ContactShadow` と `ContactShadowDda` の HLSL をコンパイルして確かめる。Bend Studio の公開コード（`code_final_candidate.zip`）を読んで、実装の詳細を足す（ダウンロードは、ユーザーの指示があったときだけ）
- [ ] 2-9-6. `graphics/` が進んだら、`libs/`・`engine/`・`3d/`・`directx/`・`optimize/` などを、同じ指標・同じ完了の条件で順に直す

## 3. 追加したいページ（残り）

優先度は ★ の数（★★★ が高い）。新規ページを足したときは `ratings.yml` と `autolinks.yml` も更新する。

### 3-1. 手順のページを濃くする

- [ ] 3-1-1. ★★★ DX11 / DX12 のガイド（`dx11/guide.md`、`dx12/guide.md`）は、今は**手順の道しるべ**。各段階の完全なコード（ウィンドウ → デバイス → 三角形 → 回る立方体）を、1 段階 1 ページで書く
- [ ] 3-1-2. ★★ Vulkan 対応表（`directx/vulkan-mapping.md`）に、同期（フェンス / セマフォ）の流れの図を足す
- [ ] 3-1-3. ★★ RenderDoc / PIX（`vs/renderdoc-pix.md`）に、画面の写真と、実際の手順の画像を足す

### 3-2. 描画

- [ ] 3-2-1. ★★ VBAO（出典を確かめてから。名前だけが先に出ていて、定義がはっきりしない）
- [ ] 3-2-2. ★★ アップスケーラ（`graphics/postprocess/upscaling/`）に、ジッターと動きベクトルの動く図
- [ ] 3-2-3. ★ Lumen / Nanite（`graphics/gi/lumen.md`）に、Surface Cache と仮想化ジオメトリの図

### 3-3. ゲームの分野

- [ ] 3-3-1. ★★ 入力・サウンド・AI・ネットワーク（`engine/` に追加済み）を、1 つの小さなゲームで通して使う実践ページにする
- [ ] 3-3-2. ★★ ビヘイビア ツリー（`engine/ai/behavior-tree.md`）に、動く図（Selector と Sequence の評価の流れ）
- [ ] 3-3-3. ★ `libs/sol2.md`・`libs/pybind11.md` に、導入手順の画面（vcpkg の `vcpkg.json` を置いた状態）
- [ ] 3-3-4. ★ Wwise・OpenAL の個別ページ（FMOD は 27 ページに出る）

### 3-4. 開発の道具

- [ ] 3-4-1. ★★ `vs/team.md` と `vs/github-actions.md` に、実際の PR の画面と、ワークフローの結果の画面
- [ ] 3-4-2. ★ Conan の個別ページ（`vs/package-managers.md` の比較から先）

### 3-5. 初心者向けの導線

- [ ] 3-5-1. ★★★ 用語集（`glossary.yml`）は 9 語を足したところ。主要な用語（Git・CI・RAII・SIMD・シェーダーなど）を、ページごとに拾って足す
- [ ] 3-5-2. ★★ 学習ロードマップ（`roadmap.md`）に、「作りたいもの別」の完全な読書リスト（2D ゲーム、3D ゲーム、ツール）
- [ ] 3-5-3. ★★ よくある質問（`faq.md`）に、「どちらを使う？」を 20 件まで増やす

## 4. 完了したこと（履歴）

### 2026-10-31 の作業

- 2-7: C# 連携の第 33〜50 章にタイトルの（新規）（変更）と章頭の表を足し、第 41・42・46 章に置き換えの注記を足し、第 50 章の `LogService` の差分を直し、第 52 章の表 10 個を文章に直した
- 2-5: 読点（13 ファイル）、`translucency/refraction/boundary.md`（約 40 文 → 114 文、図 4 枚、走査線の混入と飛びを数える C++ を MSVC で実行、HLSL を `fxc` で確認。Sousa の GPU Gems 2 第 19 章は Web 版の要点のみ確認）、`postprocess/antialiasing/comparison.md`（13 文 → 約 200 文、図 3 枚＋既存の動く図、SMAA 論文（Jimenez 他 2012）とサーベイ（Yang 他 2020）を全文読んで書いた。HLSL 3 本（辺検出・TAA 解像・T2x）を `fxc` で、C++ を MSVC `/W4` で実行して確認。FXAA・MSAA の原典は未読）、`ao/world-space/comparison.md`（13 文 → 約 150 文、図 5 枚、Wright(2015) のスライドと Crassin 他(2011) を全文読み、Ray Tracing Gems 第 25 章は AO の節だけ読んだ。DFAO・VXAO の HLSL を `fxc` で、RTAO の DXR を `dxc`（lib_6_3）で確認、円錐の歩数・メモリ・RTAO のノイズを出す C++ を MSVC で実行。論文の AO 時間と歩数の比が合うことを確認）、`reflections/rt-reflections/hit-shading.md`（25 文 → 約 110 文、図 4 枚、Ray Tracing Gems 第 20 章（レイ コーン。ray differentials の導出とコード付録は未読）と第 25 章（反射・AO の節）を読んで書いた。DXR の closest hit・miss・raygen 一式（約 300 行）を `dxc`（lib_6_3）で確認、球での反射の実測で β の式を確かめる C++ を MSVC で実行）、`pipeline/cases.md`（34 文 → 約 135 文、図 3 枚、3 事例を数えた C++ と HLSL（GPU カリング CS・クラスター CS／PS・半解像度の合成）を `fxc` で、D3D11 の間接描画コードを MSVC `/c` で確認。論文は引かない実践ページ。旧版の「20 M ピクセル」は 13.8 M の誤りだったので直した）、`atmosphere/god-rays/volume.md`（18 文 → 約 120 文、図 4 枚、Wronski(2014) のスライドとノート 67 枚を全部読んで書いた（図・付録コードは未読、Hillaire 2015 は取得できず未読）。ESM 縮小・注入・積分・適用の HLSL（約 240 行）を `fxc` で、細い筋の推定誤差を調べる C++ を MSVC で実行）、`reflections/rt-reflections/denoise.md`（34 文 → 約 170 文、図 3 枚、SVGF(Schied 他 2017) を全文、Ray Tracing Gems 第 25 章の反射の節を読んで書いた。時間蓄積・反射の再投影・空間再構成・à-trous の HLSL（約 360 行）を `fxc` で、1 次元の à-trous で「ノイズと段差の取引」を測る C++ を MSVC で実行。旧版の重複した節を削除）、`atmosphere/scattering/bruneton.md`（27 文 → 約 180 文、図 4 枚、Bruneton & Neyret(2008) を全文、2017 年の参照実装の文書を前半読んで書いた。透過率・単散乱・4D→3D の座標・空と空気遠近法の HLSL（約 340 行）を `fxc` で確認、µ の写し替えと夕焼けの透過率を数える C++ を MSVC で実行。旧版の「256×128×32」は論文の 32×128×256 と違う記述だったので直した）、`atmosphere/sky-models/day-night.md`（16 文 → 約 150 文、図 2 枚＋既存の動く図、Hillaire(2020) を大半、Lagarde 他(2014) の太陽の節と表 11 を読んで書いた。時刻→太陽・月・環境光・露出の HLSL（約 100 行）を `fxc` で確認、太陽の位置・薄明・照度・EV・透過率の近似を確かめる C++ を MSVC で実行。照度の桁は Wikipedia の表（一次資料ではない））、太字（12 ページ）、定型句（「効率的」など 25 か所と、「必要があります」47 か所）、「このページでは」で始まる導入 2 ページを整えた
- 2-4-2: `graphics` の 282 ページの「このページを読む前に」から、本文で使っていない MVP 変換と GPU パイプラインのリンクを外した
- 2-4-1: `type_traits`・`functional` の演算子・`cmath` の特殊関数・`ratio` の接頭辞・`cctype`・`cwctype` の約 160 ページで、同じ文章の所を、ページごとの具体的な話に差し替えた
- STL `numeric` の `cfloat`・`climits`・`complex`・`cstdint`・`numbers`・`ratio`・`cmath` の 3 ページを書き直して 2-3-13 を完了
- STL `support` の `coroutine`・`functional`・`type_traits`・`stacktrace`・`*_order_fallback` など 31 ページを書き直して 2-3-12 を完了
- STL `support/concepts` の 30 ページと `support/iterator` の 15 ページを書き直して 2-3-11 を完了
- STL `algorithms` の 38 ページを書き直して 2-3-10 を完了
- STL `containers` の 27 ページを書き直して 2-3-9 を完了
- STL `concurrency` の 45 ページを書き直して 2-3-8 を完了
- STL `memory` の 66 ページを書き直して 2-3-7 を完了
- STL `utilities` のルート約 55 ページを書き直して 2-3-6 を完了
- STL `random` のエンジン系 9 ページを書き直して 2-3-5 を完了
- STL `chrono` の 69 ページを書き直して 2-3-4 を完了
- STL `ctime`・`cwchar`・`locale`・`regex` の 74 ページを書き直して 2-3-3 を完了
- STL `io` のルートを書き直して 2-3-2 を完了: `cin`・`cout`、`cstdarg` と `va_*`、`setjmp` 系、`basic_*stream`・`iostream`、`basic_streambuf`・`filebuf`・`stringbuf`・`spanbuf`・`syncbuf`

### 2026-10-29 の作業

- C# 連携の第 5〜29 章、第 39・40・50 章を、Editor を育てる形に見直し（第 12〜15 章でシーン ツリー、プロパティ、アセット、ログを作り、第 16 章で Prism に載せ替え、第 22〜23 章でモジュールと選択の伝達）。第 17〜21 章の DI の例を、Editor のクラスにした
- 第 23〜29 章の Editor のコードを、別のプロジェクトで組んでビルドし、起動まで確かめた。ビルドで見つかった `using System.IO;` などの漏れを直した
- 第 52 章の章番号の表を直した。ログの `Level` を `LogLevel`（列挙型）に統一した
- C# 連携の Prism を前に出した。新しい第 12 章を「Prism の導入と起動」にして、旧第 12〜15 章を第 13〜16 章に繰り下げた（旧第 16 章は第 12 章に書き直した）。第 13 章以降は `BindableBase` / `DelegateCommand` で書き、自作の `ViewModelBase` / `RelayCommand` は廃止。第 14 章の検証は最初から `ErrorsContainer`。DI の使い方（登録とコンストラクターで受け取る）は第 16 章に移し、第 17〜21 章はその理屈の章にした。`MainWindow` と `MainWindowViewModel` は `Editor/` 直下に置く
- C# 連携に第 13 章「見た目のテーマを入れる」（Fluent の `ThemeMode`、WPF-UI）を新しく足し、旧第 13〜52 章を第 14〜53 章に繰り下げた（ファイル名・参照・glossary・.pages も一括で直した）。`AssetViewModel` と `LogViewModel` は第 15（新 16）章から `Modules/` に置く形にし、第 43（新 44）章の Undo 用 `CompositeCommand` を `MacroCommand` に改名した
- `make-anim` スキル、`tools/csharp_intro.py`、`kdocs-graphics-update.patch` を追加（未追跡だったもの）

### 2026-10-28 までの作業

- 追加: C# 連携に第 17〜21 章（DI とは何か、Prism の起動順、登録と寿命、ViewModelLocator、DI コンテナーの種類）。旧第 17 章以降は 5 つ繰り下げ（旧第 17〜47 章 → 第 22〜52 章。相互参照も直し済み）。第 22・24 章は Prism 9.0.537 で動かして直した第 5 章に `=>` と命名規則（`_` の理由）を追加。起動順・遅延生成・`new MainWindow()` の挙動は Prism 9.0.537 で実行して確かめた
- 追加: `vs/` に Git の基礎・SourceTree と GitHub Desktop・Git LFS・チーム開発・GitHub Actions・clang-tidy・単体テスト・RenderDoc と PIX・GPU デバッグ・Tracy・パッケージ管理・エラーメッセージの読み方。学習ロードマップ、よくある質問
- 追加: 描画の XeGTAO・ASSAO と CACAO・MSSAO、アップスケーラ（FSR・DLSS・XeSS）、Lumen と Nanite、ReSTIR
- 追加: `engine/` の入力・サウンド・ゲーム AI（ビヘイビア ツリー、経路探索）・ネットワーク、`libs/` の sol2・pybind11、`directx/` の DX11・DX12 ガイド、Vulkan 対応表、Slang と WebGPU
- 「このページを読む前に」を、抜けていた約 690 ページに追加
- 地の文の「非常に」を 152 ページから削除
- STL を `gcd.md` の濃さに書き直し: `numeric` のほぼ全部（cmath、bit、cctype、cwctype、cstdint、cstdlib、ratio、cfenv、cuchar、complex、拡張浮動小数点型）、`support` の type_traits・concepts・exceptions・比較（cmp・ordering・three_way）・ranges・エラーコード・型情報・iterator と functional の主要ページ
- 太字の削減（2026-10-23。STL 以外の約 510 ページ）
