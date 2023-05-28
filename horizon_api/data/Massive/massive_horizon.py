from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Senior Strategic Finance Analyst - R&D, Remote, Any, United States, AMER, From Fivetran’s founding until now, our mission has remained the same: to make access to data as simple and reliable as electricity. With Fivetran, customer data arrives in their warehouses, canonical and ready to query, with no engineering or maintenance required. We’re proud that more organizations continue to leverage our technology every day to become truly data-driven.  About the Role:  Fivetran is building data pipelines to power the modern data stack for thousands of companies. We’re looking for a Strategic Finance Senior Analyst to serve as a key partner to our Engineering and Product teams. This role requires a well-rounded individual who has demonstrated the ability to deliver results in a high-growth, dynamic, and fast-paced environment. You are versatile, analytical, motivated, creative, intellectually curious, and a strong communicator.  This is a full-time position that can be either remote or based out of our Oakland or Denver offices.  What You’ll Do:   * Partner with the Engineering and Product organizations to conduct strategic    analysis and develop insights that support Fivetran’s continued growth.   * Build critical Executive and Board of Directors materials on business    performance.  * Create, track, analyze and report on key business metrics to drive strategic    business decisions.  * Prepare ad-hoc financial analysis and communicate and present results of    analysis across various levels of management.  Skills We’re Looking For:   * 3 - 5 years experience in FP&A or a related finance role.  * Advanced Excel skills with ability to build models and reports.  * Prior SaaS Engineering and Product experience is a strong plus.  * Ability to embrace ambiguity and break down complex problems to provide clear    and effective recommendations.  * Excellent communication skills; can establish credibility, build consensus,    and partner cross-functionally without direct authority.  Perks and Benefits:   * 100% paid Medical, Dental, Vision and Basic Life Insurance. Benefits begin on    your first day!  * Option of Health Savings Account (HSA) or Flexible Savings Account (FSA)  * Generous paid time off (PTO) plus paid sick time, holidays, parental leave,    and volunteer days off  * 401k match program  * Eligible donation match program  * Monthly cell phone stipend  * Home office setup reimbursement program for 100% remote employees  * Professional development and training opportunities  * Company virtual happy hours, free food, and fun team building activities  * Pet Insurance  * Commuter benefits to help with transit and parking costs  * Employee Assistance Program (EAP)  * Referral Bonuses  * RSU's - every employee is granted RSU's when they walk in the door  We’re honored to be valued at over $5.6 billion [https://fivetran.com/blog/hvr-acquisition-series-d], but more importantly, we’re proud of our core values of Get Stuck In, Do the Right Thing, and One Team, One Dream [https://fivetran.com/culture].  Fivetran brings together high-quality talent across the globe to make data access as easy and reliable as electricity for our customers. We value and recognize that our customers benefit from having innovative teams made of people from many backgrounds, experiences and identities. Fivetran promotes diversity, equity, inclusion & belonging through attracting, recruiting, developing and retaining a diverse workforce, not only because it is the right thing to do, but because it helps us build a world-class company to better serve our customers, our people and our communities.  To learn more about Fivetran’s culture and what it’s like to be part of the team, click here [https://www.youtube.com/watch?v=xlhtp4dGh8o] and enjoy our video.  To learn more about our candidate privacy policy, you can read our statement here [https://fivetran.com/candidate-privacy].

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
