## Package to use link
https://pypi.org/project/your-best-friend/

## LoveHateAlgorithm
Which person do you want to be around with right now?

## How to install the package
* pip install your-best-friend==0.1.0

## How to run the package
* import pprint
* import loveHateAlgorithm
* from loveHateAlgorithm import simple_love_hate_algorithm
* pprint("Love Hate Algorithm Started")
* person_image = "/path/to/person1.jpg"
* list_of_other_people_images = ["/path/to/person2.jpg","/path/to/person3.jpg"]
* people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts = simple_love_hate_algorithm(person_image,list_of_other_people_images)
* pprint("People less likely to have conflicts with the person in the image:")
* pprint(people_less_likely_to_have_conflicts)
* pprint("People more likely to have conflicts with the person in the image:")
* pprint(people_more_likely_to_have_conflicts)
* pprint("Love Hate Algorithm Ended")


## for a mixture of emotions
* import pprint
* import loveHateAlgorithm
* from loveHateAlgorithm import simple_love_hate_algorithm
* pprint("Love Hate Algorithm Started")
* person_image = "/path/to/person1.jpg"
* list_of_other_people_images = ["/path/to/person2.jpg","/path/to/person3.jpg"]
* people_less_likely_to_have_conflicts, people_more_likely_to_have_conflicts = more_real_love_hate_algorithm(person_image,list_of_other_people_images)
* pprint("People less likely to have conflicts with the person in the image:")
* pprint(people_less_likely_to_have_conflicts)
* pprint("People more likely to have conflicts with the person in the image:")
* pprint(people_more_likely_to_have_conflicts)
* pprint("Love Hate Algorithm Ended")

