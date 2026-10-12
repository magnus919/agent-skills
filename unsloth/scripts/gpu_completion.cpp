// GPU-only greedy completion using llama.cpp's public API.
// API pattern: https://github.com/ggml-org/llama.cpp/blob/1acee6bf8939948f9bcbf4b14034e4b475f06069/examples/simple/simple.cpp
#include "llama.h"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

static int offloaded = 0, total_layers = 0;
static void logger(enum ggml_log_level, const char * text, void *) {
    std::fputs(text, stderr);
    const char * marker = std::strstr(text, "offloaded ");
    if (marker) std::sscanf(marker, "offloaded %d/%d", &offloaded, &total_layers);
}

int main(int argc, char ** argv) {
    if (argc != 4) {
        std::fprintf(stderr, "usage: gpu-completion MODEL.gguf PROMPT.txt MAX_NEW_TOKENS\n");
        return 2;
    }
    const int budget = std::stoi(argv[3]);
    if (budget < 1 || budget > 256) return 2;
    std::ifstream file(argv[2]);
    if (!file) return 2;
    const std::string prompt((std::istreambuf_iterator<char>(file)), {});
    llama_log_set(logger, nullptr);
    ggml_backend_load_all();
    if (!llama_supports_gpu_offload()) {
        std::fprintf(stderr, "GPU offload unavailable; CPU fallback forbidden\n");
        return 3;
    }
    auto mp = llama_model_default_params();
    mp.n_gpu_layers = 99;
    llama_model * model = llama_model_load_from_file(argv[1], mp);
    if (!model || offloaded <= 0 || offloaded != total_layers) {
        std::fprintf(stderr, "full GPU offload not observed; inference refused\n");
        if (model) llama_model_free(model);
        return 3;
    }
    const llama_vocab * vocab = llama_model_get_vocab(model);
    // Matched Qwen template supplies special tokens; do not insert another BOS.
    int n = -llama_tokenize(vocab, prompt.data(), prompt.size(), nullptr, 0, false, true);
    if (n <= 0 || n + budget > 256) return 2;
    std::vector<llama_token> tokens(n);
    if (llama_tokenize(vocab, prompt.data(), prompt.size(), tokens.data(), n, false, true) != n) return 2;
    std::fprintf(stderr, "smoke_prompt_ids:");
    for (auto t : tokens) std::fprintf(stderr, " %d", t);
    std::fprintf(stderr, "\n");
    auto cp = llama_context_default_params();
    cp.n_ctx = 256;
    cp.n_batch = n;
    cp.n_threads = 2;
    cp.n_threads_batch = 2;
    llama_context * ctx = llama_init_from_model(model, cp);
    if (!ctx) return 3;
    auto smpl = llama_sampler_init_greedy();
    auto batch = llama_batch_get_one(tokens.data(), n);
    bool terminated = false;
    for (int i = 0; i < budget; ++i) {
        if (llama_decode(ctx, batch)) return 3;
        llama_token token = llama_sampler_sample(smpl, ctx, -1);
        std::fprintf(stderr, "smoke_token: %d\n", token);
        if (llama_vocab_is_eog(vocab, token)) {
            std::fprintf(stderr, "smoke_eog: %d\n", token);
            terminated = true;
            break;
        }
        char buffer[256];
        int size = llama_token_to_piece(vocab, token, buffer, sizeof(buffer), 0, true);
        if (size < 0) return 3;
        std::fwrite(buffer, 1, size, stdout);
        std::fflush(stdout);
        batch = llama_batch_get_one(&token, 1);
        // Decode the next iteration while token remains alive in this scope.
        if (i + 1 < budget) {
            // Keep the token backing the next batch alive beyond this iteration.
            tokens.assign(1, token);
            batch = llama_batch_get_one(tokens.data(), 1);
        }
    }
    llama_perf_context_print(ctx);
    llama_sampler_free(smpl);
    llama_free(ctx);
    llama_model_free(model);
    return terminated ? 0 : 4;
}
