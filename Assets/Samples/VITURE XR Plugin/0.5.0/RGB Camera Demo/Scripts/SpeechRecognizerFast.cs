using UnityEngine;

public class AndroidSpeechFast : MonoBehaviour
{
    private AndroidJavaObject recognizerIntent;
    private AndroidJavaObject unityActivity;

    void Start()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        using var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
        unityActivity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");

        using var recognizerIntentClass = new AndroidJavaClass("android.speech.RecognizerIntent");
        recognizerIntent = new AndroidJavaObject("android.content.Intent",
            recognizerIntentClass.GetStatic<string>("ACTION_RECOGNIZE_SPEECH"));

        recognizerIntent.Call<AndroidJavaObject>(
            "putExtra",
            recognizerIntentClass.GetStatic<string>("EXTRA_LANGUAGE_MODEL"),
            recognizerIntentClass.GetStatic<string>("LANGUAGE_MODEL_FREE_FORM")
        );

        recognizerIntent.Call<AndroidJavaObject>(
            "putExtra",
            recognizerIntentClass.GetStatic<string>("EXTRA_PREFER_OFFLINE"),
            true
        );

        recognizerIntent.Call<AndroidJavaObject>(
            "putExtra",
            recognizerIntentClass.GetStatic<string>("EXTRA_PROMPT"),
            "Say a command"
        );
#endif
    }

    public void StartListening()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        unityActivity.Call("startActivityForResult", recognizerIntent, 1001);
#else
        Debug.Log("Speech recognition only works on Android device.");
#endif
    }
}