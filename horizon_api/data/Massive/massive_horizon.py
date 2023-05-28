from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Account Executive - Remote, Remote - EST Hours , ABOUT SMARTASSET:  SmartAsset is on a mission to help people get better Financial Advice. Our vision is to be the web’s go to resource for financial advice powering the largest marketplace connecting consumers with financial advisors and financial products.  We have raised $110 Million in Series D Funding, bringing our valuation to over $1 Billion to further fuel SmartAsset’s continued growth of its market defining SmartAdvisor platform. Today, SmartAsset reaches more than 100 million people each month through its personal finance content, custom tools and personalized calculators. SmartAsset was also named to Y Combinator's list of Top 100 Companies of all time and Forbes' list of America's Best Startup Employers in 2020.     SmartAsset has been featured in hundreds of publications, including the Wall Street Journal, CNN, TechCrunch, The New York Times, CNBC, FOX Business, The Washington Post, U.S. News World Report, TIME, Reuters, Businessweek and Barron’s.     ABOUT THE JOB:   * Identifying and developing potential new clients through prospecting and cold    outreach  * Providing detailed information to prospective customers and educating them on    the features and benefits of SmartAsset’s platform  * Having a consultative approach with clients by understanding their business    needs  * Owning the full sales cycle, from prospecting to closing  * Responding to email queries, and converting financial advisor leads into    client relationships  * Becoming an expert in the financial advisor industry to better help identify    strong advisor prospects who will be a good fit for the Smart Advisor    platform   * Collaborating with company leadership to vet and research different    strategies for finding and converting both inbound and cold leads  * Operating with a high level of integrity and able work within organizational    Rules of Engagement  * Maintaining contacts and outreach in Salesforce      SKILLS / EXPERIENCE YOU HAVE:    * 1-3 years proven track record of success in a performance based sales role  * Experience in an inside sales, cold calling, transactional sales role  * Ability to drive deals independently in a fast-paced, dynamic environment  * Comfortable speaking to and persuading prospective clients on the phone       SKILLS / EXPERIENCE PREFERRED:   * Attention to detail; excellent organization and time-management skills  * Comfortable in a fast-paced, high-growth startup environment  * Salesforce experience preferred but not required  * Team player who possess excellent interpersonal skills and communication    skills   AVAILABLE BENEFITS AND PERKS:    * All roles at SmartAsset are currently and will remain remote - flexibility to    work from anywhere in the US.  * Medical, Dental, Vision - multiple packages available based on your    individualized needs  * Life/AD&D Insurance - basic coverage at 100% company paid, additional    supplemental available   * Short-term and Long-term Disability  * FSA: Medical and Dependant Care   * 401K - 3% match with immediate vesting  * Equity packages for each role  * Time Off:  PTO, 3 Month Paid Parental Leave,  Secondary Caregiver Leave  * EAP (Employee Assistance Program)  * Employee Resource Groups supporting our underrepresented communities  * Pet Insurance  * Home Office Stipend  * Health and Wellness Stipend  * Monthly Food Delivery Stipend     SmartAsset is an equal opportunity employer committed to fostering an inclusive, innovative environment with the best employees. We are committed to equal employment opportunity regardless of race, color, ancestry, religion, sex, national origin, sexual orientation, age, citizenship, marital status, disability, gender identity or Veteran status. If you have a disability or special need that requires accommodation, please contact us at Recruiting@smartasset.com.

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
