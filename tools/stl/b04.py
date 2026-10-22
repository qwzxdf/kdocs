"""バッチ 4: <chrono> の未登録分。"""
from mk import *  # noqa: F401,F403

CH = "utilities/chrono/"
HUB = "utilities/chrono.md"
INFO = "[`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。"
V20 = ("20", "C++20")
PRE = "#include <chrono>\n#include <print>\n"


def C(stem, summary, intro, tips, sig, args, ret, code, out, game, miss, sim, memo, rank="rare", ver=V20, cx="定数", cr=None, compiler=None, rjn=None, hub=True, extra_inc=""):
    P(CH + stem + ".md", "std::chrono::" + stem, summary, rank, "chrono", intro, tips, game, miss, sim, memo,
      sig=sig, args=args, ret=ret, cx=cx, code=code, out=out, ver=ver, info=INFO, hub=HUB if hub else None, hubname="std::chrono",
      rj=f"chrono/{rjn or stem}.html", cr=f"chrono/{cr or stem}", compiler=compiler)


# ---- 時計
for nm, what, intro, note in [
    ("utc_clock", "うるう秒を数に入れた、協定世界時（UTC）の時計。", "`system_clock` は、うるう秒を無視して「1 日は必ず 86400 秒」と数えます。実際の経過秒を正しく数えたいときは、うるう秒を含めて数える `utc_clock` を使います。", "`system_clock` との違いは、うるう秒を数えるかどうか。"),
    ("tai_clock", "うるう秒を含まず、連続して進む国際原子時（TAI）の時計。", "うるう秒で時刻が飛ぶと、経過時間の計算がずれます。`tai_clock` は、原子時計の秒をそのまま数える時計で、飛ばずに一定の速さで進みます。", "UTC より 37 秒進んでいる（2017 年以降。1972 年の時点で 10 秒の差）。"),
    ("gps_clock", "GPS の時刻に合わせた時計。", "GPS 衛星が配る時刻は、1980 年 1 月 6 日を基準にして、うるう秒を入れずに進みます。`gps_clock` は、この GPS 時刻を表す時計です。", "TAI より 19 秒遅れている。")]:
    C(nm, what, intro, [note, "`now()` で今の時点を取る。", "`is_steady` は `false`（時計の補正が入りうる）。"],
      f"class {nm} {{\n public:\n  using rep = /* 実装定義 */;\n  using period = ratio<1>;\n  using duration = chrono::duration<rep, period>;\n  using time_point = chrono::time_point<{nm}>;\n  static constexpr bool is_steady = false;\n  static time_point now();\n}};",
      [], "`now()` は今の `time_point`", PRE + f"""
int main() {{
  std::println("{{}}", std::chrono::{nm}::is_steady);
}}""", "false",
      [("うるう秒も含む厳密な経過時間", "`utc_clock` / `tai_clock` の時点を引き算する")],
      ("`system_clock` と取り違える", "1 日の長さの扱いが違います。普通のゲームのタイムスタンプには [`system_clock`](system_clock.md) で十分です。"),
      [("[`system_clock`](system_clock.md)", "うるう秒を無視する普通の時計"), ("[`clock_cast`](clock_cast.md)", "時計どうしを変換する")],
      [what.rstrip("。"), "`is_steady` は false", "普段は system_clock / steady_clock でよい"], cx="`now()` は定数", cr=nm,
      compiler="C++20 の機能です。GCC 13 以降で使えます。MSVC は 19.29 以降。")

C("clock_cast", "時計どうしの時点を、別の時計の時点に変換する。",
  "`system_clock` の時点を `utc_clock` や `file_clock` に直したいことがあります（たとえばファイルの更新時刻をカレンダー時刻に）。`clock_cast<DestClock>(tp)` は、時計の種類が違う `time_point` を目的の時計に変換します。",
  ["変換元と先の組み合わせは、`sys_clock`・`utc_clock`・`tai_clock`・`gps_clock`・`file_clock` の間なら動く。", "戻り値は目的の時計の `time_point`。"],
  "template <class DestClock, class SourceClock, class Duration>\nauto clock_cast(const time_point<SourceClock, Duration>& t);",
  [("DestClock", "テンプレート引数", "変換先の時計"), ("t", "time_point", "変換元の時点")], "変換先の時計の `time_point`",
  PRE + """
int main() {
  using namespace std::chrono;
  auto sys = sys_days{2024y / January / 1};
  auto tai = clock_cast<tai_clock>(sys);
  auto back = clock_cast<system_clock>(tai);
  std::println("{}", back == sys);
}""", "true",
  [("ファイルの更新時刻をカレンダー時刻にする", "`clock_cast<system_clock>(fs::last_write_time(p))`")],
  ("変換できない時計を指定する", "`steady_clock` のように壁時計と結びつかない時計は変換できません。"),
  [("[`file_clock`](file_clock.md)", "ファイルの時計"), ("[`system_clock`](system_clock.md)", "カレンダー時刻")],
  ["時計の種類が違う time_point を変換", "steady_clock は対象外", "ファイル時刻の変換で役立つ"], cr="clock_cast")

# ---- duration の別名
for nm, unit, rep, period, ratio_txt, ex, res, ver in [
    ("nanoseconds", "ナノ秒（10 億分の 1 秒）", "整数（64 ビット以上）", "nano", "1/1,000,000,000 秒", "std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::microseconds{3}).count()", "3000", None),
    ("microseconds", "マイクロ秒（100 万分の 1 秒）", "整数（55 ビット以上）", "micro", "1/1,000,000 秒", "std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::milliseconds{2}).count()", "2000", None),
    ("milliseconds", "ミリ秒（1000 分の 1 秒）", "整数（45 ビット以上）", "milli", "1/1000 秒", "std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::seconds{2}).count()", "2000", None),
    ("seconds", "秒", "整数（35 ビット以上）", "ratio<1>", "1 秒", "std::chrono::duration_cast<std::chrono::seconds>(std::chrono::milliseconds{2500}).count()", "2", None),
    ("minutes", "分", "整数（29 ビット以上）", "ratio<60>", "60 秒", "std::chrono::duration_cast<std::chrono::minutes>(std::chrono::seconds{150}).count()", "2", None),
    ("hours", "時間", "整数（23 ビット以上）", "ratio<3600>", "3600 秒", "std::chrono::duration_cast<std::chrono::hours>(std::chrono::minutes{150}).count()", "2", None),
    ("days", "日", "整数（25 ビット以上）", "ratio<86400>", "86,400 秒（24 時間）", "std::chrono::duration_cast<std::chrono::days>(std::chrono::hours{50}).count()", "2", V20),
    ("weeks", "週", "整数（22 ビット以上）", "ratio<604800>", "604,800 秒（7 日）", "std::chrono::duration_cast<std::chrono::days>(std::chrono::weeks{2}).count()", "14", V20),
    ("months", "月（平均の長さ）", "整数（20 ビット以上）", "ratio<2629746>", "2,629,746 秒（約 30.44 日）", "std::chrono::duration_cast<std::chrono::days>(std::chrono::months{1}).count()", "30", V20),
    ("years", "年（平均の長さ）", "整数（17 ビット以上）", "ratio<31556952>", "31,556,952 秒（約 365.2425 日）", "std::chrono::duration_cast<std::chrono::days>(std::chrono::years{1}).count()", "365", V20)]:
    C(nm, f"{unit}を数える duration の別名。",
      f"時間の長さを扱うとき、`duration<long long, std::ratio<1, 1000>>` のような書き方は長すぎます。標準は、よく使う単位に名前をつけています。`std::chrono::{nm}` は、{unit}を数える `duration` の別名です。",
      [f"1 つぶんの長さは {ratio_txt}。", "`count()` で数を取り出し、`duration_cast` で別の単位に変える。", f"リテラルでも書ける（[リテラル](literals.md) を参照）。"],
      f"using {nm} = duration</* {rep} */, {period if period.startswith('ratio') else 'std::' + period}>;",
      [], f"`{nm}{{n}}` は {unit}を n 個ぶん持つ duration",
      PRE + f"""
int main() {{
  std::println("{{}}", {ex});
}}""", res,
      [("フレーム時間の計測" if nm in ("milliseconds", "microseconds", "nanoseconds") else "経過時間の指定", f"`std::chrono::{nm}{{値}}`")],
      ("整数に切り捨てられる", "整数の `duration` に `duration_cast` で大きい単位へ直すと、小数点以下は切り捨てられます。小数で受けたいなら `duration<double>` を使います。"),
      [("[`duration`](duration.md)", "時間の長さの型"), ("[`duration_cast`](duration_cast.md)", "単位を変換する"), ("[`literals`](literals.md)", "`ms` / `s` などの書き方")],
      [f"{unit}を数える duration の別名", "`count()` で数を取り出す", "単位の変換は duration_cast"], rank="sometimes" if nm in ("milliseconds", "seconds") else "rare",
      ver=ver, cr="duration", rjn="duration", compiler="C++11 から使えます。" if ver is None else "C++20 から使えます。")

# ---- time_point_cast ほか
C("time_point_cast", "time_point の単位を、別の単位に変換する（切り捨て）。",
  "`time_point` の中の `duration` の単位を変えたいことがあります。たとえばミリ秒の時点を秒の時点にするときです。`time_point_cast<ToDuration>(tp)` が、単位を変えた `time_point` を作ります。",
  ["`duration_cast` の `time_point` 版。", "デフォルトでは 0 方向への切り捨て。", "丸めたいときは `floor` / `ceil` / `round`。"],
  "template <class ToDuration, class Clock, class Duration>\nconstexpr time_point<Clock, ToDuration> time_point_cast(const time_point<Clock, Duration>& t);",
  [("ToDuration", "テンプレート引数", "変換後の `duration`"), ("t", "time_point", "変換する時点")], "単位を変えた `time_point`",
  PRE + """
int main() {
  using namespace std::chrono;
  system_clock::time_point tp{milliseconds{1500}};
  auto s = time_point_cast<seconds>(tp);
  std::println("{}", s.time_since_epoch().count());
}""", "1",
  [("ミリ秒の時刻を秒の精度に落とす", "`time_point_cast<seconds>(tp)`")],
  ("負の時刻の丸め", "切り捨ては 0 方向です。負の時刻では「小さいほう」にはなりません。小さいほうへ丸めるなら `floor` を使います。"),
  [("[`duration_cast`](duration_cast.md)", "duration の変換"), ("[`floor`](floor.md)", "小さいほうへ丸める")],
  ["time_point の単位を変える", "0 方向へ切り捨て", "丸め方を選ぶなら floor / ceil / round"], cr="time_point_cast")

C("treat_as_floating_point", "duration の中身（rep）を、小数として扱うかの特性。",
  "`duration` の `rep` が整数か小数かで、変換の可否が変わります（整数への暗黙変換は精度が落ちるので禁止）。この判定に使うのが `treat_as_floating_point` で、`rep` が小数型なら `true` です。",
  ["`double` や `float` は `true`、`int` は `false`。", "自作の数値型を `rep` にするとき、特殊化して知らせる。", "`_v` 版で bool が取れる。"],
  "template <class Rep>\nstruct treat_as_floating_point : is_floating_point<Rep> {};\ntemplate <class Rep>\ninline constexpr bool treat_as_floating_point_v = treat_as_floating_point<Rep>::value;",
  [("Rep", "型", "調べる型")], "小数として扱うなら `true`",
  PRE + """
int main() {
  std::println("{}", std::chrono::treat_as_floating_point_v<double>);
  std::println("{}", std::chrono::treat_as_floating_point_v<int>);
}""", "true\nfalse",
  [("自作の固定小数点型を duration の rep に使う", "`treat_as_floating_point` を特殊化する")],
  ("整数 rep に暗黙変換を期待する", "小さい単位から大きい単位への変換は、整数 `rep` では暗黙にはできません。`duration_cast` を使います。"),
  [("[`duration_values`](duration_values.md)", "rep の 0・最大・最小"), ("[`duration`](duration.md)", "時間の長さ")],
  ["rep が小数かの特性", "double / float は true", "自作 rep では特殊化する"], cx="コンパイル時のみ", cr="treat_as_floating_point", ver=("11", "C++11"))

C("duration_values", "duration の rep について、0・最小・最大を返す。",
  "`duration::zero()`、`min()`、`max()` の中身は、`rep` 型の 0・最小・最大です。それを決めているのが `duration_values<Rep>` で、自作の数値型を `rep` にするときに、特殊化して値を教えます。",
  ["`zero()` / `min()` / `max()` の 3 つの静的関数をもつ。", "普通は直接使わず、`duration::zero()` などを使う。"],
  "template <class Rep>\nstruct duration_values {\n  static constexpr Rep zero() noexcept;\n  static constexpr Rep min() noexcept;\n  static constexpr Rep max() noexcept;\n};",
  [("Rep", "型", "対象の数値型")], "`rep` の 0・最小・最大",
  PRE + """
int main() {
  using V = std::chrono::duration_values<int>;
  std::println("{} {}", V::zero(), V::max());
}""", "0 2147483647",
  [("自作の数値型を duration の rep にする", "`duration_values<MyNum>` を特殊化する")],
  ("min() を 0 に近い値だと思う", "`min()` は**最小の（最も小さい）値**で、0 に近い正の値ではありません。整数なら負の最小値です。"),
  [("[`duration`](duration.md)", "時間の長さ"), ("[`treat_as_floating_point`](treat_as_floating_point.md)", "rep が小数かの特性")],
  ["rep の 0・最小・最大", "duration::zero() などの元", "自作 rep では特殊化"], cx="定数", cr="duration_values", ver=("11", "C++11"))

# ---- カレンダー部品
C("day", "月の中の日（1〜31）を表す型。",
  "日付の「日」の部分だけを、1〜31 の範囲で型安全に持ちたいことがあります。`std::chrono::day` は、その専用の型で、`int` のように範囲外の値を気づかないまま持ち歩きません。`ok()` で範囲内かを確かめられます。",
  ["`day{15}` のように作る。`unsigned` に変換して値を取り出す。", "`ok()` で 1〜31 の範囲か調べる（月ごとの日数は見ない）。", "`year/month/day` の形で日付にまとめられる。"],
  "class day {\n public:\n  constexpr explicit day(unsigned d) noexcept;\n  constexpr explicit operator unsigned() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("d", "unsigned", "日（1〜31 が有効）")], "`ok()` は 1〜31 なら `true`",
  PRE + """
int main() {
  std::chrono::day d{15};
  std::println("{} {}", unsigned(d), d.ok());
  std::println("{}", std::chrono::day{32}.ok());
}""", "15 true\nfalse",
  [("ユーザー入力の日付チェック", "`std::chrono::day{n}.ok()`")],
  ("月ごとの日数まで確かめた気になる", "`day{31}.ok()` は常に `true` です。2 月 31 日かどうかは [`year_month_day`](year_month_day.md) の `ok()` で確かめます。"),
  [("[`month`](month.md)", "月"), ("[`year_month_day`](year_month_day.md)", "年月日"), ("[`month_day`](month_day.md)", "月と日")],
  ["日（1〜31）の型", "ok() で範囲確認", "年月日は year_month_day"], cr="day")

C("month", "月（1〜12）を表す型。",
  "月を `int` で持つと、`13` のような範囲外の値や、`0` から数えるのか `1` から数えるのかの混乱が起こります。`std::chrono::month` は、1〜12 の月を型で表し、`January` ... `December` の定数も用意されています。",
  ["`month{3}` または `std::chrono::March` で作る。", "`month + months{n}` で、12 を超えると 1 に戻る（巡回する）。", "`ok()` で 1〜12 の範囲か調べる。"],
  "class month {\n public:\n  constexpr explicit month(unsigned m) noexcept;\n  constexpr explicit operator unsigned() const noexcept;\n  constexpr bool ok() const noexcept;\n};\ninline constexpr month January{1}, February{2} /* ... */, December{12};",
  [("m", "unsigned", "月（1〜12 が有効）")], "`ok()` は 1〜12 なら `true`",
  PRE + """
int main() {
  using namespace std::chrono;
  std::println("{}", unsigned(March));
  std::println("{}", unsigned(March + months{11}));
  std::println("{}", month{13}.ok());
}""", "3\n2\nfalse",
  [("シーズンイベントの月の判定", "`month == std::chrono::December`")],
  ("0 始まりだと思う", "`month` は 1 始まりです（`January` は 1）。配列の添字に使うときは `unsigned(m) - 1` にします。"),
  [("[`day`](day.md)", "日"), ("[`year`](year.md)", "年"), ("[`year_month`](year_month.md)", "年と月")],
  ["月（1〜12）の型", "定数 January … December", "足し算は巡回する"], cr="month")

C("year", "年を表す型。",
  "年を `int` で持つと、うるう年の判定を自分で書くことになります。`std::chrono::year` は、年を型で表し、`is_leap()` でうるう年かを教えてくれます。",
  ["`year{2024}` や `2024y` で作る。", "`is_leap()` でうるう年かを調べる。", "`int` に変換して値を取り出す。"],
  "class year {\n public:\n  constexpr explicit year(int y) noexcept;\n  constexpr explicit operator int() const noexcept;\n  constexpr bool is_leap() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("y", "int", "年（負の年も使える）")], "`is_leap()` はうるう年なら `true`",
  PRE + """
int main() {
  using namespace std::chrono;
  std::println("{} {}", int(2024y), 2024y.is_leap());
  std::println("{}", 2023y.is_leap());
}""", "2024 true\nfalse",
  [("セーブデータの日付の検証", "`year{y}.ok()`")],
  ("`2024` と `2024y` を取り違える", "`2024y` は `year` 型のリテラル（`using namespace std::chrono_literals` か `std::literals` が必要）です。単なる `2024` は `int` です。"),
  [("[`month`](month.md)", "月"), ("[`year_month_day`](year_month_day.md)", "年月日")],
  ["年の型", "is_leap() でうるう年判定", "2024y リテラル"], cr="year")

C("weekday", "曜日を表す型。",
  "日付から曜日を知りたいとき、自分で計算式を書く必要はありません。`std::chrono::weekday` は曜日を表す型で、`sys_days` から作れます。`Sunday` ... `Saturday` の定数があります。",
  ["`weekday{sys_days{...}}` で日付から曜日を取り出す。", "`c_encoding()` は日曜が 0、`iso_encoding()` は月曜が 1 で日曜が 7。", "`Monday[2]` のように書くと「第 2 月曜」になる。"],
  "class weekday {\n public:\n  constexpr weekday(const sys_days& d) noexcept;\n  constexpr unsigned c_encoding() const noexcept;    // 日曜 = 0\n  constexpr unsigned iso_encoding() const noexcept;  // 月曜 = 1, 日曜 = 7\n};",
  [("d", "sys_days", "曜日を知りたい日付")], "`c_encoding()` は日曜 0 〜 土曜 6",
  PRE + """
int main() {
  using namespace std::chrono;
  weekday w{sys_days{2024y / January / 1}};
  std::println("{}", w.c_encoding());
  std::println("{}", w == Monday);
}""", "1\ntrue",
  [("「毎週月曜日」のイベント判定", "`weekday{today} == std::chrono::Monday`")],
  ("日曜 = 7 だと思い込む", "`c_encoding()` は日曜が 0、`iso_encoding()` は日曜が 7 です。どちらを使うかで結果が変わります。"),
  [("[`weekday_indexed`](weekday_indexed.md)", "第 n 曜日"), ("[`weekday_last`](weekday_last.md)", "最後の曜日")],
  ["曜日の型", "c_encoding は日曜 0", "Monday[2] で第 2 月曜"], cr="weekday")

C("weekday_indexed", "「第 n の曜日」を表す型（第 2 月曜日など）。",
  "「毎月第 2 月曜日」のような予定を扱うとき、`weekday` に「何番目か」の情報を足したものが `weekday_indexed` です。`Monday[2]` と書いて作ります。",
  ["`weekday[n]` で作る（n は 1〜5）。", "`weekday()` と `index()` で中身を取り出す。", "`year/month/weekday[n]` で日付の指定になる。"],
  "class weekday_indexed {\n public:\n  constexpr std::chrono::weekday weekday() const noexcept;\n  constexpr unsigned index() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("n", "unsigned", "何番目か（1〜5）")], "`index()` は何番目か",
  PRE + """
int main() {
  using namespace std::chrono;
  auto wi = Monday[2];
  std::println("{} {}", wi.weekday().c_encoding(), wi.index());
}""", "1 2",
  [("毎月第 2 日曜日のセール日", "`std::chrono::Sunday[2]`")],
  ("第 5 曜日が存在しない月", "第 5 週の曜日が無い月もあります。`ok()` と、組み合わせた日付の `ok()` で確かめます。"),
  [("[`weekday`](weekday.md)", "曜日"), ("[`weekday_last`](weekday_last.md)", "最後の曜日")],
  ["第 n 曜日", "weekday[n] で作る", "n は 1〜5"], cr="weekday_indexed")

C("weekday_last", "「最後の曜日」を表す型（最終金曜日など）。",
  "「毎月最後の金曜日」のように、月ごとに日付が変わる指定には、`weekday_last` が使えます。`Friday[last]` と書いて作ります。",
  ["`weekday[std::chrono::last]` で作る。", "`year/month/weekday[last]` で日付の指定になる。", "月ごとに 4 週か 5 週かを気にしなくてよい。"],
  "class weekday_last {\n public:\n  constexpr std::chrono::weekday weekday() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("w", "weekday", "曜日")], "`weekday()` は元の曜日",
  PRE + """
int main() {
  using namespace std::chrono;
  auto wl = Friday[last];
  std::println("{}", wl.weekday().c_encoding());
}""", "5",
  [("月末の金曜日にボーナスを配る", "`2024y / March / Friday[last]`")],
  ("last をつけ忘れる", "`Friday[5]` と書くと「第 5 金曜」で、無い月もあります。「最後」は必ず `last` を使います。"),
  [("[`weekday_indexed`](weekday_indexed.md)", "第 n 曜日"), ("[`last_spec`](last_spec.md)", "`last` の型")],
  ["最後の曜日", "weekday[last] で作る", "月によって日付が変わる"], cr="weekday_last")

C("month_day", "月と日の組（誕生日のような、年を問わない日付）。",
  "毎年同じ日にあるイベント（誕生日、記念日）は、年を決めずに「3 月 5 日」と持ちたくなります。`std::chrono::month_day` は、月と日の組を表します。",
  ["`March / 5` または `month_day{March, day{5}}` で作る。", "2 月 29 日は有効（うるう年かどうかは年がないので判断しない）。", "年をつけて `year_month_day` にする。"],
  "class month_day {\n public:\n  constexpr month_day(const month& m, const day& d) noexcept;\n  constexpr month month() const noexcept;\n  constexpr day day() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("m", "month", "月"), ("d", "day", "日")], "`ok()` は有効な月日なら `true`",
  PRE + """
int main() {
  using namespace std::chrono;
  auto md = February / 29;
  std::println("{}", md.ok());
  std::println("{}", (February / 30).ok());
}""", "true\nfalse",
  [("毎年のイベントの日付", "`std::chrono::December / 25`")],
  ("2 月 29 日を無条件で有効だと思う", "`month_day` としては有効ですが、年をつけると平年では無効になります。年をつけて確認します。"),
  [("[`month`](month.md)", "月"), ("[`day`](day.md)", "日"), ("[`year_month_day`](year_month_day.md)", "年月日")],
  ["月と日の組", "年を問わない日付", "2/29 は有効"], cr="month_day")

C("month_day_last", "「その月の最終日」を表す型。",
  "月末の日付は月ごとに違います（28〜31）。`month_day_last` は、「その月の最後の日」を日数を知らなくても表します。`February / last` と書いて作ります。",
  ["`month / last` で作る。", "年をつけると `year_month_day_last` になる。", "具体的な日は年を決めてから分かる。"],
  "class month_day_last {\n public:\n  constexpr std::chrono::month month() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("m", "month", "月")], "`month()` は元の月",
  PRE + """
int main() {
  using namespace std::chrono;
  auto mdl = February / last;
  std::println("{}", unsigned(mdl.month()));
}""", "2",
  [("月末締めの集計日", "`std::chrono::March / std::chrono::last`")],
  ("日数を自分で場合分けする", "うるう年や 30 日の月の場合分けは不要です。`last` で表して、年をつけたあと `day()` で取ります。"),
  [("[`year_month_day_last`](year_month_day_last.md)", "年つきの月末"), ("[`last_spec`](last_spec.md)", "`last` の型")],
  ["月の最終日", "month / last", "年をつけると日が決まる"], cr="month_day_last")

C("month_weekday", "「その月の第 n 曜日」を表す型（年を問わない）。",
  "「毎年 11 月の第 4 木曜日」（アメリカの感謝祭）のような、年を決めない日付の指定が `month_weekday` です。`November / Thursday[4]` と書きます。",
  ["`month / weekday[n]` で作る。", "年をつけて `year_month_weekday` にすると、具体的な日付になる。"],
  "class month_weekday {\n public:\n  constexpr std::chrono::month month() const noexcept;\n  constexpr std::chrono::weekday_indexed weekday_indexed() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("m", "month", "月"), ("wdi", "weekday_indexed", "第 n 曜日")], "`ok()` は有効なら `true`",
  PRE + """
int main() {
  using namespace std::chrono;
  auto mw = March / Monday[2];
  std::println("{} {}", mw.ok(), mw.weekday_indexed().index());
}""", "true 2",
  [("毎年の祝日の指定", "`std::chrono::November / std::chrono::Thursday[4]`")],
  ("日付だと思う", "これは日付ではなく「指定」です。年をつけて `sys_days` にして初めて日付になります。"),
  [("[`month_weekday_last`](month_weekday_last.md)", "最後の曜日"), ("[`year_month_weekday`](year_month_weekday.md)", "年つき")],
  ["月の第 n 曜日", "年を問わない", "年をつけて日付に"], cr="month_weekday")

C("month_weekday_last", "「その月の最後の曜日」を表す型（年を問わない）。",
  "「毎年 5 月の最後の月曜日」（アメリカの戦没者追悼記念日）のような指定には `month_weekday_last` を使います。`May / Monday[last]` と書きます。",
  ["`month / weekday[last]` で作る。", "年をつけると `year_month_weekday_last`。"],
  "class month_weekday_last {\n public:\n  constexpr std::chrono::month month() const noexcept;\n  constexpr std::chrono::weekday_last weekday_last() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("m", "month", "月"), ("wdl", "weekday_last", "最後の曜日")], "`ok()` は有効なら `true`",
  PRE + """
int main() {
  using namespace std::chrono;
  auto mwl = March / Monday[last];
  std::println("{}", mwl.weekday_last().weekday().c_encoding());
}""", "1",
  [("毎月最後の曜日のイベント", "`std::chrono::March / std::chrono::Monday[std::chrono::last]`")],
  ("日付だと思う", "年をつけてから `sys_days` にします。"),
  [("[`month_weekday`](month_weekday.md)", "第 n 曜日"), ("[`year_month_weekday_last`](year_month_weekday_last.md)", "年つき")],
  ["月の最後の曜日", "年を問わない", "年をつけて日付に"], cr="month_weekday_last")

C("year_month", "年と月の組。",
  "「2024 年 3 月」のように、日を決めない期間を扱うとき、`year_month` が使えます。月末への移動や月の足し算ができます。",
  ["`2024y / March` で作る。", "`+ months{n}` で月を進められる（年の繰り上がりも自動）。", "日をつけて `year_month_day` に。"],
  "class year_month {\n public:\n  constexpr year_month(const year& y, const month& m) noexcept;\n  constexpr std::chrono::year year() const noexcept;\n  constexpr std::chrono::month month() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("y", "year", "年"), ("m", "month", "月")], "`ok()` は有効なら `true`",
  PRE + """
int main() {
  using namespace std::chrono;
  auto ym = 2024y / March;
  ym += months{11};
  std::println("{} {}", int(ym.year()), unsigned(ym.month()));
}""", "2025 2",
  [("月ごとの集計キー", "`std::chrono::year_month`")],
  ("月を足して手計算する", "`months{n}` を足せば、年の繰り上がりも自動で計算されます。"),
  [("[`year_month_day`](year_month_day.md)", "年月日"), ("[`month`](month.md)", "月")],
  ["年と月の組", "months を足せる", "日は含まない"], cr="year_month")

C("year_month_day_last", "「その年のその月の最終日」を表す型。",
  "月末の日付は、月とうるう年で決まります。`year_month_day_last` は `2024y / February / last` のように書くと、具体的な最終日（`day()`）を計算してくれます。",
  ["`year / month / last` で作る。", "`day()` で最終日が分かる。", "`sys_days` に変換して日付にできる。"],
  "class year_month_day_last {\n public:\n  constexpr std::chrono::day day() const noexcept;\n  constexpr operator sys_days() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("y", "year", "年"), ("mdl", "month_day_last", "月末の指定")], "`day()` は最終日",
  PRE + """
int main() {
  using namespace std::chrono;
  std::println("{}", unsigned((2024y / February / last).day()));
  std::println("{}", unsigned((2023y / February / last).day()));
}""", "29\n28",
  [("月末締めの日付を求める", "`(year / month / std::chrono::last).day()`")],
  ("自分で日数の表を書く", "うるう年の判定を含む日数の計算は、この型に任せます。"),
  [("[`month_day_last`](month_day_last.md)", "年を問わない月末"), ("[`year_month_day`](year_month_day.md)", "年月日")],
  ["月末の日を計算する", "うるう年も考慮", "year/month/last"], cr="year_month_day_last")

C("year_month_weekday", "「その年のその月の第 n 曜日」を表す型。",
  "「2024 年 3 月の第 2 月曜日」のような指定です。`sys_days` に変換すると、具体的な日付が分かります。",
  ["`2024y / March / Monday[2]` で作る。", "`sys_days` に変換して、`year_month_day` で日にちを取り出す。"],
  "class year_month_weekday {\n public:\n  constexpr operator sys_days() const noexcept;\n  constexpr std::chrono::weekday_indexed weekday_indexed() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("y", "year", "年"), ("mw", "month_weekday", "月と第 n 曜日")], "`sys_days` に変換できる",
  PRE + """
int main() {
  using namespace std::chrono;
  year_month_weekday ymw = 2024y / March / Monday[2];
  year_month_day ymd{sys_days{ymw}};
  std::println("{}", unsigned(ymd.day()));
}""", "11",
  [("毎月第 2 月曜日の日付を求める", "`sys_days{year / month / Monday[2]}`")],
  ("無い日付に変換する", "第 5 曜日などが存在しない月では `ok()` が `false` です。確認してから変換します。"),
  [("[`month_weekday`](month_weekday.md)", "年を問わない"), ("[`year_month_weekday_last`](year_month_weekday_last.md)", "最後の曜日")],
  ["年つきの第 n 曜日", "sys_days に変換して日付に", "ok() で存在確認"], cr="year_month_weekday")

C("year_month_weekday_last", "「その年のその月の最後の曜日」を表す型。",
  "「2024 年 3 月の最後の月曜日」の指定です。`sys_days` に変換すると具体的な日付になります。",
  ["`2024y / March / Monday[last]` で作る。", "`sys_days` に変換して日付にする。"],
  "class year_month_weekday_last {\n public:\n  constexpr operator sys_days() const noexcept;\n  constexpr std::chrono::weekday_last weekday_last() const noexcept;\n  constexpr bool ok() const noexcept;\n};",
  [("y", "year", "年"), ("mwl", "month_weekday_last", "月と最後の曜日")], "`sys_days` に変換できる",
  PRE + """
int main() {
  using namespace std::chrono;
  year_month_weekday_last ymwl = 2024y / March / Monday[last];
  year_month_day ymd{sys_days{ymwl}};
  std::println("{}", unsigned(ymd.day()));
}""", "25",
  [("月末の最後の曜日のイベント日", "`sys_days{year / month / weekday[last]}`")],
  ("最後の曜日が週の何番目かを決め打ちする", "月によって 4 回の月も 5 回の月もあります。`last` を使えば自動で決まります。"),
  [("[`month_weekday_last`](month_weekday_last.md)", "年を問わない"), ("[`year_month_weekday`](year_month_weekday.md)", "第 n 曜日")],
  ["年つきの最後の曜日", "sys_days に変換", "last で自動決定"], cr="year_month_weekday_last")

C("last_spec", "「最後」を表す定数 `std::chrono::last` の型。",
  "`February / last` や `Friday[last]` に出てくる `last` は、「最後」を表す特別な定数です。`last_spec` はその型で、直接使うことはほとんどありません。",
  ["`std::chrono::last` が唯一の値。", "`month / last`、`weekday[last]` の中で使う。"],
  "struct last_spec { explicit last_spec() = default; };\ninline constexpr last_spec last{};",
  [], "なし（目印）",
  PRE + """
int main() {
  using namespace std::chrono;
  auto ymdl = 2024y / February / last;
  std::println("{}", unsigned(ymdl.day()));
}""", "29",
  [("月末の指定", "`std::chrono::last`")],
  ("`last` を数値と思う", "`last` は数値ではなく目印の型の値です。"),
  [("[`month_day_last`](month_day_last.md)", "月末"), ("[`weekday_last`](weekday_last.md)", "最後の曜日")],
  ["「最後」を表す目印", "month / last など", "型自体は意識しない"], cr="last_spec")

# ---- 12 時間制
for nm, sigtxt, what, ex, res in [
    ("is_am", "constexpr bool is_am(const hours& h) noexcept;", "24 時間制の時刻が午前かを調べる。", "std::chrono::is_am(std::chrono::hours{9})", "true"),
    ("is_pm", "constexpr bool is_pm(const hours& h) noexcept;", "24 時間制の時刻が午後かを調べる。", "std::chrono::is_pm(std::chrono::hours{13})", "true")]:
    C(nm, what, f"時刻を「午前 / 午後」で表示するとき、24 時間制の時を 12 より大きいかで判定するのは手間です。`{nm}` が、午前（0〜11 時）か午後（12〜23 時）かを教えてくれます。",
      ["引数は `hours`（0〜23）。", "`make12` と組み合わせて 12 時間制の表示を作る。"], sigtxt, [("h", "hours", "24 時間制の時（0〜23）")], f"{'午前' if nm == 'is_am' else '午後'}なら `true`",
      PRE + f"""
int main() {{
  std::println("{{}}", {ex});
}}""", res, [("12 時間制の表示", "`is_am(h) ? \"AM\" : \"PM\"`")], ("範囲外の時を渡す", "0〜23 以外の値は未定義です。"),
      [("[`make12`](make12.md)", "12 時間制に直す"), ("[`make24`](make24.md)", "24 時間制に直す")], [what.rstrip("。"), "引数は 0〜23 の hours", "make12 とセットで使う"], cr="hour_of_day/is_am")
C("make12", "24 時間制の時を、12 時間制の時（1〜12）に直す。",
  "「15 時」を「午後 3 時」と表示するには、12 時間制に直す必要があります。`make12(hours{15})` は `hours{3}` を返します。",
  ["0 時は 12 になる（午前 12 時）。", "午前か午後かは [`is_am`](is_am.md) / [`is_pm`](is_pm.md) で別に調べる。"],
  "constexpr hours make12(const hours& h) noexcept;", [("h", "hours", "24 時間制の時（0〜23）")], "12 時間制の時（1〜12）の `hours`",
  PRE + """
int main() {
  using namespace std::chrono;
  std::println("{}", make12(hours{15}).count());
  std::println("{}", make12(hours{0}).count());
}""", "3\n12", [("時計の表示", "`make12(hours{h}).count()`")], ("0 時の結果を 0 だと思う", "0 時は 12 になります。"),
  [("[`make24`](make24.md)", "逆の変換"), ("[`hh_mm_ss`](hh_mm_ss.md)", "時分秒")], ["24 → 12 時間制", "0 時は 12", "午前午後は別に調べる"], cr="hour_of_day/make12")
C("make24", "12 時間制の時を、24 時間制の時（0〜23）に直す。",
  "「午後 3 時」を内部の時刻に直すには、24 時間制にします。`make24(hours{3}, true)` は `hours{15}` です（2 つ目の引数が「午後か」）。",
  ["2 つ目の引数が `true` なら午後。", "12 時午後は 12 時、12 時午前は 0 時。"],
  "constexpr hours make24(const hours& h, bool is_pm) noexcept;", [("h", "hours", "12 時間制の時（1〜12）"), ("is_pm", "bool", "午後なら `true`")], "24 時間制の時（0〜23）の `hours`",
  PRE + """
int main() {
  using namespace std::chrono;
  std::println("{}", make24(hours{3}, true).count());
  std::println("{}", make24(hours{12}, false).count());
}""", "15\n0", [("ユーザーが入力した 12 時間制の時刻を直す", "`make24(hours{h}, pm)`")], ("12 時の扱い", "午前 12 時は 0 時、午後 12 時は 12 時です。"),
  [("[`make12`](make12.md)", "逆の変換")], ["12 → 24 時間制", "2 つ目は午後か", "12 時の扱いに注意"], cr="hour_of_day/make24")

# ---- 時点の別名
for nm, what, base, ex, res in [
    ("sys_time", "system_clock の時点を表す別名（単位を選べる）。", "time_point<system_clock, Duration>", "std::chrono::sys_time<std::chrono::seconds> t{std::chrono::seconds{90}};\n  std::println(\"{}\", t.time_since_epoch().count());", "90"),
    ("sys_seconds", "system_clock の時点を、秒の単位で表す別名。", "sys_time<seconds>", "std::chrono::sys_seconds t{std::chrono::seconds{3600}};\n  std::println(\"{}\", t.time_since_epoch().count());", "3600"),
    ("sys_days", "system_clock の時点を、日の単位で表す別名（カレンダーの日付）。", "sys_time<days>", "std::chrono::sys_days d = 2024y / std::chrono::January / 1;\n  std::println(\"{}\", d.time_since_epoch().count());", "19723"),
    ("local_time", "タイムゾーンのない、地域の時刻を表す別名。", "time_point<local_t, Duration>", "std::chrono::local_time<std::chrono::seconds> t{std::chrono::seconds{60}};\n  std::println(\"{}\", t.time_since_epoch().count());", "60"),
    ("local_seconds", "ローカル時刻を、秒の単位で表す別名。", "local_time<seconds>", "std::chrono::local_seconds t{std::chrono::seconds{120}};\n  std::println(\"{}\", t.time_since_epoch().count());", "120"),
    ("local_days", "ローカル時刻を、日の単位で表す別名（地域のカレンダーの日付）。", "local_time<days>", "std::chrono::local_days d = 2024y / std::chrono::January / 1;\n  std::println(\"{}\", d.time_since_epoch().count());", "19723"),
    ("utc_time", "utc_clock の時点を表す別名（単位を選べる）。", "time_point<utc_clock, Duration>", "std::println(\"{}\", std::is_same_v<std::chrono::utc_time<std::chrono::seconds>, std::chrono::time_point<std::chrono::utc_clock, std::chrono::seconds>>);", "true"),
    ("file_time", "file_clock の時点を表す別名（単位を選べる）。", "time_point<file_clock, Duration>", "std::println(\"{}\", std::is_same_v<std::chrono::file_time<std::chrono::seconds>, std::chrono::time_point<std::chrono::file_clock, std::chrono::seconds>>);", "true")]:
    extra = "#include <type_traits>\n" if nm in ("utc_time", "file_time") else ""
    using = "  using namespace std::chrono;\n" if nm in ("sys_days", "local_days") else ""
    C(nm, what, f"`time_point<system_clock, seconds>` のように毎回書くのは長いので、標準が別名を用意しています。`std::chrono::{nm}` は、{what.rstrip('。')}です。",
      ["中身は `" + base + "`。", "`time_since_epoch().count()` で基準時刻からの経過を数で取れる。", "カレンダー型（`year_month_day`）と相互に変換できる。" if "days" in nm else "時計の違いを型で区別できる。"],
      f"template <class Duration>\nusing {nm} = {base};" if "Duration" in base else f"using {nm} = {base};",
      [], f"`{nm}` の値", PRE + extra + "\nint main() {\n" + using.replace("using namespace std::chrono;", "using namespace std::chrono;") + "  " + ex + "\n}", res,
      [("時刻を型で区別する", f"`std::chrono::{nm}`")], ("ローカル時刻とシステム時刻を混ぜる" if "local" in nm else "時計が違う時点を混ぜる", "`local_time` は地域の時刻、`sys_time` は UTC 基準の時刻で、型が別です。変換は `zoned_time` や `time_zone` を通します。"),
      [("[`time_point`](time_point.md)", "時点の型"), ("[`zoned_time`](zoned_time.md)", "タイムゾーンつきの時刻")],
      [what.rstrip("。"), "time_since_epoch() で経過を取る", "型で時計の種類を区別する"], cr="time_point", rjn="time_point", cx="定数")

# ---- タイムゾーン
C("time_zone", "1 つのタイムゾーン（例: Asia/Tokyo）を表す型。",
  "世界の時刻は、地域ごとに時差や夏時間が違います。`std::chrono::time_zone` は、1 つの地域の規則（Asia/Tokyo など）を持つ型で、UTC の時点とその地域のローカル時刻を変換できます。",
  ["`locate_zone(\"Asia/Tokyo\")` で取得する（所有はせず、ポインタで受け取る）。", "`name()` で名前、`get_info(...)` でその時点の時差などを取れる。", "`zoned_time` と組み合わせて使うことが多い。"],
  "class time_zone {\n public:\n  string_view name() const noexcept;\n  template <class D> sys_info get_info(const sys_time<D>& st) const;\n  template <class D> local_info get_info(const local_time<D>& tp) const;\n  template <class D> local_time<common_type_t<D, seconds>> to_local(const sys_time<D>& tp) const;\n  template <class D> sys_time<common_type_t<D, seconds>> to_sys(const local_time<D>& tp) const;\n};",
  [("st / tp", "sys_time / local_time", "調べたい時点")], "名前や、その時点の時差などの情報",
  PRE + """
int main() {
  const auto* tz = std::chrono::locate_zone("Asia/Tokyo");
  std::println("{}", tz->name());
}""", "Asia/Tokyo", [("プレイヤーの地域の時刻で日替わりを判定", "`zoned_time(tz, now)`")],
  ("tzdata がない環境", "タイムゾーンのデータベースが無い環境（一部の組み込みや古い OS）では、`locate_zone` が例外を投げます。"),
  [("[`zoned_time`](zoned_time.md)", "ゾーンつきの時刻"), ("[`locate_zone`](locate_zone.md)", "名前から取得する")],
  ["タイムゾーンを表す型", "locate_zone で取る", "データベースが必要"], cr="time_zone", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("locate_zone", "名前から time_zone を取得する。",
  "タイムゾーンを使うには、まず `\"Asia/Tokyo\"` のような名前からゾーンを取り出します。`locate_zone(name)` が、その `time_zone` へのポインタを返します。",
  ["名前は IANA のゾーン名（`Asia/Tokyo`、`America/New_York`）。", "戻り値はデータベースが持つオブジェクトへのポインタ（解放不要）。", "見つからないと例外。"],
  "const time_zone* locate_zone(string_view tz_name);", [("tz_name", "string_view", "ゾーン名")], "`time_zone` へのポインタ（見つからなければ例外）",
  PRE + """
int main() {
  const auto* tz = std::chrono::locate_zone("Asia/Tokyo");
  std::println("{}", tz->name());
}""", "Asia/Tokyo", [("ユーザー設定のゾーンを読み込む", "`std::chrono::locate_zone(setting)`")],
  ("名前を間違える", "存在しない名前は `std::runtime_error` を投げます。外から入力された名前は `try` で囲みます。"),
  [("[`current_zone`](current_zone.md)", "今のゾーン"), ("[`time_zone`](time_zone.md)", "ゾーンの型")], ["名前からゾーンを取る", "戻りはポインタ", "見つからなければ例外"], cr="tzdb/locate_zone", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("current_zone", "今の環境のタイムゾーンを取得する。",
  "プレイヤーのパソコンが設定している地域の時刻を扱いたいときは、名前を知らなくても `current_zone()` で取り出せます。",
  ["OS の設定から取得される。", "戻り値はデータベースが持つ `time_zone` へのポインタ。", "`zoned_time(current_zone(), now)` でローカル時刻にする。"],
  "const time_zone* current_zone();", [], "今のゾーンへのポインタ",
  PRE + """
int main() {
  const auto* tz = std::chrono::current_zone();
  std::println("{}", tz != nullptr);
}""", "true", [("プレイヤーの現地時刻を表示", "`zoned_time{current_zone(), system_clock::now()}`")],
  ("サーバーでクライアントの地域と取り違える", "動いているマシンの設定です。遠隔のプレイヤーの地域は、別に受け取ります。"),
  [("[`locate_zone`](locate_zone.md)", "名前から取得")], ["今の環境のゾーン", "OS の設定に従う", "戻りはポインタ"], cr="tzdb/current_zone", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("tzdb", "タイムゾーンのデータベース（IANA）を表す型。",
  "タイムゾーンの規則は、各国の政策で変わります。それを持つデータベースが `tzdb` で、バージョン・ゾーン一覧・うるう秒の一覧などをもっています。",
  ["`get_tzdb()` で現在のものを取る。", "`zones`・`links`・`leap_seconds`・`version` のメンバをもつ。", "`reload_tzdb()` で更新を読み直せる。"],
  "struct tzdb {\n  string version;\n  vector<time_zone> zones;\n  vector<time_zone_link> links;\n  vector<leap_second> leap_seconds;\n  const time_zone* locate_zone(string_view) const;\n  const time_zone* current_zone() const;\n};",
  [], "データベースの内容",
  PRE + """
int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", !db.zones.empty());
}""", "true", [("対応しているゾーン一覧を調べる", "`std::chrono::get_tzdb().zones`")],
  ("コピーして持ち歩く", "大きなオブジェクトです。参照で扱います。"),
  [("[`get_tzdb`](get_tzdb.md)", "取得する関数"), ("[`tzdb_list`](tzdb_list.md)", "複数世代の管理")], ["タイムゾーンの DB", "get_tzdb() で取る", "zones / links / leap_seconds"], cr="tzdb", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("tzdb_list", "tzdb の更新履歴（世代ごとの一覧）を管理する型。",
  "実行中にタイムゾーンのデータベースを更新すると、古い版を参照している箇所も残ります。`tzdb_list` は、新しい順に `tzdb` の世代を持ち、`front()` で最新のものを取ります。",
  ["`get_tzdb_list()` で取得する。", "`front()` が最新の `tzdb`。", "`begin()` / `end()` で世代を順に調べられる。"],
  "class tzdb_list {\n public:\n  const tzdb& front() const noexcept;\n  const_iterator begin() const noexcept;\n  const_iterator end() const noexcept;\n};",
  [], "世代の一覧",
  PRE + """
int main() {
  const auto& db = std::chrono::get_tzdb_list().front();
  std::println("{}", !db.zones.empty());
}""", "true", [("データベースの更新を確かめる", "`std::chrono::reload_tzdb()`")],
  ("古い世代の参照を持ち続ける", "更新後も古い世代が残るため、メモリが増えます。必要なら参照を持たず、その都度取り直します。"),
  [("[`tzdb`](tzdb.md)", "データベース本体")], ["tzdb の世代管理", "front() が最新", "更新は reload_tzdb"], cr="tzdb_list", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("get_tzdb", "現在のタイムゾーンデータベースを取得する。",
  "タイムゾーンの情報にアクセスする入り口です。`get_tzdb()` が、最新の `tzdb` への参照を返します。",
  ["戻り値は参照（コピーしない）。", "`locate_zone` と `current_zone` は内部でこれを使っている。"],
  "const tzdb& get_tzdb();", [], "最新の `tzdb` の参照",
  PRE + """
int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", !db.version.empty());
}""", "true", [("対応ゾーンの確認", "`std::chrono::get_tzdb().zones.size()`")],
  ("コピーを作る", "`auto db = get_tzdb();` はコピーです。`const auto&` で受けます。"),
  [("[`tzdb`](tzdb.md)", "データベースの型")], ["最新の tzdb を返す", "参照で受ける", "locate_zone の元"], cr="tzdb/get_tzdb", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("time_zone_link", "別名のタイムゾーン（古い名前から新しい名前への対応）を表す型。",
  "ゾーン名は、地名の変更などで変わります。古い名前でも使えるように、データベースは別名を持ちます。`time_zone_link` は、その「古い名前 → 実際の名前」の対応を表します。",
  ["`name()` が別名、`target()` が実際の名前。", "`tzdb.links` に入っている。"],
  "class time_zone_link {\n public:\n  string_view name() const noexcept;\n  string_view target() const noexcept;\n};",
  [], "別名と、その向き先の名前",
  PRE + """
int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", !db.links.empty());
}""", "true", [("古いゾーン名を新しい名前に直す", "`link.target()`")],
  ("別名を実体と取り違える", "別名は `time_zone` ではありません。`target()` の名前で `locate_zone` します。"),
  [("[`tzdb`](tzdb.md)", "データベース"), ("[`time_zone`](time_zone.md)", "ゾーン本体")], ["ゾーン名の別名", "name() と target()", "links に入っている"], cr="time_zone_link", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("sys_info", "ある UTC の時点での、時差・夏時間・略称の情報。",
  "あるゾーンの「ある瞬間」の時差（UTC との差）や、夏時間かどうか、略称（JST など）を知りたいことがあります。`time_zone::get_info(sys_time)` が返す `sys_info` に入っています。",
  ["`offset`（UTC との差）、`save`（夏時間のずれ）、`abbrev`（略称）をもつ。", "`begin` と `end` は、この情報が有効な期間。"],
  "struct sys_info {\n  sys_seconds begin;\n  sys_seconds end;\n  seconds offset;\n  minutes save;\n  string abbrev;\n};",
  [], "時差などの情報",
  PRE + """
int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("Asia/Tokyo");
  auto info = tz->get_info(sys_days{2024y / January / 1});
  std::println("{} {}", info.offset.count(), info.abbrev);
}""", "32400 JST", [("プレイヤーの時差を表示", "`tz->get_info(now).offset`")],
  ("夏時間を考えない", "`offset` には夏時間のずれが含まれます。`save` が 0 でないときは夏時間の最中です。"),
  [("[`local_info`](local_info.md)", "ローカル時刻から調べる"), ("[`time_zone`](time_zone.md)", "ゾーン")], ["UTC 時点の時差情報", "offset / save / abbrev", "get_info で得る"], cr="sys_info", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("local_info", "あるローカル時刻の時差情報（曖昧・存在しない場合も表す）。",
  "夏時間の切り替えでは、同じローカル時刻が 2 回ある（曖昧）か、1 回もない（存在しない）ことがあります。`local_info` は、そうした状況を `result` で示し、`first` / `second` に候補の情報を入れます。",
  ["`result` は `unique`・`nonexistent`・`ambiguous` のどれか。", "`first` と `second` は `sys_info`。", "曖昧なら両方、そうでなければ `first` だけ有効。"],
  "struct local_info {\n  static constexpr int unique = 0;\n  static constexpr int nonexistent = 1;\n  static constexpr int ambiguous = 2;\n  int result;\n  sys_info first;\n  sys_info second;\n};",
  [], "状況と候補の情報",
  PRE + """
int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("Asia/Tokyo");
  auto info = tz->get_info(local_days{2024y / January / 1});
  std::println("{}", info.first.abbrev);
}""", "JST", [("切り替え日のスケジュールを調べる", "`info.result == local_info::ambiguous`")],
  ("結果を無視して変換する", "曖昧・存在しない時刻を `to_sys` に渡すと例外です。先に `local_info` で確かめます。"),
  [("[`sys_info`](sys_info.md)", "UTC 側の情報"), ("[`nonexistent_local_time`](nonexistent_local_time.md)", "存在しない時刻の例外"), ("[`ambiguous_local_time`](ambiguous_local_time.md)", "曖昧な時刻の例外")],
  ["ローカル時刻の時差情報", "result で曖昧さを表す", "first / second に候補"], cr="local_info", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("nonexistent_local_time", "夏時間の切り替えで存在しないローカル時刻を変換したときの例外。",
  "夏時間が始まる日は、時計が 2:00 から 3:00 に飛びます。「2:30」は存在しない時刻で、これを UTC に変換しようとすると `nonexistent_local_time` が投げられます。",
  ["`std::runtime_error` から派生。", "`to_sys(local_time)` が存在しない時刻で投げる。", "`choose::earliest` / `choose::latest` を渡すと、投げずに選べる。"],
  "class nonexistent_local_time : public runtime_error {\n public:\n  template <class D> nonexistent_local_time(const local_time<D>&, const local_info&);\n};",
  [], "`what()` に説明が入る",
  PRE + """
int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("America/New_York");
  try {
    tz->to_sys(local_days{2024y / March / 10} + 2h + 30min);
  } catch (const nonexistent_local_time&) {
    std::println("存在しない時刻");
  }
}""", "存在しない時刻", [("夏時間の切り替え日のスケジュール", "`to_sys(t, choose::earliest)`")],
  ("切り替え日を考えない", "ゾーンによっては、年に 1 度、存在しない時刻があります。例外が出る箇所を `try` で囲みます。"),
  [("[`ambiguous_local_time`](ambiguous_local_time.md)", "曖昧な時刻の例外"), ("[`local_info`](local_info.md)", "事前に確かめる")],
  ["存在しないローカル時刻の例外", "夏時間の切り替えで起こる", "choose で回避"], cr="nonexistent_local_time", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("ambiguous_local_time", "夏時間の終わりで 2 回ある（曖昧な）ローカル時刻を変換したときの例外。",
  "夏時間が終わる日は、時計が 2:00 から 1:00 に戻り、「1:30」が 2 回あります。どちらの 1:30 か決められないので、UTC に変換しようとすると `ambiguous_local_time` が投げられます。",
  ["`std::runtime_error` から派生。", "`to_sys(local_time)` が曖昧な時刻で投げる。", "`choose::earliest` / `choose::latest` で、どちらかを選べる。"],
  "class ambiguous_local_time : public runtime_error {\n public:\n  template <class D> ambiguous_local_time(const local_time<D>&, const local_info&);\n};",
  [], "`what()` に説明が入る",
  PRE + """
int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("America/New_York");
  try {
    tz->to_sys(local_days{2024y / November / 3} + 1h + 30min);
  } catch (const ambiguous_local_time&) {
    std::println("曖昧な時刻");
  }
}""", "曖昧な時刻", [("夏時間の終わりの日のログ", "`to_sys(t, choose::earliest)`")],
  ("日本だけで動かして見逃す", "Asia/Tokyo には夏時間がないため、この例外は出ません。海外ゾーンで初めて出ます。"),
  [("[`nonexistent_local_time`](nonexistent_local_time.md)", "存在しない時刻の例外"), ("[`local_info`](local_info.md)", "事前に確かめる")],
  ["曖昧なローカル時刻の例外", "夏時間の終わりで起こる", "choose で回避"], cr="ambiguous_local_time", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("leap_second", "うるう秒の挿入日と値を表す型。",
  "うるう秒は、UTC に不定期に足される 1 秒です。`leap_second` は、いつ入ったか（`date()`）と、何秒か（`value()`、普通は +1 秒）を表し、`tzdb.leap_seconds` に一覧があります。",
  ["`date()` は UTC のうるう秒の挿入時刻。", "`value()` は +1 秒（正のうるう秒）か −1 秒。", "`utc_clock` の計算に使われる。"],
  "class leap_second {\n public:\n  constexpr sys_seconds date() const noexcept;\n  constexpr seconds value() const noexcept;\n};",
  [], "挿入日と値",
  PRE + """
int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", db.leap_seconds.front().value().count());
}""", "1", [("うるう秒を含む経過時間の計算", "`get_leap_second_info(utc_time)`")],
  ("日の長さを 86400 秒と決めつける", "うるう秒がある日は 86401 秒です。`system_clock` はそれを無視し、`utc_clock` は数えます。"),
  [("[`get_leap_second_info`](get_leap_second_info.md)", "ある時点の情報"), ("[`utc_clock`](utc_clock.md)", "うるう秒を数える時計")],
  ["うるう秒の記録", "date() と value()", "tzdb.leap_seconds に一覧"], cr="leap_second", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("get_leap_second_info", "ある UTC の時点が、うるう秒の中か、それまでに何秒入ったかを調べる。",
  "UTC の時刻が、うるう秒の 1 秒（23:59:60）そのものなのか、そしてその時点までに累計で何秒挿入されたかを知りたいことがあります。`get_leap_second_info(utc_time)` が教えてくれます。",
  ["`is_leap_second` が `true` なら、うるう秒の最中。", "`elapsed` は、その時点までに入ったうるう秒の累計。"],
  "template <class D>\nleap_second_info get_leap_second_info(const utc_time<D>& ut);",
  [("ut", "utc_time", "調べる時点")], "`is_leap_second` と `elapsed`",
  PRE + """
int main() {
  using namespace std::chrono;
  auto ut = utc_clock::from_sys(sys_days{2024y / January / 1});
  auto info = get_leap_second_info(ut);
  std::println("{} {}", info.is_leap_second, info.elapsed.count());
}""", "false 27", [("経過秒の厳密な計算", "`info.elapsed`")],
  ("sys_time に使う", "引数は `utc_time` です。`system_clock` の時点は、先に `utc_clock::from_sys` で変換します。"),
  [("[`leap_second`](leap_second.md)", "うるう秒の記録"), ("[`utc_clock`](utc_clock.md)", "UTC の時計")], ["うるう秒の状態を調べる", "is_leap_second と elapsed", "utc_time を渡す"], cr="get_leap_second_info", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")

# ---- 入出力
C("parse", "文字列を書式に従って読み込み、chrono の型にするための入力マニピュレータ。",
  "ユーザーが入力した日付文字列を、`year_month_day` のような型に変換したいことがあります。`std::chrono::parse(書式, 変数)` を `>>` に渡すと、書式（`%Y-%m-%d` など）に従って読み込みます。",
  ["`in >> std::chrono::parse(\"%F\", ymd);` の形で使う。", "書式は `strftime` に似た `%Y` `%m` `%d` `%H` `%M` `%S` など。", "失敗すると `failbit` が立つ。"],
  "template <class CharT, class Traits, class Alloc, class Parsable>\n/* 実装定義 */ parse(const basic_string<CharT, Traits, Alloc>& fmt, Parsable& tp);",
  [("fmt", "文字列", "書式"), ("tp", "chrono の型", "結果を入れる変数")], "ストリームに流せるマニピュレータ",
  PRE + "#include <sstream>\n" + """
int main() {
  std::istringstream in("2024-03-05");
  std::chrono::year_month_day ymd;
  in >> std::chrono::parse("%F", ymd);
  std::println("{}", unsigned(ymd.day()));
}""", "5", [("セーブデータの日付文字列を読む", "`in >> std::chrono::parse(\"%F\", ymd)`")],
  ("失敗を確かめない", "書式に合わない文字列では `failbit` が立ち、変数は変わりません。読み込み後に `if (in)` で確かめます。"),
  [("[`from_stream`](from_stream.md)", "同じ処理を関数で書く"), ("[`to_stream`](to_stream.md)", "書式で出力する")], ["文字列を chrono の型に読み込む", "書式は strftime 風", "失敗は failbit"], cr="parse", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("from_stream", "ストリームから書式に従って chrono の型を読み込む。",
  "`parse` マニピュレータの中身にあたる関数です。ストリームと書式と変数を渡して、読み込みます。",
  ["`from_stream(in, \"%F\", ymd)` の形で使う。", "戻り値はストリーム（成功したかは `if (in)` で見る）。"],
  "template <class CharT, class Traits>\nbasic_istream<CharT, Traits>& from_stream(basic_istream<CharT, Traits>& is, const CharT* fmt, year_month_day& ymd);",
  [("is", "istream", "読み込み元"), ("fmt", "書式", "`%Y-%m-%d` など"), ("ymd", "chrono の型", "結果を入れる変数")], "`is` への参照",
  PRE + "#include <sstream>\n" + """
int main() {
  std::istringstream in("2024-03-05");
  std::chrono::year_month_day ymd;
  std::chrono::from_stream(in, "%F", ymd);
  std::println("{}", unsigned(ymd.day()));
}""", "5", [("入力欄の日付文字列を読む", "`from_stream(in, \"%F\", ymd)`")],
  ("書式と文字列を合わせない", "`%F` は `%Y-%m-%d` です。文字列が `2024/03/05` なら書式も `%Y/%m/%d` にします。"),
  [("[`parse`](parse.md)", "マニピュレータ版"), ("[`to_stream`](to_stream.md)", "書式で出力する")], ["ストリームから読み込む", "書式は strftime 風", "失敗はストリームの状態で見る"], cr="from_stream", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
C("to_stream", "書式に従って chrono の型をストリームに書き出す。",
  "日付を `2024/01/01` のような決まった形で書き出したいとき、`to_stream(os, 書式, 値)` が使えます。`std::format` の chrono 用の書式と同じ指定が使えます。",
  ["`to_stream(os, \"%Y/%m/%d\", ymd)` の形で使う。", "`std::format(\"{:%Y/%m/%d}\", ymd)` でも同じ。"],
  "template <class CharT, class Traits>\nbasic_ostream<CharT, Traits>& to_stream(basic_ostream<CharT, Traits>& os, const CharT* fmt, const year_month_day& ymd);",
  [("os", "ostream", "書き出し先"), ("fmt", "書式", "`%Y/%m/%d` など"), ("ymd", "chrono の型", "書き出す値")], "`os` への参照",
  PRE + "#include <sstream>\n" + """
int main() {
  using namespace std::chrono;
  std::ostringstream oss;
  to_stream(oss, "%Y/%m/%d", 2024y / January / 1);
  std::println("{}", oss.str());
}""", "2024/01/01", [("ログに日付を決まった書式で書く", "`to_stream(os, \"%F\", ymd)`")],
  ("`std::format` で足りるのに使う", "新しいコードでは `std::format` / `std::println` の `{:%F}` が簡単です。"),
  [("[`parse`](parse.md)", "読み込み"), ("[`format`](../format.md)", "文字列の書式化")], ["chrono の型を書式つきで書き出す", "format の書式と同じ", "新しいコードは std::format"], cr="to_stream", compiler="C++20 の機能です。GCC 13 以降で使えます。")

if __name__ == "__main__":
    flush_hubs()
