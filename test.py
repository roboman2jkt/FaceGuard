import cv2
import time
import urllib.parse
from simple_facerec import SimpleFacerec
import pymongo
import threading

# Inisialisasi koneksi MongoDB
client = pymongo.MongoClient("mongodb+srv://robotikman2jkt:DdlJaVXGJO4Lo91o@cluster0.knymo2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test_presensi"]  # Ganti dengan nama database Anda
collection = db["data_siswa"]  # Ganti dengan nama koleksi Anda

# Inisialisasi pengenalan wajah dari Google Drive
sfr = SimpleFacerec()
folder_id = '1_Ymnt_JssiKV3YrAagx8cheBHRjdm2yl'  # Ganti dengan ID folder Google Drive Anda
sfr.load_encoding_images_from_drive(folder_id)
list_image_name = sfr.getlist_name()
variabels = {name: 0 for name in list_image_name}

print(variabels)

url = "https://script.google.com/macros/s/AKfycbxwGZcXEq7kgF6_uelcb3iMNvRKDjG-xwI9ewiQg03UkCWWo9F8xiJl3KKqvhe_dab9/exec"

def urlencode(teks):
    parsed_dict = urllib.parse.parse_qs(teks)
    encoded_string = urllib.parse.urlencode({k: v[0] for k, v in parsed_dict.items()})
    return encoded_string

def process_frame(frame):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        # Extract database variables
        parts = name.split()
        nama = " ".join(parts[:-1])
        kelas = parts[-1]

        # Draw bounding box and text
        if name == "Unknown":
            cv2.putText(frame, "Name : "+ name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
        else:
            cv2.putText(frame, "Name : "+ nama, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 4)

            # Update count and insert to MongoDB if detected for the first time
            variabels[name] += 1
            if variabels[name] == 1:
                data = {
                    "name": nama,
                    "class": kelas,
                    "timestamp": current_time
                }
                collection.insert_one(data)
                print(f"Data {nama} inserted to MongoDB")
            elif variabels[name] >1:
                print(f"Anda Sudah Absen {nama}")

    # Resize and display the frame
    rsize = cv2.resize(frame, (600, 450))
    cv2.imshow("Frame", rsize)

# Main loop to capture and process frames
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Create a separate thread to process the frame
    thread = threading.Thread(target=process_frame, args=(frame,))
    thread.start()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('v'):
        collection.drop()

cap.release()
cv2.destroyAllWindows()
