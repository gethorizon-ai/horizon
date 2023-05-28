from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# TODO: set Horizon API key and OpenAI API key
horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

# TODO: create list of job listings. Currently, just has one element
test_job_listings = [
    """Senior Data Scientist, Ads Quality Analytics, Remote - United States, Reddit is a community of communities where people can dive into anything through experiences built around their interests, hobbies, and passions. Our mission is to bring community, belonging, and empowerment to everyone in the world. Reddit users submit, vote, and comment on content, stories, and discussions about the topics they care about the most. From pets to parenting, there’s a community for everybody on Reddit and with over 50 million daily active users, it is home to the most open and authentic conversations on the internet. For more information, visit redditinc.com [redditinc.com].  Location: Remote-friendly  Reddit is continuing to grow our teams with the best talent. This role is completely remote friendly [https://redditblog.com/2020/10/27/evolving-reddits-workforce/] and will continue to be after the pandemic.   We are looking for a Senior Data Scientist to work within the Ads Data Science team. You will work closely with engineers and product owners from our Ads team to 1) optimize ads delivery and auction systems, 2) shape product roadmap and strategy of ads quality and relevance. This person has a solid business acumen and knows what is important to advertisers and users (i.e. redditors). In addition, this person needs to demonstrate strong cross-functional stakeholders management capabilities.  Responsibilities:   * Research, design and develop contextual ad relevance measurements. Reddit ad    is a combination of text, image, user and ad engagement attributes. You will    use modern statistical models to combine those signals and develop measures    for ad quality.   * You will design metrics and experiments to understand marketplace tradeoffs    between user engagement and ad quality, as well as measure long term user    impact of ad quality. You will develop models that would optimize both ad    quality and ad delivery.   * Serve as a thought-partner for product managers, engineering managers and    leadership in shaping the monetization roadmap and strategy for Reddit by    identifying actionable and impactful insights through deep-dive analyses and    analytics insights.  Required Qualifications:   * Relevant experiences in ads marketplace.  * Ph.D., M.S. or Bachelors degree in Statistics, Machine Learning, Economics,    Computer Science, or other quantitative fields (If M.S. degree, a minimum of    1+ years of industry data science experience required and if Bachelor’s    degree, a minimum of 2+ years of industry data science experience).  * Deep understanding of online experimentation and causal inference.  * Strong analytical and communication skills.  * Proficiency in machine learning, statistical modeling, and optimization.  * Strong skills in SQL and programming (Python or R).  Benefits:   * Comprehensive Health benefits  * 401k Matching   * Workspace benefits for your home office  * Personal & Professional development funds  * Family Planning Support  * Flexible Vacation & Reddit Global Days Off  * 4+ months paid Parental Leave    * Paid Volunteer time off  Pay Transparency:  This job posting may span more than one career level.  In addition to base salary, this job is eligible to receive equity in the form of restricted stock units, and depending on the position offered, it may also be eligible to receive a commission. Additionally, Reddit offers a wide range of benefits to U.S.-based employees, including medical, dental, and vision insurance, 401(k) program with employer match, generous time off for vacation, and parental leave. To learn more, please visit https://www.redditinc.com/careers/.  To provide greater transparency to candidates, we share base pay ranges for all US-based job postings regardless of state. We set standard base pay ranges for all roles based on function, level, and country location, benchmarked against similar stage growth companies. Final offer amounts are determined by multiple factors including, skills, depth of work experience and relevant licenses/credentials, and may vary from the amounts listed below.  The base pay range for this position is: $183,500 - $275,300.  #LI-Remote #LI-NH1  Reddit is committed to providing reasonable accommodations for qualified individuals with disabilities and disabled veterans in our job application procedures. If you need assistance or an accommodation due to a disability, please contact us at ApplicationAssistance@Reddit.com [ApplicationAssistance@Reddit.com].

###"""
]

# List of task IDs to extract necessary elements from job listing
task_ids = {
    "title": 215,
    "sub_role": 245,
    "tenure": 244,
    "locations": 243,
    "pay_min": 222,
    "pay_max": 223,
    "responsibility": 214,
}


# Define a function to make the API call and update the result
def make_api_call(task_id, inputs):
    return json.loads(
        horizon_ai.deploy_task(task_id=task_id, inputs=inputs, log_deployment=False)[
            "completion"
        ]
    )


aggregate_results = []
with ThreadPoolExecutor() as executor:
    # Process each job listing
    for listing in test_job_listings:
        # Submit tasks to the executor for concurrent calls and store the future objects
        inputs = {"input_data": listing}
        futures = [
            executor.submit(make_api_call, task_id, inputs)
            for task_id in task_ids.values()
        ]

        # Retrieve the results as they complete
        result = {}
        for future, field, task_id in zip(
            as_completed(futures), task_ids.keys(), task_ids.values()
        ):
            try:
                # Get the result of the completed task
                task_result = future.result()
            except Exception as e:
                # If error occurs, set field to None and print error
                task_result = {field: None}
                print(f"Error occurred while executing task {task_id}: {e}")
            result.update(task_result)

        # Store final result in aggregate_results object
        aggregate_results.append(result)

# TODO: Process aggregate_results. Currently, just prints first result
print(json.dumps(aggregate_results[0], indent=4))
