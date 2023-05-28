from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Growth Marketing Manager| Boston or NYC, Boston or NYC, GROWTH MARKETING MANAGER | BOSTON OR NYC  We’re Sofar Sounds, your global music community. We bring people together in unexpected spaces in over 400 cities around the world. We’re artists, music lovers and organizers. We’re a company of musicians for musicians.  We create, perform, listen and work to make intimate live music experiences that connect us all. Every show is focused on the artist.   THE ROLE  As Growth Marketing Manager, you will bring your expertise in performance marketing to contribute to customer acquisition and retention for the world’s largest global concert community. You’ll utilize all paid and organic channels, including search, display, social, affiliates and email, to sell tickets to a large, diverse and progressive audience, while optimizing the go-to-market strategy and customer journey.   Sofar has worked with over 30,000 artists, hosted over 1,000,000 fans at shows around the world and engages with millions more online each month. You will be part of a growth team that is passionate about creating an industry-leading culture that supports artists and introduces their music to new fans.   WHAT YOU’LL DO:   * Contribute strategies and tactics to grow all stages of customer acquisition    and retention.  * Execute targeted paid media campaigns to acquire customers across different    channels with a focus on paid search and online platforms.   * Perform thorough channel and campaign analysis, share performance updates and    insights with key business partners and use this data to optimize current and    develop future campaigns  * Partner with the Technology, Product and Design team to continually improve    the customer journey and landing pages, quickly testing hypotheses and    scaling programs that deliver high ROI  * Monitor sell-through, proactively identify cities that need additional    marketing support and quickly execute programs to increase ticket sales   * Maintain an in-depth, analytical understanding of all aspects of our    customers, applying insights to our growth strategies and tactics  * Collaborate with the Creative team to create effective campaign creative and    consistently update creative assets  * Drive continual improvement of our customer experience   * You’ll also discover a lot of great new music, from all around the world   WHO YOU ARE:   * 4-8 years of growth marketing experience, successfully scaling paid media    channels within allowable Cost-per-Acquisition targets.  * Hands-on execution in Google Ads and other marketing platforms. Cross-channel    experience and interest.  * Demonstrable experience in implementing data-led marketing strategies,    analytics tools and cross-channel attribution.  * Track record of increasing user acquisition, engagement and retention and    meeting/exceeding revenue and profitability goals  * Experience in a scrappy startup culture, with individual ownership and    cross-team collaboration  * Genuine, demonstrated commitment to supporting artists and local music   DIVERSITY, EQUITY & INCLUSION  We are proud to have a global workforce and strive towards having a diverse workplace. We have an Equity Council, Employee Resource Groups and ongoing learning and development in this area - DEI is important to us and our culture.   COMPENSATION, PAY EQUITY & BENEFITS  Our people and global communities are precious - we aim to treat them as such. At Sofar we feel strongly about the compensation and benefits that we provide across the board so that no matter your skill set or experience you’re paid fairly according to market rate, plus your health and wellbeing is supported through our local benefits packages.   LEARNING & DEVELOPMENT  We invest in your learning and development and strive to create a learning culture through formal and informal workshops, training, and a personal L&D budget and learning path.   HIRING JOURNEY  We’ll work with you closely to support you throughout the hiring process. If your CV/ resume shows that your skills and experience have synergy with the job description, then we’ll hop on a call to say “Hello” and to start getting to know one another.  If it’s not the right opportunity this time, we’ll always let you know.   Typically our hiring process takes a maximum of 4 weeks end to end. You’ll be guided through the process by our Talent team and an interview panel of lovely humans who will give you support and feedback throughout - we’ll do our very best to create an interview environment that brings out the best in you and sets you up for success.   If this sounds like you, we can’t wait to meet you - come on in.

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
