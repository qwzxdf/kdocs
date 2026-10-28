using System;
using System.Collections.Generic;
using System.Text;

namespace KHlsl.Server
{
    /// <summary>
    /// HLSL の整形。字下げと、足りない空白の補いだけをする(改行の位置は変えない・空白は詰めない)。
    /// 言語サーバーの textDocument/formatting と、VS 拡張の SmartIndent が同じ物を使う。
    /// </summary>
    internal static class HlslFormatter
    {
        private enum K { Word, Num, Str, Punct, LineCom, BlockCom, Pre }

        private sealed class Tok
        {
            public K Kind;
            public string Text;
            public int Line, Col;
            public int EndLine;          // 複数行のブロック コメント・プリプロセッサの最後の行
            public string Ws = "";       // 同じ行で、直前の物との間の空白
            public bool First;           // その行で最初の物(ブロック コメントの途中から始まる行は false)
            public bool Binary;          // 二項演算子の + - * / %
            public int Index;
        }

        /// <summary>{ } の内側。字下げと、文の状態を持つ。</summary>
        private sealed class Blk
        {
            public int Open;             // } の字下げ(列)
            public int Content;          // 中身の字下げ
            public int P;                // 本体を待っている if / for / else / do の数
            public bool Stmt;            // 文の途中か
            public int StmtLevel;        // いまの文の字下げ
            public bool Label;           // case / default / public: の途中か
            public bool Root;
        }

        /// <summary>( ) [ ] と、式の中の { }。</summary>
        private sealed class Brk
        {
            public char Ch;
            public int LineIndent;       // 開き括弧のある行の字下げ
            public int Align = -1;       // 開き括弧の後ろに続きがあれば、その列
            public bool Control;         // if / for / while / switch の ( )
            public bool StmtStart;       // 文の先頭の [ ](属性)
        }

        private static readonly HashSet<string> Controls = new HashSet<string> { "if", "for", "while", "switch" };
        private static readonly HashSet<string> NotOperand = new HashSet<string> { "return", "case", "else", "do", "in", "out", "inout", "typedef", "if", "while", "for", "switch" };
        private static readonly HashSet<string> Assign = new HashSet<string>
        {
            "=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "==", "!=", "<=", ">=", "&&", "||"
        };
        private static readonly string[] Puncts =
        {
            "<<=", ">>=", "...", "->", "++", "--", "<<", ">>", "<=", ">=", "==", "!=", "&&", "||",
            "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "::"
        };

        // ---- 公開 ----
        public static string[] SplitLines(string text)
        {
            var lines = text.Split('\n');
            for (int i = 0; i < lines.Length; i++)
                if (lines[i].EndsWith("\r")) lines[i] = lines[i].Substring(0, lines[i].Length - 1);
            return lines;
        }

        /// <summary>行数を変えずに、整形した行を返す。</summary>
        public static string[] Format(string[] lines, int tabSize, bool insertSpaces)
        {
            return new Engine(lines, Math.Max(1, tabSize), insertSpaces).Run();
        }

        /// <summary>textBefore(最後が改行)の次の行に、改行で入るときの字下げ(列)。</summary>
        public static int IndentForNewLine(string textBefore, int tabSize)
        {
            var lines = SplitLines(textBefore + "x");
            var res = Format(lines, tabSize, true);
            string last = res[res.Length - 1];
            return VisualWidth(last.Substring(0, last.Length - last.TrimStart().Length), tabSize);
        }

        private static int VisualWidth(string s, int tab)
        {
            int col = 0;
            foreach (char c in s) col = c == '\t' ? (col / tab + 1) * tab : col + 1;
            return col;
        }

        // ---- 字句 ----
        private static List<Tok> Lex(string[] lines)
        {
            var res = new List<Tok>();
            Tok open = null;             // 閉じていないブロック コメント
            Tok pre = null;              // 次の行へ続くプリプロセッサ
            for (int li = 0; li < lines.Length; li++)
            {
                string s = lines[li];
                if (pre != null)
                {
                    pre.EndLine = li;
                    if (!s.TrimEnd().EndsWith("\\")) pre = null;
                    continue;
                }
                int i = 0;
                bool any = false;
                if (open != null)
                {
                    int e = s.IndexOf("*/", StringComparison.Ordinal);
                    open.EndLine = li;
                    if (e < 0) continue;
                    open = null;
                    i = e + 2;
                    any = true;
                }
                int prevEnd = i;
                while (i < s.Length)
                {
                    char c = s[i];
                    if (c == ' ' || c == '\t' || c == '\r') { i++; continue; }
                    var t = new Tok { Line = li, EndLine = li, Col = i, Ws = s.Substring(prevEnd, i - prevEnd), First = !any, Index = res.Count };
                    any = true;
                    int end;
                    if (c == '#' && t.First)
                    {
                        t.Kind = K.Pre; t.Text = s.Substring(i); end = s.Length;
                        if (s.TrimEnd().EndsWith("\\")) pre = t;
                    }
                    else if (c == '/' && i + 1 < s.Length && s[i + 1] == '/')
                    {
                        t.Kind = K.LineCom; t.Text = s.Substring(i); end = s.Length;
                    }
                    else if (c == '/' && i + 1 < s.Length && s[i + 1] == '*')
                    {
                        t.Kind = K.BlockCom;
                        int e = s.IndexOf("*/", i + 2, StringComparison.Ordinal);
                        if (e < 0) { t.Text = s.Substring(i); end = s.Length; open = t; }
                        else { end = e + 2; t.Text = s.Substring(i, end - i); }
                    }
                    else if (c == '"' || c == '\'')
                    {
                        int j = i + 1;
                        while (j < s.Length && s[j] != c) j += s[j] == '\\' ? 2 : 1;
                        end = Math.Min(s.Length, j + 1);
                        t.Kind = K.Str; t.Text = s.Substring(i, end - i);
                    }
                    else if (char.IsLetter(c) || c == '_')
                    {
                        int j = i + 1;
                        while (j < s.Length && (char.IsLetterOrDigit(s[j]) || s[j] == '_')) j++;
                        end = j; t.Kind = K.Word; t.Text = s.Substring(i, j - i);
                    }
                    else if (char.IsDigit(c) || (c == '.' && i + 1 < s.Length && char.IsDigit(s[i + 1])))
                    {
                        int j = i + 1;
                        bool hex = c == '0' && j < s.Length && (s[j] == 'x' || s[j] == 'X');
                        while (j < s.Length)
                        {
                            char d = s[j];
                            if (char.IsLetterOrDigit(d) || d == '_' || d == '.') j++;
                            else if ((d == '+' || d == '-') && !hex && (s[j - 1] == 'e' || s[j - 1] == 'E')) j++;
                            else break;
                        }
                        end = j; t.Kind = K.Num; t.Text = s.Substring(i, j - i);
                    }
                    else
                    {
                        int len = 1;
                        foreach (var p in Puncts)
                            if (string.CompareOrdinal(s, i, p, 0, p.Length) == 0) { len = p.Length; break; }
                        end = i + len; t.Kind = K.Punct; t.Text = s.Substring(i, len);
                    }
                    res.Add(t);
                    prevEnd = i = end;
                }
            }
            return res;
        }

        private static bool IsComment(Tok t) { return t.Kind == K.LineCom || t.Kind == K.BlockCom || t.Kind == K.Pre; }

        private static void MarkBinary(List<Tok> toks)
        {
            Tok prev = null;
            var parens = new List<bool>();   // ( の中が、if / for / while / switch の条件か
            int control = 0;
            foreach (var t in toks)
            {
                if (IsComment(t)) continue;
                if (t.Kind == K.Punct && t.Text == "(")
                {
                    bool c = prev != null && prev.Kind == K.Word && Controls.Contains(prev.Text);
                    parens.Add(c);
                    if (c) control++;
                }
                else if (t.Kind == K.Punct && t.Text == ")" && parens.Count > 0)
                {
                    if (parens[parens.Count - 1]) control--;
                    parens.RemoveAt(parens.Count - 1);
                }
                bool arith = t.Kind == K.Punct && (t.Text == "+" || t.Text == "-" || t.Text == "*" || t.Text == "/" || t.Text == "%");
                // < > は、型の引数(Texture2D<float4>)と区別できないので、条件式の中だけ比較として扱う
                bool compare = t.Kind == K.Punct && (t.Text == "<" || t.Text == ">") && control > 0;
                if ((arith || compare) && prev != null)
                {
                    bool operand = prev.Kind == K.Num || prev.Kind == K.Str
                        || (prev.Kind == K.Word && !NotOperand.Contains(prev.Text))
                        || (prev.Kind == K.Punct && (prev.Text == ")" || prev.Text == "]"));
                    t.Binary = operand;
                }
                prev = t;
            }
        }

        // ---- 整形 ----
        private sealed class Engine
        {
            private readonly string[] _lines;
            private readonly int _tab;
            private readonly bool _spaces;
            private readonly int _unit;
            private readonly List<Tok> _toks;
            private readonly List<Tok>[] _byLine;
            private readonly List<object> _stack = new List<object>();

            private int _lineIndent;     // いま出力している行の字下げ
            private int _delta;          // ブロック コメントの途中の行を動かす量
            private StringBuilder _sb;
            private bool _emit;

            public Engine(string[] lines, int tab, bool spaces)
            {
                _lines = lines; _tab = tab; _spaces = spaces; _unit = tab;
                _toks = Lex(lines);
                MarkBinary(_toks);
                _byLine = new List<Tok>[lines.Length];
                for (int i = 0; i < lines.Length; i++) _byLine[i] = new List<Tok>();
                foreach (var t in _toks) _byLine[t.Line].Add(t);
                _stack.Add(new Blk { Root = true });
            }

            private object Top { get { return _stack[_stack.Count - 1]; } }

            private Blk NearestBlk()
            {
                for (int i = _stack.Count - 1; i >= 0; i--)
                    if (_stack[i] is Blk) return (Blk)_stack[i];
                return null;
            }

            private string Indent(int cols)
            {
                if (cols <= 0) return "";
                if (_spaces) return new string(' ', cols);
                return new string('\t', cols / _tab) + new string(' ', cols % _tab);
            }

            private int Width(string s) { return VisualWidth(s, _tab); }

            public string[] Run()
            {
                var res = new string[_lines.Length];
                Tok block = null;        // 前の行から続くブロック コメント
                for (int li = 0; li < _lines.Length; li++)
                {
                    string s = _lines[li];
                    var list = _byLine[li];
                    if (s.Trim().Length == 0 && list.Count == 0 && block == null) { res[li] = ""; continue; }
                    if (list.Count > 0 && list[0].Kind == K.Pre) { res[li] = s.TrimEnd(); continue; }
                    if (list.Count == 0 && block == null)
                    {
                        // プリプロセッサの続きの行
                        res[li] = s.TrimEnd();
                        continue;
                    }

                    _emit = block == null;
                    _sb = new StringBuilder();
                    if (block != null)
                    {
                        // 前から続くブロック コメントの中。元の字下げに、先頭の行が動いた量を足す
                        string lead = s.Substring(0, s.Length - s.TrimStart().Length);
                        string body = s.TrimStart();
                        res[li] = body.Length == 0 ? "" : Indent(Math.Max(0, Width(lead) + _delta)) + body;
                        _lineIndent = Math.Max(0, Width(lead) + _delta);
                        if (list.Count == 0 || block.EndLine != li) { if (block.EndLine <= li) block = null; res[li] = res[li].TrimEnd(); continue; }
                        block = null;
                    }

                    Tok prev = null;
                    for (int k = 0; k < list.Count; k++)
                    {
                        var t = list[k];
                        if (_emit)
                        {
                            if (t.First)
                            {
                                _lineIndent = Math.Max(0, ComputeIndent(t));
                                _sb.Append(Indent(_lineIndent));
                            }
                            else
                            {
                                string ws = t.Ws;
                                if (ws.Length == 0 && NeedSpace(prev, t)) ws = " ";
                                _sb.Append(ws);
                            }
                        }
                        int col = _emit ? Width(_sb.ToString()) : Width(s.Substring(0, t.Col)) + _delta;
                        if (_emit) _sb.Append(t.Text);
                        Update(t, col, k + 1 < list.Count ? list[k + 1] : null);
                        if (t.Kind == K.BlockCom && t.EndLine > t.Line)
                        {
                            block = t;
                            _delta = col - Width(s.Substring(0, t.Col));
                        }
                        prev = t;
                    }
                    if (_emit) res[li] = _sb.ToString().TrimEnd();
                    else res[li] = res[li];
                }
                return res;
            }

            private static bool NeedSpace(Tok prev, Tok cur)
            {
                if (prev == null || IsComment(cur)) return false;
                string p = prev.Text, c = cur.Text;
                if (prev.Kind == K.Word && Controls.Contains(p) && c == "(") return true;
                if (p == "," && c != ")" && c != "]" && c != "}" && c != ",") return true;
                if (p == ";" && c != ";" && c != ")") return true;
                if (cur.Kind == K.Punct && Assign.Contains(c)) return true;
                if (prev.Kind == K.Punct && Assign.Contains(p)) return true;
                if (cur.Binary || prev.Binary) return true;
                return false;
            }

            private Tok PrevSig(Tok t)
            {
                for (int i = t.Index - 1; i >= 0; i--)
                    if (!IsComment(_toks[i])) return _toks[i];
                return null;
            }

            private Tok NextSig(Tok t)
            {
                for (int i = t.Index + 1; i < _toks.Count; i++)
                    if (!IsComment(_toks[i])) return _toks[i];
                return null;
            }

            private bool IsLabelStart(Tok t)
            {
                if (t.Kind != K.Word) return false;
                if (t.Text == "case") return true;
                if (t.Text == "default" || t.Text == "public" || t.Text == "private" || t.Text == "protected")
                {
                    var n = NextSig(t);
                    return n != null && n.Text == ":";
                }
                return false;
            }

            private static bool IsCloser(Tok t) { return t.Kind == K.Punct && (t.Text == ")" || t.Text == "]" || t.Text == "}"); }

            /// <summary>行の最初の物 t の字下げ。</summary>
            private int ComputeIndent(Tok t)
            {
                bool closer = IsCloser(t);
                var top = Top;
                if (t.Kind == K.Punct && t.Text == "}")
                {
                    // 式の中の { } は、開いた行に揃える
                    for (int i = _stack.Count - 1; i >= 0; i--)
                    {
                        var kb = _stack[i] as Brk;
                        if (kb != null && kb.Ch == '{') return kb.LineIndent;
                        if (_stack[i] is Blk) return ((Blk)_stack[i]).Root ? 0 : ((Blk)_stack[i]).Open;
                    }
                    return 0;
                }
                var k = top as Brk;
                if (k != null)
                {
                    if (closer && ((t.Text == ")" && k.Ch == '(') || (t.Text == "]" && k.Ch == '['))) return k.LineIndent;
                    return k.Align >= 0 ? k.Align : k.LineIndent + _unit;
                }
                var b = (Blk)top;
                if (t.Kind == K.Punct && t.Text == "{")
                    return b.Stmt ? b.StmtLevel : b.Content + Math.Max(b.P - 1, 0) * _unit;
                if (!b.Stmt && !b.Root && IsLabelStart(t)) return b.Open;
                if (!b.Stmt) return b.Content + b.P * _unit;
                return b.StmtLevel + _unit;
            }

            private void StartStatement(Blk b, Tok t)
            {
                b.Stmt = true;
                b.StmtLevel = (!b.Root && IsLabelStart(t)) ? b.Open : b.Content + b.P * _unit;
            }

            /// <summary>t を読んだあとの状態にする。col は t の(整形後の)列。</summary>
            private void Update(Tok t, int col, Tok nextOnLine)
            {
                if (IsComment(t)) return;
                string x = t.Text;
                var top = Top;
                if (t.Kind == K.Punct && (x == ")" || x == "]" || x == "}")) { Close(x); return; }
                if (t.Kind == K.Punct && (x == "(" || x == "[" || x == "{")) { Open(t, col, nextOnLine); return; }

                var b = top as Blk;
                if (b == null) return;
                if (t.Kind == K.Word && (x == "else" || x == "do") && !b.Stmt)
                {
                    b.P++;
                    return;
                }
                if (!b.Stmt)
                {
                    if (t.Kind == K.Word && x == "if")
                    {
                        var pv = PrevSig(t);
                        if (pv != null && pv.Text == "else" && b.P > 0) b.P--;
                    }
                    StartStatement(b, t);
                    if (IsLabelStart(t)) b.Label = true;
                }
                if (t.Kind == K.Punct)
                {
                    if (x == ";") { b.Stmt = false; b.P = 0; b.Label = false; }
                    else if (x == ":" && b.Label) { b.Stmt = false; b.P = 0; b.Label = false; }
                }
            }

            private void Open(Tok t, int col, Tok nextOnLine)
            {
                char c = t.Text[0];
                var top = Top;
                var b = top as Blk;
                bool expr = false;
                if (c == '{')
                {
                    var pv = PrevSig(t);
                    expr = b == null || (pv != null && pv.Text == "=");
                }
                if (c == '{' && !expr)
                {
                    int open = b.Stmt ? b.StmtLevel : b.Content + Math.Max(b.P - 1, 0) * _unit;
                    _stack.Add(new Blk { Open = open, Content = open + _unit });
                    return;
                }
                var k = new Brk { Ch = c, LineIndent = _lineIndent };
                if (nextOnLine != null && !IsComment(nextOnLine))
                    k.Align = col + 1 + nextOnLine.Ws.Length;
                if (b != null)
                {
                    if (c == '(')
                    {
                        var pv = PrevSig(t);
                        k.Control = pv != null && pv.Kind == K.Word && Controls.Contains(pv.Text);
                    }
                    if (!b.Stmt)
                    {
                        k.StmtStart = c == '[';
                        StartStatement(b, t);
                    }
                }
                _stack.Add(k);
            }

            private void Close(string x)
            {
                if (x == ")" || x == "]")
                {
                    char want = x == ")" ? '(' : '[';
                    int found = -1;
                    for (int i = _stack.Count - 1; i >= 0; i--)
                    {
                        if (_stack[i] is Blk) break;
                        if (((Brk)_stack[i]).Ch == want) { found = i; break; }
                    }
                    if (found < 0) return;
                    var k = (Brk)_stack[found];
                    _stack.RemoveRange(found, _stack.Count - found);
                    var b = Top as Blk;
                    if (b != null)
                    {
                        if (k.Control) { b.Stmt = false; b.P++; }
                        else if (k.StmtStart) b.Stmt = false;
                    }
                    return;
                }
                // }
                for (int i = _stack.Count - 1; i >= 0; i--)
                {
                    var kb = _stack[i] as Brk;
                    if (kb != null && kb.Ch == '{')
                    {
                        _stack.RemoveRange(i, _stack.Count - i);
                        return;
                    }
                    if (_stack[i] is Blk) break;
                }
                while (_stack.Count > 1 && !(Top is Blk)) _stack.RemoveAt(_stack.Count - 1);
                if (_stack.Count > 1)
                {
                    _stack.RemoveAt(_stack.Count - 1);
                    var p = NearestBlk();
                    p.Stmt = false; p.P = 0; p.Label = false;
                }
            }
        }
    }
}
