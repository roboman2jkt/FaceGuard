import cv2
from time import sleep
import time
import requests
import urllib.parse
from simple_facerec import SimpleFacerec
import pymongo

import streamlit as st
 

client = pymongo.MongoClient("mongodb+srv://robotikman2jkt:DdlJaVXGJO4Lo91o@cluster0.knymo2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["data_presensi"]  # Ganti dengan nama database Anda
collection = db["data_siswa_harian"]  # Ganti dengan nama koleksi Anda

# Encode faces from Google Drive
sfr = SimpleFacerec()
folder_id = '1_Ymnt_JssiKV3YrAagx8cheBHRjdm2yl'  # Ganti dengan ID folder Google Drive Anda
sfr.load_encoding_images_from_drive(folder_id)

list_image_name = sfr.getlist_name()
variabels = {}

for i in range(0,len(list_image_name)):
    # variabel database
    parts_data = list_image_name[i].split()
    nama_data = " ".join(parts_data[:-1])
    kelas_data = parts_data[-1]
    print(f"Nama : {nama_data}")
    print(f"kelas : {kelas_data}\n")
    variabels[list_image_name[i]] = 0

print(variabels)

# url = "https://script.google.com/macros/s/AKfycbxwGZcXEq7kgF6_uelcb3iMNvRKDjG-xwI9ewiQg03UkCWWo9F8xiJl3KKqvhe_dab9/exec"


def urlencode(teks):
    # Menguraikan teks meq1njadi dictionary
    parsed_dict = urllib.parse.parse_qs(teks)
    # Mengonversi dictionary kembali menjadi URL-encoded string
    encoded_string = urllib.parse.urlencode({k: v[0] for k, v in parsed_dict.items()})
    return encoded_string

# Load Camera
cap = cv2.VideoCapture("http://192.168.10.107:81/stream")
# cap = cv2.VideoCapture(0)
while True:
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    current_date = time.strftime("%Y-%m-%d", t)  # Menambahkan tanggal

    ret, frame = cap.read()
    if not ret:
        break

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        # variabel database
        parts = name.split()
        nama = " ".join(parts[:-1])
        kelas = parts[-1]
        
        if name == "Unknown":
            cv2.putText(frame, "Name : "+ name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
        
        for j in range(0,len(list_image_name)):
            if name == list_image_name[j]:
                cv2.putText(frame, "Name : "+ nama, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 4)
                
                
                variabels[list_image_name[j]] += 1
                print(variabels)
                if variabels[list_image_name[j]] == 1:
                    data = {
                        "name": nama,
                        "class": kelas,  # Ganti sesuai kebutuhan Anda
                        "date": current_date,
                        "timestamp": current_time
                    }
                    collection.insert_one(data)
                    print(f"Data {nama} inserted to MongoDB")
        
    

    rsize = cv2.resize(frame,(600,450))
    cv2.imshow("Frame", rsize)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('v'):
        collection.drop()

cap.release()
cv2.destroyAllWindows()