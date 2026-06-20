using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Android;
using UnityEngine.Networking;
using Viture.XR;

public class SpeechManager : MonoBehaviour
{
    private AndroidJavaClass speechClass;
    private AndroidJavaObject tts;

    private bool isListening = false;

    private const string LLM_URL = "https://avis.nrp-nautilus.io/ask-llm/";
    
    [System.Serializable]
    public class LLMRequest
    {
        public string prompt;
        public string image; // base64
        public int max_tool_steps;
        public bool use_context;
        public bool reset;
        public string mode;
    }

    public int defaultMaxToolSteps = 1;
    public bool defaultUseContext = false;
    public bool defaultReset = false;

    public string selectedMode = "fast";
    // optional convenience list for inspector-driven UI
    public string[] availableModes = new string[] { "fast", "balanced", "thorough" };

    public TextReceiver textReceiver;
    private Viture.XR.Samples.StarterAssets.VitureQuickActions qa;
    
    [System.Serializable]
    public class LLMResponse
    {
        public string answer;
        public string error;
    }

    void Start()
    {
        qa = FindObjectOfType<Viture.XR.Samples.StarterAssets.VitureQuickActions>();
#if UNITY_ANDROID && !UNITY_EDITOR
        InitTTS();

        Debug.Log("ANDROID path: checking mic permission");

        if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            Debug.Log("Requesting microphone permission");
            Permission.RequestUserPermission(Permission.Microphone);
        }
        else
        {
            InitSpeech();
        }
#endif

        StartRGBCameraIfPossible();
    }

    void StartRGBCameraIfPossible()
    {
        if (VitureRGBCameraManager.Instance == null)
        {
            Debug.LogError("SpeechManager: VitureRGBCameraManager required in scene.");
            return;
        }

        Debug.Log("SpeechManager: RGB supported? " + VitureXR.Camera.RGB.isSupported);
        Debug.Log("SpeechManager: RGB active? " + VitureXR.Camera.RGB.isActive);

        if (!VitureXR.Camera.RGB.isSupported)
        {
            Debug.LogWarning("SpeechManager: RGB Camera is not supported right now.");
            // return;
        }

        if (!VitureXR.Camera.RGB.isActive)
        {
            VitureXR.Camera.RGB.Start();
            Debug.Log("SpeechManager: RGB Camera started.");
        }
    }
    void Update()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        if (speechClass == null && Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            InitSpeech();
        }
#endif
    }

    void InitSpeech()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        if (speechClass != null) return;

        Debug.Log("Initializing speech plugin AFTER permission");

        speechClass = new AndroidJavaClass("com.example.unityspeech.AndroidSpeechRecognizer");
        speechClass.CallStatic("init", gameObject.name);

        Debug.Log("Speech plugin initialized");
#endif
    }

    void InitTTS()
    {
    #if UNITY_ANDROID && !UNITY_EDITOR
        AndroidJavaClass unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
        AndroidJavaObject activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");

        tts = new AndroidJavaObject(
            "android.speech.tts.TextToSpeech",
            activity,
            new AndroidTTSInitListener()   // ✅ FIX
        );
    #endif
    }

    public void StartListening()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        if (speechClass == null)
        {
            Debug.LogWarning("Speech plugin not initialized yet. Check microphone permission.");
            return;
        }

        if (isListening)
        {
            Debug.Log("Already listening");
            return;
        }

        Debug.Log("ANDROID path: calling speechClass.startListening()");
        isListening = true;
        speechClass.CallStatic("startListening");
#else
        Debug.Log("StartListening called");
#endif
    }

    public void StopListening()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        if (speechClass == null) return;

        isListening = false;
        speechClass.CallStatic("stopListening");
#endif
    }

    public void OnSpeechResult(string text)
    {
        isListening = false;
        Debug.Log("Final speech: " + text);
        if (textReceiver != null)
        {
            textReceiver.SetProcessingText("Input: " + text);
            textReceiver.SetResultText("Response: ");
        }
        StartCoroutine(AskLLM(text));
    }

    IEnumerator AskLLM(string userText)
    {
        Texture2D frame = null;

        // capture one frame
        var manager = VitureRGBCameraManager.Instance;
        StartRGBCameraIfPossible();


        for (int i = 0; i < 90; i++)
        {
            if (manager != null && VitureXR.Camera.RGB.isActive && manager.CameraRenderTexture != null)
            {
                Debug.Log("SpeechManager: RGB ready after frames=" + i);
                break;
            }

            yield return null;
        }

        Debug.Log("SpeechManager: RGB manager null? " + (manager == null));
        Debug.Log("SpeechManager: RGB supported? " + VitureXR.Camera.RGB.isSupported);
        Debug.Log("SpeechManager: RGB active? " + VitureXR.Camera.RGB.isActive);
        Debug.Log("SpeechManager: camera RT null? " + (manager == null || manager.CameraRenderTexture == null));

        if (manager != null && VitureXR.Camera.RGB.isActive)
        {
            var task = manager.CaptureFrameAsync();
            while (!task.IsCompleted) yield return null;
            frame = task.Result;
        }
        
        if (frame == null)
        {
            Debug.Log("SpeechManager: no RGB frame captured — will send request without image");
        }
        else
        {
            Debug.Log($"SpeechManager: captured RGB frame {frame.width}x{frame.height}");
        }

        string base64Image = null;

        if (frame != null)
        {
            // Resize to 640x480 to limit upload size / server issues
            int targetW = 640;
            int targetH = 480;

            RenderTexture rt = RenderTexture.GetTemporary(targetW, targetH, 0, RenderTextureFormat.Default);
            Graphics.Blit(frame, rt);

            RenderTexture previous = RenderTexture.active;
            RenderTexture.active = rt;

            Texture2D resized = new Texture2D(targetW, targetH, TextureFormat.RGB24, false);
            resized.ReadPixels(new Rect(0, 0, targetW, targetH), 0, 0);
            resized.Apply();

            RenderTexture.active = previous;
            RenderTexture.ReleaseTemporary(rt);

            byte[] jpg = resized.EncodeToJPG(70);
            base64Image = System.Convert.ToBase64String(jpg);

            Destroy(resized);
            Destroy(frame);
        }

        LLMRequest payload = new LLMRequest
        {
            prompt = userText,
            image = base64Image,
            max_tool_steps = defaultMaxToolSteps,
            use_context = defaultUseContext,
            reset = defaultReset,
            mode = selectedMode
        };

        string json = JsonUtility.ToJson(payload);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(json);

        Debug.Log($"SpeechManager: sending LLM request. imagePresent={(base64Image != null)}, imageLength={(base64Image != null ? base64Image.Length : 0)}, jsonLength={bodyRaw.Length}");

        UnityWebRequest request = new UnityWebRequest(LLM_URL, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        request.timeout = 60; // seconds

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("LLM request failed: " + request.error);
            if (textReceiver != null)
                textReceiver.SetResultText("Response: " + "LLM request failed with error " + request.error);
                if (qa != null) qa.SetLookingUp(true);
            Speak("Sorry, I could not reach Sammy.");
            yield break;
        }

        string raw = request.downloadHandler.text;
        Debug.Log("LLM raw response: " + raw);
        
        LLMResponse data = JsonUtility.FromJson<LLMResponse>(raw);

        if (!string.IsNullOrEmpty(data.answer))
            if (textReceiver != null)
                textReceiver.SetResultText("Response: " + data.answer);
                if (qa != null) qa.SetLookingUp(true);
            else
                Debug.LogWarning("TextReceiver not assigned in Inspector");
                
            Speak(data.answer);
    }
    
    void Speak(string text)
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        if (tts == null)
        {
            Debug.LogWarning("TTS not initialized");
            return;
        }

        tts.Call<int>(
            "speak",
            text,
            0,
            null,
            "sammy_response"
        );
#else
        Debug.Log("TTS: " + text);
#endif
    }

    public void OnSpeechPartial(string text)
    {
        Debug.Log("Partial speech: " + text);
        if (textReceiver != null)
            textReceiver.SetProcessingText("Input: " + text);
            if (qa != null) qa.SetLookingUp(true);
    }

    public void OnSpeechStatus(string status)
    {
        Debug.Log("Speech status: " + status);
    }

    public void OnSpeechError(string errorCode)
    {
        isListening = false;
        Debug.LogWarning("Speech error code: " + errorCode);
    }

    void OnDestroy()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        speechClass?.CallStatic("destroy");

        if (tts != null)
        {
            tts.Call("stop");
            tts.Call("shutdown");
        }
#endif
    }
}

public class AndroidTTSInitListener : AndroidJavaProxy
{
    public AndroidTTSInitListener()
        : base("android.speech.tts.TextToSpeech$OnInitListener")
    {
    }

    public void onInit(int status)
    {
        Debug.Log("TTS init status: " + status);
    }
}
