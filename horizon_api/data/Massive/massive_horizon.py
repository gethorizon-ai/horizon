from config import Config
import horizon_ai
import json
import concurrent

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Product Manager, Client, Remote, USA, About Veho   Veho is a technology-driven shipping company that enables personalized next-day package delivery, extending partner brand value. Veho brand partners have seen a 20% increase in customer repurchase, 40% increase in customer lifetime value, and 8% rise in net promoter score.   Veho gives package recipients greater insight and control, letting them know when they will receive their package, when drivers are en route, and enables real-time rescheduling, address changes, and personal delivery instructions. Veho's technology matches demand for package delivery with a network of qualified crowdsourced driver partners, ensuring every package is delivered on time and correctly.   The concept for Veho started as a school project while co-founder Itamar Zur attended Harvard Business School. Zur constantly experienced issues receiving packages - from getting the dreaded “we missed you” note, to stolen packages. He set out to fix the problem so many customers and brands face.   Today, Veho’s robust technology platform provides customers and e-commerce brands with an unparalleled shipping experience, an industry record 99.9% average on-time performance for next-day delivery and an average 4.9-star customer rating.   As a Product Manager focused on our Client’s success, you will lead a cross-functional team responsible for creating frictionless experiences for our Clients. You may work on any number of greenfield products, from integrations & apis to data & web portals, that help us improve the end-to-end delivery experience. You will have the opportunity to work with many different internal teams and directly with our Clients.    At Veho we are laser focused on helping our Clients use delivery services to unlock strategic advantages. We have an opportunity to further our Client’s pursuit of highly personal customer experiences by better understanding their needs and streamlining how we serve them.  This role will play an important strategic role when it comes to creating happier Clients, more productive employees, while scaling efficiently.    You will create products that do the following: Help Clients and their partners integrate and onboard faster Give Clients access to strategic insights Empower Clients deliver their brand experience with consumers Driver operational efficiency in the services we provide Clients   You will do the following at Veho: Collaborate with engineering, design, and business partners Create a prioritized roadmap and rapidly launching features Conduct user research designing, running, and evaluating experiments Make customer insight and data backed recommendations Develop rich PRD’s which inform and guide the team  Partner with UX to mockup wireframes in tools such a Figma and Whimsical  Create stories to clearly articulate intent for the Engineering team Autonomously own features from concept to maturity    Basic Qualifications: 3+ years of relevant work experience in Product Management  3 + years experience coordinating between multiple project stakeholders, technical program managers, and software development teams   Preferred Qualifications: 4 year Bachelor’s degree in Business, Computer Science, Engineering, or a related field Ability to communicate and influence at any level of the organization; both technical and non-technical stakeholders Willingness and ability to learn and lean-in wherever there is a need Strong analytical problem solving skills; an ability to pull and analyze data using using SQL and BI tools and take a ‘data first’ approach Ruthless prioritization to focus on the most impactful features and products Strong customer intuition, and research skills; proven success translating customer needs into crisp product requirements Ability to operate effectively in white to gray spaces  Passionate team player that takes ownership, is candid with feedback, and treats everyone with respect A big plus, experience working with retail clients Exposure to supply chain and logistics The starting salary for this role is $103,468. The actual salary is dependent upon many factors, such as: education, experience, and skills. The pay range is subject to the discretion of the Company. #Li-Remote Veho is a growth company that looks for team members to grow with it. Veho offers a generous ownership package, casual work environment, a diverse and inclusive culture, and an electric atmosphere for professional development. No matter the location, or the role, every Veho employee shares one galvanizing mission:  to revolutionize the world of package delivery by creating exceptional experiences for customers and drivers.  We are deeply value-driven (Ownership, Candor, Team Success, Human) and care tremendously about investing in people.  We are committed to creating a diverse team and an environment that provides everyone with the opportunity to do the work of their lifetime. Veho is unable to provide sponsorship at this time.  Applicants must be able to understand and effectively communicate orally and in writing with all parties regarding work matters, which are generally conducted in English.  Qualified applicants will receive consideration without regard to race, color, religion, sex, national origin, age, sexual orientation, gender identity, gender expression, veteran status, or disability.

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
task_ids = [215, 216, 219, 224, 222, 223, 214]

with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks to the executor and store the future objects
    futures = [executor.submit(make_api_call, task_id) for task_id in task_ids]

    # Retrieve the results as they complete
    for future, task_id in zip(concurrent.futures.as_completed(futures), task_ids):
        try:
            # Get the result of the completed task
            task_result = future.result()
            result.update(task_result)
            print(task_result)
        except Exception as e:
            print(f"Error occurred while executing task {task_id}: {e}")

print(json.dumps(result, indent=4))
