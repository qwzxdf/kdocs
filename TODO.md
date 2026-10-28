# kdocs TODO

docs の外（リポジトリ直下）に置いているので、サイトにはビルドされない。2026-10-28 に、全体を調べ直して書き直した。

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

### 2-1. 安全網

- [ ] 2-1-1. 検査スクリプトを作る: `.handoff/scripts/check_anchors.py`（ビルド結果の HTML のアンカー リンク切れ）と `check_docs.py`（docs の構成の検査）が、このチェックアウトに無く、CLAUDE.md の push 前の手順を実行できない。`tools/` に作り直し、CLAUDE.md の手順のパスも合わせる
- [ ] 2-1-2. 静的な検査を足す: 太字の `**` の残り、`TODO` の下書き、`int main` があるのに実行結果が続かないコード（今 47 か所）を、一覧にして報告するスクリプト

### 2-2. 検証で残った不一致

- [ ] 2-2-1. `design/patterns/event-plus.md` に `#include <cstddef>` を足す
- [ ] 2-2-2. `stl/utilities/chrono/local_days.md`・`wformat_string.md`・`stl/io/csignal.md`・`put_money.md` を、ビルドできるように直す
- [ ] 2-2-3. `stl/containers/multiset.md`（出力の行末の空白）、`engine/resource.md`（破棄の順序は実装で変わる、と書く）、`basics/file-io.md`（Windows は改行が 2 バイト、と書く）
- [ ] 2-2-4. 手元の MSVC が未対応の機能（`add_sat` 系・`saturate_cast`・`runtime_format`・`to_input`・`strided_slice`・`c8rtomb`・`mbrtoc8`・`is_virtual_base_of`・`elements_of`）を、GCC / Clang で確かめる（ユーザーの指示があったときだけ。Compiler Explorer を使う）
- 環境で出力が変わる（直さなくてよい）: `source_location`・`predefined-macros`（パス）、`vs/terms/platform`（アドレス）、`hexfloat`、`cerr`・`wcerr`・`wclog`（標準エラー）、`file_clock`、`create_symlink`

### 2-3. STL の残りを濃くする（`gcd.md` の濃さ。約 720 ページ）

書き方は `tools/` の生成の仕組みではなく、1 ページずつ具体的に書く（同じ文章が並ばないように）。1 項目の単位は、同じ話題のまとまり 10〜40 ページ。

- [ ] 2-3-1. `io/filesystem`（53）と `io/cstdio`（50）
- [ ] 2-3-2. `io` のルート（106）: ストリームの操作子、`cin`・`cout`・`endl`・`setw` など
- [ ] 2-3-3. `io/cwchar`（22）・`locale`（19）・`regex`（18）・`ctime`（15）
- [ ] 2-3-4. `utilities/chrono`（86）
- [ ] 2-3-5. `utilities/random`（39）
- [ ] 2-3-6. `utilities` のルート（98）: `tuple`・`pair`・`optional`・`function` まわり
- [ ] 2-3-7. `memory`（`cstring` 23、`new_delete` 22、`pmr` 10、ルート 25）
- [ ] 2-3-8. `concurrency`（72）
- [ ] 2-3-9. `containers`（63 のうち薄い 26）
- [ ] 2-3-10. `algorithms`（薄い 56。`views` と数値アルゴリズム）
- [ ] 2-3-11. `support/concepts`・`iterator` の残り: iterator のコンセプト（約 35）、iterator の細かい型
- [ ] 2-3-12. `support` の残り: `coroutine`（8）、`functional` の検索器・`function_ref`・`copyable_function`・placeholders、`type_traits` の `invoke_result` 系、`stacktrace`・`contract_violation`・`text_encoding`・`*_order_fallback`
- [ ] 2-3-13. `numeric` の残り: `cfloat`、`climits`、`complex`、`cstdint`、`numbers`、`ratio` の概要ページ、`cmath/atan2.md`・`lerp.md`・`sqrt.md`

### 2-4. 書いたページを読み直す

- [ ] 2-4-1. 生成スクリプトで書いたページを読み直し、同じ文章の所を、ページごとの具体的な話に差し替える: `cctype`、`cwctype`、`cstdint` の fast / least、`ratio` の接頭辞、`cmath` の特殊関数、`type_traits` の `is_xxx`、`functional` の演算子
- [ ] 2-4-2. 機械的に入れた「このページを読む前に」（約 690 ページ）を見直す: `graphics` 全体に入れた MVP 変換と GPU パイプラインが、本当に前提のページだけに絞る
- [ ] 2-4-3. 地の文の「非常に」を削った所（201 か所）で、読点だけ残った所を直す

### 2-5. 文体の一括整理

まず見本の 1 ページで試して OK をもらってから広げる（CLAUDE.md のルール）。

- [ ] 2-5-1. 読点: `python tools/fix_commas.py --survey` で密度を調べ、`--apply 6.0 --dry` で件数を見てから適用する（「に、」1827 か所、「が、」1828 か所、「を、」96 か所）
- [ ] 2-5-2. 太字: `tools/fix_bold.py`。太字の多いページ 29 ページ（`stl/containers/vector.md` 41 か所、`stl/utilities/hash.md` 37 か所、`stl/index.md` 34 か所 ほか）
- [ ] 2-5-3. 「必要があります」（256 か所）、「つまり」（66 か所）、「効率的」（12 か所）、「具体的には」（6 か所）を、文脈ごとに手で直す
- [ ] 2-5-4. 「このページでは〜／このページは〜」で始まる導入を、動機から入る書き方に直す（先頭にあるのは数ページ。多くは導入の最後の一文）
- [ ] 2-5-5. `TODO` の下書きが残るページを書く: `design/foundations/naming.md`、`design/practice/coding-style.md`、`libs/index.md`

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

### 2026-10-28 までの作業

- 追加: `vs/` に Git の基礎・SourceTree と GitHub Desktop・Git LFS・チーム開発・GitHub Actions・clang-tidy・単体テスト・RenderDoc と PIX・GPU デバッグ・Tracy・パッケージ管理・エラーメッセージの読み方。学習ロードマップ、よくある質問
- 追加: 描画の XeGTAO・ASSAO と CACAO・MSSAO、アップスケーラ（FSR・DLSS・XeSS）、Lumen と Nanite、ReSTIR
- 追加: `engine/` の入力・サウンド・ゲーム AI（ビヘイビア ツリー、経路探索）・ネットワーク、`libs/` の sol2・pybind11、`directx/` の DX11・DX12 ガイド、Vulkan 対応表、Slang と WebGPU
- 「このページを読む前に」を、抜けていた約 690 ページに追加
- 地の文の「非常に」を 152 ページから削除
- STL を `gcd.md` の濃さに書き直し: `numeric` のほぼ全部（cmath、bit、cctype、cwctype、cstdint、cstdlib、ratio、cfenv、cuchar、complex、拡張浮動小数点型）、`support` の type_traits・concepts・exceptions・比較（cmp・ordering・three_way）・ranges・エラーコード・型情報・iterator と functional の主要ページ
- 太字の削減（2026-10-23。STL 以外の約 510 ページ）
