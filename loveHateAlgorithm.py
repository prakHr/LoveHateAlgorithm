import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # or '3' for even quieter
from deepface import DeepFace
from pprint import pprint
import mpire
import os
os.environ["OMP_NUM_THREADS"] = "1"
import time
import multiprocessing 
from mpire import WorkerPool
from pprint import pprint
import itertools
num_cores =max(multiprocessing.cpu_count()//2,1)
import shutil

import dash
import dash_ag_grid as dag
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# def remove_fake_images(list_of_images):
#     face_objects = [DeepFace.extract_faces(img_path=img_path, anti_spoofing = True, enforce_detection=False) for img_path in list_of_images]
#     real_images = []
#     for face_objs in face_objects:
#         if all(face_obj["is_real"] is True for face_obj in face_objs):
#             real_images.append(img_path)
#     return real_images

def parallel_process_emotional_image(image,emotions_weights):
    objs = DeepFace.analyze(image, actions = ['emotion'], enforce_detection=False)
    angry_emotion_of_other_person_image = sum([objs[0]['emotion'][emotion]*weight for emotion, weight in emotions_weights.items()])/len(emotions_weights)
    return {"image":image, "angry_emotion":angry_emotion_of_other_person_image}

def parallel_process_emotional_images(list_of_images,emotions_weights):
    results = [{"image":image,"emotions_weights":emotions_weights} for image in list_of_images]
    with WorkerPool(n_jobs=num_cores,daemon=False) as pool:
        results = pool.map(parallel_process_emotional_image, results, progress_bar=True)
    results = {result["image"]:result["angry_emotion"] for result in results}
    return results

def parallel_process_image(image):
    objs = DeepFace.analyze(image, actions = ['emotion'], enforce_detection=False)
    angry_emotion_of_other_person_image = objs[0]['emotion']['angry']
    return {"image":image, "angry_emotion":angry_emotion_of_other_person_image}
        

def parallel_process_images(list_of_images):
    results = [{"image":image} for image in list_of_images]
    with WorkerPool(n_jobs=num_cores,daemon=False) as pool:
        results = pool.map(parallel_process_image, results, progress_bar=True)
    results = {result["image"]:result["angry_emotion"] for result in results}
    return results

def create_dash_app(person_image):
    images = os.listdir("assets/less")

    person_filename = os.path.basename(person_image)

    img2 = [f"/assets/less/{img}" for img in images if img != person_filename]

    person_image_path = f"/assets/less/{person_filename}"
    rowData1 = []
    for i in range(len(img2)):
        rowData1.append({"img1": person_image_path, "img2": img2[i]})

    images = os.listdir("assets/more")

    person_filename = os.path.basename(person_image)

    img22 = [f"/assets/more/{img}" for img in images if img != person_filename]

    person_image_path = f"/assets/more/{person_filename}"
    rowData2 = []
    for i in range(len(img22)):
        rowData2.append({"img11": person_image_path, "img22": img22[i]})


    columnDefs1 = [
        {
            "headerName": "Image Pair",
            "field": "img1",
            "cellRenderer": "ImgPairRenderer",
            "autoHeight": True,
            "cellRendererParams": {"type": "less"}
        }
    ]

    columnDefs2 = [
        {
            "headerName": "Image Pair",
            "field": "img11",
            "cellRenderer": "ImgPairRenderer",
            "autoHeight": True,
            "cellRendererParams": {"type": "more"}
        }
    ]

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        html.H2("Image with People Less Likely to Have Conflicts"),

        dag.AgGrid(
            id="grid1",
            columnDefs=columnDefs1,
            rowData=rowData1,
            columnSize="sizeToFit",
            dashGridOptions={
                "rowHeight": 100,
                "pagination": True,              
                "paginationPageSize": 5          
            },
            style={"height": "400px"},
        ),

        dbc.Modal(id="modal1", size="xl"),

        html.H2("Image with People More Likely to Have Conflicts"),

        dag.AgGrid(
            id="grid2",
            columnDefs=columnDefs2,
            rowData=rowData2,
            columnSize="sizeToFit",
            dashGridOptions={
                "rowHeight": 100,
                "pagination": True,              
                "paginationPageSize": 5          
            },
            style={"height": "400px"},
        ),

        dbc.Modal(id="modal2", size="xl"),
    ])

    @callback(
        Output("modal1", "is_open"),
        Output("modal1", "children"),
        Input("grid1", "cellRendererData"),
    )
    def show_image1(data):
        if not data or "img1" not in data:
            return False, None
        return True, html.Div([
            html.Img(src=data["img1"], style={"width": "45%"}),
            html.Img(src=data["img2"], style={"width": "45%", "marginLeft": "10px"})
        ])

    @callback(
        Output("modal2", "is_open"),
        Output("modal2", "children"),
        Input("grid2", "cellRendererData"),
    )
    def show_image2(data):
        if not data or "img11" not in data:
            return False, None
        return True, html.Div([
            html.Img(src=data["img11"], style={"width": "45%"}),
            html.Img(src=data["img22"], style={"width": "45%", "marginLeft": "10px"})
        ])
    return app


def visualize_results(person_image, persons_less_likely_to_have_conflicts,persons_more_likely_to_have_conflicts):
    folder = "assets/less"
    keep_file = "dashAgGridComponentFunctions.js"

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if filename == keep_file:
            continue  

        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    src_path = person_image   # your local image
    dst_path = f"assets/less/{os.path.basename(person_image)}"     # destination in Dash
    assets_person_image_path = dst_path
    shutil.copy(src_path, dst_path)

    for person_image, other_person_images in persons_less_likely_to_have_conflicts.items():
        for other_person_image in other_person_images:
            src_path = other_person_image   # your local image
            dst_path = f"assets/less/{os.path.basename(other_person_image)}"     # destination in Dash
            shutil.copy(src_path, dst_path)

    folder = "assets/more"
    keep_file = "dashAgGridComponentFunctions.js"

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if filename == keep_file:
            continue  

        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    src_path = person_image   # your local image
    dst_path = f"assets/more/{os.path.basename(person_image)}"     # destination in Dash
    assets_person_image_path = dst_path
    shutil.copy(src_path, dst_path)

    for person_image, other_person_images in persons_more_likely_to_have_conflicts.items():
        for other_person_image in other_person_images:
            src_path = other_person_image   # your local image
            dst_path = f"assets/more/{os.path.basename(other_person_image)}"     # destination in Dash
            shutil.copy(src_path, dst_path)
    
    app = create_dash_app(assets_person_image_path)
    return app


def simple_love_hate_algorithm(person_image,list_of_other_people_images):
    # list_of_other_people_images = remove_fake_images(list_of_other_people_images)

    objs = DeepFace.analyze(person_image, actions = ['emotion'], enforce_detection=False)
    happy_emotion_of_person_image = objs[0]['emotion']['happy']
    
    angry_emotion_of_all_other_people_images = [
        (angry_emotion_of_other_person_image,other_person_image) 
        for other_person_image, angry_emotion_of_other_person_image in parallel_process_images(list_of_other_people_images).items()
    ]
    
    distances_between_happy_and_angry_emotions = [(abs(happy_emotion_of_person_image - angry_emotion), other_person_image) for angry_emotion, other_person_image in angry_emotion_of_all_other_people_images]
    persons_less_likely_to_have_conflicts = {person_image:[]}
    min_distance = min(distances_between_happy_and_angry_emotions,key=lambda x: x[0])[0]
    for i in range(len(distances_between_happy_and_angry_emotions)):
        if distances_between_happy_and_angry_emotions[i][0] == min_distance:
            persons_less_likely_to_have_conflicts[person_image] += [distances_between_happy_and_angry_emotions[i][1]]

    angry_emotion_of_person_image = objs[0]['emotion']['angry']
    distances_between_angry_and_angry_emotions = [(abs(angry_emotion_of_person_image - angry_emotion), other_person_image) for angry_emotion, other_person_image in angry_emotion_of_all_other_people_images]
    persons_more_likely_to_have_conflicts = {person_image:[]}
    max_distance = max(distances_between_angry_and_angry_emotions,key=lambda x: x[0])[0]
    for i in range(len(distances_between_angry_and_angry_emotions)):
        if distances_between_angry_and_angry_emotions[i][0] == max_distance:
            persons_more_likely_to_have_conflicts[person_image] += [distances_between_angry_and_angry_emotions[i][1]]

    app = visualize_results(person_image, persons_less_likely_to_have_conflicts, persons_more_likely_to_have_conflicts)

    return persons_less_likely_to_have_conflicts, persons_more_likely_to_have_conflicts,app
    
def more_real_love_hate_algorithm(person_image,list_of_other_people_images,angry_emotions = {'angry':0.9,'disgust':0.8,'fear':0.7,'sad':0.6,'neutral':0.5}, happy_emotions = {'happy':0.9,'surprise':0.8,'neutral':0.5}):
    objs = DeepFace.analyze(person_image, actions = ['emotion'], enforce_detection=False)
    happy_emotion_of_person_image = sum([objs[0]['emotion'][emotion]*weight for emotion, weight in happy_emotions.items()])/len(happy_emotions)
    
    angry_emotion_of_all_other_people_images = [
        (angry_emotion_of_other_person_image,other_person_image) 
        for other_person_image, angry_emotion_of_other_person_image in parallel_process_emotional_images(list_of_other_people_images,angry_emotions).items()
    ]

    distances_between_happy_and_angry_emotions = [(abs(happy_emotion_of_person_image - angry_emotion), other_person_image) for angry_emotion, other_person_image in angry_emotion_of_all_other_people_images]
    persons_less_likely_to_have_conflicts = {person_image:[]}
    min_distance = min(distances_between_happy_and_angry_emotions,key=lambda x: x[0])[0]
    for i in range(len(distances_between_happy_and_angry_emotions)):
        if distances_between_happy_and_angry_emotions[i][0] == min_distance:
            persons_less_likely_to_have_conflicts[person_image] += [distances_between_happy_and_angry_emotions[i][1]]

    angry_emotion_of_person_image = sum([objs[0]['emotion'][emotion]*weight for emotion, weight in angry_emotions.items()])/len(angry_emotions)
    distances_between_angry_and_angry_emotions = [(abs(angry_emotion_of_person_image - angry_emotion), other_person_image) for angry_emotion, other_person_image in angry_emotion_of_all_other_people_images]
    persons_more_likely_to_have_conflicts = {person_image:[]}
    max_distance = max(distances_between_angry_and_angry_emotions,key=lambda x: x[0])[0]
    for i in range(len(distances_between_angry_and_angry_emotions)):
        if distances_between_angry_and_angry_emotions[i][0] == max_distance:
            persons_more_likely_to_have_conflicts[person_image] += [distances_between_angry_and_angry_emotions[i][1]]
    app = visualize_results(person_image, persons_less_likely_to_have_conflicts, persons_more_likely_to_have_conflicts)
    
    return persons_less_likely_to_have_conflicts, persons_more_likely_to_have_conflicts, app

def get_output_of_love_hate_algorithm(person_image,list_of_other_people_images,algorithm_type):
    if algorithm_type == "simple":
        return simple_love_hate_algorithm(person_image,list_of_other_people_images)
    elif algorithm_type == "more_real":
        return more_real_love_hate_algorithm(person_image,list_of_other_people_images)

def run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts(app):
    app.run_server(debug=True, use_reloader=False)



# if __name__=="__main__":
    # import os
    # import pprint
    # import loveHateAlgorithm
    # from loveHateAlgorithm import get_output_of_love_hate_algorithm,run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts
    # pprint.pprint("Love Hate Algorithm Started")
    # person_image = r"C:\Users\gprak\Downloads\Github Repos\archive\train\disgusted\im7.png"
    # p = r"C:\Users\gprak\Downloads\Github Repos\archive\train\angry"
    # list_of_other_people_images = [os.path.join(p,name) for name in os.listdir(p)]
    # algorithm_type = "simple"
    # people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts, app = get_output_of_love_hate_algorithm(person_image,list_of_other_people_images,algorithm_type)
    # pprint.pprint("People less likely to have conflicts with the person in the image:")
    # pprint.pprint(people_less_likely_to_have_conflicts)
    # pprint.pprint("People more likely to have conflicts with the person in the image:")
    # pprint.pprint(people_more_likely_to_have_conflicts)
    # run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts(app)

    # import os
    # import pprint
    # import loveHateAlgorithm
    # from loveHateAlgorithm import get_output_of_love_hate_algorithm,run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts
    # pprint.pprint("Love Hate Algorithm Started")
    # person_image = r"C:\Users\gprak\Downloads\Github Repos\archive\train\disgusted\im7.png"
    # p = r"C:\Users\gprak\Downloads\Github Repos\archive\train\angry"
    # list_of_other_people_images = [os.path.join(p,name) for name in os.listdir(p)]
    # algorithm_type = "more_real"
    # people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts, app = get_output_of_love_hate_algorithm(person_image,list_of_other_people_images,algorithm_type)
    # pprint.pprint("People less likely to have conflicts with the person in the image:")
    # pprint.pprint(people_less_likely_to_have_conflicts)
    # pprint.pprint("People more likely to have conflicts with the person in the image:")
    # pprint.pprint(people_more_likely_to_have_conflicts)
    # run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts(app)

    
