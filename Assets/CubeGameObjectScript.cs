using UnityEngine;

public class CubeGameObjectScript : MonoBehaviour
{
    [Header("Test variable")]
    [SerializeField]
    [Tooltip("Test variable to show in inspector.")]
    private string m_TestString = "Hello, Viture!";

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // this.game
    }
}
