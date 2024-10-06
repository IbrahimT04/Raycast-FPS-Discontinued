// compute.cpp
#include <cmath>
#include <string>
#include <vector>
#include <tuple>

// Helper structure for map-related data
struct MapData {
    int mapX;
    int mapY;
    int stepX;
    int stepY;
    float sideDistX;
    float sideDistY;
    float deltaDistX;
    float deltaDistY;
    bool bHitWall;
    bool bBoundary;
};

// Function to initialize the screen
std::vector<std::vector<std::tuple<int, int, int>>> initialize_screen(int nScreenWidth, int nScreenHeight) {
    return {static_cast<std::size_t>(nScreenWidth),
            std::vector<std::tuple<int, int, int>>(static_cast<std::size_t>(nScreenHeight))};
}

// Function to calculate the ray direction and step size
float calculate_ray_angle(float fPlayerA, float fFOV, int x, int nScreenWidth) {
    return (fPlayerA - fFOV / 2.0f) + (float(x) / float(nScreenWidth)) * fFOV;
}

// Function to set initial values for map data
MapData initialize_map_data(float fPlayerX, float fPlayerY, float fEyeX, float fEyeY) {
    MapData data{};
    data.mapX = int(fPlayerX);
    data.mapY = int(fPlayerY);
    data.deltaDistX = std::fabs(fEyeX) > 0.0001f ? sqrtf(1 + (fEyeY * fEyeY) / (fEyeX * fEyeX)) : 999999.0f;
    data.deltaDistY = std::fabs(fEyeY) > 0.0001f ? sqrtf(1 + (fEyeX * fEyeX) / (fEyeY * fEyeY)) : 999999.0f;
    data.bHitWall = false;
    data.bBoundary = false;

    // StepX and StepY initialization
    data.stepX = fEyeX < 0 ? -1 : 1;
    data.sideDistX = (data.stepX == -1) ? (fPlayerX - float(data.mapX)) * data.deltaDistX : (float(data.mapX + 1) - fPlayerX) * data.deltaDistX;

    data.stepY = fEyeY < 0 ? -1 : 1;
    data.sideDistY = (data.stepY == -1) ? (fPlayerY - float(data.mapY)) * data.deltaDistY : (float(data.mapY + 1) - fPlayerY) * data.deltaDistY;

    return data;
}

// Function to handle wall detection
void handle_wall_detection(MapData& data, float fRayAngle, float fPlayerA, float& fDistanceToWall, float fDepth, const char g_map[], int nMapWidth, int nMapHeight) {
    while (!data.bHitWall && fDistanceToWall < fDepth) {
        if (data.sideDistX < data.sideDistY) {
            fDistanceToWall = data.sideDistX * cosf(std::fabs(fRayAngle - fPlayerA));
            data.mapX += data.stepX;
            data.sideDistX += data.deltaDistX;
        } else {
            fDistanceToWall = data.sideDistY * cosf(std::fabs(fRayAngle - fPlayerA));
            data.mapY += data.stepY;
            data.sideDistY += data.deltaDistY;
        }

        if (data.mapX < 0 || data.mapX >= nMapWidth || data.mapY < 0 || data.mapY >= nMapHeight) {
            data.bHitWall = true;
            fDistanceToWall = fDepth;
        } else if (g_map[int(data.mapX + nMapWidth * data.mapY)] == '#') {
            data.bHitWall = true;
            data.bBoundary = true;
        }
    }
}

// Function to calculate ceiling and floor positions
void calculate_ceiling_floor(float fDistanceToWall, float fDepth, int nScreenHeight, float scope, float vertical_angle, float& nCeiling, float& nFloor) {
    if (fDistanceToWall >= fDepth) {
        nCeiling = float(nScreenHeight) / 2.0f + vertical_angle;
        nFloor = float(nScreenHeight) / 2.0f + vertical_angle;
    } else {
        nCeiling = float(nScreenHeight) / 2.0f - float(nScreenHeight) / fDistanceToWall - float(scope) + vertical_angle;
        nFloor = float(nScreenHeight) / 2.0f + float(nScreenHeight) / fDistanceToWall + float(scope) + vertical_angle;
    }
}

// Function to transfer 2D screen vector to 1D array
void transfer_screen_to_output(const std::vector<std::vector<std::tuple<int, int, int>>>& screen, int nScreenWidth, int nScreenHeight, int* screen_output) {
    for (int x = 0; x < nScreenWidth; ++x) {
        for (int y = 0; y < nScreenHeight; ++y) {
            auto& color = screen[x][y];
            screen_output[(y * nScreenWidth + x) * 3 + 0] = std::get<0>(color);
            screen_output[(y * nScreenWidth + x) * 3 + 1] = std::get<1>(color);
            screen_output[(y * nScreenWidth + x) * 3 + 2] = std::get<2>(color);
        }
    }
}

extern "C" {
int* heavy_computation(const int nScreenWidth, const int nScreenHeight, const float fPlayerX, const float fPlayerY,
                       const float fPlayerA, const float fFOV, const char g_map[], const int nMapWidth,
                       const int nMapHeight, const float vertical_angle, const float scope, const float fDepth,
                       int* screen_output) {

    // Initialize the screen vector with the correct dimensions
    auto screen = initialize_screen(nScreenWidth, nScreenHeight);

    for (int x = 0; x < nScreenWidth; x++) {
        // Calculate ray angle
        float fRayAngle = calculate_ray_angle(fPlayerA, fFOV, x, nScreenWidth);

        // Direction and step size
        float fEyeX = cosf(fRayAngle);
        float fEyeY = sinf(fRayAngle);
        float fDistanceToWall = 0.0f;

        // Initialize map data and wall detection
        auto mapData = initialize_map_data(fPlayerX, fPlayerY, fEyeX, fEyeY);
        handle_wall_detection(mapData, fRayAngle, fPlayerA, fDistanceToWall, fDepth, g_map, nMapWidth, nMapHeight);

        // Calculate ceiling and floor positions
        float nCeiling, nFloor;
        calculate_ceiling_floor(fDistanceToWall, fDepth, nScreenHeight, scope, vertical_angle, nCeiling, nFloor);

        // Loop over screen height to set colors (simplified)
        for (int y = 0; y < nScreenHeight; y++) {
            std::tuple<int, int, int> color;

            // Determine pixel color based on wall and ceiling/floor positions
            if (y < int(nCeiling)) {
                color = std::make_tuple(128, 128, 255);  // Sky color
            } else if (y > int(nFloor)) {
                color = std::make_tuple(64, 64, 64);  // Ground color
            } else {
                color = std::make_tuple(192, 192, 192);  // Wall color
            }

            screen[x][y] = color;  // Store the computed color in the screen array
        }
    }

    // Transfer the 2D screen vector into the output 1D array
    transfer_screen_to_output(screen, nScreenWidth, nScreenHeight, screen_output);

    return screen_output;
}
}