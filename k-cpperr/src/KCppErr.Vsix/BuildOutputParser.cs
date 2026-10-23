using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppErr
{
    /// <summary>ビルド出力の 1 行の診断(場所つきの error / warning / note / message)。</summary>
    public sealed class Frame
    {
        public string File = "";
        public int Line;
        public int Col;
        public string Severity = "";
        public string Code = "";
        public string Message = "";
        /// <summary>この診断のあとに続く、インデントされた補足行("with" や "[ _Ty=int ]" など)。</summary>
        public List<string> Details = new List<string>();

        public bool HasLocation { get { return File.Length > 0 && Line > 0; } }

        public string Location
        {
            get
            {
                if (!HasLocation) return File;
                return Col > 0 ? File + "(" + Line + "," + Col + ")" : File + "(" + Line + ")";
            }
        }

        public FrameKind Kind
        {
            get
            {
                string m = Message.TrimStart();
                if (m.StartsWith("see reference to", StringComparison.OrdinalIgnoreCase)
                    || m.StartsWith("参照", StringComparison.Ordinal)
                    || m.StartsWith("required from", StringComparison.OrdinalIgnoreCase)
                    || m.StartsWith("in instantiation of", StringComparison.OrdinalIgnoreCase))
                    return FrameKind.Trace;
                if (m.StartsWith("could be", StringComparison.OrdinalIgnoreCase)
                    || m.StartsWith("or ", StringComparison.OrdinalIgnoreCase)
                    || m.StartsWith("candidate", StringComparison.OrdinalIgnoreCase)
                    || m.StartsWith("'", StringComparison.Ordinal) && m.Contains("' を使用できます")
                    || m.Contains("可能性があります"))
                    return FrameKind.Candidate;
                return FrameKind.Other;
            }
        }
    }

    public enum FrameKind { Trace, Candidate, Other }

    /// <summary>1 つのエラー(または警告)と、それに続く補足の診断。</summary>
    public sealed class ErrorGroup
    {
        public Frame Primary;
        public List<Frame> Frames = new List<Frame>();
        public List<string> Raw = new List<string>();

        public bool IsError { get { return Primary.Severity != "warning"; } }
    }

    public static class BuildOutputParser
    {
        // MSVC: C:\path\file.cpp(12,5): error C2664: メッセージ
        // 場所は "(行[,列])" で、パスにも括弧がある(Program Files (x86))ので、ファイル部分は最短一致にする。
        private static readonly Regex Msvc = new Regex(
            @"^(?<file>.+?)\((?<line>\d+)(?:,(?<col>\d+))?\)\s*:\s*(?<sev>fatal error|error|warning|note|message)\b\s*(?<code>[A-Za-z]{1,4}\d{3,5})?\s*:?\s*(?<msg>.*)$",
            RegexOptions.Compiled);

        // リンカーなど、行番号のない診断: LINK : fatal error LNK1104: ... / foo.obj : error LNK2019: ...
        private static readonly Regex NoLine = new Regex(
            @"^(?<file>.+?)\s:\s*(?<sev>fatal error|error|warning)\s+(?<code>[A-Za-z]{1,4}\d{3,5})\s*:\s*(?<msg>.*)$",
            RegexOptions.Compiled);

        // GCC / Clang: /path/file.cpp:12:5: error: メッセージ
        private static readonly Regex Gcc = new Regex(
            @"^(?<file>(?:[A-Za-z]:)?[^:]+):(?<line>\d+):(?:(?<col>\d+):)?\s*(?<sev>fatal error|error|warning|note):\s*(?<msg>.*)$",
            RegexOptions.Compiled);

        private static readonly Regex GccTrace = new Regex(
            @"^(?<file>(?:[A-Za-z]:)?[^:]+):(?<line>\d+):(?:(?<col>\d+):)?\s+(?<msg>(?:required from|in instantiation of).*)$",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        private static readonly Regex Prefix = new Regex(@"^\s*\d+>", RegexOptions.Compiled);

        public static List<ErrorGroup> Parse(string text)
        {
            var result = new List<ErrorGroup>();
            if (string.IsNullOrEmpty(text)) return result;

            var seen = new HashSet<string>();
            ErrorGroup current = null;
            Frame last = null;
            bool skipping = false;

            foreach (string rawLine in text.Split('\n'))
            {
                string line = Prefix.Replace(rawLine.TrimEnd('\r', ' ', '\t'), "");
                Frame f = ParseLine(line);
                if (f != null)
                {
                    bool primary = f.Severity == "error" || f.Severity == "fatal error" || f.Severity == "warning";
                    if (primary)
                    {
                        string key = f.File + "|" + f.Line + "|" + f.Col + "|" + f.Code + "|" + f.Message;
                        skipping = !seen.Add(key);
                        if (skipping) { current = null; last = null; continue; }
                        current = new ErrorGroup { Primary = f };
                        current.Raw.Add(line);
                        result.Add(current);
                        last = f;
                    }
                    else if (current != null && !skipping)
                    {
                        current.Frames.Add(f);
                        current.Raw.Add(line);
                        last = f;
                    }
                    continue;
                }

                if (current != null && !skipping && line.Length > 0 && char.IsWhiteSpace(line[0]) && line.Trim().Length > 0)
                {
                    current.Raw.Add(line);
                    if (last != null) last.Details.Add(line.Trim());
                    continue;
                }

                // インデントのない普通の行(「Main.cpp」「Generating Code...」など)でグループを閉じる
                current = null;
                last = null;
                skipping = false;
            }
            return result;
        }

        private static Frame ParseLine(string line)
        {
            if (line.Length == 0) return null;
            Match m = Msvc.Match(line);
            if (m.Success) return Make(m, true);
            m = NoLine.Match(line);
            if (m.Success) return Make(m, false);
            m = GccTrace.Match(line);
            if (m.Success)
            {
                var t = Make(m, true);
                t.Severity = "note";
                return t;
            }
            m = Gcc.Match(line);
            if (m.Success) return Make(m, true);
            return null;
        }

        private static Frame Make(Match m, bool hasLine)
        {
            var f = new Frame
            {
                File = m.Groups["file"].Value.Trim(),
                Severity = m.Groups["sev"].Success ? m.Groups["sev"].Value : "note",
                Code = m.Groups["code"].Success ? m.Groups["code"].Value : "",
                Message = m.Groups["msg"].Value.Trim()
            };
            if (hasLine)
            {
                int line, col;
                if (int.TryParse(m.Groups["line"].Value, out line)) f.Line = line;
                if (m.Groups["col"].Success && int.TryParse(m.Groups["col"].Value, out col)) f.Col = col;
            }
            if (f.Severity == "message") f.Severity = "note";
            return f;
        }
    }
}
