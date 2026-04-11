## Package to use link
https://pypi.org/project/your-best-friend/

## LoveHateAlgorithm
Which person do you want to be around with right now?

## How to install the package
* pip install your-best-friend==0.1.0

## How to run the package
* import pprint
* pprint("Love Hate Algorithm Started")
* person_image = r"C:\Users\gprak\Downloads\Github Repos\archive\train\disgusted\im7.png"
* p = r"C:\Users\gprak\Downloads\Github Repos\archive\train\angry"
* list_of_other_people_images = [os.path.join(p,name) for name in os.listdir(p)]
* algorithm_type = "simple"
* people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts, app = get_output_of_love_hate_algorithm(person_image,list_of_other_people_images,algorithm_type)
* pprint("People less likely to have conflicts with the person in the image:")
* pprint(people_less_likely_to_have_conflicts)
* pprint("People more likely to have conflicts with the person in the image:")
* pprint(people_more_likely_to_have_conflicts)
* run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts(app)



## for a mixture of emotions
* import pprint
* pprint("Love Hate Algorithm Started")
* person_image = r"C:\Users\gprak\Downloads\Github Repos\archive\train\disgusted\im7.png"
* p = r"C:\Users\gprak\Downloads\Github Repos\archive\train\angry"
* list_of_other_people_images = [os.path.join(p,name) for name in os.listdir(p)]
* algorithm_type = "more_real"
* people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts, app = get_output_of_love_hate_algorithm(person_image,list_of_other_people_images,algorithm_type)
* pprint("People less likely to have conflicts with the person in the image:")
* pprint(people_less_likely_to_have_conflicts)
* pprint("People more likely to have conflicts with the person in the image:")
* pprint(people_more_likely_to_have_conflicts)
* run_dash_app_for_persons_with_less_and_more_likely_to_have_conflicts(app)


