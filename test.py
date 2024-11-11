import json
import base64
import os


def save_tak_to_json(tak_file_path, json_file_path):
    """ .tak 파일의 정보를 JSON 파일에 저장 """
    # .tak 파일을 바이너리로 읽기
    with open(tak_file_path, "rb") as tak_file:
        tak_data = tak_file.read()
    
    # Base64 인코딩하여 JSON으로 저장
    encoded_data = base64.b64encode(tak_data).decode("utf-8")
    json_data = {"tak_data": encoded_data}
    
    # JSON 파일에 저장
    with open(json_file_path, "w") as json_file:
        json.dump(json_data, json_file)
    print(f"{tak_file_path}의 데이터가 {json_file_path}에 저장되었습니다.")

def export_json_to_tak(json_file_path, tak_file_path):
    """ JSON 파일의 정보를 .tak 파일로 내보내기 (파일 생성) """
    # JSON 파일을 읽고 Base64 디코딩하여 .tak 파일로 저장
    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)
    
    encoded_data = json_data["tak_data"]
    tak_data = base64.b64decode(encoded_data)
    
    # .tak 파일을 생성하여 저장
    with open(tak_file_path, "wb") as tak_file:
        tak_file.write(tak_data)
    print(f"{json_file_path}의 데이터가 {tak_file_path}로 생성되었습니다.")


current_directory = os.path.dirname(__file__)
# save_tak_to_json(os.path.join(current_directory, "AA.tak"), os.path.join(current_directory, "1.json"))
export_json_to_tak(os.path.join(current_directory, "1.json"), os.path.join(current_directory, "AA.tak"))