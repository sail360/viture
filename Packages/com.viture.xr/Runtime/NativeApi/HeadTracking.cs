using System.Runtime.InteropServices;

namespace Viture.XR
{
    internal static partial class VitureNativeApi
    {
        internal static class HeadTracking
        {
            [DllImport(k_LibName, EntryPoint = "VitureUnityXR_HeadTracking_Reset")]
            internal static extern void Reset();

            [DllImport(k_LibName, EntryPoint = "VitureUnityXR_HeadTracking_SetWorldOrigin")]
            internal static extern void SetWorldOrigin(float px, float py, float pz,
                                                       float qx, float qy, float qz, float qw);

            [DllImport(k_LibName, EntryPoint = "VitureUnityXR_HeadTracking_SetWorldOriginToCurrent")]
            internal static extern void SetWorldOriginToCurrent();
        }
    }
}
