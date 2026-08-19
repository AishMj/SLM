#include "contract.hpp"
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <sstream>
#include "nlohmann/json.hpp"

using Json = nlohmann::json;

bool pointInZone(float x, float y, const std::vector<SPt2f> &poly)
{
    if (poly.size() < 3) return false;
    bool inside = false;
    const size_t n = poly.size();
    for (size_t i = 0, j = n - 1; i < n; j = i++)
    {
        if ((poly[i].y > y) != (poly[j].y > y))
        {
            const float xc = (poly[j].x - poly[i].x) * (y - poly[i].y)
                           / (poly[j].y - poly[i].y) + poly[i].x;
            if (x < xc) inside = !inside;
        }
    }
    return inside;
}

float sideOfLine(const SPt2f &a, const SPt2f &b, float px, float py)
{
    return (b.x - a.x) * (py - a.y) - (b.y - a.y) * (px - a.x);
}

// intersection area as a percentage of a's area, 0..100
float boxOverlap(const SBox &a, const SBox &b)
{
    const float x1 = std::max(a.x, b.x);
    const float y1 = std::max(a.y, b.y);
    const float x2 = std::min(a.x + a.w, b.x + b.w);
    const float y2 = std::min(a.y + a.h, b.y + b.h);
    if (x2 <= x1 || y2 <= y1) return 0.0f;
    const float inter = (x2 - x1) * (y2 - y1);
    const float area  = a.w * a.h;
    return (area <= 0.0f) ? 0.0f : (inter / area) * 100.0f;
}

SBox headRegion(const SBox &p, float ratio)
{
    SBox h; h.x = p.x; h.y = p.y; h.w = p.w; h.h = p.h * ratio;
    return h;
}

// ---------- loading, using nlohmann/json ----------

static Json readJson(const std::string &path)
{
    std::ifstream f(path);
    if (!f.is_open()) { std::printf("cannot open %s\n", path.c_str()); return Json(); }
    try { Json j; f >> j; return j; }
    catch (const std::exception &e) { std::printf("bad JSON in %s: %s\n", path.c_str(), e.what()); return Json(); }
}

std::vector<SFrame> loadFrames(const std::string &path)
{
    std::vector<SFrame> frames;
    const Json root = readJson(path);
    if (!root.contains("frames")) return frames;

    for (const auto &jf : root["frames"])
    {
        SFrame fr;
        fr.camera_id    = jf.value("camera_id", std::string("cam_01"));
        fr.timestamp_us = jf.value("timestamp_us", (int64_t)0);

        for (const auto &jd : jf.value("detections", Json::array()))
        {
            SDetection d;
            d.label      = jd.value("label", std::string());
            d.class_id   = jd.value("class_id", 0);
            d.confidence = jd.value("confidence", 0.0f);
            d.track_id   = jd.value("track_id", -1);
            const auto b = jd.value("bbox", Json::array());
            if (b.size() >= 4)
            {
                d.bbox.x = b[0].get<float>(); d.bbox.y = b[1].get<float>();
                d.bbox.w = b[2].get<float>(); d.bbox.h = b[3].get<float>();
            }
            fr.result.detections.push_back(d);
        }
        frames.push_back(fr);
    }
    return frames;
}

SBlockConfig loadConfig(const std::string &path)
{
    SBlockConfig c;
    const Json j = readJson(path);
    if (j.is_null()) return c;

    for (const auto &p : j.value("polygon", Json::array()))
        if (p.size() >= 2) { SPt2f pt; pt.x = p[0].get<float>(); pt.y = p[1].get<float>(); c.polygon.push_back(pt); }

    if (j.contains("line_a")) { c.line_a.x = j["line_a"][0]; c.line_a.y = j["line_a"][1]; }
    if (j.contains("line_b")) { c.line_b.x = j["line_b"][0]; c.line_b.y = j["line_b"][1]; }

    c.min_persons         = j.value("min_persons", 1);
    c.alert_count         = j.value("alert_count", 1);
    c.target_class_id     = j.value("target_class_id", 0);
    c.person_class_id     = j.value("person_class_id", 0);
    c.helmet_class_id     = j.value("helmet_class_id", 1);
    c.min_confidence_x100 = j.value("min_confidence_x100", 50);
    c.min_overlap_x100    = j.value("min_overlap_x100", 10);
    c.allowed_dx          = j.value("allowed_dx", 1.0f);
    c.allowed_dy          = j.value("allowed_dy", 0.0f);
    c.min_movement_x1000  = j.value("min_movement_x1000", 10);
    c.has_expected        = j.contains("expected_events");
    c.expected_events     = j.value("expected_events", 0);
    return c;
}

std::string describe(const SEvent &e)
{
    std::ostringstream o;
    o << "{use_case=" << e.use_case << " tracks=[";
    for (size_t i = 0; i < e.track_ids.size(); ++i) o << (i ? "," : "") << e.track_ids[i];
    o << "] count=" << e.person_count;
    if (!e.direction.empty()) o << " dir=" << e.direction;
    o << "}";
    return o.str();
}
