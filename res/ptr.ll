define i32 @main() {
  %2 = alloca i32          ; int x
  %3 = alloca i32*         ; int * ptr
  store i32 0, i32* %2     ; x = 0
  store i32* %2, i32** %3  ; ptr = &x
  ret i32 0
}
