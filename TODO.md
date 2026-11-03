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

- [ ] 2-2-4. 手元の MSVC が未対応の機能（`add_sat` 系・`saturate_cast`・`runtime_format`・`to_input`・`strided_slice`・`c8rtomb`・`mbrtoc8`・`is_virtual_base_of`・`elements_of`）を、GCC / Clang で確かめる（ユーザーの指示があったときだけ。Compiler Explorer を使う）
- 環境で出力が変わる（直さなくてよい）: `source_location`・`predefined-macros`（パス）、`vs/terms/platform`（アドレス）、`hexfloat`、`cerr`・`wcerr`・`wclog`（標準エラー）、`file_clock`、`create_symlink`

### 2-8. 表の規則への移行（CLAUDE.md の「表の規則」）

STL（`docs/stl/`）は対象外。STL 以外の表（約 3600 個）のうち、案内・比較・引く用の一覧（約 300 個）を除く約 3300 個（約 1000 ページ）を、番号つきリスト・文章・小見出し・コメントに直す。新しく書くページは、最初から守る。

- [ ] 2-8-1. 見本の 4 ページ（`graphics/shadows/contact-shadows.md`、`graphics/gi/ssgi.md`、`design/foundations/error-handling.md`）で、手順・長所短所・コストと限界・記号の説明を直した。この形で広げる
- [ ] 2-8-2. `tools/check_docs.py` に、STL 以外の警告を足す（最初は警告。直したページから、エラーに切り替える）
    - セルが 40 字を超える表（40 字は、セルの長さの分布を調べて決める）
    - 案内の表で、1 列目にリンクがない
    - 「説明」「理由」「手順」「長所」などの列がある表
    - 体言止めが続く「ポイント」
- [ ] 2-8-3. 手順・段階（約 90 個）と長所・短所（約 50 個）を、番号つきリストと 2 段落に直す（形が決まっているので、スクリプトで下書きして、1 ページずつ読んで直す）
    - `tools/tables_to_lists.py` で、2 列の「見出し語 | 長い文」の表を箇条書き・番号つきリストに機械変換できる。`graphics/` は 894 個（271 ページ）を変換済み（2026-11-04）。ほかのフォルダは未実行。変換後は、1 項目ごとに段落へ深める作業（2-8-6）が残る
- [ ] 2-8-4. 「場面 | 書き方」（約 300 個）を、小見出しとコードの交互に直す。コードの記号の説明（「点 | 説明」「項目 | 内容」、約 380 個）を、コードのコメントに直す
- [ ] 2-8-5. フラグ・値・引数・メンバーの表（STL 以外、約 300 個）を、項目ごとの本文に直す。表は索引にとどめる（`libs/imgui/reference/flags.md` の 152 行など）
- [ ] 2-8-6. 説明が長いセルの表（「要素 | 内容」「設定 | 意味」「使いどころ | 説明」など、約 1800 個）を、項目ごとの段落に直す。優先順位は `graphics` → `libs` → `optimize` → `directx` → `gamemath` → `rendering` → `design` → `vs` → `csharp` → `3d` → `encoding` → `basics`
- [ ] 2-8-7. 見出し的な表（1 列目があとの見出しと対応するもの、約 110 個）のうち、リンクがないもの（約 84 個）は、リンクを付けるか文章に直す。リンクには `{#id}` を使って、`check_anchors.py` で確かめる
- [ ] 2-8-8. `docs/_template.md` を、「STL は表、STL 以外は本文」の形に分けて書き直す

### 2-9. 全ページを見本の水準に寄せる（CLAUDE.md の「ページの質の基準」）

見本は `graphics/shadows/contact-shadows.md`。全 2380 ページを一度には直せないので、指標で薄いページを見つけて、低い順に進める。1 ページごとに、CLAUDE.md の 10 項目（表・コメント・資料との照合・資料の扱い・コードの抜け・重複・書き方・参考文献・読点・自己レビュー）を適用する。

- [ ] 2-9-1. 薄いページを見つける指標を作る（`tools/survey_depth.py` を拡張）。参考文献が名前だけ、文章量が少ない、表の割合が高い、コードのコメントが少ない、読点の密度が高いページを、点数で並べる
- [ ] 2-9-2. `check_docs.py` に警告を足す: 参考文献に著者・URL・ページがない、同じ段落が 1 ページに 2 回ある、読点の密度が高い
- [ ] 2-9-3. `graphics/`（約 320 ページ）を、`python tools/survey_graphics.py` の点数が低いものから 1 ページずつ、質の基準 10 項目で直す（資料を実際に読む。PDF は pypdf で本文を取り出す）。必要なら、ページを増やしてよい
    - 済み（2026-11-04）: `postprocess/upscaling/xess.md`、`fsr.md`、`dlss.md`、`ao/mssao.md`。表の機械変換は 2 列の説明表だけ済み
    - 次の候補（点数の低い順）: `shadows/vsm/comparison.md`、`translucency/alpha-test/comparison.md`、`gi/probes/compare.md`、`reflections/ssr-basics/artifacts.md`、`postprocess/upscaling/index.md`、`gi/restir.md`、`ao/xegtao.md`、`ao/assao-cacao.md`、`gi/lumen.md
- [x] 2-9-4. 描画の統合: `rendering/` を `graphics/` に移した（2026-11-03）。`graphics/pipeline/` と各分野の `cost.md`、`redirects.yml`、`hooks/redirects.py`。重複している内容の整理は 2-9-3 で進める
- [ ] 2-9-7. 済みの 4 ページ（`upscaling/xess.md`、`fsr.md`、`dlss.md`、`ao/mssao.md`）を、見本の水準に直す（2026-11-04 のレビューより）
    - 読点を減らす（1 文あたり 1.1〜1.7 → 0.7 以下）
    - 図を足す。MSSAO は、入れ子の半球と層の合成の流れ。アップスケーラ 3 つは、ジッターの位相が画素を埋める様子と、フレームの中での呼び出しの位置
    - コードを足す。MSSAO は、AOnear・バイラテラル アップサンプル・最大値と平均の合成を、丁寧なコメントつきの HLSL で。FSR はジッターと初期化の流れ。コンパイルしていないと明記する
    - 重複を整理する。ジッター・ミップ バイアス・入力・露出の共通部分を `upscaling/index.md` に集め、3 社の値を比べる「Upscaler Comparison」ページを作る
    - MSSAO の実行時間の文を、論文の表 8 に合わせる（8600M GT は Sibenik・Conference で同程度、Sponza で MSSAO が速い）。DLSS のジッターのコードに、単位の換算がガイドに書かれていない旨を注記する。MSSAO の「使いどころ」は、SAO・XeGTAO の資料を読んで確かめるか、削る
    - DLSS の 5 章以降、FSR 2 の README の後半を読んで、足りない点を足す
- [ ] 2-9-5. 見本の既知の不足: `ContactShadow` と `ContactShadowDda` の HLSL をコンパイルして確かめる。Bend Studio の公開コード（`code_final_candidate.zip`）を読んで、実装の詳細を足す（ダウンロードは、ユーザーの指示があったときだけ）
- [ ] 2-9-6. `graphics/` が進んだら、`libs/`・`engine/`・`3d/`・`directx/`・`optimize/` などを、同じ指標で順に直す

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
- 2-5: 読点（13 ファイル）、太字（12 ページ）、定型句（「効率的」など 25 か所と、「必要があります」47 か所）、「このページでは」で始まる導入 2 ページを整えた
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
