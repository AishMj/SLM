#ifndef CONTRACT_HPP
#define CONTRACT_HPP
// Types every generated kernel compiles against. No external dependencies.
#include <cstdint>
#include <string>
#include <vector>

struct SBox {
    float x=0, y=0, w=0, h=0;                 // normalised 0..1, TOP-LEFT
    float cx() const { return x + w*0.5f; }
    float cy() const { return y + h*0.5f; }
};
struct SPt2f { float x=0, y=0; };

// One detection from the object_detection EVENT. The tracker is attached to
// that event, so track_id is always populated.
struct SDetection {
    std::string label;
    int32_t     class_id   = 0;
    float       confidence = 0.0f;
    SBox        bbox;
    int32_t     track_id   = -1;
};

struct CObjectDetectionResult { std::vector<SDetection> detections; };

struct SFrame {
    std::string            camera_id;
    int64_t                timestamp_us = 0;
    CObjectDetectionResult result;
};

// What every analytic emits.
struct SEvent {
    std::string          use_case;
    std::string          camera_id;
    int64_t              timestamp_us = 0;
    std::vector<int32_t> track_ids;
    int                  person_count = 0;
    std::string          direction;
    float                confidence   = 0.0f;
};

// One config struct for all blocks - keeps the harness generic.
struct SBlockConfig {
    std::vector<SPt2f> polygon;
    SPt2f  line_a, line_b;
    int    min_persons          = 1;
    int    alert_count          = 1;
    int    target_class_id      = 0;
    int    person_class_id      = 0;
    int    helmet_class_id      = 1;
    int    min_confidence_x100  = 50;
    int    min_overlap_x100     = 10;
    float  allowed_dx           = 1.0f;
    float  allowed_dy           = 0.0f;
    int    min_movement_x1000   = 10;
    bool   has_expected         = false;
    int    expected_events      = 0;
};

// ---- allow-list: the ONLY functions generated code may call ----
bool  pointInZone(float x, float y, const std::vector<SPt2f> &poly);
float sideOfLine(const SPt2f &a, const SPt2f &b, float px, float py);
float boxOverlap(const SBox &a, const SBox &b);
SBox  headRegion(const SBox &person, float ratio);

const int CLASS_PERSON  = 0;
const int CLASS_BICYCLE = 1;
const int CLASS_VEHICLE = 2;

// harness only - generated code must NOT call these
std::vector<SFrame> loadFrames(const std::string &path);
SBlockConfig        loadConfig(const std::string &path);
std::string         describe(const SEvent &e);
#endif
