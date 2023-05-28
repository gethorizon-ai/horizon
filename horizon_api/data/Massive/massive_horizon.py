from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# TODO: set Horizon API key and OpenAI API key
horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

# TODO: create list of job listings. Currently, just has one element
test_job_listings = [
    """Senior Content Editor - Token, New York, NY (HQ), We’re looking for an experienced content creator and editor that is excited to shake up the world of cryptocurrency.   Are you ready to shape our brand and voice? Are you ready to attract new audiences and build a close-knit community? If so, join us at Quidd!   You will be responsible for nearly all content that shows up, from Quidd Token about Quidd Token, across the blogs, email newsletters, ads, press releases, and other long-form mediums. As the resident in-house copywriter, copy editor, and content planner, you will run everything end-to-end, from overall strategy to messaging to production to analysis.   The QUIDD token is the official utility token for the QUIDD ecosystem which first pioneered digital collecting 5 years ago with officially-licensed collectibles from over 325 of the world's most beloved brands and 7 million collectors. The QUIDD token is designed to give QUIDD collectors and creators added utility in both the QUIDD app including purchasing of NFTs and collectibles, governance and trade as well as trade, create and collect-to-earn programs utilizing the QUIDD token.   This will be your mission -- to tell the world about Quidd Token and its community; all the while growing the community. To accomplish this, everyday you will work with a small, cross-functional team, including product managers, designers, engineers, and merchandisers, putting you at the center of the action. What You'll Do Develop and execute the company’s content strategyDefine key messages, always knowing what sells from a reader’s perspectivePlan, write, and edit a lot, including copy for blog posts, website articles, ad creative, push notifications, automated emails, user guides, email newsletters, and press releasesProduce a series of original long-form content focused on popular culture, balancing crypto credibility with mainstream understanding and appeal, etc.Own and operate the overall content schedule, including management of an extended team of freelance copywriters in on-going content productionTrack, analyze, and report on all media exposure, including open rates, click-thru rates, pageviews, and more across content channelsPartner with graphic designers and video production companies to produce world-class teaser materials Who You Are An extremely-organized person; your world-class project management is an inborn characteristic...there is something inside you that must do itA talented writer; writing and editing comes easy to do, and you enjoy doing itA storyteller; you are a natural at drawing in an audience and telling our story, and the story of our collectors Super curious about cryptocurrency: you’ve seen the headlines and gone further down the rabbit hole; you’ve researched some of the latest projects and have your own investments or interest in investingA hands-on doer; you can run content schedules, craft messaging, create graphics and short video clips on-the-fly, publish content, and analyze resultsNot a beginner; you have proven track record and can point to a portfolio of content and content marketing you’ve done, both good and badA resilient sponge; small teams and startups aren’t easy and there will be hazards along the way so you must be fortified and willing to learn...success will be more rewarding as a result What You're Good At Branding and voice; you can craft a unique and fresh voice for this 5 year-old brand, both through creative inspiration and real-time iterationCalendarization; you are oriented towards the future and plan very, very well Researching & Writing; you are skilled with copywriting and can write persuasively, quickly and easily; you can interview and conduct research, detailing and contextualizing the stories behind the collectibles Editing & Communicating; you can get the most out of other writers, turning feedback into actions through an extended network of collaborators and writers, at scaleGoing Deeper; there’s the surface and then there’s what is underneath; you are skilled at investigating what is happening on deeper levels, using empathy, and contextualizing stories for the world to consume and understandGeeking Out; you can effortlessly go deep on pop culture references What You've Done Functional: a minimum of 5+ years managing editorial, content creation, and content marketing for a startup, technology company, or big brandIndustry: personal and professional experience in crypto and/or marketplaces, collectibles, e-commerce

###"""
]


# Define a function to make the API call and update the result
def make_api_call(task_id, inputs):
    return json.loads(
        horizon_ai.deploy_task(task_id=task_id, inputs=inputs, log_deployment=False)[
            "completion"
        ]
    )


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

aggregate_results = []
with ThreadPoolExecutor() as executor:
    # Process each job listing
    for listing in test_job_listings:
        inputs = {"input_data": listing}
        result = {}

        # Submit tasks to the executor for concurrent calls and store the future objects
        futures = [
            executor.submit(make_api_call, task_id, inputs)
            for task_id in task_ids.values()
        ]

        # Retrieve the results as they complete
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
