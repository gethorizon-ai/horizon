from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Senior Engineer, New York, NY | Miami, FL | San Francisco, CA | Boston, MA | Washington DC | Los Angeles, CA | Remote Eligible (US based), About us:  Chief is changing the face of leadership. Our mission: build the most powerful network focused on connecting and supporting women leaders. Our members are VP and C-level executives across every industry who are leading their companies today and building a more equitable tomorrow. Chief was recently recognized as one of Fast Company's Most Innovative Companies of 2021 [https://www.fastcompany.com/90600358/workplace-most-innovative-companies-2021], and you can read more about us in Forbes [https://www.forbes.com/sites/carriehammer/2019/08/28/chiefs-carolyn-childers-and-lindsay-kaplan-are-changing-the-path-to-the-executive-suite/#5c9bfaa33545] or watch us on the Today Show [https://www.youtube.com/watch?v=kK83G4MtN14].  Launched in early 2019, Chief is a Series B stage start-up backed by General Catalyst, Inspired Capital, Primary Ventures, CapitalG, and other top-tier investors. The Chief network includes 12,000+ members from across the United States. We are headquartered in New York City with additional Flagship spaces in Los Angeles, Chicago, and, soon, San Francisco.  We are tech-powered. Our members make meaningful connections, engage in compelling discussions, and view our unique content through our digital platform. Our Product and Technology teams are building the future of that platform, with data and insights at its heart.   ABOUT THE ROLE:    Chief is seeking an experienced full stack web engineer. Our member site is the cornerstone of our member experience. As such, it is central to both our members and organization. It is built with Typescript, React, Storybook on the frontend; GraphQL, and Postgres on the server. This is an opportunity to own, and grow with, the evolution of the platform. This role will play a crucial part in directing the technical design, implementation, build, and deployment of the expanding feature set as well as the functionality of the site.   WHAT YOU’LL DO:    * Collaborate with our product team to implement features that deliver a    premium online experience for our members.  * Manage a modern development process from feature inception to production    deployment.  * Ensure the system is highly available and fault tolerant.   WHAT YOU’VE DONE AND ENJOY DOING:   * Extensive experience with Node, and solid understanding of Typescript.  * Experience in highly available production environments.  * Excellent communicator and collaborator; able to work effectively with both    technical and non-technical teams.  * Cloud (AWS or similar) experience   YOU GET BONUS POINTS FOR:   * Having worked with Typescript and React in production.  * Building backend systems (queues, ORMs, etc) in Typescript.  * Experience using GraphQL and Apollo  * Knowledge of best practices in JavaScript (ES6+), the DOM, HTML, CSS,    browsers, and web performance   WHY YOU'LL WANT TO WORK HERE:   * Competitive salary and equity  * Flexible vacation policy and 4.5 day work weeks  * 20 weeks of paid gender neutral parental leave  * Full medical, dental, and vision packages, 401(k)  * Opportunity to work for a startup focused on driving real change for women in    business  * Opportunity to create and attend inspiring experiences and events with    leaders of the industry  * Access to our ongoing virtual Chief member exclusive content, including    workshops, thought leadership, and iconic speakers  While we’re committed to remaining compliant and adhering to mandates, for us, pay transparency is more than a consideration of what’s lawful and unlawful but rather, an opportunity to disclose what’s required, and what we think is a fair and equitable compensation framework.  At Chief, we want to hire, develop, and retain the best talent, making Chief a top destination to accelerate your career. Our compensation framework is a key part of our vision, and we continually revisit and invest in our philosophy and framework to ensure we remain competitive and relevant, on a quest to achieve our vision.  The pay transparency mandates, as well as our own policies and practices, are a means of narrowing the gender pay gap and fostering an engaged and positive working environment that builds trust, on our mission to change the face of leadership.  The base salary for this role is: $175,000   #LI-REMOTE  

###"""

inputs = {"input_data": test_job_listing}
result = {}


# Define a function to make the API call and update the result
def make_api_call(task_id):
    return json.loads(
        horizon_ai.deploy_task(task_id=task_id, inputs=inputs, log_deployment=False)[
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
