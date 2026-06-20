using System;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using NativeWebSocket;
using Viture.XR;

public class VitureWebSocketFrameSender : MonoBehaviour
{
    [Header("Server")]
    public string websocketUrl = "ws://127.0.0.1:8000/ws/frames/";

    [Header("Capture")]
    public Transform poseSource; // usually headset/camera transform
    public float fps = 5f;
    public int jpgQuality = 70;

    private WebSocket websocket;
    private int frameId = 1;
    private float timer = 0f;
    private bool isSending = false;

    async void Start()
    {
        if (poseSource == null)
            poseSource = Camera.main.transform;

        await ConnectWebSocket();

        if (VitureRGBCameraManager.Instance == null)
        {
            Debug.LogError("Add VitureRGBCameraManager to the scene.");
            return;
        }

        if (!VitureXR.Camera.RGB.isActive)
        {
            VitureXR.Camera.RGB.Start();
            Debug.Log("Started Viture RGB camera.");
        }
    }

    async Task ConnectWebSocket()
    {
        websocket = new WebSocket(websocketUrl);

        websocket.OnOpen += () =>
        {
            Debug.Log("WebSocket connected");
        };

        websocket.OnError += (e) =>
        {
            Debug.LogError("WebSocket error: " + e);
        };

        websocket.OnClose += (e) =>
        {
            Debug.LogWarning("WebSocket closed: " + e);
        };

        await websocket.Connect();
    }

    async void Update()
    {
#if !UNITY_WEBGL || UNITY_EDITOR
        websocket?.DispatchMessageQueue();
#endif

        timer += Time.deltaTime;
        if (timer < 1f / fps)
            return;

        timer = 0f;

        if (!isSending)
            await SendFrame();
    }

    async Task SendFrame()
    {
        if (websocket == null || websocket.State != WebSocketState.Open)
        {
            Debug.LogWarning("WebSocket not open. Reconnecting...");
            await ConnectWebSocket();
            return;
        }

        var manager = VitureRGBCameraManager.Instance;
        if (manager == null || !VitureXR.Camera.RGB.isActive)
            return;

        isSending = true;

        try
        {
            Texture2D frame = await manager.CaptureFrameAsync();

            if (frame == null)
            {
                Debug.LogWarning("No camera frame yet.");
                isSending = false;
                return;
            }

            byte[] jpgBytes = frame.EncodeToJPG(jpgQuality);

            Vector3 p = poseSource.position;
            Quaternion q = poseSource.rotation;

            string json = $@"{{
                ""type"": ""frame_meta"",
                ""frame_id"": {frameId},
                ""timestamp"": {Time.time},
                ""position"": [{p.x}, {p.y}, {p.z}],
                ""rotation_xyzw"": [{q.x}, {q.y}, {q.z}, {q.w}],
                ""encoding"": ""jpg"",
                ""width"": {frame.width},
                ""height"": {frame.height}
            }}";

            await websocket.SendText(json);
            await websocket.Send(jpgBytes);

            Debug.Log($"Sent frame {frameId}, bytes={jpgBytes.Length}");

            Destroy(frame);
            frameId++;
        }
        catch (Exception e)
        {
            Debug.LogError("SendFrame failed: " + e.Message);
        }

        isSending = false;
    }

    async void OnApplicationQuit()
    {
        if (websocket != null)
            await websocket.Close();
    }
}