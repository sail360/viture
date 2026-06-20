using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

/// <summary>
/// Record and draw the last N poses for head, left hand and right hand relative to the XR Origin.
/// - Stores poses in origin-local space (if XR Origin is found).
/// - Draws with Gizmos (visible in Scene view and Game view when gizmos are enabled).
/// - Attempts to find an XROrigin via reflection; falls back to common GameObject names.
/// </summary>
public class PoseTrailDrawer : MonoBehaviour
{
    [Tooltip("Number of poses to keep per trail (per node).")]
    public int trailLength = 40;

    [Tooltip("Reference transform for the XR Origin. If left empty the script will try to find one automatically.")]
    public Transform xrOriginTransform;

    [Header("Draw options")]
    public bool drawHead = true;

    public Color headColor = Color.yellow;

    public float pointSize = 0.0025f;
    [Header("Runtime drawing")]
    [Tooltip("Draw trails with LineRenderers so they are visible in Game view (no Gizmos required).")]
    public bool useLineRenderers = true;
    [Tooltip("Do not draw trail points that are this close to the current head position. This prevents near-camera artifacts.")]
    public float minDistanceFromCurrentHead = 0.02f;
    [Tooltip("Do not draw trail points farther than this from the current head position.")]
    public float maxVisibleDistance = 3f;
    [Tooltip("Layers considered for occlusion checks against the current head position.")]
    public LayerMask occlusionMask = Physics.DefaultRaycastLayers;
    [Tooltip("Log the current sample counts every `logInterval` seconds.")]
    public bool logCounts = false;
    public float logInterval = 0.5f;
    [Header("Head sampling")]
    [Tooltip("Seconds between head samples. Set to >0 to sample periodically.")]
    public float headSampleInterval = 0.1f;
    [Tooltip("Show a local axes visual (RGB XYZ) at each head sample location.")]
    public bool showHeadAxes = false;
    [Tooltip("Length of each axis line in meters.")]
    public float axisLength = 0.05f;

    struct PoseSample { public Vector3 pos; public Quaternion rot; }

    readonly List<PoseSample> m_Head = new List<PoseSample>();

    // Line renderers for persistent Game-view drawing
    LineRenderer m_HeadLR;
    Material m_LineMaterial;
    float m_LogTimer = 0f;
    float m_HeadSampleTimer = 0f;

    // Axis visualizer pool for head samples
    readonly List<GameObject> m_HeadAxisPool = new List<GameObject>();

    void Awake()
    {
        if (xrOriginTransform == null)
            xrOriginTransform = FindXROriginTransform();
    }

    void OnEnable()
    {
        if (useLineRenderers)
            CreateLineRenderers();
    }

    void Start()
    {
        // Ensure line renderers exist and capture an initial sample so something is visible immediately on Play
        if (useLineRenderers && m_HeadLR == null)
            CreateLineRenderers();

        // Do an initial capture/draw pass
        CaptureHeadPose();

        if (useLineRenderers)
        {
            UpdateLineRenderer(m_Head, m_HeadLR);
            if (showHeadAxes) UpdateHeadAxes();
        }
    }

    void OnDisable()
    {
        DestroyLineRenderers();
    }

    void Update()
    {
        // Head sampling: either every frame (interval <= 0) or every headSampleInterval seconds
        if (headSampleInterval > 0f)
        {
            m_HeadSampleTimer += Time.deltaTime;
            if (m_HeadSampleTimer >= headSampleInterval)
            {
                m_HeadSampleTimer = 0f;
                CaptureHeadPose();
            }
        }
        else
        {
            CaptureHeadPose();
        }

        if (useLineRenderers)
        {
            UpdateLineRenderer(m_Head, m_HeadLR);
            if (showHeadAxes)
                UpdateHeadAxes();
        }

        if (logCounts)
        {
            m_LogTimer += Time.deltaTime;
            if (m_LogTimer >= logInterval)
            {
                m_LogTimer = 0f;
                Debug.Log($"PoseTrailDrawer counts - head:{m_Head.Count}");
            }
        }
    }

    void CaptureHeadPose()
    {
        if (!TryGetHeadCamera(out var camObj))
            return;

        Vector3 worldPos = camObj.transform.position;
        Quaternion worldRot = camObj.transform.rotation;

        if (xrOriginTransform != null)
        {
            Vector3 localPos = xrOriginTransform.InverseTransformPoint(worldPos);
            Quaternion localRot = Quaternion.Inverse(xrOriginTransform.rotation) * worldRot;
            AddSample(m_Head, new PoseSample { pos = localPos, rot = localRot });
        }
        else
        {
            AddSample(m_Head, new PoseSample { pos = worldPos, rot = worldRot });
        }
    }

    bool TryGetHeadCamera(out Camera camObj)
    {
        // Find a camera robustly: Camera.main, then under xrOrigin, then any camera
        camObj = Camera.main;
        if (camObj == null && xrOriginTransform != null)
            camObj = xrOriginTransform.GetComponentInChildren<Camera>();
        if (camObj == null && Camera.allCameras.Length > 0)
            camObj = Camera.allCameras[0];

        return camObj != null;
    }

    void AddSample(List<PoseSample> list, PoseSample sample)
    {
        list.Add(sample);
        if (list.Count > trailLength)
            list.RemoveAt(0);
    }

    void OnDrawGizmos()
    {
        // Draw in world space; convert origin-local to world using xrOriginTransform
        if (drawHead)
            DrawTrail(m_Head, headColor);
    }

    void DrawTrail(List<PoseSample> list, Color color)
    {
        if (list == null || list.Count == 0)
            return;

        Gizmos.color = color;
        Vector3 prev = Vector3.zero;
        bool hasPrev = false;

        var hasHeadCam = TryGetHeadCamera(out var camObj);
        var camPos = hasHeadCam ? camObj.transform.position : Vector3.zero;

        for (int i = 0; i < list.Count; ++i)
        {
            var s = list[i];
            Vector3 worldPos = xrOriginTransform != null ? xrOriginTransform.TransformPoint(s.pos) : s.pos;

            if (hasHeadCam && !IsVisibleFromHead(camPos, worldPos))
                continue;

            // point
            Gizmos.DrawSphere(worldPos, pointSize);

            // orientation indicator (small forward line)
            Vector3 forward = (xrOriginTransform != null ? (xrOriginTransform.rotation * s.rot) : s.rot) * Vector3.forward;
            Gizmos.DrawLine(worldPos, worldPos + forward * (pointSize * 4f));

            if (hasPrev)
                Gizmos.DrawLine(prev, worldPos);

            prev = worldPos;
            hasPrev = true;
        }
    }

    Transform FindXROriginTransform()
    {
        // Try to locate the XROrigin type at runtime via reflection to avoid a hard compile dependency
        var xrOriginType = System.Type.GetType("Unity.XR.CoreUtils.XROrigin, Unity.XR.CoreUtils");
        if (xrOriginType != null)
        {
            var found = FindObjectOfType(xrOriginType) as Component;
            if (found != null)
                return found.transform;
        }

        // Try common names used by XR Interaction Toolkit
        var candidates = new[] { "XR Origin"};
        foreach (var name in candidates)
        {
            var go = GameObject.Find(name);
            if (go != null)
                return go.transform;
        }

        // Last resort: find any GameObject that contains a Camera and treat its root as origin
        if (Camera.main != null)
            return Camera.main.transform.root;

        return null;
    }

    void CreateLineRenderers()
    {
        if (m_LineMaterial == null)
        {
            m_LineMaterial = CreateLineMaterial();
        }

        m_HeadLR = CreateLR("PoseTrail_Head", headColor);
        // Create axis pool for head samples
        if (showHeadAxes)
            CreateHeadAxesPool();
    }

    LineRenderer CreateLR(string name, Color col)
    {
        var go = new GameObject(name);
        go.transform.SetParent(transform, false);
        var lr = go.AddComponent<LineRenderer>();
        lr.material = m_LineMaterial;
        lr.startColor = col;
        lr.endColor = col;
        lr.useWorldSpace = true;
        lr.widthMultiplier = Mathf.Max(pointSize, 0.0005f);
        lr.numCornerVertices = 0;
        lr.numCapVertices = 0;
        lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        lr.receiveShadows = false;
        lr.textureMode = LineTextureMode.Stretch;
        lr.alignment = LineAlignment.View;
        lr.generateLightingData = false;
        var gradient = new Gradient();
        gradient.SetKeys(
            new[]
            {
                new GradientColorKey(col, 0f),
                new GradientColorKey(col, 1f),
            },
            new[]
            {
                new GradientAlphaKey(0.15f, 0f),
                new GradientAlphaKey(0.65f, 1f),
            }
        );
        lr.colorGradient = gradient;
        lr.positionCount = 0;
        return lr;
    }

    Material CreateLineMaterial()
    {
        // Prefer transparent unlit shaders to avoid opaque quads/boards in XR.
        var shader = Shader.Find("Universal Render Pipeline/Unlit");
        if (shader == null)
            shader = Shader.Find("Unlit/Color");
        if (shader == null)
            shader = Shader.Find("Sprites/Default");
        if (shader == null)
            shader = Shader.Find("Legacy Shaders/Particles/Alpha Blended");

        var mat = shader != null ? new Material(shader) : new Material(Shader.Find("Diffuse"));
        if (mat.HasProperty("_Color"))
            mat.color = new Color(1f, 1f, 1f, 0.7f);
        return mat;
    }

    void UpdateLineRenderer(List<PoseSample> list, LineRenderer lr)
    {
        if (lr == null)
            return;

        if (list == null || list.Count == 0)
        {
            lr.positionCount = 0;
            return;
        }

        var hasHeadCam = TryGetHeadCamera(out var camObj);
        var camPos = hasHeadCam ? camObj.transform.position : Vector3.zero;

        // Keep only history points that are visible from the current camera.
        var positions = new List<Vector3>(list.Count);
        for (int i = 0; i < list.Count; ++i)
        {
            var s = list[i];
            Vector3 worldPos = xrOriginTransform != null ? xrOriginTransform.TransformPoint(s.pos) : s.pos;

            if (hasHeadCam && !IsVisibleFromHead(camPos, worldPos))
                continue;

            positions.Add(worldPos);
        }

        if (positions.Count < 2)
        {
            lr.positionCount = 0;
            return;
        }

        lr.positionCount = positions.Count;
        for (int i = 0; i < positions.Count; ++i)
        {
            lr.SetPosition(i, positions[i]);
        }
    }

    bool IsVisibleFromHead(Vector3 headPosition, Vector3 worldPos)
    {
        Vector3 toPoint = worldPos - headPosition;
        float distance = toPoint.magnitude;
        if (distance < minDistanceFromCurrentHead || distance > maxVisibleDistance)
            return false;

        if (Physics.Raycast(headPosition, toPoint / distance, out RaycastHit hit, distance, occlusionMask, QueryTriggerInteraction.Ignore))
            return false;

        return true;
    }

    void DestroyLineRenderers()
    {
        if (m_HeadLR != null)
            DestroyImmediate(m_HeadLR.gameObject);
        m_HeadLR = null;

        if (m_LineMaterial != null)
        {
            DestroyImmediate(m_LineMaterial);
            m_LineMaterial = null;
        }
        DestroyHeadAxes();
    }

    void CreateHeadAxesPool()
    {
        DestroyHeadAxes();
        if (m_LineMaterial == null)
        {
            m_LineMaterial = CreateLineMaterial();
        }

        for (int i = 0; i < trailLength; ++i)
        {
            var go = new GameObject($"HeadAxis_{i}");
            go.transform.SetParent(transform, false);

            // Create three line renderers for X (red), Y (green), Z (blue)
            var lrX = go.AddComponent<LineRenderer>();
            var lrY = go.AddComponent<LineRenderer>();
            var lrZ = go.AddComponent<LineRenderer>();

            lrX.material = m_LineMaterial;
            lrY.material = m_LineMaterial;
            lrZ.material = m_LineMaterial;

            lrX.startColor = Color.red; lrX.endColor = Color.red;
            lrY.startColor = Color.green; lrY.endColor = Color.green;
            lrZ.startColor = Color.blue; lrZ.endColor = Color.blue;

            lrX.useWorldSpace = true; lrY.useWorldSpace = true; lrZ.useWorldSpace = true;
            lrX.widthMultiplier = lrY.widthMultiplier = lrZ.widthMultiplier = Mathf.Max(pointSize * 2f, 0.001f);
            lrX.positionCount = lrY.positionCount = lrZ.positionCount = 2;

            go.SetActive(false);
            m_HeadAxisPool.Add(go);
        }
    }

    void UpdateHeadAxes()
    {
        if (!showHeadAxes || m_HeadAxisPool == null)
            return;

        int count = m_HeadAxisPool.Count;
        for (int i = 0; i < count; ++i)
        {
            var go = m_HeadAxisPool[i];
            if (i < m_Head.Count)
            {
                var s = m_Head[i];
                Vector3 worldPos = xrOriginTransform != null ? xrOriginTransform.TransformPoint(s.pos) : s.pos;
                Quaternion worldRot = xrOriginTransform != null ? xrOriginTransform.rotation * s.rot : s.rot;

                var lrs = go.GetComponents<LineRenderer>();
                if (lrs.Length >= 3)
                {
                    // X axis
                    lrs[0].SetPosition(0, worldPos);
                    lrs[0].SetPosition(1, worldPos + worldRot * Vector3.right * axisLength);
                    // Y axis
                    lrs[1].SetPosition(0, worldPos);
                    lrs[1].SetPosition(1, worldPos + worldRot * Vector3.up * axisLength);
                    // Z axis
                    lrs[2].SetPosition(0, worldPos);
                    lrs[2].SetPosition(1, worldPos + worldRot * Vector3.forward * axisLength);
                }

                go.SetActive(true);
            }
            else
            {
                go.SetActive(false);
            }
        }
    }

    void DestroyHeadAxes()
    {
        if (m_HeadAxisPool != null)
        {
            for (int i = 0; i < m_HeadAxisPool.Count; ++i)
            {
                if (m_HeadAxisPool[i] != null)
                    DestroyImmediate(m_HeadAxisPool[i]);
            }
            m_HeadAxisPool.Clear();
        }
    }
}
