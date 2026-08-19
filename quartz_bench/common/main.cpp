// Fixed harness. Never changes. Compiled against whatever kernel the SLM wrote.
#include "contract.hpp"
#include <cstdio>
#include <string>
#include <vector>

#if defined(BLOCK_FRAMES_2)
void stage_kernel(const SFrame &prev, const SFrame &curr,
                  const SBlockConfig &cfg, std::vector<SEvent> &out);
#else
void stage_kernel(const SFrame &curr,
                  const SBlockConfig &cfg, std::vector<SEvent> &out);
#endif

int main(int argc, char **argv)
{
    const std::string fp = (argc > 1) ? argv[1] : "frames.json";
    const std::string cp = (argc > 2) ? argv[2] : "config.json";

    std::vector<SFrame> frames = loadFrames(fp);
    SBlockConfig        cfg    = loadConfig(cp);

    if (frames.empty()) { std::printf("no frames from %s\n", fp.c_str()); return 2; }

    int total = 0;
    for (size_t i = 0; i < frames.size(); ++i)
    {
        std::vector<SEvent> out;
#if defined(BLOCK_FRAMES_2)
        if (i == 0) { std::printf("frame %2zu  skipped (no previous)\n", i); continue; }
        stage_kernel(frames[i-1], frames[i], cfg, out);
#else
        stage_kernel(frames[i], cfg, out);
#endif
        std::printf("frame %2zu  det=%2zu  events=%zu%s\n", i,
                    frames[i].result.detections.size(), out.size(),
                    out.empty() ? "" : "   <-- FIRED");
        for (const SEvent &e : out) { std::printf("          %s\n", describe(e).c_str()); ++total; }
    }

    std::printf("\ntotal events: %d\n", total);
    if (cfg.has_expected)
    {
        std::printf("expected    : %d\n", cfg.expected_events);
        if (total == cfg.expected_events) { std::printf("\nPASS\n"); return 0; }
        std::printf("\nFAIL - compiles but behaviour is wrong\n"); return 1;
    }
    return 0;
}
