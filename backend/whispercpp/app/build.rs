fn main() {
    // Use the standard library path for Docker builds
    println!("cargo:rustc-link-search=native=/usr/local/lib");
    
    // Runtime shared libs first
    println!("cargo:rustc-link-lib=dylib=gomp");
    println!("cargo:rustc-link-lib=dylib=openblas");
    
    // GGML libraries (must be linked before whisper)
    println!("cargo:rustc-link-lib=dylib=ggml");
    println!("cargo:rustc-link-lib=dylib=ggml-base");
    println!("cargo:rustc-link-lib=dylib=ggml-cpu");
    
    // Whisper shared library
    println!("cargo:rustc-link-lib=dylib=whisper");
}
