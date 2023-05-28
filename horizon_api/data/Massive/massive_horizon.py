from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Commercial Counsel, Marketing, United States, About Kraken   As one of the largest and most trusted digital asset platforms globally, we are empowering people to experience the life-changing potential of crypto. Trusted by over 8 million consumer and pro traders, institutions, and authorities worldwide - our unique combination of products, services, and global expertise is helping tip the scales towards mass crypto adoption. But we’re only just getting started. We want to be pioneers in crypto and add value to the everyday lives of billions. Now is not the time to sit on the sidelines. Join us to bring crypto to the world.   To ensure Kraken is the right fit for you, please ensure you read Kraken Culture Explained [https://kraken-culture.notion.site/] to find out more about us!   About the Role   This role is fully remote within the United States. Per the listed requirement for US state bar admission, we will consider US-based applicants. Responsibilities Partner with our dynamic internal marketing teams to implement company marketing strategyCounsel and advise on risks and opportunities associated with marketing, advertising, offers and promotions, sponsorships, digital social media engagements, and online advertising, such as display and banner ads, targeted advertising, and insertion ordersReview marketing communications and creative documentsDraft and negotiate marketing-related agreements, as well as other commercial transactionsAct as a trusted advisor to internal Marketing and Legal stakeholders in understanding and interpreting proposed and final contract termsDevelop and update form contracts, playbooks, and guidelinesWork and coordinate cross-departmentally with diverse teams, including Compliance, Marketing, Finance, Tax, Security, Regional Operations, Business Development, and Corporate Development, as well as with executive leadershipUse a highly regulated and well-resourced environment to your strategic commercial advantageDevelop strategies for addressing risk in business-centric ways and build commercial processes that allow the business flexibility and freedom to move quickly Requirements 4+ years of experience as a practicing attorney in commercial marketing/advertising law, whether in-house or at a top law firm--creation of agreements, counseling and advising on risks and opportunities, etc.Admission to practice law in the United StatesExperience or interest in structuring, drafting, and negotiating a variety of commercial and licensing agreements, including technology-related agreements, partnership agreements, and general commercial contractsInterest in the crypto industry / what our company is offering to the world and whyA proactive, entrepreneurial mindset, plus an opportunity-making attitude, using the law to increase the company’s optionality, not decrease itPreferred (but not required): 2+ years of experience working in financial services at a bank, representing banking clients, or in commercial negotiations across from banks on a regular basis, or 2+ years working with marketing teams on sponsorships, digital marketing, agency agreements, or similar Location Tagging: #US We’re powered by people from around the world with their own unique and diverse experiences. We value all Krakenites and their talents, contributions, and perspectives, regardless of their background. We encourage you to apply for roles where you don't fully meet the listed requirements, especially if you're passionate or knowledgable about crypto! As an equal opportunity employer we don’t tolerate discrimination or harassment of any kind. Whether that’s based on race, ethnicity, age, gender identity, citizenship, religion, sexual orientation, disability, pregnancy, veteran status or any other protected characteristic as outlined by federal, state or local laws.  Stay in the know Kraken Culture Explained Follow us on Twitter Catch up on our blog Follow us on LinkedIn

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
