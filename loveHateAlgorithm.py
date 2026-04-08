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

    return persons_less_likely_to_have_conflicts, persons_more_likely_to_have_conflicts
    
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

    return persons_less_likely_to_have_conflicts, persons_more_likely_to_have_conflicts

# if __name__=="__main__":
#     pprint("Love Hate Algorithm Started")
#     person_image = "person1.jpg"
#     list_of_other_people_images = ["person2.jpg"]
#     people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts = simple_love_hate_algorithm(person_image,list_of_other_people_images)
#     pprint("People less likely to have conflicts with the person in the image:")
#     pprint(people_less_likely_to_have_conflicts)
#     pprint("People more likely to have conflicts with the person in the image:")
#     pprint(people_more_likely_to_have_conflicts)
#     pprint("Love Hate Algorithm Ended")



# if __name__=="__main__":
#     pprint("Love Hate Algorithm Started")
#     person_image = "person1.jpg"
#     list_of_other_people_images = ["person2.jpg"]
#     people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts = more_real_love_hate_algorithm(person_image,list_of_other_people_images)
#     pprint("People less likely to have conflicts with the person in the image:")
#     pprint(people_less_likely_to_have_conflicts)
#     pprint("People more likely to have conflicts with the person in the image:")
#     pprint(people_more_likely_to_have_conflicts)
#     pprint("Love Hate Algorithm Ended")


    
