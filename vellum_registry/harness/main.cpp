// main.cpp - THE GENERIC HARNESS
//
// This file never changes. It is written once and compiled against whatever
// kernel the SLM produced.
//
//   generated/kernel.cpp   <- SLM writes ONLY this
//   harness/main.cpp       <- fixed, this file
//   harness/helpers.cpp    <- fixed, the allow-list implementations
//
// build:
//   g++ -std=c++14 -Iinclude generated/kernel.cpp harness/helpers.cpp \
//       harness/main.cpp -o run_block
//
// run:
//   ./run_block testdata/frames.json testdata/config.json

#include "contract.hpp"

#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------
// The SLM-written kernel. ONE of these signatures, chosen by the block's
// "frames" field in its json. The harness picks which to call at build time.
//
//   frames = 1  ->  BLOCK_FRAMES_1
//   frames = 2  ->  BLOCK_FRAMES_2
// ---------------------------------------------------------------------------

#if defined(BLOCK_FRAMES_2)
void stage_kernel(const SFrame &prev, const SFrame &curr,
                  const SBlockConfig &cfg, std::vector<SEvent> &out);
#else
void stage_kernel(const SFrame &curr,
                  const SBlockConfig &cfg, std::vector<SEvent> &out);
#endif

// ---------------------------------------------------------------------------

int main(int argc, char **argv)
{
    const std::string framesPath = (argc > 1) ? argv[1] : "testdata/frames.json";
    const std::string cfgPath    = (argc > 2) ? argv[2] : "testdata/config.json";

    std::vector<SFrame> frames = loadFrames(framesPath);
    SBlockConfig        cfg    = loadConfig(cfgPath);

    if (frames.empty())
    {
        std::printf("no frames loaded from %s\n", framesPath.c_str());
        return 1;
    }

    int total = 0;

    for (size_t i = 0; i < frames.size(); ++i)
    {
        std::vector<SEvent> out;

#if defined(BLOCK_FRAMES_2)
        // a 2-frame block cannot run on the very first frame - there is no
        // previous. that is correct behaviour, not a bug.
        if (i == 0) { std::printf("frame %2zu  skipped, no previous\n", i); continue; }
        stage_kernel(frames[i - 1], frames[i], cfg, out);
#else
        stage_kernel(frames[i], cfg, out);
#endif

        std::printf("frame %2zu  detections=%2zu  events=%zu%s\n",
                    i, frames[i].result.detections.size(), out.size(),
                    out.empty() ? "" : "   <-- FIRED");

        for (const SEvent &e : out)
        {
            std::printf("          %s\n", describe(e).c_str());
            ++total;
        }
    }

    std::printf("\ntotal events: %d\n", total);

    // expected_events in the config turns this from a smoke test into a
    // correctness test. a kernel with an inverted comparison compiles
    // perfectly and fires zero times - only this catches it.
    if (cfg.has_expected)
    {
        std::printf("expected    : %d\n", cfg.expected_events);
        if (total == cfg.expected_events)
        {
            std::printf("\nPASS\n");
            return 0;
        }
        std::printf("\nFAIL - compiles but does not behave as specified\n");
        return 1;
    }

    return 0;
}
