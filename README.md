# VITURE Unity XR Project

This repository is a Unity 6 project configured for VITURE XR development. It includes a local `com.viture.xr` package, imported VITURE sample content, Unity XR Interaction Toolkit samples, XR Hands samples, and Android build settings for deploying to VITURE-compatible hardware.

Documentation: https://www.viture.com/developer/unity-sdk/unity#overview, follow setup there for VITURE XR development via Unity.

## Project Details

- Unity editor version: `6000.0.67f1`
- Render pipeline: Universal Render Pipeline
- Main local package: `Packages/com.viture.xr`
- VITURE XR package version: `0.8.0`
- Product name: `Baskin World`
- Target platform: Android
- Minimum Android SDK: API 33

## Requirements

Install these before opening the project:

- Unity Hub
- Unity `6000.0.67f1` or another compatible Unity 6 editor
- Android Build Support for the selected Unity editor
- Android SDK & NDK Tools
- OpenJDK, usually installed through Unity Hub with Android Build Support
- Git, because the project depends on `com.endel.nativewebsocket` from GitHub

For device testing, use VITURE-compatible hardware. The included VITURE package README lists:

- VITURE Pro Neckband with compatible XR glasses
- VITURE Luma Ultra for 6DoF tracking

## Opening The Project

1. Clone or download this repository.
2. Open Unity Hub.
3. Choose **Add project from disk** and select this folder.
4. Open the project with Unity `6000.0.67f1`.
5. Let Unity restore packages from `Packages/manifest.json`.

The first import can take a while because Unity will rebuild the `Library` folder and fetch package dependencies.

## Important Packages

The project uses these major packages:

- `com.viture.xr`: local VITURE XR plugin
- `com.unity.xr.management`
- `com.unity.xr.hands`
- `com.unity.xr.interaction.toolkit`
- `com.unity.inputsystem`
- `com.unity.render-pipelines.universal`
- `com.endel.nativewebsocket`
- `com.unity.nuget.newtonsoft-json`

The VITURE package contains runtime APIs for head tracking, hand tracking, marker tracking, RGB camera access, capture, simulation, Android native libraries, and editor setup tools.

## Scenes

Configured scenes include:

- `Assets/Scenes/SampleScene.unity`
- `Assets/Samples/XR Interaction Toolkit/3.0.10/Hands Interaction Demo/HandsDemoScene.unity`
- `Assets/Samples/VITURE XR Plugin/0.5.0/RGB Camera Demo/Scenes/RGB Camera API Demo.unity`

The enabled build scene is:

- `Assets/Samples/VITURE XR Plugin/0.5.0/RGB Camera Demo/Scenes/RGB Camera API Demo.unity`

Open that scene if you want to run the currently configured demo.

## VITURE XR Setup

The repository already contains XR settings under `Assets/XR`:

- `Assets/XR/Loaders/VitureLoader.asset`
- `Assets/XR/Settings/VitureSettings.asset`
- `Assets/XR/XRGeneralSettingsPerBuildTarget.asset`

The VITURE settings currently enable hand tracking on startup and request camera permission. The Android manifest also requests microphone permission for the RGB camera/speech demo.

If Unity shows project validation warnings, open the VITURE setup or validation tools from the Unity editor menu and apply the recommended fixes. Also confirm these settings:

1. Go to **Edit > Project Settings > XR Plug-in Management**.
2. Select the Android tab.
3. Make sure the VITURE loader is enabled.
4. Go to **Edit > Project Settings > Player > Android**.
5. Confirm the app is using the Input System package and Android settings required by the VITURE validation tools.

## Building For Android

1. Open **File > Build Profiles** or **File > Build Settings**.
2. Select the Android profile/platform.
3. Switch platform to Android if needed.
4. Confirm the enabled scene is the RGB Camera API demo or add the scene you want to build.
5. Connect the target Android/VITURE device with USB debugging enabled.
6. Choose **Build And Run**.

## Local Scripts

Important scripts are here: Assets/Samples/VITURE XR Plugin/0.5.0/RGB Camera Demo/Scripts

## External Documentation

- VITURE Unity SDK documentation: https://www.viture.com/developer/unity-sdk/unity#overview
- VITURE support Discord: https://discord.gg/viture
