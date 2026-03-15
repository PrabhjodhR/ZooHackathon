from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv #to load vars from .env file
from openai import OpenAI
import os
import json

load_dotenv() #loads vars from .env file

app = Flask(__name__) #creates backend app
CORS(app) #allows requests from React frontend (tht hv diff origins)

port = int(os.getenv("PORT", 5000)) #checks if port is mentioned in .env else set port to 5000

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) #connects backend to OpenAI using the key in .env

#Below is the string we give the model as a prompt
PROMPT = """
You are a task organization assistant.

The user will provide a messy brain dump of tasks, reminders, and things they need to do.

Organize the input into these categories:

-must_do_today
-should_do_today
-quick_wins
-can_wait

Also estimate the day_load as one of:
-light: only a few small or low-effort tasks
-manageable: one main task plus a few smaller tasks, with flexibility
-heavy: one to two demanding tasks plus several additional responsibilities
-overloaded: the set of tasks feels unrealistic, excessive, crisis-level, emotionally draining, or unlikely to be completed comfortably in one day

Estimate day_load based on the number of tasks, their urgency, their apparent difficulty, and whether the overall list feels realistically doable in one day.
Do not assume exact task durations, but do use common sense about scope and intensity.

The reasoning should sound natural and human, like a helpful productivity assistant. Keep it brief, warm, and conversational, but still clear and grounded in the tasks provided. Do not summarize or repeat the task list.

Rules:
-Return raw valid JSON only.
-Do not include markdown or extra text.
-Use exactly these keys:
must_do_today, should_do_today, quick_wins, can_wait, day_load, reasoning
-Keep task wording short and clear.
-Each task must appear in only one category.
-Do not invent tasks that are not implied by the input.
-If a category has no tasks, return an empty array.
-reasoning must be brief, natural, and conversational.
-Do not sound robotic or overly formal.
-Place urgent or deadline-driven academic, work, or required tasks in must_do_today.
-Place essential self-care, hygiene, eating, sleep, medication, and basic physical or mental health needs in must_do_today whenever they appear.
-Treat tasks like eating meals, showering, taking meds, resting, drinking water, or taking care of mental health as non-optional basics, not lower-priority extras.
-Prioritize school, work, and deadline-driven responsibilities over optional personal tasks unless the personal task is explicitly urgent or has a same-day deadline.
-Place important but less urgent tasks in should_do_today.
-Place small, low-effort tasks like short calls, bookings, simple purchases, or quick research in quick_wins unless they are explicitly urgent.
-Place lower-priority, leisure, or longer-term tasks in can_wait.
-Treat multiple substantial tasks such as school work, job applications, project work, design work, or emotionally demanding responsibilities in the same day as increasing the day load.
-Be conservative when estimating day_load. If the list includes several demanding tasks, prefer overloaded over heavy.
-If even one task is extremely large-scope, crisis-level, unrealistic for one person to complete in a day, or absurdly high-stakes, strongly prefer overloaded.
-If the list mixes normal daily responsibilities with one obviously massive or impossible task, treat the overall day as overloaded rather than heavy.
-Do not normalize absurd tasks as if they are ordinary errands. Let unusually extreme tasks meaningfully affect day_load.
"""

#Test route for debugging -> confirms Flask app is running and frontend is reaching the correct backend
# @app.route("/test")
# def test():
#     print("TEST ROUTE HIT", flush=True)
#     return {"message": "hello from THIS backend"}

#Below is the main route, only accepts POST requests; request comes in, run route
@app.route("/organize", methods=["POST"])
def organize():
    try:
        data = request.get_json() #reads json 


        brain_dump = data.get("brainDump") if data else None

        #checks if brainDump exists and tht its a string
        if not brain_dump or not isinstance(brain_dump, str):
            return jsonify({"error": "brainDump is required."}), 400 #returns error if not

        #sending braindump to ai 
        response = client.responses.create( #this part changes based on the model u use
            model="gpt-5.4", 
            instructions=PROMPT,
            input=f"Organize this brain dump:\n\n{brain_dump}", #sends user input
            max_output_tokens=1000, #limit response length
        )

        #gets raw text from ai 
        raw_text = response.output_text.strip()
        #convert json text into python dictionary
        result = json.loads(raw_text)

        return jsonify(result) #yayy return results to frontend

    #error handling :(
    except Exception as error:
        import traceback
        traceback.print_exc()
        print("OpenAI error:", error, flush=True)
        return jsonify({
            "error": "Failed to organize tasks",
            "details": str(error)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
