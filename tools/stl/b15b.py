"""バッチ 15 の補足: snprintf のページ。"""
from b15 import F  # noqa: F401

F("snprintf", "書式を指定して、大きさを決めた文字配列に書き込む（あふれない）。", "`sprintf` は配列の大きさを確かめないため、あふれる危険があります。`snprintf` は、書き込む最大のバイト数を指定でき、あふれた分は切り捨てて、必ず終端文字を付けます。戻り値は「切り捨てなければ書けたはずの長さ」なので、`nullptr` と 0 を渡して、必要な大きさを先に調べる使い方もできます。", "int snprintf(char* buffer, std::size_t bufsz, const char* format, ...);",
  [("buffer", "char*", "書き込み先（`nullptr` も可）"), ("bufsz", "size_t", "書き込める最大のバイト数（終端を含む）"), ("format", "const char*", "書式文字列")], "書けたはずの文字数（終端を除く）", 'char buf[8];\nint n = std::snprintf(buf, sizeof buf, "%d-%s", 12, "abcdefgh");\nstd::println("{} {}", buf, n);', "12-abcd 11",
  "固定長のバッファに、安全に文字列を組み立てる", ("戻り値を書き込んだ長さと思う", "戻り値は、切り捨てがなかった場合の長さです。`n >= bufsz` なら、切り捨てられています。"), [("[`sprintf`](sprintf.md)", "大きさを確かめない"), ("[`std::format_to_n`](../../utilities/format_to.md)", "型安全な書き方")], inc=("cstdio", "print"), ver=("11", "C++11"))

if __name__ == "__main__":
    flush_hubs()
