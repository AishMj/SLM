#ifndef CONTRACT_HPP
#define CONTRACT_HPP

// The types generated custom_logic code compiles against.
// Deliberately minimal - no JSON library, no external dependencies, so this
// compiles on a bare Ubuntu box with nothing but g++.
//
// Mirrors AI_HardwareAgnosticLayer/ai_tasks/common/include/ in shape.
// Keep them in sync - if they drift, code that compiles here fails there.

#include <cstdint>
#include <string>
#include <vector>

// Axis-aligned box, NORMALISED to [0,1]. (x, y) is the TOP-LEFT, not centre.
struct SBox
{
    float x = 0.0f;
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

struct SDetection
{
    std::string label;             // free text, do not branch on it
    int32_t     class_id   = 0;    // authoritative
    float       confidence = 0.0f;
    SBox        bbox;
    int32_t     track_id   = -1;   // -1 means untracked
};

struct CObjectDetectionResult
{
    std::vector<SDetection> detections;
};

struct SUseCaseEvent
{
    std::string          use_case;
    std::vector<int32_t> track_ids;
    int                  person_count = 0;
};

struct SConfig
{
    std::vector<SPt2f> polygon;
    int                min_persons = 2;
};

// The only helper generated code may call.
bool pointInZone(float x, float y, const std::vector<SPt2f> &poly);

const int CLASS_PERSON  = 0;
const int CLASS_BICYCLE = 1;
const int CLASS_VEHICLE = 2;

#endif // CONTRACT_HPP
