#PROLLY DETECTED AS SHITT I DONT THINK IT WORKS I DIDNT TEST IT OUT RIP
import sys, time, ctypes
from ctypes import wintypes

TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
PROCESS_ALL_ACCESS = 0x1F0FFF
DONT_RESOLVE_DLL_REFERENCES = 0x00000001
WH_GETMESSAGE = 3
WM_NULL = 0x0000
MAX_PATH = 260

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_wchar * MAX_PATH)
    ]

def GetPID(processName):
    processID = 0
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        return 0
    success = ctypes.windll.kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
    while success:
        if entry.szExeFile.lower() == processName.lower():
            processID = entry.th32ProcessID
            break
        success = ctypes.windll.kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    ctypes.windll.kernel32.CloseHandle(snapshot)
    return processID

def HookFunction(processHandle, functionAddress, newBytes, originalBytes):
    size = len(originalBytes)
    originalBuffer = (ctypes.c_ubyte * size)()
    bytesRead = ctypes.c_size_t(0)
    ctypes.windll.kernel32.ReadProcessMemory(processHandle, functionAddress, originalBuffer, size, ctypes.byref(bytesRead))
    for i in range(size):
        originalBytes[i] = originalBuffer[i]
    sizeNew = len(newBytes)
    newBuffer = (ctypes.c_ubyte * sizeNew)(*newBytes)
    bytesWritten = ctypes.c_size_t(0)
    ctypes.windll.kernel32.WriteProcessMemory(processHandle, functionAddress, newBuffer, sizeNew, ctypes.byref(bytesWritten))

def RestoreFunction(processHandle, functionAddress, originalBytes):
    size = len(originalBytes)
    origBuffer = (ctypes.c_ubyte * size)(*originalBytes)
    bytesWritten = ctypes.c_size_t(0)
    ctypes.windll.kernel32.WriteProcessMemory(processHandle, functionAddress, origBuffer, size, ctypes.byref(bytesWritten))

def GetCurrentDirectory():
    buffer = ctypes.create_string_buffer(MAX_PATH)
    if ctypes.windll.kernel32.GetModuleFileNameA(None, buffer, MAX_PATH):
        fullPath = buffer.value.decode('utf-8')
        pos = max(fullPath.rfind('\\'), fullPath.rfind('/'))
        return fullPath[:pos+1]
    return ""

def Injector():
    ctypes.windll.kernel32.SetConsoleTitleA(b"faded - dev console")
    targetProcessName = "RobloxPlayerBeta.exe"
    crashHandlerName = "RobloxCrashHandler.exe"
    callBackName = "niggerboy"
    currentDir = GetCurrentDirectory()
    dllPath = currentDir + "amdxx64.dll"
    processID = GetPID(targetProcessName)
    if processID == 0:
        ctypes.windll.user32.MessageBoxA(None, b"open roblox", b"dev - error", 0x10)
        return -1
    crashHandlerID = GetPID(crashHandlerName)
    processHandle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, processID)
    if not processHandle:
        return -1
    wintrust_path = "C:\\Windows\\System32\\Wintrust.dll".encode('utf-8')
    hModule = ctypes.windll.kernel32.LoadLibraryA(wintrust_path)
    if not hModule:
        ctypes.windll.kernel32.CloseHandle(processHandle)
        return -1
    funcAddress = ctypes.windll.kernel32.GetProcAddress(hModule, b"WinVerifyTrust") #ud frfr
    if not funcAddress:
        ctypes.windll.kernel32.CloseHandle(processHandle)
        return -1
    originalBytes = bytearray(6)
    hookBytes = [0xB8, 0x00, 0x00, 0x00, 0x00, 0xC3]
    HookFunction(processHandle, funcAddress, hookBytes, originalBytes)
    hwnd = ctypes.windll.user32.FindWindowA(None, b"Roblox")
    threadID = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
    dllPath_bytes = dllPath.encode('utf-8')
    dllHandle = ctypes.windll.kernel32.LoadLibraryExA(dllPath_bytes, None, DONT_RESOLVE_DLL_REFERENCES)
    if not dllHandle:
        RestoreFunction(processHandle, funcAddress, originalBytes)
        ctypes.windll.kernel32.CloseHandle(processHandle)
        return -1
    callbackAddr = ctypes.windll.kernel32.GetProcAddress(dllHandle, callBackName.encode('utf-8'))
    if not callbackAddr:
        RestoreFunction(processHandle, funcAddress, originalBytes)
        ctypes.windll.kernel32.CloseHandle(processHandle)
        return -1
    hook = ctypes.windll.user32.SetWindowsHookExA(WH_GETMESSAGE, callbackAddr, dllHandle, threadID)
    if not hook:
        RestoreFunction(processHandle, funcAddress, originalBytes)
        ctypes.windll.kernel32.CloseHandle(processHandle)
        return -1
    ctypes.windll.user32.PostThreadMessageA(threadID, WM_NULL, 0, 0)
    print(f"injected - pid -> {processID}")
    time.sleep(3)
    ctypes.windll.kernel32.FreeConsole()
    return 0

sys.exit(Injector())
