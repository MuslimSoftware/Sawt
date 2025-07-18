fn main() {
    // Tell the linker where to find the libraries
    println!("cargo:rustc-link-search=native=../interface/artifacts");
    
    // Link against all required libraries in the correct order
    println!("cargo:rustc-link-lib=static=whisper");
    println!("cargo:rustc-link-lib=static=ggml");
    println!("cargo:rustc-link-lib=static=ggml-base");
    println!("cargo:rustc-link-lib=static=ggml-cpu");
    println!("cargo:rustc-link-lib=static=ggml-blas");
    println!("cargo:rustc-link-lib=static=ggml-metal");
    
    // Link against system frameworks (required on macOS)
    println!("cargo:rustc-link-lib=framework=Accelerate");
    println!("cargo:rustc-link-lib=framework=Metal");
    println!("cargo:rustc-link-lib=framework=MetalKit");
    println!("cargo:rustc-link-lib=framework=Foundation");

    // Set optimization flags for C++ compilation
    let mut build = cc::Build::new();
    build.cpp(true)
        .file("../interface/wrapper.cpp")
        .include("../interface/headers/include");
    
    // Add optimization flags (only in release mode to avoid conflicts)
    if cfg!(debug_assertions) == false {
        build.flag("-O3")
             .flag("-ffast-math");
    }
    
    build.compile("whisper_backend");
}
