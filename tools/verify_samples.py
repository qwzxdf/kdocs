"""docs のサンプル コードを、手元の MSVC でビルド・実行して、「実行結果」と照合する。

対象: ```cpp のコード ブロックのうち、`int main` を含み、直後に ```text title="実行結果..." が続くもの。
使い方:
  python tools/verify_samples.py docs/stl/numeric/gcd.md            指定したファイル(フォルダーも可)
  python tools/verify_samples.py --since 3b3eb89                    その版から変わった md 全部
  python tools/verify_samples.py --since 3b3eb89 --jobs 6           並列数
  python tools/verify_samples.py docs/stl --report out.txt          結果をファイルにも書く
標準ヘッダーだけのサンプルが対象。標準以外のヘッダーを使うものは「スキップ」と数える。
MSVC は /std:c++latest /EHsc /utf-8 /W3。警告は無視して、結果の一致だけを見る。
"""
import argparse
import shutil
import concurrent.futures
import hashlib
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VCVARS = r'C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'

STD_HEADERS = set('''
algorithm any array atomic barrier bit bitset charconv chrono cinttypes climits clocale cmath codecvt compare complex concepts condition_variable
coroutine csetjmp csignal cstdarg cstddef cstdint cstdio cstdlib cstring ctime cuchar cwchar cwctype deque exception execution expected
filesystem flat_map flat_set format forward_list fstream functional future generator initializer_list iomanip ios iosfwd iostream istream
iterator latch limits list locale map mdspan memory memory_resource mutex new numbers numeric optional ostream print queue random ranges
ratio regex scoped_allocator semaphore set shared_mutex source_location span spanstream sstream stack stacktrace stdexcept stdfloat text_encoding
stop_token streambuf string string_view strstream syncstream system_error thread tuple type_traits typeindex typeinfo unordered_map
unordered_set utility valarray variant vector version cfenv cctype cerrno cfloat cassert
'''.split())

SAMPLE = re.compile(r'```cpp\n((?:(?!```).)*?)```[ \t]*\n+```text title="実行結果[^"]*"\n((?:(?!```).)*?)```', re.S)


def vc_env():
    out = subprocess.run(f'cmd /c ""{VCVARS}" >nul && set"', capture_output=True, text=True, shell=True, encoding='mbcs', errors='replace').stdout
    env = {}
    for ln in out.splitlines():
        if '=' in ln:
            k, v = ln.split('=', 1)
            env[k] = v
    return env


def md_files(args, since):
    files = []
    if since:
        out = subprocess.run(['git', 'diff', '--name-only', since, 'HEAD', '--', 'docs'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout
        files = [os.path.join(ROOT, p) for p in out.split('\n') if p.endswith('.md')]
    for a in args:
        a = os.path.abspath(a)
        if os.path.isdir(a):
            for d, _, fs in os.walk(a):
                files += [os.path.join(d, f) for f in fs if f.endswith('.md')]
        else:
            files.append(a)
    return sorted(set(f for f in files if os.path.exists(f)))


def includes(code):
    return re.findall(r'#\s*include\s*[<"]([^>"]+)[>"]', code)


def run_one(job):
    path, idx, code, expected, env, workdir = job
    rel = os.path.relpath(path, ROOT).replace('\\', '/')
    inc = includes(code)
    if any(i not in STD_HEADERS for i in inc):
        return rel, idx, 'skip', '標準以外のヘッダー'
    if 'windows.h' in code:
        return rel, idx, 'skip', 'windows.h'
    key = hashlib.md5((rel + str(idx)).encode()).hexdigest()[:10]
    d = os.path.join(workdir, key)
    os.makedirs(d, exist_ok=True)
    src = os.path.join(d, 's.cpp')
    exe = os.path.join(d, 's.exe')
    with open(src, 'w', encoding='utf-8', newline='\n') as f:
        f.write(code)
    cl = shutil.which('cl.exe', path=env.get('Path') or env.get('PATH'))
    cp = subprocess.run([cl, '/nologo', '/std:c++latest', '/EHsc', '/utf-8', '/W3', '/Fo' + d + '\\', '/Fe' + exe, src],
                        capture_output=True, env=env, cwd=d, timeout=300)
    if cp.returncode != 0 or not os.path.exists(exe):
        msg = cp.stdout.decode('mbcs', 'replace')
        errs = [l for l in msg.splitlines() if 'error' in l.lower()][:3]
        return rel, idx, 'compile', ' / '.join(errs) or msg[:200]
    try:
        rp = subprocess.run([exe], capture_output=True, cwd=d, timeout=20, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return rel, idx, 'timeout', ''
    got = rp.stdout.decode('utf-8', 'replace').replace('\r\n', '\n').rstrip()
    want = expected.replace('\r\n', '\n').rstrip()
    if got == want:
        return rel, idx, 'ok', ''
    return rel, idx, 'diff', 'expected=%r got=%r' % (want[:300], got[:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--since')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--report')
    a = ap.parse_args()
    files = md_files(a.paths, a.since)
    env = vc_env()
    work = tempfile.mkdtemp(prefix='kdocs_verify_')
    jobs = []
    for p in files:
        s = open(p, encoding='utf-8').read()
        blocks = [(m.start(), m.group(1)) for m in re.finditer(r'```cpp\n((?:(?!```).)*?)```', s, re.S)]
        for i, m in enumerate(SAMPLE.finditer(s)):
            code, exp = m.group(1), m.group(2)
            if 'int main' in code:
                if '#include' not in code:
                    # 解説のために分けた続きのコード: 直前の #include があるブロックから連結する
                    prev = [b for b in blocks if b[0] < m.start()]
                    j = max((k for k, b in enumerate(prev) if '#include' in b[1] and 'int main' not in b[1]), default=None)
                    if j is not None:
                        code = '\n'.join(b[1] for b in prev[j:] if 'int main' not in b[1]) + '\n' + code
                jobs.append((p, i, code, exp, env, work))
    print('files', len(files), 'samples', len(jobs), flush=True)
    stats = {}
    lines = []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for rel, idx, st, info in ex.map(run_one, jobs):
            stats[st] = stats.get(st, 0) + 1
            if st not in ('ok', 'skip'):
                lines.append('%s #%d %s %s' % (rel, idx, st, info))
                print(lines[-1], flush=True)
    print(stats)
    if a.report:
        with open(a.report, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n' + str(stats) + '\n')


if __name__ == '__main__':
    sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)
    main()
