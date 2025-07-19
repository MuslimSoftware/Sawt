#include "whisper.h"
#include <string>
#include <memory>
#include <cstring>

// Simple global context for the current model
static whisper_context* g_ctx = nullptr;
static std::string g_current_model_path;

extern "C" {

const char* whisper_transcribe(const char* model_path, const float* audio_data, size_t num_samples) {
    // Initialize context if needed or if model path changed
    if (!g_ctx || g_current_model_path != model_path) {
        // Clean up previous context
        if (g_ctx) {
            whisper_free(g_ctx);
            g_ctx = nullptr;
        }
        
        // Initialize new context with basic parameters
        g_ctx = whisper_init_from_file(model_path);
        if (!g_ctx) {
            return nullptr;
        }
        
        g_current_model_path = model_path;
    }
    
    // Use basic whisper_full with minimal parameters
    whisper_full_params wparams = {};
    wparams.strategy = WHISPER_SAMPLING_GREEDY;
    wparams.print_progress = false;
    wparams.print_special = false;
    wparams.print_timestamps = false;
    wparams.language = "en";
    wparams.n_threads = 4;
    
    // Run transcription
    if (whisper_full(g_ctx, wparams, audio_data, num_samples) != 0) {
        return nullptr;
    }
    
    // Get the result
    const int n_segments = whisper_full_n_segments(g_ctx);
    if (n_segments == 0) {
        return nullptr;
    }
    
    // Concatenate all segments
    std::string result;
    for (int i = 0; i < n_segments; ++i) {
        const char* text = whisper_full_get_segment_text(g_ctx, i);
        if (text) {
            result += text;
            result += " ";
        }
    }
    
    // Return a copy of the result (caller is responsible for freeing)
    char* result_copy = new char[result.length() + 1];
    strcpy(result_copy, result.c_str());
    return result_copy;
}

void whisper_free_result(const char* ptr) {
    if (ptr) {
        delete[] ptr;
    }
}

void whisper_cleanup() {
    if (g_ctx) {
        whisper_free(g_ctx);
        g_ctx = nullptr;
    }
    g_current_model_path.clear();
}

} 