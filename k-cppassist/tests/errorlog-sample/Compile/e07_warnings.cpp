// 警告(/W4)。エラーも少し混ぜてある
#include <cstdio>
#include <cstring>
#include <vector>

int NoReturn(int x) {
  if (x > 0) return 1;
}                                        // C4715: 値を返さないパスがある

void Warnings() {
  int unused;                            // C4101: 未使用のローカル変数
  double d = 3.14;
  int i = d;                             // C4244: double から int
  long long big = 1LL << 40;
  int small = big;                       // C4244: 縮小変換
  std::vector<int> v;
  int n = v.size();                      // C4267: size_t から int
  char buf[4];
  strcpy(buf, "abc");                    // C4996: 安全でない関数
  int x = 5;
  if (x = 3) {}                          // C4706: 条件内の代入
  printf("%d\n");                        // 書式の引数不足
  printf("%s\n", 42);                    // 書式の型不一致
  (void)i; (void)small; (void)n;
}

void Shadow(int a) {
  int a = 2;                             // C2082: 引数の再定義(エラー)
  for (int i = 0; i < 2; ++i) {
    int i = 5;                           // C4456: 外側を隠す
  }
}
