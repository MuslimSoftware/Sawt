fn main() {
    // Tell the linker where to find the libraries
    println!("cargo:rustc-link-search=native=..");
    
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

    cc::Build::new()
        .cpp(true)
        .file("../whisper_backend.cpp")
        .include("../whisper_backend/include")
        .compile("whisper_backend");
}
