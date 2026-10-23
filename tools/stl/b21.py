"""バッチ 21: 取りこぼしの補充（chrono の補助、cstdio の remove/rename、ios のメンバ、シグナル・errno のマクロ、wctype）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mk import *  # noqa: F401,F403,E402
import members  # noqa: E402
import b19  # noqa: E402
from b19 import SPEC, run  # noqa: E402

CH = "utilities/chrono/"
CHI = "[`<chrono>`](../chrono.md) の概要を先に読んでください。"
V20 = ("20", "C++20")
C20 = "C++20 の機能です。GCC 13 以降、MSVC 19.29 以降で使えます。"

P(CH + "abs.md", "std::chrono::abs", "duration の絶対値を返す。", "rare", "chrono",
  "`duration` が負のこともある差（`now - target`）から、「どれだけずれているか」の大きさだけが欲しいことがあります。`std::chrono::abs(d)` は、`duration` の絶対値を返します。整数の `abs` を使うと、`count()` を取り出す手間が増えます。",
  ["`duration` を受け取り、同じ型で返す。", "符号つきの `rep` の `duration` だけで使える。", "`std::abs`（数値）とは別の関数。"],
  [("目標時刻とのずれの大きさ", "`std::chrono::abs(now - target)`")], ("符号なしの rep で使う", "`rep` が符号なし整数の `duration` には使えません。"),
  [("[`floor`](floor.md)", "単位を丸める"), ("[`duration`](duration.md)", "時間の長さ")], ["duration の絶対値", "now - target の大きさ", "std::abs とは別"],
  sig="template <class Rep, class Period>\nconstexpr duration<Rep, Period> abs(duration<Rep, Period> d);", args=[("d", "duration", "絶対値を求める時間")], ret="`|d|`", cx="定数",
  code="""#include <chrono>
#include <print>

int main() {
  using namespace std::chrono_literals;
  auto d = 100ms - 250ms;
  std::println("{}", std::chrono::abs(d).count());
}""", out="150", ver=("17", "C++17"), info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/abs.html", cr="chrono/abs")
for nm, what, intro in [
    ("ceil", "duration / time_point を、指定した単位に切り上げる。", "`duration_cast` は 0 方向へ切り捨てます。`ceil` は、大きいほうへ切り上げます。必要な数のフレームを求める、残り時間を秒に切り上げて表示する、といった場面で使います。"),
    ("round", "duration / time_point を、指定した単位に四捨五入する。", "`duration_cast` は切り捨て、`ceil` は切り上げです。`round` は、最も近い値へ丸めます。ちょうど中間のときは、偶数のほうへ丸められます。")]:
    P(CH + nm + ".md", "std::chrono::" + nm, what, "rare", "chrono", intro,
      ["`floor`・`ceil`・`round`・`duration_cast` で、丸め方を選ぶ。", "`duration` にも `time_point` にも使える。", "戻り値の単位は、`ToDuration` で指定する。"],
      [("残り時間を秒単位で表示する", f"`std::chrono::{nm}<std::chrono::seconds>(remaining)`")], ("`duration_cast` と同じだと思う", "`duration_cast` は 0 方向への切り捨てです。負の値では、`floor` と結果が違います。"),
      [("[`floor`](floor.md)", "切り捨て"), ("[`duration_cast`](duration_cast.md)", "0 方向への切り捨て")], [what.rstrip("。"), "duration にも time_point にも使える", "丸め方で使い分ける"],
      sig=f"template <class ToDuration, class Rep, class Period>\nconstexpr ToDuration {nm}(const duration<Rep, Period>& d);", args=[("ToDuration", "テンプレート引数", "変換後の `duration`"), ("d", "duration", "変換する時間")], ret="丸めた `ToDuration`", cx="定数",
      code=f"""#include <chrono>
#include <print>

int main() {{
  using namespace std::chrono_literals;
  auto d = 2500ms;
  std::println("{{}}", std::chrono::{nm}<std::chrono::seconds>(d).count());
}}""", out="3" if nm == "ceil" else "2", ver=("17", "C++17"), info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj=f"chrono/{nm}.html", cr=f"chrono/duration/{nm}")
P(CH + "is_clock.md", "std::chrono::is_clock", "型が chrono の「時計」の条件を満たすかを調べる型特性。", "rare", "chrono",
  "ジェネリックな関数で、`system_clock` や `steady_clock` のような時計の型だけを受け付けたいことがあります。`is_clock_v<C>` は、`C` が時計として必要な型名（`rep`・`period`・`duration`・`time_point`）と `now()`・`is_steady` を持つなら `true` です。",
  ["`_v` 版で `bool` が取れる。", "自作の時計が、条件を満たしているかの確認に使える。", "C++20 の機能。"],
  [("時計の型だけを受け付けるテンプレート", "`static_assert(std::chrono::is_clock_v<Clock>);`")], ("時刻の型（`time_point`）を渡す", "`time_point` は時計ではありません。時計の型は `system_clock` などです。"),
  [("[`system_clock`](system_clock.md)", "時計の例"), ("[`steady_clock`](steady_clock.md)", "時計の例")], ["時計の条件を調べる型特性", "_v 版で bool", "自作の時計の検査に"],
  sig="template <class T>\nstruct is_clock;\ntemplate <class T>\ninline constexpr bool is_clock_v = is_clock<T>::value;", args=[("T", "型", "調べる型")], ret="時計なら `true`", cx="コンパイル時のみ",
  code="""#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::is_clock_v<std::chrono::steady_clock>);
  std::println("{}", std::chrono::is_clock_v<int>);
}""", out="true\nfalse", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/is_clock.html", cr="chrono/is_clock", compiler=C20)
P(CH + "local_t.md", "std::chrono::local_t", "「どのタイムゾーンでもない、地域の時刻」を表す疑似の時計の型。", "rare", "chrono",
  "`local_time` は、`system_clock`（UTC 基準）とは別に、「タイムゾーンが決まっていない時刻」を表します。その型の目印になる疑似の時計が `local_t` です。実際の時計ではなく、`now()` はありません。`time_zone` を通して、`sys_time` と変換して初めて、特定の瞬間になります。",
  ["`local_time<Duration>` = `time_point<local_t, Duration>`。", "時計として `now()` は持たない。", "`time_zone::to_sys` で UTC の時点に変換する。"],
  [("「毎日朝 6 時」のような地域の時刻を扱う", "`std::chrono::local_days{...} + 6h`")], ("実際の瞬間と思う", "`local_time` は、タイムゾーンが決まるまで、特定の瞬間ではありません。"),
  [("[`local_time`](local_time.md)", "ローカル時刻の別名"), ("[`time_zone`](time_zone.md)", "変換する")], ["タイムゾーンなしの時刻の目印", "now() を持たない", "time_zone で変換"],
  sig="struct local_t {};", args=[], ret="なし（目印の型）", cx="なし",
  code="""#include <chrono>
#include <print>
#include <type_traits>

int main() {
  using LT = std::chrono::local_time<std::chrono::seconds>;
  std::println("{}", std::is_same_v<LT, std::chrono::time_point<std::chrono::local_t, std::chrono::seconds>>);
}""", out="true", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/local_t.html", cr="chrono/local_t", compiler=C20)
P(CH + "choose.md", "std::chrono::choose", "曖昧なローカル時刻の変換で、どちらを選ぶかを指定する列挙型。", "rare", "chrono",
  "夏時間の終わりでは、同じローカル時刻が 2 回あります。`time_zone::to_sys(local_time, choose::earliest)` のように、`choose` を渡すと、例外を投げずに、早いほう（`earliest`）か遅いほう（`latest`）を選べます。",
  ["`earliest`: 2 回あるうちの早いほう。", "`latest`: 遅いほう。", "存在しない時刻に対しては、切り替わりの時点が返る。"],
  [("曖昧な時刻を、早いほうに決める", "`tz->to_sys(t, std::chrono::choose::earliest)`")], ("例外を投げると思う", "`choose` を渡すと、例外は投げず、どちらかが選ばれます。"),
  [("[`ambiguous_local_time`](ambiguous_local_time.md)", "曖昧な時刻の例外"), ("[`time_zone`](time_zone.md)", "ゾーン")], ["曖昧なローカル時刻の選び方", "earliest / latest", "例外を避けられる"],
  sig="enum class choose {\n  earliest,\n  latest\n};", args=[], ret="なし（列挙型）", cx="なし",
  code="""#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("America/New_York");
  auto t = local_days{2024y / November / 3} + 1h + 30min;  // 2 回ある時刻
  auto a = tz->to_sys(t, choose::earliest);
  auto b = tz->to_sys(t, choose::latest);
  std::println("{}", (b - a).count());
}""", out="3600", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/choose.html", cr="chrono/choose", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
P(CH + "reload_tzdb.md", "std::chrono::reload_tzdb", "タイムゾーンのデータベースを、最新のものに読み込み直す。", "rare", "chrono",
  "夏時間の規則は、国の政策で変わります。OS のタイムゾーンのデータが更新されたとき、起動したままのプログラムは古い規則を使い続けます。`reload_tzdb()` は、データベースを読み込み直して、最新の規則を反映します。",
  ["新しいデータがあれば、新しい `tzdb` を追加して、その参照を返す。", "古い `tzdb` への参照は、そのまま有効。", "常時動くサーバーなどで、定期的に呼ぶ。"],
  [("長時間動くサーバーが、規則の更新を取り込む", "`std::chrono::reload_tzdb();`")], ("更新できない環境で呼ぶ", "データベースが更新できない環境では、現在のものがそのまま返ります。"),
  [("[`get_tzdb`](get_tzdb.md)", "現在のデータベース"), ("[`remote_version`](remote_version.md)", "新しい版があるか")], ["タイムゾーン DB を読み直す", "新しい版を追加する", "常時動くプログラム向け"],
  sig="const tzdb& reload_tzdb();", args=[], ret="最新の `tzdb` への参照", cx="データベースの大きさに比例",
  code="""#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::reload_tzdb();
  std::println("{}", !db.version.empty());
}""", out="true", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/reload_tzdb.html", cr="chrono/tzdb_functions", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
P(CH + "remote_version.md", "std::chrono::remote_version", "OS が持つ、最新のタイムゾーンデータベースの版を返す。", "rare", "chrono",
  "いま使っているデータベースより新しい版があるかを、読み込む前に知りたいことがあります。`remote_version()` は、OS 側にある最新の版の文字列を返します。`get_tzdb().version` と比べて違えば、`reload_tzdb()` で読み込み直せます。",
  ["戻り値は版を表す文字列（例: `2024a`）。", "現在の版は `get_tzdb().version`。", "違えば `reload_tzdb()` を呼ぶ。"],
  [("更新があるときだけ読み直す", "`if (remote_version() != get_tzdb().version) reload_tzdb();`")], ("読み直しをしても反映されない", "OS 側のデータが更新されていないと、同じ版のままです。"),
  [("[`reload_tzdb`](reload_tzdb.md)", "読み直す")], ["最新の版を返す", "get_tzdb().version と比べる", "更新確認に使う"],
  sig="std::string remote_version();", args=[], ret="OS が持つ最新の版の文字列", cx="OS に依存",
  code="""#include <chrono>
#include <print>

int main() {
  std::println("{}", !std::chrono::remote_version().empty());
}""", out="true", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/remote_version.html", cr="chrono/tzdb_functions", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
P(CH + "zoned_traits.md", "std::chrono::zoned_traits", "zoned_time が、ゾーンの指定をどう解釈するかを決める特性。", "rare", "chrono",
  "`zoned_time` は、`\"Asia/Tokyo\"` のような文字列から `time_zone` を探します。この「ゾーンの型」と「既定のゾーン」「文字列からゾーンを探す方法」を決めているのが `zoned_traits` です。自作のゾーンの型を `zoned_time` で使うときに、特殊化します。",
  ["`default_zone()` と `locate_zone(name)` を持つ。", "標準では `const time_zone*` に対して用意されている。", "ふつうは意識しない。"],
  [("自作のゾーン型を zoned_time で使う", "`zoned_traits<MyZone>` を特殊化する")], ("特殊化せずに自作型を渡す", "特殊化がないと、`zoned_time` が文字列からゾーンを探せません。"),
  [("[`zoned_time`](zoned_time.md)", "ゾーンつきの時刻"), ("[`time_zone`](time_zone.md)", "ゾーン")], ["zoned_time のゾーン解釈の特性", "default_zone / locate_zone", "ふつうは触らない"],
  sig="template <class TimeZonePtr>\nstruct zoned_traits;  // const time_zone* に対して特殊化済み", args=[("TimeZonePtr", "型", "ゾーンを指す型")], ret="`default_zone()` と `locate_zone()`", cx="定数",
  code="""#include <chrono>
#include <print>

int main() {
  const auto* tz = std::chrono::zoned_traits<const std::chrono::time_zone*>::locate_zone("Asia/Tokyo");
  std::println("{}", tz->name());
}""", out="Asia/Tokyo", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/zoned_traits.html", cr="chrono/zoned_traits", compiler="C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。")
for nm, base, what in [("tai_time", "tai_clock", "tai_clock の時点（単位を選べる）"), ("tai_seconds", "tai_time<seconds>", "tai_clock の時点（秒単位）"), ("gps_time", "gps_clock", "gps_clock の時点（単位を選べる）"), ("gps_seconds", "gps_time<seconds>", "gps_clock の時点（秒単位）"), ("utc_seconds", "utc_time<seconds>", "utc_clock の時点（秒単位）")]:
    short = nm.split("_")[0]
    P(CH + nm + ".md", "std::chrono::" + nm, f"{what}を表す別名。", "rare", "chrono",
      f"`time_point<{base.split('<')[0] if '<' in base else base}, ...>` のように毎回書くのは長いので、標準が別名を用意しています。`{nm}` は、{what}です。",
      ["中身は " + (f"`time_point<{base}, Duration>`" if "_time" in nm and "seconds" not in nm else f"`{base}`") + "。", "`time_since_epoch().count()` で経過を取れる。", "時計の違いを型で区別できる。"],
      [("時計ごとに時点の型を区別する", f"`std::chrono::{nm}`")], ("時計が違う時点を混ぜる", "別の時計の時点どうしは、引き算できません。`clock_cast` で変換します。"),
      [("[`clock_cast`](clock_cast.md)", "時計どうしを変換する"), (f"[`{short}_clock`]({short}_clock.md)", "時計")], [f"{what}の別名", "time_since_epoch() で経過を取る", "clock_cast で他の時計に変換"],
      sig=(f"template <class Duration>\nusing {nm} = time_point<{base}, Duration>;" if "seconds" not in nm else f"using {nm} = {base};"), args=[], ret=f"`{nm}` の値", cx="なし",
      code=f"""#include <chrono>
#include <print>
#include <type_traits>

int main() {{
  std::println("{{}}", std::is_same_v<std::chrono::{nm}{'<std::chrono::seconds>' if 'seconds' not in nm else ''}, std::chrono::time_point<std::chrono::{short}_clock, std::chrono::seconds>>);
}}""", out="true", ver=V20, info=CHI, hub="utilities/chrono.md", hubname="std::chrono", group="時間（std::chrono）", rj="chrono/time_point.html", cr="chrono/time_point", compiler=C20)

# month / weekday の定数
for i, mn in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1):
    add_secs(CH + "month.md", fn("std::chrono::" + mn, f"inline constexpr std::chrono::month {mn}{{{i}}};", None, f"{i} 月を表す定数", "定数", None, notes=f"`std::chrono::{mn}` は、{i} 月（`month{{{i}}}`）を表す定数です。`2024y / {mn} / 1` のように、日付を組み立てるときに使います。", ver=V20, ids=mn))
for i, wd in enumerate(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]):
    add_secs(CH + "weekday.md", fn("std::chrono::" + wd, f"inline constexpr std::chrono::weekday {wd}{{{i}}};", None, f"{['日', '月', '火', '水', '木', '金', '土'][i]}曜日を表す定数", "定数", None, notes=f"`std::chrono::{wd}` は、{['日', '月', '火', '水', '木', '金', '土'][i]}曜日（`c_encoding()` が {i}）を表す定数です。`{wd}[2]`（第 2 {['日', '月', '火', '水', '木', '金', '土'][i]}曜日）や、`{wd}[std::chrono::last]`（最後の{['日', '月', '火', '水', '木', '金', '土'][i]}曜日）のように使います。", ver=V20, ids=wd))

# ---- cstdio の remove / rename
SIO = "io/cstdio/"
SIOI = "[`std::fopen`](fopen.md) を先に読んでください。"
P(SIO + "remove.md", "std::remove（<cstdio>）", "ファイルを削除する（C の関数）。", "rare", "cstdio",
  "`<cstdio>` の `std::remove` は、ファイル名を渡して、ファイルを削除する C の関数です。`<algorithm>` の `std::remove`（要素を後ろへ詰める）とは別物なので、混同しないようにします。C++17 以降では、`std::filesystem::remove` のほうが、フォルダも扱えて、エラーも詳しく分かります。",
  ["`<algorithm>` の `std::remove` とは別物。", "成功すると 0、失敗すると 0 以外。", "新しいコードでは `std::filesystem::remove`。"],
  [("一時ファイルを消す", "`std::remove(\"tmp.dat\");`")], ("`algorithm` の `remove` と混同する", "`<cstdio>` の `remove` は文字列を受け取るファイル削除、`<algorithm>` の `remove` はイテレータの範囲を受け取る要素の移動です。"),
  [("[`filesystem::remove`](../filesystem/remove.md)", "新しい書き方"), ("[`rename`](rename.md)", "名前を変える")], ["ファイルを削除する C の関数", "algorithm の remove とは別物", "新しいコードは filesystem::remove"],
  sig="int remove(const char* filename);", args=[("filename", "const char*", "削除するファイルのパス")], ret="成功なら 0、失敗なら 0 以外", cx="OS に依存",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("kdocs_remove_demo.txt", "w");
  std::fclose(f);
  std::println("{}", std::remove("kdocs_remove_demo.txt"));
}""", out="0", info=SIOI, rj="cstdio/remove.html", cr="io/c/remove")
P(SIO + "rename.md", "std::rename", "ファイルの名前を変える（移動もできる）。", "rare", "cstdio",
  "ファイルの名前を変える、または別のフォルダに移動する C の関数です。移動先にすでにファイルがあるときの動作は、環境によって違います（Windows では失敗し、Linux では上書き）。C++17 以降では、`std::filesystem::rename` が、同じ働きでエラーも詳しく分かります。",
  ["移動先に同名のファイルがあるときの動作は、環境で違う。", "成功すると 0。", "新しいコードでは `std::filesystem::rename`。"],
  [("一時ファイルを正式な名前にする", "`std::rename(\"save.tmp\", \"save.dat\");`")], ("上書きの挙動を決めつける", "移動先が存在するときの結果は、実装定義です。先に消すか、`filesystem::rename` を使います。"),
  [("[`filesystem::rename`](../filesystem/rename.md)", "新しい書き方"), ("[`remove`](remove.md)", "削除する")], ["ファイルの名前を変える C の関数", "上書きの挙動は環境で違う", "新しいコードは filesystem::rename"],
  sig="int rename(const char* old_filename, const char* new_filename);", args=[("old_filename", "const char*", "元のパス"), ("new_filename", "const char*", "新しいパス")], ret="成功なら 0、失敗なら 0 以外", cx="OS に依存",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("kdocs_rename_a.txt", "w");
  std::fclose(f);
  std::println("{}", std::rename("kdocs_rename_a.txt", "kdocs_rename_b.txt"));
  std::remove("kdocs_rename_b.txt");
}""", out="0", info=SIOI, rj="cstdio/rename.html", cr="io/c/rename")

# ---- ios_base::failure
P("io/ios_base_failure.md", "std::ios_base::failure", "ストリームのエラーで投げられる例外クラス。", "rare", "ios",
  "ストリームは、エラーが起きても、既定では例外を投げず、状態（`failbit` など）だけを立てます。`exceptions()` で例外を有効にすると、エラーのときに `std::ios_base::failure` が投げられます。`std::system_error` の派生クラスで、`code()` でエラーコードを取れます。",
  ["`exceptions(std::ios::failbit | std::ios::badbit)` で有効にする。", "`std::system_error` から派生。", "既定では投げられない。"],
  [("ファイルを開けなかったら例外にする", "`file.exceptions(std::ios::failbit);`")], ("既定で例外が出ると思う", "既定では、状態を確かめる必要があります。例外にするには、`exceptions()` を設定します。"),
  [("[`basic_ios`](basic_ios.md)", "状態の確認"), ("[`system_error`](../support/exceptions/system_error.md)", "親のクラス")], ["ストリームの例外", "exceptions() で有効にする", "system_error の派生"],
  sig="class ios_base::failure : public system_error {\n public:\n  explicit failure(const std::string& message, const std::error_code& ec = std::io_errc::stream);\n};", args=[], ret="`what()` と `code()` を持つ", cx="なし",
  code="""#include <fstream>
#include <ios>
#include <print>

int main() {
  std::ifstream in;
  in.exceptions(std::ios::failbit);
  try {
    in.open("not_exist_kdocs.txt");
  } catch (const std::ios_base::failure&) {
    std::println("開けなかった");
  }
}""", out="開けなかった", ver=("11", "C++11"), info="[`std::basic_ios`](basic_ios.md) を先に読んでください。", rj="ios/ios_base/failure.html", cr="io/ios_base/failure")

# ---- ios_base / basic_ios / istream / ostream のメンバ
M = members.MEMBERS
M["io/ios_base.md"] = "flags setf unsetf precision width xalloc register_callback sync_with_stdio imbue getloc"
M["io/basic_ios.md"] = "good fail bad eof rdstate setstate clear tie rdbuf copyfmt fill narrow widen exceptions operator_bool swap"
M["io/istream.md"] = "operator>> get getline read ignore peek gcount tellg seekg"
M["io/ostream.md"] = "operator<< put write flush tellp seekp"
for n, sg, d, cx in [
    ("flags", "fmtflags flags() const;\nfmtflags flags(fmtflags fl);", "いまの書式フラグを返します。引数つきの版は、フラグを**全部置き換え**て、それまでのフラグを返します。", "定数"),
    ("setf", "fmtflags setf(fmtflags fl);\nfmtflags setf(fmtflags fl, fmtflags mask);", "書式フラグを**追加**します。2 引数の版は、`mask` の範囲（`basefield` など）を先にクリアしてから設定するので、`hex` の切り替えに使えます。", "定数"),
    ("unsetf", "void unsetf(fmtflags mask);", "指定した書式フラグを解除します。", "定数"),
    ("precision", "streamsize precision() const;\nstreamsize precision(streamsize new_precision);", "小数の出力の桁数（既定は 6）を返す、または設定します。`setprecision` マニピュレータと同じ働きです。", "定数"),
    ("width", "streamsize width() const;\nstreamsize width(streamsize new_width);", "次の 1 回の出力の最小の幅を返す、または設定します。出力のたびにリセットされます。`setw` と同じ働きです。", "定数"),
    ("xalloc", "static int xalloc();", "`iword`・`pword` で使う、新しい添字を確保して返します。自作のマニピュレータが、ストリームごとの設定を覚えるのに使います。", "定数"),
    ("register_callback", "void register_callback(event_callback fn, int index);", "`imbue`・`copyfmt`・ストリームの破棄のときに呼ばれる関数を登録します。`iword`/`pword` の後始末に使います。", "定数"),
    ("sync_with_stdio", "static bool sync_with_stdio(bool sync = true);", "C++ のストリームと C の入出力（`printf` など）を同期するかを設定します。`false` にすると、入出力が速くなります（競技プログラミングの定番）が、`printf` と混ぜられなくなります。", "定数"),
    ("imbue", "std::locale imbue(const std::locale& loc);", "ストリームのロケールを設定します。数値の区切りや、日付の書式が変わります。", "定数"),
    ("getloc", "std::locale getloc() const;", "ストリームのロケールを返します。", "定数"),
]:
    SPEC[("io/ios_base.md", n)] = (sg, d, cx)
for n, sg, d, cx in [
    ("eof", "bool eof() const;", "入力が終端に達していれば `true`。ループの条件に使うと、最後に 1 回余分に読むことがあります。読み込みの成否で判定します。", "定数"),
    ("clear", "void clear(iostate state = goodbit);", "状態フラグを `state` で**置き換え**ます（既定は、エラーなしに戻す）。失敗したあとに、読み込みを再開するために使います。", "定数"),
    ("tie", "std::ostream* tie() const;\nstd::ostream* tie(std::ostream* tiestr);", "入力の前に自動でフラッシュされる、結び付いた出力ストリームを返す、または設定します。`cin` は `cout` と結び付いています。`cin.tie(nullptr)` で解除すると、速くなります。", "定数"),
    ("rdbuf", "std::streambuf* rdbuf() const;\nstd::streambuf* rdbuf(std::streambuf* sb);", "ストリームバッファを返す、または付け替えます。`cout` の出力先を、一時的にファイルや文字列に切り替えられます。", "定数"),
    ("copyfmt", "basic_ios& copyfmt(const basic_ios& rhs);", "書式の設定（フラグ・幅・桁数・ロケール・埋め文字）を、別のストリームからコピーします。", "定数"),
    ("fill", "char_type fill() const;\nchar_type fill(char_type ch);", "幅を埋める文字（既定は空白）を返す、または設定します。`setfill` と同じ働きです。", "定数"),
    ("narrow", "char narrow(char_type c, char dfault) const;", "`wchar_t` などの文字を `char` に変換します。変換できなければ `dfault` を返します。", "定数"),
    ("widen", "char_type widen(char c) const;", "`char` を、ストリームの文字型に変換します。", "定数"),
    ("exceptions", "iostate exceptions() const;\nvoid exceptions(iostate except);", "どの状態フラグが立ったときに、例外（`ios_base::failure`）を投げるかを設定します。", "定数"),
    ("operator_bool", "explicit operator bool() const;", "`!fail()` と同じです。`if (in >> x)` のように、読み込みの成否を判定するのに使います。", "定数"),
    ("swap", "void swap(basic_ios& rhs) noexcept;", "ストリームの状態と書式を入れ替えます（バッファは入れ替えません）。", "定数"),
]:
    SPEC[("io/basic_ios.md", n)] = (sg, d, cx)
for n, sg, d, cx in [
    ("operator>>", "istream& operator>>(int& value);\nistream& operator>>(std::string& str);", "書式つきで読み込みます。空白を区切りとして読み飛ばします。失敗すると `failbit` が立ちます。", "O(読んだ文字数)"),
    ("get", "int get();\nistream& get(char& ch);\nistream& get(char* s, streamsize n, char delim = '\\n');", "空白や改行も含めて、1 文字（または複数文字）を、書式なしで読みます。", "O(読んだ文字数)"),
    ("getline", "istream& getline(char* s, streamsize n, char delim = '\\n');", "区切り文字（既定は改行）まで、1 行を読みます。区切り文字は読み捨てます。`std::string` に読むなら、自由関数の `std::getline` を使います。", "O(読んだ文字数)"),
    ("read", "istream& read(char* s, streamsize n);", "ちょうど `n` バイトを、書式なしで読みます（バイナリ用）。足りなければ `failbit` と `eofbit` が立ちます。", "O(n)"),
    ("ignore", "istream& ignore(streamsize count = 1, int_type delim = EOF);", "最大 `count` 文字を読み飛ばします。`delim` に当たったら、それも読んで止まります。", "O(count)"),
    ("gcount", "streamsize gcount() const;", "直前の書式なしの読み込み（`get`・`getline`・`read`・`ignore`）で、読んだ文字数。", "定数"),
    ("tellg", "pos_type tellg();", "入力側の現在位置を返します。`seekg` で戻るときの目印になります。", "定数"),
    ("seekg", "istream& seekg(pos_type pos);\nistream& seekg(off_type off, ios_base::seekdir dir);", "入力側の位置を動かします。ファイルの途中から読み直したいときに使います。", "定数"),
]:
    SPEC[("io/istream.md", n)] = (sg, d, cx)
for n, sg, d, cx in [
    ("operator<<", "ostream& operator<<(int value);\nostream& operator<<(const std::string& str);", "書式つきで出力します。`<<` を続けて書けます（戻り値がストリーム自身のため）。", "O(出力の長さ)"),
    ("write", "ostream& write(const char* s, streamsize n);", "`n` バイトを、書式なしで書き込みます（バイナリ用）。", "O(n)"),
    ("flush", "ostream& flush();", "バッファの中身を、出力先に書き出します。", "出力の量に比例"),
    ("tellp", "pos_type tellp();", "出力側の現在位置を返します。", "定数"),
    ("seekp", "ostream& seekp(pos_type pos);\nostream& seekp(off_type off, ios_base::seekdir dir);", "出力側の位置を動かします。書き込み位置を戻して、書き直したいときに使います。", "定数"),
]:
    SPEC[("io/ostream.md", n)] = (sg, d, cx)

# ---- シグナル・errno・assert のマクロ
for sg_, d_ in [("SIGINT", "割り込み（`Ctrl+C`）"), ("SIGTERM", "終了要求"), ("SIGSEGV", "不正なメモリアクセス（セグメンテーション違反）"), ("SIGABRT", "異常終了（`abort()`）"), ("SIGFPE", "算術エラー（0 での整数除算など）"), ("SIGILL", "不正な命令")]:
    add_secs("io/csignal.md", fn(sg_, f"#define {sg_} /* 実装定義の整数 */", None, f"{d_}を表すシグナル番号のマクロ", "なし", None,
                                 notes=f"`{sg_}` は、{d_}を表すシグナルの番号です。`std::signal({sg_}, handler)` で、ハンドラを登録します。" + ("ハンドラから戻った後の動作は未定義なので、通常は終了処理だけを行います。" if sg_ in ("SIGSEGV", "SIGFPE", "SIGILL") else ""), ids=sg_))
for sg_, d_ in [("SIG_DFL", "既定の動作に戻す"), ("SIG_IGN", "シグナルを無視する"), ("SIG_ERR", "`signal` が失敗したときの戻り値")]:
    add_secs("io/csignal.md", fn(sg_, f"#define {sg_} /* 実装定義 */", None, f"{d_}ための特別なハンドラの値", "なし", None, notes=f"`{sg_}` は、{d_}ための値です。", ids=sg_))
for en, d_ in [("EDOM", "数学関数の引数が、定義域の外"), ("ERANGE", "結果が、表せる範囲の外"), ("EILSEQ", "不正なマルチバイト列"), ("ENOENT", "ファイルやフォルダがない"), ("EACCES", "アクセス権がない"), ("EEXIST", "すでに存在する"),
               ("EINVAL", "引数が不正"), ("ENOMEM", "メモリ不足"), ("ENOSPC", "デバイスに空きがない"), ("EINTR", "システムコールがシグナルで中断された")]:
    add_secs("io/cerrno.md", fn(en, f"#define {en} /* 実装定義の整数 */", None, f"`errno` の値：{d_}", "なし", None, notes=f"`errno` が `{en}` のとき、{d_}ことを表します。`std::errc` の対応する値（`std::errc::{ {'EDOM': 'argument_out_of_domain', 'ERANGE': 'result_out_of_range', 'EILSEQ': 'illegal_byte_sequence', 'ENOENT': 'no_such_file_or_directory', 'EACCES': 'permission_denied', 'EEXIST': 'file_exists', 'EINVAL': 'invalid_argument', 'ENOMEM': 'not_enough_memory', 'ENOSPC': 'no_space_on_device', 'EINTR': 'interrupted'}[en] }`）と比べるほうが、移植性があります。", ids=en))
add_secs("io/assert.md", fn("NDEBUG", "#define NDEBUG", None, "`assert` を無効にするマクロ", "なし", None, notes="`#include <cassert>` の前に `NDEBUG` が定義されていると、`assert(...)` は何もしなくなります。リリースビルドでは、通常これが定義されます（`-DNDEBUG`）。`assert` の中に副作用のある式を書くと、リリースで消えるので、注意します。", ids="NDEBUG"))
add_secs("io/assert.md", fn("static_assert", "static_assert(constant-expression, message);", None, "コンパイル時に条件を検査するキーワード", "コンパイル時", None, notes="実行時ではなく、**コンパイル時**に条件を検査します。条件が偽なら、コンパイルエラーになり、`message` が表示されます。型のサイズやテンプレートの前提の確認に使います。C++17 からは、`message` を省略できます。", ids="static_assert"))

# ---- wctype
WC = "numeric/cwctype/"
WCI = "[`std::iswalpha`](iswalpha.md) を先に読んでください。"
for nm, summ, intro, sig, args, ret, body, out in [
    ("wctype_t", "ワイド文字の分類の種類を表す型。", "`iswctype` に渡す、「どの分類か」を表す型です。`wctype(\"alpha\")` で作ります。ロケールごとの独自の分類を使いたいときに使います。", "using wctype_t = /* 実装定義 */;", [], "なし（型）", 'std::wctype_t t = std::wctype("alpha");\nstd::println("{}", t != 0);', "true"),
    ("wctype", "分類の名前から、wctype_t を取得する。", "`\"alpha\"`・`\"digit\"`・`\"upper\"` などの名前から、分類を表す値を取り出します。`iswctype` と組み合わせて、実行時に分類を選べます。", "std::wctype_t wctype(const char* property);", [("property", "const char*", "分類の名前（`\"alpha\"` など）")], "分類を表す値。名前が不正なら 0", 'std::println("{}", std::wctype("alpha") != 0);', "true"),
    ("iswctype", "ワイド文字が、指定した分類に属するかを調べる。", "`iswalpha` などの固定の関数ではなく、`wctype` で取った分類の値で、実行時に分類を選んで判定します。", "int iswctype(std::wint_t wc, std::wctype_t desc);", [("wc", "wint_t", "調べるワイド文字"), ("desc", "wctype_t", "`wctype` で取った分類")], "属していれば 0 以外", 'std::println("{}", std::iswctype(L\'a\', std::wctype("alpha")) != 0);', "true"),
    ("wctrans_t", "ワイド文字の変換の種類を表す型。", "`towctrans` に渡す、「どの変換か」を表す型です。`wctrans(\"toupper\")` で作ります。", "using wctrans_t = /* 実装定義 */;", [], "なし（型）", 'std::wctrans_t t = std::wctrans("toupper");\nstd::println("{}", t != 0);', "true"),
    ("wctrans", "変換の名前から、wctrans_t を取得する。", "`\"toupper\"`・`\"tolower\"` などの名前から、変換を表す値を取り出します。`towctrans` と組み合わせて、実行時に変換を選べます。", "std::wctrans_t wctrans(const char* property);", [("property", "const char*", "変換の名前（`\"toupper\"` など）")], "変換を表す値。名前が不正なら 0", 'std::println("{}", std::wctrans("toupper") != 0);', "true"),
    ("towctrans", "ワイド文字を、指定した変換で変換する。", "`towupper` などの固定の関数ではなく、`wctrans` で取った変換の値で、実行時に変換を選んで適用します。", "std::wint_t towctrans(std::wint_t wc, std::wctrans_t desc);", [("wc", "wint_t", "変換するワイド文字"), ("desc", "wctrans_t", "`wctrans` で取った変換")], "変換した文字", 'std::println("{}", static_cast<char>(std::towctrans(L\'a\', std::wctrans("toupper"))));', "A")]:
    Q(WC + nm + ".md", "std::" + nm, summ, "rare", ["cwctype", "print"], intro, ["`<cwctype>` の部品。", "ロケールに依存する。", "ふつうは `iswalpha` などの固定の関数を使う。"], sig, args, ret, body, out,
      use="実行時に分類・変換を選ぶ", miss=("名前を間違える", "名前が不正だと 0 が返ります。0 を確かめてから使います。"), sim=[("[`iswalpha`](iswalpha.md)", "固定の分類の関数")], cx="定数", ver=("11", "C++11"), info=WCI, rj=f"cwctype/{nm}.html", cr=f"string/wide/{nm}", group="<cwctype> のワイド文字の判定・変換")

if __name__ == "__main__":
    run(sys.argv[1:])
    flush_hubs()
