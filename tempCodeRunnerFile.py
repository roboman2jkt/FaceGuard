import cv2
from time import sleep
import time
import requests
import urllib.parse
from simple_facerec import SimpleFacerec

# Encode faces from Google Drive
sfr = SimpleFacerec()
folder_id = '1_Ymnt_JssiKV3YrAagx8cheBHRjdm2yl'  # Ganti dengan ID folder Google Drive Anda
sfr.load_encoding_images_from_drive(folder_id)

list_image_name = sfr.getlist_name()
variabels = {}

for i in range(0,len(list_image_name)):
    print(list_image_name[i])
    variabels[list_image_name[i]] = 0

print(variabels)
   

url = "https://script.google.com/macros/s/AKfycbxwGZcXEq7kgF6_uelcb3iMNvRKDjG-xwI9ewiQg03UkCWWo9F8xiJl3KKqvhe_dab9/exec"


def urlencode(teks):
    # Menguraikan teks meq1njadi dictionary
    parsed_dict = urllib.parse.parse_qs(teks)
    # Mengonversi dictionary kembali menjadi URL-encoded string
    encoded_string = urllib.parse.urlencode({k: v[0] for k, v in parsed_dict.items()})
    return encoded_string

# Load Camera
cap = cv2.VideoCapture(1)

while True:
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    ret, frame = cap.read()
    if not ret:
        break

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
        if name == "Unknown":
            cv2.putText(frame, "Name : "+ name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
        
        for j in range(0,len(list_image_name)):
            if name == list_image_name[j]:
                cv2.putText(frame, "Name : "+ name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 4)
                
                
                variabels[list_image_name[j]] += 1
                print(variabels)
                if variabels[list_image_name[j]] == 1:
                    response = requests.get(url,params=urlencode(f"value1={name}&value2=XI B"))

                    if response.status_code == 200:
                        print(response)
                        print(name)
        
    resize_image = cv2.resize(frame, (100,100))        

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()