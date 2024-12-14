import os
import cv2
import pathlib
import requests
from datetime import datetime

class ChangeDetection:
    result_prev=[]
    author="admin"
    HOST="http://127.0.0.1:8000"
    username="admin"
    password="admin"
    token=""
    title=""
    text=""
    def __init__(self,names, location="기본위치"):
        self.result_prev= [0 for i in range(len(names))]
        self.location = location  # CCTV 설치 위치
        res= requests.post(self.HOST+'/api-token-auth/',{
            'username':self.username,
            'password':self.password
        })
        res.raise_for_status()
        self.token=res.json()['token']
        print(self.token)

    def add(self, names, detected_current, save_dir, image, person_count):
        self.title = ''
        self.text = ''

        # 사람이 10명 이상 감지되면 전송
        if person_count > 5:
            self.title = self.location  # 위치 정보를 title로 설정
            self.text = f"감지된 사람 수: {person_count}명"
            print(f"DEBUG - 위치: {self.location}, 감지된 사람 수: {person_count}명")
            self.send(save_dir, image)

        # 현재 상태를 이전 상태로 저장
        self.result_prev = detected_current[:]

    def send(self, save_dir, image):
        now = datetime.now()
        now.isoformat()

        today = datetime.now()
        save_path = os.getcwd() / save_dir / 'detected' / str(today.year) / str(today.month) / str(today.day)
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

        full_path = save_path / '{0}-{1}-{2}-{3}.jpg'.format(today.hour, today.minute, today.second, today.microsecond)

        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(full_path, dst)

        headers = {
            'Authorization': f'Token {self.token}',
            'Accept': 'application/json'
        }

        data = {
            'author': 1,
            'title': self.title,
            'text': self.text,
            'created_date': now.isoformat(),
            'published_date': now.isoformat()
        }

        files = {'image': open(full_path, 'rb')}
        
        try:
            print("Sending with token:", self.token)
            res = requests.post(f'{self.HOST}/api_root/Post/', 
                              data=data, 
                              files=files, 
                              headers=headers)
            print(f"Response: {res.status_code}, {res.text}")
            print(f"Headers sent: {headers}")
        except requests.RequestException as e:
            print(f"Failed to send data: {e}")
