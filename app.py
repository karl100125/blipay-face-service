import io
import os
import face_recognition
import numpy as np
from flask import Flask, jsonify, request
from PIL import Image, ImageOps

API_KEY = os.environ.get("FACE_API_KEY", "blipay123")
THRESHOLD = 0.50
MAX_SIDE = 1600
MIN_SIDE = 480
MAX_UPLOAD = 8 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * MAX_UPLOAD

def load_image(file_storage):
    raw = file_storage.read()
    if not raw or len(raw) > MAX_UPLOAD:
        raise ValueError("Image is empty or too large.")
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img).convert("RGB")
    w, h = img.size
    longest, shortest = max(w, h), min(w, h)
    if longest > MAX_SIDE:
        s = MAX_SIDE / longest
        img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
    elif shortest < MIN_SIDE:
        s = MIN_SIDE / shortest
        img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
    return np.array(img)

def largest_face_encoding(arr, upsample=1):
    locs = face_recognition.face_locations(arr, number_of_times_to_upsample=upsample)
    if not locs:
        return None, 0
    locs.sort(key=lambda b: (b[2] - b[0]) * (b[1] - b[3]), reverse=True)
    enc = face_recognition.face_encodings(arr, [locs[0]], num_jitters=1) # Binalik sa 1 para mas mabilis
    return (enc[0] if enc else None), len(locs)

def respond(match, reason, distance=None, code=200):
    return jsonify(match=match, reason=reason, distance=distance, threshold=THRESHOLD), code

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/verify", methods=["POST"])
def verify():
    if request.headers.get("X-API-Key") != API_KEY:
        return respond(False, "Unauthorized.", code=401)

    id_file, selfie_file = request.files.get("id_photo"), request.files.get("selfie")
    if not id_file or not selfie_file:
        return respond(False, "Both ID photo and selfie are required.", code=400)

    try:
        id_img = load_image(id_file)
        selfie_img = load_image(selfie_file)
    except Exception as e:
        return respond(False, f"Image error: {str(e)}", code=400)

    selfie_enc, selfie_faces = largest_face_encoding(selfie_img, upsample=1)
    if selfie_enc is None:
        return respond(False, "No face detected in the selfie. Face the camera in good light.")
    if selfie_faces > 1:
        return respond(False, "More than one face in the selfie. Only you should be in frame.")

    id_enc, _ = largest_face_encoding(id_img, upsample=2)
    if id_enc is None:
        return respond(False, "No face detected on the ID photo. Upload a clear, front-facing photo of the ID.")

    distance = float(face_recognition.face_distance([id_enc], selfie_enc)[0])
    if distance <= THRESHOLD:
        return respond(True, "Face matches the ID.", round(distance, 4))
    return respond(False, "Your face does not match the photo on the ID.", round(distance, 4))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)