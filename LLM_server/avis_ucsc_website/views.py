from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import LocalizationUploadForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import sys

load_dotenv()
from django.core.files.storage import FileSystemStorage
from .forms import VRSUploadForm
from .ragsystem import RAGSystem

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Create a file handler
# if not logger.handlers:
#     handler = logging.FileHandler('ask_llm.log')
#     handler.setLevel(logging.DEBUG)
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
    
#     # Also log to console
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.DEBUG)
#     console_handler.setFormatter(formatter)
#     logger.addHandler(console_handler)


if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

# Example using OpenAI-compatible SDK pattern
from openai import OpenAI
from .tool_router import TOOLS_SPEC, tool_registry
import time
from typing import Optional
import requests

# import h5py
# import numpy as np
# import torch
# from hloc import extract_features
# from .extract_features_smart import extract_one_image_ram

# from projectaria_tools.core import data_provider
# from projectaria_tools.core.stream_id import StreamId
# from hloc.utils.base_model import dynamic_load
# from hloc import extractors
# from PIL import Image

# import cv2
# import torch
# from hloc.utils.io import list_h5_names
from django.views.decorators.http import require_POST
# from projectaria_tools.core.mps.utils import (
#     filter_points_from_confidence,
#     filter_points_from_count,
#     get_gaze_vector_reprojection,
#     get_nearest_eye_gaze,
#     get_nearest_hand_tracking_result,
#     get_nearest_pose,
#     get_nearest_wrist_and_palm_pose,
# )
# from projectaria_tools.core import data_provider
# import projectaria_tools.core.mps as mps
from .forms import SignupForm

@login_required
def dashboard(request):
    return render(request, "dashboard.html")


@login_required
def reports(request):
    return render(request, "reports.html")

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


# def preprocess_netvlad(image: Image.Image) -> torch.Tensor:
#     # Match HLOC NetVLAD preprocessing
#     image = image.convert("RGB")
#     image = np.asarray(image).astype(np.float32)  # HWC

#     h, w = image.shape[:2]
#     max_side = max(w, h)

#     # HLOC: resize only if larger than resize_max=1024
#     if max_side > 1024:
#         scale = 1024 / max_side
#         new_size = (int(round(w * scale)), int(round(h * scale)))  # (W, H)
#         image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

#     # HLOC: HWC -> CHW, then /255
#     image = image.transpose(2, 0, 1)
#     image = image / 255.0

#     return torch.from_numpy(image).float()


# ROOT = Path("db_images")
# GLOBAL_H5 = Path("/workspace/avis_ucsc_website/static/global-feats.h5")
# QUERY_H5 = Path("query-global.h5")
# PAIRS_TXT = Path("pairs-query-db.txt")

# conf = extract_features.confs["netvlad"]
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print("Loading Model")
# Model = dynamic_load(extractors, conf["model"]["name"])
# model = Model(conf["model"]).eval().to(device)
# print("Model Loaded")

# def l2_normalize(x: np.ndarray, axis: int = -1, eps: float = 1e-12) -> np.ndarray:
#     denom = np.linalg.norm(x, axis=axis, keepdims=True)
#     return x / np.clip(denom, eps, None)


# def load_db_descriptors(global_h5):
#     names = list_h5_names(global_h5)
#     descs = []

#     with h5py.File(str(global_h5), "r") as f:
#         for name in names:
#             grp = f[name]
#             if "global_descriptor" in grp:
#                 desc = grp["global_descriptor"][()]
#             elif "descriptors" in grp:
#                 desc = grp["descriptors"][()]
#             else:
#                 raise RuntimeError(
#                     f"{name} has keys {list(grp.keys())}, no descriptor found"
#                 )

#             descs.append(np.asarray(desc, dtype=np.float32).reshape(-1))

#     db_descs = np.stack(descs, axis=0)
#     db_descs = l2_normalize(db_descs, axis=1)
#     return names, db_descs


# class GlobalRetriever:
#     def __init__(self, db_names, db_descs):
#         self.db_names = db_names
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.db_descs = torch.from_numpy(db_descs.astype(np.float32)).to(self.device)

#     @torch.inference_mode()
#     def search(self, query_desc: np.ndarray, k: int = 10):
#         q = np.asarray(query_desc, dtype=np.float32).reshape(1, -1)
#         q = l2_normalize(q, axis=1)
#         q = torch.from_numpy(q).to(self.device)

#         sim = torch.matmul(q, self.db_descs.T).squeeze(0)
#         k = min(k, len(self.db_names))
#         scores, indices = torch.topk(sim, k=k, largest=True, sorted=True)

#         return [
#             {"db": self.db_names[i], "score": float(s)}
#             for s, i in zip(scores.cpu().tolist(), indices.cpu().tolist())
#         ]


# _retriever = None


# def get_retriever():
#     global _retriever
#     if _retriever is None:
#         db_names, db_descs = load_db_descriptors(GLOBAL_H5)
#         _retriever = GlobalRetriever(db_names, db_descs)
#     return _retriever


# _ = get_retriever()


# def retrieve(features, k=10):
#     if "global_descriptor" in features:
#         query_desc = features["global_descriptor"]
#     elif "descriptors" in features:
#         query_desc = features["descriptors"]
#     else:
#         raise RuntimeError(f"Unexpected feature keys: {list(features.keys())}")

#     retriever = get_retriever()
#     return retriever.search(query_desc, k=k)

# with torch.inference_mode():
#     dummy = Image.new("RGB", (640, 480))
#     _ = extract_one_image_ram(dummy, model, preprocess_netvlad)

# @login_required
# def localize(request):
#     result = None
#     image_url = None

#     if request.method == "POST":
#         form = LocalizationUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             query_image = form.cleaned_data["query_image"]
#             t0 = time.perf_counter()
            
#             img = Image.open(query_image).convert("RGB")
#             t1 = time.perf_counter()
            
#             features = extract_one_image_ram(img, model, preprocess_netvlad)
#             t2 = time.perf_counter()

#             matches = retrieve(features, k=3)
#             t3 = time.perf_counter()

#             # print(f"decode: {t1 - t0:.4f}s")
#             # print(f"extract: {t2 - t1:.4f}s")
#             # print(f"retrieve: {t3 - t2:.4f}s")
#             # print(f"total: {t3 - t0:.4f}s")
#             top_match = matches[0]["db"] if matches else None
#             m = re.match(r"(session_\d+)/session_\d+-idx-(\d+)\.png", top_match)
#             if not m:
#                 raise ValueError(f"Unexpected format: {top_match}")

#             session = m.group(1)          # 'session_1'
#             frame_idx = int(m.group(2))   # 1145

#             print(session, frame_idx)
#             # closed_loop_traj = 
#             # time_ns = 
#             # stream_id = get_stream_id(label)
#             # record = vrs_data.get_image_data_by_index(stream_id, idx)

#             # pose = get_nearest_pose(closed_loop_traj, time_ns)
#             # print(pose)
#             raw_path = "/workspace/ceph_s3/raw_data/"
#             vrs_path = raw_path + session + ".vrs"
#             provider = data_provider.create_vrs_data_provider(vrs_path)
#             stream_id = provider.get_stream_id_from_label("camera-rgb")
#             rgb_record = provider.get_image_data_by_index(
#                 stream_id, frame_idx
#             )
#             time_ns = rgb_record[1].capture_timestamp_ns

#             vrs_to_multi_slam = {}
#             vrs_to_multi_slam_path = os.path.join(
#                 "/workspace/ceph_s3/world_map/",
#                 "vrs_to_multi_slam.json"
#             )

#             if os.path.exists(vrs_to_multi_slam_path):
#                 with open(vrs_to_multi_slam_path, "r", encoding="utf-8") as f:
#                     vrs_to_multi_slam = json.load(f)
        
#             print(vrs_to_multi_slam)
#             print(vrs_to_multi_slam[vrs_path])
#             closed_loop_path = "/workspace/ceph_s3/world_map/" + vrs_to_multi_slam[vrs_path] + "/slam/closed_loop_trajectory.csv"
#             closed_loop_traj = mps.read_closed_loop_trajectory(closed_loop_path)

#             pose = get_nearest_pose(closed_loop_traj, time_ns)
#             print(pose.transform_world_device.translation())
#             result = {
#                 "status": f"success: {t3 - t0:.4f}s {pose.transform_world_device.translation()}",
#                 "message": f"Received {query_image.name}.",
#                 "top_match": top_match,
#                 # "matches": top_match,
#                 "estimated_pose": "(x=1.2, y=3.4, z=0.8)",
#             }
#     else:
#         form = LocalizationUploadForm()

#     return render(
#         request,
#         "localization.html",
#         {"form": form, "result": result, "image_url": image_url},
#     )

# # @login_required
# # @require_POST
# # @csrf_exempt
# # def localize_api(request):
# #     t0 = time.perf_counter()

# #     form = LocalizationUploadForm(request.POST, request.FILES)
# #     if not form.is_valid():
# #         return JsonResponse(
# #             {
# #                 "ok": False,
# #                 "errors": form.errors,
# #                 "non_field_errors": form.non_field_errors(),
# #             },
# #             status=400,
# #         )
# #     query_image = form.cleaned_data["query_image"]

# #     t1 = time.perf_counter()
# #     img = Image.open(query_image).convert("RGB")
# #     t2 = time.perf_counter()

# #     query_desc = extract_one_image_ram(img, model, preprocess_netvlad)
# #     t3 = time.perf_counter()

# #     matches = retrieve(query_desc, k=3)
# #     t4 = time.perf_counter()

# #     top_match = matches[0]["db"] if matches else None

# #     return JsonResponse(
# #         {
# #             "ok": True,
# #             "top_match": top_match,
# #             # "matches": matches,
# #             "timing_ms": {
# #                 "form": round((t1 - t0) * 1000, 2),
# #                 "decode": round((t2 - t1) * 1000, 2),
# #                 "extract": round((t3 - t2) * 1000, 2),
# #                 "retrieve": round((t4 - t3) * 1000, 2),
# #                 "total": round((t4 - t0) * 1000, 2),
# #             },
# #         }
# #     )

# from PIL import Image
# import io

# # @csrf_exempt
# # @require_POST
# # def localize_api(request):
# #     t0 = time.perf_counter()

# #     if not request.body:
# #         return JsonResponse({"ok": False, "error": "Empty body"}, status=400)

# #     img = Image.open(io.BytesIO(request.body)).convert("RGB")
# #     t1 = time.perf_counter()

# #     features = extract_one_image_ram(img, model, preprocess_netvlad)
# #     t2 = time.perf_counter()

# #     matches = retrieve(features, k=10)
# #     t3 = time.perf_counter()

# #     top_match = matches[0]["db"] if matches else None

# #     return JsonResponse({
# #         "ok": True,
# #         "top_match": top_match,
# #         "matches": matches,
# #         "timing_ms": {
# #             "decode": round((t1 - t0) * 1000, 2),
# #             "extract": round((t2 - t1) * 1000, 2),
# #             "retrieve": round((t3 - t2) * 1000, 2),
# #             "total": round((t3 - t0) * 1000, 2),
# #         },
# #     })

# import re

# @csrf_exempt
# @require_POST
# def localize_api(request):
#     t0 = time.perf_counter()

#     body = request.body
#     t1 = time.perf_counter()

#     if not body:
#         return JsonResponse({"ok": False, "error": "Empty body"}, status=400)

#     img = Image.open(io.BytesIO(body)).convert("RGB")
#     t2 = time.perf_counter()

#     if torch.cuda.is_available():
#         torch.cuda.synchronize()
#     features = extract_one_image_ram(img, model, preprocess_netvlad)
#     if torch.cuda.is_available():
#         torch.cuda.synchronize()
#     t3 = time.perf_counter()

#     matches = retrieve(features, k=10)

#     if torch.cuda.is_available():
#         torch.cuda.synchronize()
#     t4 = time.perf_counter()

#     top_match = matches[0]["db"] if matches else None
#     m = re.match(r"(session_\d+)/session_\d+-idx-(\d+)\.png", top_match)
#     if not m:
#         raise ValueError(f"Unexpected format: {top_match}")

#     session = m.group(1)          # 'session_1'
#     frame_idx = int(m.group(2))   # 1145

#     print(session, frame_idx)

#     raw_path = "/workspace/ceph_s3/raw_data/"
#     vrs_path = raw_path + session + ".vrs"
#     provider = data_provider.create_vrs_data_provider(vrs_path)
#     stream_id = provider.get_stream_id_from_label("camera-rgb")
#     rgb_record = provider.get_image_data_by_index(
#         stream_id, frame_idx
#     )
#     time_ns = rgb_record[1].capture_timestamp_ns

#     vrs_to_multi_slam = {}
#     vrs_to_multi_slam_path = os.path.join(
#         "/workspace/ceph_s3/world_map/",
#         "vrs_to_multi_slam.json"
#     )

#     if os.path.exists(vrs_to_multi_slam_path):
#         with open(vrs_to_multi_slam_path, "r", encoding="utf-8") as f:
#             vrs_to_multi_slam = json.load(f)

#     print(vrs_to_multi_slam)
#     print(vrs_to_multi_slam[vrs_path])
#     closed_loop_path = "/workspace/ceph_s3/world_map/" + vrs_to_multi_slam[vrs_path] + "/slam/closed_loop_trajectory.csv"
#     closed_loop_traj = mps.read_closed_loop_trajectory(closed_loop_path)

#     pose = get_nearest_pose(closed_loop_traj, time_ns)
#     print(pose.transform_world_device.translation())
#     translation = pose.transform_world_device.translation().tolist()

#     return JsonResponse({
#         "ok": True,
#         "top_match": top_match,
#         "matches": matches,
#         "translation": translation,
#         "timing_ms": {
#             "read_body": round((t1 - t0) * 1000, 2),
#             "decode_image": round((t2 - t1) * 1000, 2),
#             "extract": round((t3 - t2) * 1000, 2),
#             "retrieve": round((t4 - t3) * 1000, 2),
#             "total": round((t4 - t0) * 1000, 2),
#         },
#     })

@login_required
def viewer(request):
    return render(request, "viewer.html")


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://ellm.nrp-nautilus.io/v1",
)


def llm_page(request):
    return render(request, "llm_page.html")


max_tool_steps = 5
OLD_SAMMY_PROMPT = (
    "You are a tool-using assistant.\n"
    "- For exact values (counts, positions, timestamps), ALWAYS call the appropriate tool.\n"
    "- If the user asks for multiple steps (e.g., get a pose then connect a link), call tools in sequence to complete the request.\n"
    "- After you receive a tool result that answers the question, write the final answer and STOP calling tools.\n"
    "- Never call the same tool with the same arguments more than once.\n"
    "- If a required tool is missing, say what you cannot do.\n"
)

SAM_PROMPT = (
    "You are a tool-using assistant.\n"
    "- For exact values such as counts, positions, and timestamps, always call the appropriate tool.\n"
    "- If the user asks for multiple steps, call tools in sequence to complete the request.\n"
    "- After you receive a tool result that answers the question, write the final answer and stop calling tools.\n"
    "- Never call the same tool with the same arguments more than once.\n"
    "- If a required tool is missing, say what you cannot do.\n"
    "\n"
    "Your final response will be spoken aloud by a text-to-speech system.\n"
    "- The final answer should sound natural when read aloud.\n"
    "- Write in plain, conversational sentences.\n"
    "- Prefer one short paragraph unless the user explicitly asks for a detailed breakdown.\n"
    "- Summarize first and keep it brief.\n"
    "- Do not use markdown tables, bullet points, numbered lists, section headers, dividers, code blocks, or markdown emphasis unless the user explicitly asks for them.\n"
    "- Avoid raw JSON, file-like formatting, and long structured dumps.\n"
    "- Prefer short, clear phrasing that sounds good when spoken.\n"
    "- Expand abbreviations when helpful for speech clarity.\n"
)

rag_system = RAGSystem()

# Note: Messages are now stored per-user in Django sessions instead of globally
# This ensures each user has their own conversation context

# Preset modes for different usage profiles. Each preset supplies defaults
# for `max_tool_steps` and `use_context`. Request fields explicitly provided
# will override the preset values.
MODE_PRESETS = {
    "fast": {
        "max_tool_steps": 1,
        "use_context": False,
        "prompt": (
            "Fast mode: answer as briefly and directly as possible. "
            "Use the image only when it clearly improves the answer and user asks questions about image. "
            "Do not call tools unless absolutely necessary. "
            "Avoid extra explanation and keep the response quick."
        ),
    },
    "balanced": {"max_tool_steps": 3, "use_context": True},
    "thorough": {"max_tool_steps": 10, "use_context": True},
}

def generate_response(
    prompt: Optional[str] = None, context: Optional[str] = None, **kwargs
) -> str:
    messages = kwargs.get("messages", [])

    # Optionally inject context into the existing system message
    if context:
        messages = messages.copy()  # Make a copy to avoid modifying original
        if messages and messages[0]["role"] == "system":
            # Merge context into existing system message
            messages[0] = {
                "role": "system",
                "content": f"{messages[0]['content']}\n\nContext: {context}"
            }
        else:
            # If no system message at start, prepend one
            messages = [{"role": "system", "content": f"Context: {context}"}] + messages

    # If caller passed only prompt, convert it to a user message
    if prompt and not kwargs.get("messages"):
        messages = messages + [{"role": "user", "content": prompt}]

    create_kwargs = {
        "model": "qwen3-small",
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.0),
        "max_tokens": kwargs.get("max_tokens", 120),
        "extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    }

    if "temperature" in kwargs:
        create_kwargs["temperature"] = kwargs["temperature"]

    if "tools" in kwargs:
        create_kwargs["tools"] = kwargs["tools"]

    if "tool_choice" in kwargs:
        create_kwargs["tool_choice"] = kwargs["tool_choice"]

    resp_json = client.chat.completions.create(**create_kwargs)

    message = resp_json.choices[0].message
    content = message.content or ""
    tool_calls = message.tool_calls or []

    return message, content, tool_calls


@csrf_exempt
def ask_llm(request):
    logger.debug("ask_llm called")
    if request.method != "POST":
        logger.warning(f"Invalid request method: {request.method}")
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        logger.debug("Parsing request body")
        data = json.loads(request.body)
        prompt = data.get("prompt", "").strip()
        image = data.get("image")
        reset = data.get("reset", False)  # Allow user to reset conversation
        logger.debug(f"Received prompt: {prompt[:100] if prompt else 'None'}...")
        logger.debug(f"Image provided: {bool(image)}")
        logger.debug(f"Reset conversation: {reset}")

        if not prompt:
            logger.warning("Empty prompt, returning error")
            return JsonResponse({"error": "Prompt is required"}, status=400)

        # Initialize or retrieve session messages
        if reset or "messages" not in request.session:
            logger.debug("Initializing new conversation session")
            request.session["messages"] = [
                {"role": "system", "content": SAM_PROMPT},
            ]
        
        session_messages = request.session["messages"]
        logger.debug(f"Current session message count: {len(session_messages)}")

        # Mode presets can provide defaults; explicit request fields override presets
        mode = data.get("mode")
        preset = MODE_PRESETS.get(mode) if mode else None
        mode_prompt = preset.get("prompt") if preset and "prompt" in preset else None

        default_use_context = preset.get("use_context") if preset and "use_context" in preset else True
        default_max_steps = preset.get("max_tool_steps") if preset and "max_tool_steps" in preset else max_tool_steps

        # Per-request controls: whether to fetch context and how many tool steps
        use_context_raw = data.get("use_context", default_use_context)
        if isinstance(use_context_raw, str):
            use_context = use_context_raw.lower() not in ("false", "0", "no", "off")
        else:
            use_context = bool(use_context_raw)

        try:
            max_steps_param = int(data.get("max_tool_steps", default_max_steps))
        except Exception:
            max_steps_param = int(default_max_steps)
        # Bound max steps to a reasonable range
        max_steps_param = max(1, min(50, max_steps_param))

        logger.debug(f"Settings: mode={mode}, preset={preset}, use_context={use_context}, max_tool_steps={max_steps_param}")
        fast_mode = mode == "fast"

        if use_context:
            logger.debug("Getting RAG context")
            memory_context = rag_system.get_context(prompt)
            logger.debug(f"Memory context retrieved: {memory_context[:100] if memory_context else 'None'}...")
        else:
            logger.debug("Skipping RAG context per request")
            memory_context = None

        tstart = time.monotonic()
        seen_calls = set()
        logger.debug("Appending user prompt to messages")
        session_messages.append({"role": "user", "content": prompt})
        logger.debug(f"Total messages before loop: {len(session_messages)}")

        current_messages = session_messages.copy()
        if mode_prompt:
            logger.debug(f"Applying mode prompt for mode={mode}")
            if current_messages and current_messages[0]["role"] == "system":
                current_messages[0] = {
                    "role": "system",
                    "content": f"{current_messages[0]['content']}\n\n{mode_prompt}",
                }
            else:
                current_messages = [{"role": "system", "content": mode_prompt}] + current_messages

        if image:
            logger.debug("Processing image")
            if not image.startswith("data:image"):
                image = f"data:image/jpeg;base64,{image}"

            # Use image ONLY for this LLM call.
            # Do not append image to global messages/history.
            current_messages = current_messages[:-1] + [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            },
                        },
                    ],
                }
            ]
            logger.debug("Image message prepared")

        for step in range(max_steps_param):
            logger.debug(f"Tool loop step {step + 1}/{max_steps_param}")
            logger.debug(f"Current messages count: {len(current_messages)}")
            try:
                response_kwargs = {
                    "context": memory_context if memory_context else None,
                    "messages": current_messages.copy(),
                    "temperature": 0.0,
                }

                if not fast_mode:
                    response_kwargs["tools"] = TOOLS_SPEC
                    response_kwargs["tool_choice"] = "auto"

                message, content, tool_calls = generate_response(**response_kwargs)
                logger.debug(f"generate_response succeeded, content length: {len(content)}")
                logger.debug(f"Tool calls received: {len(tool_calls)}")
            except Exception as gen_error:
                logger.error(f"ERROR in generate_response: {gen_error}")
                raise

            if content:
                logger.debug(f"Assistant response: {content[:100]}...")
                assistant_message = {
                    "role": "assistant",
                    "content": content,
                }
                if tool_calls:
                    assistant_message["tool_calls"] = tool_calls
                    logger.debug(f"Tool calls to execute: {[tc.function.name for tc in tool_calls]}")

                session_messages.append(assistant_message)
                current_messages.append(assistant_message)

            if not tool_calls:
                logger.debug("No tool calls, returning response")
                tend = time.monotonic()
                elapsed = tend - tstart
                logger.info(f"Response generated successfully in {elapsed:.2f} seconds")
                request.session.modified = True
                request.session.save()
                logger.debug(f"Session saved with {len(session_messages)} messages")
                return JsonResponse({"answer": content})

            if fast_mode:
                logger.debug("Fast mode returning one-shot response without tool calls")
                tend = time.monotonic()
                elapsed = tend - tstart
                logger.info(f"Fast response generated in {elapsed:.2f} seconds")
                request.session.modified = True
                request.session.save()
                logger.debug(f"Session saved with {len(session_messages)} messages")
                return JsonResponse({"answer": content})

            for tc in tool_calls:
                name = tc.function.name
                args = tc.function.arguments
                tool_call_id = tc.id

                logger.debug(f"Executing tool: {name}")
                logger.debug(f"Tool arguments: {args}")

                if isinstance(args, str):
                    logger.debug("Parsing tool arguments from string")
                    args = json.loads(args)

                sig = (name, json.dumps(args, sort_keys=True))
                if sig in seen_calls:
                    logger.warning(f"DUPLICATE TOOL CALL DETECTED: {name} with same args")
                    session_messages.append(
                        {
                            "role": "assistant",
                            "content": "I'm repeatedly calling the same tool with the same arguments; I will stop and explain what's missing.",
                        }
                    )
                    logger.debug("Breaking due to duplicate tool calls")
                    break

                seen_calls.add(sig)
                logger.debug(f"Calling tool_registry[{name}]")
                try:
                    result = tool_registry[name](**args)
                    logger.debug(f"Tool result type: {type(result)}")
                except Exception as tool_error:
                    logger.error(f"ERROR executing tool {name}: {tool_error}")
                    raise

                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": name,
                    "content": json.dumps(result),
                }

                session_messages.append(tool_message)
                current_messages.append(tool_message)
                logger.debug("Tool response appended to messages")

        tend = time.monotonic()
        elapsed = tend - tstart
        logger.warning(f"Tool loop exceeded max steps (time: {elapsed:.2f}s)")
        request.session.modified = True
        return JsonResponse({"answer": "Tool loop exceeded max steps."})

    except Exception as e:
        logger.exception(f"Exception in ask_llm: {type(e).__name__}")
        request.session.modified = True
        return JsonResponse({"error": str(e)}, status=500)


def upload_vrs_page(request):
    form = VRSUploadForm()
    return render(request, "upload_vrs.html", {"form": form})


def upload_vrs_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    form = VRSUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse(
            {
                "ok": False,
                "errors": form.errors,
                "non_field_errors": form.non_field_errors(),
            },
            status=400,
        )

    vrs_file = form.cleaned_data["vrs_file"]
    json_file = form.cleaned_data["json_file"]

    upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    storage = FileSystemStorage(location=upload_dir)

    vrs_saved_name = storage.save(vrs_file.name, vrs_file)
    json_saved_name = storage.save(json_file.name, json_file)

    return JsonResponse(
        {
            "ok": True,
            "message": "Files uploaded successfully.",
            "vrs_name": vrs_saved_name,
            "json_name": json_saved_name,
        }
    )

@login_required
def world_map(request):
    return render(request, "world_map.html")

@login_required
def baskin_world_links(request):
    return render(request, "baskin_world_links.html")

