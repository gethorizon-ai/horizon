from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """QA Engineer I, Redwood City, CA, Poshmark is seeking a Software QA Engineer to join the  Quality Assurance team. You will design, develop, drive and deliver high-level test strategies, methodologies and take a hands-on approach to see that they are implemented timely and efficiently. You will partner with our team to help us build out our QA functions and streamline our manual testing, while maintaining close liaison with other departments on technical matters. Overall, driving the integrity and quality of technical work on significant projects. This is a unique opportunity for someone looking to take on big challenges and grow professionally.     Responsibilities   * Conduct manual QA testing of new and existing products, performance and end    to end product for Poshmark's mobile applications (iOS & Android) as well as    Web application and Cloud Platform  * Develop test scenarios and test cases based on business requirements and user    stories  * Identify and write bug reports  * Ability to analyze potential issue and do root cause analysis and assign    issue to the right development team  * Follow up with Engineering and Product team members to see bug fixes through    completion  * Review bug descriptions, functional requirements and design documents,    incorporating this information into test plans and test cases  6-Month Accomplishments   * Able to contribute to develop new test cases, test scenarios  * Run and perform regular regression tests and debug/fix possible issues  * Debug and enhance current test suites  12-Month Accomplishments   * Contributing in design proper process and QA methodologies  at current level    for features  * Implement / enhance ability to work on larger projects with proper process in    place  Qualifications:   * 1+ years of software testing experience in mobile (iOS and android) and    desktop environments  * Experience with bug tracking software - experience with JIRA preferred  * Excellent verbal and written communication skills  * Excellent attention to detail, with an ability to multitask and meet    deadlines  * Ability to work in both a team environment and independently  * Aptitude to learn quickly and effectively  * Strong time management and prioritization skills  Salary Range $80,000—$182,000 USD  About Us  Poshmark is a leading social marketplace for new and secondhand style for women, men, kids, pets, home, and more. By combining the human connection of physical shopping with the scale, ease, and selection benefits of e-commerce, Poshmark makes buying and selling simple, social, and sustainable. Its community of more than 80 million registered users across the U.S., Canada, Australia, and India, is driving the future of commerce while promoting more sustainable consumption. For more information, please visit www.poshmark.com [http://www.poshmark.com/], and for company news and announcements, please visit investors.poshmark.com [http://investors.poshmark.com/]. You can also find Poshmark on Instagram [https://www.instagram.com/poshmark/], Facebook [https://www.facebook.com/Poshmark/], Twitter [https://twitter.com/poshmarkapp], Pinterest, [https://www.pinterest.com/poshmark/] and YouTube [https://www.youtube.com/user/PoshmarkLIVE].  Why Poshmark?  At Poshmark, we’re constantly challenging the status quo and are looking for innovative and passionate people to help shape the future of Poshmark. We’re disrupting the industry by combining social connections with e-commerce through data-driven solutions and the latest technology to optimize our platform. We’re nothing without our amazing team who deliver an unparalleled social shopping experience to the millions of people we connect each day.  We built Poshmark around four core values: 1) focus on people to create empowered communities that drive success; 2) together we grow to support each other to strive for our dreams; 3) lead with love to foster genuine connections built upon a foundation of respect; and 4) embrace your weirdness to accept and empower one another on their own unique journey. We’re invested in our team and community, working together to build an entirely new way to shop. That way, when we win, we all win together. Come help us build the most connected shopping experience ever.  We will set you up with comprehensive global and in-country benefits to support you and your family needs.  Poshmark is an Equal Opportunity Employer. We celebrate diversity and are committed to creating an inclusive environment for all employees.

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
    for future, field, task_id in zip(
        as_completed(futures), task_ids.keys(), task_ids.values()
    ):
        try:
            # Get the result of the completed task
            task_result = future.result()
        except Exception as e:
            # If error occurs, set field to None
            task_result = {field: None}
            print(f"Error occurred while executing task {task_id}: {e}")
        result.update(task_result)

print(json.dumps(result, indent=4))
