using TMPro;
using UnityEngine;

public class TextReceiver : MonoBehaviour
{
    public TextMeshPro processingText;
    public TextMeshPro resultText;

    void Start()
    {
        processingText.text = "Input:";
        resultText.text = "Response:";
    }

    public void SetProcessingText(string text)
    {
        processingText.text = text;
    }

    public void SetResultText(string text)
    {
        resultText.text = text;
    }
}