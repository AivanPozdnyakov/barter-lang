int x = 1;
float y = 2.0;
float res = x + y;
float x_floated = (float)x;
int y_inted = (int)y;
bool f = bool(x);
short s = 32;
float c = float(s);

define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca float, align 4
  %3 = alloca float, align 4
  %4 = alloca float, align 4
  %5 = alloca i32, align 4
  %6 = alloca i8, align 1
  %7 = alloca i16, align 2
  %8 = alloca float, align 4
  store i32 1, i32* %1, align 4
  store float 2.000000e+00, float* %2, align 4
  %9 = load i32, i32* %1, align 4
  %10 = sitofp i32 %9 to float
  %11 = load float, float* %2, align 4
  %12 = fadd float %10, %11
  store float %12, float* %3, align 4
  %13 = load i32, i32* %1, align 4
  %14 = sitofp i32 %13 to float
  store float %14, float* %4, align 4
  %15 = load float, float* %2, align 4
  %16 = fptosi float %15 to i32
  store i32 %16, i32* %5, align 4
  %17 = load i32, i32* %1, align 4
  %18 = icmp ne i32 %17, 0
  %19 = zext i1 %18 to i8
  store i8 %19, i8* %6, align 1
  store i16 32, i16* %7, align 2
  %20 = load i16, i16* %7, align 2
  %21 = sitofp i16 %20 to float
  store float %21, float* %8, align 4
  ret i32 0
}
