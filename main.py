#PROLLY DETECTED AS SHITT I DONT THINK IT WORKS I DIDNT TEST IT OUT RIP
import ctypes
from ctypes import wintypes
import roblox  

PROCESS_ALL_ACCESS = 0x1F0FFF
STATUS_SUCCESS = 0x00000000
NtProcessId = 15932 #ur process id

ntdll = ctypes.WinDLL("ntdll.dll")
kernel32 = ctypes.WinDLL("kernel32.dll")

class CLIENT_ID(ctypes.Structure):
    _fields_ = [
        ("UniqueProcess", wintypes.HANDLE),
        ("UniqueThread", wintypes.HANDLE)
    ]

class OBJECT_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.ULONG),
        ("RootDirectory", wintypes.HANDLE),
        ("ObjectName", wintypes.LPVOID),
        ("Attributes", wintypes.ULONG),
        ("SecurityDescriptor", wintypes.LPVOID),
        ("SecurityQualityOfService", wintypes.LPVOID)
    ]

def initialize_object_attributes():
    return OBJECT_ATTRIBUTES(
        Length=ctypes.sizeof(OBJECT_ATTRIBUTES),
        RootDirectory=None,
        ObjectName=None,
        Attributes=0,
        SecurityDescriptor=None,
        SecurityQualityOfService=None
    )

def nt_std_cout(message):
    print(f"ntdll.dll -> {message}")
    return 1

def main():
    kernel32.SetConsoleTitleW("ntdll debug console")
    nt_std_cout("made by the legendary faded himself :O")

    NtOpenProcess = ntdll.NtOpenProcess 
    NtOpenProcess.argtypes = [
        ctypes.POINTER(wintypes.HANDLE),
        wintypes.DWORD,
        ctypes.POINTER(OBJECT_ATTRIBUTES),
        ctypes.POINTER(CLIENT_ID)
    ]
    NtOpenProcess.restype = wintypes.LONG

    if not NtOpenProcess:
        nt_std_cout("did not open process :c")
        input("Press Enter to exit...")
        return False

    object_attributes = initialize_object_attributes()
    client_id = CLIENT_ID(
        UniqueProcess=ctypes.cast(NtProcessId, wintypes.HANDLE),
        UniqueThread=None
    )

    process_handle = wintypes.HANDLE()
    status = NtOpenProcess(
        ctypes.byref(process_handle),
        PROCESS_ALL_ACCESS,
        ctypes.byref(object_attributes),
        ctypes.byref(client_id)
    )

    if status == STATUS_SUCCESS:
        nt_std_cout("hacked roblox! diddy streak 3000!")
        input("Press Enter to exit...")
        kernel32.CloseHandle(process_handle)
        return True
    else:
        nt_std_cout("looks like roblox hacked you! failed to open process!")
        input("Press Enter to exit...")
        return False

if __name__ == "__main__":
    main()
