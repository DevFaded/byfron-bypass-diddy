import ctypes
from ctypes import wintypes

TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", wintypes.LPVOID),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.CHAR * 260)
    ]

kernel32 = ctypes.WinDLL("kernel32.dll")

def nt_get_roblox_pid():  
    process_id = 0

    h_snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if h_snapshot == -1:
        return process_id

    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)

    if kernel32.Process32First(h_snapshot, ctypes.byref(pe32)):
        while True:
            if pe32.szExeFile.decode('utf-8').lower() == "robloxplayerbeta.exe":
                process_id = pe32.th32ProcessID
                break
            if not kernel32.Process32Next(h_snapshot, ctypes.byref(pe32)):
                break

    kernel32.CloseHandle(h_snapshot) 
    return process_id

if __name__ == "__main__":
    roblox_pid = nt_get_roblox_pid()
    if roblox_pid:
        print(f"Roblox process ID: {roblox_pid}")
    else:
        print("Roblox process not found.")
