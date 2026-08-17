#ifndef NL_CONTRACT_HPP
#define NL_CONTRACT_HPP

// Types that generated kernels compile against.
// No JSON library, no external dependencies - builds on a bare box with g++.
//
// THE CENTRAL IDEA: each stage's OUTPUT type is the next stage's INPUT type.
// That is what makes a chain composable, and it is what the SLM has to respect.
//
//   detections --[stage 1]--> SStageEvent --[stage 2]--> SUseCaseEvent
//

#include <cstdint>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------

struct SBox
{
    float x = 0.0f;   // normalised 0..1, TOP-LEFT
    float y = 0.0f;
    float w = 0.0f;
    float h = 0.0f;

    float cx() const { return x + w * 0.5f; }
    float cy() const { return y + h * 0.5f; }
};

struct SPt2f
{
    float x = 0.0f;
    float y = 0.0f;
};

// ---------------------------------------------------------------------------
// Stage 0 input - what a detector produces
// ---------------------------------------------------------------------------

struct SDetection
{
    std::string label;             // free text, do NOT branch on it
    int32_t     class_id   = 0;    // authoritative
    float       confidence = 0.0f;
    SBox        bbox;
    int32_t     track_id   = -1;   // -1 means untracked
};

struct CObjectDetectionResult
{
    std::vector<SDetection> detections;
};

// One frame from one camera.
struct SFrame
{
    std::string            camera_id;
    int64_t                timestamp_us = 0;
    CObjectDetectionResult result;
};

// ---------------------------------------------------------------------------
// THE HAND-OFF TYPE
//
// Produced by stage 1. Consumed by stage 2. This is the whole composition
// contract - if a stage does not fill these fields, the next stage cannot work.
// ---------------------------------------------------------------------------

struct SStageEvent
{
    std::string stage;             // which stage produced it, e.g. "line_crossing"
    std::string camera_id;         // which camera it happened on
    int64_t     timestamp_us = 0;  // WHEN - required for cross-camera windows
    int32_t     track_id     = -1; // WHO - on that camera
    SBox        bbox;              // WHERE - carried forward so stage 2 can crop
    std::string direction;         // "in" or "out", empty if not applicable
    float       confidence   = 0.0f;
};

// ---------------------------------------------------------------------------
// Final output - a use case conclusion
// ---------------------------------------------------------------------------

struct SUseCaseEvent
{
    std::string          use_case;
    std::string          camera_id;
    int64_t              timestamp_us = 0;
    std::vector<int32_t> track_ids;      // may span cameras
    int                  person_count = 0;
    std::string          direction;
    float                confidence   = 0.0f;
};

// ---------------------------------------------------------------------------
// Config blocks
// ---------------------------------------------------------------------------

struct SZoneConfig
{
    std::vector<SPt2f> polygon;
    int                min_persons          = 1;
    int                min_confidence_x100  = 50;
};

struct SLineConfig
{
    SPt2f a;
    SPt2f b;
    int   min_confidence_x100 = 50;
};

struct SChainConfig
{
    std::string source_camera;      // where stage 1 runs
    std::string target_camera;      // where stage 2 runs
    int64_t     window_us    = 5000000;   // 5 s correlation window
    float       min_face_conf = 0.5f;
};

// ---------------------------------------------------------------------------
// THE ALLOW-LIST. Generated code may call these and nothing else.
// ---------------------------------------------------------------------------

bool  pointInZone(float x, float y, const std::vector<SPt2f> &poly);
float sideOfLine(const SPt2f &a, const SPt2f &b, float px, float py);
SBox  headRegion(const SBox &person);
bool  hasFace(const SBox &crop, float minConfidence);

const int CLASS_PERSON  = 0;
const int CLASS_BICYCLE = 1;
const int CLASS_VEHICLE = 2;

#endif // NL_CONTRACT_HPP
