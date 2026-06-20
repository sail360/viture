package com.example.unityspeech;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.unity3d.player.UnityPlayer;

import java.util.ArrayList;
import java.util.Locale;

public class AndroidSpeechRecognizer {
    private static SpeechRecognizer speechRecognizer;
    private static Intent recognizerIntent;
    private static String unityObjectName = "SpeechManager";

    public static void init(String unityObject) {
        unityObjectName = unityObject;

        Activity activity = UnityPlayer.currentActivity;

        activity.runOnUiThread(() -> {
            try {
                speechRecognizer = SpeechRecognizer.createSpeechRecognizer(activity);

                recognizerIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                recognizerIntent.putExtra(
                        RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
                );
                recognizerIntent.putExtra(
                        RecognizerIntent.EXTRA_PARTIAL_RESULTS,
                        true
                );
                recognizerIntent.putExtra(
                        RecognizerIntent.EXTRA_PREFER_OFFLINE,
                        true
                );

                speechRecognizer.setRecognitionListener(new RecognitionListener() {
                    @Override
                    public void onReadyForSpeech(Bundle params) {
                        UnityPlayer.UnitySendMessage(unityObjectName, "OnSpeechStatus", "ready");
                    }

                    @Override
                    public void onBeginningOfSpeech() {}

                    @Override
                    public void onEndOfSpeech() {}

                    @Override
                    public void onError(int error) {
                        UnityPlayer.UnitySendMessage(unityObjectName, "OnSpeechError", String.valueOf(error));
                    }

                    @Override
                    public void onResults(Bundle results) {
                        ArrayList<String> matches =
                                results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);

                        if (matches != null && matches.size() > 0) {
                            UnityPlayer.UnitySendMessage(unityObjectName, "OnSpeechResult", matches.get(0));
                        }
                    }

                    @Override
                    public void onPartialResults(Bundle partialResults) {
                        ArrayList<String> matches =
                                partialResults.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);

                        if (matches != null && matches.size() > 0) {
                            UnityPlayer.UnitySendMessage(unityObjectName, "OnSpeechPartial", matches.get(0));
                        }
                    }

                    @Override public void onRmsChanged(float rmsdB) {}
                    @Override public void onBufferReceived(byte[] buffer) {}
                    @Override public void onEvent(int eventType, Bundle params) {}
                });

            } catch (Exception e) {
                UnityPlayer.UnitySendMessage(unityObjectName, "OnSpeechError", e.toString());
            }
        });
    }

    public static void startListening() {
        Activity activity = UnityPlayer.currentActivity;
        activity.runOnUiThread(() -> {
            if (speechRecognizer != null && recognizerIntent != null) {
                speechRecognizer.startListening(recognizerIntent);
            }
        });
    }

    public static void stopListening() {
        Activity activity = UnityPlayer.currentActivity;
        activity.runOnUiThread(() -> {
            if (speechRecognizer != null) {
                speechRecognizer.stopListening();
            }
        });
    }

    public static void destroy() {
        Activity activity = UnityPlayer.currentActivity;
        activity.runOnUiThread(() -> {
            if (speechRecognizer != null) {
                speechRecognizer.destroy();
                speechRecognizer = null;
            }
        });
    }
}