from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Senior Growth Marketing Manager, New York, NY, Canary Technologies is a fast-growing enterprise hospitality technology company that provides hotels with innovative solutions to drive efficiency and enhance the guest experience. Our core solutions get rid of antiquated technology in hotels. With backing from some of the top investors in Silicon Valley, including Y Combinator, Canary Technologies is trusted by thousands worldwide and serves some of the world’s largest and most iconic hotel brands.   This opportunity will provide close interaction with senior leaders and founders. Our founders are alums of the Cornell Hotel School, Columbia University, and The University of Pennsylvania- Wharton. They have previously built software companies and have worked at firms such as Bain & Company and Starwood Hotels & Resorts.   We are an organization that strongly believes in meritocracy and performance. There is significant opportunity for advancement and growth in this role, both of which are based on performance and talent.     About You   You are passionate about marketing and are excited to work in the travel & hospitality industry. You're detail-oriented and thrive in a fast-paced environment. You have demonstrated success running digital marketing campaigns from start to finish, coordinating with stakeholders, and driving results.   About the Role   This role is an integral part of our Marketing team. You will have the opportunity to work cross-functionally with the entire team, including leadership to expand our marketing reach. The day-to-day responsibilities will evolve as the company grows. This is a Growth Marketing generalist role that will wear multiple hats, including email marketing, digital marketing, and marketing operations -- we are looking for an agile, autonomous team player who isn’t afraid to roll up their sleeves. Responsibilities Generate quality and reliable pipeline growth for the Sales team.Develop and execute digital marketing campaigns across multiple channels, including email, SEM, paid social, and Canary’s website. Collaborate with the Marketing, Product, Sales, and Leadership teams on campaigns execution, including the development of content & design assets and digital marketing to ensure campaign effectiveness. Execute across all stages of marketing campaigns, including ideation, experimentation, measurement, iteration, and scaling. Build processes and workflows for experimentation & measurement to enable scale.Understand the customer (hotels) and their customers (hotel guests).Optimize online response and conversion rates via landing page optimization.Manage contractors and outside vendors. Build a growth marketing team. Qualifications 8+ years of Marketing experience, with 5+ years of demand generation experience in a B2B technology environment.Experience with Salesforce and Marketo, or similar systems. Proven experience in building, testing, and scaling marketing channels within a high-growth environment.Proven experience developing content (in conjunction with graphic designers & content marketers) and optimizing content across multiple marketing channels.Ability to think critically about a product’s place in the marketplace, generate informed marketing tests and execute.Digital marketing experience including but not limited to Email, Google Ads, LinkedIn, Facebook.Proven agility, flexibility, and autonomy in managing projects end-to-end with strong attention to detail.Demonstrated ability to manage multiple projects and priorities with agreed-upon timelines and various scopes.Have successfully built and managed an internal and/or external team. Pluses Salesloft ExperienceABM experience Benefits Health Care Plan 401k PlanPaid Time Off (Vacation, Sick & Public Holidays)Stock Option Plan Canary Technologies is an Equal Opportunity Employer and all qualified applicants will receive consideration for employment without regard to race, color, religion, gender, sexual orientation, national origin, genetic information, age, disability, veteran status, or any other legally protected basis Most importantly, we work hard to ensure Canary is a fun and exciting place to work. How do we do this? First, we've added Canary Days to the calendar as company holidays to ensure that the team has 1 long weekend each month. Second, we have a list clubs and perks listed below that create space for us to hang out! Self Improvement Club: We meet each month and share our personal goals for the month.  We are able to expense $75 towards any purchases that helped us achieve these goals. Fireside Chat: We meet each month to discuss a wide range of issues.  This group was started focused on women's issues and has expanded in scope over the last several months. Donuts! : Each week a Slackbot called ‘Donut’ pairs us up with a random teammate. $50 to stay at any hotel that uses Canary Check-inBook a trip at one of the hotels that has Canary Checkin, stay there, leave a review on TripAdvisor/Google and get a $50 reimbursement! $500 travel reimbursement: We get up to $500 if we want to make a trip to SF or NY for personal reasons. We will spend at least 3 days of that trip working at a wework with fellow Canaryites!

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
    # "title": 215,
    # "sub_role": 245,
    "tenure": 244,
    # "locations": 243,
    # "pay_min": 222,
    # "pay_max": 223,
    # "responsibility": 214,
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
