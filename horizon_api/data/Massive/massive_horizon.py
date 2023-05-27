from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Lead Software Engineer, US Remote, At H1 we are creating a healthier future by delivering a platform that connects stakeholders across the healthcare ecosystem for greater collaboration and discovery.  We believe providing a trusted and single source of truth for healthcare professional information will power connections in healthcare - and that these connections will lead us to a healthier future. Visit h1.co [http://h1.co] to learn more about us.   Product Engineering is responsible for the development and delivery of our consumer-facing applications. Today, that includes enterprise SaaS web applications but will be expanding into mobile within the year. Our applications are a window into our knowledge base of millions of healthcare professional profiles and their affiliations. The product engineering team builds the applications that allow our customers to search and visualize information to make rapid, business-critical decisions. The team is small and scrappy, but as we rapidly expand the markets we serve, the team must grow and scale.      WHAT YOU’LL DO AT H1 As a Lead Engineer on the Product Engineering team, you will help guide our feature product's technical strategy and architecture, H1 Trial Landscape. You will be working with stakeholders across the engineering, data, and product organizations to support your team in delivering the best scalable, stable, and high-quality healthcare data application in the market.   You will: - Build a world-class user experience - Guide the technical strategy and architecture of our feature core product - Design engineering architecture for our frontends, APIs, services, and databases - Work cross-functionally across the engineering, data, and product organizations to support your team in delivering the best healthcare data application in the market     ABOUT YOU - You are a builder. You love to get your hands dirty. You view tech stacks holistically and understand how each system dovetails to the other. The H1 core product is built with Typescript, React, Node.JS [http://Node.JS], ElasticSearch, Kubernetes, and AWS. You are not afraid to use modern tools and enjoy working in a modern tech stack. - You are a teammate. Being part of a team is a requirement for you. You appreciate working together, solving problems, and iterating to become something better. You like unblocking people, furthering their understanding, and accepting feedback professionally. You understand that delivering the best solution to the customer requires teamwork. - You are an owner. You take pride in your work, so you feel responsible for your slice of the codebase. You have high standards. You monitor your code and make sure that it is reliable and performant.  - You are a student. You understand that as an engineer, you never stop learning. You enjoy learning new things and exploring ideas. You will adopt new technologies tempered by due diligence.     REQUIREMENTS - 5+ years of experience in building all-star products within top-tier engineering teams - Experience with our core technologies: Typescript, React, NodeJS, GraphQL, ElasticSearch, AWS - Experience with databases like PostgreSQL - Software management tools such as Git, JIRA, and CircleCI - Developer Operations, deploying to systems like Netlify, AWS, and Kubernetes   Not meeting all the requirements but still feel like you’d be a great fit? Tell us how you can contribute to our team in a cover letter!  COMPENSATION This role pays $150,000 to $185,000, based on experience. In addition to stock options. H1 OFFERS  - A full suite of health insurance options, in addition to Unlimited Paid Time Off - Flexible work hours & the opportunity to work from anywhere, with optional commuter benefits - Investment in your success by providing you with the skills, knowledge, and mentorship to make you successful - An opportunity to work with leading biotech and life sciences companies, in an innovative industry with a mission to improve healthcare around the globe H1 is proud to be an equal opportunity employer that celebrates diversity and is committed to creating an inclusive workplace with equal opportunity for all applicants and teammates. Our goal is to recruit the most talented people from a diverse candidate pool regardless of race, color, ancestry, national origin, religion, disability, sex (including pregnancy), age, gender, gender identity, sexual orientation, marital status, veteran status, or any other characteristic protected by law.  H1 is committed to working with and providing access and reasonable accommodation to applicants with mental and/or physical disabilities. If you require an accommodation, please reach out to your recruiter once you've begun the interview process. All requests for accommodations are treated discreetly and confidentially, as practical and permitted by law.  #LI-H1

###"""

inputs = {"input_data": test_job_listing}
result = {}


# Define a function to make the API call and update the result
def make_api_call(task_id):
    return json.loads(
        horizon_ai.deploy_task(task_id=task_id, inputs=inputs, log_deployment=True)[
            "completion"
        ]
    )


# List of task IDs to parallelize
task_ids = {
    "title": 215,
    "sub_role": 245,
    "tenure": 244,
    "locations": 243,
    "pay_min": 222,
    "pay_max": 223,
    "responsibility": 214,
}

with ThreadPoolExecutor() as executor:
    # Submit tasks to the executor and store the future objects
    futures = [executor.submit(make_api_call, task_id) for task_id in task_ids.values()]

    # Retrieve the results as they complete
    for future, task_id in zip(as_completed(futures), task_ids.values()):
        try:
            # Get the result of the completed task
            task_result = future.result()
            result.update(task_result)
        except Exception as e:
            print(f"Error occurred while executing task {task_id}: {e}")

print(json.dumps(result, indent=4))
