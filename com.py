import ctypes
from ctypes.wintypes import DWORD, BYTE, BOOL


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8)
    ]

GUID_DEVCLASS_PORTS = GUID(0x4D36E978, 0xE325, 0x11CE, (0xBF, 0xC1, 0x08, 0x00, 0x2B, 0xE1, 0x03, 0x18))


DIGCF_PRESENT = 0x02
SPDRP_FRIENDLYNAME = 0x0000000C
DIF_REMOVE = 0x00000005
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
ERROR_INSUFFICIENT_BUFFER = 122

class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("ClassGuid", GUID),
        ("DevInst", DWORD),
        ("Reserved", ctypes.POINTER(ctypes.c_ulong))
    ]


SetupDiGetClassDevs = ctypes.windll.setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.argtypes = [ctypes.POINTER(GUID), ctypes.c_void_p, ctypes.c_void_p, DWORD]
SetupDiGetClassDevs.restype = ctypes.c_void_p

SetupDiEnumDeviceInfo = ctypes.windll.setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.argtypes = [ctypes.c_void_p, DWORD, ctypes.POINTER(SP_DEVINFO_DATA)]
SetupDiEnumDeviceInfo.restype = BOOL

SetupDiGetDeviceRegistryProperty = ctypes.windll.setupapi.SetupDiGetDeviceRegistryPropertyW
SetupDiGetDeviceRegistryProperty.argtypes = [ctypes.c_void_p, ctypes.POINTER(SP_DEVINFO_DATA), DWORD, ctypes.POINTER(DWORD), ctypes.POINTER(BYTE), DWORD, ctypes.POINTER(DWORD)]
SetupDiGetDeviceRegistryProperty.restype = BOOL

SetupDiCallClassInstaller = ctypes.windll.setupapi.SetupDiCallClassInstaller
SetupDiCallClassInstaller.argtypes = [DWORD, ctypes.c_void_p, ctypes.POINTER(SP_DEVINFO_DATA)]
SetupDiCallClassInstaller.restype = BOOL

SetupDiDestroyDeviceInfoList = ctypes.windll.setupapi.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.argtypes = [ctypes.c_void_p]
SetupDiDestroyDeviceInfoList.restype = BOOL

def uninstallCOMPort():
    deviceInfoSet = SetupDiGetClassDevs(ctypes.byref(GUID_DEVCLASS_PORTS), None, None, DIGCF_PRESENT)
    if deviceInfoSet == INVALID_HANDLE_VALUE:
        print("Failed to get device information set. Error code: %d" % ctypes.GetLastError())
        return False

    deviceInfoData = SP_DEVINFO_DATA()
    deviceInfoData.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)

    index = 0
    while SetupDiEnumDeviceInfo(deviceInfoSet, index, ctypes.byref(deviceInfoData)):
        index += 1
        dataType = DWORD()
        dataSize = DWORD()
        if not SetupDiGetDeviceRegistryProperty(deviceInfoSet, ctypes.byref(deviceInfoData), SPDRP_FRIENDLYNAME,
                                                ctypes.byref(dataType), None, 0, ctypes.byref(dataSize)):
            if ctypes.GetLastError() != ERROR_INSUFFICIENT_BUFFER:
                continue

        buffer = (BYTE * dataSize.value)()
        if not SetupDiGetDeviceRegistryProperty(deviceInfoSet, ctypes.byref(deviceInfoData), SPDRP_FRIENDLYNAME,
                                                ctypes.byref(dataType), buffer, dataSize, None):
            continue

        friendlyName = ctypes.wstring_at(buffer)


        if ("Dispositivo Serial USB" in friendlyName or
            "USB Serial Device" in friendlyName or
            "USB to Serial" in friendlyName or
            "USB COM Port" in friendlyName):

            # Desinstala o dispositivo
            if not SetupDiCallClassInstaller(DIF_REMOVE, deviceInfoSet, ctypes.byref(deviceInfoData)):
                print("Failed to remove device. Error code: %d" % ctypes.GetLastError())
                SetupDiDestroyDeviceInfoList(deviceInfoSet)
                return False

            SetupDiDestroyDeviceInfoList(deviceInfoSet)
            return True

    SetupDiDestroyDeviceInfoList(deviceInfoSet)
    return False