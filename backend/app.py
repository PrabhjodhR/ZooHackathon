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
-overloaded: multiple demanding tasks or several medium-to-large responsibilities that would likely be unrealistic or exhausting to complete comfortably in one day

Estimate day_load based only on the number of tasks, their apparent urgency, and how demanding they seem. Do not assume exact task durations.
The reasoning should sound natural and human, like a helpful productivity assistant. Keep it brief, warm, and conversational, but still clear and grounded in the tasks provided do not summarize/repeat the tasks.

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
-Prioritize school, work, and deadline-driven responsibilities over optional personal tasks unless the personal task is explicitly urgent or has a same-day deadline.
-Place important but less urgent tasks in should_do_today.
-Place small, low-effort tasks like short calls, bookings, or simple purchases in quick_wins unless they are explicitly urgent.
-Place lower-priority or longer-term tasks in can_wait.
-Treat multiple substantial tasks such as school work, job applications, or project work in the same day as increasing the day load, even if some quick wins are also present.
-Be conservative when estimating day_load. If the list includes several demanding tasks, prefer overloaded over heavy.
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
    app.run(debug=True, port=port)
